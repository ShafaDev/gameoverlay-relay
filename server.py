"""
GameOverlay Server - Fly.io Compatible
Flask-SocketIO server with rooms support
"""

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gameoverlay-secret-key-change-this')

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO with CORS support
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)

# Store active rooms and users
rooms = {}  # {room_code: {username: sid}}

@app.route('/')
def index():
    return {
        'status': 'running',
        'service': 'GameOverlay Server',
        'version': '1.0',
        'active_rooms': len(rooms)
    }

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    
    # Remove user from all rooms
    sid = request.sid
    for room_code in list(rooms.keys()):
        users_to_remove = []
        for username, user_sid in rooms[room_code].items():
            if user_sid == sid:
                users_to_remove.append(username)
        
        for username in users_to_remove:
            del rooms[room_code][username]
            emit('user_left', {
                'username': username,
                'users_count': len(rooms[room_code])
            }, room=room_code)
        
        # Clean up empty rooms
        if not rooms[room_code]:
            del rooms[room_code]

@socketio.on('join_room')
def handle_join_room(data):
    room_code = data.get('room_code', '').upper()
    username = data.get('username', 'Anonymous')
    
    if not room_code:
        emit('error', {'message': 'Room code required'})
        return
    
    # Create room if doesn't exist
    if room_code not in rooms:
        rooms[room_code] = {}
    
    # Add user to room
    rooms[room_code][username] = request.sid
    join_room(room_code)
    
    print(f'{username} joined room {room_code}')
    
    # Notify user they joined
    emit('joined_room', {
        'room_code': room_code,
        'username': username,
        'users_count': len(rooms[room_code])
    })
    
    # Notify others in room
    emit('user_joined', {
        'username': username,
        'users_count': len(rooms[room_code])
    }, room=room_code, skip_sid=request.sid)

@socketio.on('send_message')
def handle_send_message(data):
    room_code = data.get('room_code', '').upper()
    username = data.get('username', 'Anonymous')
    message = data.get('message', '')
    
    if not room_code or not message:
        return
    
    if room_code not in rooms:
        emit('error', {'message': 'Room not found'})
        return
    
    print(f'{username} in {room_code}: {message}')
    
    # Broadcast message to all in room except sender
    emit('receive_message', {
        'username': username,
        'message': message
    }, room=room_code, skip_sid=request.sid)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    
    print('=' * 60)
    print('GameOverlay Server Starting')
    print(f'Port: {port}')
    print('=' * 60)
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )
