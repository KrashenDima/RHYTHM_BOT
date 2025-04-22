from dataclasses import dataclass
from datetime import datetime

from app.infrastructure.models.base import BaseModel

@dataclass
class ProfilesModel(BaseModel):
    id: int
    user_id: int
    name: str
    city: str
    text: str
    musician_type: str
    interest: str
    photo_url: str
    created_at: datetime
    updated_at: datetime | None