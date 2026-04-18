import os
import io
import time
import json
import base64
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, redirect, url_for, session, send_from_directory
from flask_cors import CORS
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
from PIL import Image
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import bcrypt
import jwt

# ============= CONFIGURATION =============
import os
from dotenv import load_dotenv

# Load environment variables first!
load_dotenv()

USE_SQLITE = os.environ.get('USE_SQLITE', 'false').lower() == 'true'

if USE_SQLITE:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'DATABASE_SQLITE/fitfinder.db')
    DB_NAME = f'sqlite:///{DB_PATH}'
else:
    DB_NAME = os.environ.get('DATABASE_URL', 'postgresql+psycopg://postgres:postgres@localhost:5432/fitfinder')
    if DB_NAME.startswith('postgres://'):
        DB_NAME = DB_NAME.replace('postgres://', 'postgresql+psycopg://', 1)
    elif DB_NAME.startswith('postgresql://'):
        DB_NAME = DB_NAME.replace('postgresql://', 'postgresql+psycopg://', 1)
SECRET_KEY = os.environ.get('SECRET_KEY', 'g8L5mK9pQ2rT7vW3xY6zA0bC4dE8fF1gH4iJ7kL0mN3oP6qR9sT2uV5wX8yZ1')

if not SECRET_KEY or SECRET_KEY in ('fitfinder-secret-key-change-in-production', 'g8L5mK9pQ2rT7vW3xY6zA0bC4dE8fF1gH4iJ7kL0mN3oP6qR9sT2uV5wX8yZ1'):
    if os.environ.get('FLASK_ENV', '').lower() == 'production' or os.environ.get('PRODUCTION', '').lower() in ('1', 'true'):
        raise RuntimeError('SECRET_KEY must be set in production environment')
    print('[WARNING] Using fallback SECRET_KEY. Set SECRET_KEY env var for production!')

# Google Gemini configuration
GEMINI_API_KEY = os.environ.get('GOOGLE_GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY')
GEMINI_MODEL = os.environ.get('GOOGLE_GEMINI_MODEL', 'gemini-2.5-flash-lite')
GEMINI_API_BASE = os.environ.get('GOOGLE_GEMINI_API_BASE', 'https://generativelanguage.googleapis.com/v1beta/models')

if GEMINI_API_KEY:
    print(f"[DEBUG] Gemini API Key loaded for model: {GEMINI_MODEL} via {GEMINI_API_BASE}")
else:
    print("[DEBUG] Gemini API Key NOT loaded - outfit generation will use templates")

# Folder paths
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
GENERATED_FOLDER = os.path.join(APP_ROOT, 'generated_outfits')
TMP_FOLDER = os.path.join(APP_ROOT, 'tmp')
os.makedirs(GENERATED_FOLDER, exist_ok=True)
os.makedirs(TMP_FOLDER, exist_ok=True)

# ============= FLASK APP SETUP =============

app = Flask(__name__, static_folder='src/main/resources/static')
CORS(app, supports_credentials=True)
limiter = Limiter(app=app, key_func=get_remote_address)
# csrf = CSRFProtect(app)  # Disabled for API-first application
app.secret_key = SECRET_KEY

# Enhanced logging for debugging
import logging
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)
app.logger.info("FitFinder Flask app started with DEBUG logging")
app.logger.info("Try-on provider: local-only fallback")


# CSRF protection disabled for API-first application
# @app.before_request
# def csrf_exempt_api():
#     if request.path.startswith('/api/'):
#         # Skip CSRF check for API routes
#         pass

# Prevent oversized uploads to avoid DoS
app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024  # 6 MB
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_IMAGE_MIMETYPES = {'image/png', 'image/jpeg', 'image/jpg'}

# Production-ready setup
# (dotenv loaded at the top)

# Rate limiting (prod)
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(
        app=app,
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
            parts = auth_header.split(" ")
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
            else:
                return jsonify({'success': False, 'message': 'Invalid token format. Use "Authorization: Bearer <token>"'}), 401

        if not token:
            return jsonify({'success': False, 'message': 'Token is missing. Login to obtain a token and include in Authorization header.'}), 401

        if token in token_blacklist:
            return jsonify({'success': False, 'message': 'Token blacklisted (logged out)'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            db = get_db_session()
            user = db.query(User).filter_by(id=data.get('user_id')).first()
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


def is_allowed_image_file(file):
    if not file:
        return False
    filename = file.filename or ''
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return False
    if file.mimetype not in ALLOWED_IMAGE_MIMETYPES:
        return False
    return True


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'success': False, 'error': 'File too large (<=6MB)'}), 413


@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# ============= DATABASE SETUP =============

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    userid = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default='USER')
    created_at = Column(DateTime, default=datetime.utcnow)
    
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

def _save_uploaded_images(files_with_prefix):
    import uuid
    saved_paths = []
    for prefix, upload in files_with_prefix:
        ext = upload.filename.rsplit('.', 1)[-1].lower() if '.' in upload.filename else 'jpg'
        unique_id = str(uuid.uuid4())[:8]
        path = os.path.join(TMP_FOLDER, f"{prefix}_{unique_id}.{ext}")
        upload.save(path)
        saved_paths.append(path)
    return saved_paths


def _cleanup_paths(paths):
    for path in paths:
        try:
            os.remove(path)
        except Exception as e:
            app.logger.warning(f"Cleanup failed {path}: {e}")


def _fit_overlay(base_image, overlay_image, width_ratio, height_ratio, y_ratio):
    target_width = max(1, int(base_image.width * width_ratio))
    target_height = max(1, int(base_image.height * height_ratio))

    fitted = overlay_image.copy()
    fitted.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

    x = (base_image.width - fitted.width) // 2
    y = max(0, int(base_image.height * y_ratio) - fitted.height // 2)
    return fitted, x, y


def _detect_pose_geometry(human_path):
    try:
        import mediapipe as mp  # type: ignore[import-not-found]
    except Exception:
        return None

    try:
        image = Image.open(human_path).convert('RGB')
        image_width, image_height = image.size
        pose = mp.solutions.pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
        )
        result = pose.process(image)
        pose.close()

        if not result.pose_landmarks:
            return None

        landmarks = result.pose_landmarks.landmark

        def _point(index):
            landmark = landmarks[index]
            return (
                max(0.0, min(1.0, landmark.x)) * image_width,
                max(0.0, min(1.0, landmark.y)) * image_height,
            )

        left_shoulder = _point(mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value)
        right_shoulder = _point(mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value)
        left_hip = _point(mp.solutions.pose.PoseLandmark.LEFT_HIP.value)
        right_hip = _point(mp.solutions.pose.PoseLandmark.RIGHT_HIP.value)

        shoulder_center_x = (left_shoulder[0] + right_shoulder[0]) / 2
        shoulder_center_y = (left_shoulder[1] + right_shoulder[1]) / 2
        hip_center_x = (left_hip[0] + right_hip[0]) / 2
        hip_center_y = (left_hip[1] + right_hip[1]) / 2
        shoulder_width = max(1.0, abs(left_shoulder[0] - right_shoulder[0]))
        torso_height = max(1.0, abs(hip_center_y - shoulder_center_y))

        return {
            'shoulder_center_x': shoulder_center_x,
            'shoulder_center_y': shoulder_center_y,
            'hip_center_x': hip_center_x,
            'hip_center_y': hip_center_y,
            'shoulder_width': shoulder_width,
            'torso_height': torso_height,
            'image_width': image_width,
            'image_height': image_height,
        }
    except Exception as e:
        app.logger.warning(f'Pose detection failed for {human_path}: {e}')
        return None


def _place_overlay_from_pose(base_image, overlay_image, pose_geometry, kind='upper'):
    if not pose_geometry:
        if kind == 'upper':
            return _fit_overlay(base_image, overlay_image, width_ratio=0.52, height_ratio=0.48, y_ratio=0.23)
        return _fit_overlay(base_image, overlay_image, width_ratio=0.56, height_ratio=0.34, y_ratio=0.58)

    if kind == 'upper':
        width_ratio = min(0.72, max(0.42, pose_geometry['shoulder_width'] / pose_geometry['image_width'] * 1.75))
        height_ratio = min(0.58, max(0.30, pose_geometry['torso_height'] / pose_geometry['image_height'] * 1.05))
        fitted = overlay_image.copy()
        fitted.thumbnail((max(1, int(base_image.width * width_ratio)), max(1, int(base_image.height * height_ratio))), Image.Resampling.LANCZOS)
        x = int(pose_geometry['shoulder_center_x'] - fitted.width / 2)
        y = int(pose_geometry['shoulder_center_y'] - fitted.height * 0.12)
        return fitted, max(0, x), max(0, y)

    width_ratio = min(0.72, max(0.44, pose_geometry['shoulder_width'] / pose_geometry['image_width'] * 1.65))
    height_ratio = min(0.42, max(0.24, pose_geometry['torso_height'] / pose_geometry['image_height'] * 0.58))
    fitted = overlay_image.copy()
    fitted.thumbnail((max(1, int(base_image.width * width_ratio)), max(1, int(base_image.height * height_ratio))), Image.Resampling.LANCZOS)
    x = int(pose_geometry['hip_center_x'] - fitted.width / 2)
    y = int(pose_geometry['hip_center_y'] - fitted.height * 0.18)
    return fitted, max(0, x), max(0, y)

def _image_to_datauri(pil_img):
    buf = io.BytesIO()
    pil_img.save(buf, format='PNG')
    b = base64.b64encode(buf.getvalue()).decode('ascii')
    return f'data:image/png;base64,{b}'


def _extract_json_object(text):
    if not text:
        return None

    cleaned = text.strip()
    if cleaned.startswith('```'):
        cleaned = cleaned.strip('`')
        if cleaned.lower().startswith('json'):
            cleaned = cleaned[4:].strip()

    start = cleaned.find('{')
    end = cleaned.rfind('}')
    if start == -1 or end == -1 or end <= start:
        return None

    try:
        return json.loads(cleaned[start:end + 1])
    except Exception:
        return None


def generate_outfit_with_gemini(style, occasion, gender, season=None, color_preference=None):
    if not GEMINI_API_KEY:
        return None

    prompt = (
        'Generate a fashion outfit recommendation as strict JSON only. '
        'Return exactly these keys: outfitName, style, occasion, gender, season, colorPreference, '
        'topDescription, bottomDescription, shoesDescription, accessoriesDescription, colorPalette. '
        f'Use style={style}, occasion={occasion}, gender={gender}, season={season or "All Seasons"}, '
        f'colorPreference={color_preference or "Neutral tones"}. '
        'Keep descriptions concise, practical, and wearable.'
    )

    payload = {
        'contents': [
            {
                'role': 'user',
                'parts': [
                    {'text': prompt}
                ]
            }
        ],
        'generationConfig': {
            'temperature': 0.7,
            'responseMimeType': 'application/json'
        }
    }

    url = f'{GEMINI_API_BASE}/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}'

    try:
        resp = requests.post(url, json=payload, timeout=30)
        if not resp.ok:
            app.logger.warning(f'Gemini request failed: status={resp.status_code}, body={resp.text[:300]}')
            return None

        data = resp.json()
        candidates = data.get('candidates', []) if isinstance(data, dict) else []
        if not candidates:
            return None

        parts = candidates[0].get('content', {}).get('parts', [])
        response_text = ''.join(part.get('text', '') for part in parts if isinstance(part, dict))
        outfit_data = _extract_json_object(response_text)
        if not outfit_data:
            return None

        return {
            'outfitName': outfit_data.get('outfitName') or f'{style.title()} {gender.title()} Outfit',
            'style': outfit_data.get('style') or style,
            'occasion': outfit_data.get('occasion') or occasion,
            'gender': outfit_data.get('gender') or gender,
            'season': outfit_data.get('season') or season or 'All Seasons',
            'colorPreference': outfit_data.get('colorPreference') or color_preference or 'Neutral tones',
            'topDescription': outfit_data.get('topDescription') or '',
            'bottomDescription': outfit_data.get('bottomDescription') or '',
            'shoesDescription': outfit_data.get('shoesDescription') or '',
            'accessoriesDescription': outfit_data.get('accessoriesDescription') or '',
            'colorPalette': outfit_data.get('colorPalette') or (color_preference or 'Neutral tones')
        }
    except Exception as e:
        app.logger.warning(f'Gemini generation failed, falling back to templates: {e}')
        return None

def local_fallback_single(human_path, cloth_path, garment_type='full_body'):
    try:
        try:
            # Try Local Deep Learning AI (IDM-VTON / Diffusers) first
            from src.model.idm_vton import run_inference
            filename = f"virtual_tryon_ai_{int(time.time()*1000)}.png"
            path = os.path.join(GENERATED_FOLDER, filename)
            run_inference(human_path, cloth_path, path)
            
            # Read image back to base64 for frontend
            out = Image.open(path)
            return {'success': True, 'note': 'local_ai_diffusion', 'file': filename, 'image': _image_to_datauri(out)}
        except ImportError:
            # PyTorch/Diffusers not installed, fall through to Pillow mock
            pass
        except Exception as e:
            print(f"[WARNING] Local AI inference failed, falling back to basic mock: {e}")

        # Basic Pillow mock fallback
        human = Image.open(human_path).convert('RGBA')
        cloth = Image.open(cloth_path).convert('RGBA')
        pose_geometry = _detect_pose_geometry(human_path)

        if garment_type in ('lower_body', 'pants', 'bottom'):
            cloth, x, y = _place_overlay_from_pose(human, cloth, pose_geometry, kind='lower')
        else:
            cloth, x, y = _place_overlay_from_pose(human, cloth, pose_geometry, kind='upper')

        out = Image.new('RGBA', human.size)
        out.paste(human, (0, 0))
        out.paste(cloth, (x, y), cloth)
        out = out.convert('RGB')
        
        filename = f"virtual_tryon_fallback_{int(time.time()*1000)}.png"
        path = os.path.join(GENERATED_FOLDER, filename)
        out.save(path, format='PNG')
        
        return {'success': True, 'note': 'local_fallback', 'file': filename, 'image': _image_to_datauri(out)}
    except Exception as e:
        return {'success': False, 'error': 'local fallback failed', 'details': str(e)}


def local_fallback_combo(human_path, top_path, bottom_path):
    try:
        human = Image.open(human_path).convert('RGBA')
        top = Image.open(top_path).convert('RGBA')
        bottom = Image.open(bottom_path).convert('RGBA')
        pose_geometry = _detect_pose_geometry(human_path)
        top, top_x, top_y = _place_overlay_from_pose(human, top, pose_geometry, kind='upper')
        bottom, bottom_x, bottom_y = _place_overlay_from_pose(human, bottom, pose_geometry, kind='lower')
        out = Image.new('RGBA', human.size)
        out.paste(human, (0, 0))
        out.paste(top, (top_x, top_y), top)
        out.paste(bottom, (bottom_x, bottom_y), bottom)
        out = out.convert('RGB')

        filename = f"virtual_tryon_fallback_combo_{int(time.time()*1000)}.png"
        path = os.path.join(GENERATED_FOLDER, filename)
        out.save(path, format='PNG')

        return {'success': True, 'note': 'local_fallback', 'file': filename, 'image': _image_to_datauri(out)}
    except Exception as e:
        return {'success': False, 'error': 'local fallback failed', 'details': str(e)}

# ============= AUTH ROUTES =============

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    userid = data.get('userid')
    password = data.get('password')
    
    if not userid or not password:
        return jsonify({'success': False, 'message': 'UserID and password are required'}), 400

    db = get_db_session()
    try:
        existing_user = db.query(User).filter_by(userid=userid).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'UserID already exists'}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(userid=userid, password=hashed_password, role='USER')
        db.add(new_user)
        db.commit()

        profile = UserProfile(user_id=new_user.id)
        db.add(profile)
        db.commit()

        return jsonify({'success': True, 'message': 'Registration successful'})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': 'Registration failed', 'details': str(e)}), 500
    finally:
        db.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    userid = data.get('userid')
    password = data.get('password')
    
    if not userid or not password:
        return jsonify({'success': False, 'message': 'UserID and password are required'}), 400
    
    db = get_db_session()
    try:
        user = db.query(User).filter_by(userid=userid).first()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

        token = generate_token(user.id, user.userid)
        return jsonify({
            'success': True,
            'data': {
                'token': token,
                'userid': user.userid,
                'userId': user.id,
                'role': user.role
            }
        })
    finally:
        db.close()

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
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1]
        token_blacklist.add(token)
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
    data = request.get_json(silent=True) or {}
    
    db = get_db_session()
    try:
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
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': 'Profile update failed', 'details': str(e)}), 500
    finally:
        db.close()

# ============= VIRTUAL TRY-ON ROUTES =============

@app.route('/tryon', methods=['POST'])
@token_required
def tryon_single(current_user):
    app.logger.info("Try-on request received (legacy /tryon endpoint)")
    garment_type = request.form.get('garmentType', 'full_body')
    human_file = request.files.get('humanImage') or request.files.get('person_image')
    cloth_file = request.files.get('clothImage') or request.files.get('cloth_image')

    if not human_file or not cloth_file:
        return jsonify({'success': False, 'error': 'person_image/humanImage and cloth_image/clothImage required'}), 400

    if not is_allowed_image_file(human_file) or not is_allowed_image_file(cloth_file):
        return jsonify({'success': False, 'error': 'Invalid image (PNG/JPG/JPEG only, <=6MB)'}), 400

    human_path, cloth_path = _save_uploaded_images([('human', human_file), ('cloth', cloth_file)])
    try:
        result = local_fallback_single(human_path, cloth_path, garment_type)
        return jsonify(result)
    finally:
        _cleanup_paths([human_path, cloth_path])


@app.route('/api/tryon/single', methods=['POST'])
@token_required
def api_tryon_single(current_user):
    garment_type = request.form.get('garmentType', 'full_body')
    human_file = request.files.get('humanImage') or request.files.get('person_image')
    cloth_file = request.files.get('clothImage') or request.files.get('cloth_image')

    if not human_file or not cloth_file:
        return jsonify({'success': False, 'error': 'humanImage and clothImage are required'}), 400

    if not is_allowed_image_file(human_file) or not is_allowed_image_file(cloth_file):
        return jsonify({'success': False, 'error': 'Invalid image file type (PNG/JPEG only)'}), 400

    human_path, cloth_path = _save_uploaded_images([('human', human_file), ('cloth', cloth_file)])
    try:
        result = local_fallback_single(human_path, cloth_path, garment_type)
        return jsonify(result)
    finally:
        _cleanup_paths([human_path, cloth_path])


@app.route('/api/tryon/combo', methods=['POST'])
@token_required
def tryon_combo(current_user):
    human_file = request.files.get('humanImage')
    top_file = request.files.get('clothImage')
    bottom_file = request.files.get('bottomClothImage')

    if not human_file or not top_file or not bottom_file:
        return jsonify({'success': False, 'error': 'humanImage, clothImage, bottomClothImage are required'}), 400

    if not is_allowed_image_file(human_file) or not is_allowed_image_file(top_file) or not is_allowed_image_file(bottom_file):
        return jsonify({'success': False, 'error': 'Invalid image file type (PNG/JPEG only)'}), 400

    human_path, top_path, bottom_path = _save_uploaded_images([
        ('human', human_file),
        ('top', top_file),
        ('bottom', bottom_file),
    ])

    try:
        result = local_fallback_combo(human_path, top_path, bottom_path)
        return jsonify(result)
    finally:
        _cleanup_paths([human_path, top_path, bottom_path])

# ============= OUTFIT GENERATOR ROUTES =============

@app.route('/api/outfit/generate', methods=['POST'])
@token_required
def generate_outfit(current_user):
    data = request.get_json(silent=True) or {}
    style = data.get('style', 'casual')
    occasion = data.get('occasion', 'casual')
    gender = data.get('gender', 'female')
    season = data.get('season')
    color_preference = data.get('colorPreference')

    outfit = generate_outfit_with_gemini(style, occasion, gender, season, color_preference)

    if not outfit:
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
    try:
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
    
    finally:
        db.close()

    return jsonify({
        'success': True,
        'data': {'outfits': outfits_data}
    })

@app.route('/api/gallery/save', methods=['POST'])
@token_required
def save_to_gallery(current_user):
    data = request.get_json(silent=True) or {}
    
    db = get_db_session()
    try:
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
        return jsonify({'success': True, 'message': 'Outfit saved to gallery'})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': 'Failed to save outfit', 'details': str(e)}), 500
    finally:
        db.close()

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
    try:
        limit = int(request.args.get('limit', 20))
    except (TypeError, ValueError):
        limit = 20
    
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
    data = request.get_json(silent=True) or {}
    
    db = get_db_session()
    try:
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
        return jsonify({'success': True, 'message': 'History saved'})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': 'Failed to save history', 'details': str(e)}), 500
    finally:
        db.close()

# ============= CONTACT ROUTES =============

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')
    
    if not name or not email or not message:
        return jsonify({'success': False, 'error': 'All fields are required'}), 400
    
    db = get_db_session()
    try:
        new_message = ContactMessage(name=name, email=email, message=message)
        db.add(new_message)
        db.commit()
        return jsonify({'success': True, 'message': 'Message sent successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': 'Failed to submit contact', 'details': str(e)}), 500
    finally:
        db.close()

# ============= ADMIN ROUTES =============

@app.route('/api/admin/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    if current_user.role != 'ADMIN':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    db = get_db_session()
    try:
        users = db.query(User).all()
        user_data = []
        for user in users:
            profile = db.query(UserProfile).filter_by(user_id=user.id).first()
            user_data.append({
                'id': user.id,
                'userid': user.userid,
                'role': user.role,
                'name': profile.name if profile else '',
                'email': profile.email if profile else '',
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        return jsonify({'success': True, 'data': {'users': user_data}})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to get users', 'details': str(e)}), 500
    finally:
        db.close()

@app.route('/api/admin/outfits', methods=['GET'])
@token_required
def get_all_outfits(current_user):
    if current_user.role != 'ADMIN':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    db = get_db_session()
    try:
        outfits = db.query(Outfit).all()
        outfit_data = []
        for outfit in outfits:
            outfit_data.append({
                'id': outfit.id,
                'user_id': outfit.user_id,
                'outfit_name': outfit.outfit_name,
                'style': outfit.style,
                'occasion': outfit.occasion,
                'gender': outfit.gender,
                'season': outfit.season,
                'created_at': outfit.created_at.isoformat() if outfit.created_at else None
            })
        return jsonify({'success': True, 'data': {'outfits': outfit_data}})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to get outfits', 'details': str(e)}), 500
    finally:
        db.close()

@app.route('/api/admin/history', methods=['GET'])
@token_required
def get_all_history(current_user):
    if current_user.role != 'ADMIN':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    db = get_db_session()
    try:
        history = db.query(TryOnHistory).all()
        history_data = []
        for h in history:
            history_data.append({
                'id': h.id,
                'user_id': h.user_id,
                'garment_type': h.garment_type,
                'result_image_url': h.result_image_url,
                'created_at': h.created_at.isoformat() if h.created_at else None
            })
        return jsonify({'success': True, 'data': {'history': history_data}})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to get history', 'details': str(e)}), 500
    finally:
        db.close()

# ============= HEALTH CHECK =============

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'gemini': bool(GEMINI_API_KEY),
        'gemini_api_key_loaded': bool(GEMINI_API_KEY),
        'tryon_provider': 'local'
    })

# ============= STATIC FILE ROUTES =============

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('api/'):
        return not_found(None)
    full_path = os.path.join(app.static_folder, path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return send_from_directory(app.static_folder, path)
    elif os.path.exists(full_path + '.html'):
        return send_from_directory(app.static_folder, path + '.html')
    else:
        return send_from_directory(app.static_folder, 'index.html')

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

