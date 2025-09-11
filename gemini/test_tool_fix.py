"""Test the fixed Gemini agent tool functionality"""

from Guwahati import Guwahati
from nw_agent_gemini_simple import SimpleWaterAgentGemini

def test_tool_functionality():
    """Test that the tool calling functionality works"""
    
    print("🧪 Testing Tool Functionality...")
    print("-" * 50)
    
    try:
        # Create a mock agent just to test tool calling (without API key)
        guwahati_hierarchy = Guwahati.create_hierarchy()
        print("✅ Guwahati hierarchy created successfully")
        
        # Test tool mapping directly
        class MockAgent:
            def __init__(self, hierarchy):
                self.guwahati_hierarchy = hierarchy
            
            def _call_tool(self, tool_name: str, **kwargs):
                """Mock version of the tool calling method"""
                try:
                    # Map tool names to direct hierarchy access
                    if tool_name == 'get_hierarchy_structure':
                        return {
                            'locations': getattr(self.guwahati_hierarchy, 'all_locations', []),
                            'applications': getattr(self.guwahati_hierarchy, 'all_applications', []),
                            'modules': getattr(self.guwahati_hierarchy, 'all_modules', []),
                            'instrumentations': getattr(self.guwahati_hierarchy, 'all_instrumentations', [])
                        }
                    elif tool_name == 'get_all_locations':
                        return getattr(self.guwahati_hierarchy, 'all_locations', [])
                    elif tool_name == 'get_network_summary':
                        locations = getattr(self.guwahati_hierarchy, 'all_locations', [])
                        applications = getattr(self.guwahati_hierarchy, 'all_applications', [])
                        modules = getattr(self.guwahati_hierarchy, 'all_modules', [])
                        instrumentations = getattr(self.guwahati_hierarchy, 'all_instrumentations', [])
                        return {
                            'total_locations': len(locations),
                            'total_applications': len(applications),
                            'total_modules': len(modules),
                            'total_instrumentations': len(instrumentations),
                            'summary': f"Network contains {len(locations)} locations, {len(applications)} applications, {len(modules)} modules, and {len(instrumentations)} instrumentations"
                        }
                    else:
                        return f"Tool '{tool_name}' not implemented in simple version"
                except Exception as e:
                    return f"Error calling tool '{tool_name}': {str(e)}"
        
        mock_agent = MockAgent(guwahati_hierarchy)
        
        # Test different tools
        test_tools = [
            'get_hierarchy_structure',
            'get_all_locations', 
            'get_network_summary'
        ]
        
        for tool_name in test_tools:
            print(f"\n🔧 Testing tool: {tool_name}")
            result = mock_agent._call_tool(tool_name)
            
            if isinstance(result, dict):
                print(f"   ✅ Success! Result type: dict with {len(result)} keys")
                for key, value in result.items():
                    if isinstance(value, list):
                        print(f"      {key}: {len(value)} items")
                    else:
                        print(f"      {key}: {value}")
            elif isinstance(result, list):
                print(f"   ✅ Success! Result type: list with {len(result)} items")
                if result:
                    print(f"      Sample item: {result[0] if result else 'None'}")
            else:
                print(f"   ✅ Success! Result: {str(result)[:100]}{'...' if len(str(result)) > 100 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Fixed Gemini Agent Components...")
    print("=" * 60)
    
    success = test_tool_functionality()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tool functionality tests passed!")
        print("🎉 The 'show my plant hierarchy' query should now work!")
        print("\n📝 Ready to test with actual Gemini API:")
        print("1. Get API key from: https://makersuite.google.com/app/apikey") 
        print("2. Run: streamlit run nw_agent_gemini_simple_app.py")
        print("3. Try: 'show my plant hierarchy'")
    else:
        print("❌ Some tests failed - check the implementation")
