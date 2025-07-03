# 🔍 TruthLens: AI-Powered News Authenticator

An intelligent web application that uses machine learning and real-time web search to verify the authenticity of news articles.

## ✨ Features

- **🤖 AI-Powered Detection**: Uses a trained machine learning model to classify news as authentic or fake
- **🔍 Real-time Web Search**: Searches multiple news APIs to find related articles and sources
- **🧪 Sample Testing**: Pre-loaded sample articles to test the system
- **📊 Confidence Scoring**: Shows prediction confidence levels
- **🎨 Modern UI**: Clean, intuitive interface with dark theme support
- **📝 Logging**: Tracks all predictions for analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Internet connection (for news API searches)

### Installation

1. **Clone/Download the project files**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** to `http://localhost:8501`

## 📁 Project Structure

```
├── app.py                 # Main Streamlit application
├── model95.jb            # Trained ML model (95% accuracy)
├── vectorizer95.jb       # Text vectorizer for the model
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── assets/              # Static assets (images, etc.)
└── logs/                # Prediction logs
```

## 🎯 Usage

### Testing with Samples
1. Click any of the 4 sample article buttons:
   - 📱 **Real News - Tech**: iPhone announcement
   - 🏏 **Real News - Sports**: Cricket World Cup
   - ❌ **Fake News Example**: Fictional study
   - 🎓 **Real News - Education**: University rankings

2. Click **"🔍 Analyze News"** to get results

### Custom Article Testing
1. Paste any news article text into the input area
2. Click **"🔍 Analyze News"**
3. View the authenticity prediction and related sources

### Understanding Results
- **✅ Authentic News**: High confidence, supported by sources
- **⚠️ Potentially Misleading**: Mixed signals, verify carefully
- **❌ Likely Fake News**: Low confidence, no credible sources found

## 🔧 Technical Details

### Machine Learning Model
- **Type**: Classification model
- **Accuracy**: 95%
- **Features**: Text preprocessing, TF-IDF vectorization
- **Training**: Trained on curated dataset of real/fake news

### News APIs
- **Bing News API**: Primary source for recent articles
- **NewsAPI**: Secondary source for comprehensive coverage
- **Fallback**: Graceful handling when APIs are unavailable

### Text Processing
- Lowercasing and punctuation removal
- Query extraction from article content
- Smart search term generation

## 🛠️ Configuration

### API Keys
The app includes demo API keys for testing. For production use:

1. Get your own API keys:
   - [Bing News API](https://rapidapi.com/microsoft-azure-org-microsoft-cognitive-services/api/bing-news-search1/)
   - [NewsAPI](https://newsapi.org/)

2. Replace the keys in `app.py`:
   ```python
   subscription_key = "YOUR_BING_API_KEY"
   NEWSAPI_KEY = "YOUR_NEWSAPI_KEY"
   ```

## 📊 Model Performance

- **Training Accuracy**: 95%
- **Precision**: High accuracy in detecting fake news
- **Recall**: Effective at identifying authentic sources
- **F1-Score**: Balanced performance across metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🔮 Future Enhancements

- [ ] Real-time learning from user feedback
- [ ] Support for multiple languages
- [ ] Social media integration
- [ ] Bias detection capabilities
- [ ] Fact-checking integration
- [ ] Mobile app version

## 🆘 Support

If you encounter any issues:

1. Check the requirements are installed correctly
2. Ensure you have an active internet connection
3. Verify the model files are present
4. Check the console for error messages

## 🎉 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [scikit-learn](https://scikit-learn.org/)
- News data from Bing News API and NewsAPI
- UI icons from various emoji sets

---

**Made with ❤️ for fighting misinformation**