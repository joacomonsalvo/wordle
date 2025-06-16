from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.supabase_client import sign_out
from ui.game import WordleGame
from ui.statistics import StatisticsWindow
from ui.admin import AdminWindow


class HomeWindow(QMainWindow):
    """Ventana de inicio con opciones para jugar o ver estadísticas."""
    
    def __init__(self, user_id, is_admin, language):
        super().__init__()
        self.user_id = user_id
        self.is_admin = is_admin
        self.language = language
        
        self.setWindowTitle("Wordle - Home" if self.language!="spanish" else "Wordle - Inicio")
        self.setMinimumSize(700, 700)
        self.setup_ui()
        
    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        header = QWidget()
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)
        
        language_label = QLabel("Language:" if self.language!="spanish" else "Lenguaje:")
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "english")
        self.language_combo.addItem("Español", "spanish")
        
        index = 0 if self.language == "english" else 1
        self.language_combo.setCurrentIndex(index)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        
        logout_btn = QPushButton("Logout" if self.language!="spanish" else "Cerrar Sesión")
        logout_btn.clicked.connect(self.handle_logout)
        
        header_layout.addWidget(language_label)
        header_layout.addWidget(self.language_combo)
        header_layout.addStretch()
        header_layout.addWidget(logout_btn)
        
        title_label = QLabel("Wordle")
        title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_container.setLayout(buttons_layout)
        
        play_btn = QPushButton("Play Wordle" if self.language!="spanish" else "Jugar Wordle")
        play_btn.setMinimumHeight(50)
        play_btn.setFont(QFont("Arial", 14))
        play_btn.clicked.connect(self.start_game)
        
        stats_btn = QPushButton("My Statistics" if self.language!="spanish" else "Mis Estadísticas")
        stats_btn.setMinimumHeight(50)
        stats_btn.setFont(QFont("Arial", 14))
        stats_btn.clicked.connect(self.show_statistics)
        
        if self.is_admin:
            admin_btn = QPushButton("Admin Panel" if self.language!="spanish" else "Panel de Administrador")
            admin_btn.setMinimumHeight(50)
            admin_btn.setFont(QFont("Arial", 14))
            admin_btn.clicked.connect(self.show_admin_panel)
            buttons_layout.addWidget(admin_btn)
        
        buttons_layout.addWidget(play_btn)
        buttons_layout.addWidget(stats_btn)
        
        main_layout.addWidget(header)
        main_layout.addWidget(title_label)
        main_layout.addStretch()
        main_layout.addWidget(buttons_container)
        main_layout.addStretch()
        
    def change_language(self, index):
        """Cambiar el idioma de la aplicación."""
        new_language = self.language_combo.itemData(index)
        
        if new_language != self.language:
            self.language = new_language
            
            if self.language == "spanish":
                self.setWindowTitle("Wordle - Inicio")
            else:
                self.setWindowTitle("Wordle - Home")
    
    def start_game(self):
        """Iniciar un nuevo juego de Wordle."""
        self.game_window = WordleGame(self.user_id, self.is_admin, self.language)
        self.hide()
        self.game_window.show()
    
    def show_statistics(self):
        """Mostrar estadísticas del usuario."""
        self.stats_window = StatisticsWindow(self.user_id, self.is_admin, self.language)
        self.hide()
        self.stats_window.show()
    
    def show_admin_panel(self):
        """Mostrar panel de administrador (solo para administradores)."""
        if not self.is_admin:
            return
            
        self.admin_panel = AdminWindow(self.user_id)
        self.hide()
        self.admin_panel.show()
    
    def handle_logout(self):
        """Manejar cierre de sesión del usuario."""
        try:
            sign_out()
            
            from ui.login import LoginWindow
            self.login_window = LoginWindow()
            self.hide()
            self.login_window.show()
        except Exception as e:
            print(f"Error logging out: {e}" if self.language!="spanish" else f"Error al cerrar sesión: {e}")
