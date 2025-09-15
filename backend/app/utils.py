import re
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
from app.db import SessionLocal, CampaignResult, Audience

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def extract_video_id(url: str) -> str:
    m = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return m.group(1) if m else url


def parse_iso8601_duration(dur: str) -> int:
    hrs = mins = secs = 0
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", dur)
    if not m:
        return 0
    if m.group(1):
        hrs = int(m.group(1))
    if m.group(2):
        mins = int(m.group(2))
    if m.group(3):
        secs = int(m.group(3))
    return hrs * 3600 + mins * 60 + secs


def get_video_meta(video_id: str) -> dict:
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    res = youtube.videos().list(
        part="snippet,statistics,contentDetails", id=video_id
    ).execute()

    items = res.get("items", [])
    if not items:
        raise ValueError("Video not found")

    it = items[0]
    sn = it["snippet"]
    stats = it.get("statistics", {})
    cd = it.get("contentDetails", {})

    return {
        "video_id": video_id,
        "title": sn.get("title", ""),
        "description": sn.get("description", ""),
        "tags": sn.get("tags", []),
        "categoryId": sn.get("categoryId"),
        "publishedAt": sn.get("publishedAt"),
        "viewCount": int(stats.get("viewCount", 0)),
        "likeCount": int(stats.get("likeCount", 0)) if stats.get("likeCount") else None,
        "duration": parse_iso8601_duration(cd.get("duration", "PT0S")),
    }


def save_recommendations(video_id: str, recommendations: list):
    """
    Save recommendation results into campaigns table.
    Only the DB-required fields are stored.
    """
    db = SessionLocal()
    try:
        for rec in recommendations:
            campaign = CampaignResult(
                video_id=video_id,
                country=rec["country"],
                audience=rec["audience_name"],
                budget_spent=rec["suggested_budget"],
                predicted_watch_time=rec["pred_watchtime_per_dollar"],
            )
            db.add(campaign)
            exists = db.query(Audience).filter_by(
                country=rec["country"],
                interests=rec["audience_name"]
            ).first()
            if not exists:
                aud = Audience(
                    country=rec["country"],
                    interests=rec["audience_name"]
                )
                db.add(aud)
        db.commit()
    finally:
        db.close()
