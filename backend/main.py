import csv
from io import StringIO
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from backend.database import SessionLocal, engine
from backend import models, schemas
from workers.nlp_mapper.worker import run_nlp_mapping_pipeline
from workers.cv_analytics.worker import process_camera_telemetry
from datetime import datetime, timedelta
import re

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="BuilderCV Core API")

# Словарь начальных данных
DEMO_INITIAL_VOLUMES = {
    "Подготовительные работы": 300.0,
    "Механизированная разработка": 850.0,
    "Планировка дна": 1000.0,
    "Устройство щебеночного основания": 150.0,
    "Укладка бетонной подготовки": 100.0,
    "Устройство горизонтальной рулонной гидроизоляции": 660.0
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project_dashboard(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        project = models.Project(id=project_id, name=f"Тестовый объект #{project_id}")
        db.add(project)
        db.commit()
        db.refresh(project)
    return project

@app.post("/projects/{project_id}/upload-plan/")
async def upload_project_plan(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stages = db.query(models.Stage).filter(models.Stage.project_id == project_id).all()
    stage_ids = [s.id for s in stages]
    if stage_ids:
        db.query(models.Telemetry).filter(models.Telemetry.stage_id.in_(stage_ids)).delete(synchronize_session=False)
    
    db.query(models.Stage).filter(models.Stage.project_id == project_id).delete(synchronize_session=False)
    db.commit()

    content = await file.read()
    try:
        decoded_content = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        decoded_content = content.decode("cp1251")
        
    delimiter = ';' if ';' in decoded_content.split('\n')[0] else ','
    csv_reader = csv.DictReader(StringIO(decoded_content), delimiter=delimiter)

    def parse_date(date_str):
        if not date_str or str(date_str).strip() == "":
            return None
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue
        return None

    for row in csv_reader:
        cleaned_row = {k.strip(): str(v).strip() for k, v in row.items() if k}
        stage_name = (
            cleaned_row.get("Вид работ") or 
            cleaned_row.get("Наименование работ") or 
            cleaned_row.get("Название этапа") or 
            "Неизвестный этап"
        )
        raw_vol = cleaned_row.get("Объем работ") or cleaned_row.get("Объем") or "0"
        vol_match = re.search(r"[\d\.]+", raw_vol.replace(',', '.'))
        try:
            target_volume = float(vol_match.group(0)) if vol_match else 0.0
        except ValueError:
            target_volume = 0.0

        start_date = parse_date(cleaned_row.get("Начало работ") or cleaned_row.get("Начало"))
        end_date = parse_date(cleaned_row.get("Окончание работ") or cleaned_row.get("Окончание"))

        initial_vol = 0.0
        for key, val in DEMO_INITIAL_VOLUMES.items():
            if key.lower() in stage_name.lower():
                initial_vol = val
                break

        new_stage = models.Stage(
            project_id=project.id,
            name=stage_name,
            target_volume=target_volume,
            current_volume=initial_vol,
            start_date=start_date,
            end_date=end_date
        )
        db.add(new_stage)
    
    db.commit()
    
   
    for stage in db.query(models.Stage).filter(models.Stage.project_id == project.id).all():
        if stage.current_volume > 0:
            init_telemetry = models.Telemetry(
                stage_id=stage.id,
                detected_objects=[{"class": "system_init", "conf": 1.0}],
                calculated_volume=stage.current_volume,
                timestamp=datetime.utcnow() - timedelta(days=1)
            )
            db.add(init_telemetry)
            
    db.commit()
    run_nlp_mapping_pipeline(db, project.id)

    return {"status": "success", "message": "План загружен и классифицирован!"}

@app.post("/telemetry/")
def receive_telemetry(
    telemetry: schemas.TelemetryCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    background_tasks.add_task(
        process_camera_telemetry, 
        db, 
        telemetry.stage_id, 
        telemetry.detected_objects
    )
    return {"status": "accepted_for_processing"}

@app.get("/stages/{stage_id}/history")
def get_stage_history(stage_id: int, db: Session = Depends(get_db)):
    """Возвращает историю прироста объема ТОЛЬКО ЗА СЕГОДНЯ"""
    records = db.query(models.Telemetry).filter(
        models.Telemetry.stage_id == stage_id,
        models.Telemetry.calculated_volume > 0
    ).order_by(models.Telemetry.timestamp).all()
    
    today = datetime.utcnow().date()
    
   
    today_records = [r for r in records if r.timestamp.date() == today]
    past_records = [r for r in records if r.timestamp.date() < today]
    
    start_vol = past_records[-1].calculated_volume if past_records else 0
    
    history = []
    
    if today_records:
        history.append({
            "time": (today_records[0].timestamp - timedelta(seconds=5)).strftime("%H:%M:%S"), 
            "volume": round(start_vol, 2)
        })
        for r in today_records:
            history.append({
                "time": r.timestamp.strftime("%H:%M:%S"), 
                "volume": round(r.calculated_volume, 2)
            })
            
    return history