from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.supabase_client import sign_out
from ui.game import WordleGame
from ui.statistics import StatisticsWindow
from ui.admin_panel import AdminPanel


class HomeWindow(QMainWindow):
    """Home window with options to play or view statistics."""
    
    def __init__(self, user_id, is_admin, language):
        super().__init__()
        self.user_id = user_id
        self.is_admin = is_admin
        self.language = language
        
        self.setWindowTitle("Wordle - Home")
        self.setMinimumSize(500, 400)
        self.setup_ui()
        
    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Header with language selection and logout
        header = QWidget()
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)
        
        # Language selector
        language_label = QLabel("Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "english")
        self.language_combo.addItem("Español", "spanish")
        
        # Set current language
        index = 0 if self.language == "english" else 1
        self.language_combo.setCurrentIndex(index)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.handle_logout)
        
        # Add widgets to header
        header_layout.addWidget(language_label)
        header_layout.addWidget(self.language_combo)
        header_layout.addStretch()
        header_layout.addWidget(logout_btn)
        
        # Title
        title_label = QLabel("Wordle")
        title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Buttons container
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_container.setLayout(buttons_layout)
        
        # Play button
        play_btn = QPushButton("Play Wordle")
        play_btn.setMinimumHeight(50)
        play_btn.setFont(QFont("Arial", 14))
        play_btn.clicked.connect(self.start_game)
        
        # Statistics button
        stats_btn = QPushButton("My Statistics")
        stats_btn.setMinimumHeight(50)
        stats_btn.setFont(QFont("Arial", 14))
        stats_btn.clicked.connect(self.show_statistics)
        
        # Admin panel button (only shown to admins)
        if self.is_admin:
            admin_btn = QPushButton("Admin Panel")
            admin_btn.setMinimumHeight(50)
            admin_btn.setFont(QFont("Arial", 14))
            admin_btn.clicked.connect(self.show_admin_panel)
            buttons_layout.addWidget(admin_btn)
        
        # Add widgets to layouts
        buttons_layout.addWidget(play_btn)
        buttons_layout.addWidget(stats_btn)
        
        main_layout.addWidget(header)
        main_layout.addWidget(title_label)
        main_layout.addStretch()
        main_layout.addWidget(buttons_container)
        main_layout.addStretch()
        
    def change_language(self, index):
        """Change the application language."""
        new_language = self.language_combo.itemData(index)
        
        if new_language != self.language:
            self.language = new_language
            
            # In a real app, we would update translations here
            # For now, just update the window title to reflect the language change
            if self.language == "spanish":
                self.setWindowTitle("Wordle - Inicio")
            else:
                self.setWindowTitle("Wordle - Home")
    
    def start_game(self):
        """Start a new Wordle game."""
        self.game_window = WordleGame(self.user_id, self.is_admin, self.language)
        self.hide()
        self.game_window.show()
    
    def show_statistics(self):
        """Show user statistics."""
        self.stats_window = StatisticsWindow(self.user_id, self.is_admin, self.language)
        self.hide()
        self.stats_window.show()
    
    def show_admin_panel(self):
        """Show admin panel (admin only)."""
        if not self.is_admin:
            return
            
        self.admin_panel = AdminPanel(self.user_id, self.language)
        self.hide()
        self.admin_panel.show()
    
    def handle_logout(self):
        """Handle user logout."""
        try:
            sign_out()
            
            # Return to login screen
            from ui.login import LoginWindow
            self.login_window = LoginWindow()
            self.hide()
            self.login_window.show()
        except Exception as e:
            print(f"Error logging out: {e}")
