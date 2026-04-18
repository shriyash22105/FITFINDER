# FitFinder Project Structure

## Overview
Professional project organization with clean separation of concerns.

## Root Directory Files
```
app.py                  - Main Flask application (all API routes)
init_db.py             - Database initialization script
requirements.txt       - Python dependencies (pinned versions)
railway.json          - Railway.app deployment configuration
README.md             - Main project documentation
.env                  - Environment variables (secrets not in git)
.gitignore            - Git ignore rules
```

## Directories

### `/src/` - Source Code & Frontend
- `main/resources/static/` - HTML frontend files
  - `index.html` - Landing page
  - `login.html` - User login page
  - `register.html` - User registration page
  - `dashboard.html` - User dashboard
  - `outfit-generator.html` - Outfit generation interface
  - `tryon.html` - Virtual try-on interface
  - `gallery.html` - Saved outfits gallery
  - `profile.html` - User profile page
  - `about.html` - About page
  - `contact.html` - Contact page

### `/tests/` - Test Suite
- `test_api.py` - Comprehensive API test suite
  - Health check tests
  - Authentication tests (login, logout, token refresh)
  - Profile management tests
  - Outfit generation tests
  - Virtual try-on tests
  - Gallery and history tests
  - Contact form tests

### `/docs/` - Documentation
- `API_DOCUMENTATION.md` - Full API endpoint reference
- `PROJECT_SYNOPSIS.md` - Project overview and goals
- `ARCHITECTURE.md` - System architecture and data flow
- `SECURITY.md` - Security measures and hardening
- `INDEX.md` - Documentation index
- `TODO.md` - Project tasks and roadmap

### `/config/` - Configuration Files
- `railway.json` - Cloud deployment config (can be moved here)
- `.env.template` - Environment variables template

### `/_junk/` - Legacy & Unused Items
Legacy files kept for reference but not used:
- `diagrams2/` - Old UML/system diagrams
- `target/` - Maven build artifacts (Java era)
- `uploads/` - Old upload directory
- `generated_outfits/` - Legacy generated files
- `tmp/` - Temporary directory cache
- `__pycache__/` - Python bytecode cache
- `*.db` files - Local development databases (auto-recreatable)
- System artifacts: `nul`, `stop`
- Test images: `test_cloth.jpg`, `test_person.jpg`

### `/.venv/` - Virtual Environment
Python virtual environment (not committed to git)

### `/.git/` - Version Control
Git repository files

### `/.vscode/` - Editor Config
VS Code workspace settings and extensions

## Key Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login (returns JWT)
- `POST /api/auth/logout` - User logout (blacklists token)
- `POST /api/auth/refresh` - Refresh JWT token (7-day expiry)

### Profile
- `GET /api/profile` - Get user profile
- `PUT /api/profile/update` - Update profile information

### Outfit Generation
- `POST /api/outfit/generate` - Generate outfit recommendations

### Virtual Try-On
- `POST /api/tryon/single` - Try-on single garment
- `POST /api/tryon/combo` - Try-on top + bottom combo
- `GET /api/tryon/jobs/:job_id` - Poll try-on job status

### Gallery
- `GET /api/gallery` - Get saved outfits
- `POST /api/gallery/save` - Save outfit to gallery

### History
- `GET /api/history` - Get try-on history
- `POST /api/history/save` - Save try-on result

### Other
- `GET /api/health` - API health check
- `POST /api/contact` - Contact form submission

## Running Tests

```bash
# Install requirements (already done)
pip install -r requirements.txt

# Run API test suite
python tests/test_api.py
```

## Database

Default: SQLite (`fitfinder.db`)
- User credentials: userid=`admin123`, password=`Secret@123`
- Auto-initialized from `init_db.py`

Production: PostgreSQL (configure in `.env`)

## Security Features

✅ JWT authentication (7-day expiry)
✅ Password hashing with bcrypt
✅ CORS enabled (configurable)
✅ File upload validation (PNG/JPEG only)
✅ Max upload size: 6MB
✅ Bearer token required for protected routes
✅ Token blacklisting on logout
✅ Database transaction safety with rollback
✅ Global error handlers (413, 404, 500)

## Development Setup

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate (Windows)
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python init_db.py

# 5. Run Flask app
python app.py

# 6. Access at http://localhost:5000
```

## Deployment

Railway.app configuration included in `railway.json`

```bash
# Deploy to Railway
railway up
```

---
**Last Updated**: Post-migration restructuring
**Status**: Production-ready
