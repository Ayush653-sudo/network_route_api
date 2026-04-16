from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Node, Edge
from schemas import EdgeCreate, EdgeResponse
from constants.log_messages import NODE_DOES_NOT_EXIST, EDGE_ALREADY_EXISTS, EDGE_NOT_FOUND_BY_ID

router = APIRouter(prefix="/edges", tags=["Edges"])


def _get_node_or_404(db: Session, name: str) -> Node:
    node = db.query(Node).filter(Node.name == name).first()
    if not node:
        raise HTTPException(status_code=400, detail=NODE_DOES_NOT_EXIST.format(name))
    return node


@router.post("", response_model=EdgeResponse, status_code=status.HTTP_201_CREATED)
def add_edge(payload: EdgeCreate, db: Session = Depends(get_db)):
    source_node = _get_node_or_404(db, payload.source)
    dest_node = _get_node_or_404(db, payload.destination)

    existing = (
        db.query(Edge)
        .filter(Edge.source_id == source_node.id, Edge.destination_id == dest_node.id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=EDGE_ALREADY_EXISTS.format(payload.source, payload.destination),
        )

    edge = Edge(source_id=source_node.id, destination_id=dest_node.id, latency=payload.latency)
    db.add(edge)
    try:
        db.commit()
        db.refresh(edge)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=EDGE_ALREADY_EXISTS.format(payload.source, payload.destination),
        )

    return EdgeResponse.from_orm_edge(edge)


@router.get("", response_model=list[EdgeResponse])
def list_edges(db: Session = Depends(get_db)):
    edges = db.query(Edge).order_by(Edge.id).all()
    return [EdgeResponse.from_orm_edge(e) for e in edges]


@router.delete("/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_edge(edge_id: int, db: Session = Depends(get_db)):
    edge = db.get(Edge, edge_id)
    if not edge:
        raise HTTPException(status_code=404, detail=EDGE_NOT_FOUND_BY_ID.format(edge_id))

    db.delete(edge)
    db.commit()
