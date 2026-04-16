from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database import get_db
from models import Node, RouteHistory
from schemas import RouteRequest, RouteResponse, RouteHistoryResponse, ErrorResponse
from services.graph import build_graph, dijkstra
from constants.log_messages import (
    SOURCE_DESTINATION_MUST_DIFFER,
    NODE_DOES_NOT_EXIST,
    NO_PATH_EXISTS,
)

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.post(
    "/shortest",
    response_model=RouteResponse,
    responses={
        404: {"model": ErrorResponse, "description": "No path exists between the two nodes"},
        400: {"model": ErrorResponse, "description": "Invalid or non-existent nodes"},
    },
)
def get_shortest_route(payload: RouteRequest, db: Session = Depends(get_db)):
    if payload.source == payload.destination:
        raise HTTPException(status_code=400, detail=SOURCE_DESTINATION_MUST_DIFFER)

    source_node = db.query(Node).filter(Node.name == payload.source).first()
    if not source_node:
        raise HTTPException(status_code=400, detail=NODE_DOES_NOT_EXIST.format(payload.source))

    dest_node = db.query(Node).filter(Node.name == payload.destination).first()
    if not dest_node:
        raise HTTPException(status_code=400, detail=NODE_DOES_NOT_EXIST.format(payload.destination))

    graph = build_graph(db)
    result = dijkstra(graph, payload.source, payload.destination)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=NO_PATH_EXISTS.format(payload.source, payload.destination),
        )

    total_latency, path = result

    history = RouteHistory(
        source=payload.source,
        destination=payload.destination,
        total_latency=round(total_latency, 6),
        path=path,
    )
    db.add(history)
    db.commit()

    return RouteResponse(total_latency=round(total_latency, 6), path=path)


@router.get("/history", response_model=list[RouteHistoryResponse])
def get_route_history(
    source: str | None = Query(default=None, description="Filter by source node name"),
    destination: str | None = Query(default=None, description="Filter by destination node name"),
    limit: int | None = Query(default=None, ge=1, description="Maximum number of records to return"),
    date_from: datetime | None = Query(default=None, description="Filter records created on or after this timestamp"),
    date_to: datetime | None = Query(default=None, description="Filter records created on or before this timestamp"),
    db: Session = Depends(get_db),
):
    query = db.query(RouteHistory)

    if source:
        query = query.filter(RouteHistory.source == source)
    if destination:
        query = query.filter(RouteHistory.destination == destination)
    if date_from:
        query = query.filter(RouteHistory.created_at >= date_from)
    if date_to:
        query = query.filter(RouteHistory.created_at <= date_to)

    query = query.order_by(RouteHistory.created_at.desc())

    if limit:
        query = query.limit(limit)

    return query.all()
