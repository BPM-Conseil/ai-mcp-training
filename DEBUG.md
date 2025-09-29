# 🐛 Debug Setup Guide

This project includes comprehensive debugging support for both the backend and MCP server using VS Code and debugpy.

## 📁 File Structure

```
├── backend/
│   ├── Dockerfile              # Production build
│   ├── Dockerfile.debug        # Debug build with debugpy
│   └── ...
├── mcp_server/
│   ├── Dockerfile              # Production build
│   ├── Dockerfile.debug        # Debug build with debugpy
│   └── ...
├── docker-compose.yml          # Production setup
├── docker-compose.debug.yml    # Debug setup with volume mounts
└── .vscode/launch.json         # VS Code debug configurations
```

## 🚀 Quick Start

### **Production Mode**
```bash
docker compose up --build
```

### **Debug Mode**
```bash
docker compose -f docker-compose.debug.yml up --build
```

## 🔧 Debug Features

### **Debug Dockerfiles Include:**
- ✅ `debugpy` for remote debugging
- ✅ Volume mounts for live code reload
- ✅ Exposed debug ports (5678, 5679)
- ✅ `--wait-for-client` flag (containers wait for debugger)

### **Debug Ports:**
- **Backend Debug**: `localhost:5678`
- **MCP Server Debug**: `localhost:5679`
- **Application Ports**: Same as production (8000, 8765)

## 🎯 VS Code Debugging

### **Step 1: Start Debug Containers**
```bash
docker compose -f docker-compose.debug.yml up --build
```

### **Step 2: Attach Debugger**
1. Open VS Code in the project root
2. Go to **Run and Debug** (Ctrl+Shift+D)
3. Select configuration:
   - **"Python: Remote Attach Backend"** - Debug backend service
   - **"Python: Remote Attach MCP Server"** - Debug MCP server
4. Click **Start Debugging** (F5)

### **Step 3: Set Breakpoints**
- Set breakpoints in your Python code
- The debugger will pause execution when hit
- Use standard VS Code debugging features

## 🔄 Live Code Reload

Debug mode includes volume mounts for live development:

```yaml
volumes:
  - ./backend:/app:delegated      # Backend live reload
  - ./mcp_server:/app:delegated   # MCP server live reload
```

**Benefits:**
- ✅ Code changes reflect immediately
- ✅ No need to rebuild containers
- ✅ Faster development cycle

## 🛠️ Debug Commands

### **Start Debug Environment**
```bash
# Full debug stack
docker compose -f docker-compose.debug.yml up --build

# Debug specific service
docker compose -f docker-compose.debug.yml up backend --build
docker compose -f docker-compose.debug.yml up mcp-server --build
```

### **View Debug Logs**
```bash
# All services
docker compose -f docker-compose.debug.yml logs -f

# Specific service
docker compose -f docker-compose.debug.yml logs -f backend
docker compose -f docker-compose.debug.yml logs -f mcp-server
```

### **Stop Debug Environment**
```bash
docker compose -f docker-compose.debug.yml down
```

## 🔍 Debugging Tips

### **Container Waiting for Debugger**
When you see:
```
Waiting for debugger attach...
```

This means the container is waiting for VS Code to connect. Attach the debugger to continue.

### **Path Mappings**
The debug configuration maps local paths to container paths:
```json
"pathMappings": [
    {
        "localRoot": "${workspaceFolder}/backend",
        "remoteRoot": "/app"
    }
]
```

### **Debug Both Services Simultaneously**
1. Start debug containers
2. Attach to backend (F5 → "Python: Remote Attach Backend")
3. Open new VS Code window
4. Attach to MCP server (F5 → "Python: Remote Attach MCP Server")

### **Troubleshooting**

**Connection Refused:**
- Ensure containers are running: `docker ps`
- Check port mappings: `docker compose -f docker-compose.debug.yml ps`

**Breakpoints Not Hit:**
- Verify path mappings in `.vscode/launch.json`
- Check that `justMyCode: false` is set
- Ensure you're debugging the correct service

**Code Changes Not Reflected:**
- Verify volume mounts are working: `docker compose -f docker-compose.debug.yml config`
- Check file permissions on mounted volumes

## 🎛️ Advanced Configuration

### **Custom Debug Settings**
Edit `.vscode/launch.json` to customize:
- Debug ports
- Path mappings
- Additional debugpy options

### **Environment Variables**
Debug containers support all production environment variables plus:
- `PYTHONDONTWRITEBYTECODE=1` - No .pyc files
- `PYTHONUNBUFFERED=1` - Real-time logs
- `PYTHONPATH=/app` - Module resolution

### **Performance Optimization**
Debug mode uses `delegated` volume mounts for better performance on macOS/Windows:
```yaml
volumes:
  - ./backend:/app:delegated
```

## 🔄 Switching Between Modes

### **Development → Production**
```bash
docker compose -f docker-compose.debug.yml down
docker compose up --build
```

### **Production → Development**
```bash
docker compose down
docker compose -f docker-compose.debug.yml up --build
```

## 📝 Notes

- Debug containers include additional development tools
- Volume mounts may affect performance (use for development only)
- Production Dockerfiles are optimized for size and security
- Debug ports are only exposed in debug mode for security
