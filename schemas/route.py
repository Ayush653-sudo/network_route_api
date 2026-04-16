from datetime import datetime
from pydantic import BaseModel, Field


class RouteRequest(BaseModel):
    source: str = Field(..., min_length=1, max_length=255, examples=["ServerA"])
    destination: str = Field(..., min_length=1, max_length=255, examples=["ServerD"])


class RouteResponse(BaseModel):
    total_latency: float
    path: list[str]


class RouteHistoryResponse(BaseModel):
    id: int
    source: str
    destination: str
    total_latency: float
    path: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    error: str
