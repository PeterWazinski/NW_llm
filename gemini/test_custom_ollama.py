#!/usr/bin/env python3
"""Test script to verify custom Ollama server URL configuration"""

from nw_agent_langgraph import WaterAgentLangGraph
import os

def test_custom_ollama_url():
    """Test different ways to configure Ollama server URL"""
    print("🧪 Testing Custom Ollama Server Configuration")
    print("=" * 50)
    
    # Test 1: Default configuration (local server)
    print("\n🔍 Test 1: Default configuration")
    try:
        agent = WaterAgentLangGraph()
        url = agent.ollama_base_url or "http://localhost:11434 (default)"
        print(f"✅ Agent initialized with Ollama URL: {url}")
    except Exception as e:
        print(f"❌ Failed to initialize with default config: {str(e)}")
    
    # Test 2: Custom URL via parameter
    print("\n🔍 Test 2: Custom URL via parameter")
    custom_url = "http://your-server:11434"  # Replace with your actual URL
    try:
        agent = WaterAgentLangGraph(ollama_base_url=custom_url)
        print(f"✅ Agent initialized with custom URL: {agent.ollama_base_url}")
    except Exception as e:
        print(f"❌ Failed to initialize with custom URL: {str(e)}")
    
    # Test 3: Environment variable
    print("\n🔍 Test 3: Environment variable configuration")
    os.environ['OLLAMA_BASE_URL'] = "http://env-server:11434"
    try:
        agent = WaterAgentLangGraph()
        print(f"✅ Agent initialized with env URL: {agent.ollama_base_url}")
    except Exception as e:
        print(f"❌ Failed to initialize with env URL: {str(e)}")
    finally:
        # Clean up environment variable
        if 'OLLAMA_BASE_URL' in os.environ:
            del os.environ['OLLAMA_BASE_URL']
    
    print("\n✅ Configuration tests completed!")
    print("\nTo use your Ollama server:")
    print("1. agent = WaterAgentLangGraph(ollama_base_url='http://your-server:11434')")
    print("2. Set OLLAMA_BASE_URL environment variable")

if __name__ == "__main__":
    test_custom_ollama_url()
