#!/usr/bin/env python3
"""
Simple test script to verify the save_notes functionality works.
This script tests the save_notes and get_notes API endpoints.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"  # Adjust port if needed
TEST_LESSON_ID = 1

def test_save_notes():
    """Test saving notes for a lesson"""
    print("Testing save_notes functionality...")
    
    # Test data
    test_notes = "These are my test notes for lesson 1. I learned about important concepts."
    
    # Prepare the request
    url = f"{BASE_URL}/api/save_notes"
    data = {
        "lesson_id": TEST_LESSON_ID,
        "content": test_notes
    }
    
    try:
        # Make the request
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Save notes test PASSED")
            return True
        else:
            print("❌ Save notes test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Error during save notes test: {e}")
        return False

def test_get_notes():
    """Test retrieving notes for a lesson"""
    print("\nTesting get_notes functionality...")
    
    url = f"{BASE_URL}/api/get_notes/{TEST_LESSON_ID}"
    
    try:
        # Make the request
        response = requests.get(url, headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Get notes test PASSED")
            return True
        else:
            print("❌ Get notes test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Error during get notes test: {e}")
        return False

def test_mark_lesson_complete():
    """Test marking a lesson as complete"""
    print("\nTesting mark_lesson_complete functionality...")
    
    url = f"{BASE_URL}/api/mark_lesson_complete"
    data = {
        "lesson_id": TEST_LESSON_ID
    }
    
    try:
        # Make the request
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Mark lesson complete test PASSED")
            return True
        else:
            print("❌ Mark lesson complete test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Error during mark lesson complete test: {e}")
        return False

def test_submit_question():
    """Test submitting a question"""
    print("\nTesting submit_question functionality...")
    
    url = f"{BASE_URL}/api/submit_question"
    data = {
        "lesson_id": TEST_LESSON_ID,
        "question": "Can you explain the concept of inheritance in more detail?"
    }
    
    try:
        # Make the request
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Submit question test PASSED")
            return True
        else:
            print("❌ Submit question test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Error during submit question test: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Testing Notes Functionality")
    print("=" * 50)
    
    # Note: These tests require user authentication
    # You may need to be logged in for these to work properly
    print("Note: These tests require user authentication.")
    print("Make sure you're logged in to the application first.")
    print()
    
    # Run tests
    save_success = test_save_notes()
    get_success = test_get_notes()
    complete_success = test_mark_lesson_complete()
    question_success = test_submit_question()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Save Notes: {'✅ PASSED' if save_success else '❌ FAILED'}")
    print(f"Get Notes: {'✅ PASSED' if get_success else '❌ FAILED'}")
    print(f"Mark Complete: {'✅ PASSED' if complete_success else '❌ FAILED'}")
    print(f"Submit Question: {'✅ PASSED' if question_success else '❌ FAILED'}")
    
    if all([save_success, get_success, complete_success, question_success]):
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 