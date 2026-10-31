CREATE DATABASE IF NOT EXISTS ai_business_intelligence;

USE ai_business_intelligence;


-- =========================
-- USERS
-- =========================

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(30) DEFAULT 'business_user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================
-- DATASETS
-- =========================

CREATE TABLE IF NOT EXISTS datasets (
    dataset_id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_name VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    row_count INT DEFAULT 0,
    column_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================
-- DATASET COLUMNS
-- =========================

CREATE TABLE IF NOT EXISTS dataset_columns (
    column_id INT AUTO_INCREMENT PRIMARY KEY,

    dataset_id INT NOT NULL,

    column_name VARCHAR(255) NOT NULL,

    data_type VARCHAR(50) NOT NULL,

    column_order INT,

    FOREIGN KEY (dataset_id)
        REFERENCES datasets(dataset_id)
        ON DELETE CASCADE
);


-- =========================
-- REPORTS
-- =========================

CREATE TABLE IF NOT EXISTS reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,

    created_by INT,

    report_name VARCHAR(200),

    file_path VARCHAR(300),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (created_by)
        REFERENCES users(id)
);