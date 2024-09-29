from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from depth import get_pen_state, start_depth_sensor
from test import get_position_change, start_vision
import time
import random
import threading

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Emit pen state and mouse position to the client every second
@socketio.on('connect')
def handle_connect():
    print('Client connected')

    def emit_data():
        x = 750
        y = 350
        while True:
            print("looping now")
            # Simulate distance data (you will replace this with actual data)
            pen_state = get_pen_state()
            print(f'Emitting pen state: {pen_state}')

            # Emit the pen state to the frontend
            socketio.emit('pen_state', {'state': pen_state})

            # Get and emit mouse position
            [dx, dy] = get_position_change()
            x -= dx
            y -= dy
            print(f'Emitting mouse position: {x}, {y}')
            socketio.emit('mouse_position', {'x': int(x), 'y': int(y)})

            time.sleep(0.2)  # Emit every second

    socketio.start_background_task(emit_data)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == "__main__":
    threading.Thread(target=start_depth_sensor).start()
    threading.Thread(target=start_vision).start()
    socketio.run(app, debug=False, host='0.0.0.0', port=9631, allow_unsafe_werkzeug=True)
