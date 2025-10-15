"""
Ollama HTTP Request Interceptor
Provides various methods to intercept and log HTTP requests to Ollama server
"""

import json
import time
import logging
from typing import Any, Dict, Optional
import httpx
import aiohttp
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage
from langchain_core.language_models.llms import LLM

# Configure logging for HTTP interception
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Removed InterceptingHTTPXClient class - using monkey patching approach instead

class InterceptingChatOllama(ChatOllama):
    """Custom ChatOllama that uses our intercepting HTTP client via monkey patching"""
    
    def __init__(self, *args, **kwargs):
        # Setup HTTP interception before calling super().__init__
        self._setup_httpx_interception()
        super().__init__(*args, **kwargs)
    
    def _setup_httpx_interception(self):
        """Setup HTTP interception by monkey patching httpx.Client globally"""
        import httpx
        
        # Check if already patched to avoid double patching
        if not hasattr(httpx.Client, '_intercepted'):
            original_client_init = httpx.Client.__init__
            original_request = httpx.Client.request
            original_send = httpx.Client.send
            
            def intercepted_init(self, *args, **kwargs):
                original_client_init(self, *args, **kwargs)
                self._request_count = 0
            
            def intercepted_request(self, method: str, url, **kwargs):
                self._request_count = getattr(self, '_request_count', 0) + 1
                start_time = time.time()
                
                # Log request details
                print(f"\n🔍 === HTTP REQUEST #{self._request_count} ===")
                print(f"📡 Method: {method}")
                print(f"🌐 URL: {url}")
                print(f"📋 Headers: {dict(kwargs.get('headers', {}))}")
                
                # Log request body if present
                if 'content' in kwargs:
                    try:
                        body = kwargs['content']
                        if isinstance(body, bytes):
                            body = body.decode('utf-8')
                        if body:
                            try:
                                parsed_body = json.loads(body)
                                print(f"📦 Request Body (JSON):")
                                print(json.dumps(parsed_body, indent=2))
                            except json.JSONDecodeError:
                                print(f"📦 Request Body (Raw): {body}")
                    except Exception as e:
                        print(f"⚠️ Could not parse request body: {e}")
                
                # Log query parameters
                if 'params' in kwargs:
                    print(f"🔗 Query Params: {kwargs['params']}")
                
                # Make the actual request
                try:
                    response = original_request(self, method, url, **kwargs)
                    end_time = time.time()
                    
                    # Log response details
                    print(f"✅ Response Status: {response.status_code}")
                    print(f"⏱️ Response Time: {(end_time - start_time)*1000:.2f}ms")
                    print(f"📥 Response Headers: {dict(response.headers)}")
                    
                    # Log response body (truncated for readability)
                    try:
                        response_text = response.text
                        if response_text:
                            try:
                                parsed_response = json.loads(response_text)
                                print(f"📨 Response Body (JSON):")
                                response_str = json.dumps(parsed_response, indent=2)
                                if len(response_str) > 1000:
                                    print(response_str[:1000] + "...")
                                else:
                                    print(response_str)
                            except json.JSONDecodeError:
                                print(f"📨 Response Body (Raw): {response_text[:500]}...")
                    except Exception as e:
                        print(f"⚠️ Could not parse response body: {e}")
                    
                    print(f"🔍 === END REQUEST #{self._request_count} ===\n")
                    return response
                    
                except Exception as e:
                    end_time = time.time()
                    print(f"❌ Request Failed: {e}")
                    print(f"⏱️ Failed After: {(end_time - start_time)*1000:.2f}ms")
                    print(f"🔍 === END REQUEST #{self._request_count} (FAILED) ===\n")
                    raise
            
            def intercepted_send(self, request, **kwargs):
                """Intercept send method as well"""
                self._request_count = getattr(self, '_request_count', 0) + 1
                start_time = time.time()
                
                # Log request details
                print(f"\n🔍 === HTTP SEND #{self._request_count} ===")
                print(f"📡 Method: {request.method}")
                print(f"🌐 URL: {request.url}")
                print(f"📋 Headers: {dict(request.headers)}")
                
                # Log request body
                if request.content:
                    try:
                        body = request.content.decode('utf-8')
                        if body:
                            try:
                                parsed_body = json.loads(body)
                                print(f"📦 Request Body (JSON):")
                                print(json.dumps(parsed_body, indent=2))
                            except json.JSONDecodeError:
                                print(f"📦 Request Body (Raw): {body}")
                    except Exception as e:
                        print(f"⚠️ Could not parse request body: {e}")
                
                # Send the request
                try:
                    response = original_send(self, request, **kwargs)
                    end_time = time.time()
                    
                    # Log response details
                    print(f"✅ Response Status: {response.status_code}")
                    print(f"⏱️ Response Time: {(end_time - start_time)*1000:.2f}ms")
                    print(f"📥 Response Headers: {dict(response.headers)}")
                    
                    # Log response body (truncated for readability)
                    try:
                        response_text = response.text
                        if response_text:
                            try:
                                parsed_response = json.loads(response_text)
                                print(f"📨 Response Body (JSON):")
                                response_str = json.dumps(parsed_response, indent=2)
                                if len(response_str) > 1000:
                                    print(response_str[:1000] + "...")
                                else:
                                    print(response_str)
                            except json.JSONDecodeError:
                                print(f"📨 Response Body (Raw): {response_text[:500]}...")
                    except Exception as e:
                        print(f"⚠️ Could not parse response body: {e}")
                    
                    print(f"🔍 === END SEND #{self._request_count} ===\n")
                    return response
                    
                except Exception as e:
                    end_time = time.time()
                    print(f"❌ Send Failed: {e}")
                    print(f"⏱️ Failed After: {(end_time - start_time)*1000:.2f}ms")
                    print(f"🔍 === END SEND #{self._request_count} (FAILED) ===\n")
                    raise
            
            # Apply the monkey patch
            httpx.Client.__init__ = intercepted_init
            httpx.Client.request = intercepted_request
            httpx.Client.send = intercepted_send
            httpx.Client._intercepted = True
            
            print("🔧 HTTP interception enabled via monkey patching")

# Method 2: Using httpx event hooks
class EventHookHTTPXClient(httpx.Client):
    """HTTPX client using event hooks for request/response logging"""
    
    def __init__(self, *args, **kwargs):
        # Add event hooks
        event_hooks = kwargs.get('event_hooks', {})
        event_hooks['request'] = [self.log_request] + event_hooks.get('request', [])
        event_hooks['response'] = [self.log_response] + event_hooks.get('response', [])
        kwargs['event_hooks'] = event_hooks
        super().__init__(*args, **kwargs)
    
    def log_request(self, request: httpx.Request):
        """Log outgoing request"""
        print(f"\n🚀 OUTGOING REQUEST:")
        print(f"   Method: {request.method}")
        print(f"   URL: {request.url}")
        print(f"   Headers: {dict(request.headers)}")
        
        if request.content:
            try:
                body = request.content.decode('utf-8')
                parsed = json.loads(body)
                print(f"   Body: {json.dumps(parsed, indent=4)}")
            except:
                print(f"   Body (raw): {request.content}")
    
    def log_response(self, response: httpx.Response):
        """Log incoming response"""
        print(f"\n📨 INCOMING RESPONSE:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        try:
            if hasattr(response, '_content') and response._content:
                content = response._content.decode('utf-8')
                parsed = json.loads(content)
                print(f"   Body: {json.dumps(parsed, indent=4)[:500]}...")
        except:
            print(f"   Body: [Could not parse response body]")

# Method 3: Requests library interception (if using requests instead of httpx)
def setup_requests_logging():
    """Setup requests library logging using HTTPConnection debug"""
    import http.client as http_client
    import logging
    
    # Enable HTTP connection debugging
    http_client.HTTPConnection.debuglevel = 1
    
    # Configure logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

# Method 4: Monkey patching httpx globally
def setup_global_httpx_interception():
    """Globally intercept all httpx requests"""
    import httpx
    
    # Store original methods
    original_request = httpx.Client.request
    original_send = httpx.Client.send
    
    def intercepted_request(self, method: str, url, **kwargs):
        print(f"\n🌐 INTERCEPTED REQUEST: {method} {url}")
        if 'json' in kwargs:
            print(f"📦 JSON Payload: {json.dumps(kwargs['json'], indent=2)}")
        if 'content' in kwargs:
            print(f"📦 Content: {kwargs['content']}")
        if 'params' in kwargs:
            print(f"🔗 Params: {kwargs['params']}")
        
        # Call original method
        response = original_request(self, method, url, **kwargs)
        
        print(f"✅ Response: {response.status_code}")
        return response
    
    # Apply monkey patch
    httpx.Client.request = intercepted_request
    print("🔧 Global HTTPX interception enabled!")

# Method 5: Using mitmproxy programmatically (advanced)
def setup_mitmproxy_interception(port: int = 8080):
    """Setup mitmproxy for HTTP interception (requires mitmproxy package)"""
    try:
        from mitmproxy import options, master
        from mitmproxy.addons import dumper
        
        class OllamaInterceptor:
            def request(self, flow):
                if "ollama" in flow.request.pretty_host or ":11434" in flow.request.pretty_url:
                    print(f"\n🎯 OLLAMA REQUEST INTERCEPTED:")
                    print(f"   URL: {flow.request.pretty_url}")
                    print(f"   Method: {flow.request.method}")
                    print(f"   Headers: {dict(flow.request.headers)}")
                    if flow.request.content:
                        try:
                            content = json.loads(flow.request.content.decode())
                            print(f"   Body: {json.dumps(content, indent=2)}")
                        except:
                            print(f"   Body (raw): {flow.request.content}")
            
            def response(self, flow):
                if "ollama" in flow.request.pretty_host or ":11434" in flow.request.pretty_url:
                    print(f"\n🎯 OLLAMA RESPONSE INTERCEPTED:")
                    print(f"   Status: {flow.response.status_code}")
                    if flow.response.content:
                        try:
                            content = json.loads(flow.response.content.decode())
                            print(f"   Body: {json.dumps(content, indent=2)[:500]}...")
                        except:
                            print(f"   Body (raw): {flow.response.content[:200]}...")
        
        opts = options.Options(listen_port=port)
        m = master.Master(opts)
        m.addons.add(OllamaInterceptor())
        m.addons.add(dumper.Dumper())
        
        print(f"🔧 mitmproxy interception started on port {port}")
        return m
        
    except ImportError:
        print("❌ mitmproxy not installed. Install with: pip install mitmproxy")
        return None

# Utility function to create intercepting ChatOllama
def create_intercepting_ollama(base_url: str = None, model: str = "qwen2.5:7b-instruct-q4_K_M", method: str = "custom_client"):
    """
    Create a ChatOllama instance with HTTP interception
    
    Args:
        base_url: Ollama server URL
        model: Model name
        method: Interception method ('custom_client', 'event_hooks', 'global_patch')
    """
    
    if method == "custom_client":
        return InterceptingChatOllama(model=model, base_url=base_url)
    
    elif method == "event_hooks":
        # Create ChatOllama with event hook client
        client = EventHookHTTPXClient(base_url=base_url)
        ollama = ChatOllama(model=model, base_url=base_url)
        # Note: This might need adjustment based on ChatOllama's internal structure
        return ollama
    
    elif method == "global_patch":
        setup_global_httpx_interception()
        return ChatOllama(model=model, base_url=base_url)
    
    else:
        raise ValueError(f"Unknown interception method: {method}")

# Example usage and testing
if __name__ == "__main__":
    # Test the intercepting client
    print("🧪 Testing Ollama HTTP Interception...")
    
    # Method 1: Custom intercepting client
    intercepting_ollama = create_intercepting_ollama(
        base_url="http://localhost:11434",
        model="qwen2.5:7b-instruct-q4_K_M",
        method="custom_client"
    )
    
    # Test with a simple message
    try:
        from langchain_core.messages import HumanMessage
        messages = [HumanMessage(content="Hello, how are you?")]
        response = intercepting_ollama.invoke(messages)
        print(f"🤖 LLM Response: {response}")
    except Exception as e:
        print(f"❌ Test failed: {e}")