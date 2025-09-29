@echo off
echo 🐛 Starting Debug Environment...
echo.
echo This will start containers with debugpy enabled.
echo VS Code can attach to:
echo   - Backend: localhost:5678
echo   - MCP Server: localhost:5679
echo.
docker compose -f docker-compose.debug.yml up --build
