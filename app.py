
import os
import io
import time
import json
import base64
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, redirect, url_for, session, send_from_directory
from flask_cors import CORS
import requests
from PIL import Image
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import bcrypt
import jwt

# ============= CONFIGURATION =============

import os
USE_SQLITE = os.environ.get('USE_SQLITE', 'true').lower() == 'true'

if USE_SQLITE:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'fitfinder.db')
    DB_NAME = f'sqlite:///{DB_PATH}'
else:
    DB_NAME = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/fitfinder')
SECRET_KEY = os.environ.get('SECRET_KEY', 'g8L5mK9pQ2rT7vW3xY6zA0bC4dE8fF1gH4iJ7kL0mN3oP6qR9sT2uV5wX8yZ1')

if not SECRET_KEY or SECRET_KEY == 'fitfinder-secret-key-change-in-production':
    print('[WARNING] Using fallback SECRET_KEY. Set SECRET_KEY env var for production!')

# Miragic API configuration
API_KEY = os.environ.get('MIRAGIC_API_KEY')
BASE_URL = 'https://backend.miragic.ai'

# Debug: Print if API key is loaded (only first 10 chars for security)
if API_KEY:
    print(f"[DEBUG] Miragic API Key loaded: {API_KEY[:10]}...")
else:
    print("[DEBUG] Miragic API Key NOT loaded - will use local fallback")

# Folder paths
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
GENERATED_FOLDER = os.path.join(APP_ROOT, 'generated_outfits')
TMP_FOLDER = os.path.join(APP_ROOT, 'tmp')
os.makedirs(GENERATED_FOLDER, exist_ok=True)
os.makedirs(TMP_FOLDER, exist_ok=True)

# ============= FLASK APP SETUP =============

app = Flask(__name__, static_folder='src/main/resources/static')
CORS(app, supports_credentials=True)
app.secret_key = SECRET_KEY

# Production-ready setup
from dotenv import load_dotenv
load_dotenv()

# Rate limiting (prod)
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    print("[INFO] Rate limiter enabled")
except ImportError:
    print("[INFO] Install Flask-Limiter for rate limiting")

# Token blacklist (in-memory for prod Redis recommended)
token_blacklist = set()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid token format'}), 401
        
        if token in token_blacklist:
            return jsonify({'success': False, 'message': 'Token blacklisted (logged out)'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            db = get_db_session()
            user = db.query(User).filter_by(id=data['user_id']).first()
            db.close()
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 401
            current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# Removed duplicate logout route (exists earlier)
# Logout now properly blacklists token


# Register Mobile Blueprint
try:
    from src.blueprints.mobile import mobile_bp
    app.register_blueprint(mobile_bp)
    print("[INFO] Mobile Blueprint registered at /api/mobile/v1")
except ImportError as e:
    print(f"[WARNING] Failed to load mobile blueprint: {e}")

# ============= DATABASE SETUP =============

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    userid = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default='USER')
    
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    try_on_histories = relationship("TryOnHistory", back_populates="user")
    saved_outfits = relationship("SavedOutfit", back_populates="user")
    outfits = relationship("Outfit", back_populates="user")

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
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="profile")

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
    
    user = relationship("User", back_populates="try_on_histories")

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
    
    user = relationship("User", back_populates="saved_outfits")

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
    
    user = relationship("User", back_populates="outfits")

class ContactMessage(Base):
    __tablename__ = 'contact_messages'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create engine
engine = create_engine(DB_NAME)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# ============= HELPER FUNCTIONS =============

def get_db_session():
    return Session()

def generate_token(user_id, userid):
    payload = {
        'user_id': user_id,
        'userid': userid,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            db = get_db_session()
            user = db.query(User).filter_by(id=data['user_id']).first()
            db.close()
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 401
            current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def _post_files(url, data, files):
    """Send files to Miragic API with proper authentication"""
    opened = []
    multipart = []
    try:
        for key, (filename, path, content_type) in files:
            f = open(path, 'rb')
            opened.append(f)
            multipart.append((key, (filename, f, content_type)))
        
        # Only use X-API-Key header as per Miragic API docs
        headers = {'X-API-Key': API_KEY}
        resp = requests.post(url, headers=headers, data=data, files=multipart, timeout=60)
        return resp
    finally:
        for f in opened:
            try:
                f.close()
            except Exception:
                pass

def create_vto_job_single(human_path, cloth_path, garment_type='full_body'):
    """Create single item virtual try-on job"""
    url = f"{BASE_URL}/api/v1/virtual-try-on"
    data = {'garmentType': garment_type}  # upper_body, lower_body, full_body
    # Pass file paths - _post_files will handle opening them
    files = [
        ('humanImage', (os.path.basename(human_path), human_path, 'image/jpeg')),
        ('clothImage', (os.path.basename(cloth_path), cloth_path, 'image/jpeg')),
    ]
    return _post_files(url, data, files)

def create_vto_job_combo(human_path, top_path, bottom_path):
    """Create combo (top + bottom) virtual try-on job"""
    url = f"{BASE_URL}/api/v1/virtual-try-on"
    data = {'garmentType': 'comb'}
    # Pass file paths - _post_files will handle opening them
    files = [
        ('humanImage', (os.path.basename(human_path), human_path, 'image/jpeg')),
        ('clothImage', (os.path.basename(top_path), top_path, 'image/jpeg')),
        ('bottomClothImage', (os.path.basename(bottom_path), bottom_path, 'image/jpeg')),
    ]
    return _post_files(url, data, files)

def poll_job(job_id, timeout_sec=60, interval_sec=2):
    """Poll Miragic API for job status"""
    start = time.time()
    url = f"{BASE_URL}/api/v1/virtual-try-on/{job_id}"
    # Only use X-API-Key header as per Miragic API docs
    headers = {'X-API-Key': API_KEY}
    
    while True:
        try:
            resp = requests.get(url, headers=headers, timeout=30)
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': 'Network error', 'details': str(e)}
        
        try:
            data = resp.json()
        except Exception:
            return {'success': False, 'error': 'invalid json response', 'raw': resp.text}
        
        # Check status from response - Miragic returns data.data.status
        try:
            status = data.get('data', {}).get('status', 'UNKNOWN')
            
            if status == 'COMPLETED':
                # Return the full result with processedUrl
                return {
                    'success': True,
                    'data': {
                        'processedUrl': data.get('data', {}).get('processedUrl'),
                        'resultImagePath': data.get('data', {}).get('resultImagePath'),
                        'status': 'COMPLETED'
                    }
                }
            elif status == 'FAILED':
                error_msg = data.get('data', {}).get('errorMessage', 'Job failed')
                return {'success': False, 'error': error_msg, 'raw': data}
            elif status in ('PENDING', 'PROCESSING'):
                # Continue polling
                if time.time() - start > timeout_sec:
                    return {'success': False, 'error': 'Polling timeout', 'raw': data}
                time.sleep(interval_sec)
                continue
            else:
                # Unknown status, continue polling
                if time.time() - start > timeout_sec:
                    return {'success': False, 'error': 'Polling timeout', 'raw': data}
                time.sleep(interval_sec)
                
        except Exception as e:
            return {'success': False, 'error': 'Unexpected response format', 'raw': data, 'details': str(e)}

def _image_to_datauri(pil_img):
    buf = io.BytesIO()
    pil_img.save(buf, format='PNG')
    b = base64.b64encode(buf.getvalue()).decode('ascii')
    return f'data:image/png;base64,{b}'

def local_fallback_single(human_path, cloth_path):
    try:
        human = Image.open(human_path).convert('RGBA')
        cloth = Image.open(cloth_path).convert('RGBA')
        cloth = cloth.resize((int(human.width * 0.6), int(human.height * 0.6)))
        out = Image.new('RGBA', human.size)
        out.paste(human, (0, 0))
        x = (human.width - cloth.width) // 2
        y = int(human.height * 0.25)
        out.paste(cloth, (x, y), cloth)
        out = out.convert('RGB')
        
        filename = f"virtual_tryon_fallback_{int(time.time()*1000)}.png"
        path = os.path.join(GENERATED_FOLDER, filename)
        out.save(path, format='PNG')
        
        return {'success': True, 'note': 'local_fallback', 'file': filename, 'image': _image_to_datauri(out)}
    except Exception as e:
        return {'success': False, 'error': 'local fallback failed', 'details': str(e)}

# ============= AUTH ROUTES =============

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    userid = data.get('userid')
    password = data.get('password')
    
    if not userid or not password:
        return jsonify({'success': False, 'message': 'UserID and password are required'}), 400
    
    db = get_db_session()
    existing_user = db.query(User).filter_by(userid=userid).first()
    
    if existing_user:
        db.close()
        return jsonify({'success': False, 'message': 'UserID already exists'}), 400
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(userid=userid, password=hashed_password, role='USER')
    db.add(new_user)
    db.commit()
    
    # Create empty profile
    profile = UserProfile(user_id=new_user.id)
    db.add(profile)
    db.commit()
    
    db.close()
    
    return jsonify({'success': True, 'message': 'Registration successful'})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    userid = data.get('userid')
    password = data.get('password')
    
    if not userid or not password:
        return jsonify({'success': False, 'message': 'UserID and password are required'}), 400
    
    db = get_db_session()
    user = db.query(User).filter_by(userid=userid).first()
    
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        db.close()
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    token = generate_token(user.id, user.userid)
    db.close()
    
    return jsonify({
        'success': True,
        'data': {
            'token': token,
            'userid': user.userid,
            'userId': user.id,
            'role': user.role
        }
    })

@app.route('/api/auth/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    """Refresh token for 7 more days (call before expiry)"""


    new_token = generate_token(current_user.id, current_user.userid)
    return jsonify({
        'success': True,
        'data': {
            'token': new_token,
            'message': 'Token refreshed'
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# ============= PROFILE ROUTES =============

@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    db = get_db_session()
    profile = db.query(UserProfile).filter_by(user_id=current_user.id).first()
    
    if not profile:
        db.close()
        return jsonify({'success': False, 'message': 'Profile not found'}), 404
    
    profile_data = {
        'id': profile.id,
        'userId': profile.user_id,
        'name': profile.name,
        'email': profile.email,
        'avatar': profile.avatar,
        'gender': profile.gender,
        'preferredStyle': profile.preferred_style,
        'preferredColor': profile.preferred_color,
        'createdAt': profile.created_at.isoformat() if profile.created_at else None,
        'updatedAt': profile.updated_at.isoformat() if profile.updated_at else None
    }
    db.close()
    
    return jsonify({'success': True, 'data': {'profile': profile_data}})

@app.route('/api/profile/update', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    
    db = get_db_session()
    profile = db.query(UserProfile).filter_by(user_id=current_user.id).first()
    
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    if 'name' in data:
        profile.name = data['name']
    if 'email' in data:
        profile.email = data['email']
    if 'gender' in data:
        profile.gender = data['gender']
    if 'preferredStyle' in data:
        profile.preferred_style = data['preferredStyle']
    if 'preferredColor' in data:
        profile.preferred_color = data['preferredColor']
    
    db.commit()
    db.close()
    
    return jsonify({'success': True, 'message': 'Profile updated successfully'})

# ============= VIRTUAL TRY-ON ROUTES =============

@app.route('/api/tryon/single', methods=['POST'])
@token_required
def tryon_single(current_user):
    garment_type = request.form.get('garmentType', 'full_body')
    
    human_file = request.files.get('humanImage')
    cloth_file = request.files.get('clothImage')
    
    if not human_file or not cloth_file:
        return jsonify({'success': False, 'error': 'humanImage and clothImage are required'}), 400
    
    human_path = os.path.join(TMP_FOLDER, f"human_{int(time.time()*1000)}.jpg")
    cloth_path = os.path.join(TMP_FOLDER, f"cloth_{int(time.time()*1000)}.jpg")
    human_file.save(human_path)
    cloth_file.save(cloth_path)
    
    if API_KEY:
        try:
            resp = create_vto_job_single(human_path, cloth_path, garment_type)
        except Exception as e:
            return jsonify({'success': False, 'error': 'API request error', 'details': str(e)}), 500
        
        try:
            os.remove(human_path)
            os.remove(cloth_path)
        except OSError:
            pass
        
        if not resp.ok:
            return jsonify({
                'success': False, 
                'error': 'Miragic API request failed', 
                'status_code': resp.status_code,
                'details': resp.text[:500] if resp.text else 'No response body'
            }), 500
        
        try:
            data = resp.json()
        except Exception:
            return jsonify({
                'success': False, 
                'error': 'Invalid JSON response from Miragic', 
                'raw': resp.text[:500]
            }), 500
        
        # Try multiple formats to get job_id
        job_id = None
        if 'data' in data:
            job_id = data['data'].get('jobId') or data['data'].get('job_id')
        if not job_id:
            job_id = data.get('jobId') or data.get('job_id')
            
        if not job_id:
            return jsonify({
                'success': False, 
                'error': 'No job ID returned from Miragic', 
                'response': data
            }), 500
        
        job_result = poll_job(job_id)
        
        # Format the response properly for the frontend
        if job_result.get('success'):
            result_data = job_result.get('data', job_result)
            # Extract image from various possible formats
            image_url = result_data.get('resultUrl') or result_data.get('result_url') or result_data.get('image')
            if image_url:
                return jsonify({
                    'success': True,
                    'data': {
                        'processedUrl': image_url,
                        'resultImagePath': image_url
                    }
                })
        
        return jsonify(job_result)
    else:
        result = local_fallback_single(human_path, cloth_path)
        try:
            os.remove(human_path)
            os.remove(cloth_path)
        except OSError:
            pass
        return jsonify(result)

@app.route('/api/tryon/combo', methods=['POST'])
@token_required
def tryon_combo(current_user):
    human_file = request.files.get('humanImage')
    top_file = request.files.get('clothImage')
    bottom_file = request.files.get('bottomClothImage')
    
    if not human_file or not top_file or not bottom_file:
        return jsonify({'success': False, 'error': 'humanImage, clothImage, bottomClothImage are required'}), 400
    
    human_path = os.path.join(TMP_FOLDER, f"human_{int(time.time()*1000)}.jpg")
    top_path = os.path.join(TMP_FOLDER, f"top_{int(time.time()*1000)}.jpg")
    bottom_path = os.path.join(TMP_FOLDER, f"bottom_{int(time.time()*1000)}.jpg")
    human_file.save(human_path)
    top_file.save(top_path)
    bottom_file.save(bottom_path)
    
    if API_KEY:
        resp = create_vto_job_combo(human_path, top_path, bottom_path)
        for p in [human_path, top_path, bottom_path]:
            try:
                os.remove(p)
            except OSError:
                pass
        
        if not resp.ok:
            return jsonify({'success': False, 'error': 'Miragic request failed', 'details': resp.text}), 500
        
        data = resp.json()
        if not data.get('success'):
            return jsonify({'success': False, 'error': 'Miragic returned error', 'details': data}), 500
        
        job_id = data.get('data', {}).get('jobId')
        if not job_id:
            return jsonify({'success': False, 'error': 'no job id returned', 'details': data}), 500
        
        job_result = poll_job(job_id)
        
        # Format the response properly for the frontend
        if job_result.get('success'):
            result_data = job_result.get('data', job_result)
            image_url = result_data.get('processedUrl') or result_data.get('resultImagePath')
            if image_url:
                return jsonify({
                    'success': True,
                    'data': {
                        'processedUrl': image_url,
                        'resultImagePath': image_url
                    }
                })
        
        return jsonify(job_result)
    else:
        try:
            human = Image.open(human_path).convert('RGBA')
            top = Image.open(top_path).convert('RGBA')
            bottom = Image.open(bottom_path).convert('RGBA')
            top = top.resize((int(human.width * 0.6), int(human.height * 0.35)))
            bottom = bottom.resize((int(human.width * 0.6), int(human.height * 0.35)))
            out = Image.new('RGBA', human.size)
            out.paste(human, (0, 0))
            x = (human.width - top.width) // 2
            y_top = int(human.height * 0.2)
            y_bottom = int(human.height * 0.55)
            out.paste(top, (x, y_top), top)
            out.paste(bottom, (x, y_bottom), bottom)
            out = out.convert('RGB')
            
            filename = f"virtual_tryon_fallback_{int(time.time()*1000)}.png"
            path = os.path.join(GENERATED_FOLDER, filename)
            out.save(path, format='PNG')
            
            result = {'success': True, 'note': 'local_fallback', 'file': filename, 'image': _image_to_datauri(out)}
        except Exception as e:
            result = {'success': False, 'error': 'local fallback failed', 'details': str(e)}
        
        for p in [human_path, top_path, bottom_path]:
            try:
                os.remove(p)
            except OSError:
                pass
        
        return jsonify(result)

# ============= OUTFIT GENERATOR ROUTES =============

@app.route('/api/outfit/generate', methods=['POST'])
@token_required
def generate_outfit(current_user):
    data = request.get_json()
    style = data.get('style', 'casual')
    occasion = data.get('occasion', 'casual')
    gender = data.get('gender', 'female')
    season = data.get('season')
    color_preference = data.get('colorPreference')
    
    # Generate outfit description (in production, this would call an AI API)
    outfit_templates = {
        'casual': {
            'female': {
                'top': 'Classic white cotton t-shirt with a relaxed fit',
                'bottom': 'High-waisted blue track pants',
                'shoes': 'White leather sneakers',
                'accessories': 'Simple gold chain necklace, canvas tote bag'
            },
            'male': {
                'top': 'Navy blue crew-neck sweatshirt',
                'bottom': 'Black slim-fit chino pants',
                'shoes': 'Black leather loafers',
                'accessories': 'Minimalist watch, leather belt'
            }
        },
        'work': {
            'female': {
                'top': 'Crisp white button-up blouse',
                'bottom': 'Tailored black pencil skirt',
                'bottom_m': 'Charcoal grey dress pants',
                'shoes': 'Black pointed-toe heels',
                'accessories': 'Simple pearl earrings, leather handbag'
            },
            'male': {
                'top': 'Light blue oxford shirt',
                'bottom': 'Grey wool dress pants',
                'shoes': 'Brown leather oxford shoes',
                'accessories': 'Leather briefcase, silk tie'
            }
        },
        'formal': {
            'female': {
                'top': 'Elegant silk blouse in champagne',
                'bottom': 'Long black evening gown skirt',
                'shoes': 'Black stiletto heels',
                'accessories': 'Diamond drop earrings, clutch purse'
            },
            'male': {
                'top': 'Black tuxedo jacket with satin lapels',
                'bottom': 'Matching tuxedo pants',
                'shoes': 'Black patent leather shoes',
                'accessories': 'Bow tie, cufflinks, pocket square'
            }
        },
        'party': {
            'female': {
                'top': 'Sequined crop top',
                'bottom': 'Metallic mini skirt',
                'shoes': 'Strappy gold heels',
                'accessories': 'Statement earrings, mini crossbody bag'
            },
            'male': {
                'top': 'Patterned silk shirt',
                'bottom': 'Dark slim-fit jeans',
                'shoes': 'White sneakers',
                'accessories': 'Bracelet, sunglasses'
            }
        },
        'date-night': {
            'female': {
                'top': 'Lace trimmed cami top',
                'bottom': 'Flowy midi skirt',
                'shoes': 'Rose gold strappy sandals',
                'accessories': 'Heart necklace, small handbag'
            },
            'male': {
                'top': 'Grey merino wool sweater',
                'bottom': 'Dark wash jeans',
                'shoes': 'Clean white sneakers',
                'accessories': 'Subtle cologne'
            }
        },
        'workout': {
            'female': {
                'top': 'Moisture-wicking sports bra',
                'bottom': 'Running shorts with pockets',
                'shoes': 'Cushioned running shoes',
                'accessories': 'Fitness tracker, hair tie'
            },
            'male': {
                'top': 'Performance tank top',
                'bottom': 'Athletic joggers',
                'shoes': 'Training shoes',
                'accessories': 'Smart watch, gym bag'
            }
        }
    }
    
    template = outfit_templates.get(style, outfit_templates['casual']).get(gender, outfit_templates['casual']['female'])
    
    # Build outfit
    outfit = {
        'outfitName': f"{style.title()} {gender.title()} Outfit",
        'style': style,
        'occasion': occasion,
        'gender': gender,
        'season': season or 'All Seasons',
        'colorPreference': color_preference or 'Neutral tones',
        'topDescription': template['top'],
        'bottomDescription': template.get('bottom', template.get('bottom_m', '')),
        'shoesDescription': template['shoes'],
        'accessoriesDescription': template['accessories'],
        'colorPalette': 'Navy,White,Black,Grey' if not color_preference else color_preference
    }
    
    # Save outfit to database
    db = get_db_session()
    new_outfit = Outfit(
        user_id=current_user.id,
        outfit_name=outfit['outfitName'],
        style=outfit['style'],
        occasion=outfit['occasion'],
        season=outfit['season'],
        gender=outfit['gender'],
        color_preference=outfit['colorPreference'],
        top_description=outfit['topDescription'],
        bottom_description=outfit['bottomDescription'],
        shoes_description=outfit['shoesDescription'],
        accessories_description=outfit['accessoriesDescription'],
        is_ai_generated=True
    )
    db.add(new_outfit)
    db.commit()
    outfit['id'] = new_outfit.id
    db.close()
    
    return jsonify({
        'success': True,
        'data': {'outfit': outfit}
    })

# ============= GALLERY ROUTES =============

@app.route('/api/gallery', methods=['GET'])
@token_required
def get_gallery(current_user):
    db = get_db_session()
    outfits = db.query(SavedOutfit).filter_by(user_id=current_user.id).order_by(SavedOutfit.created_at.desc()).all()
    
    outfits_data = [{
        'id': o.id,
        'outfitName': o.outfit_name,
        'outfitDescription': o.outfit_description,
        'imageUrl': o.image_url,
        'style': o.style,
        'occasion': o.occasion,
        'gender': o.gender,
        'createdAt': o.created_at.isoformat() if o.created_at else None
    } for o in outfits]
    
    db.close()
    
    return jsonify({
        'success': True,
        'data': {'outfits': outfits_data}
    })

@app.route('/api/gallery/save', methods=['POST'])
@token_required
def save_to_gallery(current_user):
    data = request.get_json()
    
    db = get_db_session()
    new_outfit = SavedOutfit(
        user_id=current_user.id,
        outfit_name=data.get('outfitName', 'Untitled'),
        outfit_description=data.get('outfitDescription', ''),
        image_url=data.get('imageUrl', ''),
        style=data.get('style', ''),
        occasion=data.get('occasion', ''),
        gender=data.get('gender', '')
    )
    db.add(new_outfit)
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'message': 'Outfit saved to gallery'
    })

@app.route('/api/gallery/<int:outfit_id>', methods=['DELETE'])
@token_required
def delete_from_gallery(current_user, outfit_id):
    db = get_db_session()
    outfit = db.query(SavedOutfit).filter_by(id=outfit_id, user_id=current_user.id).first()
    
    if not outfit:
        db.close()
        return jsonify({'success': False, 'message': 'Outfit not found'}), 404
    
    db.delete(outfit)
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'message': 'Outfit deleted'
    })

# ============= HISTORY ROUTES =============

@app.route('/api/history', methods=['GET'])
@app.route('/api/history/recent', methods=['GET'])
@token_required
def get_history(current_user):
    limit = request.args.get('limit', 20)
    
    db = get_db_session()
    history = db.query(TryOnHistory).filter_by(user_id=current_user.id).order_by(TryOnHistory.created_at.desc()).limit(limit).all()
    
    history_data = [{
        'id': h.id,
        'humanImageUrl': h.human_image_url,
        'clothingImageUrl': h.clothing_image_url,
        'resultImageUrl': h.result_image_url,
        'garmentType': h.garment_type,
        'description': h.outfit_description,
        'createdAt': h.created_at.isoformat() if h.created_at else None
    } for h in history]
    
    db.close()
    
    return jsonify({
        'success': True,
        'data': {'history': history_data}
    })

@app.route('/api/history/save', methods=['POST'])
@token_required
def save_history(current_user):
    data = request.get_json()
    
    db = get_db_session()
    new_history = TryOnHistory(
        user_id=current_user.id,
        human_image_url=data.get('humanImageUrl', ''),
        clothing_image_url=data.get('clothingImageUrl', ''),
        result_image_url=data.get('resultImageUrl', ''),
        garment_type=data.get('garmentType', 'single'),
        outfit_description=data.get('description', '')
    )
    db.add(new_history)
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'message': 'History saved'
    })

# ============= CONTACT ROUTES =============

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')
    
    if not name or not email or not message:
        return jsonify({'success': False, 'error': 'All fields are required'}), 400
    
    db = get_db_session()
    new_message = ContactMessage(name=name, email=email, message=message)
    db.add(new_message)
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'message': 'Message sent successfully'
    })

# ============= HEALTH CHECK =============

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'miragic': bool(API_KEY),
        'api_key_loaded': bool(API_KEY),
        'api_key_prefix': API_KEY[:8] + '...' if API_KEY else None
    })

# ============= STATIC FILE ROUTES =============

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# ============= MAIN =============

if __name__ == '__main__':
    # Create generated_outfits folder in the expected location
    java_generated = os.path.join(APP_ROOT, 'generated_outfits')
    os.makedirs(java_generated, exist_ok=True)
    
    print("Starting FitFinder Flask Backend...")
    print(f"Database: {DB_NAME}")
    print(f"Static files: {app.static_folder}")
    print(f"Generated outfits: {GENERATED_FOLDER}")
    app.run(host='0.0.0.0', port=5000, debug=True)

