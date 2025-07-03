import streamlit as st
import pandas as pd
import os
import logging
import requests
import re
import string
import joblib
from datetime import datetime, timedelta


st.set_page_config(page_title="TruthLens: AI-Powered Authenticator", layout="wide", page_icon="🔍")


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")


st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0e1117; color: #f0f2f6; }
.news-card { border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; margin-bottom: 20px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.05); background-color: white; height: 100%; transition: all 0.3s ease; }
.news-card:hover { transform: translateY(-3px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
.authentic-box { background-color: #e8f5e9; border-left: 5px solid #4caf50; padding: 15px; border-radius: 5px; margin: 20px 0; color: #000; }
.warning-box { background-color: #fffde7; border-left: 5px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0; color: #000; }
.danger-box { background-color: #ffebee; border-left: 5px solid #f44336; padding: 15px; border-radius: 5px; margin: 20px 0; color: #000; }
</style>
""", unsafe_allow_html=True)

def clean_text(text):
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    text = re.sub("\n", " ", text)
    return text


def extract_query(text):
    sentences = re.split(r'(?<=[.!?])\s', text)
    if len(sentences) >= 2:
        return f"{sentences[0]} {sentences[1]}"
    return text[:250]


def extract_query(text):
   
    sentences = re.split(r'(?<=[.!?])\s', text)
    base = (sentences[0] + (" " + sentences[1] if len(sentences) >= 2 else "")) if sentences else text
    return base.strip().strip('"\'')[:250]

def get_news_references(article_text, num_results=3):
    query = extract_query(article_text)
    logging.info(f"Searching for references with query: {query!r}")
    results = []

  
    try:
        subscription_key = "b44bOb62d7msh4c3029991170245p180afajsn2077ee7fd1eO"
        endpoint = "https://bing-news-search1.p.rapidapi.com/news/search"
        headers = {
            "X-BingApis-SDK": "true",
            "X-RapidAPI-Key": subscription_key,
            "X-RapidAPI-Host": "bing-news-search1.p.rapidapi.com"
        }
        params = {"q": query, "count": num_results, "freshness": "Day",
                  "textFormat": "Raw", "safeSearch": "Off"}
        res = requests.get(endpoint, headers=headers, params=params, timeout=10)
        logging.debug(f"[Bing] {res.status_code} → {res.text}")
        if res.status_code == 200:
            for item in res.json().get('value', [])[:num_results]:
                results.append({
                    "title": item["name"],
                    "description": item["description"],
                    "url": item["url"],
                    "source": item["provider"][0]["name"],
                    "publishedAt": item["datePublished"],
                    "urlToImage": item.get("image",{}).get("thumbnail",{}).get("contentUrl","")
                })
        elif res.status_code == 403:
            logging.warning("Bing News API: not subscribed — skipping.")
    except Exception:
        logging.exception("Bing API Exception")

   
    if len(results) < num_results:
        try:
            NEWSAPI_KEY = "07594036124e431aa51b101ac842a868"
            params = {
                "q": query,
                "qInTitle": query,          
                "apiKey": NEWSAPI_KEY,
                "pageSize": num_results,
                "sortBy": "publishedAt",
                "language": "en"
            }
            res = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
            logging.debug(f"[NewsAPI] {res.status_code} → {res.text}")
            if res.status_code == 200:
                candidates = res.json().get("articles", [])
                # Post-filter: require at least one key term (e.g. “t20”, “world”, “cup”)
                key_terms = {t.lower() for t in re.findall(r"\w+", query)}
                for art in candidates:
                    title_l = art["title"].lower()
                    if any(term in title_l for term in key_terms):
                        results.append({
                            "title": art["title"],
                            "description": art["description"] or "",
                            "url": art["url"],
                            "source": art["source"]["name"],
                            "publishedAt": art["publishedAt"],
                            "urlToImage": art.get("urlToImage","")
                        })
                    if len(results) >= num_results:
                        break
        except Exception:
            logging.exception("NewsAPI Exception")

    # ——————————
    # 3) Fallback
    if not results:
        logging.info("No references found — using fallback card")
        results.append({
            "title": "No references found",
            "description": "No related news articles were found. Please verify manually.",
            "url": "#",
            "source": "NewsVerifi",
            "publishedAt": datetime.utcnow().isoformat(),
            "urlToImage": ""
        })

    return results[:num_results]


# Load model
try:
    model = joblib.load("model95.jb")
    vectorizer = joblib.load("vectorizer95.jb")
except Exception:
    st.error("❌ Model loading failed.")
    logging.exception("Failed to load model or vectorizer")
    st.stop()

# Sample news articles for testing
SAMPLE_ARTICLES = {
    "Real News - Tech": "Apple announces new iPhone 15 with USB-C port, replacing Lightning connector. The tech giant revealed the new device at their annual September event, featuring improved cameras and performance. The switch to USB-C comes after EU regulations requiring standardized charging ports.",
    
    "Real News - Sports": "India defeats South Africa to win ICC T20 World Cup 2024. The victory came in a thrilling final match in Barbados, with Virat Kohli playing a crucial innings. This marks India's second T20 World Cup title after their 2007 triumph.",
    
    "Fake News Example": "Scientists discover that drinking coffee made from blue beans can make people live up to 200 years. The study, conducted by the fictional University of Atlantis, claims that these magical beans contain immortality compounds that reverse aging at the cellular level.",
    
    "Real News - Education": "India rises in QS World University Rankings 2026, reflecting progress in global education and research. IIT Delhi achieved its best-ever ranking at joint 123rd position, while 54 Indian institutions were featured in the rankings, up from 46 last year."
}

# UI Components
def render_header():
    st.title("🔍 TruthLens: AI-Powered News Authenticator")
    st.caption("Paste an article below and let AI + live APIs verify it.")

def render_sample_section():
    st.subheader("🧪 Try Sample Articles")
    
    # Create columns for sample buttons
    cols = st.columns(2)
    sample_keys = list(SAMPLE_ARTICLES.keys())
    
    selected_sample = None
    
    with cols[0]:
        if st.button("📱 " + sample_keys[0], use_container_width=True):
            selected_sample = SAMPLE_ARTICLES[sample_keys[0]]
        if st.button("🏏 " + sample_keys[1], use_container_width=True):
            selected_sample = SAMPLE_ARTICLES[sample_keys[1]]
    
    with cols[1]:
        if st.button("❌ " + sample_keys[2], use_container_width=True):
            selected_sample = SAMPLE_ARTICLES[sample_keys[2]]
        if st.button("🎓 " + sample_keys[3], use_container_width=True):
            selected_sample = SAMPLE_ARTICLES[sample_keys[3]]
    
    return selected_sample

def render_input():
    return st.text_area("📰 News Article:", "", height=200)

def render_results(pred, conf, refs):
    if refs and pred == 1:
        box, lbl, msg = "authentic-box", "✅ Authentic News", "Supported by multiple sources."
    elif refs and pred == 0:
        box, lbl, msg = "warning-box", "⚠️ Potentially Misleading", "Similar content exists, verify carefully."
    elif not refs and pred == 1:
        box, lbl, msg = "authentic-box", "✅ Likely Authentic", "Model predicts real but no refs found."
    else:
        box, lbl, msg = "danger-box", "❌ Likely Fake News", "No credible sources found."

    st.markdown(f'<div class="{box}"><h2>{lbl}</h2>'
                f'<p>Confidence: <strong>{conf:.0%}</strong></p>'
                f'<p>{msg}</p></div>', unsafe_allow_html=True)

    st.subheader("📰 Related Articles")
    cols = st.columns(min(3, len(refs)))
    for i, art in enumerate(refs):
        with cols[i]:
            img = art.get("urlToImage") or "https://via.placeholder.com/300x150.png?text=No+Image"
            st.image(img, use_container_width=True)
            st.markdown(f"**{art['title']}**")
            st.caption(f"{art['source']} | {art['publishedAt'][:10]}")
            desc = art.get("description", "")
            st.write(desc[:100] + "..." if len(desc)>100 else desc)
            st.markdown(f"[Read more]({art['url']})")

# App logic
def main():
    render_header()
    text = render_input()
    if st.button("Analyze News", use_container_width=True):
        if not text.strip():
            st.warning("Please paste some text.")
            return

        with st.spinner("Analyzing…"):
            cleaned = clean_text(text)
            vec = vectorizer.transform([cleaned])
            pred = model.predict(vec)[0]
            conf = model.predict_proba(vec)[0].max()
            refs = get_news_references(text)

        render_results(pred, conf, refs)

        
        try:
            df = pd.DataFrame([{
                "timestamp": datetime.now().isoformat(),
                "prediction": "Real" if pred else "Fake",
                "confidence": conf,
                "refs": bool(refs)
            }])
            path = "prediction_log.csv"
            df.to_csv(path, mode='a', header=not os.path.exists(path), index=False)
        except Exception:
            logging.exception("Failed to write log")

if __name__ == "__main__":
    main()
