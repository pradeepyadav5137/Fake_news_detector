# 🔍 TruthLens: AI-Powered News Authenticator

An advanced machine learning application that uses AI and real-time news APIs to verify the authenticity of news articles and detect potential fake news.

## ✨ Features

- **🤖 AI-Powered Analysis**: Advanced ML model for fake news detection
- **🌐 Real-Time Verification**: Cross-references with live news APIs (Bing News, NewsAPI)
- **📊 Interactive Dashboard**: Real-time statistics and prediction analytics
- **🎨 Modern UI**: Beautiful glass-morphism design with gradient backgrounds
- **📈 Progress Tracking**: Multi-step progress indicators for better UX
- **🔒 Secure Configuration**: Environment variable support for API keys
- **📱 Responsive Design**: Works seamlessly across different screen sizes

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd fake_news_detector
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys** (optional but recommended):
   ```bash
   export BING_API_KEY="your_bing_api_key"
   export NEWSAPI_KEY="your_newsapi_key"
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Open in browser**:
   Navigate to `http://localhost:8501`

## 🎯 How to Use

1. **Enter News Article**: Paste or type the news article you want to verify
2. **Try Samples**: Use pre-loaded sample articles for quick testing
3. **Analyze**: Click the "Analyze News Article" button
4. **Review Results**: Check the confidence score and related articles
5. **View Statistics**: Monitor analytics in the sidebar dashboard

## 📊 Features Overview

### News Verification
- ML-based authenticity prediction
- Confidence scoring (0-100%)
- Multiple news source cross-referencing
- Real-time API integration

### User Interface
- Modern gradient design
- Interactive confidence gauge
- Progress tracking with status updates
- Responsive news article cards
- Statistics dashboard with charts

### Analytics Dashboard
- Total prediction count
- Real vs fake news distribution
- Weekly activity metrics
- Historical performance tracking

## 🛠️ Technical Details

### Architecture
- **Frontend**: Streamlit with custom CSS
- **Backend**: Python with scikit-learn
- **APIs**: Bing News Search, NewsAPI
- **Visualization**: Plotly for interactive charts
- **Data**: Pandas for data processing

### Dependencies
- `streamlit>=1.28.0` - Web application framework
- `pandas>=1.5.0` - Data manipulation
- `scikit-learn>=1.3.0` - Machine learning
- `joblib>=1.3.0` - Model serialization
- `requests>=2.28.0` - HTTP requests
- `plotly>=5.15.0` - Interactive visualizations
- `numpy>=1.24.0` - Numerical computing

## 🔧 Configuration

### Environment Variables
```bash
BING_API_KEY=your_bing_news_api_key
NEWSAPI_KEY=your_newsapi_key
```

### File Structure
```
fake_news_detector/
├── app.py                 # Main application
├── model95.jb            # Trained ML model
├── vectorizer95.jb       # Text vectorizer
├── requirements.txt      # Dependencies
├── log.csv              # Prediction logs
├── assets/              # Static assets
├── README.md           # Project documentation
└── IMPROVEMENTS_REPORT.md # Enhancement details
```

## 📈 Performance

- **Model Accuracy**: ~95% (based on training data)
- **Response Time**: < 3 seconds average
- **API Integration**: Dual fallback system
- **Caching**: Optimized model loading

## 🔒 Security

- Environment variable-based API key management
- Input sanitization and validation
- Secure error handling without data exposure
- No hardcoded credentials in source code

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 Changelog

### Latest Version
- ✅ Fixed duplicate function definitions
- 🔒 Added secure API key management
- 🎨 Complete UI/UX overhaul
- 📊 Interactive statistics dashboard
- 🚀 Performance optimizations
- 📱 Responsive design improvements

See `IMPROVEMENTS_REPORT.md` for detailed changes.

## ⚠️ Disclaimer

This tool is designed to assist in news verification but should not be the sole source for determining news authenticity. Always cross-reference with multiple reliable sources and use critical thinking when evaluating news content.

## 📜 License

This project is for educational and research purposes. Please ensure compliance with API terms of service when using external news APIs.

## 🆘 Support

For issues, questions, or contributions:
- Check existing issues in the repository
- Create detailed bug reports
- Include system information and error logs
- Provide steps to reproduce issues

---

Made with ❤️ for promoting media literacy and fighting misinformation.