from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QApplication, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView
)

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from database.supabase_client import get_all_statistics, sign_out
from ui.styles import create_styled_button


import csv
from PyQt6.QtWidgets import QFileDialog

class AdminWindow(QWidget):
    logoutRequested = pyqtSignal() # Signal to request showing the login page

    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Admin Statistics Panel")
        self.setMinimumSize(700, 700)
        self.setup_ui()

    def setup_ui(self):
        """Set up the unified statistics UI."""
        # Main layout
        main_layout = QVBoxLayout(self)

        # Create logout button early so it's available for header
        self.logout_button = create_styled_button("Log Out", is_primary=False)
        self.logout_button.setStyleSheet("background-color: rgb(68,165,126); color: white; border: none; padding:6px 12px; border-radius:5px;")
        self.logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_button.clicked.connect(self.handle_logout)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header with title and (optional) logout button
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_widget.setLayout(header_layout)

        title_label = QLabel("Estadísticas de Administración")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.logout_button)

        main_layout.addWidget(header_widget)

        # Summary statistics container
        summary_widget = QWidget()
        summary_layout = QHBoxLayout()
        summary_widget.setLayout(summary_layout)

        # Create stat widgets (placeholders until `update_ui_with_stats` runs)
        self.games_played_label = self.create_stat_widget("Juegos Totales", "0")
        self.games_en_label = self.create_stat_widget("Partidas en Inglés", "0.0%")
        self.games_es_label = self.create_stat_widget("Partidas en Español", "0.0%")
        self.win_rate_label = self.create_stat_widget("Tasa de Victoria", "0.0%")
        self.avg_time_label = self.create_stat_widget("Tiempo Prom.", "0.0s")
        self.avg_attempts_label = self.create_stat_widget("Intentos Prom.", "0.0")

        summary_layout.addWidget(self.games_played_label)
        summary_layout.addWidget(self.games_en_label)
        summary_layout.addWidget(self.games_es_label)
        summary_layout.addWidget(self.win_rate_label)
        summary_layout.addWidget(self.avg_time_label)
        summary_layout.addWidget(self.avg_attempts_label)

        main_layout.addWidget(summary_widget)

        # Game history label
        history_title = QLabel("Game History")
        history_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        main_layout.addWidget(history_title)

        # Game history table
        self.history_table = QTableWidget()
        self.setup_history_table()
        # Action buttons for export and link
        action_layout = QHBoxLayout()
        export_btn = create_styled_button("Exportar CSV", is_primary=False)
        export_btn.setStyleSheet("background-color: rgb(68,165,126); color: white; border: none; padding:6px 12px; border-radius:5px;")
        export_btn.clicked.connect(self.export_csv)
        link_btn = create_styled_button("Copiar enlace Looker", is_primary=False)
        link_btn.setStyleSheet("background-color: rgb(68,165,126); color: white; border: none; padding:6px 12px; border-radius:5px;")
        link_btn.clicked.connect(self.copy_looker_link)
        action_layout.addWidget(export_btn)
        action_layout.addWidget(link_btn)
        action_widget = QWidget()
        action_widget.setLayout(action_layout)
        main_layout.addWidget(self.history_table)
        main_layout.addWidget(action_widget)

        # Stretch at the end
        main_layout.addStretch()

        # Style
        self.setStyleSheet("background-color: #f5f5f5;")


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
        """Fetch and process statistics for all users."""
        try:
            self.game_results = get_all_statistics()
            self.calculate_statistics()
            self.update_ui_with_stats()
        except Exception as e:
            print(f"Error loading admin statistics: {e}")
            self.game_results = []


    # ----------------------------- NEW METHODS -----------------------------
    def calculate_statistics(self):
        """Compute summary metrics from the game list."""
        self.total_games = len(self.game_results)

        # Language distribution counts
        lang_counts = {"english": 0, "spanish": 0}
        total_time = 0
        total_attempts = 0
        wins = 0

        for g in self.game_results:
            lang = g.get("language", "").lower()
            if lang in ("english", "en"):
                lang_counts["english"] += 1
            elif lang in ("spanish", "es", "español"):
                lang_counts["spanish"] += 1

            total_time += g.get("time_taken", 0)
            # Count attempts for every game
            total_attempts += g.get("attempts", 0)
            if g.get("win", False):
                wins += 1

        # Percentages
        self.en_pct = (lang_counts["english"] / self.total_games * 100) if self.total_games else 0
        self.es_pct = (lang_counts["spanish"] / self.total_games * 100) if self.total_games else 0
        self.win_rate = (wins / self.total_games * 100) if self.total_games else 0
        self.avg_time = (total_time / self.total_games) if self.total_games else 0
        self.avg_attempts = (total_attempts / self.total_games) if self.total_games else 0

    def update_ui_with_stats(self):
        """Populate the stat widgets and history table with computed data."""
        # Update stat widgets
        self.set_stat_value(self.games_played_label, str(self.total_games))
        self.set_stat_value(self.games_en_label, f"{self.en_pct:.1f}%")
        self.set_stat_value(self.games_es_label, f"{self.es_pct:.1f}%")
        self.set_stat_value(self.win_rate_label, f"{self.win_rate:.1f}%")
        self.set_stat_value(self.avg_time_label, f"{self.avg_time:.1f}s")
        self.set_stat_value(self.avg_attempts_label, f"{self.avg_attempts:.1f}")

        # Fill history table
        self.history_table.setRowCount(len(self.game_results))
        for row, game in enumerate(sorted(self.game_results, key=lambda g: g.get("created_at", ""), reverse=True)):
            # User
            user_item = QTableWidgetItem(game.get("username", "Unknown"))
            self.history_table.setItem(row, 0, user_item)

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
            result_text = "Victoria" if game.get("win", False) else "Derrota"
            result_item = QTableWidgetItem(result_text)
            self.history_table.setItem(row, 5, result_item)

            # Hints Used
            hints_item = QTableWidgetItem(str(game.get("hints_used", 0)))
            self.history_table.setItem(row, 6, hints_item)

    # ----------------------------- Export / Link Methods -----------------------------
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "estadisticas.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # headers
                writer.writerow(["usuario", "palabra", "idioma", "intentos", "tiempo", "resultado", "pistas"])
                for g in self.game_results:
                    writer.writerow([
                        g.get("username", ""),
                        g.get("word", ""),
                        g.get("language", ""),
                        g.get("attempts", 0),
                        g.get("time_taken", 0),
                        "victoria" if g.get("win", False) else "derrota",
                        g.get("hints_used", 0)
                    ])
        except Exception as e:
            print(f"Error exporting CSV: {e}")

    def copy_looker_link(self):
        link = "https://looker.google.com/your-dashboard-link"
        QApplication.clipboard().setText(link)

    # ----------------------------- UI HELPERS -----------------------------
    def create_stat_widget(self, title: str, value: str) -> QWidget:
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

    def set_stat_value(self, widget: QWidget, value: str):
        # Assumes first child widget is the value QLabel
        value_label: QLabel = widget.layout().itemAt(0).widget()
        value_label.setText(value)

    def setup_history_table(self):
        headers = ["Usuario", "Palabra", "Idioma", "Intentos", "Tiempo", "Resultado", "Pistas"]
        self.history_table.setColumnCount(len(headers))
        self.history_table.setHorizontalHeaderLabels(headers)
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setMinimumHeight(330)  # or any height you prefer

        # End setup; legacy code below is skipped
        return


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = AdminWindow(1)  # Pass a user_id
    window.show()
    sys.exit(app.exec())
