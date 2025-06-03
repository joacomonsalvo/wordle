from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, 
                              QPushButton, QScrollArea, QApplication)
from ui.styles import create_styled_button
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont



class RulesWindow(QMainWindow):
    """Window displaying the rules of the Wordle game."""
    
    def __init__(self, user_id, is_admin, language):
        super().__init__()
        self.user_id = user_id
        self.is_admin = is_admin
        self.language = language
        
        self.setWindowTitle("Wordle - Rules")
        self.setMinimumSize(500, 400)
        self.setMaximumSize(800, 800)
        
        # Center window on screen
        screen = QApplication.primaryScreen().geometry()
        self.move(int((screen.width() - self.width()) / 2),
                  int((screen.height() - self.height()) / 2))
        
        # Set window background color
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f7f7f7;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget {
                background-color: transparent;
            }
        """)
        self.setup_ui()
        
    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Title
        title_label = QLabel("How to Play Wordle")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Scroll area for rules content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Rules content
        if self.language == "spanish":
            self.add_spanish_rules(scroll_layout)
        else:
            self.add_english_rules(scroll_layout)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Continue button
        continue_btn = create_styled_button("Let's Play!")
        continue_btn.setMinimumWidth(200)
        continue_btn.clicked.connect(self.proceed_to_home)
        main_layout.addWidget(continue_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(20)
        
    def add_english_rules(self, layout):
        """Add English rules to the layout."""
        rules = [
            ("<b>Guess the WORDLE in 6 tries.</b>", 14),
            ("Each guess must be a valid 5 letter word.", 12),
            ("Hit the Enter button to submit.", 12),
            ("After each guess, the color of the tiles will change to show how close your guess was to the word.", 12),
            ("<b>Examples:</b>", 14),
            ("<span style='background-color:#6aaa64; color:white; padding:2px 6px;'>W</span> " +
             "O R D L - The letter W is in the word and in the correct spot.", 12),
            ("W <span style='background-color:#c9b458; color:white; padding:2px 6px;'>O</span> " +
             "R D L - The letter O is in the word but in the wrong spot.", 12),
            ("W O R <span style='background-color:#787c7e; color:white; padding:2px 6px;'>D</span> " +
             "L - The letter D is not in the word in any spot.", 12),
            ("<b>Hints:</b>", 14),
            ("You have 3 hints available per game:", 12),
            ("1. Reveal a random correct letter", 12),
            ("2. Eliminate wrong letters from the keyboard", 12),
            ("3. Get a clue about the word's meaning", 12)
        ]
        
        for text, size in rules:
            label = QLabel(text)
            label.setFont(QFont("Arial", size))
            label.setWordWrap(True)
            label.setTextFormat(Qt.TextFormat.RichText)
            layout.addWidget(label)
            layout.addSpacing(10)
            
    def add_spanish_rules(self, layout):
        """Add Spanish rules to the layout."""
        rules = [
            ("<b>Adivina el WORDLE en 6 intentos.</b>", 14),
            ("Cada intento debe ser una palabra válida de 5 letras.", 12),
            ("Presiona el botón Enter para enviar.", 12),
            ("Después de cada intento, el color de las fichas cambiará para mostrar qué tan cerca estuviste de la palabra.", 12),
            ("<b>Ejemplos:</b>", 14),
            ("<span style='background-color:#6aaa64; color:white; padding:2px 6px;'>P</span> " +
             "A L A B - La letra P está en la palabra y en el lugar correcto.", 12),
            ("P <span style='background-color:#c9b458; color:white; padding:2px 6px;'>A</span> " +
             "L A B - La letra A está en la palabra pero en el lugar incorrecto.", 12),
            ("P A L <span style='background-color:#787c7e; color:white; padding:2px 6px;'>A</span> " +
             "B - La letra A no está en la palabra en ningún lugar.", 12),
            ("<b>Pistas:</b>", 14),
            ("Tienes 3 pistas disponibles por juego:", 12),
            ("1. Revelar una letra correcta aleatoria", 12),
            ("2. Eliminar letras incorrectas del teclado", 12),
            ("3. Obtener una pista sobre el significado de la palabra", 12)
        ]
        
        for text, size in rules:
            label = QLabel(text)
            label.setFont(QFont("Arial", size))
            label.setWordWrap(True)
            label.setTextFormat(Qt.TextFormat.RichText)
            layout.addWidget(label)
            layout.addSpacing(10)
            
    def proceed_to_home(self):
        try:
            from ui.home import HomeWindow
            self.home_window = HomeWindow(self.user_id, self.is_admin, self.language)
            self.hide()
            self.home_window.show()
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Could not load home window: {str(e)}")
