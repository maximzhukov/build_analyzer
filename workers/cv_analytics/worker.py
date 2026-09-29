from sqlalchemy.orm import Session
from backend.models import Stage, Telemetry
from workers.cv_analytics.strategies import StrategyRegistry

def process_camera_telemetry(db: Session, stage_id: int, detected_objects: list):
    stage = db.query(Stage).filter(Stage.id == stage_id).first()
    if not stage:
        raise ValueError(f"Этап с ID {stage_id} не найден")

    
    strategy = StrategyRegistry.get_strategy(stage.nlp_stage_id)

    
    new_volume = strategy.calculate_volume(detected_objects, stage.current_volume)

    
    telemetry_record = Telemetry(
        stage_id=stage.id,
        detected_objects=detected_objects,
        calculated_volume=new_volume
    )
    db.add(telemetry_record)

    
    stage.current_volume = new_volume
    db.commit()
    
    return new_volume