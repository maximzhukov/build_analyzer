from fastapi import BackgroundTasks
from workers.cv_analytics.worker import process_camera_telemetry

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