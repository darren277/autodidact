# Save Notes Functionality Implementation

This document describes the implementation of the save_notes functionality for the lesson view page.

## Overview

The save_notes functionality allows users to save their personal notes for each lesson. Notes are associated with both the lesson and the user, so each user can have their own notes for each lesson.

## Changes Made

### 1. Database Model Updates (`models/lessons.py`)

- **Updated Notes model**: Added `user_id` field to associate notes with specific users
- **Relationship**: Notes now have a one-to-one relationship with both lesson and user

```python
class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # NEW FIELD
```

### 2. API Endpoints (`main.py`)

Added three new API endpoints:

#### `/api/save_notes` (POST)
- **Purpose**: Save or update user notes for a lesson
- **Authentication**: Required (user must be logged in)
- **Request Body**:
  ```json
  {
    "lesson_id": 1,
    "content": "User's notes content..."
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Notes saved successfully"
  }
  ```

#### `/api/get_notes/<lesson_id>` (GET)
- **Purpose**: Retrieve user's notes for a specific lesson
- **Authentication**: Required (user must be logged in)
- **Response**:
  ```json
  {
    "success": true,
    "content": "User's notes content..."
  }
  ```

#### `/api/mark_lesson_complete` (POST)
- **Purpose**: Mark a lesson as complete (placeholder implementation)
- **Authentication**: Required (user must be logged in)
- **Request Body**:
  ```json
  {
    "lesson_id": 1
  }
  ```

#### `/api/submit_question` (POST)
- **Purpose**: Submit a question about a lesson (placeholder implementation)
- **Authentication**: Required (user must be logged in)
- **Request Body**:
  ```json
  {
    "lesson_id": 1,
    "question": "User's question..."
  }
  ```

### 3. Frontend Updates

#### Template Updates (`templates/lessons/view.html`)
- **Notes textarea**: Now populated with existing user notes when page loads
- **Dynamic content**: `{{ user_notes }}` variable displays user's saved notes

#### JavaScript Updates (`static/js/view-lesson.js`)
- **Save button state**: Properly initialized as disabled when no changes
- **Error handling**: Improved error handling and user feedback
- **Status messages**: Clear success/error messages for user actions

### 4. Lesson View Route Updates (`main.py`)

Updated `view_lesson()` function to:
- Load existing user notes from database
- Handle cases where user is not authenticated
- Provide fallback for missing notes

## Database Migration

Since the Notes model was updated with a new field, you need to recreate the database tables:

```bash
# Drop existing tables
make drop

# Create new tables with updated schema
make create
```

## Testing

### 1. Manual Testing

1. **Start the application**:
   ```bash
   python wsgi.py
   ```

2. **Login to the application** (required for authentication)

3. **Navigate to a lesson page** (e.g., `/view_lesson/1`)

4. **Test the save notes functionality**:
   - Type some notes in the textarea
   - Click the "Save" button
   - Verify the success message appears
   - Refresh the page and verify notes are still there

### 2. Automated Testing

Run the test script:

```bash
python test_save_notes.py
```

**Note**: The test script requires user authentication. Make sure you're logged in to the application first.

### 3. Integration Testing

Run the integration tests:

```bash
python tests/integration/lessons_crud.py
```

## Security Considerations

1. **Authentication**: All notes endpoints require user authentication
2. **User Isolation**: Notes are isolated by user - users can only access their own notes
3. **Input Validation**: Basic validation for required fields
4. **Error Handling**: Proper error handling and user feedback

## Future Enhancements

1. **Real-time saving**: Auto-save notes as user types
2. **Version history**: Track changes to notes over time
3. **Rich text editing**: Support for formatting, images, etc.
4. **Note sharing**: Allow users to share notes with others
5. **Note templates**: Pre-defined note templates for different lesson types
6. **Export functionality**: Export notes to various formats (PDF, Markdown, etc.)

## Troubleshooting

### Common Issues

1. **"User not authenticated" error**:
   - Make sure you're logged in to the application
   - Check that the session is properly maintained

2. **Database errors**:
   - Ensure database tables are recreated after schema changes
   - Check database connection settings

3. **Notes not saving**:
   - Check browser console for JavaScript errors
   - Verify the API endpoint is accessible
   - Check server logs for backend errors

### Debug Mode

Enable debug mode in `settings.py` to see detailed error messages:

```python
DEBUG = True
```

## API Documentation

### Save Notes
- **URL**: `/api/save_notes`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Body**: `{"lesson_id": 1, "content": "notes content"}`
- **Response**: `{"success": true, "message": "Notes saved successfully"}`

### Get Notes
- **URL**: `/api/get_notes/<lesson_id>`
- **Method**: `GET`
- **Headers**: `Content-Type: application/json`
- **Response**: `{"success": true, "content": "notes content"}`

### Mark Lesson Complete
- **URL**: `/api/mark_lesson_complete`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Body**: `{"lesson_id": 1}`
- **Response**: `{"success": true, "message": "Lesson marked as complete", "new_percentage": 100}`

### Submit Question
- **URL**: `/api/submit_question`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Body**: `{"lesson_id": 1, "question": "user question"}`
- **Response**: `{"success": true, "message": "Question submitted successfully"}` 