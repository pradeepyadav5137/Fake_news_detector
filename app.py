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
.sample-card { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 12px; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

def clean_text(text):
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    text = re.sub("\n", " ", text)
    return text


def extract_query(text):
    sentences = re.split(r'(?<=[.!?])\s', text)
    base = (sentences[0] + (" " + sentences[1] if len(sentences) >= 2 else "")) if sentences else text
    return base.strip().strip('"\'')[:250]


def get_news_references(article_text, num_results=3):
    query = extract_query(article_text)
    logging.info(f"Searching for references with query: {query!r}")
    results = []

    # Try Bing News API first
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

    # Try NewsAPI if Bing didn't provide enough results
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

    # Fallback if no results found
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
    st.markdown("Click any button below to load a sample article:")
    
    # Create columns for sample buttons
    cols = st.columns(2)
    sample_keys = list(SAMPLE_ARTICLES.keys())
    
    selected_sample = None
    
    with cols[0]:
        if st.button("📱 " + sample_keys[0], use_container_width=True, key="sample1"):
            st.session_state.sample_text = SAMPLE_ARTICLES[sample_keys[0]]
            selected_sample = SAMPLE_ARTICLES[sample_keys[0]]
        if st.button("🏏 " + sample_keys[1], use_container_width=True, key="sample2"):
            st.session_state.sample_text = SAMPLE_ARTICLES[sample_keys[1]]
            selected_sample = SAMPLE_ARTICLES[sample_keys[1]]
    
    with cols[1]:
        if st.button("❌ " + sample_keys[2], use_container_width=True, key="sample3"):
            st.session_state.sample_text = SAMPLE_ARTICLES[sample_keys[2]]
            selected_sample = SAMPLE_ARTICLES[sample_keys[2]]
        if st.button("🎓 " + sample_keys[3], use_container_width=True, key="sample4"):
            st.session_state.sample_text = SAMPLE_ARTICLES[sample_keys[3]]
            selected_sample = SAMPLE_ARTICLES[sample_keys[3]]
    
    return selected_sample

def render_input():
    # Get sample text from session state if available
    default_text = st.session_state.get('sample_text', "")
    return st.text_area("📰 News Article:", value=default_text, height=200, key="news_input")

def render_results(pred, conf, refs):
    # Determine result type and styling
    if refs and len([r for r in refs if r['title'] != "No references found"]) > 0:
        has_real_refs = True
    else:
        has_real_refs = False
    
    if has_real_refs and pred == 1:
        box, lbl, msg = "authentic-box", "✅ Authentic News", "This appears to be authentic news supported by multiple credible sources."
    elif has_real_refs and pred == 0:
        box, lbl, msg = "warning-box", "⚠️ Potentially Misleading", "Similar content exists but may contain misleading information. Verify carefully with sources."
    elif not has_real_refs and pred == 1:
        box, lbl, msg = "authentic-box", "✅ Likely Authentic", "Model predicts this is authentic, but no recent references found."
    else:
        box, lbl, msg = "danger-box", "❌ Likely Fake News", "This appears to be fake news. No credible sources found."

    # Display main result
    st.markdown(f'<div class="{box}"><h2>{lbl}</h2>'
                f'<p>🎯 Confidence: <strong>{conf:.0%}</strong></p>'
                f'<p>{msg}</p></div>', unsafe_allow_html=True)

    # Display related articles with improved formatting
    st.subheader("📰 Related Articles & Sources")
    
    if has_real_refs:
        # Filter out "No references found" entries
        real_refs = [r for r in refs if r['title'] != "No references found"]
        
        if len(real_refs) == 1:
            # Single column for one article
            with st.container():
                art = real_refs[0]
                render_article_card(art)
        else:
            # Multiple columns for multiple articles
            cols = st.columns(min(3, len(real_refs)))
            for i, art in enumerate(real_refs):
                with cols[i % len(cols)]:
                    render_article_card(art)
    else:
        st.info("🔍 No related news articles found. This could indicate the news is either very recent, very specific, or potentially fabricated.")

def render_article_card(art):
    """Render an individual article card with improved formatting"""
    with st.container():
        # Display image if available
        img_url = art.get("urlToImage")
        if img_url and img_url != "":
            try:
                st.image(img_url, use_container_width=True, caption=f"Source: {art['source']}")
            except:
                st.image("https://via.placeholder.com/300x150.png?text=No+Image", use_container_width=True)
        else:
            st.image("https://via.placeholder.com/300x150.png?text=No+Image", use_container_width=True)
        
        # Article title
        st.markdown(f"**{art['title']}**")
        
        # Source and date
        try:
            date_str = art['publishedAt'][:10] if art['publishedAt'] else "Unknown date"
        except:
            date_str = "Unknown date"
        
        st.caption(f"📰 {art['source']} | 📅 {date_str}")
        
        # Description
        desc = art.get("description", "")
        if desc and desc.strip():
            truncated_desc = desc[:150] + "..." if len(desc) > 150 else desc
            st.write(truncated_desc)
        
        # Read more link
        if art['url'] and art['url'] != "#":
            st.markdown(f"🔗 [Read full article]({art['url']})")
        
        st.markdown("---")

# App logic
def main():
    # Initialize session state
    if 'sample_text' not in st.session_state:
        st.session_state.sample_text = ""
    
    render_header()
    
    # Add sample section
    render_sample_section()
    
    st.markdown("---")
    
    # Input section
    text = render_input()
    
    # Clear button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.sample_text = ""
            st.rerun()
    
    with col2:
        analyze_button = st.button("🔍 Analyze News", use_container_width=True, type="primary")
    
    if analyze_button:
        if not text.strip():
            st.warning("⚠️ Please paste some text to analyze.")
            return

        with st.spinner("🔍 Analyzing article and searching for references..."):
            # Clean and process text
            cleaned = clean_text(text)
            vec = vectorizer.transform([cleaned])
            pred = model.predict(vec)[0]
            conf = model.predict_proba(vec)[0].max()
            
            # Get news references
            refs = get_news_references(text)

        # Display results
        render_results(pred, conf, refs)

        # Log prediction
        try:
            df = pd.DataFrame([{
                "timestamp": datetime.now().isoformat(),
                "prediction": "Real" if pred else "Fake",
                "confidence": conf,
                "refs": bool(refs and len([r for r in refs if r['title'] != "No references found"]) > 0)
            }])
            path = "prediction_log.csv"
            df.to_csv(path, mode='a', header=not os.path.exists(path), index=False)
        except Exception:
            logging.exception("Failed to write log")

if __name__ == "__main__":
    main()
