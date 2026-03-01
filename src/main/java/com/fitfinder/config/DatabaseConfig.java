package com.fitfinder.config;

import com.fitfinder.model.User;
import com.fitfinder.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;

/**
 * Database Configuration - Initializes database with default data
 */
@Configuration
@RequiredArgsConstructor
@Slf4j
public class DatabaseConfig {
    
    /**
     * Initialize database with default admin user
     */
    @Bean
    public CommandLineRunner init(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        return args -> {
            // Check if default user exists
            if (!userRepository.existsByUserid("admin")) {
                User defaultUser = User.builder()
                        .userid("admin")
                        .password(passwordEncoder.encode("admin"))
                        .build();
                
                userRepository.save(defaultUser);
                log.info("Default admin user created: admin");
            } else {
                log.info("Default admin user already exists");
            }
        };
    }
}
