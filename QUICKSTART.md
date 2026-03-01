# FitFinder Java - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Install Prerequisites
```bash
# Check Java version (need 17+)
java -version

# Check Maven
mvn -version
```

If not installed, download:
- **JDK 17+**: https://adoptium.net/
- **Maven 3.8+**: https://maven.apache.org/

### Step 2: Clone/Extract Project
```bash
cd FITFINDER-JAVA
```

### Step 3: Build Project
```bash
mvn clean install
```

### Step 4: Run Application
```bash
mvn spring-boot:run
```

Or:
```bash
mvn package
java -jar target/fitfinder-java-1.0.0.jar
```

### Step 5: Access Application
- **Application**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health
- **H2 Console**: http://localhost:5000/h2-console

---

## 🔓 Default Credentials

```
Username: admin123
Password: Secret@123
```

---

## 🌐 API Quick Reference

### Login
```bash
curl -X POST http://localhost:5000/login \
  -d "userid=admin123&password=Secret@123"
```

### Single Try-On
```bash
curl -X POST http://localhost:5000/api/tryon/single \
  -F "humanImage=@human.jpg" \
  -F "clothImage=@cloth.jpg" \
  -F "garmentType=full_body"
```

### Combo Try-On
```bash
curl -X POST http://localhost:5000/api/tryon/combo \
  -F "humanImage=@human.jpg" \
  -F "clothImage=@top.jpg" \
  -F "bottomClothImage=@bottom.jpg"
```

### Health Check
```bash
curl http://localhost:5000/api/health
```

---

## 🗄️ Database Setup

### H2 Console Access
1. Navigate to: http://localhost:5000/h2-console
2. Connection URL: `jdbc:h2:file:./users`
3. Username: `sa`
4. Password: (leave blank)

### PostgreSQL Setup
```properties
# In application.properties:
spring.jpa.database-platform=org.hibernate.dialect.PostgreSQL10Dialect
spring.datasource.url=jdbc:postgresql://localhost:5432/fitfinder
spring.datasource.username=postgres
spring.datasource.password=your_password
spring.datasource.driver-class-name=org.postgresql.Driver
```

---

## 🔑 Environment Variables

```bash
# Linux/Mac
export MIRAGIC_API_KEY=your_api_key_here

# Windows PowerShell
$env:MIRAGIC_API_KEY = "your_api_key_here"

# Windows CMD
set MIRAGIC_API_KEY=your_api_key_here
```

---

## 📦 Project Structure Overview

```
src/main/java/com/fitfinder/
├── FitFinderApplication.java    # Main class
├── controller/                   # REST endpoints
├── service/                      # Business logic
├── model/                        # Entities & DTOs
├── repository/                   # Data access
├── config/                       # Configuration
└── util/                         # Utilities
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in application.properties:
server.port=8080

# Or via command line:
java -jar target/fitfinder-java-1.0.0.jar --server.port=8080
```

### Database Locked
```bash
# Delete H2 database file
rm users.db*

# Restart application
mvn spring-boot:run
```

### Memory Issues
```bash
# Increase heap size
mvn spring-boot:run -Dspring-boot.run.jvmArguments="-Xmx1024m"
```

### Dependencies Not Found
```bash
# Clear Maven cache
mvn clean install -U
```

---

## 📝 Configuration Files

### application.properties
```properties
# Server
server.port=5000

# Database
spring.datasource.url=jdbc:h2:file:./users
spring.jpa.hibernate.ddl-auto=update

# File Upload (100MB max)
spring.servlet.multipart.max-file-size=100MB

# Miragic API (Optional)
miragic.api-key=${MIRAGIC_API_KEY:}
```

---

## 🧪 Testing

### Manual Testing
```bash
# 1. Start app
mvn spring-boot:run

# 2. Check health
curl http://localhost:5000/api/health

# 3. Login
curl -X POST http://localhost:5000/login \
  -d "userid=admin123&password=Secret@123"

# 4. Test try-on endpoint
curl -X POST http://localhost:5000/api/tryon/single \
  -F "humanImage=@test.jpg" \
  -F "clothImage=@cloth.jpg"
```

### Unit Tests (Create in src/test/java)
```java
@SpringBootTest
public class UserServiceTest {
    @Autowired
    private UserService userService;
    
    @Test
    public void testAuthentication() {
        Optional<User> user = userService.authenticate("admin123", "Secret@123");
        assertTrue(user.isPresent());
    }
}
```

---

## 📦 Building for Production

### Single JAR Deployment
```bash
# Build
mvn clean package -DskipTests

# Run
java -jar target/fitfinder-java-1.0.0.jar
```

### Docker Build
```bash
# Build image
docker build -t fitfinder:latest .

# Run container
docker run -p 5000:5000 \
  -e MIRAGIC_API_KEY=your_key \
  fitfinder:latest
```

### Docker Compose
```bash
docker-compose up -d
```

---

## 📂 File Organization

After running, these folders are created:
```
FITFINDER-JAVA/
├── tmp/                      # Temporary uploaded images
├── generated_outfits/        # Generated try-on results
├── users.db                  # H2 database file
└── users.trace.db            # H2 trace file
```

---

## 🎯 Next Steps

1. **Secure Administration**: Change default admin password
2. **API Integration**: Set MIRAGIC_API_KEY for AI features
3. **Database Migration**: Move to PostgreSQL for production
4. **Frontend Enhancement**: Customize HTML/CSS in `src/main/webapp/static/`
5. **Authentication**: Implement JWT tokens
6. **Monitoring**: Add Spring Boot Actuator

---

## 📞 Support

### Common Issues

| Issue | Solution |
|-------|----------|
| Port 5000 in use | Change `server.port` in properties |
| Database error | Delete `users.db*` files and restart |
| Login fails | Use `admin123` / `Secret@123` |
| Images not processing | Check file permissions in `tmp/` and `generated_outfits/` |

### Useful Resources
- Spring Boot Docs: https://spring.io/projects/spring-boot
- Maven Docs: https://maven.apache.org/
- H2 Database: https://www.h2database.com/

