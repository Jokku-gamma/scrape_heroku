from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str

@app.post("/scrape")
async def scrape_page(request: ScrapeRequest):
    url = request.url
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state('domcontentloaded')
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        visible_elements = []
        for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "a", "button"]):
            if tag.name == "a" and tag.get("href"):
                visible_elements.append({"type": "link", "text": tag.text.strip(), "url": tag.get("href")})
            elif tag.name == "button":
                visible_elements.append({"type": "button", "text": tag.text.strip()})
            elif tag.name == "div":
                visible_elements.append({"type": "div", "text": tag.text.strip()})
            elif tag.name == "p":
                visible_elements.append({"type": "paragraph", "text": tag.text.strip()})
            else:
                visible_elements.append({"type": tag.name, "text": tag.text.strip()})

        browser.close()

    return {"visible_elements": visible_elements}
