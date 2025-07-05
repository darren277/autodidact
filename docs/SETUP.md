# Autodidact Setup Guide

This guide will help you set up and run the Autodidact application locally for development.

## Prerequisites

### Required Software
- **Python 3.12+** - [Download from python.org](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Download from postgresql.org](https://www.postgresql.org/download/)
- **Redis 6+** - [Download from redis.io](https://redis.io/download)
- **Make** (for Windows users) - Install via [GnuWin32](http://gnuwin32.sourceforge.net/packages/make.htm) or use Git Bash/WSL

### Optional Software
- **Docker & Docker Compose** - For containerized development
- **kubectl** - For Kubernetes deployment
- **Helm** - For Kubernetes package management

## Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd autodidact
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Database

#### Option A: Local PostgreSQL
1. Install PostgreSQL on your system
2. Create a database:
```sql
CREATE DATABASE autodidact;
CREATE USER autodidact_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE autodidact TO autodidact_user;
```

#### Option B: Docker PostgreSQL
```bash
docker run --name postgres-autodidact \
  -e POSTGRES_DB=autodidact \
  -e POSTGRES_USER=autodidact_user \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -d postgres:15
```

### 5. Set Up Redis

#### Option A: Local Redis
1. Install Redis on your system
2. Start Redis server:
```bash
redis-server
```

#### Option B: Docker Redis
```bash
docker run --name redis-autodidact \
  -p 6379:6379 \
  -d redis:7-alpine
```

## Environment Configuration

Create a `.env` file in the root directory with the following variables:

### Required Environment Variables
```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=autodidact_user
POSTGRES_PASS=your_password
POSTGRES_DB=autodidact

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379

# Flask Configuration
FLASK_APP_SECRET=your-super-secret-flask-key-change-this
DEBUG=True

# Master Encryption Key (for encrypting user API keys)
MASTER_ENCRYPTION_KEY=your-super-secret-master-key-change-this-in-production
```

### Optional Environment Variables
```bash
# Port Configuration
PORT=5000
BIND_IP=0.0.0.0
BIND_PORT=5000

# GPT Configuration
GPT_MODEL_ID=gpt-4o
GPT_ASSISTANT_NAME=Interactive Learning Companion

# System Prompt
SYSTEM_PROMPT=You are a personal tutor specializing in mathematics and science. Provide clear, step-by-step explanations to help students understand concepts.

# CORS Configuration
ENABLE_CORS=True

# Logging
LOG_LEVEL=DEBUG

# AWS Cognito (for production authentication)
AWS_REGION=us-east-1
COGNITO_DOMAIN=your-domain
USER_POOL_ID=your-user-pool-id
USER_POOL_CLIENT_ID=your-app-client-id
USER_POOL_CLIENT_SECRET=your-app-client-secret

# OpenProject Integration
OPENPROJECT_API_KEY=your-openproject-api-key
OPENPROJECT_URL=https://your-openproject-instance.com

# Blooms LLM Endpoint
BLOOMS_LLM_ENDPOINT=http://localhost:5055/blooms_llm

# Default Assistant ID
DEFAULT_ASSISTANT_ID=asst_X0dIT6aOTHFQgJNE923sjv8E
```

## Database Setup

### 1. Create Database Tables
```bash
python manage.py create_tables
```

### 2. Seed with Example Data (Optional)
```bash
python manage.py seed_data
```

### 3. Verify Setup
```bash
python manage.py show_tables
```

## Running the Application

### Development Mode
```bash
# Using Make (recommended)
make w

# Or directly with Python
python main.py
```

### Production Mode
```bash
# Using Gunicorn
make g

# Or using Waitress (Windows-friendly)
make w2
```

### Docker Mode
```bash
# Build and run with Docker
docker build -t autodidact .
docker run -p 5000:5000 --env-file .env autodidact
```

## Accessing the Application

Once running, the application will be available at:
- **Local Development**: http://localhost:5000
- **Production**: http://your-domain:5000

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database exists

2. **Redis Connection Error**
   - Verify Redis is running
   - Check Redis URL in `.env`

3. **Import Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

4. **Permission Errors (Windows)**
   - Run PowerShell as Administrator
   - Check file permissions

### Database Management Commands

```bash
# Create tables
python manage.py create_tables

# Drop all tables
python manage.py drop_tables

# Show table contents
python manage.py show_tables

# Migrate chat history (if upgrading)
python manage.py migrate_chat_history
```

### Logs and Debugging

- Check console output for error messages
- Set `DEBUG=True` in `.env` for detailed error pages
- Check `LOG_LEVEL=DEBUG` for verbose logging

## Next Steps

After successful setup:
1. Visit the application in your browser
2. Create your first course and lessons
3. Test the AI assistant functionality
4. Explore the note-taking features

For production deployment, see [DEPLOYMENT.md](./DEPLOYMENT.md). 