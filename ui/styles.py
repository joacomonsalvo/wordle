from PyQt6.QtWidgets import QPushButton, QLineEdit
from PyQt6.QtCore import Qt


def create_styled_button(text, is_primary=True):
    """Create a styled button with modern design."""
    btn = QPushButton(text)
    btn.setMinimumHeight(40)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)

    if is_primary:
        btn.setStyleSheet("""
            QPushButton {
                background-color: #10a37f;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0e906f;
            }
            QPushButton:pressed {
                background-color: #0c7a5e;
            }
        """)
    else:
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #10a37f;
                border: 1px solid #10a37f;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(16, 163, 127, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(16, 163, 127, 0.2);
            }
        """)

    return btn


def create_styled_input(placeholder):
    """Create a styled input field with modern design."""
    input_field = QLineEdit()
    input_field.setPlaceholderText(placeholder)
    input_field.setMinimumHeight(40)
    input_field.setStyleSheet("""
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #e5e5e5;
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 14px;
        }
        QLineEdit:focus {
            border: 1px solid #10a37f;
            outline: none;
        }
    """)
    return input_field
