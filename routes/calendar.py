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


def sync_push_route():
    print("SYNC PUSH: Endpoint hit")
    user = session.get('user', None)
    if not user:
        print("SYNC PUSH: User not authenticated")
        return jsonify({'error': 'User not authenticated'}), 401
    from models.user import User, CalendarEvent
    user_obj = User.find_by_sub(user['sub'])
    print(f"SYNC PUSH: user_obj={user_obj}")
    if not user_obj or not user_obj.google_calendar_id:
        print("SYNC PUSH: Google Calendar not set up for this user.")
        return jsonify({'error': 'Google Calendar not set up for this user.'}), 400

    from lib.apis.google_agenda import calendar_service
    service = calendar_service()
    calendar_id = user_obj.google_calendar_id

    events = CalendarEvent.query.filter_by(user_id=user_obj.id).all()
    print(f"SYNC PUSH: Found {len(events)} events to push")
    pushed, updated = 0, 0
    for event in events:
        print(f"SYNC PUSH: Processing event {event.id} - {event.title}")
        body = {
            'summary': event.title,
            'description': event.description or '',
            'start': {'dateTime': event.start_datetime.isoformat(), 'timeZone': 'UTC'},
            'end': {'dateTime': event.end_datetime.isoformat() if event.end_datetime else event.start_datetime.isoformat(), 'timeZone': 'UTC'},
            'location': event.location or '',
        }
        try:
            if event.google_event_id:
                print(f"SYNC PUSH: Updating Google event {event.google_event_id}")
                service.events().update(calendarId=calendar_id, eventId=event.google_event_id, body=body).execute()
                updated += 1
            else:
                print("SYNC PUSH: Creating new Google event")
                created = service.events().insert(calendarId=calendar_id, body=body).execute()
                event.google_event_id = created['id']
                db.session.commit()
                pushed += 1
        except Exception as e:
            print(f'Error syncing event {event.title}: {e}')
    print(f"SYNC PUSH: Done. {pushed} created, {updated} updated.")
    return jsonify({'message': f'Push complete: {pushed} created, {updated} updated.'}), 200


def sync_pull_route():
    print("SYNC PULL: Endpoint hit")
    user = session.get('user', None)
    if not user:
        print("SYNC PULL: User not authenticated")
        return jsonify({'error': 'User not authenticated'}), 401
    from models.user import User, CalendarEvent
    user_obj = User.find_by_sub(user['sub'])
    print(f"SYNC PULL: user_obj={user_obj}")
    if not user_obj or not user_obj.google_calendar_id:
        print("SYNC PULL: Google Calendar not set up for this user.")
        return jsonify({'error': 'Google Calendar not set up for this user.'}), 400

    from lib.apis.google_agenda import calendar_service
    service = calendar_service()
    calendar_id = user_obj.google_calendar_id

    events_result = service.events().list(calendarId=calendar_id, singleEvents=True).execute()
    google_events = events_result.get('items', [])
    print(f"SYNC PULL: Found {len(google_events)} Google events to pull")
    pulled, updated = 0, 0
    for g_event in google_events:
        if g_event.get('status') == 'cancelled':
            continue
        g_id = g_event['id']
        app_event = CalendarEvent.query.filter_by(user_id=user_obj.id, google_event_id=g_id).first()
        start = g_event['start'].get('dateTime') or g_event['start'].get('date')
        end = g_event['end'].get('dateTime') or g_event['end'].get('date')
        start_dt = dtparse(start)
        end_dt = dtparse(end) if end else None
        if app_event:
            app_event.title = g_event.get('summary', '')
            app_event.description = g_event.get('description', '')
            app_event.start_datetime = start_dt
            app_event.end_datetime = end_dt
            app_event.location = g_event.get('location', '')
            updated += 1
        else:
            new_event = CalendarEvent(
                user_id=user_obj.id,
                title=g_event.get('summary', ''),
                description=g_event.get('description', ''),
                start_datetime=start_dt,
                end_datetime=end_dt,
                location=g_event.get('location', ''),
                event_type='study_session',
                google_event_id=g_id
            )
            db.session.add(new_event)
            pulled += 1
    db.session.commit()
    print(f"SYNC PULL: Done. {pulled} created, {updated} updated.")
    return jsonify({'message': f'Pull complete: {pulled} created, {updated} updated.'}), 200


def sync_twoway_route():
    print("SYNC TWO-WAY: Endpoint hit")
    user = session.get('user', None)
    if not user:
        print("SYNC TWO-WAY: User not authenticated")
        return jsonify({'error': 'User not authenticated'}), 401
    from models.user import User, CalendarEvent
    user_obj = User.find_by_sub(user['sub'])
    print(f"SYNC TWO-WAY: user_obj={user_obj}")
    if not user_obj or not user_obj.google_calendar_id:
        print("SYNC TWO-WAY: Google Calendar not set up for this user.")
        return jsonify({'error': 'Google Calendar not set up for this user.'}), 400

    # --- Pull ---
    from lib.apis.google_agenda import calendar_service
    service = calendar_service()
    calendar_id = user_obj.google_calendar_id
    events_result = service.events().list(calendarId=calendar_id, singleEvents=True).execute()
    google_events = events_result.get('items', [])
    print(f"SYNC TWO-WAY: Found {len(google_events)} Google events to pull")
    pulled, updated_pull = 0, 0
    from dateutil.parser import parse as dtparse
    for g_event in google_events:
        if g_event.get('status') == 'cancelled':
            continue
        g_id = g_event['id']
        app_event = CalendarEvent.query.filter_by(user_id=user_obj.id, google_event_id=g_id).first()
        start = g_event['start'].get('dateTime') or g_event['start'].get('date')
        end = g_event['end'].get('dateTime') or g_event['end'].get('date')
        start_dt = dtparse(start)
        end_dt = dtparse(end) if end else None
        if app_event:
            app_event.title = g_event.get('summary', '')
            app_event.description = g_event.get('description', '')
            app_event.start_datetime = start_dt
            app_event.end_datetime = end_dt
            app_event.location = g_event.get('location', '')
            updated_pull += 1
        else:
            new_event = CalendarEvent(
                user_id=user_obj.id,
                title=g_event.get('summary', ''),
                description=g_event.get('description', ''),
                start_datetime=start_dt,
                end_datetime=end_dt,
                location=g_event.get('location', ''),
                event_type='study_session',
                google_event_id=g_id
            )
            db.session.add(new_event)
            pulled += 1
    db.session.commit()

    # --- Push ---
    events = CalendarEvent.query.filter_by(user_id=user_obj.id).all()
    print(f"SYNC TWO-WAY: Found {len(events)} app events to push")
    pushed, updated_push = 0, 0
    for event in events:
        body = {
            'summary': event.title,
            'description': event.description or '',
            'start': {'dateTime': event.start_datetime.isoformat(), 'timeZone': 'UTC'},
            'end': {'dateTime': event.end_datetime.isoformat() if event.end_datetime else event.start_datetime.isoformat(), 'timeZone': 'UTC'},
            'location': event.location or '',
        }
        try:
            if event.google_event_id:
                service.events().update(calendarId=calendar_id, eventId=event.google_event_id, body=body).execute()
                updated_push += 1
            else:
                created = service.events().insert(calendarId=calendar_id, body=body).execute()
                event.google_event_id = created['id']
                db.session.commit()
                pushed += 1
        except Exception as e:
            print(f'Error syncing event {event.title}: {e}')
    print(f"SYNC TWO-WAY: Done. {pulled} pulled, {updated_pull} updated from Google; {pushed} pushed, {updated_push} updated to Google.")
    return jsonify({'message': f'Two-way sync complete: {pulled} pulled, {updated_pull} updated from Google; {pushed} pushed, {updated_push} updated to Google.'}), 200
