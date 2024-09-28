from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from depth import get_pen_state, start_depth_sensor
import time
import random
import threading

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

def get_position():
    # This function will return a simulated mouse position (you can replace it with actual logic)
    return random.randint(5, 1550), random.randint(5, 710)  # Simulating x, y positions

# Emit pen state and mouse position to the client every second
@socketio.on('connect')
def handle_connect():
    print('Client connected')

    def emit_data():
        while True:
            # Simulate distance data (you will replace this with actual data)
            pen_state = get_pen_state()
            #print(f'Emitting pen state: {pen_state}')

            # Emit the pen state to the frontend
            socketio.emit('pen_state', {'state': pen_state})

            # Get and emit mouse position
            x, y = get_position()  # Simulating the mouse position
            #print(f'Emitting mouse position: {x}, {y}')
            socketio.emit('mouse_position', {'x': x, 'y': y})

            time.sleep(0.1)  # Emit every second

    socketio.start_background_task(emit_data)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == "__main__":
    threading.Thread(target=start_depth_sensor).start()
    socketio.run(app, debug=False, host='0.0.0.0', port=9631, allow_unsafe_werkzeug=True)
