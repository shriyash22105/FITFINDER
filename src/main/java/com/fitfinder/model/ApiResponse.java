package com.fitfinder.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

/**
 * Generic API Response wrapper for REST endpoints
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ApiResponse<T> {
    private Boolean success;
    private String message;
    private T data;
    private String error;
    
    @JsonProperty("note")
    private String note;
    
    public static <T> ApiResponse<T> success(T data) {
        return ApiResponse.<T>builder()
                .success(true)
                .message("Request successful")
                .data(data)
                .build();
    }
    
    public static <T> ApiResponse<T> error(String error) {
        return ApiResponse.<T>builder()
                .success(false)
                .error(error)
                .build();
    }
    
    public static <T> ApiResponse<T> error(String error, String message) {
        return ApiResponse.<T>builder()
                .success(false)
                .error(error)
                .message(message)
                .build();
    }
}
