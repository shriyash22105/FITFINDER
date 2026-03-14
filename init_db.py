"""
FitFinder Database Initialization Script
Creates all tables in PostgreSQL/SQLite database based on ER diagram
"""

import os
from passlib.hash import bcrypt
from sqlalchemy import create_engine

# Database URL - change this to match your PostgreSQL configuration
# Default uses SQLite for testing, change to PostgreSQL for production
USE_SQLITE = os.environ.get('USE_SQLITE', 'true').lower() == 'true'

if USE_SQLITE:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'fitfinder.db')
    DATABASE_URL = f'sqlite:///{DB_PATH}'
else:
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://postgres:postgres@localhost:5432/fitfinder'

def init_db():
    """Initialize database with all required tables"""
    engine = create_engine(DATABASE_URL)
    
    # Import and create all tables from models
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
    
    from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
    from datetime import datetime
    
    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        userid = Column(String(50), unique=True, nullable=False)
        password = Column(String(255), nullable=False)
        role = Column(String(20), default='USER')

    class UserProfile(Base):
        __tablename__ = 'user_profiles'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('users.id'), unique=True)
        name = Column(String(100))
        email = Column(String(100))
        avatar = Column(String(255))
        gender = Column(String(20))
        preferred_style = Column(String(50))
        preferred_color = Column(String(50))
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow)

    class TryOnHistory(Base):
        __tablename__ = 'try_on_history'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('users.id'))
        human_image_url = Column(String(500))
        clothing_image_url = Column(String(500))
        result_image_url = Column(String(500))
        garment_type = Column(String(50))
        outfit_description = Column(Text)
        created_at = Column(DateTime, default=datetime.utcnow)

    class SavedOutfit(Base):
        __tablename__ = 'saved_outfits'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('users.id'))
        outfit_name = Column(String(100))
        outfit_description = Column(Text)
        image_url = Column(String(500))
        style = Column(String(50))
        occasion = Column(String(50))
        gender = Column(String(20))
        created_at = Column(DateTime, default=datetime.utcnow)

    class Outfit(Base):
        __tablename__ = 'outfits'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('users.id'))
        outfit_name = Column(String(100))
        style = Column(String(50))
        occasion = Column(String(50))
        season = Column(String(50))
        gender = Column(String(20))
        color_preference = Column(String(50))
        top_description = Column(Text)
        bottom_description = Column(Text)
        shoes_description = Column(Text)
        accessories_description = Column(Text)
        image_url = Column(String(500))
        is_ai_generated = Column(Boolean, default=True)
        created_at = Column(DateTime, default=datetime.utcnow)

    class ContactMessage(Base):
        __tablename__ = 'contact_messages'
        id = Column(Integer, primary_key=True)
        name = Column(String(100))
        email = Column(String(100))
        message = Column(Text)
        is_read = Column(Boolean, default=False)
        created_at = Column(DateTime, default=datetime.utcnow)
    
    # Create all tables
    Base.metadata.create_all(engine)
    print("Tables created successfully!")
    
    # Insert default admin user if not exists
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if user exists
        existing_user = session.query(User).filter_by(userid='admin123').first()
        
        if not existing_user:
            # Use bcrypt directly
            import bcrypt
            password = 'Secret@123'
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            admin = User(userid='admin123', password=hashed.decode('utf-8'), role='ADMIN')
            session.add(admin)
            session.flush()  # Flush to get the ID
            
            # Create profile
            profile = UserProfile(user_id=admin.id, name='Admin', email='admin@fitfinder.com')
            session.add(profile)
            session.commit()
            print("Default admin user created!")
        else:
            print("Admin user already exists!")
        
        print(f"Database initialized successfully!")
        print(f"Database URL: {DATABASE_URL}")
        print(f"Default login: userid='admin123', password='Secret@123'")
        
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()


if __name__ == '__main__':
    init_db()

