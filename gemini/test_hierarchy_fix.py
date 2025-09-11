"""Test script to verify the Gemini agent fix for hierarchy queries"""

import os
from nw_agent_gemini_simple import SimpleWaterAgentGemini

def test_hierarchy_query():
    """Test the specific hierarchy query that was causing issues"""
    
    # Check if we have an API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No GOOGLE_API_KEY environment variable found")
        print("💡 Set it with: set GOOGLE_API_KEY=your-api-key")
        return False
    
    try:
        print("🧪 Testing Gemini agent with hierarchy query...")
        print("-" * 60)
        
        # Initialize agent
        agent = SimpleWaterAgentGemini(google_api_key=api_key)
        
        # Test queries that should work
        test_queries = [
            "show my plant hierarchy",
            "what is the hierarchy structure?",
            "show me the network hierarchy",
            "what locations are in the system?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: '{query}'")
            print("-" * 30)
            
            try:
                result = agent.invoke(query)
                
                if result.get('error'):
                    print(f"❌ Error: {result['content']}")
                else:
                    print(f"✅ Success!")
                    print(f"Response: {result['content'][:200]}{'...' if len(result['content']) > 200 else ''}")
                    
                    if result.get('tool_results'):
                        print(f"🔧 Tools used: {list(result['tool_results'].keys())}")
                        
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_hierarchy_query()
    
    if success:
        print("\n🎉 Testing completed!")
    else:
        print("\n⚠️ Testing failed - check your API key setup")
        
    print("\n💡 If you don't have a Google API key:")
    print("1. Go to: https://makersuite.google.com/app/apikey")
    print("2. Create a new API key")
    print("3. Set it: set GOOGLE_API_KEY=your-key-here")
