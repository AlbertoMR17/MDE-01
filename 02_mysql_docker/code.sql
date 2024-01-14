-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS Pictures;

-- Usar la base de datos
USE Pictures;

-- Crear la tabla "pictures"
CREATE TABLE IF NOT EXISTS pictures (
    id VARCHAR(36) PRIMARY KEY,
    path VARCHAR(255),
    date DATETIME,
    size FLOAT
);

-- Crear la tabla "tags"
CREATE TABLE IF NOT EXISTS tags (
    tag VARCHAR(32),
    picture_id VARCHAR(36),
    confidence FLOAT,
    date DATETIME,
    PRIMARY KEY (tag, picture_id),
    FOREIGN KEY (picture_id) REFERENCES pictures(id)
);
