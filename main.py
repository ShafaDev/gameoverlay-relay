"""
GameOverlay Relay Server - REPLIT VERSION
Free forever! No credit card needed!
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gameoverlay-replit-2024'
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

# Store active rooms
rooms = {}

@app.route('/')
def index():
    """Main endpoint - health check"""
    return jsonify({
        'status': 'GameOverlay Relay Server Running!',
        'platform': 'Replit',
        'active_rooms': len(rooms),
        'version': '1.0',
        'free': 'Forever! No credit card needed!'
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'active_rooms': len(rooms)})

@socketio.on('connect')
def handle_connect():
    print(f'[SERVER] Client connected: {request.sid}')
    emit('connected', {'status': 'Connected to relay server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'[SERVER] Client disconnected: {request.sid}')
    for room_code in list(rooms.keys()):
        if request.sid in rooms[room_code]:
            username = rooms[room_code][request.sid]
            del rooms[room_code][request.sid]
            emit('user_left', {'username': username}, room=room_code, skip_sid=request.sid)
            if not rooms[room_code]:
                del rooms[room_code]

@socketio.on('join_room')
def handle_join_room(data):
    room_code = data.get('room_code', '').upper()
    username = data.get('username', 'Anonymous')
    
    if not room_code:
        emit('error', {'message': 'Room code required'})
        return
    
    if room_code not in rooms:
        rooms[room_code] = {}
    
    rooms[room_code][request.sid] = username
    join_room(room_code)
    
    print(f'[SERVER] {username} joined room {room_code}')
    
    emit('joined_room', {
        'room_code': room_code,
        'username': username,
        'users_count': len(rooms[room_code])
    })
    
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
        
        emit('user_left', {'username': username}, room=room_code)
        
        if not rooms[room_code]:
            del rooms[room_code]

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*50)
    print("GameOverlay Relay Server - REPLIT")
    print("="*50)
    print(f"Starting on port {port}")
    print("Free forever - no credit card!")
    print("="*50 + "\n")
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
