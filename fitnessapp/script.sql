-- Fitness Club Management System Database Schema

CREATE DATABASE IF NOT EXISTS fitness_club;
USE fitness_club;

-- Clients table
CREATE TABLE clients (
    client_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    date_of_birth DATE,
    gender ENUM('M', 'F'),
    medical_restrictions TEXT,
    fitness_goals TEXT,
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active'
);

-- Membership types table
CREATE TABLE membership_types (
    membership_type_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    duration_days INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    gym_access BOOLEAN DEFAULT TRUE,
    pool_access BOOLEAN DEFAULT FALSE,
    group_classes_access BOOLEAN DEFAULT FALSE,
    visits_limit INT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Memberships table
CREATE TABLE memberships (
    membership_id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT NOT NULL,
    membership_type_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    price_paid DECIMAL(10, 2) NOT NULL,
    discount_applied DECIMAL(10, 2) DEFAULT 0,
    visits_remaining INT,
    status ENUM('active', 'expired', 'cancelled', 'frozen') DEFAULT 'active',
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
    FOREIGN KEY (membership_type_id) REFERENCES membership_types(membership_type_id)
);

-- Attendance records table
CREATE TABLE attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT NOT NULL,
    membership_id INT NOT NULL,
    check_in_time DATETIME NOT NULL,
    check_out_time DATETIME,
    zone_accessed VARCHAR(50) NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
    FOREIGN KEY (membership_id) REFERENCES memberships(membership_id)
);

-- Users table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    password VARCHAR(32) NOT NULL,
    role ENUM('admin','trainer','client','director') NOT NULL,
    trainer_id INT,
    client_id INT,
    FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id) ON DELETE SET NULL,
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE SET NULL
);

-- Trainers table
CREATE TABLE trainers (
    trainer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    specialization VARCHAR(100),
    hire_date DATE,
    status VARCHAR(20) DEFAULT 'active'
);

-- Group classes table
CREATE TABLE group_classes (
    class_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    trainer_id INT NOT NULL,
    room_number INT,
    max_participants INT NOT NULL,
    duration_minutes INT NOT NULL,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id)
);

-- Class schedule table
CREATE TABLE class_schedule (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    class_id INT NOT NULL,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    FOREIGN KEY (class_id) REFERENCES group_classes(class_id) ON DELETE CASCADE,
    UNIQUE KEY unique_schedule (class_id, day_of_week, start_time)
);

-- Class enrollments table
CREATE TABLE class_enrollments (
    enrollment_id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT NOT NULL,
    schedule_id INT NOT NULL,
    enrollment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    attendance_status ENUM('enrolled', 'attended', 'cancelled', 'no_show') DEFAULT 'enrolled',
    class_date DATE NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES class_schedule(schedule_id) ON DELETE CASCADE
);

-- Personal training sessions table
CREATE TABLE personal_training_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT NOT NULL,
    trainer_id INT NOT NULL,
    session_date DATETIME NOT NULL,
    duration_minutes INT NOT NULL,
    status ENUM('scheduled', 'completed', 'cancelled') DEFAULT 'scheduled',
    notes TEXT,
    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
    FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id)
);

-- Training journal table
CREATE TABLE training_journal (
    journal_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    exercise_name VARCHAR(100) NOT NULL,
    sets INT,
    reps INT,
    weight DECIMAL(8, 2),
    notes TEXT,
    recorded_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES personal_training_sessions(session_id) ON DELETE CASCADE
);

-- Discounts and promotions table
CREATE TABLE promotions (
    promotion_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    discount_percentage DECIMAL(5, 2),
    discount_amount DECIMAL(10, 2),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    applicable_membership_types VARCHAR(255),
    status ENUM('active', 'inactive') DEFAULT 'active'
);

-- Reports and analytics table
CREATE TABLE attendance_reports (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    report_date DATE NOT NULL,
    total_visits INT,
    unique_clients INT,
    gym_visits INT,
    pool_visits INT,
    group_classes_visits INT,
    peak_hour TIME,
    generated_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_client_email ON clients(email);
CREATE INDEX idx_client_phone ON clients(phone);
CREATE INDEX idx_membership_client ON memberships(client_id);
CREATE INDEX idx_membership_status ON memberships(status);
CREATE INDEX idx_attendance_client ON attendance(client_id);
CREATE INDEX idx_attendance_date ON attendance(check_in_time);
CREATE INDEX idx_enrollment_client ON class_enrollments(client_id);
CREATE INDEX idx_enrollment_schedule ON class_enrollments(schedule_id);
CREATE INDEX idx_personal_training_client ON personal_training_sessions(client_id);
CREATE INDEX idx_personal_training_trainer ON personal_training_sessions(trainer_id);

-- Trainer Availability table for blocking time
CREATE TABLE trainer_availability (
    availability_id INT PRIMARY KEY AUTO_INCREMENT,
    trainer_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    reason VARCHAR(255),
    FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id) ON DELETE CASCADE
);

-- Training Programs table
CREATE TABLE training_programs (
    program_id INT PRIMARY KEY AUTO_INCREMENT,
    trainer_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id) ON DELETE CASCADE
);

-- Program Exercises table
CREATE TABLE program_exercises (
    program_exercise_id INT PRIMARY KEY AUTO_INCREMENT,
    program_id INT NOT NULL,
    exercise_name VARCHAR(100) NOT NULL,
    sets INT,
    reps VARCHAR(50),
    notes TEXT,
    FOREIGN KEY (program_id) REFERENCES training_programs(program_id) ON DELETE CASCADE
);

-- Client Assigned Programs table
CREATE TABLE client_programs (
    client_program_id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT NOT NULL,
    program_id INT NOT NULL,
    assigned_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
    FOREIGN KEY (program_id) REFERENCES training_programs(program_id) ON DELETE CASCADE,
    UNIQUE KEY (client_id, program_id)
);

-- Feedback table
CREATE TABLE feedback (
    feedback_id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT NOT NULL,
    feedback_type ENUM('complaint', 'suggestion', 'question') NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('new', 'in_progress', 'resolved') DEFAULT 'new',
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE
);

-- Notifications table
CREATE TABLE notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    subject VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
