import random
import time

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QFont

from database.supabase_client import save_game_result


class GameSaver(QObject):
    """Clase trabajadora para guardar los resultados del juego de forma asíncrona."""
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, user_id, target_word, language, attempts, time_taken, win, hints_used):
        super().__init__()
        self.user_id = user_id
        self.target_word = target_word
        self.language = language
        self.attempts = attempts
        self.time_taken = time_taken
        self.win = win
        self.hints_used = hints_used

    def save_game(self):
        """Guardar el resultado del juego en un hilo separado."""
        try:
            save_game_result(
                self.user_id,
                self.target_word,
                self.language,
                self.attempts,
                self.time_taken,
                self.win,
                self.hints_used
            )
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class LetterTile(QFrame):
    """Un cuadrado que representa una letra en el juego de Wordle."""

    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.letter = ""
        self.state = "empty"  # empty, filled, correct, present, absent

        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(60, 60)

        self.setFrameShape(QFrame.Shape.Box)
        self.setLineWidth(2)

        self.letter_label = QLabel("")
        self.letter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.letter_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.letter_label)
        self.setLayout(layout)

        self.update_style()

    def set_letter(self, letter):
        """Establece la letra para este azulejo."""
        self.letter = letter.upper() if letter else ""
        self.letter_label.setText(self.letter)

        if letter:
            self.state = "filled"
        else:
            self.state = "empty"

        self.update_style()

    def set_state(self, state):
        """Establece el estado del azulejo (correcto, presente, ausente)."""
        self.state = state
        self.update_style()

    def update_style(self):
        """Actualiza el estilo visual basado en el estado actual."""
        style = "border: 2px solid "

        if self.state == "empty":
            style += "#d3d6da;"
            self.letter_label.setStyleSheet("color: black;")
        elif self.state == "filled":
            style += "#878a8c;"
            self.letter_label.setStyleSheet("color: black;")
        elif self.state == "correct":
            style += "#6aaa64; background-color: #6aaa64;"
            self.letter_label.setStyleSheet("color: white;")
        elif self.state == "present":
            style += "#c9b458; background-color: #c9b458;"
            self.letter_label.setStyleSheet("color: white;")
        elif self.state == "absent":
            style += "#787c7e; background-color: #787c7e;"
            self.letter_label.setStyleSheet("color: white;")

        self.setStyleSheet(style)


class KeyboardKey(QPushButton):
    """Un botón en el teclado virtual."""

    def __init__(self, text, key_press_callback):
        super().__init__(text)
        self.key = text
        self.state = "unused"  # unused, correct, present, absent

        self.clicked.connect(lambda: key_press_callback(self.key))

        self.setFixedHeight(50)
        self.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.update_style()

    def set_state(self, state):
        """Establece el estado de la tecla."""
        # Only update to a 'better' state (correct > present > absent > unused)
        if (state == "correct" or
                (state == "present" and self.state != "correct") or
                (state == "absent" and self.state not in ["correct", "present"])):
            self.state = state
            self.update_style()

    def update_style(self):
        """Actualiza el estilo visual basado en el estado actual."""
        if self.state == "unused":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #d3d6da;
                    color: black;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #c3c6ca;
                }
            """)
        elif self.state == "correct":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #6aaa64;
                    color: white;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #5a9a54;
                }
            """)
        elif self.state == "present":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #c9b458;
                    color: white;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #b9a448;
                }
            """)
        elif self.state == "absent":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #787c7e;
                    color: white;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #686c6e;
                }
            """)


class WordleGame(QMainWindow):
    """La ventana principal del juego Wordle."""

    def __init__(self, user_id, is_admin, language):
        super().__init__()
        self.user_id = user_id
        self.is_admin = is_admin
        self.language = language

        self.current_row = 0
        self.current_col = 0
        self.game_over = False
        self.win = False
        self.start_time = time.time()
        self.hints_used = 0
        self.max_hints = 3

        self.load_word_list()

        self.setWindowTitle("Wordle")
        self.setMinimumSize(700, 700)
        self.setup_ui()

    def load_word_list(self):
        """Cargue de la base de datos la lista de palabras según el idioma seleccionado."""
        from database.supabase_client import get_words_for_game
        from PyQt6.QtWidgets import QMessageBox

        try:
            language_name = "english" if self.language == "english" else "spanish"

            self.valid_words = get_words_for_game(language_name)

            if not self.valid_words or not all(isinstance(word, str) for word in self.valid_words):
                raise ValueError(
                    "Invalid words list received from database" if self.language == "english" else "Invalida lista de palabras recibida de la base de datos")

            self.target_word = random.choice(self.valid_words).upper()

        except Exception as e:
            print(f"Error loading word list: {str(e)}")
            default_words = ["HELLO", "WORLD", "PYTHON", "BAGGY", "QUICK"] if self.language == "english" else \
                ["FECHA", "MUNDO", "TORTA", "FELIZ", "LOCOS"]
            self.valid_words = default_words
            self.target_word = random.choice(default_words)

            QMessageBox.warning(
                self,
                "Warning" if self.language == "english" else "Advertencia",
                "Could not load word list. Using default words." if self.language == "english"
                else "No se pudo cargar la lista de palabras. Usando palabras predeterminadas."
            )

        if not hasattr(self, 'target_word') or not self.target_word:
            self.target_word = "ERROR"

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        header = QWidget()
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)

        back_btn = QPushButton("Back to Home" if self.language != "spanish" else "Volver al Inicio")
        back_btn.clicked.connect(self.back_to_home)

        title_label = QLabel("Wordle")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hints_layout = QHBoxLayout()
        hint_text = "Pistas" if self.language == "spanish" else "Hints"
        hints_label = QLabel(f"{hint_text}: {self.max_hints - self.hints_used}/{self.max_hints}")
        hint_btn = QPushButton("Use Hint" if self.language != "spanish" else "Usar Pista")
        hint_btn.clicked.connect(self.use_hint)
        hints_layout.addWidget(hints_label)
        hints_layout.addWidget(hint_btn)

        self.hints_label = hints_label
        self.hint_btn = hint_btn

        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(hints_layout)

        board_widget = QWidget()
        board_layout = QGridLayout()
        board_layout.setSpacing(5)
        board_widget.setLayout(board_layout)

        self.tiles = []
        for row in range(6):
            row_tiles = []
            for col in range(5):
                tile = LetterTile(row, col)
                row_tiles.append(tile)
                board_layout.addWidget(tile, row, col)
            self.tiles.append(row_tiles)

        keyboard_widget = QWidget()
        keyboard_layout = QVBoxLayout()
        keyboard_widget.setLayout(keyboard_layout)
        self.keyboard_keys = {}

        row1_layout = QHBoxLayout()
        row1_keys = "QWERTYUIOP"
        for key in row1_keys:
            key_btn = KeyboardKey(key, self.key_pressed)
            row1_layout.addWidget(key_btn)
            self.keyboard_keys[key] = key_btn

        row2_layout = QHBoxLayout()
        row2_layout.addSpacing(15)
        row2_keys = "ASDFGHJKL"
        for key in row2_keys:
            key_btn = KeyboardKey(key, self.key_pressed)
            row2_layout.addWidget(key_btn)
            self.keyboard_keys[key] = key_btn
        row2_layout.addSpacing(15)

        row3_layout = QHBoxLayout()

        enter_btn = KeyboardKey("ENTER", self.key_pressed)
        enter_btn.setFixedWidth(80)
        row3_layout.addWidget(enter_btn)

        row3_keys = "ZXCVBNM"
        for key in row3_keys:
            key_btn = KeyboardKey(key, self.key_pressed)
            row3_layout.addWidget(key_btn)
            self.keyboard_keys[key] = key_btn

        backspace_btn = KeyboardKey("⌫", self.key_pressed)
        backspace_btn.setFixedWidth(80)
        row3_layout.addWidget(backspace_btn)

        keyboard_layout.addLayout(row1_layout)
        keyboard_layout.addLayout(row2_layout)
        keyboard_layout.addLayout(row3_layout)

        main_layout.addWidget(header)
        main_layout.addWidget(board_widget)
        main_layout.addStretch()
        main_layout.addWidget(keyboard_widget)

    def key_pressed(self, key):
        """Manejar una pulsación de tecla en el teclado virtual."""
        if self.game_over:
            return

        if key == "ENTER":
            self.submit_guess()
        elif key == "⌫":
            self.delete_letter()
        else:
            self.add_letter(key)

    def add_letter(self, letter):
        """Agregar una letra a la posición actual."""
        if self.current_col < 5:
            self.tiles[self.current_row][self.current_col].set_letter(letter)
            self.current_col += 1

    def delete_letter(self):
        """Eliminar la última letra ingresada."""
        if self.current_col > 0:
            self.current_col -= 1
            self.tiles[self.current_row][self.current_col].set_letter("")

    def submit_guess(self):
        """Enviar la suposición actual para evaluación."""
        if self.current_col < 5:
            self.show_message(
                "Not enough letters" if self.language != "spanish" else "Por favor, ingresa una palabra de 5 letras.",
                "Please enter a 5-letter word." if self.language != "spanish" else "Por favor, ingresa una palabra de 5 letras.")
            return
        guess = ""
        for col in range(5):
            guess += self.tiles[self.current_row][col].letter

        self.evaluate_guess(guess)

        if guess == self.target_word:
            self.game_win()
        elif self.current_row >= 5:
            self.game_lose()
        else:
            self.current_row += 1
            self.current_col = 0

    def evaluate_guess(self, guess):
        """Evaluar la suposición actual contra la palabra objetivo."""
        remaining_letters = {}
        for letter in self.target_word:
            remaining_letters[letter] = remaining_letters.get(letter, 0) + 1

        for col, letter in enumerate(guess):
            if letter == self.target_word[col]:
                self.tiles[self.current_row][col].set_state("correct")
                self.keyboard_keys[letter].set_state("correct")
                remaining_letters[letter] -= 1

        for col, letter in enumerate(guess):
            if letter == self.target_word[col]:
                continue

            if letter in remaining_letters and remaining_letters[letter] > 0:
                self.tiles[self.current_row][col].set_state("present")
                self.keyboard_keys[letter].set_state("present")
                remaining_letters[letter] -= 1
            else:
                self.tiles[self.current_row][col].set_state("absent")
                self.keyboard_keys[letter].set_state("absent")

    def game_win(self):
        """Manejar la condición de victoria del juego."""
        self.game_over = True
        self.win = True
        elapsed_time = time.time() - self.start_time
        attempts = self.current_row + 1

        self.show_message(
            "Congratulations!" if self.language != "spanish" else "¡Felicidades!",
            f"You won in {attempts} tries!" if self.language != "spanish" else f"¡Ganaste en {attempts} intentos!"
        )

        self.save_game_result_async(
            self.user_id,
            self.target_word,
            self.language,
            attempts,
            elapsed_time,
            True,  # Win
            self.hints_used
        )

    def game_lose(self):
        """Manejar la condición de perder del juego."""
        self.game_over = True
        self.win = False
        elapsed_time = time.time() - self.start_time
        self.show_message(
            "Game Over" if self.language != "spanish" else "¡Juego Terminado!",
            f"The word was {self.target_word}." if self.language != "spanish" else f"La palabra era {self.target_word}."
        )
        self.save_game_result_async(
            self.user_id,
            self.target_word,
            self.language,
            6,  # Max attempts
            elapsed_time,
            False,  # Loss
            self.hints_used
        )

    def use_hint(self):
        """Utiliza una pista para ayudar al jugador revelando una letra."""
        if self.hints_used >= self.max_hints or self.game_over:
            return

        self.reveal_letter_hint()

        self.hints_used += 1
        self.hints_label.setText(
            f"Hints: {self.max_hints - self.hints_used}/{self.max_hints}" if self.language != "spanish" else f"Pistas restantes: {self.max_hints - self.hints_used}/{self.max_hints}")

        if self.hints_used >= self.max_hints:
            self.hint_btn.setEnabled(False)

    def reveal_letter_hint(self):
        """Pista: Revelar una letra correcta"""
        unguessed_indices = []

        for col in range(5):
            correct = False

            for row in range(self.current_row):
                if (self.tiles[row][col].letter == self.target_word[col] and
                        self.tiles[row][col].state == "correct"):
                    correct = True
                    break

            if not correct:
                unguessed_indices.append(col)

        if not unguessed_indices:
            self.show_message("Hint" if self.language != "spanish" else "Pista",
                              "You've already found all the correct letters!" if self.language != "spanish" else "Ya has encontrado todas las letras correctas!")
            return

        col = random.choice(unguessed_indices)
        letter = self.target_word[col]

        position = col + 1
        self.show_message("Letter Hint" if self.language != "spanish" else "Pista",
                          f"The letter in position {position} is '{letter}'." if self.language != "spanish" else f"La letra en la posición {position} es '{letter}'.")

    def show_message(self, title, message):
        """Mostrar dialogo"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def save_game_result_async(self, user_id, target_word, language, attempts, time_taken, win, hints_used):
        """Guardar el resultado del juego en un hilo en segundo plano."""
        self.thread = QThread()
        self.worker = GameSaver(user_id, target_word, language, attempts, time_taken, win, hints_used)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.save_game)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.error.connect(self.handle_save_error)

        self.thread.start()

    def handle_save_error(self, error_message):
        """Manejar errores que ocurren durante el guardado del resultado del juego."""
        print(f"Error saving game result: {error_message}")

    def back_to_home(self):
        """Volver a la pantalla de inicio."""
        if not self.game_over:
            reply = QMessageBox.question(
                self,
                "Quit Game" if self.language != "spanish" else "¿Desea salir del juego?",
                "Are you sure you want to quit? Your progress will be lost." if self.language != "spanish"
                else "¿Estás seguro de que quieres salir del juego? Tu progreso se perderá.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                return

        from ui.home import HomeWindow
        self.home_window = HomeWindow(self.user_id, self.is_admin, self.language)
        self.hide()
        self.home_window.show()
