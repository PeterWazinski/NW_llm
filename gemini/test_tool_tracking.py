#!/usr/bin/env python3
"""
Test script to verify tool call tracking in LangGraph agent
"""

from nw_agent_langgraph import WaterAgentLangGraph

def main():
    print("🧪 Testing LangGraph Tool Call Tracking")
    print("=" * 50)
    
    try:
        # Initialize agent
        print("🔄 Initializing agent...")
        agent = WaterAgentLangGraph()
        
        if not agent.is_ready():
            print("❌ Agent is not ready!")
            return
            
        print("✅ Agent initialized successfully!")
        
        # Test 1: Simple query that should use tools
        print("\n🔍 Test 1: Query that should use get_all_locations")
        result = agent.invoke("What locations do we have?", "test_thread_1")
        
        print(f"📝 Result type: {type(result)}")
        if isinstance(result, dict):
            print(f"⏱️  Execution time: {result.get('execution_time', 0):.3f}s")
            print(f"🔧 Tools called: {result.get('tools_called', [])}")
            print(f"💬 Response preview: {result.get('content', '')[:100]}...")
        else:
            print("❌ Expected dict result, got:", type(result))
        
        # Test 2: Query that shouldn't use tools
        print("\n🔍 Test 2: Simple greeting (should use no tools)")
        result2 = agent.invoke("Hello", "test_thread_2")
        
        if isinstance(result2, dict):
            print(f"⏱️  Execution time: {result2.get('execution_time', 0):.3f}s")
            print(f"🔧 Tools called: {result2.get('tools_called', [])}")
            print(f"💬 Response preview: {result2.get('content', '')[:100]}...")
        
        print("\n✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
