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
    """Dialogo para restablecer contraseña."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Restablecer Contraseña")
        self.setMinimumWidth(300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        username_label = QLabel("Nombre de usuario:")
        self.username_input = create_styled_input("Ingresa tu nombre de usuario")

        password_label = QLabel("Contraseña nueva:")
        self.password_input = create_styled_input("Ingresa tu nueva contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        confirm_label = QLabel("Confirmar contraseña nueva:")
        self.confirm_input = create_styled_input("Confirma tu nueva contraseña")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        reset_btn = create_styled_button("Restablecer contraseña")
        reset_btn.clicked.connect(self.reset_password)

        layout.addWidget(QLabel("Ingresa tu nombre de usuario y tu nueva contraseña"))
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
            QMessageBox.warning(self, "Error", "Por favor completa todos los campos.")
            return

        if password != confirm:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
            return

        try:
            from database.supabase_client import reset_user_password
            reset_user_password(username, password)
            QMessageBox.information(
                self,
                "Excelente",
                "Tu contraseña ha sido restablecida exitosamente. Ahora puedes iniciar sesión con tu nueva contraseña."
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al restablecer la contraseña: {str(e)}")


class LoginWindow(QMainWindow):
    """Ventana de inicio de sesión."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wordle")
        self.setMinimumSize(700, 700)

        screen = QApplication.primaryScreen().geometry()
        self.move(int((screen.width() - self.width()) / 2),
                  int((screen.height() - self.height()) / 2))

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f7f7f7;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
            QFrame QLabel {
                margin: 0px;
                padding: 0px;
            }
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card.setLayout(card_layout)

        title_label = QLabel("Wordle")
        title_label.setFont(QFont("SF Pro Display", 32, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #10a37f;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tagline_label = QLabel("Un juego lúdico de palabras que desafía tu ingenio y vocabulario en cada partida.")
        tagline_label.setWordWrap(True)
        tagline_label.setFont(QFont("SF Pro Display", 15))
        tagline_label.setStyleSheet("color: #444444;")
        tagline_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Bienvenido de nuevo")
        subtitle.setFont(QFont("SF Pro Display", 15))
        subtitle.setStyleSheet("color: #666666;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.username_input = create_styled_input("Nombre de usuario")
        self.password_input = create_styled_input("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        login_btn = create_styled_button("Iniciar sesión")
        login_btn.clicked.connect(self.handle_login)

        signup_container = QWidget()
        signup_layout = QHBoxLayout()
        signup_layout.setContentsMargins(0, 0, 0, 0)
        signup_container.setLayout(signup_layout)

        signup_text = QLabel("¿No tienes una cuenta?")
        signup_text.setStyleSheet("color: #666666;")
        signup_btn = QPushButton("Regístrate")
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

        forgot_btn = QPushButton("¿Olvidaste tu contraseña?")
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

        card_layout.addWidget(title_label)
        card_layout.addSpacing(5)
        card_layout.addWidget(tagline_label)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(forgot_btn, alignment=Qt.AlignmentFlag.AlignRight)
        card_layout.addWidget(login_btn)
        card_layout.addWidget(signup_container)

        main_layout.addWidget(card)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.show_error("Por favor ingresa nombre de usuario y contraseña.")
            return

        try:
            user = sign_in(username, password)

            if user:
                self.user_id = user["id"]
                self.is_admin = user.get("is_admin", False)

                if self.is_admin:
                    self.show_admin_panel()
                else:
                    self.show_language_selection()
            else:
                self.show_error("Nombre de usuario o contraseña inválidos.")
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            self.show_error(f"Ocurrio un Error: {str(e)}")

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
        self.user_id = user_id
        self.is_admin = is_admin
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
