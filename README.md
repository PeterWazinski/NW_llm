# 💧 Netilion Water LLM Assistant

An intelligent AI-powered assistant for analyzing and interacting with Netilion Water plant hierarchies using Large Language Models (LLM), LangGraph, and advanced result processing capabilities.

## 🎯 Project Overview

This project provides a conversational AI interface to explore, analyze, and query water plant infrastructure data. The assistant leverages advanced language models to understand natural language queries about plant components, hierarchies, measurements, and operational data.

### Key Features

🏭 **Plant Hierarchy Analysis**
- Navigate complex water plant structures (locations → applications → modules → instruments → assets)
- Query relationships between different plant components
- Analyze instrument configurations and measurement parameters
- **NEW**: Filter instrumentations by type with case-insensitive validation

🤖 **Enhanced Natural Language Interface**
- Ask questions in plain English about your water plant
- Get detailed information about specific components by name or ID
- **NEW**: Intelligent result filtering - no more overwhelming data dumps!
- **NEW**: Advanced prompting strategies for better LLM responses
- Receive structured summaries and contextual analysis

⚡ **Performance Monitoring & Server Flexibility**
- Real-time execution timing for individual tools and complete responses
- **NEW**: Persistent execution footers with server/model information
- **NEW**: Command-line arguments for Ollama server configuration
- Console logging for debugging and performance optimization
- Comprehensive performance metrics

🛠️ **Advanced Toolset (15+ Tools)**
- **NEW**: `get_instrumentations_by_type()` with validation
- **NEW**: `filter_instrumentations_by_criteria()` for complex filtering
- Support for both ID-based and name-based component queries
- Enhanced tool descriptions with result processing guidance
- Markdown-formatted outputs for enhanced readability

## 🏗️ Architecture

The system is built on a modern, modular architecture combining:

- **LangGraph Framework**: Advanced AI agent orchestration with memory and state management
- **Ollama**: Flexible local/remote LLM inference with multiple model support
- **Streamlit**: Enhanced web interface with persistent UI elements and command-line configuration
- **Enhanced Tools**: 15+ specialized functions with intelligent result processing
- **Smart Filtering**: Advanced prompting strategies to prevent LLM data dumps

### Component Structure

```
🏭 Netilion Water Plant
├── 📍 Locations (e.g., "Nijeshwari PWSS")
│   └── 🚰 Applications (water_abstraction, water_distribution, effluent_discharge)
│       └── 🔧 Modules (source, storage, transfer, quality_control, etc.)
│           └── 📊 Instruments (Flow, Pressure, Analysis, Pump, Voltage)
│               └── 🏷️ Assets (Physical equipment with serial numbers)
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Ollama installed (local or remote server)
- Compatible models (Qwen2.5, Llama3.2, etc.)
- **NEW**: Flexible server configuration options

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/PeterWazinski/NW_llm.git
   cd NW_llm
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Ollama model**
   ```bash
   ollama serve
   ollama pull qwen2.5:7b-instruct-q4_K_M
   ```

4. **Run the application**
   ```bash
   # Basic usage (local Ollama)
   streamlit run nw_agent_lg_app.py
   
   # Advanced options - NEW!
   streamlit run nw_agent_lg_app.py -- --local                    # Force local mode
   streamlit run nw_agent_lg_app.py -- --remote --ollama-url "http://server:11434"  # Remote server
   streamlit run nw_agent_lg_app.py -- --model "llama3.2:latest" # Specific model
   streamlit run nw_agent_lg_app.py -- --help                    # Show all options
   ```

## 💬 Usage Examples

### Basic Queries
- *"Show me the complete hierarchy of the water system"*
- *"What applications are available in Nijeshwari PWSS?"*
- *"Give me a summary of all instrumentations"*

### Component Analysis
- *"What instruments are in the Source module?"*
- *"List all Flow type instruments with their details"*
- *"Show me assets connected to the Borewell level instrument"*

### **NEW**: Enhanced Filtering Queries
- *"Show me only the pump instruments that don't have thresholds defined"*
- *"Which level instruments are in the Source module?"* 
- *"Find all flow instruments and tell me which ones have both upper and lower thresholds"*
- *"Get all pressure instruments that measure 'pressure_bar' and summarize their settings"*

### **NEW**: Smart Analysis (Prevents Data Dumps!)
- *"Analyze all instrumentations by type and show me the distribution"*
- *"Find instruments without thresholds and group them by module"*
- *"Compare threshold configurations across different instrument types"*

## 🛠️ Available Tools

The AI assistant has access to **15+ specialized tools** with enhanced result processing:

### Data Retrieval Tools
- `get_all_locations` - List all plant locations
- `get_all_applications` - List all applications across the plant
- `get_all_modules` - List all modules with their types
- `get_all_instrumentations` - List all measurement instruments
- `get_all_assets` - List all physical assets

### Hierarchical Navigation Tools
- `get_applications_for_location` - Find applications in a specific location
- `get_modules_for_application` - Find modules in a specific application  
- `get_instruments_for_module` - Find instruments in a specific module
- `get_assets_for_instrument` - Find assets connected to an instrument

### **NEW**: Advanced Search & Filter Tools
- `get_instrumentations_by_type` - Find instruments by type with validation
- `get_instrumentations_by_value_key` - Find instruments by measurement type
- `filter_instrumentations_by_criteria` - Complex filtering with natural language
- `search_hierarchy` - Search components by name patterns

### Summary and Visualization Tools
- `get_summary` - Get structured component counts
- `get_md_summary` - Get markdown-formatted summary
- `get_detailed_statistics` - Comprehensive statistics and distributions
- `pprint_hierarchy` - Display complete hierarchy with formatting
- `pprint_hierarchy_md` - Display hierarchy in markdown format

## 📊 Performance Features

### **NEW**: Enhanced Execution Monitoring
- Individual tool execution times (millisecond precision)
- Total agent response times with **persistent UI footers**
- **Server information display** (local/remote, model, URL)
- Performance comparison across different query types
- **Footer persists across queries** without contaminating LLM context

### **NEW**: Command Line Configuration
```bash
# Server configuration options
streamlit run nw_agent_lg_app.py -- --local                    # Force local
streamlit run nw_agent_lg_app.py -- --remote                   # Force remote
streamlit run nw_agent_lg_app.py -- --ollama-url "http://server:11434"
streamlit run nw_agent_lg_app.py -- --model "qwen2.5:7b-instruct-q4_K_M"
```

### Console Logging
```
🌐 Using Ollama server at: http://localhost:11434
🤖 Using model: qwen2.5:7b-instruct-q4_K_M
📦 Found 5 available models: llama3.2:latest, qwen2.5:7b-instruct-q4_K_M...
🔧 Tool 'get_instrumentations_by_type' executed in 0.045s
🔧 Tool 'filter_instrumentations_by_criteria' executed in 0.028s
🤖 Agent execution completed in 2.34s
🔧 Tools called: ['get_instrumentations_by_type']
```

## 🗂️ Project Structure

```
NW_llm/
├── nw_agent_langgraph.py     # LangGraph AI agent with enhanced memory
├── nw_agent_lg_app.py        # Enhanced Streamlit app with CLI args
├── nw_water_tools.py         # Enhanced tools with smart result processing
├── requirements.txt          # Python dependencies with detailed comments
├── Guwahati.py              # Sample water plant data and hierarchy
├── run_examples.bat/.sh     # Quick start scripts for different configurations
├── nwater/                  # Core water system modules
│   ├── __init__.py
│   ├── nw_hierarchy.py      # Enhanced hierarchy with type filtering
│   ├── hub_connector.py     # Data connection utilities
│   ├── nmf_analyzer.py      # Analysis tools
│   └── NMFhierarchy.py      # Extended hierarchy management
└── product_app.py           # Additional product utilities
```

## 🔧 Technical Details

### **NEW**: Enhanced AI Configuration
- **Framework**: LangGraph with advanced state management and memory
- **Models**: Multi-model support (Qwen2.5, Llama3.2, etc.)
- **Inference**: Flexible local/remote Ollama servers with auto-discovery
- **Memory**: Thread-based conversation persistence
- **Result Processing**: Advanced prompting to prevent data dumps

### **NEW**: Smart Result Processing
- Chain-of-thought reasoning instructions
- Enhanced tool descriptions with processing guidance
- Natural language filtering capabilities
- Result analysis before presentation
- Context-aware response formatting

### Performance Optimizations
- Tool execution timing decorators with enhanced logging
- Efficient hierarchy traversal algorithms
- Optimized data structures for fast lookups
- **NEW**: Separate UI metadata from LLM context
- Markdown formatting for improved LLM processing

### **NEW**: Flexible Configuration
- Command-line argument parsing with argparse
- Runtime server switching (local/remote)
- Model validation and auto-discovery
- **NEW**: Persistent UI elements without LLM contamination
- Enhanced error handling with user-friendly messages

## 🧠 Smart Result Processing

### Problem Solved: LLM Data Dumps
Previous versions would return entire unfiltered lists when queried. The enhanced system now:

✅ **Analyzes user intent** before presenting results  
✅ **Filters data contextually** based on specific questions  
✅ **Summarizes large datasets** meaningfully  
✅ **Groups related items** for better understanding  
✅ **Provides counts and context** (e.g., "Found 3 out of 15 matching items")  

### Enhancement Strategies Implemented
- **Enhanced Tool Descriptions**: Explicit result processing instructions
- **System Prompt Engineering**: Critical instructions for analyzing tool results  
- **Chain-of-Thought Integration**: Structured reasoning approach
- **Natural Language Filtering**: `filter_instrumentations_by_criteria` tool
- **Advanced Examples**: Comprehensive usage patterns for better LLM guidance

## 🤝 Contributing

Contributions are welcome! Please feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add your changes with proper tool timing decorators
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines
- All new tools should include the `@self.time_tool_execution` decorator
- **NEW**: Include result processing instructions in tool docstrings
- Follow the existing naming conventions for consistency
- Add comprehensive docstrings with usage examples
- Test with both component IDs and names where applicable
- **NEW**: Ensure tools guide LLM toward intelligent result filtering
- **NEW**: Separate UI metadata from LLM conversation context

## 🆕 Recent Updates

### v2.0 - Enhanced Intelligence & Flexibility
- **🧠 Smart Result Processing**: LLM now analyzes and filters results instead of data dumps
- **⚙️ Command-Line Configuration**: Flexible Ollama server and model selection
- **🔍 Advanced Filtering**: New `get_instrumentations_by_type()` and `filter_instrumentations_by_criteria()` tools
- **📊 Persistent UI Enhancements**: Execution footers with server info that persist across queries
- **🎯 LangGraph Migration**: Advanced agent framework with improved memory management
- **🚀 Improved Prompting**: Chain-of-thought reasoning and enhanced tool guidance

### Key Improvements for LLM Performance
- **Result Processing Instructions**: Tools now guide LLMs on how to handle large datasets
- **Context Separation**: UI metadata no longer contaminates LLM conversation context
- **Enhanced Examples**: Comprehensive usage patterns for better AI understanding
- **Validation & Error Handling**: Robust input validation and user-friendly error messages

## 📝 License

This project is part of the Netilion Water ecosystem for industrial water plant monitoring and analysis.

## 🙏 Acknowledgments

- **Endress+Hauser** for the Netilion Water platform
- **LangGraph** community for the advanced agent framework
- **LangChain** community for the foundational agent tools
- **Ollama** project for flexible local/remote LLM inference
- **Qwen Team** for the excellent language models
- **Streamlit** for the enhanced web interface capabilities

---

**🚀 Ready to explore your water plant with AI? Start the application and ask your first question!**
