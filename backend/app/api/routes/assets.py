from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models import Asset
from app.schemas.asset import AssetResponse, AssetCreate, AssetUpdate
from app.schemas.common import APIResponse
from typing import List

router = APIRouter()

@router.get("", response_model=APIResponse)
def get_assets(department: str = None, corridor_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Asset)
    if department:
        query = query.filter(Asset.department == department)
    if corridor_id:
        query = query.filter(Asset.corridor_id == corridor_id)
    assets = query.all()
    return APIResponse(success=True, data=assets)

@router.get("/{asset_id}", response_model=APIResponse)
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return APIResponse(success=True, data=asset)

@router.post("", response_model=APIResponse)
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    new_asset = Asset(**asset.model_dump())
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)
    return APIResponse(success=True, data=new_asset)

@router.put("/{asset_id}", response_model=APIResponse)
def update_asset(asset_id: str, asset: AssetUpdate, db: Session = Depends(get_db)):
    db_asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    for k, v in asset.model_dump(exclude_unset=True).items():
        setattr(db_asset, k, v)
    db.commit()
    db.refresh(db_asset)
    return APIResponse(success=True, data=db_asset)
