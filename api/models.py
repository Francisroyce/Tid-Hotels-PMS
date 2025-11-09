# -*- coding: utf-8 -*-
"""
SQLAlchemy Models for Tide Hotels PMS
Defines all database tables and relationships
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


# Enums
class RoomStatusEnum(enum.Enum):
    VACANT = "Vacant"
    OCCUPIED = "Occupied"
    DIRTY = "Dirty"
    CLEANING = "Cleaning"
    OUT_OF_ORDER = "Out of Order"


class PaymentStatusEnum(enum.Enum):
    PAID = "Paid"
    PENDING = "Pending"
    OWING = "Owing"


class LoyaltyTierEnum(enum.Enum):
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"


class MaintenanceStatusEnum(enum.Enum):
    REPORTED = "Reported"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class MaintenancePriorityEnum(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class OrderStatusEnum(enum.Enum):
    PENDING = "Pending"
    PREPARING = "Preparing"
    READY = "Ready"
    DELIVERED = "Delivered"


class UserRoleEnum(enum.Enum):
    MANAGER = "Manager"
    FRONT_DESK = "Front Desk"
    HOUSEKEEPING = "Housekeeping"
    ACCOUNTS = "Accounts"
    RESTAURANT = "Restaurant"
    MAINTENANCE = "Maintenance"


# Models
class RoomType(Base):
    __tablename__ = 'room_types'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    rate_ngn = Column(Float, nullable=False)
    rate_usd = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    rooms = relationship("Room", back_populates="room_type", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'rates': {
                'NGN': self.rate_ngn,
                'USD': self.rate_usd
            },
            'capacity': self.capacity
        }


class Room(Base):
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String(20), unique=True, nullable=False)
    type = Column(String(100), ForeignKey('room_types.name'), nullable=False)
    rate = Column(Float, nullable=False)
    status = Column(SQLEnum(RoomStatusEnum), default=RoomStatusEnum.VACANT, nullable=False)
    guest_id = Column(Integer, ForeignKey('guests.id'), nullable=True)
    
    room_type = relationship("RoomType", back_populates="rooms")
    guest = relationship("Guest", back_populates="room", foreign_keys=[guest_id])
    orders = relationship("Order", back_populates="room")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="room")
    
    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'type': self.type,
            'rate': self.rate,
            'status': self.status.value,
            'guestId': self.guest_id
        }


class Guest(Base):
    __tablename__ = 'guests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=False)
    birthdate = Column(String(50))
    nationality = Column(String(100))
    id_type = Column(String(100), nullable=False)
    id_number = Column(String(100), nullable=False)
    id_other_type = Column(String(100))
    address = Column(Text)
    arrival_date = Column(String(50), nullable=False)
    departure_date = Column(String(50), nullable=False)
    adults = Column(Integer, nullable=False)
    children = Column(Integer, default=0)
    room_number = Column(String(20), nullable=False)
    room_type = Column(String(100), nullable=False)
    booking_source = Column(String(100), nullable=False)
    currency = Column(String(3), nullable=False)
    discount = Column(Float, default=0)
    special_requests = Column(Text)
    loyalty_points = Column(Integer, default=0)
    loyalty_tier = Column(SQLEnum(LoyaltyTierEnum), default=LoyaltyTierEnum.BRONZE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    room = relationship("Room", back_populates="guest", foreign_keys=[Room.guest_id])
    transactions = relationship("Transaction", back_populates="guest", cascade="all, delete-orphan")
    loyalty_transactions = relationship("LoyaltyTransaction", back_populates="guest", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'birthdate': self.birthdate,
            'nationality': self.nationality,
            'idType': self.id_type,
            'idNumber': self.id_number,
            'idOtherType': self.id_other_type,
            'address': self.address,
            'arrivalDate': self.arrival_date,
            'departureDate': self.departure_date,
            'adults': self.adults,
            'children': self.children,
            'roomNumber': self.room_number,
            'roomType': self.room_type,
            'bookingSource': self.booking_source,
            'currency': self.currency,
            'discount': self.discount,
            'specialRequests': self.special_requests,
            'loyaltyPoints': self.loyalty_points,
            'loyaltyTier': self.loyalty_tier.value
        }


class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guest_id = Column(Integer, ForeignKey('guests.id'), nullable=False)
    description = Column(String(500), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    guest = relationship("Guest", back_populates="transactions")
    
    def to_dict(self):
        return {
            'id': self.id,
            'guestId': self.guest_id,
            'description': self.description,
            'amount': self.amount,
            'date': self.date
        }


class LoyaltyTransaction(Base):
    __tablename__ = 'loyalty_transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guest_id = Column(Integer, ForeignKey('guests.id'), nullable=False)
    points = Column(Integer, nullable=False)
    description = Column(String(500), nullable=False)
    date = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    guest = relationship("Guest", back_populates="loyalty_transactions")
    
    def to_dict(self):
        return {
            'id': self.id,
            'guestId': self.guest_id,
            'points': self.points,
            'description': self.description,
            'date': self.date
        }


class WalkInTransaction(Base):
    __tablename__ = 'walk_in_transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    service = Column(String(200), nullable=False)
    service_details = Column(String(500))
    amount = Column(Float, nullable=False)
    discount = Column(Float, default=0)
    tax = Column(Float, default=0)
    amount_paid = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    currency = Column(String(3), nullable=False)
    date = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'service': self.service,
            'serviceDetails': self.service_details,
            'amount': self.amount,
            'discount': self.discount,
            'tax': self.tax,
            'amountPaid': self.amount_paid,
            'paymentMethod': self.payment_method,
            'currency': self.currency,
            'date': self.date
        }


class Reservation(Base):
    __tablename__ = 'reservations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guest_name = Column(String(200), nullable=False)
    guest_email = Column(String(200), nullable=False)
    guest_phone = Column(String(50), nullable=False)
    check_in_date = Column(String(50), nullable=False)
    check_out_date = Column(String(50), nullable=False)
    room_type = Column(String(100), nullable=False)
    ota = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'guestName': self.guest_name,
            'guestEmail': self.guest_email,
            'guestPhone': self.guest_phone,
            'checkInDate': self.check_in_date,
            'checkOutDate': self.check_out_date,
            'roomType': self.room_type,
            'ota': self.ota
        }


class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    items = Column(Text, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(SQLEnum(OrderStatusEnum), default=OrderStatusEnum.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    room = relationship("Room", back_populates="orders")
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'roomId': self.room_id,
            'items': json.loads(self.items),
            'total': self.total,
            'status': self.status.value,
            'createdAt': self.created_at.isoformat()
        }


class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    department = Column(String(100), nullable=False)
    job_title = Column(String(100), nullable=False)
    salary = Column(Float, nullable=False)
    hire_date = Column(String(50), nullable=False)
    email = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=False)
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(50))
    profile_picture = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'department': self.department,
            'jobTitle': self.job_title,
            'salary': self.salary,
            'hireDate': self.hire_date,
            'email': self.email,
            'phone': self.phone,
            'emergencyContactName': self.emergency_contact_name,
            'emergencyContactPhone': self.emergency_contact_phone,
            'profilePicture': self.profile_picture
        }


class MaintenanceRequest(Base):
    __tablename__ = 'maintenance_requests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=True)
    location = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    reported_at = Column(String(50), nullable=False)
    status = Column(SQLEnum(MaintenanceStatusEnum), default=MaintenanceStatusEnum.REPORTED, nullable=False)
    priority = Column(SQLEnum(MaintenancePriorityEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    room = relationship("Room", back_populates="maintenance_requests")
    
    def to_dict(self):
        return {
            'id': self.id,
            'roomId': self.room_id,
            'location': self.location,
            'description': self.description,
            'reportedAt': self.reported_at,
            'status': self.status.value,
            'priority': self.priority.value
        }


class Settings(Base):
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        import json
        return {
            'key': self.key,
            'value': json.loads(self.value)
        }


class SyncLog(Base):
    __tablename__ = 'sync_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    level = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'message': self.message,
            'level': self.level
        }