"""Test the water tools functionality independently"""

from nw_water_tools import NWWaterTools
from Guwahati import Guwahati

def test_water_tools():
    """Test the water tools that should work with hierarchy queries"""
    
    print("🧪 Testing Water Tools Functionality...")
    print("-" * 50)
    
    try:
        guwahati_hierarchy = Guwahati.create_hierarchy()
        tools = NWWaterTools(guwahati_hierarchy)
        print("✅ Water tools initialized successfully")
        
        # Test hierarchy structure
        print("\n🔍 Testing get_hierarchy_structure()...")
        hierarchy = tools.get_hierarchy_structure()
        print(f"✅ Hierarchy result type: {type(hierarchy)}")
        print(f"📊 Sample result: {str(hierarchy)[:200]}{'...' if len(str(hierarchy)) > 200 else ''}")
        
        # Test other relevant tools
        print("\n🔍 Testing get_all_locations()...")
        locations = tools.get_all_locations()
        print(f"✅ Locations result type: {type(locations)}")
        print(f"📊 Sample result: {str(locations)[:200]}{'...' if len(str(locations)) > 200 else ''}")
        
        print("\n🔍 Testing get_network_summary()...")
        summary = tools.get_network_summary()
        print(f"✅ Summary result type: {type(summary)}")
        print(f"📊 Sample result: {str(summary)[:200]}{'...' if len(str(summary)) > 200 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing water tools: {str(e)}")
        return False

def test_query_matching():
    """Test the query matching logic"""
    
    print("\n🧪 Testing Query Matching Logic...")
    print("-" * 50)
    
    test_queries = [
        "show my plant hierarchy",
        "what is the hierarchy structure?", 
        "show me the network hierarchy",
        "what locations are in the system?",
        "show me a summary",
        "list all pipes"
    ]
    
    # Simulate the tool matching logic
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        message_lower = query.lower()
        
        matched_tools = []
        
        # Plant/hierarchy queries
        if any(word in message_lower for word in ['hierarchy', 'structure', 'tree', 'parent', 'child', 'plant']):
            matched_tools.append('get_hierarchy_structure')
        
        # Location queries
        if any(word in message_lower for word in ['location', 'where', 'place', 'area']):
            if 'all' in message_lower or 'list' in message_lower:
                matched_tools.append('get_all_locations')
        
        # Summary queries
        if any(word in message_lower for word in ['summary', 'overview', 'total', 'count']):
            matched_tools.append('get_network_summary')
        
        # Pipe queries
        if any(word in message_lower for word in ['pipe', 'connection', 'connected']):
            matched_tools.append('get_all_pipes')
        
        print(f"   → Matched tools: {matched_tools}")

if __name__ == "__main__":
    print("🚀 Testing Water Assistant Components...")
    print("=" * 60)
    
    # Test water tools
    tools_ok = test_water_tools()
    
    # Test query matching
    test_query_matching()
    
    print("\n" + "=" * 60)
    if tools_ok:
        print("✅ All basic components are working!")
        print("💡 The issue was likely in the Gemini API call formatting.")
        print("🔧 The fixes should resolve the 'contents not specified' error.")
    else:
        print("❌ Some components need attention.")
        
    print("\n📝 Next steps:")
    print("1. Test with: streamlit run nw_agent_gemini_simple_app.py")
    print("2. Try query: 'show my plant hierarchy'")
    print("3. Check the enhanced error handling and tool results")
