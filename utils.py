import sqlite3
from datetime import datetime

from datetimerange import DateTimeRange


def connect_to_db():
    conn = sqlite3.connect('database.db')
    return conn


def get_events():
    events = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM events")
        rows = cur.fetchall()
        for row in rows:
            event = {
                'id': row['id'],
                'title': row['title'],
                'event_date': row['event_date'],
                'start_time': row['start_time'],
                'end_time': row['end_time']
            }
            events.append(event)
    except Exception as err:
        print('=================')
        print(err)
        print('=================')
        events = []
    return events


def get_event_by_id(event_id):
    event = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        row = cur.fetchone()
        event['id'] = row['id']
        event['title'] = row['title']
        event['event_date'] = row['event_date']
        event['start_time'] = row['start_time']
        event['end_time'] = row['end_time']
    except Exception as err:
        print('=================')
        print(err)
        print('=================')
        event = {}
    return event


def create_event(event):
    created_event = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO events (title, event_date, start_time, end_time) VALUES (?, ?, ?, ?)",
            (
                event['title'],
                event['event_date'],
                event['start_time'],
                event['end_time']
            )
        )
        conn.commit()
        created_event = get_event_by_id(cur.lastrowid)
    except Exception as err:
        print('=================')
        print(err)
        print('=================')
        conn().rollback()
    finally:
        conn.close()
    return created_event


def update_event(event):
    updated_event = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            'UPDATE events SET title = ?, event_date = ?, start_time = ?, end_time = ? WHERE id =?',
            (
                event['title'],
                event['event_date'],
                event['start_time'],
                event['end_time'],
                event['id']
            )
        )
        conn.commit()
        updated_event = get_event_by_id(event['id'])
    except Exception as err:
        print('=================')
        print(err)
        print('=================')
        conn.rollback()
        updated_event = {}
    finally:
        conn.close()
    return updated_event


def delete_event(event_id):
    message = {}
    try:
        conn = connect_to_db()
        conn.execute("DELETE from events WHERE id = ?", (event_id,))
        conn.commit()
        message["status"] = "Event deleted successfully"
    except Exception as err:
        print('=================')
        print(err)
        print('=================')
        conn.rollback()
        message["status"] = "Cannot delete event"
    finally:
        conn.close()
    return message


def has_overlapping_time(event_date, start_time, end_time, event_id=None):
    events = get_events()
    timerange_1 = DateTimeRange(f'{event_date} {start_time}', f'{event_date} {end_time}')
    for event in events:
        if event['id'] == event_id:
            continue
        timerange_2 = DateTimeRange(
            f'{event["event_date"]} {event["start_time"]}', f'{event["event_date"]} {event["end_time"]}'
        )
        if timerange_1.is_intersection(timerange_2):
            return True
    return False


def is_outside_event_hours(start_time, end_time):
    time_1 = datetime.strptime(start_time, "%I:%M %p")
    time_2 = datetime.strptime(end_time, "%I:%M %p")
    upper_limit = datetime.strptime('8:00 AM', "%I:%M %p")
    lower_limit = datetime.strptime('8:00 PM', "%I:%M %p")
    if time_1 < upper_limit or time_2 > lower_limit:
        return True
    return False


def is_in_the_past(event_date, start_time, end_time):
    datetime_1 = datetime.strptime(f'{event_date} {start_time}', "%Y-%m-%d %I:%M %p")
    datetime_2 = datetime.strptime(f'{event_date} {end_time}', "%Y-%m-%d %I:%M %p")
    if datetime_1 <= datetime.now() or datetime_2 <= datetime.now():
        return True
    return False


def validate_schedule(event_date, start_time, end_time, event_id=None):
    if has_overlapping_time(event_date, start_time, end_time, event_id):
        return {'error': 'Overlapping time'}, 400
    if is_outside_event_hours(start_time, end_time):
        return {'error': 'Is outside 8AM - 8PM'}, 400
    if is_in_the_past(event_date, start_time, end_time):
        return {'error': 'Is in the past'}, 400
    return None


def invalid_keys(request_obj):
    if 'title' not in request_obj:
        return True
    if 'event_date' not in request_obj:
        return True
    if 'start_time' not in request_obj:
        return True
    if 'end_time' not in request_obj:
        return True
    return False


def invalid_date_format(event_date):
    try:
        datetime.strptime(f'{event_date} 8:00 AM', "%Y-%m-%d %I:%M %p")
    except Exception as err:
        print('=================')
        print(err)
        print('=================')
        return True
    return False


def invalid_time_format(start_time, end_time):
    try:
        datetime.strptime(start_time, "%I:%M %p")
        datetime.strptime(end_time, "%I:%M %p")
    except Exception as err:
        print('=================')
        print(err)
        print('=================')
        return True
    return False


def validate_request(request_obj):
    if invalid_keys(request_obj):
        return {'error': 'Missing fields in request'}, 400
    if invalid_date_format(request_obj['event_date']):
        return {'error': 'Invalid date format must be YYYY-MM-DD'}, 400
    if invalid_time_format(request_obj['start_time'], request_obj['end_time']):
        return {'error': 'Invalid time format must be 08:00 AM'}, 400
    return None
