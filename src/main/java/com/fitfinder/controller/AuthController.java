package com.fitfinder.controller;

import com.fitfinder.model.ApiResponse;
import com.fitfinder.model.User;
import com.fitfinder.service.UserService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * Authentication Controller - Handles user login, logout, and session management
 */
@Controller
@RequiredArgsConstructor
@Slf4j
public class AuthController {
    
    private final UserService userService;
    
    /**
     * Login endpoint - Authenticates user and creates session
     * Supports both form-based and JSON requests
     */
    @PostMapping("/login")
    public ResponseEntity<?> login(
            @RequestParam(required = false) String userid,
            @RequestParam(required = false) String password,
            HttpSession session) {
        
        log.info("Login attempt for user: {}", userid);
        
        if (userid == null || userid.isEmpty() || password == null || password.isEmpty()) {
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error("Invalid request", "User ID and password are required"));
        }
        
        Optional<User> user = userService.authenticate(userid, password);
        
        if (user.isPresent()) {
            session.setAttribute("user", userid);
            log.info("User logged in successfully: {}", userid);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Login successful");
            
            return ResponseEntity.ok(response);
        } else {
            log.warn("Login failed for user: {}", userid);
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(ApiResponse.error("Invalid credentials", "User ID or password is incorrect"));
        }
    }
    
    /**
     * Logout endpoint - Invalidates user session
     */
    @GetMapping("/logout")
    public ResponseEntity<?> logout(HttpSession session) {
        String userid = (String) session.getAttribute("user");
        if (userid != null) {
            log.info("User logged out: {}", userid);
            session.invalidate();
        }
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "Logout successful");
        
        return ResponseEntity.ok(response);
    }
    
    /**
     * Check authentication status
     */
    @GetMapping("/api/auth/status")
    public ResponseEntity<?> authStatus(HttpSession session) {
        String userid = (String) session.getAttribute("user");
        
        Map<String, Object> response = new HashMap<>();
        response.put("authenticated", userid != null);
        if (userid != null) {
            response.put("userid", userid);
        }
        
        return ResponseEntity.ok(response);
    }
    
    /**
     * Register new user (optional, for testing)
     */
    @PostMapping("/api/auth/register")
    public ResponseEntity<?> register(
            @RequestParam String userid,
            @RequestParam String password) {
        
        log.info("Register attempt for user: {}", userid);
        
        if (userid == null || userid.isEmpty() || password == null || password.isEmpty()) {
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error("Invalid request", "User ID and password are required"));
        }
        
        try {
            User newUser = userService.registerUser(userid, password);
            log.info("User registered successfully: {}", userid);
            
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(ApiResponse.success("User registered successfully"));
        } catch (IllegalArgumentException e) {
            log.warn("Registration failed: {}", e.getMessage());
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error("Registration failed", e.getMessage()));
        }
    }
}
