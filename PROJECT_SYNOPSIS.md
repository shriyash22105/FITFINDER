# PROJECT SYNOPSIS

---

## GROUP MEMBERS:

### 1. Name of the student: _________________________________  
Roll No: _________________________________

### 2. Name of the student: _________________________________
Roll No: _________________________________

### 3. Name of the student: _________________________________
Roll No: _________________________________

---

## CLASS: _________________________________

---

## PROJECT TITLE:
# **FitFinder - AI-Powered Fashion Virtual Try-On Assistant**

---

## PROJECT DESCRIPTION IN BRIEF (Problem Definition):

**Problem Statement:**
The fashion industry lacks intelligent solutions that enable customers to visualize clothing on themselves before purchase. Customers often struggle with:
- Uncertainty about how clothes will look on their body type
- High return rates due to poor fit visualization
- Inability to view multiple outfit combinations quickly
- Time-consuming shopping experience
- Limited personalized outfit recommendations

**Solution:**
FitFinder is an AI-powered web application that provides:
1. **Virtual Try-On System** - Upload user photo and clothing images to see realistic visualization of garments on the user
2. **AI Outfit Generator** - Generate personalized outfit combinations based on occasion, style preferences, and gender
3. **Dual Processing Strategy** - Integrates with Miragic AI API for premium results with local fallback for reliability
4. **User Authentication** - Secure login system with password encryption
5. **Responsive Web Interface** - Beautiful, intuitive UI for seamless user experience

**Key Benefits:**
- Reduces return rates and customer dissatisfaction
- Increases customer confidence in online purchases
- Saves time by providing instant styling recommendations
- Provides realistic visualization before purchase commitment
- Improves overall shopping experience

---

## TECHNOLOGY USED (S/W and H/W Requirements):

### Software Requirements:

**Backend Stack:**
- **Framework**: Spring Boot 3.1.5 (Java 17)
- **Database**: 
  - Development: H2 Database (in-memory/file-based)
  - Production: PostgreSQL 15+
- **ORM**: Spring Data JPA with Hibernate
- **Security**: Spring Security with BCrypt Password Encoding
- **HTTP Client**: OkHttp 4.11.0
- **JSON Processing**: Gson 2.10.1
- **Build Tool**: Maven 3.8+
- **Logging**: SLF4J with Logback

**Frontend Stack:**
- **Languages**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Responsive CSS with Flexbox/Grid
- **HTTP**: Fetch API for REST calls
- **UI Framework**: Custom vanilla JavaScript (no dependencies)

**External APIs:**
- **Miragic AI API** - Virtual try-on processing (Optional with fallback)
  - Single garment try-on
  - Combo garment try-on
  - Job polling mechanism

**Containerization & Deployment:**
- **Docker**: Multi-stage builds with Alpine base
- **Docker Compose**: Full-stack orchestration
- **Nginx**: Reverse proxy (optional)
- **Cloud**: AWS, Azure, GCP compatible

**Development Tools:**
- **IDE**: IntelliJ IDEA / VS Code
- **Version Control**: Git
- **CI/CD**: GitHub Actions (optional)

### Hardware Requirements:

**Minimum Development Configuration:**
| Component | Specification |
|-----------|---------------|
| **Processor** | Intel i5 / AMD Ryzen 5 or equivalent (2+ cores) |
| **RAM** | 8 GB minimum (16 GB recommended) |
| **Storage** | 10 GB free space (SSD recommended) |
| **Network** | Internet connection (min 1 Mbps) |

**Minimum Production Configuration:**
| Component | Specification |
|-----------|---------------|
| **Processor** | 2+ vCPU cores |
| **RAM** | 4 GB minimum (8 GB recommended for 100+ concurrent users) |
| **Storage** | 50 GB (depends on image storage needs) |
| **Network** | High-speed internet, static IP for API access |

**Optional Hardware:**
- GPU (for local image processing acceleration)
- Load Balancer (for distributed deployment)
- CDN (for static asset delivery)

---

## MODULE DETAILS:

### 1. USER DETAILS:

#### User Roles:
1. **End Users** - Fashion shoppers who use the try-on and outfit generation features
2. **System Administrators** - Manage system health, monitor API usage, handle configurations

#### User Personas:
| Persona | Description |
|---------|-------------|
| **Fashion Conscious Shopper** | Primary target - Age 18-40, comfort-seeking, style-aware |
| **Online Buyer** | Secondary target - Prefers online shopping, seeks confidence in purchases |
| **Style Explorer** | Tertiary target - Looking for outfit inspiration and recommendations |

#### User Access Levels:
- **Anonymous**: View home, about, contact pages
- **Authenticated**: Access try-on tool, outfit generator, dashboard
- **Admin**: System monitoring, configuration management

#### User Data Stored:
- `userid` (username/login ID)
- `password` (BCrypt hashed)
- `created_at` (registration timestamp)
- Session information (temporary)

---

### 2. FUNCTIONAL DETAILS:

#### 2.1 Authentication Module

**Function**: User login, logout, and session management

**Features**:
- User registration with userid and password
- Secure BCrypt password hashing (12 rounds)
- Login validation with exact credential matching
- Session management using HTTP sessions
- Logout with session invalidation
- Auth status check endpoint

**User Flows**:

**Login Flow:**
```
1. User enters userid and password
2. System validates credentials via UserService
3. If valid: Create HTTP session, redirect to dashboard
4. If invalid: Display error message
5. Session expires after inactivity (30 min default)
```

**Registration Flow:**
```
1. User provides userid and password
2. System checks if userid already exists
3. If unique: Hash password with BCrypt
4. Store in database with created_at timestamp
5. Redirect to login page
6. Success message displayed
```

**Endpoints**:
- `POST /login` - Authenticate user
- `POST /logout` - Invalidate session
- `GET /api/auth/status` - Check authentication status
- `POST /api/auth/register` - Create new user account

---

#### 2.2 Virtual Try-On Module

**Function**: Process images for virtual garment try-on

**Features**:
- Upload user photo (human image)
- Upload clothing image(s)
- Single garment try-on (top/bottom/dress)
- Combo garment try-on (top + bottom)
- Dual processing (Miragic AI or Local fallback)
- Image overlay and composition
- Result download capability

**Processing Workflow:**

**Single Try-On Process:**
```
1. User uploads human photo and garment image
2. System validates file formats (JPEG/PNG)
3. If Miragic API configured:
   - Upload to Miragic backend
   - Create try-on job
   - Poll job status every 2 seconds (max 60s timeout)
   - Retrieve result image
4. If API unavailable (fallback):
   - Process locally using Java AWT
   - Resize garment to 60% of human width
   - Position at 25% from top
   - Overlay on human image
   - Save as PNG
5. Return result to user
6. Clean up temporary files
```

**Combo Try-On Process:**
```
1. User uploads human photo, top clothing, bottom clothing
2. System validates all files
3. Processing via Miragic or Local:
   - Overlay top at 20% from top
   - Overlay bottom at 55% from top
   - Create natural-looking combination
4. Return composite result
5. Delete temporary files
```

**Local Image Processing (Fallback):**
- Uses Java AWT (java.awt package)
- BufferedImage for image manipulation
- Graphics2D for drawing and composition
- ImageIO for file I/O (JPEG, PNG support)
- Image resizing with aspect ratio preservation
- Transparent background support

**Endpoints**:
- `POST /api/tryon/single` - Process single garment try-on
- `POST /api/tryon/combo` - Process combo garment try-on

**Response Format**:
```json
{
  "success": true,
  "data": {
    "image": "base64_encoded_image",
    "processedAt": "2026-02-09T10:30:00",
    "processingTime": 2500
  },
  "message": "Try-on completed successfully",
  "note": "miragic_api | local_fallback"
}
```

---

#### 2.3 AI Outfit Generator Module

**Function**: Generate AI-powered outfit recommendations

**Features**:
- Scene selection (Casual, Work, Date Night, Workout, Formal, Party)
- Style preference (Minimalist, Vintage, Streetwear, Comfort, Bohemian, Artistic)
- Gender selection (Female, Male, Unisex)
- AI-powered generation (Miragic API integration)
- Local fallback for demo purposes
- Visual outfit display

**Outfit Generation Flow:**
```
1. User selects scene, style, gender
2. System builds prompt: "Generate {gender} outfit for {scene} in {style}"
3. Send to Miragic AI API with parameters
4. Receive generated outfit image
5. Display result with metadata
6. Option to regenerate with different parameters
```

**Parameter Combinations**:
- Scenes: 6 options
- Styles: 6 options
- Genders: 3 options
- Total combinations: 108 unique outfit possibilities

**Endpoints**:
- `POST /api/generate-outfit` - Generate AI outfit

**Request Format**:
```json
{
  "scene": "casual",
  "style": "minimalist",
  "gender": "female"
}
```

---

#### 2.4 Health Check Module

**Function**: Monitor system health and API availability

**Features**:
- Application status check
- Miragic API availability verification
- Database connectivity check
- System uptime information
- Timestamp for health check

**Endpoints**:
- `GET /api/health` - System health status

**Response Format**:
```json
{
  "status": "UP",
  "services": {
    "miragic_api": "AVAILABLE",
    "database": "CONNECTED"
  },
  "timestamp": "2026-02-09T10:30:00Z",
  "uptime": 3600000
}
```

---

#### 2.5 Static Content & Frontend Module

**Function**: Serve web pages and handle client-side interactions

**Static Pages**:

| Page | Purpose |
|------|---------|
| **index.html** | Home page with navigation and tool showcase |
| **login.html** | User login interface |
| **dashboard.html** | Post-login dashboard |
| **tryon.html** | Virtual try-on interface |
| **outfit-generator.html** | AI outfit generation interface |
| **about.html** | Project information page |
| **contact.html** | Contact form and company info |

**Frontend Features**:
- Responsive design (mobile, tablet, desktop)
- Real-time image preview
- Loading spinners and status messages
- Error handling and validation
- File upload with drag-and-drop
- Session management JavaScript
- API integration via Fetch

---

#### 2.6 Database Module

**Function**: Persist and retrieve user data

**Database Schema**:

**USERS Table:**
```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    userid VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_userid (userid)
);
```

**Key Operations**:
- Create user (registration)
- Read user (authentication lookup)
- Update user (profile changes - future feature)
- Delete user (account deletion - future feature)

**Indices**: 
- Primary Key: `id`
- Unique Index: `userid` (for fast authentication)
- Regular Index: `created_at` (for date-based queries)

---

#### 2.7 Security Module

**Function**: Protect user data and system integrity

**Security Features**:

1. **Password Security**:
   - BCrypt hashing with 12 salt rounds
   - Algorithm: BCRYPT
   - No plaintext storage
   - Salted hash verification

2. **Session Management**:
   - HTTP Session-based authentication
   - Session timeout: 30 minutes (configurable)
   - Session invalidation on logout
   - SessionID in browser cookies

3. **CORS Configuration**:
   - Allow all origins (development)
   - Restrict to specific domains (production)
   - All HTTP methods enabled
   - All headers allowed

4. **Input Validation**:
   - File type validation (JPEG, PNG only)
   - File size limits (10MB per image)
   - String length constraints
   - SQL injection prevention via JPA

5. **API Security**:
   - X-API-Key header for Miragic API authentication
   - HTTPS enforcement (production)
   - Rate limiting (future feature)
   - API key rotation (future feature)

---

### 2.8 System Architecture Overview

```
USER INTERFACE (HTML/CSS/JavaScript)
        ↓
REST CONTROLLERS (AuthController, TryOnController, HealthController)
        ↓
BUSINESS LOGIC (UserService, VirtualTryOnService)
        ↓
DATA ACCESS (UserRepository, Database)
        ↓
EXTERNAL SERVICES (Miragic AI API - optional)
```

---

### 2.9 Integration Points

**External Integrations**:

1. **Miragic AI API**:
   - Base URL: `https://backend.miragic.ai`
   - Authentication: X-API-Key header
   - Endpoints: /upload, /process, /check_job_status
   - Polling: Every 2 seconds, max 60 seconds

2. **File System**:
   - Temporary folder: `/tmp`
   - Output folder: `/generated_outfits`
   - Auto-cleanup after processing

3. **Database**:
   - H2 (development)
   - PostgreSQL (production)
   - Connection pooling: HikariCP

---

### 2.10 Error Handling & Recovery

**Error Scenarios**:

| Error | Cause | Resolution |
|-------|-------|-----------|
| **Invalid credentials** | Wrong userid/password | Retry login |
| **User exists** | Duplicate userid | Choose different username |
| **API timeout** | Miragic delayed response | Use local fallback |
| **File size exceeded** | Image > 10MB | Upload smaller image |
| **Invalid file type** | Non-image format | Upload JPEG/PNG only |
| **DB connection** | Database unavailable | System unavailable page |

**Fallback Mechanisms**:
- Miragic API → Local image processing
- PostgreSQL → H2 database
- External assets → CDN → Local cache

---

## TECHNICAL WORKFLOW SUMMARY:

### User Registration & Login:
1. User enters credentials on login page
2. System validates vs. database
3. BCrypt verification of password
4. Session created if valid
5. User redirected to dashboard

### Virtual Try-On Workflow:
1. User navigates to try-on page
2. Uploads human photo + garment image
3. Frontend validates files
4. Backend processes via Miragic or local
5. Result image returned
6. Temporary files deleted
7. User downloads result

### Outfit Generation Workflow:
1. User selects scene, style, gender
2. Frontend sends request to backend
3. Backend queries Miragic API
4. Generated image returned
5. User views result
6. Can regenerate or download

---

## PROJECT COMPLEXITY & SCOPE:

**Codebase Metrics**:
- Total Java Code: 925+ lines
- Total Documentation: 3,000+ lines
- Number of Classes: 9
- Number of Endpoints: 7
- UML Diagrams: 7
- Configuration Files: 3
- HTML Pages: 6

**Technology Layers**:
- Frontend (HTML/CSS/JS)
- REST API (Spring Boot)
- Business Logic (Services)
- Data Access (JPA/Hibernate)
- Database (SQL)
- External APIs (HTTP)

**Scalability Considerations**:
- Stateless REST architecture
- Connection pooling for database
- Async processing for long-running tasks (future)
- Caching layer (future)
- Load balancing ready
- Containerization support

---

## FUTURE ENHANCEMENTS:

1. **User Features**:
   - Profile customization
   - Outfit history/favorites
   - Size preferences
   - Style quiz
   - Wishlist functionality

2. **AI Features**:
   - Multi-person try-on
   - Real-time video try-on
   - Body type detection
   - Color recommendation
   - Fabric texture preview

3. **Technical Features**:
   - JWT authentication
   - OAuth2 integration
   - Email notifications
   - Push notifications
   - Payment integration
   - AR try-on (mobile)

4. **Performance**:
   - Image caching
   - CDN integration
   - API rate limiting
   - Database query optimization
   - Background job processing

5. **Analytics**:
   - User engagement tracking
   - Try-on success metrics
   - Popular styles/scenes
   - Conversion analysis

---

## DEPLOYMENT OPTIONS:

1. **Standalone JAR**: Embedded Tomcat, suitable for small-scale
2. **Docker Container**: Containerized deployment for cloud
3. **Docker Compose**: Full-stack with PostgreSQL and services
4. **Kubernetes**: Enterprise-grade orchestration
5. **Cloud Platforms**: AWS (EC2/ECS), Azure (App Service), GCP (Cloud Run)

---

## TESTING & VALIDATION:

**Functional Testing**:
- ✓ User authentication (login/logout)
- ✓ Image upload and validation
- ✓ Try-on processing (local and API)
- ✓ Outfit generation
- ✓ Error handling

**Non-Functional Testing** (Ready for implementation):
- Unit tests (UserService, VirtualTryOnService)
- Integration tests (Controllers)
- Performance tests (Load testing)
- Security tests (SQL injection, XSS)

---

## CONCLUSION:

FitFinder is a comprehensive, production-ready AI-powered fashion application that bridges the gap between online shopping and in-store try-on experience. By leveraging modern Java Spring Boot architecture, AI integration (Miragic API), and responsive web design, FitFinder provides an innovative solution to the fashion e-commerce industry.

The system demonstrates strong software engineering practices including:
- ✅ Clean code architecture (3-layer design)
- ✅ Security best practices (BCrypt, session management)
- ✅ Error handling and fallback mechanisms
- ✅ Cloud-ready containerization
- ✅ Comprehensive documentation
- ✅ Scalable infrastructure support

---

## REFERENCES:

1. **Spring Boot Documentation**: https://spring.io/projects/spring-boot
2. **Spring Data JPA**: https://spring.io/projects/spring-data-jpa
3. **Miragic AI API**: https://www.miragic.ai
4. **PostgreSQL**: https://www.postgresql.org
5. **Docker**: https://www.docker.com
6. **MDN Web Docs**: https://developer.mozilla.org

---

**Signature of Student _________________________________**                      **Receiver's Signature _________________________________**

**Date: _________________________________**                                       **Date: _________________________________**

**Time: _________________________________**                                       **Time: _________________________________**

---
