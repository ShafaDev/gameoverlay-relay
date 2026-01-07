"""
GameOverlay Relay Server
Deploy to Railway for free hosting!
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gameoverlay-secret-key-2024')
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

# Store active rooms
rooms = {}

@app.route('/')
def index():
    return jsonify({
        'status': 'GameOverlay Relay Server Running!',
        'active_rooms': len(rooms),
        'version': '1.0'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@socketio.on('connect')
def handle_connect():
    print(f'[SERVER] Client connected: {request.sid}')
    emit('connected', {'status': 'Connected to relay server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'[SERVER] Client disconnected: {request.sid}')
    # Remove from all rooms
    for room_code in list(rooms.keys()):
        if request.sid in rooms[room_code]:
            username = rooms[room_code][request.sid]
            del rooms[room_code][request.sid]
            emit('user_left', {'username': username}, room=room_code, skip_sid=request.sid)
            if not rooms[room_code]:
                del rooms[room_code]
                print(f'[SERVER] Room {room_code} deleted (empty)')

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
    rooms[room_code][request.sid] = username
    join_room(room_code)
    
    print(f'[SERVER] {username} joined room {room_code}')
    
    # Notify user they joined
    emit('joined_room', {
        'room_code': room_code,
        'username': username,
        'users_count': len(rooms[room_code])
    })
    
    # Notify others in room
    emit('user_joined', {'username': username}, room=room_code, skip_sid=request.sid)

@socketio.on('send_message')
def handle_send_message(data):
    room_code = data.get('room_code', '').upper()
    message = data.get('message', '')
    username = data.get('username', 'Anonymous')
    
    if room_code not in rooms or request.sid not in rooms[room_code]:
        emit('error', {'message': 'Not in room'})
        return
    
    print(f'[SERVER] {username} in {room_code}: {message}')
    
    # Send to all others in room
    emit('receive_message', {
        'username': username,
        'message': message
    }, room=room_code, skip_sid=request.sid)

@socketio.on('leave_room')
def handle_leave_room(data):
    room_code = data.get('room_code', '').upper()
    
    if room_code in rooms and request.sid in rooms[room_code]:
        username = rooms[room_code][request.sid]
        del rooms[room_code][request.sid]
        leave_room(room_code)
        
        print(f'[SERVER] {username} left room {room_code}')
        
        # Notify others
        emit('user_left', {'username': username}, room=room_code)
        
        # Delete room if empty
        if not rooms[room_code]:
            del rooms[room_code]
            print(f'[SERVER] Room {room_code} deleted (empty)')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
