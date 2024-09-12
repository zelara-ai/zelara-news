from fastapi import FastAPI, HTTPException
from src.lib.fetch import scrape_news

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Plant News API"}

@app.get("/api/news")
def get_news():
    articles = scrape_news()
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found")
    return {"articles": articles}
