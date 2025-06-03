from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.rules import RulesWindow


class LanguageSelectionWindow(QMainWindow):
    """Window for selecting application language."""
    
    def __init__(self, user_id, is_admin):
        super().__init__()
        self.user_id = user_id
        self.is_admin = is_admin
        self.selected_language = "english"  # Default language
        
        self.setWindowTitle("Wordle - Language Selection")
        self.setMinimumSize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Title
        title_label = QLabel("Select Language")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Language selection container
        selection_container = QWidget()
        selection_layout = QVBoxLayout()
        selection_container.setLayout(selection_layout)
        
        # Language dropdown
        language_label = QLabel("Choose your preferred language:")
        language_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "english")
        self.language_combo.addItem("Español", "spanish")
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        
        # Continue button
        continue_btn = QPushButton("Continue")
        continue_btn.clicked.connect(self.proceed_to_rules)
        
        # Add widgets to selection layout
        selection_layout.addWidget(language_label)
        selection_layout.addWidget(self.language_combo)
        selection_layout.addWidget(continue_btn)
        
        # Add selection container to main layout
        main_layout.addWidget(selection_container)
        
    def on_language_changed(self, index):
        # Get the language code from the combo box
        self.selected_language = self.language_combo.itemData(index)
        
        # In a real app, we would update application translations here
        # For example:
        # if self.selected_language == "spanish":
        #     translator.load(":/translations/wordle_es.qm")
        # else:
        #     translator.load("")  # Default language (English)
        
    def proceed_to_rules(self):
        self.rules_window = RulesWindow(self.user_id, self.is_admin, self.selected_language)
        self.hide()
        self.rules_window.show()
