package com.fitfinder.service;

import com.fitfinder.model.ApiResponse;
import com.fitfinder.util.ImageProcessingUtil;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import okhttp3.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.time.Instant;
import java.util.concurrent.TimeUnit;

/**
 * VirtualTryOnService - Handles virtual try-on operations
 * Integrates with Miragic AI API or provides local fallback implementation
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class VirtualTryOnService {
    
    @Value("${miragic.api-key:}")
    private String miragicApiKey;
    
    @Value("${miragic.base-url:https://backend.miragic.ai}")
    private String miragicBaseUrl;
    
    @Value("${app.generated-folder:generated_outfits}")
    private String generatedFolder;
    
    private final OkHttpClient httpClient = new OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .build();
    
    private final Gson gson = new Gson();
    
    /**
     * Process single garment virtual try-on
     * @param humanPath Path to human image
     * @param clothPath Path to cloth image
     * @param garmentType Type of garment
     * @return API Response with try-on result
     */
    public ApiResponse<Object> processSingleTryOn(String humanPath, String clothPath, String garmentType) {
        log.info("Processing single try-on with garment type: {}", garmentType);
        
        try {
            if (!miragicApiKey.isEmpty()) {
                return processMiragicSingleTryOn(humanPath, clothPath, garmentType);
            } else {
                return processLocalSingleTryOn(humanPath, clothPath);
            }
        } catch (Exception e) {
            log.error("Error processing single try-on", e);
            return ApiResponse.error("Processing failed", e.getMessage());
        }
    }
    
    /**
     * Process combo garment virtual try-on (top + bottom)
     * @param humanPath Path to human image
     * @param topPath Path to top cloth image
     * @param bottomPath Path to bottom cloth image
     * @param garmentType Type of garment
     * @return API Response with try-on result
     */
    public ApiResponse<Object> processComboTryOn(String humanPath, String topPath, String bottomPath, String garmentType) {
        log.info("Processing combo try-on with garment type: {}", garmentType);
        
        try {
            if (!miragicApiKey.isEmpty()) {
                return processMiragicComboTryOn(humanPath, topPath, bottomPath, garmentType);
            } else {
                return processLocalComboTryOn(humanPath, topPath, bottomPath);
            }
        } catch (Exception e) {
            log.error("Error processing combo try-on", e);
            return ApiResponse.error("Processing failed", e.getMessage());
        }
    }
    
    /**
     * Process try-on using Miragic AI API
     */
    private ApiResponse<Object> processMiragicSingleTryOn(String humanPath, String clothPath, String garmentType) throws IOException {
        String url = miragicBaseUrl + "/api/v1/virtual-try-on";
        
        RequestBody body = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("garmentType", garmentType)
                .addFormDataPart("humanImage", new File(humanPath).getName(),
                        RequestBody.create(new File(humanPath), MediaType.parse("image/jpeg")))
                .addFormDataPart("clothImage", new File(clothPath).getName(),
                        RequestBody.create(new File(clothPath), MediaType.parse("image/jpeg")))
                .build();
        
        Request request = new Request.Builder()
                .url(url)
                .header("X-API-Key", miragicApiKey)
                .post(body)
                .build();
        
        try (Response response = httpClient.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                String errorBody = response.body() != null ? response.body().string() : "Unknown error";
                // Check for insufficient credits error - fall back to local processing
                if (errorBody.contains("INSUFFICIENT_CREDITS")) {
                    log.warn("Miragic API has insufficient credits. Falling back to local processing.");
                    return processLocalSingleTryOn(humanPath, clothPath);
                }
                return ApiResponse.error("Miragic request failed", errorBody);
            }
            
            String responseBody = response.body().string();
            JsonObject jsonResponse = gson.fromJson(responseBody, JsonObject.class);
            
            if (!jsonResponse.get("success").getAsBoolean()) {
                // Check for insufficient credits error - fall back to local processing
                if (responseBody.contains("INSUFFICIENT_CREDITS")) {
                    log.warn("Miragic API returned insufficient credits. Falling back to local processing.");
                    return processLocalSingleTryOn(humanPath, clothPath);
                }
                return ApiResponse.error("Miragic returned error", responseBody);
            }
            
            String jobId = jsonResponse.getAsJsonObject("data").get("jobId").getAsString();
            log.info("Job created with ID: {}", jobId);
            return pollMiragicJob(jobId);
        }
    }
    
    /**
     * Process combo try-on using Miragic AI API
     */
    private ApiResponse<Object> processMiragicComboTryOn(String humanPath, String topPath, String bottomPath, String garmentType) throws IOException {
        String url = miragicBaseUrl + "/api/v1/virtual-try-on";
        
        RequestBody body = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("garmentType", garmentType)
                .addFormDataPart("humanImage", new File(humanPath).getName(),
                        RequestBody.create(new File(humanPath), MediaType.parse("image/jpeg")))
                .addFormDataPart("clothImage", new File(topPath).getName(),
                        RequestBody.create(new File(topPath), MediaType.parse("image/jpeg")))
                .addFormDataPart("bottomClothImage", new File(bottomPath).getName(),
                        RequestBody.create(new File(bottomPath), MediaType.parse("image/jpeg")))
                .build();
        
        Request request = new Request.Builder()
                .url(url)
                .header("X-API-Key", miragicApiKey)
                .post(body)
                .build();
        
        try (Response response = httpClient.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                String errorBody = response.body() != null ? response.body().string() : "Unknown error";
                // Check for insufficient credits error - fall back to local processing
                if (errorBody.contains("INSUFFICIENT_CREDITS")) {
                    log.warn("Miragic API has insufficient credits. Falling back to local processing.");
                    return processLocalComboTryOn(humanPath, topPath, bottomPath);
                }
                return ApiResponse.error("Miragic request failed", errorBody);
            }
            
            String responseBody = response.body().string();
            JsonObject jsonResponse = gson.fromJson(responseBody, JsonObject.class);
            
            if (!jsonResponse.get("success").getAsBoolean()) {
                // Check for insufficient credits error - fall back to local processing
                if (responseBody.contains("INSUFFICIENT_CREDITS")) {
                    log.warn("Miragic API returned insufficient credits. Falling back to local processing.");
                    return processLocalComboTryOn(humanPath, topPath, bottomPath);
                }
                return ApiResponse.error("Miragic returned error", responseBody);
            }
            
            String jobId = jsonResponse.getAsJsonObject("data").get("jobId").getAsString();
            log.info("Combo job created with ID: {}", jobId);
            return pollMiragicJob(jobId);
        }
    }
    
    /**
     * Poll Miragic job status with cleaner response format
     */
    private ApiResponse<Object> pollMiragicJob(String jobId) throws IOException {
        String url = miragicBaseUrl + "/api/v1/virtual-try-on/" + jobId;
        long startTime = System.currentTimeMillis();
        long timeoutMs = 120000; // 120 seconds for longer processing
        long intervalMs = 2000;  // 2 seconds
        
        while (System.currentTimeMillis() - startTime < timeoutMs) {
            Request request = new Request.Builder()
                    .url(url)
                    .header("X-API-Key", miragicApiKey)
                    .get()
                    .build();
            
            try (Response response = httpClient.newCall(request).execute()) {
                String responseBody = response.body().string();
                JsonObject jsonResponse = gson.fromJson(responseBody, JsonObject.class);
                
                String status = jsonResponse.getAsJsonObject("data").get("status").getAsString();
                
                if ("COMPLETED".equals(status) || "FAILED".equals(status)) {
                    // Extract the data portion directly for cleaner response
                    JsonObject dataObj = jsonResponse.getAsJsonObject("data");
                    String processedUrl = dataObj.has("processedUrl") ? dataObj.get("processedUrl").getAsString() : null;
                    String resultImagePath = dataObj.has("resultImagePath") ? dataObj.get("resultImagePath").getAsString() : null;
                    String errorMessage = dataObj.has("errorMessage") ? dataObj.get("errorMessage").getAsString() : null;
                    
                    // Build a clean response
                    JsonObject cleanResult = new JsonObject();
                    cleanResult.addProperty("status", status);
                    cleanResult.addProperty("processedUrl", processedUrl);
                    cleanResult.addProperty("resultImagePath", resultImagePath);
                    cleanResult.addProperty("humanImagePath", dataObj.has("humanImagePath") ? dataObj.get("humanImagePath").getAsString() : null);
                    cleanResult.addProperty("clothImagePath", dataObj.has("clothImagePath") ? dataObj.get("clothImagePath").getAsString() : null);
                    
                    if (errorMessage != null && !errorMessage.isEmpty()) {
                        cleanResult.addProperty("errorMessage", errorMessage);
                    }
                    
                    return ApiResponse.builder()
                            .success("COMPLETED".equals(status))
                            .message("COMPLETED".equals(status) ? "Virtual try-on completed successfully" : "Virtual try-on failed")
                            .data(cleanResult)
                            .build();
                }
                
                // Log progress for pending jobs
                int progress = jsonResponse.getAsJsonObject("data").has("progress") 
                    ? jsonResponse.getAsJsonObject("data").get("progress").getAsInt() 
                    : 0;
                log.info("Job {} progress: {}%", jobId, progress);
            }
            
            try {
                Thread.sleep(intervalMs);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return ApiResponse.error("Polling interrupted");
            }
        }
        
        return ApiResponse.error("Polling timeout", "The virtual try-on request timed out. Please try again.");
    }
    
    /**
     * Local fallback for single garment try-on
     */
    private ApiResponse<Object> processLocalSingleTryOn(String humanPath, String clothPath) {
        try {
            String filename = "virtual_tryon_fallback_" + Instant.now().toEpochMilli() + ".png";
            String outputPath = generatedFolder + File.separator + filename;
            
            ImageProcessingUtil.createSingleTryOnImage(humanPath, clothPath, outputPath);
            
            JsonObject result = new JsonObject();
            result.addProperty("success", true);
            result.addProperty("note", "local_fallback");
            result.addProperty("file", filename);
            
            return ApiResponse.builder()
                    .success(true)
                    .note("local_fallback")
                    .data(result)
                    .build();
        } catch (Exception e) {
            log.error("Local fallback failed", e);
            return ApiResponse.error("Local fallback failed", e.getMessage());
        }
    }
    
    /**
     * Local fallback for combo garment try-on
     */
    private ApiResponse<Object> processLocalComboTryOn(String humanPath, String topPath, String bottomPath) {
        try {
            String filename = "virtual_tryon_fallback_combo_" + Instant.now().toEpochMilli() + ".png";
            String outputPath = generatedFolder + File.separator + filename;
            
            ImageProcessingUtil.createComboTryOnImage(humanPath, topPath, bottomPath, outputPath);
            
            JsonObject result = new JsonObject();
            result.addProperty("success", true);
            result.addProperty("note", "local_fallback");
            result.addProperty("file", filename);
            
            return ApiResponse.builder()
                    .success(true)
                    .note("local_fallback")
                    .data(result)
                    .build();
        } catch (Exception e) {
            log.error("Local fallback failed", e);
            return ApiResponse.error("Local fallback failed", e.getMessage());
        }
    }
}
