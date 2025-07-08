from flask import render_template, request, jsonify, current_app, session
from datetime import datetime
import json
from models.user import CalendarEvent, User
from database import db

# CALENDAR ROUTES #

#@login_required
def calendar_view():
    """Render the calendar page"""
    return render_template('calendar.html')

#@login_required
def get_events():
    user = session.get('user', None)
    if not user:
        return jsonify({'error': 'User not authenticated'}), 401

    user_sub = session['user']['sub']
    print('user_sub from session:', user_sub)
    current_user = User.find_by_sub(user_sub)
    print('current_user from database:', current_user)
    
    if not current_user:
        print('User not found in database. Creating user...')
        # Create user if it doesn't exist
        current_user = User.create_or_update(
            email=session['user']['email'],
            name=session['user']['name'],
            sub=user_sub
        )
        print('Created/found user:', current_user)

    """Get events for the current user in FullCalendar format"""
    try:
        # Get query parameters for filtering
        start = request.args.get('start')
        end = request.args.get('end')
        event_type = request.args.get('event_type')
        
        # Convert date strings to datetime objects if provided
        start_date = None
        end_date = None
        if start:
            start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
        if end:
            end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
        
        # Get events for the current user
        try:
            print('current_user', current_user)
            events = CalendarEvent.get_user_events(
                user_id=current_user.id,
                start_date=start_date,
                end_date=end_date,
                event_type=event_type
            )

            # Convert to FullCalendar format
            calendar_events = [event.to_fullcalendar_format() for event in events]

            return jsonify(calendar_events)
        except ValueError as ve:
            current_app.logger.error(f"Value error fetching events: {str(ve)}")
            return jsonify({'error': f'Invalid date format: {str(ve)}'}), 400
        except Exception as e:
            current_app.logger.error(f"Error fetching events [CalendarEvent.get_user_events()]: {str(e)}")
            return jsonify({'error': 'Failed to fetch events'}), 500
    
    except Exception as e:
        current_app.logger.error(f"Error fetching events: {str(e)}")
        return jsonify({'error': 'Failed to fetch events'}), 500

#@login_required
def create_event():
    """Create a new calendar event"""
    try:
        user = session.get('user', None)

        if not user:
            return jsonify({'error': 'User not authenticated'}), 401

        user_sub = session['user']['sub']
        current_user = User.find_by_sub(user_sub)
        
        if not current_user:
            # Create user if it doesn't exist
            current_user = User.create_or_update(
                email=session['user']['email'],
                name=session['user']['name'],
                sub=user_sub
            )

        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'event_type', 'start_datetime']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse datetime strings
        start_datetime = datetime.fromisoformat(data['start_datetime'].replace('Z', '+00:00'))
        end_datetime = None
        if data.get('end_datetime'):
            end_datetime = datetime.fromisoformat(data['end_datetime'].replace('Z', '+00:00'))
        
        # Validate event type
        valid_event_types = ['lecture', 'exam', 'study_session', 'one_on_one']
        if data['event_type'] not in valid_event_types:
            return jsonify({'error': f'Invalid event type. Must be one of: {", ".join(valid_event_types)}'}), 400
        
        # Create the event
        event = CalendarEvent.create_event(
            user_id=current_user.id,
            title=data['title'],
            description=data.get('description'),
            event_type=data['event_type'],
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location=data.get('location'),
            participants=json.dumps(data.get('participants', [])) if data.get('participants') else None
        )
        
        return jsonify(event.to_fullcalendar_format()), 201
    
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating event: {str(e)}")
        return jsonify({'error': 'Failed to create event'}), 500

#@login_required
def update_event(event_id):
    """Update an existing calendar event"""
    try:
        user = session.get('user', None)

        if not user:
            return jsonify({'error': 'User not authenticated'}), 401

        user_sub = session['user']['sub']
        current_user = User.find_by_sub(user_sub)
        
        if not current_user:
            # Create user if it doesn't exist
            current_user = User.create_or_update(
                email=session['user']['email'],
                name=session['user']['name'],
                sub=user_sub
            )

        event = CalendarEvent.query.filter_by(id=event_id, user_id=current_user.id).first()
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'event_type' in data:
            valid_event_types = ['lecture', 'exam', 'study_session', 'one_on_one']
            if data['event_type'] not in valid_event_types:
                return jsonify({'error': f'Invalid event type. Must be one of: {", ".join(valid_event_types)}'}), 400
            event.event_type = data['event_type']
        if 'location' in data:
            event.location = data['location']
        if 'start_datetime' in data:
            event.start_datetime = datetime.fromisoformat(data['start_datetime'].replace('Z', '+00:00'))
        if 'end_datetime' in data:
            if data['end_datetime']:
                event.end_datetime = datetime.fromisoformat(data['end_datetime'].replace('Z', '+00:00'))
            else:
                event.end_datetime = None
        if 'participants' in data:
            event.participants = json.dumps(data['participants']) if data['participants'] else None
        
        event.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(event.to_fullcalendar_format())
    
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating event: {str(e)}")
        return jsonify({'error': 'Failed to update event'}), 500

#@login_required
def delete_event(event_id):
    """Delete a calendar event"""
    try:
        user = session.get('user', None)

        if not user:
            return jsonify({'error': 'User not authenticated'}), 401

        user_sub = session['user']['sub']
        current_user = User.find_by_sub(user_sub)
        
        if not current_user:
            # Create user if it doesn't exist
            current_user = User.create_or_update(
                email=session['user']['email'],
                name=session['user']['name'],
                sub=user_sub
            )

        event = CalendarEvent.query.filter_by(id=event_id, user_id=current_user.id).first()
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({'message': 'Event deleted successfully'})
    
    except Exception as e:
        current_app.logger.error(f"Error deleting event: {str(e)}")
        return jsonify({'error': 'Failed to delete event'}), 500

#@login_required
def get_event_types():
    """Get available event types"""
    return jsonify({
        'event_types': [
            {'value': 'lecture', 'label': 'Lecture'},
            {'value': 'exam', 'label': 'Exam'},
            {'value': 'study_session', 'label': 'Study Session'},
            {'value': 'one_on_one', 'label': 'One-on-One'}
        ]
    })
