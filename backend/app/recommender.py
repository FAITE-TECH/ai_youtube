import json, os
from app.ml_model import compute_match_score, predict_watchtime_per_dollar
from dotenv import load_dotenv
load_dotenv()
AUD_FILE = os.path.join(os.path.dirname(__file__), "audiences.json")

with open(AUD_FILE) as f:
    AUDIENCES = json.load(f)

def analyze_video_and_recommend(video_meta, topk=3, per_audience_budget=50):
    video_text = video_meta['title'] + " " + video_meta['description'] + " " + " ".join(video_meta.get('tags',[]))
    recs=[]
    for a in AUDIENCES:
        score = compute_match_score(video_text, a['embedding'])
        predicted = predict_watchtime_per_dollar(score, per_audience_budget, a['country'])
        recs.append({
            'audience_id': a['id'],
            'audience_name': a['name'],
            'country': a['country'],
            'match_score': score,
            'pred_watchtime_per_dollar': predicted,
            'suggested_budget': per_audience_budget
        })
    recs = sorted(recs, key=lambda x: x['match_score'], reverse=True)[:topk]
    return recs
