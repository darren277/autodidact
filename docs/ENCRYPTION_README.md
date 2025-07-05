# API Key Encryption System

This document describes the secure encryption system implemented for storing OpenAI API keys in the database.

## Overview

The system uses **AES-256 encryption** with **Fernet** (a symmetric encryption scheme) to securely store API keys in the PostgreSQL database. Each user's API key is encrypted with a unique salt, making it impossible to decrypt without the master key.

## Security Features

### 1. **Symmetric Encryption (AES-256)**
- Uses the `cryptography` library's Fernet implementation
- AES-256 encryption in CBC mode with PKCS7 padding
- Provides confidentiality and integrity

### 2. **Key Derivation (PBKDF2)**
- Uses PBKDF2-HMAC-SHA256 for key derivation
- 100,000 iterations for computational cost
- Unique salt per user prevents rainbow table attacks

### 3. **Salt Generation**
- 16-byte random salt generated for each user
- Stored alongside encrypted data
- Ensures same API key encrypts to different ciphertexts for different users

### 4. **Master Key Protection**
- Single master key used to derive user-specific encryption keys
- Should be stored securely in environment variables
- Never logged or exposed in application code

## Implementation Details

### Database Schema

```sql
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    sub VARCHAR(100) UNIQUE NOT NULL,
    encrypted_api_key TEXT,
    salt BYTEA,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Encryption Process

1. **Key Derivation**: Master key + user salt → user-specific encryption key
2. **Encryption**: API key + user-specific key → encrypted data
3. **Storage**: Encrypted data + salt stored in database

### Decryption Process

1. **Key Derivation**: Master key + stored salt → user-specific encryption key
2. **Decryption**: Encrypted data + user-specific key → original API key

## Usage

### Setting an API Key

```python
from models.user import User
from settings import MASTER_ENCRYPTION_KEY

user = User.find_by_sub(user_sub)
user.set_api_key("sk-your-api-key-here", MASTER_ENCRYPTION_KEY)
db.session.commit()
```

### Retrieving an API Key

```python
from utils.api_key_manager import get_user_api_key

api_key = get_user_api_key(user_sub)
if api_key:
    # Use the API key
    pass
```

## Environment Variables

Add to your `.env` file:

```bash
# Strong, random master key (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
MASTER_ENCRYPTION_KEY=your-super-secret-master-key-change-this-in-production
```

## Security Best Practices

### 1. **Master Key Management**
- Generate a strong, random master key
- Store in environment variables, not in code
- Rotate master key periodically
- Use different keys for development/staging/production

### 2. **Database Security**
- Encrypt database at rest
- Use strong database passwords
- Limit database access to application only
- Regular security audits

### 3. **Application Security**
- Use HTTPS in production
- Implement proper session management
- Log security events
- Regular dependency updates

### 4. **Key Rotation**
- Implement API key rotation procedures
- Monitor for suspicious activity
- Have incident response plan

## Migration from Session Storage

The system automatically migrates users from session storage to database storage:

1. User logs in → User record created in database
2. User visits settings → API key status checked from database
3. User saves API key → Encrypted and stored in database
4. Session updated with `has_api_key` status

## Testing

Run the encryption test:

```bash
python test_encryption.py
```

This will verify:
- Basic encryption/decryption functionality
- User model integration
- Key derivation and salt generation

## Troubleshooting

### Common Issues

1. **Decryption fails**: Check master key is correct
2. **Salt missing**: User record may be corrupted
3. **Import errors**: Ensure `cryptography` package is installed

### Recovery Procedures

1. **Lost master key**: Cannot recover encrypted data
2. **Corrupted user record**: Delete and recreate user
3. **Database issues**: Restore from backup

## Future Enhancements

1. **Key Rotation**: Implement automatic key rotation
2. **Audit Logging**: Log all API key operations
3. **Multi-factor**: Add additional authentication for API key access
4. **Hardware Security**: Use HSM for master key storage 