from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobCreateRequest(BaseModel):
    input_text: str


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    input_text: str
    status: str
    progress: int
    result: str | None
    created_at: datetime
