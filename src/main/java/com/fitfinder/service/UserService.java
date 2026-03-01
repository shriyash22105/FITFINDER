package com.fitfinder.service;

import com.fitfinder.model.User;
import com.fitfinder.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Optional;

/**
 * UserService - Handles user authentication and management
 * Provides login credentials verification and user operations
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    
    /**
     * Authenticate user with userid and password
     * @param userid User identifier
     * @param password Plain text password
     * @return User if authentication successful, empty Optional otherwise
     */
    public Optional<User> authenticate(String userid, String password) {
        log.info("Authenticating user: {}", userid);
        Optional<User> user = userRepository.findByUserid(userid);
        
        if (user.isPresent()) {
            if (passwordEncoder.matches(password, user.get().getPassword())) {
                log.info("User authenticated successfully: {}", userid);
                return user;
            }
        }
        
        log.warn("Authentication failed for user: {}", userid);
        return Optional.empty();
    }
    
    /**
     * Register a new user with encrypted password
     * @param userid User identifier
     * @param password Plain text password
     * @return Created User
     */
    public User registerUser(String userid, String password) {
        log.info("Registering new user: {}", userid);
        
        if (userRepository.existsByUserid(userid)) {
            throw new IllegalArgumentException("User already exists: " + userid);
        }
        
        User user = User.builder()
                .userid(userid)
                .password(passwordEncoder.encode(password))
                .build();
        
        return userRepository.save(user);
    }
    
    /**
     * Get user by userid
     * @param userid User identifier
     * @return User if found
     */
    public Optional<User> getUserByUserid(String userid) {
        return userRepository.findByUserid(userid);
    }
}
