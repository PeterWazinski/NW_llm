@echo off
REM Demo script showing different ways to run the Streamlit app with Ollama configuration

echo 🚀 Netilion Water Assistant - Ollama Configuration Examples
echo ==========================================================
echo.

echo 1. Run with LOCAL Ollama server:
echo    streamlit run nw_agent_lg_app.py -- --local
echo.

echo 2. Run with REMOTE Ollama server:
echo    streamlit run nw_agent_lg_app.py -- --remote
echo.

echo 3. Run with CUSTOM Ollama server URL:
echo    streamlit run nw_agent_lg_app.py -- --remote --ollama-url http://192.168.1.100:11434
echo.

echo 4. Run with specific MODEL:
echo    streamlit run nw_agent_lg_app.py -- --local --model llama3.1:8b
echo.

echo 5. Run with DEFAULT settings (auto-detect):
echo    streamlit run nw_agent_lg_app.py
echo.

echo 📝 Notes:
echo    - Use '--' before your custom flags to separate them from Streamlit's flags
echo    - --local forces local Ollama server (http://localhost:11434)
echo    - --remote uses the default remote server or --ollama-url if specified
echo    - --model specifies which LLM model to use
echo    - Without flags, the app uses the class default (currently: run_ollama_locally = True)
echo.

pause