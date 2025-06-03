from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QTabWidget, QGridLayout, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.supabase_client import (get_all_statistics, get_language_distribution,
                                      get_hardest_words)


class AdminPanel(QMainWindow):
    """Admin panel showing aggregate game statistics."""

    def __init__(self, user_id, language):
        super().__init__()
        self.user_id = user_id
        self.language = language
        self.is_admin = True  # Admin panel is only accessible to admins

        # Set window properties
        title = "Panel de Administrador" if language == "spanish" else "Admin Panel"
        self.setWindowTitle(f"Wordle - {title}")
        self.setMinimumSize(800, 600)

        # Load statistics
        self.load_statistics()

        # Set up UI
        self.setup_ui()

    def load_statistics(self):
        """Load all statistics from the database."""
        try:
            # Get all game results
            self.all_game_results = get_all_statistics()

            # Get language distribution
            self.language_distribution = get_language_distribution()

            # Get hardest words
            self.hardest_english = get_hardest_words("English", 10)
            self.hardest_spanish = get_hardest_words("Español", 10)

            # Calculate derived statistics
            self.calculate_statistics()
        except Exception as e:
            print(f"Error loading admin statistics: {e}")
            self.all_game_results = []
            self.language_distribution = []
            self.hardest_english = []
            self.hardest_spanish = []

    def calculate_statistics(self):
        """Calculate derived statistics from game results."""
        self.total_games = len(self.all_game_results)

        if self.total_games == 0:
            self.win_rate = 0
            self.avg_time = 0
            self.avg_attempts = 0
            return

        # Calculate win rate
        wins = sum(1 for g in self.all_game_results if g.get("win", False))
        self.win_rate = (wins / self.total_games) * 100 if self.total_games > 0 else 0

        # Calculate average time per game (in seconds)
        total_time = sum(g.get("time_taken", 0) for g in self.all_game_results)
        self.avg_time = total_time / self.total_games if self.total_games > 0 else 0

        # Calculate average attempts for wins
        winning_games = [g for g in self.all_game_results if g.get("win", False)]
        total_attempts = sum(g.get("attempts", 0) for g in winning_games)
        self.avg_attempts = total_attempts / len(winning_games) if winning_games else 0

    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

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

        # Header with back button
        header = QWidget()
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)

        back_btn = QPushButton("Back to Home")
        back_btn.clicked.connect(self.back_to_home)

        if self.language == "spanish":
            title_text = "Panel de Administrador"
        else:
            title_text = "Admin Panel"

        title_label = QLabel(title_text)
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Tab widget for different statistics
        self.tab_widget = QTabWidget()

        # Create tabs
        if self.language == "spanish":
            tab_names = ["Resumen", "Distribución de Idiomas", "Palabras Más Difíciles", "Historial de Juegos"]
        else:
            tab_names = ["Summary", "Language Distribution", "Hardest Words", "Game History"]

        # Summary tab
        summary_tab = QWidget()
        self.setup_summary_tab(summary_tab)
        self.tab_widget.addTab(summary_tab, tab_names[0])

        # Language distribution tab
        language_tab = self.create_language_tab()
        self.tab_widget.addTab(language_tab, tab_names[1])

        # Hardest words tab
        words_tab = self.create_hardest_words_tab()
        self.tab_widget.addTab(words_tab, tab_names[2])

        # Game history tab
        history_tab = QWidget()
        self.setup_history_tab(history_tab)
        self.tab_widget.addTab(history_tab, tab_names[3])

        # Add widgets to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(self.tab_widget)

    def setup_summary_tab(self, tab):
        """Set up the summary statistics tab."""
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Summary title
        if self.language == "spanish":
            summary_title = "Estadísticas Generales"
        else:
            summary_title = "Overall Statistics"

        title_label = QLabel(summary_title)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Statistics grid
        stats_widget = QWidget()
        stats_layout = QGridLayout()
        stats_widget.setLayout(stats_layout)

        # Create statistic widgets
        if self.language == "spanish":
            total_games = self.create_stat_widget("Total de Partidas", str(self.total_games))
            win_rate = self.create_stat_widget("Tasa de Victoria", f"{self.win_rate:.1f}%")
            avg_time = self.create_stat_widget("Tiempo Promedio", f"{self.avg_time:.1f}s")
            avg_attempts = self.create_stat_widget("Intentos Promedio", f"{self.avg_attempts:.1f}")
        else:
            total_games = self.create_stat_widget("Total Games", str(self.total_games))
            win_rate = self.create_stat_widget("Win Rate", f"{self.win_rate:.1f}%")
            avg_time = self.create_stat_widget("Average Time", f"{self.avg_time:.1f}s")
            avg_attempts = self.create_stat_widget("Average Attempts", f"{self.avg_attempts:.1f}")

        # Add statistics to grid
        stats_layout.addWidget(total_games, 0, 0)
        stats_layout.addWidget(win_rate, 0, 1)
        stats_layout.addWidget(avg_time, 1, 0)
        stats_layout.addWidget(avg_attempts, 1, 1)

        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addWidget(stats_widget)
        layout.addStretch()

    def create_language_tab(self):
        """Create tab showing language distribution with table."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Create table for language distribution
        table = QTableWidget()
        table.setColumnCount(2)

        # Set headers based on language
        if self.language == "spanish":
            headers = ["Idioma", "Partidas Jugadas"]
        else:
            headers = ["Language", "Games Played"]

        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        # Add data to table
        table.setRowCount(len(self.language_distribution))
        for i, lang in enumerate(self.language_distribution):
            language = lang.get("language_name", "Unknown")

            # Display language name based on current UI language
            if self.language == "spanish":
                language_display = "Español" if language == "Español" else "Inglés"
            else:
                language_display = "Spanish" if language == "Español" else "English"

            count = lang.get("game_count", 0)

            table.setItem(i, 0, QTableWidgetItem(language_display))
            table.setItem(i, 1, QTableWidgetItem(str(count)))

        layout.addWidget(table)

        return tab

    def create_hardest_words_tab(self):
        """Create tab showing hardest words with table."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Create table for hardest words
        table = QTableWidget()
        table.setColumnCount(4)

        # Set headers based on language
        if self.language == "spanish":
            headers = ["Palabra", "Idioma", "Intentos Promedio", "Veces Jugada"]
        else:
            headers = ["Word", "Language", "Avg. Attempts", "Times Played"]

        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Combine hardest words from both languages
        hardest_words = []
        if self.hardest_english:
            hardest_words.extend(self.hardest_english)
        if self.hardest_spanish:
            hardest_words.extend(self.hardest_spanish)

        # Sort by average attempts (descending)
        hardest_words.sort(key=lambda x: x.get("avg_attempts", 0), reverse=True)

        # Add data to table
        table.setRowCount(len(hardest_words))

        for i, word in enumerate(hardest_words):
            word_text = word.get("word", "")
            language = word.get("language", "")
            avg_attempts = word.get("avg_attempts", 0)
            times_played = word.get("times_played", 0)

            # Display language name based on current UI language
            if self.language == "spanish":
                language_display = "Español" if language == "spanish" else "Inglés"
            else:
                language_display = "Spanish" if language == "spanish" else "English"

            table.setItem(i, 0, QTableWidgetItem(word_text))
            table.setItem(i, 1, QTableWidgetItem(language_display))
            table.setItem(i, 2, QTableWidgetItem(f"{avg_attempts:.1f}"))
            table.setItem(i, 3, QTableWidgetItem(str(times_played)))

        layout.addWidget(table)

        return tab

    def update_words_table(self, language_code):
        """Update the hardest words table for the selected language."""
        # Set up columns
        if self.language == "spanish":
            headers = ["Palabra", "Intentos Promedio", "Veces Jugada"]
        else:
            headers = ["Word", "Average Attempts", "Times Played"]

        self.words_table.setColumnCount(len(headers))
        self.words_table.setHorizontalHeaderLabels(headers)
        self.words_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Get the appropriate data
        words_data = self.hardest_english if language_code == "english" else self.hardest_spanish

        # Populate table
        self.words_table.setRowCount(len(words_data))

        for row, word_data in enumerate(words_data):
            # Word
            word_item = QTableWidgetItem(word_data.get("word", ""))
            self.words_table.setItem(row, 0, word_item)

            # Average attempts
            avg_attempts = word_data.get("avg_attempts", 0)
            avg_item = QTableWidgetItem(f"{avg_attempts:.1f}")
            self.words_table.setItem(row, 1, avg_item)

            # Times played
            count_item = QTableWidgetItem(str(word_data.get("times_played", 0)))
            self.words_table.setItem(row, 2, count_item)

    def setup_history_tab(self, tab):
        """Set up the game history tab."""
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Game history title
        if self.language == "spanish":
            title_text = "Historial de Juegos"
        else:
            title_text = "Game History"

        title_label = QLabel(title_text)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create table for game history
        table = QTableWidget()

        # Set up columns
        if self.language == "spanish":
            headers = ["Usuario", "Fecha", "Palabra", "Idioma", "Intentos", "Tiempo", "Resultado", "Pistas"]
        else:
            headers = ["User", "Date", "Word", "Language", "Attempts", "Time", "Result", "Hints"]

        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Populate table with game results
        table.setRowCount(len(self.all_game_results))

        for row, game in enumerate(sorted(self.all_game_results, key=lambda g: g.get("created_at", ""), reverse=True)):
            # User
            user_item = QTableWidgetItem(game.get("username", ""))
            table.setItem(row, 0, user_item)

            # Date
            date_item = QTableWidgetItem(game.get("created_at", "")[:10])
            table.setItem(row, 1, date_item)

            # Word
            word_item = QTableWidgetItem(game.get("word", ""))
            table.setItem(row, 2, word_item)

            # Language
            lang = game.get("language", "")
            if self.language == "spanish":
                lang_display = "Español" if lang == "spanish" else "Inglés"
            else:
                lang_display = "Spanish" if lang == "spanish" else "English"

            lang_item = QTableWidgetItem(lang_display)
            table.setItem(row, 3, lang_item)

            # Attempts
            attempts_item = QTableWidgetItem(str(game.get("attempts", 0)))
            table.setItem(row, 4, attempts_item)

            # Time
            time_item = QTableWidgetItem(f"{game.get('time_taken', 0):.1f}s")
            table.setItem(row, 5, time_item)

            # Result
            if self.language == "spanish":
                result_text = "Victoria" if game.get("win", False) else "Derrota"
            else:
                result_text = "Win" if game.get("win", False) else "Loss"

            result_item = QTableWidgetItem(result_text)
            table.setItem(row, 6, result_item)

            # Hints Used
            hints_item = QTableWidgetItem(str(game.get("hints_used", 0)))
            table.setItem(row, 7, hints_item)

        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addWidget(table)

    def back_to_home(self):
        """Return to the home screen."""
        from ui.home import HomeWindow
        self.home_window = HomeWindow(self.user_id, self.is_admin, self.language)
        self.hide()
        self.home_window.show()
