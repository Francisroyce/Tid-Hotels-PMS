# ==================== IMPORTS ====================
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime
import json
import os
from typing import Dict, Any, List

# ==================== APP SETUP ====================
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Use 'threading' async mode for Python 3.13 compatibility
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ==================== DATA STORAGE ====================
DATA_FILE = 'hotel_data.json'

INITIAL_DATA = {
    'rooms': [],
    'guests': [],
    'reservations': [],
    'transactions': [],
    'loyaltyTransactions': [],
    'walkInTransactions': [],
    'orders': [],
    'employees': [],
    'syncLog': [],
    'maintenanceRequests': [],
    'roomTypes': [],
    'taxSettings': {'isEnabled': True, 'rate': 7.5},
    'stopSell': {}
}

hotel_data = INITIAL_DATA.copy()

id_counters = {
    'rooms': 1,
    'guests': 1,
    'reservations': 1,
    'transactions': 1,
    'loyaltyTransactions': 1,
    'walkInTransactions': 1,
    'orders': 1,
    'employees': 1,
    'maintenanceRequests': 1,
    'roomTypes': 1
}

# ==================== DATA FUNCTIONS ====================

def load_data():
    """Load data from file if it exists"""
    global hotel_data, id_counters
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                loaded_data = json.load(f)
                hotel_data = loaded_data.get('data', INITIAL_DATA.copy())
                id_counters = loaded_data.get('counters', id_counters.copy())
        except Exception as e:
            print(f"Error loading data: {e}")
            hotel_data = INITIAL_DATA.copy()

def save_data():
    """Save data to file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump({
                'data': hotel_data,
                'counters': id_counters
            }, f, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")

def broadcast_update():
    """Broadcast data update to all connected clients"""
    socketio.emit('data_update', hotel_data, broadcast=True)
    save_data()

def add_sync_log(message: str, level: str = 'info'):
    """Add entry to sync log"""
    log_entry = {
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'message': message,
        'level': level
    }
    hotel_data['syncLog'].insert(0, log_entry)
    if len(hotel_data['syncLog']) > 100:
        hotel_data['syncLog'] = hotel_data['syncLog'][:100]

def get_next_id(entity: str) -> int:
    """Get next ID for an entity"""
    current_id = id_counters[entity]
    id_counters[entity] += 1
    return current_id

# Initialize data on startup
load_data()

# ==================== API ROUTES ====================

@app.route('/api/data', methods=['GET'])
def get_data():
    """Get all hotel data"""
    return jsonify(hotel_data)

@app.route('/api/data/clear', methods=['POST'])
def clear_data():
    """Clear all data (except room types and settings)"""
    global hotel_data
    hotel_data = {
        'rooms': [],
        'guests': [],
        'reservations': [],
        'transactions': [],
        'loyaltyTransactions': [],
        'walkInTransactions': [],
        'orders': [],
        'employees': [],
        'syncLog': [],
        'maintenanceRequests': [],
        'roomTypes': hotel_data.get('roomTypes', []),
        'taxSettings': hotel_data.get('taxSettings', {'isEnabled': True, 'rate': 7.5}),
        'stopSell': {}
    }
    add_sync_log('All data cleared', 'warn')
    broadcast_update()
    return jsonify({'success': True}), 200

# ==================== SOCKET.IO HANDLERS ====================

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('data_update', hotel_data)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# ==================== MAIN ENTRY ====================

if __name__ == '__main__':
    print("✅ Tid Hotels PMS API running on http://127.0.0.1:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
