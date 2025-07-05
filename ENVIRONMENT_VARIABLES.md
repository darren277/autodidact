# Environment Variables Reference

This document provides a comprehensive reference for all environment variables used in the Autodidact application.

## Quick Start

Create a `.env` file in the root directory with the minimum required variables:

```bash
# Required for basic functionality
OPENAI_API_KEY=your-openai-api-key
POSTGRES_HOST=localhost
POSTGRES_USER=autodidact_user
POSTGRES_PASS=your_password
POSTGRES_DB=autodidact
FLASK_APP_SECRET=your-secret-key
MASTER_ENCRYPTION_KEY=your-master-key
```

## Complete Reference

### Application Configuration

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `5000` | No | Port number for the Flask application |
| `HOST` | `0.0.0.0` | No | Host address to bind the application to |
| `DEBUG` | `False` | No | Enable debug mode (True/False) |
| `ENABLE_CORS` | `True` | No | Enable Cross-Origin Resource Sharing |
| `LOG_LEVEL` | `DEBUG` | No | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Database Configuration (PostgreSQL)

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `POSTGRES_HOST` | `localhost` | Yes | PostgreSQL server hostname |
| `POSTGRES_PORT` | `5432` | No | PostgreSQL server port |
| `POSTGRES_USER` | `myusername` | Yes | PostgreSQL username |
| `POSTGRES_PASS` | `mypassword` | Yes | PostgreSQL password |
| `POSTGRES_DB` | `autodidact` | No | PostgreSQL database name |

### Redis Configuration

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `REDIS_URL` | `redis://localhost` | No | Redis connection URL |
| `REDIS_HOST` | `localhost` | No | Redis server hostname |
| `REDIS_PORT` | `6379` | No | Redis server port |

### Security Configuration

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `FLASK_APP_SECRET` | `some super secret key...` | Yes | Flask application secret key |
| `MASTER_ENCRYPTION_KEY` | `your-super-secret-master-key...` | Yes | Master key for encrypting user API keys |

### OpenAI Configuration

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `OPENAI_API_KEY` | - | Yes | OpenAI API key for GPT models |
| `GPT_MODEL_ID` | `gpt-4o` | No | Default GPT model to use |
| `GPT_ASSISTANT_NAME` | `Interactive Learning Companion` | No | Name for the AI assistant |
| `DEFAULT_ASSISTANT_ID` | `asst_X0dIT6aOTHFQgJNE923sjv8E` | No | Default OpenAI assistant ID |

### AI/LLM Configuration

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `SYSTEM_PROMPT` | `You are a personal tutor...` | No | Default system prompt for AI |
| `BLOOMS_LLM_ENDPOINT` | `http://localhost:5055/blooms_llm` | No | Blooms LLM service endpoint |

### AWS Cognito Configuration (Authentication)

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `AWS_REGION` | `us-east-1` | No | AWS region for Cognito |
| `COGNITO_DOMAIN` | `your-domain` | No | Cognito domain name |
| `USER_POOL_ID` | `your-user-pool-id` | No | Cognito User Pool ID |
| `USER_POOL_CLIENT_ID` | `your-app-client-id` | No | Cognito App Client ID |
| `USER_POOL_CLIENT_SECRET` | `your-app-client-secret` | No | Cognito App Client Secret |

### OpenProject Integration

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `OPENPROJECT_API_KEY` | - | No | OpenProject API key |
| `OPENPROJECT_URL` | - | No | OpenProject instance URL |

### Kubernetes Deployment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `NAMESPACE` | `autodidact` | No | Kubernetes namespace |
| `DOCKER_REGISTRY` | - | No | Docker registry URL (e.g., ECR) |
| `FLASK_IMAGE` | `autodidact_flask` | No | Docker image name |
| `FLASK_VERSION` | `latest` | No | Docker image tag |
| `FLASK_PORT` | `5000` | No | Container port |
| `BIND_IP` | `0.0.0.0` | No | IP address to bind to |
| `BIND_PORT` | `5000` | No | Port to bind to |

## Environment-Specific Configurations

### Development Environment

```bash
# Development .env
DEBUG=True
LOG_LEVEL=DEBUG
POSTGRES_HOST=localhost
REDIS_HOST=localhost
FLASK_APP_SECRET=dev-secret-key-change-in-production
MASTER_ENCRYPTION_KEY=dev-master-key-change-in-production
OPENAI_API_KEY=your-openai-api-key
```

### Production Environment

```bash
# Production .env
DEBUG=False
LOG_LEVEL=INFO
POSTGRES_HOST=your-production-db-host
REDIS_HOST=your-production-redis-host
FLASK_APP_SECRET=your-super-secure-production-secret
MASTER_ENCRYPTION_KEY=your-super-secure-production-master-key
OPENAI_API_KEY=your-openai-api-key
AWS_REGION=us-east-1
COGNITO_DOMAIN=your-cognito-domain
USER_POOL_ID=your-user-pool-id
USER_POOL_CLIENT_ID=your-client-id
USER_POOL_CLIENT_SECRET=your-client-secret
```

### Kubernetes Environment

```bash
# Kubernetes .env
NAMESPACE=autodidact
DOCKER_REGISTRY=your-account.dkr.ecr.us-east-1.amazonaws.com
FLASK_IMAGE=autodidact_flask
FLASK_VERSION=latest
POSTGRES_HOST=postgres
REDIS_HOST=redis
DEBUG=False
```

## Security Best Practices

### Required Variables for Security

1. **FLASK_APP_SECRET**
   - Must be a strong, random string
   - Minimum 32 characters recommended
   - Used for session encryption and CSRF protection

2. **MASTER_ENCRYPTION_KEY**
   - Must be a strong, random string
   - Minimum 32 characters recommended
   - Used to encrypt user API keys in the database

3. **OPENAI_API_KEY**
   - Valid OpenAI API key
   - Keep secure and rotate regularly

### Variable Security Guidelines

- **Never commit `.env` files** to version control
- Use **strong, unique passwords** for all services
- **Rotate secrets regularly** in production
- Use **environment-specific** configurations
- **Limit access** to production environment variables

## Validation and Testing

### Validate Environment Setup

```bash
# Test database connection
python manage.py show_tables

# Test Redis connection
python -c "import redis; r = redis.Redis(); r.ping()"

# Test OpenAI connection
python -c "import openai; openai.api_key='your-key'; print('Valid')"
```

### Environment Variable Validation

The application validates required environment variables on startup:

```python
# Required variables that will cause startup failure if missing:
required_vars = [
    'OPENAI_API_KEY',
    'POSTGRES_HOST',
    'POSTGRES_USER', 
    'POSTGRES_PASS',
    'FLASK_APP_SECRET',
    'MASTER_ENCRYPTION_KEY'
]
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASS`
   - Check if PostgreSQL is running
   - Ensure database exists

2. **Redis Connection Errors**
   - Verify `REDIS_HOST`, `REDIS_PORT`
   - Check if Redis is running

3. **OpenAI API Errors**
   - Verify `OPENAI_API_KEY` is valid
   - Check API key permissions
   - Ensure sufficient credits

4. **Authentication Errors**
   - Verify Cognito configuration
   - Check redirect URIs
   - Ensure client secrets are correct

### Debug Mode

Enable debug mode for detailed error information:

```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

### Environment Variable Loading

The application uses `python-dotenv` to load environment variables:

```python
from dotenv import load_dotenv
load_dotenv()
```

Variables are loaded in this order:
1. System environment variables
2. `.env` file in project root
3. Default values in `settings.py`

## Migration and Updates

### Adding New Variables

1. Add the variable to `settings.py` with a default value
2. Update this documentation
3. Add validation if required
4. Update deployment configurations

### Deprecating Variables

1. Mark as deprecated in `settings.py`
2. Add warning messages
3. Provide migration path
4. Remove in future version

## Related Documentation

- [Setup Guide](./SETUP.md) - Initial setup instructions
- [Deployment Guide](./DEPLOYMENT.md) - Production deployment
- [Security Guide](./SECURITY.md) - Security best practices 