from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db, Base, engine
from app.schemas.common import APIResponse

router = APIRouter()

@router.post("/initialize", response_model=APIResponse)
def initialize_demo(db: Session = Depends(get_db)):
    # Clear tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    counts = {
        "assets": 0,
        "tasks": 0,
        "corridors": 0,
        "trains": 0
    }
    
    # Normally we would import from scripts/generate_synthetic_data.py
    # and call its main function to generate and insert data.
    
    try:
        from scripts.generate_synthetic_data import generate_and_save_data
        counts = generate_and_save_data(db)
    except Exception as e:
        print(f"Error generating synthetic data: {e}")
        
    return APIResponse(success=True, data={"message": "Demo initialized", "counts": counts})
