# Build Stage
FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /build

# Copy project files
COPY pom.xml .
COPY src ./src

# Build application
RUN mvn clean package -DskipTests

# Runtime Stage
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# Copy JAR from builder
COPY --from=builder /build/target/fitfinder-java-1.0.0.jar app.jar

# Create necessary directories
RUN mkdir -p /app/tmp /app/generated_outfits

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/api/health || exit 1

# Runtime configuration
ENV SERVER_PORT=8080
ENV JAVA_OPTS="-Xmx512m -Xms256m"

# Run application
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
