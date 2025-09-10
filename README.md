# 💧 Netilion Water LLM Assistant

An intelligent AI-powered assistant for analyzing and interacting with Netilion Water plant hierarchies using Large Language Models (LLM) and LangChain framework.

## 🎯 Project Overview

This project provides a conversational AI interface to explore, analyze, and query water plant infrastructure data. The assistant leverages advanced language models to understand natural language queries about plant components, hierarchies, measurements, and operational data.

### Key Features

🏭 **Plant Hierarchy Analysis**
- Navigate complex water plant structures (locations → applications → modules → instruments → assets)
- Query relationships between different plant components
- Analyze instrument configurations and measurement parameters

🤖 **Natural Language Interface**
- Ask questions in plain English about your water plant
- Get detailed information about specific components by name or ID
- Receive structured summaries and reports

⚡ **Performance Monitoring**
- Real-time execution timing for individual tools and complete responses
- Console logging for debugging and performance optimization
- Comprehensive performance metrics

🛠️ **Advanced Toolset**
- 13 specialized tools for different aspects of plant analysis
- Support for both ID-based and name-based component queries
- Markdown-formatted outputs for enhanced readability

## 🏗️ Architecture

The system is built on a modular architecture combining:

- **LangChain Framework**: Orchestrates the AI agent and tool interactions
- **Ollama**: Provides local LLM inference with Qwen2.5-7B-Instruct model
- **Streamlit**: Delivers an intuitive web interface for user interactions
- **Custom Tools**: Specialized functions for water plant data access and analysis

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
- Ollama installed and running
- Qwen2.5-7B-Instruct model downloaded

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
   streamlit run nw_agent_app.py
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

### Advanced Analysis
- *"Find all instrumentations that don't have thresholds defined"*
- *"Compare modules between different applications"*
- *"Analyze measurement parameters for pressure instruments"*

## 🛠️ Available Tools

The AI assistant has access to 13 specialized tools:

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

### Summary and Visualization Tools
- `get_summary` - Get structured component counts
- `get_md_summary` - Get markdown-formatted summary
- `pprint_hierarchy` - Display complete hierarchy with formatting
- `pprint_hierarchy_md` - Display hierarchy in markdown format

## 📊 Performance Features

### Execution Timing
- Individual tool execution times (millisecond precision)
- Total agent response times
- Performance comparison across different query types

### Console Logging
```
🔧 Tool 'get_all_instrumentations' executed in 0.045s
🔧 Tool 'get_instruments_for_module' executed in 0.012s
🕐 Agent execution time: 2.34 seconds
📝 Query: What instruments are in the Source module?
💬 Response length: 456 characters
```

## 🗂️ Project Structure

```
NW_llm/
├── nw_agent.py              # Main AI agent with LangChain integration
├── nw_agent_app.py          # Streamlit web interface
├── requirements.txt         # Python dependencies with detailed comments
├── Guwahati.py             # Sample water plant data and hierarchy
├── nwater/                 # Core water system modules
│   ├── __init__.py
│   ├── nw_hierarchy.py     # Hierarchy management and visualization
│   ├── hub_connector.py    # Data connection utilities
│   └── nmf_analyzer.py     # Analysis tools
└── product_app.py          # Additional product utilities
```

## 🔧 Technical Details

### AI Model Configuration
- **Model**: Qwen2.5-7B-Instruct (4-bit quantized)
- **Framework**: LangChain with tool-calling capabilities
- **Memory**: Conversation buffer for context retention
- **Inference**: Local Ollama server

### Performance Optimizations
- Tool execution timing decorators
- Efficient hierarchy traversal algorithms
- Optimized data structures for fast lookups
- Markdown formatting for improved LLM processing

### Error Handling
- Graceful fallbacks for missing components
- Comprehensive error logging
- User-friendly error messages
- Tool execution monitoring

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
- Follow the existing naming conventions for consistency
- Add comprehensive docstrings for new functions
- Test with both component IDs and names where applicable

## 📝 License

This project is part of the Netilion Water ecosystem for industrial water plant monitoring and analysis.

## 🙏 Acknowledgments

- **Endress+Hauser** for the Netilion Water platform
- **LangChain** community for the agent framework
- **Ollama** project for local LLM inference
- **Qwen Team** for the excellent language model

---

**🚀 Ready to explore your water plant with AI? Start the application and ask your first question!**
