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
        name_lower = stage.name.lower()
        
        if "котлован" in name_lower or "выемка" in name_lower or "земл" in name_lower:
            stage.nlp_stage_id = "STAGE_EARTH_WORK"
        elif "подбетон" in name_lower or "основан" in name_lower:
            stage.nlp_stage_id = "STAGE_FOUNDATION"
        elif "перекрыт" in name_lower or "колонн" in name_lower or "пилон" in name_lower:
            stage.nlp_stage_id = "STAGE_CONCRETE_WORK"
        else:
            stage.nlp_stage_id = "UNKNOWN"

    db.commit()