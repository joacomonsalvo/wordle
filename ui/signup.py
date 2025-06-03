from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QFrame,
                             QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.styles import create_styled_button, create_styled_input

from database.supabase_client import sign_up


class SignupWindow(QMainWindow):
    """Window for new user registration."""
    
    # Signal emitted when signup is successful
    signup_successful = pyqtSignal(int, bool)
    
    def __init__(self, login_window=None):
        self.login_window = login_window
        super().__init__()
        self.setWindowTitle("Wordle")
        self.setMinimumSize(400, 550)
        self.setMaximumSize(800, 700)
        
        # Center window on screen
        screen = QApplication.primaryScreen().geometry()
        self.move(int((screen.width() - self.width()) / 2),
                  int((screen.height() - self.height()) / 2))
        
        # Set window background color
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f7f7f7;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Create a card-like container
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(20)
        card.setLayout(card_layout)
        
        # Title
        title_label = QLabel("Wordle")
        title_label.setFont(QFont("SF Pro Display", 32, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #10a37f;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle
        subtitle = QLabel("Create your account")
        subtitle.setFont(QFont("SF Pro Display", 16))
        subtitle.setStyleSheet("color: #666666;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Form
        self.username_input = create_styled_input("Username")
        self.email_input = create_styled_input("Email")
        self.password_input = create_styled_input("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input = create_styled_input("Confirm Password")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Sign up button
        signup_btn = create_styled_button("Create account")
        signup_btn.clicked.connect(self.handle_signup)
        
        # Back to login section
        login_container = QWidget()
        login_layout = QHBoxLayout()
        login_layout.setContentsMargins(0, 0, 0, 0)
        login_container.setLayout(login_layout)
        
        login_text = QLabel("Already have an account?")
        login_text.setStyleSheet("color: #666666;")
        login_btn = QPushButton("Sign in")
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #10a37f;
                text-decoration: none;
                font-weight: 500;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        login_btn.clicked.connect(self.show_login)
        
        login_layout.addWidget(login_text)
        login_layout.addWidget(login_btn)
        login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add widgets to card layout
        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.email_input)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.confirm_input)
        card_layout.addWidget(signup_btn)
        card_layout.addWidget(login_container)
        
        # Add card to main layout
        main_layout.addWidget(card)
        
    def handle_signup(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if not username or not password or not email:
            self.show_error("Please fill in all fields: username, email, and password.")
            return
            
        # Basic email validation
        if '@' not in email or '.' not in email:
            self.show_error("Please enter a valid email address.")
            return
            
        if password != confirm:
            self.show_error("Passwords do not match.")
            return
            
        try:
            user = sign_up(username, password, email)
            
            if user:
                QMessageBox.information(self, "Success", "Account created successfully! Please sign in.")
                # Emit signal with user ID and admin status
                self.signup_successful.emit(user["id"], user.get("is_admin", False))
                self.close()
            else:
                self.show_error("Failed to create account.")
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            self.show_error(f"An error occurred: {str(e)}")
            
    def show_login(self):
        if self.login_window:
            self.login_window.show()
        self.close()
        
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
        
    def show_success(self, message):
        QMessageBox.information(self, "Success", message)
