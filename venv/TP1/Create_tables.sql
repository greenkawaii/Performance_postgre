-- ============================================
-- PHASE 1 : CRÉATION DES TABLES
-- ============================================

-- Table des étudiants
CREATE TABLE students (
    id_etu SERIAL PRIMARY KEY,
    nom VARCHAR(25) NOT NULL,
    prenom VARCHAR(25) NOT NULL
);

-- Table des cours
CREATE TABLE courses (
    id_cou SERIAL PRIMARY KEY,
    matiere VARCHAR(50) NOT NULL UNIQUE
);

-- Table des inscriptions
CREATE TABLE enrollments (
    etudiant INT NOT NULL,
    date TIMESTAMP NOT NULL,
    statut BOOLEAN,
    PRIMARY KEY(etudiant, date),
    FOREIGN KEY (etudiant) REFERENCES students(id_etu)
);

-- Table des logs d'accès
CREATE TABLE access_logs (
    cour SMALLINT NOT NULL,
    etudiant SMALLINT NOT NULL,
    date TIMESTAMP NOT NULL,
    PRIMARY KEY(cour, etudiant, date),
    FOREIGN KEY (etudiant) REFERENCES students(id_etu),
    FOREIGN KEY (cour) REFERENCES courses(id_cou)
);