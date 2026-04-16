from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Node
from schemas import NodeCreate, NodeResponse
from constants.log_messages import NODE_ALREADY_EXISTS, NODE_NOT_FOUND_BY_ID

router = APIRouter(prefix="/nodes", tags=["Nodes"])


@router.post("", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
def add_node(payload: NodeCreate, db: Session = Depends(get_db)):
    if db.query(Node).filter(Node.name == payload.name).first():
        raise HTTPException(status_code=400, detail=NODE_ALREADY_EXISTS.format(payload.name))

    node = Node(name=payload.name)
    db.add(node)
    try:
        db.commit()
        db.refresh(node)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail=NODE_ALREADY_EXISTS.format(payload.name))

    return node


@router.get("", response_model=list[NodeResponse])
def list_nodes(db: Session = Depends(get_db)):
    return db.query(Node).order_by(Node.id).all()


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(node_id: int, db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail=NODE_NOT_FOUND_BY_ID.format(node_id))

    db.delete(node)
    db.commit()
