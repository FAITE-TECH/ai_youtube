from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import AnalyzeResponse, CampaignResultIn
from app.utils import extract_video_id, get_video_meta, save_recommendations
from app.recommender import analyze_video_and_recommend
from app.db import init_db, SessionLocal, CampaignResult
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="YouTube Promo AI")
init_db()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/analyze", response_model=AnalyzeResponse)
def analyze(url: str):
    try:
        vid = extract_video_id(url)
        meta = get_video_meta(vid)
        recs = analyze_video_and_recommend(meta, topk=3, per_audience_budget=50)

        save_recommendations(meta["video_id"], recs)

        return {
            "video_id": meta["video_id"],
            "title": meta["title"],
            "recommendations": recs,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/log_result")
def log_result(item: CampaignResultIn):
    db = SessionLocal()
    try:
        cr = CampaignResult(
            video_id=item.video_id,
            country=item.country,
            audience=item.audience,
            budget_spent=item.budget_spent,
            predicted_watch_time=item.predicted_watch_time,
        )
        db.add(cr)
        db.commit()
        db.refresh(cr)
        return {"status": "ok", "id": cr.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
