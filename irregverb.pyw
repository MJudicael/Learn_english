import sys
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QMessageBox, QMenuBar, QMenu,
    QDialog, QLineEdit
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

# --- Constantes pour les fichiers de données ---
FICHIER_VERBES = "verbes.txt"
FICHIER_TRADUCTIONS = "traduction.txt"


def charger_donnees(fichier, separateur, num_parties):
    """
    Fonction générique pour charger des données depuis un fichier texte.
    """
    donnees = []
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            for ligne in f:
                ligne = ligne.strip()
                if not ligne or ligne.startswith("#"):
                    continue
                parties = ligne.split(separateur)
                if len(parties) == num_parties:
                    donnees.append(parties)
    except FileNotFoundError:
        return None  # Géré dans la classe principale
    return donnees


class HoverButton(QPushButton):
    """
    Un bouton personnalisé qui montre la réponse au survol.
    """
    def __init__(self, text, app_instance):
        super().__init__(text)
        self.app = app_instance

    def enterEvent(self, event):
        """Événement déclenché lorsque la souris entre sur le bouton."""
        if not self.app.waiting_for_next:
            self.app.show_current_answer()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Événement déclenché lorsque la souris quitte le bouton."""
        if not self.app.waiting_for_next:
            self.app.hide_answer()
        super().leaveEvent(event)


class AddTranslationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter une traduction")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Champ anglais
        self.english_input = QLineEdit()
        self.english_input.setPlaceholderText("Mot en anglais")
        layout.addWidget(QLabel("Anglais :"))
        layout.addWidget(self.english_input)
        
        # Champ français
        self.french_input = QLineEdit()
        self.french_input.setPlaceholderText("Mot en français")
        layout.addWidget(QLabel("Français :"))
        layout.addWidget(self.french_input)
        
        # Bouton d'ajout
        add_button = QPushButton("Ajouter")
        add_button.clicked.connect(self.accept)
        layout.addWidget(add_button)
        
        self.setLayout(layout)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("À propos")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Titre
        title = QLabel("Quiz de Révision")
        title.setFont(QFont("Helvetica", 16, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Version
        version = QLabel("Version 2.2")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        # Description
        description = QLabel(
            "Application de révision pour les verbes irréguliers anglais, "
            "le vocabulaire et les mathématiques.\n\n"
            "© 2024 Tous droits réservés\n"
            "Créé par : Mougin Judicaël\n"
            "Licence : MIT"
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)
        
        # Bouton OK
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)


class QuizApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.verbes = []
        self.traductions = []
        self.verbes_reussis = set()  # Nouveau : ensemble pour stocker les verbes réussis
        self.setWindowTitle("Révision : Verbes, Maths et Vocabulaire")
        self.setGeometry(100, 100, 450, 200)

        # Chargement des données
        self.verbes = charger_donnees(FICHIER_VERBES, ";", 4)
        if self.verbes is None:
            self.show_error_and_exit(f"Fichier '{FICHIER_VERBES}' introuvable.")
            return

        self.traductions = charger_donnees(FICHIER_TRADUCTIONS, ";", 2)
        if self.traductions is None:
            self.show_error_and_exit(f"Fichier '{FICHIER_TRADUCTIONS}' introuvable.")
            return

        if not self.verbes and not self.traductions:
            self.show_error_and_exit("Aucune donnée trouvée. Vérifiez vos fichiers .txt.")
            return

        self.score = 50
        self.current_question_data = {}
        self.waiting_for_next = False

        self.setup_ui()
        self.next_question()

    def show_error_and_exit(self, message):
        """Affiche une erreur critique et ferme l'application."""
        QMessageBox.critical(self, "Erreur Critique", message)
        # Utiliser QTimer pour quitter après que la boîte de dialogue soit fermée
        QTimer.singleShot(0, self.close)


    def setup_ui(self):
        # Ajout de la barre de menu
        menubar = self.menuBar()
        
        # Menu Edition
        edit_menu = menubar.addMenu("Edition")
        add_translation_action = edit_menu.addAction("Ajouter une traduction")
        add_translation_action.triggered.connect(self.show_add_translation_dialog)
        
        # Menu Aide
        help_menu = menubar.addMenu("Aide")
        about_action = help_menu.addAction("À propos")
        about_action.triggered.connect(self.show_about_dialog)

        # Reste du code existant de setup_ui
        """Configure l'interface utilisateur."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Label pour la question
        self.label_question = QLabel("Question", self)
        self.label_question.setFont(QFont("Helvetica", 24, QFont.Bold))
        self.label_question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.label_question)

        # Label pour la réponse (initialement vide)
        self.label_answer = QLabel("", self)
        self.label_answer.setFont(QFont("Helvetica", 18))
        self.label_answer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_answer.setStyleSheet("color: blue;")
        main_layout.addWidget(self.label_answer)
        main_layout.addSpacing(20)

        # Barre de progression
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(self.score)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumWidth(300)
        main_layout.addWidget(self.progress_bar, 0, Qt.AlignmentFlag.AlignCenter)
        self.update_progress_bar_style()

        main_layout.addSpacing(20)

        # Layout pour les boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_correct = QPushButton("✅ Bonne réponse")
        self.btn_correct.clicked.connect(self.correct_answer)
        self.btn_correct.setStyleSheet("background-color: green; color: white; padding: 10px; border-radius: 5px;")

        self.btn_wrong = QPushButton("❌ Mauvaise réponse")
        self.btn_wrong.clicked.connect(self.wrong_answer)
        self.btn_wrong.setStyleSheet("background-color: red; color: white; padding: 10px; border-radius: 5px;")
        
        # Bouton de survol
        self.btn_hover = HoverButton("Survoler pour la réponse", self)
        self.btn_hover.setStyleSheet("background-color: #007BFF; color: white; padding: 10px; border-radius: 5px;")


        buttons_layout.addWidget(self.btn_correct)
        buttons_layout.addWidget(self.btn_hover)
        buttons_layout.addWidget(self.btn_wrong)
        main_layout.addLayout(buttons_layout)


    def next_question(self):
        """Choisit et affiche la prochaine question au hasard."""
        self.waiting_for_next = False
        self.hide_answer()

        # Déterminer le type de question
        question_types = []
        if self.verbes and len(self.verbes_reussis) < len(self.verbes):
            question_types.append('verbe')
        if self.traductions:
            question_types.append('traduction')
        question_types.append('maths')

        choice = random.choice(question_types)

        # Définir la couleur et le thème selon le type de question
        if choice == 'verbe':
            theme = "Verbe irrégulier"  # Définir theme avant de l'utiliser
            theme_label = f'<div style="color: white; font-size: 10pt;">{theme}</div>'
            self.label_question.setStyleSheet("color: #20FEEF;")  # Bleu
            # Filtrer les verbes non réussis
            verbes_disponibles = [v for v in self.verbes if v[0] not in self.verbes_reussis]
            if verbes_disponibles:  # Si des verbes sont encore disponibles
                fr, inf, pret, part = random.choice(verbes_disponibles)
                self.current_question_data = {
                    'question': f"{theme_label}<div style='font-size: 24pt;'>{fr}</div>",
                    'answer': f"{inf} / {pret} / {part}",
                    'type': 'verbe',
                    'fr': fr
                }
        elif choice == 'traduction':
            theme = "Traduction"  # Définir theme avant de l'utiliser
            theme_label = f'<div style="color: white; font-size: 10pt;">{theme}</div>'
            self.label_question.setStyleSheet("color: #FFFFFF;")  # Blanc
            eng, fr = random.choice(self.traductions)
            self.current_question_data = {
                'question': f"{theme_label}<div style='font-size: 24pt;'>{eng}</div>",
                'answer': fr
            }
        elif choice == 'maths':
            theme = "Mathématique"  # Définir theme avant de l'utiliser
            theme_label = f'<div style="color: white; font-size: 10pt;">{theme}</div>'
            self.label_question.setStyleSheet("color: #ffce33;")  # Orange clair
            a, b = random.randint(2, 9), random.randint(2, 9)
            self.current_question_data = {
                'question': f"{theme_label}<div style='font-size: 24pt;'>{a} x {b} ?</div>",
                'answer': str(a * b)
            }
        
        self.label_question.setText(self.current_question_data['question'])
        # Important : activer le support du HTML rich text
        self.label_question.setTextFormat(Qt.RichText)

    def update_score(self, change):
        """Met à jour le score et la barre de progression."""
        if self.waiting_for_next:
            return
        self.score = max(0, min(100, self.score + change))
        self.progress_bar.setValue(self.score)
        self.update_progress_bar_style()
        
        self.waiting_for_next = True
        self.show_current_answer()
        # Passer à la question suivante après un court délai
        QTimer.singleShot(500, self.next_question)

    def correct_answer(self):
        if (self.current_question_data.get('type') == 'verbe' and 
            'fr' in self.current_question_data):
            # Ajouter le verbe à l'ensemble des verbes réussis
            self.verbes_reussis.add(self.current_question_data['fr'])
        self.update_score(1)

    def wrong_answer(self):
        self.update_score(-1)

    def show_current_answer(self):
        self.label_answer.setText(self.current_question_data.get('answer', ''))

    def hide_answer(self):
        self.label_answer.setText("")

    def update_progress_bar_style(self):
        """Change la couleur de la barre de progression selon le score."""
        if self.score <= 25:
            color = "#ff0000"  # Rouge
        elif self.score <= 50:
            color = "#ffff00"  # Jaune
        elif self.score <= 75:
            color = "#90ee90"  # Vert clair
        else:
            color = "#006400"  # Vert foncé
        
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                width: 10px; 
            }}
        """)

    def show_add_translation_dialog(self):
        dialog = AddTranslationDialog(self)
        if dialog.exec_():
            english = dialog.english_input.text().strip()
            french = dialog.french_input.text().strip()
            
            if english and french:  # Vérification que les champs ne sont pas vides
                try:
                    with open(FICHIER_TRADUCTIONS, "a", encoding="utf-8") as f:
                        f.write(f"\n{english};{french}")
                    
                    # Mise à jour de la liste des traductions
                    self.traductions.append([english, french])
                    QMessageBox.information(self, "Succès", "Traduction ajoutée avec succès !")
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter la traduction: {str(e)}")
            else:
                QMessageBox.warning(self, "Attention", "Veuillez remplir tous les champs !")

    def show_about_dialog(self):
        """Affiche la boîte de dialogue À propos"""
        dialog = AboutDialog(self)
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuizApp()
    window.show()
    sys.exit(app.exec())  # Remplacer exec_() par exec()