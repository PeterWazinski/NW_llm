# Google Gemini Setup Guide

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install langchain-google-genai google-generativeai
```

### 2. Get Google API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key for use in your application

### 3. Set Environment Variable
```bash
# Linux/Mac
export GOOGLE_API_KEY="your-api-key-here"

# Windows
set GOOGLE_API_KEY=your-api-key-here
```

### 4. Test the Agent
```bash
python test_gemini_agent.py
```

### 5. Run the Streamlit App
```bash
streamlit run nw_agent_gemini_app.py
```

## 📋 Files Created

### Core Agent Files
- **`nw_agent_gemini.py`** - Main agent class using Google Gemini
- **`nw_agent_gemini_app.py`** - Streamlit web interface for Gemini agent

### Testing & Support
- **`test_gemini_agent.py`** - Test script for Gemini agent
- **`requirements_gemini.txt`** - Additional dependencies for Gemini
- **`GEMINI_SETUP.md`** - This setup guide

## 🔧 Usage Examples

### Basic Usage
```python
from nw_agent_gemini import WaterAgentGemini

# Initialize with API key
agent = WaterAgentGemini(google_api_key="your-api-key")

# Use with environment variable
agent = WaterAgentGemini()  # Uses GOOGLE_API_KEY env var

# Ask questions
response = agent.invoke("What locations are in the water system?")
print(response['content'])
```

### Advanced Usage
```python
# Initialize with specific model
agent = WaterAgentGemini()
agent.gemini_model = "gemini-1.5-pro"  # For more complex tasks

# Use with thread ID for memory
response = agent.invoke("Hello", thread_id="user123")
```

## 🎯 Model Options

- **gemini-1.5-flash** (default) - Fast, efficient for most tasks
- **gemini-1.5-pro** - More powerful, better for complex reasoning
- **gemini-pro** - Previous generation model

## 🔒 Security Notes

- Never commit API keys to version control
- Use environment variables for production
- Rotate API keys regularly
- Monitor usage in Google Cloud Console

## 🐛 Troubleshooting

### Common Issues
1. **API Key Error**: Verify your key is correct and has proper permissions
2. **Import Error**: Ensure `langchain-google-genai` is installed
3. **Rate Limits**: Gemini has usage quotas - check your limits
4. **Model Not Available**: Verify the model name is correct

### Debug Commands
```bash
# Test API key
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('API key works!')"

# Check installed packages
pip list | grep -E "(langchain|google)"
```

## 📚 Additional Resources

- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [LangChain Google Integration](https://python.langchain.com/docs/integrations/chat/google_generative_ai)
- [Usage & Pricing](https://ai.google.dev/pricing)
