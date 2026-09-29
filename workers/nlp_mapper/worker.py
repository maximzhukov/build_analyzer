from sqlalchemy.orm import Session
from backend.models import Stage


def run_nlp_mapping_pipeline(db: Session, project_id: int):
    unmapped_stages = db.query(Stage).filter(
        Stage.project_id == project_id,
        Stage.nlp_stage_id == None
    ).all()

    if not unmapped_stages:
        return

    
    

    for stage in unmapped_stages:
        
        
        
        
        if "земл" in stage.name.lower():
            stage.nlp_stage_id = "STAGE_EARTH_WORK"
        elif "кирп" in stage.name.lower() or "кладк" in stage.name.lower():
            stage.nlp_stage_id = "STAGE_BRICK_WORK"
        else:
            stage.nlp_stage_id = "UNKNOWN"

    db.commit()