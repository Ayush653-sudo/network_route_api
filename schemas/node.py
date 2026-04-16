from pydantic import BaseModel, Field


class NodeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["ServerA"])


class NodeResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
