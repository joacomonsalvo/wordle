from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGroupBox, QApplication, QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from database.supabase_client import get_all_statistics, get_language_distribution, get_hardest_words, sign_out
from ui.styles import create_styled_button


class AdminWindow(QWidget):
    logoutRequested = pyqtSignal() # Signal to request showing the login page

    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Admin Statistics Panel")
        self.resize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title
        title_label = QLabel("Admin Statistics Panel")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(title_label)

        # Overall Statistics
        overall_group = QGroupBox("Overall Statistics")
        overall_layout = QVBoxLayout()
        self.overall_stats = QLabel("Loading overall statistics...")
        self.overall_stats.setStyleSheet("font-size: 14px; color: #555;")
        overall_layout.addWidget(self.overall_stats)
        overall_group.setLayout(overall_layout)
        overall_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; } QGroupBox::title { color: #2c3e50; }")
        layout.addWidget(overall_group)

        # Language Distribution
        lang_group = QGroupBox("Language Distribution (%)")
        lang_layout = QVBoxLayout()
        self.lang_dist = QLabel("Loading language distribution...")
        self.lang_dist.setStyleSheet("font-size: 14px; color: #555;")
        lang_layout.addWidget(self.lang_dist)
        lang_group.setLayout(lang_layout)
        lang_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; } QGroupBox::title { color: #2c3e50; }")
        layout.addWidget(lang_group)

        # Hardest Words
        hardest_group = QGroupBox("Top 3 Hardest Words per Language")
        hardest_layout = QVBoxLayout()
        self.hardest_words = QLabel("Loading hardest words...")
        self.hardest_words.setStyleSheet("font-size: 14px; color: #555;")
        hardest_layout.addWidget(self.hardest_words)
        hardest_group.setLayout(hardest_layout)
        hardest_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; } QGroupBox::title { color: #2c3e50; }")
        layout.addWidget(hardest_group)

        # Add a stretch to push content to the top before the button
        layout.addStretch(1)

        # Create a container for the logout button to align it to the right
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 15, 0, 0)
        button_layout.addStretch()

        # Create logout button with the same style as in User Home UI
        self.logout_button = create_styled_button("Log Out", is_primary=False)
        self.logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_button.clicked.connect(self.handle_logout)
        button_layout.addWidget(self.logout_button)
        
        # Add the button container to the main layout
        layout.addWidget(button_container)

        # Apply a clean style to the window
        self.setStyleSheet("background-color: #f5f5f5;") # Keep existing window style

        # Load statistics
        self.load_statistics()

    def handle_logout(self):
        try:
            # Sign out the user
            sign_out()
            
            # Import here to avoid circular imports
            from ui.login import LoginWindow
            
            # Create and show the login window
            self.login_window = LoginWindow()
            self.hide()  # Hide the admin window
            self.login_window.show()
            
        except Exception as e:
            print(f"Error during logout: {e}")

    def load_statistics(self):
        try:
            overall_data = get_all_statistics()
            language_data = get_language_distribution()
            hardest_words_data = get_hardest_words(None)  # Pass None to get all languages
            self.update_statistics(overall_data, language_data, hardest_words_data)
        except Exception as e:
            self.overall_stats.setText(f"Could not load overall statistics: {str(e)}")
            self.lang_dist.setText(f"Could not load language distribution: {str(e)}")
            self.hardest_words.setText(f"Could not load hardest words: {str(e)}")

    def update_statistics(self, overall_data, language_data, hardest_words_data):
        # --- Update overall statistics ---
        actual_overall_data = {}
        if isinstance(overall_data, list) and overall_data:
            actual_overall_data = overall_data[0]  # Assuming the first item is the stats dict
        elif isinstance(overall_data, dict):
            actual_overall_data = overall_data

        overall_text = f"Total Games Played: {actual_overall_data.get('total_games', 0)}\n"
        overall_text += f"Average Attempts: {actual_overall_data.get('avg_attempts', 0):.2f}\n"
        overall_text += f"Win Rate: {actual_overall_data.get('win_rate', 0):.2f}%"
        self.overall_stats.setText(overall_text)

        # --- Update language distribution ---
        lang_counts = {'es': 0, 'en': 0}
        if isinstance(language_data, list):
            for item in language_data:
                # Prioritize idioma_id if available
                lang_id_val = item.get('idioma_id')
                game_count = item.get('game_count', item.get('count', 0)) # Check for 'count' as well

                if lang_id_val == 1: # Spanish from idioma_id
                    lang_counts['es'] = game_count
                elif lang_id_val == 2: # English from idioma_id
                    lang_counts['en'] = game_count
                else: # Fallback to language_name if idioma_id is not present or different
                    lang_name = str(item.get('language_name', '')).lower()
                    if lang_name == 'spanish' or lang_name == 'es':
                        lang_counts['es'] = game_count
                    elif lang_name == 'english' or lang_name == 'en':
                        lang_counts['en'] = game_count

        elif isinstance(language_data, dict): # If it's already in {'es': X, 'en': Y} format
            lang_counts['es'] = language_data.get('es', 0)
            lang_counts['en'] = language_data.get('en', 0)

        total_games_by_lang = sum(lang_counts.values())
        if total_games_by_lang > 0:
            es_percentage = (lang_counts.get('es', 0) / total_games_by_lang) * 100
            en_percentage = (lang_counts.get('en', 0) / total_games_by_lang) * 100
            lang_text = f"Spanish: {es_percentage:.2f}% ({lang_counts.get('es',0)} games)\nEnglish: {en_percentage:.2f}% ({lang_counts.get('en',0)} games)"
        else:
            lang_text = "Spanish: 0.00% (0 games)\nEnglish: 0.00% (0 games)"
        self.lang_dist.setText(lang_text)

        # --- Update hardest words ---
        grouped_hardest_words = {'es': [], 'en': []}
        if isinstance(hardest_words_data, list):
            for item in hardest_words_data:
                lang_code = str(item.get('language', '')).lower() # Expecting 'language' key with 'es' or 'en'
                if lang_code == 'es':
                    grouped_hardest_words['es'].append(item)
                elif lang_code == 'en':
                    grouped_hardest_words['en'].append(item)
        elif isinstance(hardest_words_data, dict): # If already in {'es': [...], 'en': [...]} format
            grouped_hardest_words = hardest_words_data

        hardest_text = "Spanish:\n"
        # Sort by avg_attempts descending, then take top 3
        es_words = sorted(grouped_hardest_words.get('es', []), key=lambda x: x.get('avg_attempts', 0), reverse=True)
        if es_words:
            for i, word_info in enumerate(es_words[:3], 1):
                hardest_text += f"  {i}. {word_info.get('word', 'N/A')} (Avg Attempts: {word_info.get('avg_attempts', 0):.2f})\n"
        else:
            hardest_text += "  No data available.\n"
        
        hardest_text += "\nEnglish:\n"
        # Sort by avg_attempts descending, then take top 3
        en_words = sorted(grouped_hardest_words.get('en', []), key=lambda x: x.get('avg_attempts', 0), reverse=True)
        if en_words:
            for i, word_info in enumerate(en_words[:3], 1):
                hardest_text += f"  {i}. {word_info.get('word', 'N/A')} (Avg Attempts: {word_info.get('avg_attempts', 0):.2f})\n"
        else:
            hardest_text += "  No data available.\n"
            
        self.hardest_words.setText(hardest_text.strip())


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = AdminWindow(1)  # Pass a user_id
    window.show()
    sys.exit(app.exec())
