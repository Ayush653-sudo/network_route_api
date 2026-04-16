from pydantic import BaseModel, Field, field_validator
from constants.log_messages import SOURCE_DESTINATION_NODES_MUST_DIFFER


class EdgeCreate(BaseModel):
    source: str = Field(..., min_length=1, max_length=255, examples=["ServerA"])
    destination: str = Field(..., min_length=1, max_length=255, examples=["ServerB"])
    latency: float = Field(..., gt=0, examples=[12.5])

    @field_validator("destination")
    @classmethod
    def source_destination_differ(cls, destination: str, info) -> str:
        if info.data.get("source") and destination == info.data["source"]:
            raise ValueError(SOURCE_DESTINATION_NODES_MUST_DIFFER)
        return destination


class EdgeResponse(BaseModel):
    id: int
    source: str
    destination: str
    latency: float

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_edge(cls, edge) -> "EdgeResponse":
        return cls(
            id=edge.id,
            source=edge.source_node.name,
            destination=edge.destination_node.name,
            latency=edge.latency,
        )
