""""""
# Test script for encryption functionality

import os
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

def test_encryption():
    """Test the encryption/decryption functionality"""
    
    # Test master key
    master_key = "test-master-key-for-encryption"
    
    # Test API key
    test_api_key = "sk-test1234567890abcdef"
    
    print("Testing encryption functionality...")
    print(f"Master key: {master_key}")
    print(f"Test API key: {test_api_key}")
    print("-" * 50)
    
    # Generate salt
    salt = os.urandom(16)
    print(f"Generated salt: {salt.hex()}")
    
    # Derive key from master key and salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
    print(f"Derived key: {key.decode()}")
    
    # Create Fernet cipher and encrypt
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(test_api_key.encode())
    print(f"Encrypted data: {encrypted_data}")
    
    # Decrypt
    decrypted_data = cipher.decrypt(encrypted_data)
    decrypted_api_key = decrypted_data.decode()
    print(f"Decrypted API key: {decrypted_api_key}")
    
    # Verify
    if decrypted_api_key == test_api_key:
        print("✅ Encryption/decryption test PASSED!")
        return True
    else:
        print("❌ Encryption/decryption test FAILED!")
        return False

def test_user_model():
    """Test the User model encryption methods"""
    print("\n" + "=" * 50)
    print("Testing User model encryption methods...")
    
    try:
        from models.user import User
        from main import app, db
        
        with app.app_context():
            # Create a test user
            test_user = User(
                email="test@example.com",
                name="Test User",
                sub="test-sub-123"
            )
            
            master_key = "test-master-key"
            test_api_key = "sk-test1234567890abcdef"
            
            # Test setting API key
            test_user.set_api_key(test_api_key, master_key)
            print(f"✅ API key encrypted and stored")
            print(f"   Encrypted data length: {len(test_user.encrypted_api_key) if test_user.encrypted_api_key else 0}")
            print(f"   Salt length: {len(test_user.salt) if test_user.salt else 0}")
            
            # Test retrieving API key
            retrieved_key = test_user.get_api_key(master_key)
            print(f"✅ API key retrieved: {retrieved_key}")
            
            # Verify
            if retrieved_key == test_api_key:
                print("✅ User model encryption test PASSED!")
                return True
            else:
                print("❌ User model encryption test FAILED!")
                return False
                
    except Exception as e:
        print(f"❌ User model test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("Running encryption tests...")
    
    test1_passed = test_encryption()
    test2_passed = test_user_model()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"Basic encryption test: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"User model test: {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        print("🎉 All tests passed! Encryption is working correctly.")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Please check the implementation.")
        sys.exit(1)