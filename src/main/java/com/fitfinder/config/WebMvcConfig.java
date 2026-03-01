package com.fitfinder.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Web MVC Configuration
 * Handles static resource mapping for generated outfits
 */
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {
    
    @Value("${app.generated-folder:generated_outfits}")
    private String generatedFolder;
    
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // Serve generated_outfits folder at /generated_outfits URL path
        registry.addResourceHandler("/generated_outfits/**")
                .addResourceLocations("file:" + generatedFolder + "/")
                .setCachePeriod(3600);
        
        // Serve tmp folder for temporary files
        registry.addResourceHandler("/tmp/**")
                .addResourceLocations("file:tmp/")
                .setCachePeriod(0);
    }
    
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOrigins("*")
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .maxAge(3600);
    }
}
