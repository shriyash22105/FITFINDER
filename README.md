# FITFINDER Java Project - Complete Documentation

## 📋 Project Overview

**FitFinder** is an AI-powered virtual try-on and outfit generation platform converted from Python Flask to Java Spring Boot. The application allows users to:

- **User Authentication**: Secure login system with bcrypt password hashing
- **Virtual Try-On**: Single and combo garment virtual try-on using AI
- **Image Processing**: Local image manipulation fallback
- **Session Management**: User session tracking and authentication
- **REST API**: RESTful endpoints for all operations

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | Spring Boot 3.1.5 |
| **Language** | Java 17+ |
| **Database** | H2 (default) / PostgreSQL |
| **ORM** | Spring Data JPA + Hibernate |
| **Security** | Spring Security + BCrypt |
| **Image Processing** | Java AWT + ImageIO |
| **HTTP Client** | OkHttp 4.11.0 |
| **JSON Processing** | Gson 2.10.1 |
| **Build Tool** | Maven |

---

## 📁 Project Structure

```
FITFINDER-JAVA/
├── pom.xml                                    # Maven configuration
├── README.md                                  # Project documentation
├── ARCHITECTURE.md                            # Architecture documentation
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/fitfinder/
│   │   │       ├── FitFinderApplication.java         # Main entry point
│   │   │       ├── controller/
│   │   │       │   ├── AuthController.java           # Authentication endpoints
│   │   │       │   ├── TryOnController.java          # Virtual try-on endpoints
│   │   │       │   └── HealthController.java         # Health check endpoint
│   │   │       ├── service/
│   │   │       │   ├── UserService.java              # User business logic
│   │   │       │   └── VirtualTryOnService.java      # Try-on processing logic
│   │   │       ├── model/
│   │   │       │   ├── User.java                     # User entity
│   │   │       │   ├── TryOnRequest.java             # Single try-on DTO
│   │   │       │   ├── TryOnComboRequest.java        # Combo try-on DTO
│   │   │       │   └── ApiResponse.java              # Generic response wrapper
│   │   │       ├── repository/
│   │   │       │   └── UserRepository.java           # User data access
│   │   │       ├── config/
│   │   │       │   ├── SecurityConfig.java           # Security & CORS setup
│   │   │       │   └── DatabaseConfig.java           # Database initialization
│   │   │       └── util/
│   │   │           └── ImageProcessingUtil.java      # Image manipulation
│   │   ├── resources/
│   │   │   └── application.properties                # Configuration
│   │   └── webapp/
│   │       └── static/                               # HTML files (copied from original)
│   │           ├── index.html
│   │           ├── login_page.html
│   │           ├── dashboard.html
│   │           ├── about.html
│   │           ├── contact.html
│   │           ├── outfit-generator.html
│   │           └── tryon.html
│   └── test/java/                                    # Unit tests (to be added)
└── generated_outfits/                                # Generated images folder
```

---

## 🔧 Core Components

### 1. **Entity Model** (com.fitfinder.model)

#### User Entity
```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    Long id;
    
    @Column(unique = true, nullable = false)
    String userid;           // Username
    
    String password;         // BCrypt hashed password
    LocalDateTime createdAt; // Account creation time
}
```

#### DTOs
- `TryOnRequest`: Single garment try-on request
- `TryOnComboRequest`: Combo (top + bottom) garment try-on request
- `ApiResponse<T>`: Generic response wrapper for all API responses

### 2. **Repository Layer** (com.fitfinder.repository)

`UserRepository` extends `JpaRepository<User, Long>` providing:
- `findByUserid(String userid)`: Fetch user by ID
- `existsByUserid(String userid)`: Check user existence
- Standard CRUD operations

### 3. **Service Layer** (com.fitfinder.service)

#### UserService
- **authenticate()**: Verify user credentials against bcrypt hashed passwords
- **registerUser()**: Create new user with password encryption
- **getUserByUserid()**: Retrieve user information

#### VirtualTryOnService
- **processSingleTryOn()**: Handle single garment virtual try-on
- **processComboTryOn()**: Handle combo garment virtual try-on (top + bottom)
- **processMiragicSingleTryOn()**: Integration with Miragic AI API
- **processMiragicComboTryOn()**: Miragic composite garment processing
- **pollMiragicJob()**: Poll Miragic job status with timeout
- **processLocalSingleTryOn()**: Local fallback for single garment
- **processLocalComboTryOn()**: Local fallback for combo garments

### 4. **Controller Layer** (com.fitfinder.controller)

#### AuthController
- `POST /login`: User authentication
- `GET /logout`: Session invalidation
- `GET /api/auth/status`: Check authentication status
- `POST /api/auth/register`: User registration (optional)

#### TryOnController
- `POST /api/tryon/single`: Process single garment try-on
- `POST /api/tryon/combo`: Process combo garment try-on

#### HealthController
- `GET /api/health`: Health check and integration status

### 5. **Utility Layer** (com.fitfinder.util)

#### ImageProcessingUtil
- **createSingleTryOnImage()**: Overlay single cloth on human image
- **createComboTryOnImage()**: Overlay top and bottom on human image
- **resizeImage()**: Resize image to fit dimensions

### 6. **Configuration** (com.fitfinder.config)

#### SecurityConfig
- BCrypt password encoder configuration (12 rounds)
- CORS configuration for cross-origin requests

#### DatabaseConfig
- PostgreSQL/H2 database initialization
- Default admin user creation on startup

---

## 🔐 Authentication Flow

```
User Login Request
    ↓
AuthController.login()
    ↓
UserService.authenticate()
    ↓
BCrypt.verify(password)
    ↓
Session Created
    ↓
User Authenticated
```

### Authentication Details
- **Protected by**: Spring Security
- **Password Encoding**: BCrypt (12 rounds)
- **Session Storage**: Server-side (HttpSession)
- **Default Admin**: userid=`admin123`, password=`Secret@123`

---

## 📸 Virtual Try-On Flow

### Single Garment Flow
```
Upload (Human + Cloth Images)
    ↓
Save Temporary Files
    ↓
Check API Key
    │
    ├─ [API Key Available] → Miragic AI Processing
    │       ↓
    │   Create VTO Job
    │       ↓
    │   Poll Job Status (timeout: 60s)
    │       ↓
    │   Return Result
    │
    └─ [No API Key] → Local Fallback
            ↓
        JavaAWT Image Processing
            ↓
        Overlay Cloth on Human
            ↓
        Save as PNG
            ↓
        Return Result
    ↓
Cleanup Temporary Files
```

### Combo Garment Flow
```
Upload (Human + Top + Bottom Images)
    ↓
Save Temporary Files
    ↓
Check API Key
    │
    ├─ [API Key Available] → Miragic AI Processing
    │       ↓
    │   Create Combo VTO Job
    │       ↓
    │   Poll Job Status (timeout: 60s)
    │       ↓
    │   Return Result
    │
    └─ [No API Key] → Local Fallback
            ↓
        JavaAWT Image Processing
            ↓
        Overlay Top on Human (20% from top)
            ↓
        Overlay Bottom on Human (55% from top)
            ↓
        Save as PNG
            ↓
        Return Result
    ↓
Cleanup Temporary Files
```

---

## 🌐 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | User login |
| GET | `/logout` | User logout |
| GET | `/api/auth/status` | Check auth status |
| POST | `/api/auth/register` | Register new user |

### Virtual Try-On Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tryon/single` | Single garment try-on |
| POST | `/api/tryon/combo` | Combo garment try-on |

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    userid VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Default Admin User
```
userid: admin123
password: Secret@123 (bcrypt hashed)
```

---

## ⚙️ Configuration

### application.properties

```properties
# Server
server.port=5000

# Database (PostgreSQL default, can use H2)
spring.datasource.url=jdbc:postgresql://localhost:5432/fitfinder
spring.datasource.username=fitfinder_user
spring.datasource.password=fitfinder_password
spring.jpa.hibernate.ddl-auto=update

# Miragic API (optional)
miragic.api-key=${MIRAGIC_API_KEY:}
miragic.base-url=https://backend.miragic.ai

# File Upload
spring.servlet.multipart.max-file-size=100MB
spring.servlet.multipart.max-request-size=100MB

# Folders
app.tmp-folder=tmp
app.generated-folder=generated_outfits
```

### Environment Variables

```bash
# Miragic AI API Integration
export MIRAGIC_API_KEY=your_api_key_here

# Or in PowerShell:
$env:MIRAGIC_API_KEY = "your_api_key_here"
```

---

## 📦 Building & Running

### Prerequisites
- Java 17 or higher
- Maven 3.8+

### Build
```bash
mvn clean package
```

### Run
```bash
mvn spring-boot:run
```

Or after packaging:
```bash
java -jar target/fitfinder-java-1.0.0.jar
```

### With Custom Configuration
```bash
java -jar target/fitfinder-java-1.0.0.jar \
    --server.port=5000 \
    --miragic.api-key=your_key_here
```

---

## 🧪 Testing

### Test Endpoints with cURL

```bash
# Health check
curl http://localhost:5000/api/health

# Login
curl -X POST http://localhost:5000/login \
  -d "userid=admin123&password=Secret@123"

# Single try-on
curl -X POST http://localhost:5000/api/tryon/single \
  -F "humanImage=@human.jpg" \
  -F "clothImage=@cloth.jpg" \
  -F "garmentType=full_body"

# Combo try-on
curl -X POST http://localhost:5000/api/tryon/combo \
  -F "humanImage=@human.jpg" \
  -F "clothImage=@top.jpg" \
  -F "bottomClothImage=@bottom.jpg"
```

---

## 📝 Dependencies Conversion

| Python Package | Java Equivalent |
|----------------|-----------------|
| Flask | Spring Boot Web |
| Flask-CORS | Spring Web CORS |
| requests | OkHttp / WebClient |
| Pillow | Java AWT / ImageIO |
| SQLAlchemy | Spring Data JPA |
| passlib (bcrypt) | Spring Security Crypto |
| json | Gson |

---

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM maven:3.8.1-openjdk-17 AS builder
WORKDIR /build
COPY . .
RUN mvn clean package -DskipTests

FROM openjdk:17-slim
WORKDIR /app
COPY --from=builder /build/target/fitfinder-java-1.0.0.jar app.jar
EXPOSE 5000
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  fitfinder:
    build: .
    ports:
      - "5000:5000"
    environment:
      - MIRAGIC_API_KEY=${MIRAGIC_API_KEY}
    volumes:
      - ./generated_outfits:/app/generated_outfits
      - ./tmp:/app/tmp
```

---

## 🔄 Comparison: Python vs Java

| Aspect | Python (Flask) | Java (Spring Boot) |
|--------|---|---|
| **Framework** | Flask 3.0 | Spring Boot 3.1.5 |
| **Type Safety** | Dynamic | Strongly Typed |
| **Performance** | Medium | High |
| **Scalability** | Medium | Enterprise-Grade |
| **Memory** | Lower | Higher |
| **Development** | Rapid | Structured |
| **Testing** | Easier | Comprehensive |
| **Production** | Gunicorn/uWSGI | Embedded Tomcat |

---

## 📚 Additional Notes

### Error Handling
- All endpoints return standardized `ApiResponse` wrapper
- Errors include detailed messages for debugging
- Temporary files are cleaned up automatically

### Security Considerations
- Passwords hashed with BCrypt (12 rounds)
- CORS configured for all origins (should be restricted in production)
- Session cookies marked as HttpOnly

### Performance Optimization
- Connection pooling for database
- HTTP client connection pooling
- Image caching is not implemented but can be added
- Consider implementing Redis for session management

### Future Enhancements
- JWT token-based authentication
- Rate limiting
- File upload validation
- Advanced error logging
- Caching layer (Redis)
- WebSocket for real-time progress
- Swagger/OpenAPI documentation

