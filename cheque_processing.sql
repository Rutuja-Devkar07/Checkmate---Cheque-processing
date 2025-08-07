

CREATE DATABASE IF NOT EXISTS cheque_processing;

USE cheque_processing;

CREATE TABLE IF NOT EXISTS cheque_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    payee VARCHAR(255) ,
    amount VARCHAR(50),
    bank VARCHAR(255),
    micr_code VARCHAR(50),
    branch VARCHAR(255),
    ifsc_code VARCHAR(50),
    account_number VARCHAR(50),
    cheque_number VARCHAR(50),
    date VARCHAR(50),
    signature_verification VARCHAR(255)
);

