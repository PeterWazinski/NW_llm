"""
Simplified Google Gemini Water Assistant
Uses Google Generative AI directly without LangChain dependencies
"""

import os
import json
from typing import Dict, Any, Optional
import google.generativeai as genai
from nw_water_tools import NWWaterTools
from Guwahati import Guwahati

class SimpleWaterAgentGemini:
    def __init__(self, google_api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        """Initialize the Gemini water assistant"""
        
        # Configure API key
        api_key = google_api_key or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable or pass it directly.")
        
        try:
            genai.configure(api_key=api_key)
            
            # Initialize model with safety settings
            self.model_name = model_name
            
            # Configure safety settings to be more permissive for technical content
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ]
            
            # Generation config for consistent responses
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            self.model = genai.GenerativeModel(
                model_name=model_name,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            
            # Initialize water tools
            self.guwahati_hierarchy = Guwahati.create_hierarchy()
            self.tools = NWWaterTools(self.guwahati_hierarchy)
            
            # Conversation history (simple in-memory storage)
            self.conversation_history = []
            
            print(f"✅ Simple Gemini Water Assistant initialized with {model_name}")
            
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini model: {str(e)}. Please check your API key and internet connection.")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt with available tools"""
        return f"""You are a helpful assistant for the Guwahati Water Network system analysis.

AVAILABLE TOOLS:
{self._get_tools_description()}

When users ask questions, use the appropriate tools to provide accurate, helpful information about the water network system.

Always explain your reasoning and provide context for your answers. If you need to use a tool, clearly indicate which tool you're using and why.
"""
    
    def _get_tools_description(self) -> str:
        """Get description of available tools"""
        tool_descriptions = []
        for method_name in dir(self.tools):
            if not method_name.startswith('_') and callable(getattr(self.tools, method_name)):
                method = getattr(self.tools, method_name)
                if hasattr(method, '__doc__') and method.__doc__:
                    tool_descriptions.append(f"- {method_name}: {method.__doc__.strip()}")
        return "\n".join(tool_descriptions)
    
    def _call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call a water network tool"""
        try:
            # Map tool names to direct hierarchy access
            if tool_name == 'get_hierarchy_structure':
                # Get the full hierarchy structure
                return {
                    'locations': getattr(self.guwahati_hierarchy, 'all_locations', []),
                    'applications': getattr(self.guwahati_hierarchy, 'all_applications', []),
                    'modules': getattr(self.guwahati_hierarchy, 'all_modules', []),
                    'instrumentations': getattr(self.guwahati_hierarchy, 'all_instrumentations', [])
                }
            elif tool_name == 'get_all_locations':
                return getattr(self.guwahati_hierarchy, 'all_locations', [])
            elif tool_name == 'get_all_nodes':
                all_nodes = []
                all_nodes.extend(getattr(self.guwahati_hierarchy, 'all_locations', []))
                all_nodes.extend(getattr(self.guwahati_hierarchy, 'all_applications', []))
                all_nodes.extend(getattr(self.guwahati_hierarchy, 'all_modules', []))
                all_nodes.extend(getattr(self.guwahati_hierarchy, 'all_instrumentations', []))
                return all_nodes
            elif tool_name == 'get_all_pipes':
                # For now, return a placeholder - would need actual pipe data
                return "Pipe information not available in current hierarchy structure"
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
    
    def process_message(self, message: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a user message and return response"""
        
        # Validate input
        if not message or not message.strip():
            return {
                'content': "Please provide a valid question about the water network.",
                'error': True,
                'model': self.model_name
            }
        
        # Add system prompt and conversation history
        full_prompt = self.get_system_prompt() + "\n\n"
        
        # Add conversation history
        for msg in self.conversation_history[-5:]:  # Keep last 5 messages
            full_prompt += f"User: {msg['user']}\nAssistant: {msg['assistant']}\n\n"
        
        # Add current message
        full_prompt += f"User: {message.strip()}\nAssistant: "
        
        # Check if the response suggests using a tool first
        tool_results = self._handle_tool_calls(message, "")
        
        try:
            # If we have tool results, incorporate them into the prompt
            if tool_results:
                enhanced_prompt = full_prompt + f"\n\nRelevant Data Retrieved:\n{json.dumps(tool_results, indent=2)}\n\nPlease provide a comprehensive response using this data to answer the user's question: {message}"
                response = self.model.generate_content(enhanced_prompt)
            else:
                # Generate response without tools
                response = self.model.generate_content(full_prompt)
            
            # Safely extract response text
            if hasattr(response, 'text') and response.text:
                assistant_response = response.text.strip()
            elif hasattr(response, 'parts') and response.parts:
                assistant_response = str(response.parts[0]).strip()
            else:
                assistant_response = "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
            
            # Store conversation
            self.conversation_history.append({
                'user': message,
                'assistant': assistant_response,
                'thread_id': thread_id
            })
            
            return {
                'content': assistant_response,
                'tool_results': tool_results,
                'model': self.model_name,
                'thread_id': thread_id
            }
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            print(f"Debug - Full error: {e}")  # Debug logging
            print(f"Debug - Message: {message}")  # Debug logging
            print(f"Debug - Prompt length: {len(full_prompt) if 'full_prompt' in locals() else 'N/A'}")  # Debug logging
            
            # Try to provide a helpful response even with errors
            if tool_results:
                fallback_response = f"I encountered an error generating a response, but I was able to retrieve some relevant data about your query '{message}':\n\n"
                for tool_name, result in tool_results.items():
                    fallback_response += f"**{tool_name}**: {str(result)[:200]}{'...' if len(str(result)) > 200 else ''}\n\n"
                return {
                    'content': fallback_response,
                    'tool_results': tool_results,
                    'error': True,
                    'model': self.model_name
                }
            else:
                return {
                    'content': error_msg,
                    'error': True,
                    'model': self.model_name
                }
    
    def _handle_tool_calls(self, user_message: str, assistant_response: str) -> Dict[str, Any]:
        """Simple heuristic-based tool calling"""
        tool_results = {}
        
        # Convert to lowercase for easier matching
        message_lower = user_message.lower()
        response_lower = assistant_response.lower()
        
        # Plant/hierarchy queries - added "plant" keyword
        if any(word in message_lower for word in ['hierarchy', 'structure', 'tree', 'parent', 'child', 'plant']):
            tool_results['get_hierarchy_structure'] = self._call_tool('get_hierarchy_structure')
        
        # Location-related queries
        if any(word in message_lower for word in ['location', 'where', 'place', 'area']):
            if 'all' in message_lower or 'list' in message_lower:
                tool_results['get_all_locations'] = self._call_tool('get_all_locations')
            elif any(word in message_lower for word in ['node', 'nodes']):
                tool_results['get_all_nodes'] = self._call_tool('get_all_nodes')
        
        # Pipe/connection queries
        if any(word in message_lower for word in ['pipe', 'connection', 'connected']):
            tool_results['get_all_pipes'] = self._call_tool('get_all_pipes')
        
        # Summary/overview queries
        if any(word in message_lower for word in ['summary', 'overview', 'total', 'count']):
            tool_results['get_network_summary'] = self._call_tool('get_network_summary')
        
        return tool_results
    
    def invoke(self, message: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """Main method to invoke the agent (for compatibility)"""
        return self.process_message(message, thread_id)

# Example usage
if __name__ == "__main__":
    # Test the simple agent
    try:
        agent = SimpleWaterAgentGemini()
        
        # Test queries
        test_queries = [
            "What locations are in the water system?",
            "Show me a summary of the network",
            "What's the hierarchy structure?",
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing: {query}")
            print("-" * 50)
            
            result = agent.invoke(query)
            print(f"Response: {result['content']}")
            
            if result.get('tool_results'):
                print(f"Tools used: {list(result['tool_results'].keys())}")
    
    except Exception as e:
        print(f"❌ Error testing agent: {e}")
        print("\n💡 Make sure to set your GOOGLE_API_KEY environment variable")
