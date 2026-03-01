package com.fitfinder.model;

import lombok.*;
import org.springframework.web.multipart.MultipartFile;

/**
 * Virtual Try-On Request DTO for single garment
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TryOnRequest {
    private MultipartFile humanImage;
    private MultipartFile clothImage;
    private String garmentType;
}
