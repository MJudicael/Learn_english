OBJECTIF CNE v1.5.0
==================
Développé par Judicaël Mougin


DESCRIPTION
----------
Application d'apprentissage par questions/réponses destinée à la préparation d'examens.
Permet de mémoriser et tester ses connaissances de manière interactive.


FONCTIONNALITÉS
--------------
1. Questions/Réponses
   - Affichage aléatoire des questions
   - Visualisation de la réponse au survol
   - Maximum 100 questions par session
   - Validation manuelle (bonne/mauvaise réponse)

2. Suivi de Progression 
   - Barre de progression colorée :
     * Vert  : > 70% de réussite
     * Jaune : 50-70% de réussite  
     * Rouge : < 50% de réussite
   - Compteur questions restantes
   - Mémorisation des questions réussies

3. Gestion des Questions
   - Interface dédiée pour ajouter/modifier
   - Base de données SQLite
   - Système de validation (2 bonnes réponses requises)


UTILISATION
----------
1. Démarrer une session
   - Cliquer sur "Démarrer" (bouton turquoise en haut à gauche)
   - Les questions s'affichent en jaune

2. Répondre aux questions  
   - Survoler le bouton "Réponse" pour voir la solution
   - Valider avec "Bonne réponse" ou "Mauvaise réponse"
   - La barre de progression s'actualise

3. Gérer les questions
   - Menu "Gestion des mots" > "Ouvrir"
   - Ajouter ou modifier des questions
   - Les modifications sont sauvegardées automatiquement


NOTES
-----
- Maximum 100 questions par session
- Les questions sont considérées comme acquises après 2 bonnes réponses
- La base de données conserve l'historique entre les sessions


Pour toute question ou suggestion :
Judicaël Mougin
Version 1.5.0 - 2025

Pysid 6 necessary
