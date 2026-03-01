package com.fitfinder.model;

import jakarta.persistence.*;
import lombok.*;

/**
 * User Entity - Represents a user in the FitFinder system
 * Stores user credentials with bcrypt-hashed passwords
 */
@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String userid;
    
    @Column(nullable = false)
    private String password;
    
    @Column(name = "created_at")
    private java.time.LocalDateTime createdAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = java.time.LocalDateTime.now();
    }
}
