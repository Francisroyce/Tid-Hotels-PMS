"""
Flask Backend Server for Tidé Hotels PMS
Provides REST API endpoints and WebSocket real-time updates
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from sqlalchemy.orm import Session
from datetime import datetime
import json

from database import engine, init_db, db_session
from models import (
    Room, Guest, Reservation, Transaction, LoyaltyTransaction, WalkInTransaction,
    Order, Employee, MaintenanceRequest, RoomType, Settings, SyncLog,
    RoomStatusEnum, MaintenanceStatusEnum, LoyaltyTierEnum
)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tide-hotels-secret-key-change-in-production'
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO
# Using 'threading' mode to be compatible with Python 3.13
# For production with high concurrency, you can switch to 'eventlet' or 'gevent' on Python <=3.12
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize database
init_db()

# Helper function to broadcast data updates
def broadcast_data_update():
    """Send complete data state to all connected clients"""
    data = get_all_data()
    socketio.emit('data_update', data, broadcast=True)

def get_all_data():
    """Retrieve all data from database"""
    try:
        tax_setting = db_session.query(Settings).filter_by(key='tax_settings').first()
        tax_settings = json.loads(tax_setting.value) if tax_setting else {'isEnabled': True, 'rate': 7.5}

        stop_sell_setting = db_session.query(Settings).filter_by(key='stop_sell').first()
        stop_sell = json.loads(stop_sell_setting.value) if stop_sell_setting else {}

        return {
            'roomTypes': [rt.to_dict() for rt in db_session.query(RoomType).all()],
            'rooms': [r.to_dict() for r in db_session.query(Room).all()],
            'guests': [g.to_dict() for g in db_session.query(Guest).all()],
            'reservations': [r.to_dict() for r in db_session.query(Reservation).all()],
            'transactions': [t.to_dict() for t in db_session.query(Transaction).all()],
            'loyaltyTransactions': [lt.to_dict() for lt in db_session.query(LoyaltyTransaction).all()],
            'walkInTransactions': [wt.to_dict() for wt in db_session.query(WalkInTransaction).all()],
            'orders': [o.to_dict() for o in db_session.query(Order).all()],
            'employees': [e.to_dict() for e in db_session.query(Employee).all()],
            'maintenanceRequests': [mr.to_dict() for mr in db_session.query(MaintenanceRequest).all()],
            'syncLog': [sl.to_dict() for sl in db_session.query(SyncLog).order_by(SyncLog.id.desc()).limit(50).all()],
            'taxSettings': tax_settings,
            'stopSell': stop_sell
        }
    except Exception as e:
        print(f"Error getting all data: {e}")
        return {}

# ============= REST API ENDPOINTS =============
# ... Keep all your existing REST API routes unchanged ...

# ============= WEBSOCKET EVENTS =============

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('data_update', get_all_data())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

# ============= RUN SERVER =============

if __name__ == '__main__':
    print("Starting Tidé Hotels PMS Backend Server...")
    print("Server running on http://localhost:5001")
    # Using 'threading' mode, compatible with Python 3.13
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
