"""
SQLAlchemy models for the skill-swap application.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, CheckConstraint, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os

# Create the base class
Base = declarative_base()

class User(Base):
    """User model for storing user account information."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(100))
    bio = Column(Text)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    requests_as_requester = relationship("ServiceRequest", foreign_keys="ServiceRequest.requester_id", back_populates="requester")
    requests_as_provider = relationship("ServiceRequest", foreign_keys="ServiceRequest.provider_id", back_populates="provider")
    reviews_given = relationship("Review", foreign_keys="Review.reviewer_id", back_populates="reviewer")
    reviews_received = relationship("Review", foreign_keys="Review.reviewee_id", back_populates="reviewee")

class Skill(Base):
    """Skill model for storing skills information."""
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    
    # Relationships
    users = relationship("UserSkill", back_populates="skill", cascade="all, delete-orphan")
    service_requests = relationship("ServiceRequest", back_populates="skill")

class UserSkill(Base):
    """Association table for User-Skill many-to-many relationship."""
    __tablename__ = 'user_skills'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="skills")
    skill = relationship("Skill", back_populates="users")

class ServiceRequest(Base):
    """ServiceRequest model for storing service request information."""
    __tablename__ = 'service_requests'
    
    id = Column(Integer, primary_key=True)
    requester_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    provider_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills.id'), nullable=True)
    time = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    credit_cost = Column(Integer, nullable=False)
    status = Column(String(20), default='pending')
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Add check constraint for status
    __table_args__ = (
        CheckConstraint(status.in_(['pending', 'accepted', 'rejected', 'completed'])),
    )
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], back_populates="requests_as_requester")
    provider = relationship("User", foreign_keys=[provider_id], back_populates="requests_as_provider")
    skill = relationship("Skill", back_populates="service_requests")
    reviews = relationship("Review", back_populates="service_request", cascade="all, delete-orphan")

class Review(Base):
    """Review model for storing review information."""
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    service_request_id = Column(Integer, ForeignKey('service_requests.id', ondelete='CASCADE'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reviewee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    rating = Column(Integer, nullable=False)
    comments = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Add check constraint for rating
    __table_args__ = (
        CheckConstraint('rating BETWEEN 1 AND 5'),
    )
    
    # Relationships
    service_request = relationship("ServiceRequest", back_populates="reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    reviewee = relationship("User", foreign_keys=[reviewee_id], back_populates="reviews_received")

# Get database URL from the database file path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skill_swap.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine
engine = create_engine(DATABASE_URL)

def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(engine)
