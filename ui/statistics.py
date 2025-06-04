from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.supabase_client import get_user_statistics


class StatisticsWindow(QMainWindow):
    """Window displaying user statistics."""
    
    def __init__(self, user_id, is_admin, language):
        super().__init__()
        self.user_id = user_id
        self.is_admin = is_admin
        self.language = language
        
        # Set window properties
        title = "Estadísticas" if language == "spanish" else "Statistics"
        self.setWindowTitle(f"Wordle - {title}")
        self.setMinimumSize(700, 500)
        
        # Load user statistics
        self.load_statistics()
        
        # Set up UI
        self.setup_ui()
        
    def load_statistics(self):
        """Load user statistics from the database."""
        try:
            # Get user game results
            result = get_user_statistics(self.user_id)
            # Check if result is a list directly or has a data attribute
            if isinstance(result, list):
                self.game_results = result
            else:
                self.game_results = result.data if result.data else []
            
            # Calculate derived statistics
            self.calculate_statistics()
        except Exception as e:
            print(f"Error loading statistics: {e}")
            self.game_results = []
            
            # Initialize stats to 0 to prevent attribute errors
            self.total_games = 0
            self.win_rate = 0
            self.avg_time = 0
            self.avg_attempts = 0
            self.current_streak = 0
            self.max_streak = 0
            
    def calculate_statistics(self):
        """Calculate derived statistics from game results."""
        self.total_games = len(self.game_results)
        
        if self.total_games == 0:
            self.win_rate = 0
            self.avg_time = 0
            self.avg_attempts = 0
            self.current_streak = 0
            self.max_streak = 0
            return
            
        # Sort games by creation date
        sorted_games = sorted(self.game_results, key=lambda g: g.get("created_at", ""))
        
        # Calculate win rate
        wins = sum(1 for g in self.game_results if g.get("win", False))
        self.win_rate = (wins / self.total_games) * 100 if self.total_games > 0 else 0
        
        # Calculate average time per game (in seconds)
        total_time = sum(g.get("time_taken", 0) for g in self.game_results)
        self.avg_time = total_time / self.total_games if self.total_games > 0 else 0
        
        # Calculate average attempts for wins
        winning_games = [g for g in self.game_results if g.get("win", False)]
        total_attempts = sum(g.get("attempts", 0) for g in winning_games)
        self.avg_attempts = total_attempts / len(winning_games) if winning_games else 0
        
        # Calculate streaks
        current_streak = 0
        max_streak = 0
        
        for game in sorted_games:
            if game.get("win", False):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
                
        self.current_streak = current_streak
        self.max_streak = max_streak
        
    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Header with back button
        header = QWidget()
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)
        
        back_btn = QPushButton("Back to Home")
        back_btn.clicked.connect(self.back_to_home)
        
        if self.language == "spanish":
            title_text = "Estadísticas"
        else:
            title_text = "Statistics"
            
        title_label = QLabel(title_text)
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Summary statistics
        summary_widget = QWidget()
        summary_layout = QHBoxLayout()
        summary_widget.setLayout(summary_layout)
        
        # Create labels based on language
        if self.language == "spanish":
            games_label = self.create_stat_widget("Partidas", str(self.total_games))
            win_rate_label = self.create_stat_widget("% Victoria", f"{self.win_rate:.1f}%")
            streak_label = self.create_stat_widget("Racha Actual", str(self.current_streak))
            max_streak_label = self.create_stat_widget("Racha Máxima", str(self.max_streak))
            avg_time_label = self.create_stat_widget("Tiempo Promedio", f"{self.avg_time:.1f}s")
            avg_attempts_label = self.create_stat_widget("Intentos Promedio", f"{self.avg_attempts:.1f}")
        else:
            games_label = self.create_stat_widget("Games Played", str(self.total_games))
            win_rate_label = self.create_stat_widget("Win Rate", f"{self.win_rate:.1f}%")
            streak_label = self.create_stat_widget("Current Streak", str(self.current_streak))
            max_streak_label = self.create_stat_widget("Max Streak", str(self.max_streak))
            avg_time_label = self.create_stat_widget("Avg Time", f"{self.avg_time:.1f}s")
            avg_attempts_label = self.create_stat_widget("Avg Attempts", f"{self.avg_attempts:.1f}")
            
        summary_layout.addWidget(games_label)
        summary_layout.addWidget(win_rate_label)
        summary_layout.addWidget(streak_label)
        summary_layout.addWidget(max_streak_label)
        summary_layout.addWidget(avg_time_label)
        summary_layout.addWidget(avg_attempts_label)
        
        # Game history table
        if self.language == "spanish":
            history_label = QLabel("Historial de Partidas")
        else:
            history_label = QLabel("Game History")
            
        history_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        self.history_table = QTableWidget()
        self.setup_history_table()
        
        # Add widgets to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(summary_widget)
        main_layout.addWidget(history_label)
        main_layout.addWidget(self.history_table)
        
    def create_stat_widget(self, title, value):
        """Create a widget displaying a statistic with title and value."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        
        return widget
        
    def setup_history_table(self):
        """Set up the game history table."""
        # Set up columns
        if self.language == "spanish":
            headers = ["Fecha", "Palabra", "Idioma", "Intentos", "Tiempo", "Resultado", "Pistas Usadas"]
        else:
            headers = ["Date", "Word", "Language", "Attempts", "Time", "Result", "Hints Used"]
            
        self.history_table.setColumnCount(len(headers))
        self.history_table.setHorizontalHeaderLabels(headers)
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Populate table with game results
        self.history_table.setRowCount(len(self.game_results))
        
        for row, game in enumerate(sorted(self.game_results, key=lambda g: g.get("created_at", ""), reverse=True)):
            # Date
            date_item = QTableWidgetItem(game.get("created_at", "")[:10])
            self.history_table.setItem(row, 0, date_item)
            
            # Word
            word_item = QTableWidgetItem(game.get("word", ""))
            self.history_table.setItem(row, 1, word_item)
            
            # Language
            lang = game.get("language", "")
            lang_display = "Español" if lang == "spanish" else "English"
            lang_item = QTableWidgetItem(lang_display)
            self.history_table.setItem(row, 2, lang_item)
            
            # Attempts
            attempts_item = QTableWidgetItem(str(game.get("attempts", 0)))
            self.history_table.setItem(row, 3, attempts_item)
            
            # Time
            time_item = QTableWidgetItem(f"{game.get('time_taken', 0):.1f}s")
            self.history_table.setItem(row, 4, time_item)
            
            # Result
            if self.language == "spanish":
                result_text = "Victoria" if game.get("win", False) else "Derrota"
            else:
                result_text = "Win" if game.get("win", False) else "Loss"
                
            result_item = QTableWidgetItem(result_text)
            self.history_table.setItem(row, 5, result_item)
            
            # Hints Used
            hints_item = QTableWidgetItem(str(game.get("hints_used", 0)))
            self.history_table.setItem(row, 6, hints_item)
            
    def back_to_home(self):
        """Return to the home screen."""
        from ui.home import HomeWindow
        self.home_window = HomeWindow(self.user_id, self.is_admin, self.language)
        self.hide()
        self.home_window.show()
