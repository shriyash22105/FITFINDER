package com.fitfinder.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;

/**
 * Security Configuration - Sets up security beans and CORS
 * Static files are served from /static/ directory
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    /**
     * BCrypt Password Encoder Bean
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12); // 12 rounds of bcrypt hashing
    }
    
    /**
     * Security Filter Chain - Allows static files and login page without authentication
     */
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                // Allow all static resources including HTML
                .requestMatchers("/static/**", "/css/**", "/js/**", "/images/**", "/**").permitAll()
                // Allow generated_outfits folder
                .requestMatchers("/generated_outfits/**").permitAll()
                // Allow tmp folder
                .requestMatchers("/tmp/**").permitAll()
                // Allow HTML pages directly
                .requestMatchers("/*.html", "/**/*.html").permitAll()
                // Allow API endpoints for auth
                .requestMatchers("/api/auth/**", "/login", "/logout").permitAll()
                // Allow virtual try-on API endpoints
                .requestMatchers("/api/tryon/**").permitAll()
                // Allow root and index
                .requestMatchers("/", "/index").permitAll()
                // All other requests require authentication
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/static/login.html")
                .loginProcessingUrl("/api/auth/login")
                .successHandler((request, response, authentication) -> {
                    response.setContentType("application/json");
                    response.getWriter().write("{\"success\":true,\"message\":\"Login successful\"}");
                })
                .failureHandler((request, response, exception) -> {
                    response.setContentType("application/json");
                    response.setStatus(401);
                    response.getWriter().write("{\"success\":false,\"message\":\"Invalid credentials\"}");
                })
                .permitAll()
            )
            .logout(logout -> logout
                .logoutUrl("/logout")
                .logoutSuccessUrl("/static/login.html?logout=true")
                .permitAll()
            );
        return http.build();
    }
    
    /**
     * CORS Configuration
     * Allows cross-origin requests from any source
     */
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(Arrays.asList("*"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(false);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
