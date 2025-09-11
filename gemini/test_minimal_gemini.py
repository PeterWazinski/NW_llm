"""Simple test for Google Gemini integration without complex imports"""

# Test minimal Gemini API functionality
def test_minimal_gemini():
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing google.generativeai: {e}")
        return False

def test_langchain_google():
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ LangChain Google Genai imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing langchain_google_genai: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Google Gemini Integration...")
    print("-" * 50)
    
    test1 = test_minimal_gemini()
    test2 = test_langchain_google()
    
    if test1 and test2:
        print("\n🎉 All basic imports successful!")
        print("💡 You can now use the Gemini agent with a valid API key.")
    else:
        print("\n⚠️  Some imports failed. You may need to resolve dependencies.")
    
    print("\n📚 Next steps:")
    print("1. Get a Google API key from: https://makersuite.google.com/app/apikey")
    print("2. Set environment variable: set GOOGLE_API_KEY=your-key-here")
    print("3. Test with: python test_gemini_agent.py")
    print("4. Run Streamlit app: streamlit run nw_agent_gemini_app.py")
