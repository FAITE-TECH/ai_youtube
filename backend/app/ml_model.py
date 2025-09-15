import os, joblib
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()

MODEL_PATH = os.getenv("MODEL_PATH", "./models/model_watchtime.joblib")
EMB_MODEL = SentenceTransformer('all-MiniLM-L6-v2')  # runtime load; small

def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

MODEL = load_model()

def compute_match_score(video_text, audience_embedding):
    v = EMB_MODEL.encode([video_text], normalize_embeddings=True)[0]
    a = np.array(audience_embedding)
    score = float(np.dot(v, a))
    return score

def predict_watchtime_per_dollar(match_score, budget_spent, country):
    country_IN = 1 if country=='IN' else 0
    if MODEL is None:
        country_factor = 0.6 if country=='IN' else 1.0
        return max(0.1, (match_score*10) * country_factor)
    X = np.array([[match_score, budget_spent, country_IN]])
    return float(MODEL.predict(X)[0])
