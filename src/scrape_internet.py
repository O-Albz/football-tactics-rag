import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time

BASE_URL = "https://blogarchive.statsbomb.com"

STATSBOMB_ARTICLES = [
    # Already working
    "/articles/soccer/the-incredible-tactical-rb-leipzig-machine-part-one-a-uniquely-versatile-attack",
    "/articles/football/analyzing-defensive-structure-using-statsbombs-free-tracking-data",
    "/articles/soccer/how-statsbomb-data-helps-measure-counter-pressing",
    "/articles/soccer/another-world-cup-weekend-tactical-guide",
    "/articles/soccer/the-world-cup-of-set-pieces",
    "/articles/soccer/messi-data-biography-analysis-the-guardiola-era-2008-09-to-2011-12",
    "/articles/soccer/messi-data-biography-analysis-young-messi-2004-05-to-2007-08",
    "/articles/soccer/a-sneak-peak-at-iq-tactics-a-brief-history-of-radials-sonars-wagon-wheels-in-soccer",

    # New ones confirmed working
    "/articles/soccer/lets-talk-about-press-baybee",
    "/articles/soccer/how-do-teams-create-better-chances-2",
    "/articles/soccer/modelling-team-playing-style",
    "/articles/soccer/defensive-metrics-measuring-the-intensity-of-a-high-press",
    "/articles/soccer/the-rise-of-press-resistant-midfielders",
    "/articles/soccer/revisiting-pressure-with-statsbomb-360",
]

def scrape_article(path: str) -> dict | None:
    url = BASE_URL + path
    headers = {"User-Agent": "football-tactics-rag/1.0 (educational project)"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        if response.status_code != 200:
            print(f"Failed ({response.status_code}): {url}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("h1")
        title_text = title.get_text(strip=True) if title else path.split("/")[-1]

        # StatsBomb blog archive uses article or main tags for content
        body = soup.find("article") or soup.find("main")
        if not body:
            print(f"No body found: {url}")
            return None

        paragraphs = body.find_all("p")
        text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40)

        if len(text) < 500:
            print(f"Too short: {url}")
            return None

        return {"title": title_text, "text": text, "url": url}

    except Exception as e:
        print(f"Error: {url} — {e}")
        return None

def scrape_all(output_dir: str = "./data/documents"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for path in STATSBOMB_ARTICLES:
        print(f"Scraping: {path}")
        article = scrape_article(path)

        if article:
            slug = path.split("/")[-1][:60]
            filepath = Path(output_dir) / f"statsbomb_{slug}.md"
            content = f"# {article['title']}\n\nSource: {article['url']}\n\n{article['text']}"

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Saved: statsbomb_{slug}.md ({len(article['text'])} chars)")

        time.sleep(2)

if __name__ == "__main__":
    scrape_all()