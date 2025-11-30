# BizComply AI - Project Setup Guide

## 🚀 Quick Start

### 1. Extract the ZIP File
Extract `BizComply_AI_Complete.zip` to your desired location

### 2. Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
```bash
# Copy environment template
copy .env.example .env

# Edit .env file with your API keys:
# OPENAI_API_KEY=your_openai_key
# GROQ_API_KEY=your_groq_key
# SERPER_API_KEY=your_serper_key
```

### 4. Run the Application
```bash
streamlit run app.py
```

The application will start at `http://localhost:8501`

## 🌟 Features Included

### 🤖 AI Compliance Chatbot
- **RAG Integration**: Document-based compliance answers
- **Live Web Search**: Real-time regulatory updates
- **Response Modes**: Concise/Simple/Detailed options
- **Business Profiling**: Personalized compliance guidance

### 📚 Knowledge Base
- Compliance documents in `/documents/`
- Industry-specific regulations
- Legal references and citations

### 🔧 Technical Components
- **Models**: Embeddings, LLM, compliance engines
- **Utils**: Web search, document processing
- **Config**: API keys and settings
- **Services**: Regulatory monitoring

## 📋 Requirements

- Python 3.8+
- Streamlit
- OpenAI/Groq API key (for LLM)
- Serper API key (for web search)

## 🎯 Usage

1. **Start the app**: `streamlit run app.py`
2. **Complete business profile** in the sidebar
3. **Ask compliance questions** in the chat
4. **Choose response mode** (Concise/Simple/Detailed)
5. **Get personalized guidance** for your business

## 📞 Support

For issues or questions, refer to the GitHub repository:
https://github.com/AmruthaAnoop/bizcomply

---

**BizComply AI** - Your intelligent compliance assistant! 🚀
