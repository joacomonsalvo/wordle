from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QPushButton, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.rules import RulesWindow


class LanguageSelectionWindow(QMainWindow):
    """Ventana para seleccionar el idioma de la aplicación."""

    def __init__(self, user_id, is_admin):
        super().__init__()
        self.user_id = user_id
        self.is_admin = is_admin
        self.selected_language = "spanish"

        self.setWindowTitle("Wordle - Seleccionar Idioma")
        self.setMinimumSize(700, 700)
        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(50, 80, 50, 80)
        main_layout.setSpacing(40)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        title_label = QLabel("Seleccionar Idioma")
        title_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: rgb(65, 165, 126);")
        main_layout.addWidget(title_label)

        selection_container = QWidget()
        selection_layout = QVBoxLayout()
        selection_layout.setSpacing(20)
        selection_container.setLayout(selection_layout)

        language_label = QLabel("Selecciona tu idioma:")
        language_label.setFont(QFont("Arial", 14))
        language_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.language_combo = QComboBox()
        self.language_combo.setFixedHeight(40)
        self.language_combo.setFont(QFont("Arial", 12))
        self.language_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 2px solid rgb(65, 165, 126);
                border-radius: 8px;
            }
        """)
        self.language_combo.addItem("Español", "spanish")
        self.language_combo.addItem("English", "english")
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)

        continue_btn = QPushButton("Continuar")
        continue_btn.setFixedHeight(40)
        continue_btn.setFont(QFont("Arial", 14, QFont.Weight.Medium))
        continue_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(65, 165, 126);
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgb(55, 145, 110);
            }
        """)
        continue_btn.clicked.connect(self.proceed_to_rules)

        selection_layout.addWidget(language_label)
        selection_layout.addWidget(self.language_combo)
        selection_layout.addWidget(continue_btn)

        main_layout.addWidget(selection_container)

    def on_language_changed(self, index):
        self.selected_language = self.language_combo.itemData(index)

    def proceed_to_rules(self):
        self.rules_window = RulesWindow(self.user_id, self.is_admin, self.selected_language)
        self.hide()
        self.rules_window.show()
