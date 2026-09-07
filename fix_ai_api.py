import re

with open('backend/app/api/routes/ai.py', 'r') as f:
    code = f.read()

replacement = \"\"\"@router.post(\"/predict-impact\", response_model=APIResponse)
def predict_impact(payload: dict = Body(...), db: Session = Depends(get_db)):
    corridor_id = payload.get('corridor_id')
    block_duration = payload.get('block_duration', 1.0)
    block_start_hour = payload.get('block_start_hour', 12)
    
    from app.models import Corridor, Train
    corridor = db.query(Corridor).filter(Corridor.corridor_id == corridor_id).first()
    if not corridor:
        raise HTTPException(status_code=404, detail=\"Corridor not found\")
        
    trains = db.query(Train).filter(Train.corridor_id == corridor_id).all()
    corridor_dict = {c.name: getattr(corridor, c.name) for c in corridor.__table__.columns}
    trains_dict = [{c.name: getattr(t, c.name) for c in t.__table__.columns} for t in trains]
    
    try:
        impact = predictor.predict_impact(corridor_dict, trains_dict, float(block_duration), int(block_start_hour))
        return APIResponse(success=True, data=impact)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
\"\"\"

code = re.sub(
    r'@router\.post\(\"/predict-impact\".*?def predict_impact.*?(?=@router|$)',
    replacement,
    code,
    flags=re.DOTALL
)

with open('backend/app/api/routes/ai.py', 'w') as f:
    f.write(code)
