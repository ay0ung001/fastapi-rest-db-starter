CREATE DATABASE if not exists ece140;

USE ece140;

-- DUMP EVERYTHING... YOU REALLY SHOULDN'T DO THIS!
DROP TABLE if exists users;

-- 1. Create the users table
CREATE TABLE if not exists users (
  -- [INSERT CODE HERE]'
  user_id                 INT AUTO_INCREMENT PRIMARY KEY,
  first_name              VARCHAR(100) NOT NULL, 
  last_name               VARCHAR(100) NOT NULL
);

-- 2. Insert initial seed records into the table
-- [INSERT CODE HERE]
INSERT INTO users (first_name, last_name)
VALUES
  ('Rick', 'Gessner'),
  ('Ramsin', 'Khoshabeh'), 
  ('Curt', 'Schurgers');

