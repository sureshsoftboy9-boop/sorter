# 🐳 PhotoSort Docker Setup Guide

## Overview
PhotoSort can now be easily deployed using Docker on any machine (Zima, Linux, Mac, Windows with Docker).

## Prerequisites
- Docker installed ([Get Docker](https://www.docker.com/products/docker-desktop))
- Docker Compose installed (comes with Docker Desktop)

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# 1. Navigate to sorter directory
cd /path/to/sorter

# 2. Build and start the container
docker-compose up -d

# 3. Open in browser
http://localhost:5000

# 4. Stop the container
docker-compose down
```

### Option 2: Using Docker Directly

```bash
# 1. Build the image
docker build -t photosort .

# 2. Run the container
docker run -d \
  --name photosort \
  -p 5000:5000 \
  -v photosort_data:/app \
  photosort

# 3. Open in browser
http://localhost:5000

# 4. Stop the container
docker stop photosort
docker rm photosort
```

## Advanced Configuration

### Mount Photo Directories

To access your photo directories on the host machine:

```bash
docker run -d \
  --name photosort \
  -p 5000:5000 \
  -v /path/to/source/photos:/photos/source \
  -v /path/to/dest/photos:/photos/dest \
  -v photosort_data:/app \
  photosort
```

Then in the app, use:
- Source: `/photos/source`
- Destination: `/photos/dest`

### Using Different Port

```bash
docker run -d \
  --name photosort \
  -p 8080:5000 \
  -v photosort_data:/app \
  photosort
```

Then access at: `http://localhost:8080`

### Custom Docker Compose with Volumes

Create an advanced `docker-compose.yml`:

```yaml
version: '3.8'

services:
  photosort:
    build: .
    ports:
      - "5000:5000"
    volumes:
      # App data
      - photosort_data:/app
      # Photo directories (customize these paths)
      - /mnt/photos/source:/photos/source
      - /mnt/photos/sorted:/photos/sorted
    environment:
      - FLASK_APP=app.py
      - FLASK_ENV=production
    restart: unless-stopped
    container_name: photosort

volumes:
  photosort_data:
    driver: local
```

## Usage on Different Devices

### Zima Machine
```bash
# 1. Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Add user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER

# 3. Run PhotoSort
docker-compose up -d

# 4. Access from any device on network:
# http://zima-ip:5000
```

### Linux Server
```bash
# Same as Zima - just install Docker and run docker-compose up
docker-compose up -d
```

### Access from Other Devices on Network

Once running in Docker:

1. **Find your machine's IP:**
   ```bash
   # Linux/Mac
   ifconfig | grep "inet "
   
   # Windows (in PowerShell)
   ipconfig | findstr "IPv4"
   ```

2. **Access from any device:**
   - Open browser
   - Go to: `http://your-machine-ip:5000`
   - Example: `http://192.168.1.100:5000`

3. **On mobile/tablet:**
   - Same URL in mobile browser
   - Full touch support included!

## Docker Files Explanation

### Dockerfile
- Uses Python 3.9 slim image (small, efficient)
- Installs image processing libraries (Pillow dependencies)
- Copies app and static files
- Exposes port 5000
- Runs Flask app in production mode

### docker-compose.yml
- Simplifies container management
- Auto-restarts if container crashes
- Mounts persistent data volume
- Easy port configuration
- One command to manage everything

## Useful Docker Commands

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View container logs
docker logs photosort

# Follow logs in real-time
docker logs -f photosort

# Stop container
docker stop photosort

# Start container
docker start photosort

# Remove container
docker rm photosort

# View volumes
docker volume ls

# Inspect container
docker inspect photosort

# Execute command in container
docker exec -it photosort bash
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs photosort

# Rebuild image
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use
```bash
# Use different port in docker-compose.yml or:
docker run -p 8080:5000 photosort
```

### Can't access from other devices
- Make sure firewall allows port 5000
- Check machine IP address is correct
- Try `http://localhost:5000` from same machine first

### Permission denied errors
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

## Performance Tips

1. **Use volumes for persistent data** - session.json, config.json persist between container restarts
2. **Add more RAM** - For large photo collections, allocate more memory to Docker
3. **Use SSD storage** - Faster thumbnail generation
4. **Network access** - App runs at full speed on local network

## Data Persistence

All data is stored in Docker volumes:
- `photosort_data:/app` - Contains session.json, config.json, cache
- Photo directories - Mount from host using volumes
- Data persists even if container is removed

## Backing Up Data

```bash
# Export volume data
docker run --rm -v photosort_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/photosort_backup.tar.gz -C /data .

# Restore volume data
docker run --rm -v photosort_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/photosort_backup.tar.gz -C /data
```

## Deployment Scenarios

### Single Machine (Zima)
```bash
# On Zima, run once:
docker-compose up -d

# Access from any device on network
http://zima-ip:5000
```

### Multiple Machines
- Deploy same image to multiple machines
- Each has its own separate data
- Scale photo sorting across team

### Cloud Deployment
- Use same Docker image
- Deploy to AWS, Azure, Google Cloud, etc.
- Access from anywhere

## Production Considerations

For production use:
1. **Reverse Proxy** - Use Nginx in front of Flask
2. **HTTPS** - Use SSL certificates (Let's Encrypt)
3. **Authentication** - Add password protection
4. **Backups** - Regular backup of volumes
5. **Monitoring** - Use docker logging/monitoring tools

## Further Reading

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Guide](https://docs.docker.com/compose/)
- [Flask Deployment](https://flask.palletsprojects.com/deployment/)

---

**Status: ✅ Ready for Docker Deployment**

Your PhotoSort app is now containerized and ready to deploy on any device with Docker!

Happy photo sorting! 🚀📸
