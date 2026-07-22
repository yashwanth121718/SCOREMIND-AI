-- ============================================================
-- Automated Answer Script Evaluation System Using AI
-- Database Schema Script for MySQL 8.0+
-- ============================================================

CREATE DATABASE IF NOT EXISTS `answer_eval_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `answer_eval_db`;

-- 1. Users Table
DROP TABLE IF EXISTS `evaluations`;
DROP TABLE IF EXISTS `student_answers`;
DROP TABLE IF EXISTS `questions`;
DROP TABLE IF EXISTS `exams`;
DROP TABLE IF EXISTS `subjects`;
DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('admin', 'teacher', 'student') NOT NULL DEFAULT 'student',
    `profile_pic` VARCHAR(255) DEFAULT 'default_avatar.png',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_users_role` (`role`),
    INDEX `idx_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Subjects Table
CREATE TABLE `subjects` (
    `subject_id` INT AUTO_INCREMENT PRIMARY KEY,
    `subject_name` VARCHAR(150) NOT NULL,
    `subject_code` VARCHAR(50) NOT NULL UNIQUE,
    `teacher_id` INT NOT NULL,
    FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Exams Table
CREATE TABLE `exams` (
    `exam_id` INT AUTO_INCREMENT PRIMARY KEY,
    `subject_id` INT NOT NULL,
    `exam_name` VARCHAR(150) NOT NULL,
    `exam_date` DATE NOT NULL,
    `total_marks` FLOAT NOT NULL DEFAULT 100.0,
    FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`subject_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Questions Table
CREATE TABLE `questions` (
    `question_id` INT AUTO_INCREMENT PRIMARY KEY,
    `exam_id` INT NOT NULL,
    `question_text` TEXT NOT NULL,
    `model_answer` TEXT NOT NULL,
    `keywords` TEXT DEFAULT NULL,
    `max_marks` FLOAT NOT NULL DEFAULT 10.0,
    FOREIGN KEY (`exam_id`) REFERENCES `exams` (`exam_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Student Answers Table
CREATE TABLE `student_answers` (
    `answer_id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `question_id` INT NOT NULL,
    `answer_text` TEXT DEFAULT NULL,
    `uploaded_file` VARCHAR(255) DEFAULT NULL,
    `submitted_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`question_id`) REFERENCES `questions` (`question_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Evaluation Table
CREATE TABLE `evaluations` (
    `evaluation_id` INT AUTO_INCREMENT PRIMARY KEY,
    `answer_id` INT NOT NULL UNIQUE,
    `student_id` INT NOT NULL,
    `question_id` INT NOT NULL,
    `similarity_score` FLOAT NOT NULL DEFAULT 0.0,
    `grammar_score` FLOAT NOT NULL DEFAULT 0.0,
    `keyword_score` FLOAT NOT NULL DEFAULT 0.0,
    `obtained_marks` FLOAT NOT NULL DEFAULT 0.0,
    `feedback` TEXT DEFAULT NULL,
    `matched_keywords` TEXT DEFAULT NULL,
    `missing_keywords` TEXT DEFAULT NULL,
    `evaluated_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`answer_id`) REFERENCES `student_answers` (`answer_id`) ON DELETE CASCADE,
    FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`question_id`) REFERENCES `questions` (`question_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- SAMPLE DATA FOR DEMONSTRATION & TESTING
-- Default Passwords for all sample users: 'admin123' / 'teacher123' / 'student123'
-- ============================================================

INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`) VALUES
(1, 'System Admin', 'admin@eval.ai', 'scrypt:32768:8:1$uH3y4x$8fd5e6c7d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8', 'admin'),
(2, 'Dr. Alan Turing', 'turing@university.edu', 'scrypt:32768:8:1$uH3y4x$8fd5e6c7d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8', 'teacher'),
(3, 'Prof. Ada Lovelace', 'ada@university.edu', 'scrypt:32768:8:1$uH3y4x$8fd5e6c7d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8', 'teacher'),
(4, 'John Doe', 'john@student.edu', 'scrypt:32768:8:1$uH3y4x$8fd5e6c7d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8', 'student'),
(5, 'Jane Smith', 'jane@student.edu', 'scrypt:32768:8:1$uH3y4x$8fd5e6c7d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8', 'student');

INSERT INTO `subjects` (`subject_id`, `subject_name`, `subject_code`, `teacher_id`) VALUES
(1, 'Data Structures & Algorithms', 'CS201', 2),
(2, 'Database Management Systems', 'CS301', 3);

INSERT INTO `exams` (`exam_id`, `subject_id`, `exam_name`, `exam_date`, `total_marks`) VALUES
(1, 1, 'Mid-Term Assessment 2026', '2026-03-15', 20.0),
(2, 2, 'DBMS Final Theory Exam', '2026-04-20', 10.0);

INSERT INTO `questions` (`question_id`, `exam_id`, `question_text`, `model_answer`, `keywords`, `max_marks`) VALUES
(1, 1, 'Explain the concept of Binary Search Trees (BST) and state its average-case search time complexity.', 'A Binary Search Tree (BST) is a node-based binary tree data structure where the key in each node is greater than all keys in its left subtree and less than all keys in its right subtree. The average-case search time complexity is O(log n), whereas the worst-case search complexity is O(n) for a skewed tree.', 'node, binary tree, left subtree, right subtree, search complexity, O(log n), skewed tree', 10.0),
(2, 2, 'What is ACID property in Database Management Systems? Explain each component.', 'ACID stands for Atomicity, Consistency, Isolation, and Durability. Atomicity ensures all operations in a transaction succeed or none occur. Consistency ensures data matches database constraints before and after transactions. Isolation guarantees concurrent transactions do not interfere. Durability guarantees committed data persists even during crashes.', 'Atomicity, Consistency, Isolation, Durability, transaction, constraints, concurrency, persistence', 10.0);

INSERT INTO `student_answers` (`answer_id`, `student_id`, `question_id`, `answer_text`) VALUES
(1, 4, 1, 'A Binary Search Tree is a data structure where each node has at most two children. The left subtree contains values smaller than the root, and the right subtree contains larger values. Searching in a BST takes O(log n) average time complexity.'),
(2, 5, 2, 'ACID properties stand for Atomicity, Consistency, Isolation, and Durability. Atomicity means all or nothing. Consistency keeps data valid. Isolation makes transactions independent. Durability ensures data is saved permanently even if server crashes.');

INSERT INTO `evaluations` (`evaluation_id`, `answer_id`, `student_id`, `question_id`, `similarity_score`, `grammar_score`, `keyword_score`, `obtained_marks`, `feedback`, `matched_keywords`, `missing_keywords`) VALUES
(1, 1, 4, 1, 88.5, 95.0, 85.0, 8.9, '🌟 Excellent Work! Your answer covers all major concepts thoroughly with strong structural clarity.', 'node, binary tree, left subtree, right subtree, O(log n)', 'skewed tree'),
(2, 2, 5, 2, 92.0, 98.0, 90.0, 9.3, '🌟 Excellent Work! Outstanding coverage of ACID principles.', 'Atomicity, Consistency, Isolation, Durability, transaction', 'persistence');
