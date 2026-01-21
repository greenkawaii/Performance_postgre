-- ============================================
-- PHASE 2 : DIAGNOSTIC DES PERFORMANCES
-- ============================================

-- ============================================
-- TEST 1 : Filtre simple sur prenom
-- ============================================
-- SANS INDEX
EXPLAIN ANALYZE
SELECT * FROM students WHERE prenom = 'Pierre';

-- ============================================
-- TEST 2 : Filtre avec LIKE
-- ============================================
EXPLAIN ANALYZE
SELECT matiere FROM courses WHERE matiere LIKE '%A2';

-- ============================================
-- TEST 3 : Jointures simples (access_logs + students)
-- ============================================
-- Récupérer nom, prenom, date des accès d'un étudiant spécifique
EXPLAIN ANALYZE
SELECT s.nom, s.prenom, a.date 
FROM access_logs a
INNER JOIN students s ON a.etudiant = s.id_etu
WHERE s.id_etu = 42
ORDER BY a.date DESC
LIMIT 100;

-- ============================================
-- TEST 4 : Jointures multiples (3 tables)
-- ============================================
-- Récupérer : nom, prenom, date, matiere pour Physique_A1
EXPLAIN ANALYZE
SELECT s.nom, s.prenom, a.date, c.matiere 
FROM access_logs a
INNER JOIN students s ON a.etudiant = s.id_etu
INNER JOIN courses c ON a.cour = c.id_cou
WHERE c.matiere = 'Physique_A1'
LIMIT 1000;

-- ============================================
-- TEST 5 : Agrégation simple
-- ============================================
-- Compter les accès par étudiant
EXPLAIN ANALYZE
SELECT a.etudiant, COUNT(*) as nb_acces
FROM access_logs a
GROUP BY a.etudiant
HAVING COUNT(*) > 100
ORDER BY nb_acces DESC
LIMIT 50;

-- ============================================
-- TEST 6 : Filtre sur date + jointure
-- ============================================
-- Accès sur 7 derniers jours avec informations étudiant
EXPLAIN ANALYZE
SELECT s.id_etu, s.nom, s.prenom, COUNT(*) as nb_acces
FROM access_logs a
INNER JOIN students s ON a.etudiant = s.id_etu
WHERE a.date >= timestamp '2024-12-25' AND a.date < timestamp '2025-01-01'
GROUP BY s.id_etu, s.nom, s.prenom
ORDER BY nb_acces DESC
LIMIT 100;

-- ============================================
-- TEST 7 : Filtre sur cours inexistant (pour comparaison)
-- ============================================
-- Cette requête devrait retourner peu/pas de résultats
EXPLAIN ANALYZE
SELECT s.nom, s.prenom, a.date 
FROM access_logs a
INNER JOIN students s ON a.etudiant = s.id_etu
INNER JOIN courses c ON a.cour = c.id_cou
WHERE c.matiere = 'Cours_Inexistant'
LIMIT 1000;

-- ============================================
-- VÉRIFICATIONS DE COHÉRENCE
-- ============================================

-- Vérifier qu'il n'y a pas d'enrollments orphelins
SELECT COUNT(*) as enrollments_sans_etudiant
FROM enrollments e
LEFT JOIN students s ON e.etudiant = s.id_etu
WHERE s.id_etu IS NULL;

-- Vérifier qu'il n'y a pas d'access_logs orphelins
SELECT COUNT(*) as access_logs_sans_etudiant
FROM access_logs a
LEFT JOIN students s ON a.etudiant = s.id_etu
WHERE s.id_etu IS NULL;

-- Vérifier les limites des données
SELECT 
  'Students' as table_name,
  COUNT(*) as total_rows,
  MIN(id_etu) as min_id,
  MAX(id_etu) as max_id
FROM students
UNION ALL
SELECT 
  'Courses',
  COUNT(*),
  MIN(id_cou),
  MAX(id_cou)
FROM courses
UNION ALL
SELECT
  'Access_logs',
  COUNT(*),
  MIN(etudiant),
  MAX(etudiant)
FROM access_logs;

-- Taille des tables
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;