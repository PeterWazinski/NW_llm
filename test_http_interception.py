#!/usr/bin/env python3
"""
Test script for Ollama HTTP interception
Demonstrates different methods to intercept HTTP requests to Ollama server
"""

import sys
import os
import json
from langchain_core.messages import HumanMessage

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ollama_interceptor import (
    InterceptingChatOllama, 
    create_intercepting_ollama,
    setup_global_httpx_interception
)

def test_basic_interception():
    """Test basic HTTP interception with custom ChatOllama"""
    print("🧪 Testing Basic HTTP Interception...")
    print("=" * 50)
    
    try:
        # Create intercepting Ollama client
        ollama = create_intercepting_ollama(
            base_url="http://localhost:11434",
            model="qwen2.5:7b-instruct-q4_K_M",
            method="custom_client"
        )
        
        # Test message
        message = HumanMessage(content="Hello! Please respond with just 'Hi there!' and nothing else.")
        
        print("📤 Sending test message to Ollama...")
        response = ollama.invoke([message])
        
        print(f"\n🤖 Final Response: {response.content}")
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_global_interception():
    """Test global HTTP interception by monkey patching"""
    print("\n🧪 Testing Global HTTP Interception...")
    print("=" * 50)
    
    try:
        # Setup global interception
        setup_global_httpx_interception()
        
        # Use regular ChatOllama - requests will be intercepted
        from langchain_ollama import ChatOllama
        ollama = ChatOllama(
            model="qwen2.5:7b-instruct-q4_K_M",
            base_url="http://localhost:11434"
        )
        
        # Test message
        message = HumanMessage(content="What is 2+2? Please respond with just the number.")
        
        print("📤 Sending test message with global interception...")
        response = ollama.invoke([message])
        
        print(f"\n🤖 Final Response: {response.content}")
        print("\n✅ Global interception test completed!")
        
    except Exception as e:
        print(f"❌ Global interception test failed: {e}")
        import traceback
        traceback.print_exc()

def test_with_water_agent():
    """Test HTTP interception with the actual WaterAgentLangGraph"""
    print("\n🧪 Testing HTTP Interception with WaterAgentLangGraph...")
    print("=" * 50)
    
    try:
        from nw_agent_langgraph import WaterAgentLangGraph
        
        # Create agent with HTTP interception enabled
        agent = WaterAgentLangGraph(
            llm_model="qwen2.5:7b-instruct-q4_K_M",
            run_locally=True,
            enable_http_interception=True
        )
        
        # Test if agent is ready
        if not agent.is_ready():
            print("❌ Agent is not ready!")
            return
        
        # Test query
        print("📤 Sending query to Water Agent...")
        result = agent.invoke("Hello! Just say 'Water system ready!' and nothing else.", thread_id="test-thread")
        
        print(f"\n🤖 Agent Response: {result['content']}")
        print(f"⏱️ Execution Time: {result['execution_time']:.3f}s")
        print(f"🔧 Tools Called: {result['tools_called']}")
        print("\n✅ Water Agent interception test completed!")
        
    except Exception as e:
        print(f"❌ Water Agent interception test failed: {e}")
        import traceback
        traceback.print_exc()

def display_usage_examples():
    """Display usage examples for HTTP interception"""
    print("\n📖 Usage Examples:")
    print("=" * 50)
    
    examples = [
        {
            "title": "🔍 Enable HTTP Interception in Streamlit App",
            "command": "streamlit run nw_agent_lg_app.py -- --intercept-http",
            "description": "Run the Streamlit app with HTTP request logging enabled"
        },
        {
            "title": "🌐 Remote Server with Interception",
            "command": "streamlit run nw_agent_lg_app.py -- --remote --ollama-url http://server:11434 --intercept-http",
            "description": "Use remote Ollama server with HTTP interception"
        },
        {
            "title": "🧪 Test Different Models with Interception",
            "command": "streamlit run nw_agent_lg_app.py -- --model llama3.2:latest --intercept-http",
            "description": "Test different models while monitoring HTTP traffic"
        },
        {
            "title": "📊 Programmatic Usage",
            "code": """
from ollama_interceptor import create_intercepting_ollama
from langchain_core.messages import HumanMessage

# Create intercepting client
ollama = create_intercepting_ollama(
    base_url="http://localhost:11434",
    model="qwen2.5:7b-instruct-q4_K_M"
)

# Use normally - all HTTP traffic will be logged
response = ollama.invoke([HumanMessage(content="Hello!")])
print(response.content)
            """,
            "description": "Use HTTP interception programmatically in your code"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}")
        if 'command' in example:
            print(f"   Command: {example['command']}")
        if 'code' in example:
            print(f"   Code:{example['code']}")
        print(f"   Description: {example['description']}")

def main():
    """Main test function"""
    print("🔍 Ollama HTTP Interception Test Suite")
    print("=" * 60)
    
    # Display usage examples first
    display_usage_examples()
    
    # Check if Ollama server is available
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print(f"\n✅ Ollama server is available at http://localhost:11434")
            print(f"📦 Available models: {len(response.json().get('models', []))}")
        else:
            print(f"\n⚠️ Ollama server responded with status {response.status_code}")
    except Exception as e:
        print(f"\n❌ Cannot connect to Ollama server: {e}")
        print("   Make sure Ollama is running: ollama serve")
        return
    
    # Run tests
    print("\n" + "=" * 60)
    test_basic_interception()
    test_global_interception()
    test_with_water_agent()
    
    print("\n🎉 All tests completed!")
    print("\nTo use HTTP interception in your Streamlit app:")
    print("streamlit run nw_agent_lg_app.py -- --intercept-http")

if __name__ == "__main__":
    main()