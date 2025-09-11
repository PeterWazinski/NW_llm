#!/usr/bin/env python3
"""Test script for Google Gemini Water Agent"""

import os
from nw_agent_gemini import WaterAgentGemini

def test_gemini_agent():
    """Test the Google Gemini water agent"""
    print("🧪 Testing Google Gemini Water Agent")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY environment variable not set")
        print("💡 Please set your Google API key:")
        print("   export GOOGLE_API_KEY='your-api-key-here'")
        print("   # or on Windows:")
        print("   set GOOGLE_API_KEY=your-api-key-here")
        return
    
    try:
        # Initialize agent
        print("🔄 Initializing Gemini agent...")
        agent = WaterAgentGemini()
        print("✅ Agent initialized successfully!")
        
        # Test basic functionality
        print("\n🔍 Test: Simple greeting")
        response = agent.invoke("Hello! Can you introduce yourself?")
        
        print(f"⏱️  Execution time: {response['execution_time']:.3f}s")
        print(f"🔧 Tools called: {response['tools_called']}")
        print(f"💬 Response: {response['content'][:200]}...")
        
        print("\n✅ Gemini agent test completed!")
        
    except Exception as e:
        print(f"❌ Error testing Gemini agent: {str(e)}")

if __name__ == "__main__":
    test_gemini_agent()
