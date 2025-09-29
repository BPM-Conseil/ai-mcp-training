@echo off
echo 🛑 Stopping All Containers...
echo.
docker compose down
docker compose -f docker-compose.debug.yml down
echo.
echo ✅ All containers stopped.
