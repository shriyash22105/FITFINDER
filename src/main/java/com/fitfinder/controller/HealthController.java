package com.fitfinder.controller;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

/**
 * Health Check Controller - Provides API health status
 */
@RestController
@RequestMapping("/api")
@Slf4j
public class HealthController {
    
    @Value("${miragic.api-key:}")
    private String miragicApiKey;
    
    /**
     * Health check endpoint
     * Returns API status and integration availability
     */
    @GetMapping("/health")
    public ResponseEntity<?> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "healthy");
        response.put("miragic", !miragicApiKey.isEmpty());
        response.put("timestamp", System.currentTimeMillis());
        
        log.debug("Health check requested");
        return ResponseEntity.ok(response);
    }
}
