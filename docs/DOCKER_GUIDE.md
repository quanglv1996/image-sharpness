# Docker Setup Guide

Hướng dẫn để chạy Image Sharpness Analyzer trên Docker.

## Prerequisites

- Docker >= 20.10
- Docker Compose >= 1.29

## Quick Start

### 1. Build và chạy với Docker Compose

```bash
# Clone hoặc cd vào project directory
cd image-sharpness

# Build image và run container
docker-compose up --build
```

Ứng dụng sẽ chạy tại: **http://localhost:5000**

### 2. Stop container

```bash
docker-compose down
```

## Chi tiết Build

### Build manual (không dùng docker-compose)

```bash
# Build image
docker build -t image-sharpness:latest .

# Run container
docker run -it -p 5000:5000 -v $(pwd)/uploads:/app/uploads image-sharpness:latest
```

### Với Windows (PowerShell)

```bash
docker run -it -p 5000:5000 -v ${PWD}/uploads:/app/uploads image-sharpness:latest
```

## Cấu hình Docker Compose

**docker-compose.yml** chứa:
- **build** - Build Dockerfile tự động
- **ports** - Map port 5000 từ container → host
- **volumes** - Persist uploaded images
- **environment** - Flask configuration
- **restart** - Tự động restart khi lỗi
- **healthcheck** - Kiểm tra health status

## Volumes

Container sử dụng `./uploads` directory để lưu uploaded images:

```
./uploads/
├── image1.png
├── image2.jpg
└── ...
```

Folder này được tự động tạo nếu chưa tồn tại.

## Environment Variables

Có thể override trong docker-compose.yml:

```yaml
environment:
  - FLASK_ENV=production    # production hoặc development
  - FLASK_DEBUG=0           # 0 = off, 1 = on
  - FLASK_PORT=5000         # Custom port
```

## Troubleshooting

### Container không start

```bash
# Xem logs
docker-compose logs -f app

# Hoặc manual
docker logs <container_id>
```

### Port 5000 đã được sử dụng

Sửa port trong docker-compose.yml:

```yaml
ports:
  - "8000:5000"  # Map port 8000 của host → 5000 của container
```

### OpenCV errors

Dockerfile đã cài dependencies cần thiết (`libglib2.0-0`, `libsm6`, `libxext6`). Nếu vẫn có lỗi, rebuild:

```bash
docker-compose up --build --force-recreate
```

### Upload file size limit

Mặc định Flask limit file size. Để increase, sửa `app.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
```

## Production Deployment

Cho production deployment, xem xét:

1. **Use Gunicorn** thay vì Flask development server:

```dockerfile
RUN pip install gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

2. **Nginx reverse proxy** - Add nginx service trong docker-compose
3. **Environment variables** - Use `.env` file
4. **Persistent storage** - Mount volumes trên host

## Performance Tips

- Increase workers trong docker-compose:
  ```yaml
  environment:
    - GUNICORN_WORKERS=4
  ```

- Limit CPU/Memory:
  ```yaml
  services:
    app:
      deploy:
        resources:
          limits:
            cpus: '2'
            memory: 2G
  ```

## File Structure

```
image-sharpness/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
├── app.py
├── src/
│   └── sharpness/
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── uploads/  # Auto-created by container
```

## Useful Commands

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# Remove stopped container
docker rm <container_id>

# Remove image
docker rmi image-sharpness:latest

# Clean up unused resources
docker system prune -a

# View container resource usage
docker stats

# Shell into running container
docker exec -it <container_id> /bin/bash
```

## Publish to Docker Hub

```bash
# Tag image
docker tag image-sharpness:latest your-username/image-sharpness:latest

# Login
docker login

# Push
docker push your-username/image-sharpness:latest
```

Người khác có thể run:
```bash
docker run -p 5000:5000 your-username/image-sharpness:latest
```
