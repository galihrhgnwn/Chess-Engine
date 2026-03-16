# Stockfish 18 REST API - Pterodactyl Panel Setup Guide

Complete guide for deploying Stockfish 18 REST API on Pterodactyl Panel.

## Prerequisites

- Pterodactyl Panel instance (admin access)
- Python 3.11+ node on your Pterodactyl server
- Sufficient disk space (~500MB for Stockfish + dependencies)
- RAM allocation (minimum 1GB recommended)

## Installation Methods

### Method 1: Using Egg File (Recommended)

#### Step 1: Import the Egg

1. **Access Pterodactyl Admin Panel**
   - Go to `Admin Panel` → `Nests`
   - Select or create a nest (e.g., "Programming Languages")

2. **Import Egg**
   - Click `Import Egg`
   - Choose `From File`
   - Upload `egg.json` from this repository
   - Or use the raw URL:
     ```
     https://raw.githubusercontent.com/galihrhgnwn/Chess-Engine/main/egg.json
     ```

3. **Verify Import**
   - The egg should appear in your nest with:
     - Name: "Stockfish 18 REST API"
     - Docker Image: `ghcr.io/pterodactyl/yolks:python_3.11`
     - Startup Command: `python main.py`

#### Step 2: Create Server

1. **Create New Server**
   - Go to `Admin Panel` → `Servers` → `Create New`
   - Fill in basic details:
     - **Server Name**: Stockfish API
     - **Owner**: Select user
     - **Nest**: Select the nest containing the egg
     - **Egg**: Stockfish 18 REST API

2. **Configure Resources**
   - **Memory**: 1024 MB (minimum)
   - **Swap**: 256 MB
   - **Disk**: 2048 MB
   - **CPU**: 50-100% (adjust based on your needs)
   - **I/O**: 500 (default)
   - **Threads**: 4 (for Stockfish analysis)

3. **Environment Variables**
   - `STOCKFISH_THREADS`: 4 (or based on CPU allocation)
   - `STOCKFISH_MEMORY`: 512 (or based on RAM allocation)
   - `ENVIRONMENT`: production

4. **Allocations**
   - Assign a port (e.g., 8000)
   - Make sure it's accessible from your network

5. **Create Server**
   - Click "Create Server"
   - Wait for installation to complete

#### Step 3: Start the Server

1. **Access Server Console**
   - Go to the server page
   - Click "Console" tab

2. **Start Server**
   - Click the "Start" button
   - Monitor the console for startup messages:
     ```
     ✓ Stockfish engine started successfully
     Uvicorn running on http://0.0.0.0:8000
     ```

3. **Verify Installation**
   - Wait for "Uvicorn running" message
   - Server status should show "Running"

### Method 2: Manual Setup (Without Egg)

If you prefer manual setup or need customization:

#### Step 1: Create Generic Python Server

1. **Create Server with Python Egg**
   - Use any existing Python egg in your Pterodactyl
   - Or create a custom one based on `python_3.11`

2. **Allocate Resources**
   - Memory: 1024 MB+
   - Disk: 2048 MB+
   - CPU: 50-100%

#### Step 2: Upload Files

1. **Access File Manager**
   - Go to server console
   - Click "File Manager" tab

2. **Upload Repository Files**
   - Upload all files from the repository:
     - `main.py`
     - `requirements.txt`
     - `.env.example`
   - Create `.env` from `.env.example`

#### Step 3: Configure Startup

1. **Edit Startup Command**
   - Go to `Startup` tab
   - Set startup command to:
     ```
     python main.py
     ```

2. **Set Environment Variables**
   - `STOCKFISH_THREADS=4`
   - `STOCKFISH_MEMORY=512`
   - `ENVIRONMENT=production`

#### Step 4: Install Dependencies

1. **Access Console**
   - Go to "Console" tab

2. **Run Installation Commands**
   - Execute these commands:
     ```
     apt-get update
     apt-get install -y stockfish
     pip install -r requirements.txt
     ```

3. **Start Server**
   - Click "Start" button
   - Monitor console for startup

## Accessing the API

### Local Network Access

If Pterodactyl is on your local network:

```
http://<pterodactyl-server-ip>:<allocated-port>
```

Example:
```
http://192.168.1.100:8000
```

### Remote Access

For remote access, you have several options:

#### Option 1: Port Forwarding (Router)

1. Configure port forwarding on your router
2. Forward external port to Pterodactyl server IP:port
3. Access via: `http://<your-public-ip>:<external-port>`

#### Option 2: Reverse Proxy (Recommended)

Setup Nginx or Caddy as reverse proxy:

**Nginx Example**:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Option 3: Cloudflare Tunnel

1. Install Cloudflare Tunnel on your server
2. Create tunnel to `localhost:8000`
3. Access via Cloudflare domain

### API Documentation

Once running, access:

- **Swagger UI**: `http://<server>:<port>/docs`
- **ReDoc**: `http://<server>:<port>/redoc`
- **Health Check**: `http://<server>:<port>/health`

## Configuration

### Adjust Stockfish Performance

Access server console and modify environment variables:

1. **Increase Threads** (for faster analysis)
   ```
   STOCKFISH_THREADS=8
   ```

2. **Increase Memory** (for deeper analysis)
   ```
   STOCKFISH_MEMORY=1024
   ```

3. **Restart Server**
   - Stop and start the server for changes to take effect

### Monitor Resource Usage

1. **Check Console**
   - Monitor CPU and memory usage in console

2. **Adjust Allocations**
   - If running out of resources, increase server allocations
   - Go to `Settings` → `Resource Allocation`

## Troubleshooting

### Server Won't Start

**Error**: `Stockfish binary not found`

**Solution**:
1. Ensure Stockfish is installed:
   ```
   apt-get install -y stockfish
   ```
2. Verify installation:
   ```
   which stockfish
   ```

### Out of Memory

**Error**: `Killed` or `OOM`

**Solution**:
1. Reduce `STOCKFISH_MEMORY` in environment variables
2. Increase server memory allocation
3. Reduce `STOCKFISH_THREADS` to lower resource usage

### Port Already in Use

**Error**: `Address already in use`

**Solution**:
1. Allocate a different port
2. Or kill process using the port:
   ```
   lsof -i :8000
   kill -9 <PID>
   ```

### Slow Analysis

**Causes**:
- Insufficient CPU allocation
- Too many threads for available cores
- Server overloaded

**Solutions**:
1. Reduce `STOCKFISH_THREADS`
2. Increase CPU allocation
3. Use `movetime` parameter instead of `depth` for time-based analysis

## Performance Tuning

### For Fast Analysis (Web UI)

```
STOCKFISH_THREADS=2
STOCKFISH_MEMORY=256
```

### For Balanced Analysis

```
STOCKFISH_THREADS=4
STOCKFISH_MEMORY=512
```

### For Deep Analysis

```
STOCKFISH_THREADS=8
STOCKFISH_MEMORY=1024
```

## Backup & Restore

### Backup Server

1. **Via Pterodactyl Panel**
   - Go to server `Backups` tab
   - Click `Create Backup`
   - Download backup file

2. **Via Command Line**
   ```bash
   tar -czf stockfish-api-backup.tar.gz /path/to/server
   ```

### Restore Server

1. **Via Pterodactyl Panel**
   - Go to server `Backups` tab
   - Click restore icon on backup
   - Confirm restoration

## Monitoring & Logs

### View Logs

1. **Real-time Console**
   - Go to server `Console` tab
   - Monitor live output

2. **Download Logs**
   - Go to `File Manager`
   - Logs typically in server root directory

### Enable Debug Logging

Set environment variable:
```
ENVIRONMENT=development
```

This provides more detailed logging output.

## Update Guide

### Update to Latest Version

1. **Stop Server**
   - Click "Stop" button

2. **Update Files**
   - Via File Manager: Upload new files
   - Or via Git: Pull latest changes

3. **Update Dependencies**
   ```
   pip install --upgrade -r requirements.txt
   ```

4. **Restart Server**
   - Click "Start" button

## Security Considerations

### For Production Deployment

1. **Restrict Access**
   - Use firewall rules
   - Implement authentication
   - Use HTTPS/TLS

2. **Rate Limiting**
   - Implement rate limiting in reverse proxy
   - Example Nginx:
     ```nginx
     limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
     limit_req zone=api_limit burst=20 nodelay;
     ```

3. **Monitor Resources**
   - Set up alerts for high CPU/memory
   - Monitor API response times

### CORS Configuration

For production, restrict CORS origins in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

## Support & Resources

- **Pterodactyl Documentation**: https://pterodactyl.io/
- **Stockfish Documentation**: https://stockfishchess.org/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Repository Issues**: https://github.com/galihrhgnwn/Chess-Engine/issues

## Egg JSON Structure

The `egg.json` file contains:

- **Meta Information**: Version and metadata
- **Docker Image**: `ghcr.io/pterodactyl/yolks:python_3.11`
- **Startup Command**: `python main.py`
- **Installation Script**: Installs Stockfish and Python dependencies
- **Environment Variables**: Configurable options for Stockfish
- **Configuration**: Startup detection and stop command

### Customizing the Egg

To customize the egg for your needs:

1. Edit `egg.json`
2. Modify environment variables section
3. Update installation script if needed
4. Re-import in Pterodactyl Panel

## Example: Full Setup Walkthrough

### Step-by-Step Example

1. **Download egg.json**
   ```bash
   wget https://raw.githubusercontent.com/galihrhgnwn/Chess-Engine/main/egg.json
   ```

2. **Import in Pterodactyl**
   - Admin Panel → Nests → Import Egg → Upload egg.json

3. **Create Server**
   - Admin Panel → Servers → Create New
   - Select Stockfish 18 REST API egg
   - Allocate 1GB RAM, 2GB Disk
   - Assign port 8000

4. **Configure Variables**
   - STOCKFISH_THREADS: 4
   - STOCKFISH_MEMORY: 512
   - ENVIRONMENT: production

5. **Start Server**
   - Click Start
   - Wait for "Uvicorn running" message

6. **Access API**
   - Swagger UI: `http://server-ip:8000/docs`
   - API: `http://server-ip:8000/api/best-move`

7. **Test API**
   ```bash
   curl -X POST http://server-ip:8000/api/best-move \
     -H "Content-Type: application/json" \
     -d '{"fen":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1","depth":20}'
   ```

Done! Your Stockfish API is now running on Pterodactyl Panel.
