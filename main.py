from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

app=FastAPI()

class Scrape(BaseModel):
    url:str

@app.post("/scrape")
async def scrape_page(req:Scrape):
    url=req.url
    if not url:
        raise HTTPException(status_code=400,detail="URL is required")
    
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page()
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        html=page.content()
        soup=BeautifulSoup(html,"html.parser")

        visible_elements=[]
        for tag in soup.find_all(["h1","h2"])