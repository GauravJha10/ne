import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal

app = FastAPI(title="Sentiment Analysis API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CommentRequest(BaseModel):
    comment: str

class SentimentResponse(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    rating: int = Field(..., ge=1, le=5)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Sentiment Analysis API (V2 Refined Mock) is running"}

@app.post("/comment", response_model=SentimentResponse)
async def analyze_sentiment(request: CommentRequest):
    text = request.comment.lower()
    
    # Enhanced keyword lists
    positive_words = ["amazing", "good", "great", "excellent", "love", "best", "wonderful", "happy", "beast", "fast", "solid", "incredible", "crisp"]
    negative_words = ["bad", "terrible", "worst", "hate", "awful", "horrible", "sad", "disappointed", "mediocre", "overcooked", "poor", "unimpressed"]
    neutral_words = ["average", "fine", "ok", "maybe", "nothing special", "not bad but", "mediocre at best"]

    # Special case for "average" or "not bad" which are often neutral
    if "average" in text or "not bad" in text or "fine" in text:
        if "not bad but" not in text and "fine" in text and len(text.split()) < 15:
             # Short "it's fine" is usually neutral
             pass
        else:
            # Check if there's more positive than negative around it
            pass

    pos_score = sum(2 if word in text else 0 for word in ["amazing", "excellent", "best", "beast", "incredible"])
    pos_score += sum(1 for word in positive_words if word in text and word not in ["amazing", "excellent", "best", "beast", "incredible"])
    
    neg_score = sum(2 if word in text else 0 for word in ["terrible", "worst", "hate", "awful", "horrible"])
    neg_score += sum(1 for word in negative_words if word in text and word not in ["terrible", "worst", "hate", "awful", "horrible"])

    # Neutrality checks
    if "average" in text or ("not" in text and "bad" in text and "but" not in text) or "mediocre" in text and pos_score == 0:
        # If it says average or not bad, and doesn't have strong positive words, it's often neutral/3
        if "mediocre" in text and "fine" not in text:
            sentiment = "negative"
            rating = 2
        else:
            sentiment = "neutral"
            rating = 3
    elif pos_score > neg_score:
        sentiment = "positive"
        if pos_score >= 3:
            rating = 5
        elif pos_score >= 1:
            rating = 4
        else:
            rating = 4
    elif neg_score > pos_score:
        sentiment = "negative"
        if neg_score >= 3:
            rating = 1
        elif neg_score >= 1:
            rating = 2
        else:
            rating = 2
    else:
        sentiment = "neutral"
        rating = 3
        
    return SentimentResponse(sentiment=sentiment, rating=rating)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
