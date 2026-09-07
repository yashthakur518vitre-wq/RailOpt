from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models import Block
from app.schemas.common import APIResponse

router = APIRouter()

@router.get("", response_model=APIResponse)
def get_blocks(department: str = None, status: str = None, corridor_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Block)
    if department:
        query = query.filter(Block.department == department)
    if status:
        query = query.filter(Block.status == status)
    if corridor_id:
        query = query.filter(Block.corridor_id == corridor_id)
    blocks = query.all()
    return APIResponse(success=True, data=blocks)

@router.get("/{block_id}", response_model=APIResponse)
def get_block(block_id: str, db: Session = Depends(get_db)):
    block = db.query(Block).filter(Block.block_id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return APIResponse(success=True, data=block)
