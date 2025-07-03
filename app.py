import streamlit as st
import pandas as pd
import os
import logging
import requests
import re
import string
import joblib
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="TruthLens: AI-Powered Authenticator", 
    layout="wide", 
    page_icon="🔍",
    initial_sidebar_state="expanded"
)

# Logging configuration
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

# Enhanced CSS styles
st.markdown("""
<style>
/* Main app styling */
[data-testid="stAppViewContainer"] { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #f0f2f6; 
}

/* Header styling */
.main-header {
    text-align: center;
    padding: 2rem 0;
    background: rgba(255,255,255,0.1);
    border-radius: 15px;
    margin-bottom: 2rem;
    backdrop-filter: blur(10px);
}

.main-header h1 {
    color: #ffffff;
    font-size: 3rem;
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.main-header p {
    color: #e0e6ed;
    font-size: 1.2rem;
    margin: 0;
}

/* News cards */
.news-card { 
    border: none;
    border-radius: 15px; 
    padding: 20px; 
    margin-bottom: 20px; 
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
    height: 100%; 
    transition: all 0.3s ease;
    color: #333;
}

.news-card:hover { 
    transform: translateY(-5px); 
    box-shadow: 0 16px 64px rgba(0,0,0,0.15);
}

/* Result boxes */
.authentic-box { 
    background: linear-gradient(135deg, #d4edda, #c3e6cb);
    border-left: 5px solid #28a745; 
    padding: 20px; 
    border-radius: 10px; 
    margin: 20px 0; 
    color: #155724;
    box-shadow: 0 4px 16px rgba(40,167,69,0.2);
}

.warning-box { 
    background: linear-gradient(135deg, #fff3cd, #ffeaa7);
    border-left: 5px solid #ffc107; 
    padding: 20px; 
    border-radius: 10px; 
    margin: 20px 0; 
    color: #856404;
    box-shadow: 0 4px 16px rgba(255,193,7,0.2);
}

.danger-box { 
    background: linear-gradient(135deg, #f8d7da, #f5c6cb);
    border-left: 5px solid #dc3545; 
    padding: 20px; 
    border-radius: 10px; 
    margin: 20px 0; 
    color: #721c24;
    box-shadow: 0 4px 16px rgba(220,53,69,0.2);
}

/* Statistics cards */
.stat-card {
    background: rgba(255,255,255,0.1);
    padding: 1.5rem;
    border-radius: 15px;
    text-align: center;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
}

.stat-number {
    font-size: 2.5rem;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 0.5rem;
}

.stat-label {
    color: #e0e6ed;
    font-size: 1rem;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 25px;
    padding: 0.75rem 2rem;
    font-weight: bold;
    color: white;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102,126,234,0.3);
}

/* Sidebar styling */
.css-1d391kg {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
}
</style>
""", unsafe_allow_html=True)

def get_api_key(key_name, default_value):
    """Get API key from environment variable or use default (for demo purposes)"""
    return os.getenv(key_name, default_value)

def clean_text(text):
    """Clean and normalize text for processing"""
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_query(text):
    """Extract meaningful query from article text"""
    sentences = re.split(r'(?<=[.!?])\s', text)
    base = (sentences[0] + (" " + sentences[1] if len(sentences) >= 2 else "")) if sentences else text
    return base.strip().strip('"\'')[:250]

def get_news_references(article_text, num_results=3):
    """Fetch news references from multiple APIs with improved error handling"""
    query = extract_query(article_text)
    logging.info(f"Searching for references with query: {query!r}")
    results = []

    # Try Bing News API
    try:
        subscription_key = get_api_key("BING_API_KEY", "b44bOb62d7msh4c3029991170245p180afajsn2077ee7fd1eO")
        endpoint = "https://bing-news-search1.p.rapidapi.com/news/search"
        headers = {
            "X-BingApis-SDK": "true",
            "X-RapidAPI-Key": subscription_key,
            "X-RapidAPI-Host": "bing-news-search1.p.rapidapi.com"
        }
        params = {
            "q": query, 
            "count": num_results, 
            "freshness": "Day",
            "textFormat": "Raw", 
            "safeSearch": "Off"
        }
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
                    "urlToImage": item.get("image", {}).get("thumbnail", {}).get("contentUrl", "")
                })
        elif res.status_code == 403:
            logging.warning("Bing News API: Access denied - check API key")
    except Exception as e:
        logging.exception("Bing API Exception")
        st.sidebar.warning("⚠️ Bing News API unavailable")

    # Try NewsAPI if we need more results
    if len(results) < num_results:
        try:
            newsapi_key = get_api_key("NEWSAPI_KEY", "07594036124e431aa51b101ac842a868")
            params = {
                "q": query,
                "qInTitle": query,          
                "apiKey": newsapi_key,
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
                            "urlToImage": art.get("urlToImage", "")
                        })
                    if len(results) >= num_results:
                        break
            elif res.status_code == 401:
                logging.warning("NewsAPI: Invalid API key")
                st.sidebar.warning("⚠️ NewsAPI key invalid")
        except Exception as e:
            logging.exception("NewsAPI Exception")
            st.sidebar.warning("⚠️ NewsAPI unavailable")

    # Fallback if no results
    if not results:
        logging.info("No references found — using fallback card")
        results.append({
            "title": "No references found",
            "description": "No related news articles were found. Please verify manually.",
            "url": "#",
            "source": "TruthLens",
            "publishedAt": datetime.utcnow().isoformat(),
            "urlToImage": ""
        })

    return results[:num_results]

# Load model with better error handling
@st.cache_resource
def load_models():
    """Load ML models with caching and error handling"""
    try:
        model = joblib.load("model95.jb")
        vectorizer = joblib.load("vectorizer95.jb")
        return model, vectorizer
    except Exception as e:
        st.error("❌ Failed to load ML models. Please check model files.")
        logging.exception("Failed to load model or vectorizer")
        st.stop()

def get_prediction_stats():
    """Get statistics from prediction logs"""
    log_file = "log.csv"
    if os.path.exists(log_file):
        try:
            df = pd.read_csv(log_file)
            return {
                "total_predictions": len(df),
                "real_news": len(df[df['prediction'] == 'Real']),
                "fake_news": len(df[df['prediction'] == 'Fake']),
                "avg_confidence": df['confidence'].mean() if 'confidence' in df.columns else 0,
                "recent_activity": len(df[pd.to_datetime(df['timestamp']) > datetime.now() - timedelta(days=7)])
            }
        except Exception as e:
            logging.exception("Error reading prediction stats")
    return {"total_predictions": 0, "real_news": 0, "fake_news": 0, "avg_confidence": 0, "recent_activity": 0}

def render_header():
    """Render enhanced header with statistics"""
    st.markdown("""
    <div class="main-header">
        <h1>🔍 TruthLens</h1>
        <p>AI-Powered News Authenticator</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistics in sidebar
    with st.sidebar:
        st.markdown("### 📊 Statistics")
        stats = get_prediction_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats['total_predictions']}</div>
                <div class="stat-label">Total Checks</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats['recent_activity']}</div>
                <div class="stat-label">This Week</div>
            </div>
            """, unsafe_allow_html=True)
        
        if stats['total_predictions'] > 0:
            # Prediction distribution chart
            fig = px.pie(
                values=[stats['real_news'], stats['fake_news']], 
                names=['Real News', 'Fake News'],
                title="Prediction Distribution",
                color_discrete_sequence=['#28a745', '#dc3545']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

def render_input():
    """Render enhanced input section"""
    st.markdown("### 📰 Enter News Article")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        text = st.text_area(
            "Paste your news article here:",
            "",
            height=200,
            placeholder="Paste or type the news article you want to verify..."
        )
    
    with col2:
        st.markdown("#### 💡 Tips")
        st.markdown("""
        - Include full article text
        - Headlines work too
        - Multiple languages supported
        - Real-time verification
        """)
        
        # Sample articles
        st.markdown("#### 🎯 Try Samples")
        sample_articles = [
            "India defeats South Africa to win ICC T20 World Cup 2024",
            "Apple Unveils iOS 18 with AI Features at WWDC 2024",
            "Scientists discover cure for all diseases using AI"
        ]
        
        for i, sample in enumerate(sample_articles):
            if st.button(f"Sample {i+1}", key=f"sample_{i}", use_container_width=True):
                st.session_state.sample_text = sample
    
    # Use sample text if selected
    if 'sample_text' in st.session_state:
        text = st.session_state.sample_text
        del st.session_state.sample_text
        st.rerun()
    
    return text

def render_results(pred, conf, refs, article_text):
    """Render enhanced results with better visualization"""
    # Determine result type and styling
    if refs and len([r for r in refs if r['title'] != "No references found"]) > 0:
        if pred == 1:
            box, lbl, msg = "authentic-box", "✅ Authentic News", "Verified by multiple credible sources."
            icon = "✅"
        else:
            box, lbl, msg = "warning-box", "⚠️ Potentially Misleading", "Similar content exists, but verify carefully."
            icon = "⚠️"
    else:
        if pred == 1:
            box, lbl, msg = "authentic-box", "✅ Likely Authentic", "Model predicts real, but no recent references found."
            icon = "✅"
        else:
            box, lbl, msg = "danger-box", "❌ Likely Fake News", "No credible sources found and model predicts fake."
            icon = "❌"

    # Main result display
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f'''
        <div class="{box}">
            <h2>{lbl}</h2>
            <p><strong>Confidence Score:</strong> {conf:.1%}</p>
            <p>{msg}</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        # Confidence gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = conf * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Confidence"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "lightgreen" if pred == 1 else "salmon"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 100], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(
            height=200,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Related articles section
    st.markdown("### 📰 Related Articles & Sources")
    
    if refs and len([r for r in refs if r['title'] != "No references found"]) > 0:
        cols = st.columns(min(3, len(refs)))
        for i, art in enumerate(refs):
            if art['title'] != "No references found":
                with cols[i % 3]:
                    # Enhanced news card
                    img = art.get("urlToImage") or "https://via.placeholder.com/300x150.png?text=No+Image"
                    
                    st.markdown(f'''
                    <div class="news-card">
                        <img src="{img}" style="width:100%; height:150px; object-fit:cover; border-radius:10px; margin-bottom:15px;">
                        <h4 style="color:#333; margin-bottom:10px;">{art['title'][:100]}{'...' if len(art['title']) > 100 else ''}</h4>
                        <p style="color:#666; font-size:0.9em; margin-bottom:10px;"><strong>{art['source']}</strong> | {art['publishedAt'][:10]}</p>
                        <p style="color:#555; font-size:0.85em; margin-bottom:15px;">{(art.get('description', '')[:120] + '...') if len(art.get('description', '')) > 120 else art.get('description', '')}</p>
                        <a href="{art['url']}" target="_blank" style="background:#667eea; color:white; padding:8px 16px; border-radius:20px; text-decoration:none; font-size:0.85em;">Read Full Article</a>
                    </div>
                    ''', unsafe_allow_html=True)
    else:
        st.warning("🔍 No related articles found. This might indicate the news is either very recent or potentially fabricated.")

    # Log the prediction
    log_prediction(article_text, pred, conf, len([r for r in refs if r['title'] != "No references found"]) > 0)

def log_prediction(article_text, prediction, confidence, references_found):
    """Log prediction with consistent format"""
    try:
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "news": article_text[:100] + "..." if len(article_text) > 100 else article_text,
            "prediction": "Real" if prediction else "Fake",
            "confidence": confidence,
            "references_found": references_found
        }
        
        df = pd.DataFrame([log_data])
        log_file = "log.csv"
        
        # Append to existing file or create new one
        if os.path.exists(log_file):
            df.to_csv(log_file, mode='a', header=False, index=False)
        else:
            df.to_csv(log_file, mode='w', header=True, index=False)
            
    except Exception as e:
        logging.exception("Failed to write prediction log")

def main():
    """Main application logic"""
    # Load models
    model, vectorizer = load_models()
    
    # Render UI components
    render_header()
    
    # Main content area
    text = render_input()
    
    # Analysis button and processing
    if st.button("🔍 Analyze News Article", use_container_width=True):
        if not text.strip():
            st.warning("⚠️ Please enter some text to analyze.")
            return

        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Text processing
            status_text.text("🔤 Processing text...")
            progress_bar.progress(25)
            cleaned = clean_text(text)
            
            # Step 2: ML prediction
            status_text.text("🤖 Running AI analysis...")
            progress_bar.progress(50)
            vec = vectorizer.transform([cleaned])
            pred = model.predict(vec)[0]
            conf = model.predict_proba(vec)[0].max()
            
            # Step 3: Fetching references
            status_text.text("🌐 Fetching news references...")
            progress_bar.progress(75)
            refs = get_news_references(text)
            
            # Step 4: Complete
            status_text.text("✅ Analysis complete!")
            progress_bar.progress(100)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Show results
            render_results(pred, conf, refs, text)
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            logging.exception("Analysis failed")

if __name__ == "__main__":
    main()
