from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, 
                             QTabWidget, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.supabase_client import get_all_statistics, get_language_distribution, get_hardest_words

class AdminWindow(QMainWindow):
    """Admin panel for viewing game statistics."""
    
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        self.setWindowTitle("Wordle Admin Panel")
        self.setMinimumSize(800, 600)
        self.setMaximumSize(1200, 900)
        
        # Center window on screen
        screen = QApplication.primaryScreen().geometry()
        self.move(int((screen.width() - self.width()) / 2),
                  int((screen.height() - self.height()) / 2))
        
        # Set window background color
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f7f7f7;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
                border-radius: 4px;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border: 1px solid #cccccc;
                border-bottom: none;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Title
        title = QLabel("Admin Statistics Panel")
        title.setFont(QFont("SF Pro Display", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #10a37f; margin: 20px 0;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Tab widget for different statistics
        tabs = QTabWidget()
        
        # Overall Statistics Tab
        overall_stats = QWidget()
        overall_layout = QVBoxLayout()
        overall_stats.setLayout(overall_layout)
        
        try:
            stats = get_all_statistics()
            stats_text = (
                f"Total Games Played: {stats.get('total_games', 0)}\n"
                f"Average Attempts: {stats.get('avg_attempts', 0):.2f}\n"
                f"Win Rate: {stats.get('win_rate', 0):.1f}%\n"
                f"Average Time: {stats.get('avg_time', 0):.1f} seconds"
            )
        except Exception as e:
            stats_text = f"Could not load statistics: {str(e)}"
        
        stats_label = QLabel(stats_text)
        stats_label.setFont(QFont("SF Pro Display", 14))
        stats_label.setStyleSheet("color: #333333; padding: 20px;")
        overall_layout.addWidget(stats_label)
        
        # Language Distribution Tab
        lang_stats = QWidget()
        lang_layout = QVBoxLayout()
        lang_stats.setLayout(lang_layout)
        
        try:
            lang_dist = get_language_distribution()
            lang_text = "Games by Language:\n\n"
            for item in lang_dist:
                lang_text += f"{item['language_name']}: {item['game_count']} games\n"
        except Exception as e:
            lang_text = f"Could not load language distribution: {str(e)}"
            
        lang_label = QLabel(lang_text)
        lang_label.setFont(QFont("SF Pro Display", 14))
        lang_label.setStyleSheet("color: #333333; padding: 20px;")
        lang_layout.addWidget(lang_label)
        
        # Hardest Words Tab
        hard_words = QWidget()
        hard_layout = QVBoxLayout()
        hard_words.setLayout(hard_layout)
        
        try:
            # Get all languages for dropdown selection
            hardest = get_hardest_words(None)  # Pass None to get all languages
            words_text = "Hardest Words (All Languages):\n\n"
            for word_data in hardest:
                words_text += (f"Word: {word_data['word']}\n"
                             f"Language: {word_data['language']}\n"
                             f"Average Attempts: {word_data['avg_attempts']:.1f}\n"
                             f"Times Played: {word_data['times_played']}\n\n")
        except Exception as e:
            words_text = f"Could not load hardest words: {str(e)}"
            
        words_label = QLabel(words_text)
        words_label.setFont(QFont("SF Pro Display", 14))
        words_label.setStyleSheet("color: #333333; padding: 20px;")
        hard_layout.addWidget(words_label)
        
        # Add tabs
        tabs.addTab(overall_stats, "Overall Statistics")
        tabs.addTab(lang_stats, "Language Distribution")
        tabs.addTab(hard_words, "Hardest Words")
        
        main_layout.addWidget(tabs)
