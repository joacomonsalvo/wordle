from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QDialog,
                             QApplication, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.supabase_client import sign_in
from ui.language_selection import LanguageSelectionWindow
from ui.signup import SignupWindow

from ui.styles import create_styled_button, create_styled_input


class PasswordResetDialog(QDialog):
    """Dialog for password reset functionality."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reset Password")
        self.setMinimumWidth(300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Username input
        username_label = QLabel("Username:")
        self.username_input = create_styled_input("Enter your username")

        # New password input
        password_label = QLabel("New Password:")
        self.password_input = create_styled_input("Enter new password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Confirm password input
        confirm_label = QLabel("Confirm Password:")
        self.confirm_input = create_styled_input("Confirm new password")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Reset button
        reset_btn = create_styled_button("Reset Password")
        reset_btn.clicked.connect(self.reset_password)

        # Add widgets to layout
        layout.addWidget(QLabel("Enter your username and new password"))
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(confirm_label)
        layout.addWidget(self.confirm_input)
        layout.addWidget(reset_btn)

        self.setLayout(layout)

    def reset_password(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not username or not password or not confirm:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        if password != confirm:
            QMessageBox.warning(self, "Input Error", "Passwords do not match.")
            return

        try:
            # We'll implement this function in supabase_client.py
            from database.supabase_client import reset_user_password
            reset_user_password(username, password)
            QMessageBox.information(
                self,
                "Password Reset",
                "Your password has been successfully reset. You can now log in with your new password."
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


class LoginWindow(QMainWindow):
    """Main login window for the application."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wordle")
        self.setMinimumSize(400, 500)
        self.setMaximumSize(800, 650)

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
        subtitle = QLabel("Welcome back")
        subtitle.setFont(QFont("SF Pro Display", 16))
        subtitle.setStyleSheet("color: #666666;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Login form
        self.username_input = create_styled_input("Username")
        self.password_input = create_styled_input("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Login button
        login_btn = create_styled_button("Sign in")
        login_btn.clicked.connect(self.handle_login)

        # Sign up section
        signup_container = QWidget()
        signup_layout = QHBoxLayout()
        signup_layout.setContentsMargins(0, 0, 0, 0)
        signup_container.setLayout(signup_layout)

        signup_text = QLabel("Don't have an account?")
        signup_text.setStyleSheet("color: #666666;")
        signup_btn = QPushButton("Sign up")
        signup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        signup_btn.setStyleSheet("""
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
        signup_btn.clicked.connect(self.show_signup)

        signup_layout.addWidget(signup_text)
        signup_layout.addWidget(signup_btn)
        signup_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Forgot password button
        forgot_btn = QPushButton("Forgot password?")
        forgot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #666666;
                text-decoration: none;
                font-size: 12px;
            }
            QPushButton:hover {
                text-decoration: underline;
                color: #10a37f;
            }
        """)
        forgot_btn.clicked.connect(self.show_password_reset)

        # Add widgets to card layout
        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(forgot_btn, alignment=Qt.AlignmentFlag.AlignRight)
        card_layout.addWidget(login_btn)
        card_layout.addWidget(signup_container)

        # Add card to main layout
        main_layout.addWidget(card)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.show_error("Please enter both username and password.")
            return

        try:
            user = sign_in(username, password)

            if user:
                # Store user data
                self.user_id = user["id"]
                self.is_admin = user.get("is_admin", False)

                if self.is_admin:
                    # Admin users go directly to statistics panel
                    self.show_admin_panel()
                else:
                    # Regular users go to language selection
                    self.show_language_selection()
            else:
                self.show_error("Invalid username or password.")
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            self.show_error(f"An error occurred: {str(e)}")

    def show_error(self, message):
        error = QMessageBox(self)
        error.setIcon(QMessageBox.Icon.Warning)
        error.setText(message)
        error.setWindowTitle("Error")
        error.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #333333;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #10a37f;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #0e906f;
            }
        """)
        error.exec()

    def show_signup(self):
        self.signup_window = SignupWindow(login_window=self)
        self.signup_window.signup_successful.connect(self.on_signup_successful)
        self.signup_window.show()
        self.hide()

    def show_password_reset(self):
        dialog = PasswordResetDialog(self)
        dialog.exec()

    def on_signup_successful(self, user_id, is_admin):
        # Store user data
        self.user_id = user_id
        self.is_admin = is_admin

        # Show language selection
        self.show_language_selection()

    def show_language_selection(self):
        self.language_window = LanguageSelectionWindow(self.user_id, self.is_admin)
        self.hide()
        self.language_window.show()

    def show_admin_panel(self):
        from ui.admin import AdminWindow
        self.admin_window = AdminWindow(self.user_id)
        self.hide()
        self.admin_window.show()
