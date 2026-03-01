package com.fitfinder.repository;

import com.fitfinder.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Repository interface for User entity
 * Provides database operations for User records
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByUserid(String userid);
    boolean existsByUserid(String userid);
}
