# Autodidact Deployment Guide

This guide covers deploying the Autodidact application to production environments, with a focus on Kubernetes deployment.

## Deployment Options

### 1. Kubernetes (Recommended for Production)
### 2. Docker Compose
### 3. Traditional Server Deployment

## Kubernetes Deployment

### Prerequisites

1. **Kubernetes Cluster**
   - AWS EKS, Google GKE, Azure AKS, or local (minikube/kind)
   - kubectl configured and connected

2. **Helm 3+**
   ```bash
   # Install Helm
   curl https://get.helm.sh/helm-v3.12.0-linux-amd64.tar.gz | tar xz
   sudo mv linux-amd64/helm /usr/local/bin/
   ```

3. **AWS CLI** (for ECR)
   ```bash
   # Install AWS CLI
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

### AWS ECR Setup

1. **Configure AWS CLI**
   ```bash
   aws configure
   ```

2. **Create ECR Repository**
   ```bash
   make create-repo
   ```

3. **Authenticate to ECR**
   ```bash
   make auth
   ```

### Environment Configuration

Create a production `.env` file with the following variables:

```bash
# Kubernetes Configuration
NAMESPACE=autodidact
DOCKER_REGISTRY=your-account.dkr.ecr.us-east-1.amazonaws.com
FLASK_IMAGE=autodidact_flask
FLASK_VERSION=latest
FLASK_PORT=5000

# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=autodidact_user
POSTGRES_PASS=your-secure-password
POSTGRES_DB=autodidact

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Flask Configuration
FLASK_APP_SECRET=your-super-secret-production-key
DEBUG=False

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Master Encryption Key
MASTER_ENCRYPTION_KEY=your-super-secret-master-key

# AWS Cognito Configuration
AWS_REGION=us-east-1
COGNITO_DOMAIN=your-cognito-domain
USER_POOL_ID=your-user-pool-id
USER_POOL_CLIENT_ID=your-client-id
USER_POOL_CLIENT_SECRET=your-client-secret

# Domain Configuration
HOST=your-domain.com
```

### Build and Push Docker Image

1. **Build the Image**
   ```bash
   make docker-flask
   ```

2. **Verify Image in ECR**
   ```bash
   aws ecr describe-images --repository-name autodidact_flask --region us-east-1
   ```

### Deploy to Kubernetes

1. **Create Namespace**
   ```bash
   make k8s-init
   ```

2. **Create Secrets**
   ```bash
   make k8s-auth
   ```

3. **Deploy Application**
   ```bash
   make k8s-deploy
   ```

4. **Verify Deployment**
   ```bash
   kubectl get pods -n autodidact
   kubectl get services -n autodidact
   kubectl get ingress -n autodidact
   ```

### Customizing the Deployment

Edit `k8s/values.yaml` to customize your deployment:

```yaml
namespace: autodidact
host: your-domain.com

flask:
  image:
    repository: your-account.dkr.ecr.us-east-1.amazonaws.com/autodidact_flask
    tag: latest
    pullPolicy: Always
  secret:
    name: flask-secret
    flaskAppSecret: your-flask-secret

postgres:
  db: autodidact
  host: postgres
  port: 5432
  secret:
    name: postgres-secret
    user: autodidact_user
    pass: your-secure-password

redis:
  host: redis
  port: 6379

auth:
  cognito:
    userPoolId: your-user-pool-id
    userPoolClientId: your-client-id
    cognitoDomain: your-cognito-domain
    secret:
      name: cognito-secret
      userPoolClientSecret: your-client-secret

openai:
  secret:
    name: openai-secret-api-key
    apiKey: your-openai-api-key
```

### SSL/TLS Configuration

The deployment includes cert-manager for automatic SSL certificate generation:

1. **Install cert-manager** (if not already installed)
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml
   ```

2. **Update cert-manager email** in `k8s/values.yaml`:
   ```yaml
   certManagerEmail: your-email@domain.com
   ```

### Monitoring and Logging

1. **View Application Logs**
   ```bash
   kubectl logs -f deployment/flask -n autodidact
   ```

2. **Access Application**
   ```bash
   kubectl port-forward service/flask 8080:5000 -n autodidact
   ```

3. **Check Resource Usage**
   ```bash
   kubectl top pods -n autodidact
   ```

## Docker Compose Deployment

For simpler deployments, use Docker Compose:

1. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   
   services:
     flask:
       build: .
       ports:
         - "5000:5000"
       environment:
         - POSTGRES_HOST=postgres
         - REDIS_HOST=redis
       depends_on:
         - postgres
         - redis
       env_file:
         - .env
   
     postgres:
       image: postgres:15
       environment:
         - POSTGRES_DB=autodidact
         - POSTGRES_USER=autodidact_user
         - POSTGRES_PASSWORD=your_password
       volumes:
         - postgres_data:/var/lib/postgresql/data
       ports:
         - "5432:5432"
   
     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"
   
   volumes:
     postgres_data:
   ```

2. **Deploy**
   ```bash
   docker-compose up -d
   ```

## Traditional Server Deployment

### Using Gunicorn

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/autodidact.service
   ```

   ```ini
   [Unit]
   Description=Autodidact Flask Application
   After=network.target
   
   [Service]
   User=autodidact
   WorkingDirectory=/opt/autodidact
   Environment=PATH=/opt/autodidact/.venv/bin
   ExecStart=/opt/autodidact/.venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Start Service**
   ```bash
   sudo systemctl enable autodidact
   sudo systemctl start autodidact
   ```

### Using Nginx as Reverse Proxy

1. **Install Nginx**
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

2. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/autodidact
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
   
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Enable Site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/autodidact /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## Database Migration

### Production Database Setup

1. **Create Production Database**
   ```sql
   CREATE DATABASE autodidact;
   CREATE USER autodidact_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE autodidact TO autodidact_user;
   ```

2. **Run Migrations**
   ```bash
   python manage.py create_tables
   ```

3. **Seed Data (Optional)**
   ```bash
   python manage.py seed_data
   ```

## Security Considerations

### Environment Variables
- Use strong, unique passwords
- Rotate secrets regularly
- Never commit `.env` files to version control

### Database Security
- Use SSL connections
- Restrict database access
- Regular backups

### Application Security
- Enable HTTPS
- Configure CORS properly
- Use secure session management
- Implement rate limiting

### Kubernetes Security
- Use RBAC
- Network policies
- Pod security policies
- Regular security updates

## Monitoring and Maintenance

### Health Checks
- Application health endpoint: `/health`
- Database connectivity checks
- Redis connectivity checks

### Backup Strategy
- Database backups (daily)
- Application logs
- Configuration backups

### Scaling
- Horizontal Pod Autoscaling (HPA)
- Database connection pooling
- Redis clustering for high availability

## Troubleshooting

### Common Kubernetes Issues

1. **Pod Not Starting**
   ```bash
   kubectl describe pod <pod-name> -n autodidact
   kubectl logs <pod-name> -n autodidact
   ```

2. **Service Not Accessible**
   ```bash
   kubectl get endpoints -n autodidact
   kubectl describe service <service-name> -n autodidact
   ```

3. **Ingress Issues**
   ```bash
   kubectl describe ingress -n autodidact
   kubectl get certificates -n autodidact
   ```

### Database Issues
- Check connection strings
- Verify database permissions
- Monitor connection limits

### Redis Issues
- Check Redis connectivity
- Monitor memory usage
- Verify persistence settings

## Rollback Procedures

### Kubernetes Rollback
```bash
# Rollback to previous deployment
kubectl rollout undo deployment/flask -n autodidact

# Check rollback status
kubectl rollout status deployment/flask -n autodidact
```

### Database Rollback
- Restore from backup
- Use database migration tools
- Test rollback procedures regularly

## Support and Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/) 