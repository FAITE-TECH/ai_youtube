from pydantic import BaseModel
from typing import List

class AnalyzeResponse(BaseModel):
    video_id: str
    title: str
    recommendations: List[dict]

class CampaignResultIn(BaseModel):
    video_id: str
    country: str
    audience: str
    budget_spent: float
    predicted_watch_time: float
