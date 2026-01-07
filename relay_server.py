"""
GameOverlay Relay Server - RENDER VERSION
With keep-alive - never sleeps!
Free forever, no credit card!
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os
import threading
import time
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gameoverlay-secret-2024')
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

# Store active rooms
rooms = {}

# Keep-alive functionality
def keep_alive():
    """Ping server every 10 minutes to prevent Render sleep"""
    while True:
        try:
            time.sleep(600)  # 10 minutes
            # Get the Render URL from environment or use localhost for local testing
            url = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:5000')
            if url and url != 'http://localhost:5000':
                try:
                    requests.get(f"{url}/health", timeout=5)
                    print("[KEEP-ALIVE] Pinged server successfully")
                except Exception as e:
                    print(f"[KEEP-ALIVE] Ping failed: {e}")
        except Exception as e:
            print(f"[KEEP-ALIVE] Error: {e}")

# Start keep-alive in background
keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
keep_alive_thread.start()

@app.route('/')
def index():
    return jsonify({
        'status': 'GameOverlay Relay Server Running!',
        'platform': 'Render',
        'active_rooms': len(rooms),
        'version': '1.0',
        'free': 'Forever! No credit card needed!'
    })

@app.route('/health')
def health():
    """Health check endpoint for keep-alive"""
    return jsonify({
        'status': 'ok',
        'active_rooms': len(rooms),
        'uptime': 'always'
    })

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
    print("\n" + "="*50)
    print("GameOverlay Relay Server - RENDER")
    print("="*50)
    print(f"Starting on port {port}")
    print("Keep-alive enabled - never sleeps!")
    print("Free forever - no credit card!")
    print("="*50 + "\n")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
