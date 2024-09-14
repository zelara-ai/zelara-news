from fastapi import FastAPI, HTTPException
from lib.fetch import get_news_for_client

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Plant News API"}

@app.get("/api/news")
def get_news():
    articles = get_news_for_client()
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found")
    return {"articles": articles}
