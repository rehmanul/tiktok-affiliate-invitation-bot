from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class CreatorProfile(Base):
    __tablename__ = 'creator_profiles'
    id = Column(Integer, primary_key=True)
    tiktok_id = Column(String(64), unique=True, nullable=False)
    username = Column(String(128), nullable=False)
    followers = Column(Integer, nullable=False)
    category = Column(String(128))
    gmv = Column(Float, default=0.0)
    promotion_type = Column(String(64))  # e.g., video, live stream, both
    region = Column(String(64))  # e.g., UK
    last_invited = Column(DateTime)
    invited_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Campaign(Base):
    __tablename__ = 'campaigns'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    min_followers = Column(Integer, default=1000)
    max_followers = Column(Integer, default=100000)
    min_gmv = Column(Float, default=0.0)
    categories = Column(Text)  # comma separated categories
    promotion_types = Column(Text)  # comma separated promotion types
    region = Column(String(64), default='UK')
    max_invites = Column(Integer, default=50)
    invites_sent = Column(Integer, default=0)
    status = Column(String(64), default='pending')  # pending, running, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    invitations = relationship("Invitation", back_populates="campaign")

class Invitation(Base):
    __tablename__ = 'invitations'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    creator_id = Column(Integer, ForeignKey('creator_profiles.id'))
    status = Column(String(64), default='pending')  # pending, sent, failed, accepted, rejected
    sent_at = Column(DateTime)
    response_at = Column(DateTime)
    response = Column(String(256))

    campaign = relationship("Campaign", back_populates="invitations")
