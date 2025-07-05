# Autodidact

You are the teacher and the student.

An LLM-enriched learning platform for designing lesson plans for others or for yourself. Built with Python, Flask, and OpenAI's GPT models.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 12+
- Redis 6+
- ~~OpenAI API Key~~ (Optional - added via `settings` page from the app itself)
  - Get your API key from: https://platform.openai.com/api-keys

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd autodidact
   ```

2. **Set up environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   # Copy and edit the environment template
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Set up database**
   ```bash
   python manage.py create_tables
   python manage.py seed_data  # Optional: add sample data
   ```

5. **Run the application**
   ```bash
   make w  # Development mode
   # or
   python main.py
   ```

Visit http://localhost:5000 to access the application.

## 📚 Documentation

- **[Setup Guide](./SETUP.md)** - Detailed setup instructions
- **[Deployment Guide](./DEPLOYMENT.md)** - Production deployment (Kubernetes, Docker, etc.)
- **[Environment Variables](./ENVIRONMENT_VARIABLES.md)** - Complete environment variable reference
- **[Database Migration](./DATABASE_MIGRATION_SUMMARY.md)** - Database schema and migration details
- **[Encryption Guide](./ENCRYPTION_README.md)** - Security and encryption implementation

## 🏗️ Architecture

### Core Components
- **Flask Web Application** - Main web interface
- **PostgreSQL Database** - Data persistence
- **Redis** - Caching and session management
- **OpenAI GPT** - AI-powered learning assistance
- **AWS Cognito** - User authentication (production)

### Key Features
- **Course Management** - Create and organize learning content
- **AI Assistant** - Interactive learning companion
- **Note Taking** - Multiple note formats (Cornell, Mind Map, etc.)
- **Progress Tracking** - Monitor learning progress
- **Media Integration** - Support for videos and annotations

## 🛠️ Development

### Project Structure
```
autodidact/
├── lib/                    # Core application logic
│   ├── assistant/         # AI assistant functionality
│   ├── apis/             # External API integrations
│   └── tools/            # Utility tools
├── models/               # Database models
├── routes/               # Flask routes and endpoints
├── templates/            # HTML templates
├── static/              # CSS, JS, and media files
├── k8s/                 # Kubernetes deployment files
└── tests/               # Test suite
```

### Available Commands

#### Development
```bash
make w          # Run with Waitress (Windows-friendly)
make g          # Run with Gunicorn
python main.py  # Run directly with Flask
```

#### Database Management
```bash
python manage.py create_tables    # Create database tables
python manage.py drop_tables      # Drop all tables
python manage.py seed_data        # Add sample data
python manage.py show_tables      # Display table contents
```

#### Docker & Kubernetes
```bash
make docker-flask    # Build Docker image
make k8s-deploy      # Deploy to Kubernetes
make k8s-debug       # Debug Kubernetes deployment
```

## 🔧 Configuration

### Required Environment Variables
```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_USER=autodidact_user
POSTGRES_PASS=your_password
POSTGRES_DB=autodidact

# Security
FLASK_APP_SECRET=your-secret-key
MASTER_ENCRYPTION_KEY=your-master-key
```

See [Environment Variables](./ENVIRONMENT_VARIABLES.md) for complete configuration options.

## 🚀 Deployment

### Local Development
```bash
make w  # Start development server
```

### Docker
```bash
docker build -t autodidact .
docker run -p 5000:5000 --env-file .env autodidact
```

### Kubernetes (Production)
```bash
make k8s-deploy  # Deploy to Kubernetes cluster
```

See [Deployment Guide](./DEPLOYMENT.md) for detailed deployment instructions.

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python -m pytest tests/test_dashboard.py
python -m pytest tests/test_encryption.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the docs folder for detailed guides
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions and ideas

## 🔗 Related Projects

- **OpenProject Integration** - Import courses from OpenProject
- **Google Calendar Integration** - Schedule learning sessions
- **TTS Integration** - Text-to-speech for accessibility

---

**Note**: This is an educational platform designed to enhance self-directed learning through AI assistance. The system supports both individual learners and educators creating content for others.
