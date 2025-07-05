# Contributing to Autodidact

Thank you for your interest in contributing to Autodidact! This document provides guidelines and information for contributors.

## A Note About Educational Principles

An important foundational goal for this project is to encourage critical thinking, metacognition, and epistemic humility.

Self-directed learning, especially with the aid of LLM tools, where they are known for "hallucinating" as a direct side effect of how token prediction works, requires extra care to ensure one does not succumb to overconfidence or confirmation bias.

Before contributing to this project, it is important to have some understanding of the following principles:
* [Epistemic Cognition](https://en.wikipedia.org/wiki/Epistemic_cognition).
* [Metacognition](https://en.wikipedia.org/wiki/Metacognition).
* [Dunning-Kruger Effect](https://en.wikipedia.org/wiki/Dunning%E2%80%93Kruger_effect).

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL 12+
- Redis 6+
- Git

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/darren277/autodidact.git
   cd autodidact
   ```

2. **Set up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

3. **Configure Environment**
   ```bash
   # Copy example environment file
   cp env.example .env
   
   # Edit .env with your development settings
   # At minimum, you need:
   # - Database credentials
   # - Flask secret keys
   ```

4. **Set up Database**
   ```bash
   python manage.py create_tables
   python manage.py seed_data  # Optional: for testing
   ```

5. **Run Development Server**
   ```bash
   make w  # or python main.py
   ```

## 🏗️ Project Structure

```
autodidact/
├── lib/                    # Core application logic
│   ├── assistant/         # AI assistant functionality
│   ├── apis/             # External API integrations
│   ├── completions/      # OpenAI completions
│   ├── edu/              # Educational tools
│   ├── funcs/            # Function definitions
│   ├── tts/              # Text-to-speech
│   └── tools/            # Utility tools
├── models/               # Database models
├── routes/               # Flask routes and endpoints
├── templates/            # HTML templates
├── static/              # CSS, JS, and media files
├── k8s/                 # Kubernetes deployment files
├── tests/               # Test suite
└── utils/               # Utility scripts
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_dashboard.py
python -m pytest tests/test_encryption.py
python -m pytest tests/test_progress_tracking.py

# Run with coverage
python -m pytest --cov=lib --cov=models --cov=routes tests/
```

### Writing Tests
- Place tests in the `tests/` directory
- Follow the naming convention: `test_*.py`
- Use descriptive test function names
- Include both unit and integration tests

Example test structure:
```python
def test_user_creation():
    """Test user creation functionality"""
    # Arrange
    user_data = {"email": "test@example.com", "name": "Test User"}
    
    # Act
    user = User.create(**user_data)
    
    # Assert
    assert user.email == user_data["email"]
    assert user.name == user_data["name"]
```

## 📝 Code Style

### Python Style Guide
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where appropriate
- Keep functions small and focused
- Use descriptive variable and function names

### Code Formatting
```bash
# Install formatting tools
pip install black isort flake8

# Format code
black .
isort .

# Check code quality
flake8 .
```

### Commit Messages
Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Examples:
```
feat(auth): add OAuth2 authentication support
fix(database): resolve connection timeout issues
docs(setup): update installation instructions
```

## 🔄 Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes
- Write code following the style guide
- Add tests for new functionality
- Update documentation if needed

### 3. Test Your Changes
```bash
# Run tests
python -m pytest tests/

# Test manually
make w
# Visit http://localhost:5000 and test your changes
```

### 4. Commit Changes
```bash
git add .
git commit -m "feat(module): add new functionality"
```

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**
   - Operating system
   - Python version
   - Database version
   - Redis version

2. **Steps to Reproduce**
   - Clear, step-by-step instructions
   - Sample data if applicable

3. **Expected vs Actual Behavior**
   - What you expected to happen
   - What actually happened

4. **Error Messages**
   - Full error traceback
   - Log files if available

## 💡 Feature Requests

When requesting features:

1. **Describe the Problem**
   - What problem does this solve?
   - Who would benefit from this feature?

2. **Propose a Solution**
   - How should this feature work?
   - Any specific requirements or constraints?

3. **Consider Implementation**
   - Any technical considerations?
   - Impact on existing functionality?

## 🔧 Development Tools

### Recommended IDE Setup
- **VS Code**: Install Python extension
- **PyCharm**: Configure virtual environment
- **Vim/Emacs**: Use appropriate Python plugins

### Useful Extensions
- Python
- Flask
- Docker
- Kubernetes
- GitLens

### Debugging
```bash
# Enable debug mode
DEBUG=True

# Use Python debugger
import pdb; pdb.set_trace()

# Use logging
import logging
logging.debug("Debug message")
```

## 📚 Documentation

### Writing Documentation
- Use clear, concise language
- Include code examples
- Keep documentation up to date
- Use proper markdown formatting

### Documentation Structure
- `README.md`: Project overview and quick start
- `SETUP.md`: Detailed setup instructions
- `DEPLOYMENT.md`: Production deployment guide
- `ENVIRONMENT_VARIABLES.md`: Configuration reference
- `CONTRIBUTING.md`: This file

## 🔒 Security

### Security Guidelines
- Never commit sensitive data (API keys, passwords)
- Use environment variables for configuration
- Validate all user inputs
- Follow OWASP security guidelines
- Report security issues privately

### Reporting Security Issues
If you find a security vulnerability:
1. **DO NOT** create a public issue
2. Email the maintainers privately
3. Provide detailed information about the vulnerability
4. Allow time for assessment and fix

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Follow the project's coding standards

### Communication
- Use GitHub Issues for bug reports and feature requests
- Use GitHub Discussions for questions and ideas
- Be patient and helpful with newcomers
- Respect different skill levels and backgrounds

## 🎯 Areas for Contribution

### High Priority
- Bug fixes and performance improvements
- Security enhancements
- Documentation improvements
- Test coverage expansion

### Medium Priority
- New features and enhancements
- UI/UX improvements
- Integration with external services
- Mobile responsiveness

### Low Priority
- Code refactoring
- Style improvements
- Additional language support
- Advanced features

## 📞 Getting Help

### Resources
- [GitHub Issues](https://github.com/darren277/autodidact/issues)
- [GitHub Discussions](https://github.com/darren277/autodidact/discussions)
- [Documentation](./README.md)
- [Flask Documentation](https://flask.palletsprojects.com/)

### Questions
- Check existing issues and discussions first
- Provide context and error messages
- Be specific about your problem
- Show what you've tried

## 🏆 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes
- Project documentation
- Community acknowledgments

Thank you for contributing to Autodidact! 🎉 
