# FitFinder - Python Flask Backend

This project has been migrated from Java Spring Boot to Python Flask backend while keeping the same PostgreSQL database schema.

## Features

- **AI Outfit Generator** - Generate fashion combinations with AI
- **Virtual Try-On** - Upload your photo and clothing to see how they look together
- **User Authentication** - Secure login/registration with JWT tokens
- **Gallery** - Save and manage your favorite outfits
- **Profile Management** - Update your style preferences

## Tech Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: JWT (JSON Web Tokens)

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL database and update the DATABASE_URL in app.py:
```python
DATABASE_URL = 'postgresql://username:password@localhost:5432/fitfinder'
```

Or set as environment variable:
```bash
export DATABASE_URL='postgresql://username:password@localhost:5432/fitfinder'
```

3. Initialize the database:
```bash
python init_db.py
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

### Default Login

- **UserID**: admin123
- **Password**: Secret@123

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user

### Profile
- `GET /api/profile` - Get user profile
- `PUT /api/profile/update` - Update user profile

### Virtual Try-On
- `POST /api/tryon/single` - Try on single garment
- `POST /api/tryon/combo` - Try on outfit combo (top + bottom)

### Outfit Generator
- `POST /api/outfit/generate` - Generate AI outfit

### Gallery
- `GET /api/gallery` - Get saved outfits
- `POST /api/gallery/save` - Save outfit to gallery
- `DELETE /api/gallery/<id>` - Delete saved outfit

### History
- `GET /api/history` - Get try-on history
- `GET /api/history/recent` - Get recent try-ons
- `POST /api/history/save` - Save try-on to history

### Contact
- `POST /api/contact` - Submit contact form

### Health
- `GET /api/health` - Health check

## Project Structure

```
FITFINDER-JAVA/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── init_db.py           # Database initialization
├── generated_outfits/   # Generated outfit images
├── tmp/                # Temporary upload files
└── src/main/resources/
    └── static/         # HTML, CSS, JS files
        ├── index.html
        ├── login page.html
        ├── register.html
        ├── dashboard.html
        ├── tryon.html
        ├── outfit-generator.html
        ├── contact.html
        └── about.html
```

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `MIRAGIC_API_KEY` - Optional: API key for advanced virtual try-on

## License

MIT License

