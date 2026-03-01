package com.fitfinder.model;

import lombok.*;
import org.springframework.web.multipart.MultipartFile;

/**
 * Virtual Try-On Request DTO for combo garments (top + bottom)
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TryOnComboRequest {
    private MultipartFile humanImage;
    private MultipartFile clothImage;
    private MultipartFile bottomClothImage;
    private String garmentType;
}
