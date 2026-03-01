package com.fitfinder.controller;

import com.fitfinder.model.ApiResponse;
import com.fitfinder.service.VirtualTryOnService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

/**
 * Virtual Try-On Controller - Handles virtual try-on requests
 * Supports both single and combo garment try-ons
 */
@RestController
@RequestMapping("/api/tryon")
@RequiredArgsConstructor
@Slf4j
public class TryOnController {
    
    private final VirtualTryOnService tryOnService;
    
    @Value("${app.tmp-folder:tmp}")
    private String tmpFolder;
    
    @Value("${app.generated-folder:generated_outfits}")
    private String generatedFolder;
    
    /**
     * Single garment virtual try-on endpoint
     * POST /api/tryon/single
     */
    @PostMapping("/single")
    public ResponseEntity<?> trySingle(
            @RequestParam(required = false) String garmentType,
            @RequestParam(required = false) MultipartFile humanImage,
            @RequestParam(required = false) MultipartFile clothImage) {
        
        log.info("Single try-on request received with garment type: {}", garmentType);
        
        if (humanImage == null || clothImage == null) {
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error("humanImage and clothImage are required"));
        }
        
        if (garmentType == null || garmentType.isEmpty()) {
            garmentType = "full_body";
        }
        
        try {
            // Save temporary files
            String humanPath = saveTempFile(humanImage);
            String clothPath = saveTempFile(clothImage);
            
            // Process try-on
            ApiResponse<Object> result = tryOnService.processSingleTryOn(humanPath, clothPath, garmentType);
            
            // Clean up temporary files
            cleanupFile(humanPath);
            cleanupFile(clothPath);
            
            return ResponseEntity.ok(result);
        } catch (IOException e) {
            log.error("Error processing single try-on", e);
            return ResponseEntity.status(500)
                    .body(ApiResponse.error("Processing failed", e.getMessage()));
        }
    }
    
    /**
     * Combo garment virtual try-on endpoint
     * POST /api/tryon/combo
     */
    @PostMapping("/combo")
    public ResponseEntity<?> tryCombo(
            @RequestParam(required = false) String garmentType,
            @RequestParam(required = false) MultipartFile humanImage,
            @RequestParam(required = false) MultipartFile clothImage,
            @RequestParam(required = false) MultipartFile bottomClothImage) {
        
        log.info("Combo try-on request received with garment type: {}", garmentType);
        
        if (humanImage == null || clothImage == null || bottomClothImage == null) {
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error("humanImage, clothImage, and bottomClothImage are required"));
        }
        
        if (garmentType == null || garmentType.isEmpty()) {
            garmentType = "comb";
        }
        
        try {
            // Save temporary files
            String humanPath = saveTempFile(humanImage);
            String topPath = saveTempFile(clothImage);
            String bottomPath = saveTempFile(bottomClothImage);
            
            // Process try-on
            ApiResponse<Object> result = tryOnService.processComboTryOn(humanPath, topPath, bottomPath, garmentType);
            
            // Clean up temporary files
            cleanupFile(humanPath);
            cleanupFile(topPath);
            cleanupFile(bottomPath);
            
            return ResponseEntity.ok(result);
        } catch (IOException e) {
            log.error("Error processing combo try-on", e);
            return ResponseEntity.status(500)
                    .body(ApiResponse.error("Processing failed", e.getMessage()));
        }
    }
    
    /**
     * Save uploaded file to temporary folder
     */
    private String saveTempFile(MultipartFile file) throws IOException {
        // Use system temp directory for reliability
        Path tmpDir = Paths.get(System.getProperty("java.io.tmpdir"), "fitfinder", "uploads");
        Files.createDirectories(tmpDir);
        
        String filename = file.getOriginalFilename();
        String timestamp = Long.toString(Instant.now().toEpochMilli());
        String uniqueFilename = timestamp + "_" + filename;
        
        Path tempFile = tmpDir.resolve(uniqueFilename);
        file.transferTo(tempFile.toFile());
        
        log.debug("Temporary file saved: {}", tempFile.toAbsolutePath());
        return tempFile.toAbsolutePath().toString();
    }
    
    /**
     * Clean up temporary file
     */
    private void cleanupFile(String filePath) {
        try {
            File file = new File(filePath);
            if (file.exists()) {
                if (file.delete()) {
                    log.debug("Temporary file deleted: {}", filePath);
                }
            }
        } catch (Exception e) {
            log.warn("Failed to delete temporary file: {}", filePath, e);
        }
    }
}
