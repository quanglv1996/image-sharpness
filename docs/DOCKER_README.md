# 🐳 Docker Deployment

Nhanh chóng setup và deploy Image Sharpness Analyzer trên server sử dụng Docker.

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone project
cd image-sharpness

# Start application
docker-compose up --build

# Access at: http://localhost:5000
```

### Option 2: Helper Scripts

**Linux/Mac:**
```bash
chmod +x docker-run.sh
./docker-run.sh up
```

**Windows:**
```bash
docker-run.bat up
```

### Option 3: Manual Docker Commands

```bash
# Build
docker build -t image-sharpness:latest .

# Run
docker run -d -p 5000:5000 -v $(pwd)/uploads:/app/uploads --name image-sharpness image-sharpness:latest
```

## 📋 Available Commands

Using `docker-compose`:
```bash
docker-compose up --build    # Build and start
docker-compose down          # Stop
docker-compose logs -f       # View logs
docker-compose ps            # Status
```

Using helper scripts:
```bash
./docker-run.sh build        # Build
./docker-run.sh up           # Start
./docker-run.sh down         # Stop
./docker-run.sh logs         # Logs
./docker-run.sh shell        # Shell access
./docker-run.sh clean        # Remove everything
./docker-run.sh rebuild      # Full rebuild
```

## 📝 Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Docker image configuration |
| `docker-compose.yml` | Multi-container orchestration |
| `.dockerignore` | Exclude files from image |
| `.env.example` | Example environment variables |
| `docker-run.sh` | Linux/Mac helper script |
| `docker-run.bat` | Windows helper script |
| `DOCKER_GUIDE.md` | Detailed guide |

## 🌍 Server Deployment

### Using docker-compose on Server

```bash
# SSH to server
ssh user@server.com

# Clone project
git clone <repo> image-sharpness
cd image-sharpness

# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Using Nginx Reverse Proxy

Create `nginx.conf`:
```nginx
upstream app {
    server app:5000;
}

server {
    listen 80;
    server_name example.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Add to `docker-compose.yml`:
```yaml
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - app
```

## 🔧 Configuration

Create `.env` from `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` for custom settings:
```
FLASK_ENV=production
FLASK_DEBUG=0
MAX_UPLOAD_SIZE=50
```

## 💾 Volumes & Data

Uploaded images are stored in `./uploads/`:
```
./uploads/
├── image1.png
├── image2.jpg
└── ...
```

To backup:
```bash
docker cp image-sharpness-app:/app/uploads ./uploads_backup
```

## 🐛 Troubleshooting

**Port already in use:**
```bash
# Change port in docker-compose.yml
ports:
  - "8000:5000"
```

**View logs:**
```bash
docker-compose logs -f app
```

**Rebuild everything:**
```bash
docker-compose down -v
docker-compose up --build
```

## 📊 Monitoring

```bash
# Container status
docker ps

# Resource usage
docker stats

# View logs
docker logs -f container_id

# Execute command in container
docker exec -it container_id bash
```

## 🔐 Production Checklist

- [ ] Use `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=0`
- [ ] Use Gunicorn or similar WSGI server
- [ ] Add Nginx reverse proxy
- [ ] Setup SSL/HTTPS
- [ ] Configure logging
- [ ] Setup health checks
- [ ] Monitor resource usage
- [ ] Regular backups of uploads

## 📚 More Info

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for detailed documentation.
