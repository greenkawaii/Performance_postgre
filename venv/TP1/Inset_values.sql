-- ============================================
-- PHASE 1 : INSERTION DES DONNÉES
-- ============================================

-- Insérer 200 000 étudiants
INSERT INTO students(nom, prenom)
SELECT
(ARRAY['Dupont', 'Martin', 'Bernard', 'Thomas', 'Petit', 'Robert', 'Richard',
'Durand', 'Dubois', 'Moreau', 'Laurent', 'Simon', 'Michel', 'Lefebvre', 'Leroy',
'Roux', 'David', 'Bertrand', 'Morel', 'Fournier', 'Girard', 'Bonnet', 'Dupuis',
'Lambert', 'Fontaine', 'Rousseau', 'Vincent', 'Muller', 'Lefevre', 'Faure',
'Andre', 'Mercier', 'Blanc', 'Guerin', 'Boyer', 'Garnier', 'Chevalier',
'Francois', 'Legrand', 'Gauthier', 'Garcia', 'Perrin', 'Robin', 'Clement',
'Morin', 'Nicolas', 'Henry', 'Roussel', 'Mathieu', 'Gautier', 'Masson',
'Marchand', 'Duval', 'Denis', 'Dumont', 'Marie', 'Lemoine', 'Noel', 'Meyer',
'Dufour', 'Meunier', 'Brun', 'Blanchard', 'Giraud', 'Joly', 'Riviere', 'Lucas',
'Brunet', 'Gaillard', 'Barbier', 'Arnaud', 'Martinez', 'Gerard', 'Roche',
'Renard', 'Schmitt', 'Roy', 'Leroux', 'Colin', 'Vidal', 'Caron', 'Picard',
'Roger', 'Fabre', 'Aubert', 'Lemoine', 'Renaud', 'Dumas', 'Lacombe', 'Bodin',
'Bourgeois', 'Bret', 'Cordier', 'Leclerc', 'Adam', 'Potier', 'Boulanger',
'Charles', 'Antoine', 'Jacquet', 'Huet', 'Langlois', 'Gillet', 'Bouvier',
'Julien', 'Prevost', 'Millet', 'Perrot', 'Daniel', 'Cousin', 'Germain',
'Breton', 'Besson', 'Klein', 'Baudouin', 'Gros', 'Buisson', 'Albert',
'Leveque', 'Pruvost', 'Philippe', 'Briand', 'Vallet', 'Guillot', 'Barre',
'Samson', 'Pascal', 'Jourdan', 'Allard', 'Jacques', 'Raymond', 'Camus',
'Guillaume', 'Maillard', 'Charpentier', 'Menard', 'Lebrun', 'Fleury', 'Herve',
'Klein', 'Weber', 'Diallo', 'Traore', 'Sow', 'Ndiaye', 'Kone', 'Ba', 'Diallo',
'Sy', 'Gueye', 'Diop', 'Kane', 'Fall', 'Ndoye', 'Mbaye', 'Diakite', 'Camara',
'Sarr', 'Fofana', 'Sangare', 'Cisse', 'Keita', 'Toure', 'Diallo', 'Bah',
'Sissoko', 'Konate', 'Coulibaly', 'Sako', 'Doumbia', 'Kante', 'Kamara',
'Barry', 'Savane'])[floor(random() * 174) + 1],
(ARRAY['Jean', 'Pierre', 'Marie', 'Claude', 'Nicolas', 'Anne', 'Sophie', 'Paul',
'Jacques', 'Julie', 'Thomas', 'Isabelle', 'Francois', 'Catherine', 'Philippe',
'Emilie', 'Michel', 'Christine', 'David', 'Valerie', 'Patrick', 'Sandrine',
'Alexandre', 'Celine', 'Julien', 'Caroline', 'Stephane', 'Patricia',
'Sebastien', 'Nathalie', 'Eric', 'Elodie', 'Olivier', 'Melanie', 'Vincent',
'Laura', 'Gregory', 'Audrey', 'Mathieu', 'Jessica', 'Anthony', 'Virginie',
'Kevin', 'Amandine', 'Jonathan', 'Laure', 'Romain', 'Coralie', 'Maxime',
'Pauline', 'Quentin', 'Manon', 'Alexis', 'Marine', 'Florian', 'Sarah',
'Jeremy', 'Aurelie', 'Baptiste', 'Lucie', 'Thibault', 'Morgane', 'Antoine',
'Chloe', 'Charles', 'Fanny', 'Guillaume', 'Noemie', 'Damien', 'Justine',
'Hugo', 'Oceane', 'Cedric', 'Laurine', 'Jordan', 'Maeva', 'Raphael', 'Lena',
'Lucas', 'Lea', 'Arthur', 'Emma', 'Louis', 'Clara', 'Leo', 'Ines', 'Gabin',
'Lola', 'Noah', 'Jade', 'Jules', 'Louise', 'Adam', 'Alice', 'Nathan', 'Camille',
'Tom', 'Eva', 'Enzo', 'Lina', 'Theo', 'Mila', 'Ethan', 'Anna', 'Maël', 'Zoé',
'Timothee', 'Luna', 'Samuel', 'Mya', 'Victor', 'Lilou', 'Martin', 'Sofia',
'Aaron', 'Julia', 'Gabriel', 'Rose', 'Rayan', 'Agathe', 'Sacha', 'Jeanne',
'Marius', 'Elise', 'Leon', 'Celeste', 'Oscar', 'Eleonore', 'Ibrahim', 'Sara',
'Mohamed', 'Zoe', 'Ali', 'Yasmine', 'Amir', 'Fatoumata', 'Moussa', 'Aissatou',
'Abdoulaye', 'Mariam', 'Cheikh', 'Aminata', 'Ousmane', 'Kadiatou', 'Mamadou',
'Rokia', 'Boubacar', 'Hawa', 'Idrissa', 'Fanta', 'Alassane', 'Binta', 'Modou',
'Diarra', 'Pape', 'Awa', 'Serigne', 'Ndeye', 'Moustapha', 'Adama', 'Ibrahima',
'Ramatoulaye'])[floor(random() * 162) + 1]
FROM generate_series(1, 200000);

-- Insérer 1 000 cours (125 matières × 8 niveaux)
INSERT INTO courses (matiere)
SELECT CONCAT(matiere_base, '_A', niveau) as matiere
FROM (
  VALUES 
    ('Mathématiques'), ('Physique'), ('Chimie'), ('Biologie'), ('Géologie'),
    ('Astronomie'), ('Météorologie'), ('Océanographie'), ('Écologie'), ('Génétique'),
    ('Algorithmique'), ('Programmation'), ('Bases de données'), ('Réseaux'), ('Systèmes'),
    ('Intelligence Artificielle'), ('Cybersécurité'), ('Développement Web'), ('Mobile'), ('Cloud'),
    ('Big Data'), ('IoT'), ('Robotique'), ('Blockchain'), ('DevOps'),
    ('Génie Civil'), ('Génie Mécanique'), ('Génie Électrique'), ('Génie Chimique'), ('Génie Industriel'),
    ('Génie Aérospatial'), ('Génie Biomédical'), ('Génie Environnemental'), ('Génie Logiciel'), ('Génie Matériaux'),
    ('Anatomie'), ('Physiologie'), ('Pharmacologie'), ('Immunologie'), ('Neurologie'),
    ('Cardiologie'), ('Pédiatrie'), ('Chirurgie'), ('Radiologie'), ('Epidémiologie'),
    ('Histoire'), ('Géographie'), ('Philosophie'), ('Sociologie'), ('Psychologie'),
    ('Anthropologie'), ('Archéologie'), ('Linguistique'), ('Sciences Politiques'), ('Démographie'),
    ('Littérature'), ('Théâtre'), ('Musique'), ('Arts Plastiques'), ('Cinéma'),
    ('Photographie'), ('Architecture'), ('Design'), ('Danse'), ('Histoire de l''Art'),
    ('Français'), ('Anglais'), ('Espagnol'), ('Allemand'), ('Italien'),
    ('Chinois'), ('Japonais'), ('Arabe'), ('Russe'), ('Portugais'),
    ('Économie'), ('Comptabilité'), ('Finance'), ('Marketing'), ('Management'),
    ('Ressources Humaines'), ('Entreprenariat'), ('Stratégie'), ('Logistique'), ('Audit'),
    ('Droit Civil'), ('Droit Pénal'), ('Droit Commercial'), ('Droit International'), ('Droit Constitutionnel'),
    ('Droit Administratif'), ('Droit du Travail'), ('Droit Fiscal'), ('Droit de la Propriété'), ('Droit Environnemental'),
    ('Pédagogie'), ('Didactique'), ('Évaluation'), ('Orientation'), ('Technologies Educatives'),
    ('Psychologie de l''Éducation'), ('Sociologie de l''Éducation'), ('Histoire de l''Éducation'), ('Philosophie de l''Éducation'), ('Administration Scolaire'),
    ('Agronomie'), ('Sylviculture'), ('Hydrologie'), ('Climatologie'), ('Énergies Renouvelables'),
    ('Gestion des Déchets'), ('Pollution'), ('Biodiversité'), ('Agriculture Durable'), ('Aquaculture'),
    ('Éducation Physique'), ('Physiologie du Sport'), ('Nutrition Sportive'), ('Psychologie du Sport'), ('Management Sportif'),
    ('Journalisme'), ('Relations Publiques'), ('Publicité'), ('Communication Digitale'), ('Médias')
) AS matieres(matiere_base)
CROSS JOIN generate_series(1, 8) AS niveaux(niveau);

-- Insérer 2 000 000 inscriptions
INSERT INTO enrollments (etudiant, date, statut)
SELECT
  floor(random() * 199999) + 1,
  timestamp '2024-01-01' + (random() * interval '365 days'),
  random() > 0.2
FROM generate_series(1, 2000000);

-- Insérer 5 000 000 logs d'accès
INSERT INTO access_logs (cour, etudiant, date)
SELECT
  floor(random() * 1000) + 1,
  floor(random() * 200000) + 1,
  timestamp '2024-01-01' + (random() * interval '365 days')
FROM generate_series(1, 5000000);

-- Vérifications
SELECT 'STUDENTS' AS table_name, COUNT(*) AS row_count FROM students
UNION ALL
SELECT 'COURSES', COUNT(*) FROM courses
UNION ALL
SELECT 'ENROLLMENTS', COUNT(*) FROM enrollments
UNION ALL
SELECT 'ACCESS_LOGS', COUNT(*) FROM access_logs;