import random
import time

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.supabase_client import save_game_result


class LetterTile(QFrame):
    """A tile representing a single letter in the Wordle game."""

    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.letter = ""
        self.state = "empty"  # empty, filled, correct, present, absent

        self.setup_ui()

    def setup_ui(self):
        # Set fixed size for the tile
        self.setFixedSize(60, 60)

        # Set frame style
        self.setFrameShape(QFrame.Shape.Box)
        self.setLineWidth(2)

        # Create label for the letter
        self.letter_label = QLabel("")
        self.letter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.letter_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))

        # Add label to layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.letter_label)
        self.setLayout(layout)

        # Initial styling
        self.update_style()

    def set_letter(self, letter):
        """Set the letter for this tile."""
        self.letter = letter.upper() if letter else ""
        self.letter_label.setText(self.letter)

        if letter:
            self.state = "filled"
        else:
            self.state = "empty"

        self.update_style()

    def set_state(self, state):
        """Set the state of the tile (correct, present, absent)."""
        self.state = state
        self.update_style()

    def update_style(self):
        """Update the visual style based on the current state."""
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
    """A key on the virtual keyboard."""

    def __init__(self, text, key_press_callback):
        super().__init__(text)
        self.key = text
        self.state = "unused"  # unused, correct, present, absent

        # Connect the key press signal
        self.clicked.connect(lambda: key_press_callback(self.key))

        # Set up styling
        self.setFixedHeight(50)
        self.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.update_style()

    def set_state(self, state):
        """Set the state of the key."""
        # Only update to a 'better' state (correct > present > absent > unused)
        if (state == "correct" or
                (state == "present" and self.state != "correct") or
                (state == "absent" and self.state not in ["correct", "present"])):
            self.state = state
            self.update_style()

    def update_style(self):
        """Update the visual style based on the current state."""
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
    """The main Wordle game window."""

    def __init__(self, user_id, is_admin, language):
        super().__init__()
        self.user_id = user_id
        self.is_admin = is_admin
        self.language = language

        # Game state
        self.current_row = 0
        self.current_col = 0
        self.game_over = False
        self.win = False
        self.start_time = time.time()
        self.hints_used = 0
        self.max_hints = 3

        # Load word list based on language
        self.load_word_list()

        # Set up UI
        self.setWindowTitle("Wordle")
        self.setMinimumSize(600, 700)
        self.setup_ui()

    def load_word_list(self):
        """Load word list based on selected language from the database."""
        from database.supabase_client import get_words_for_game

        # Get language name in the format expected by the database
        language_name = "english" if self.language == "english" else "spanish"

        # Get words from the database
        self.valid_words = get_words_for_game(language_name)
        # Select a random target word from the valid words
        if self.valid_words:
            self.target_word = random.choice(self.valid_words).upper()
        else:
            self.target_word = "ERROR"  # Fallback in case no words are loaded

    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Header with game title and back button
        header = QWidget()
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)

        back_btn = QPushButton("Back to Home")
        back_btn.clicked.connect(self.back_to_home)

        title_label = QLabel("WORDLE")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hints_layout = QHBoxLayout()
        hints_label = QLabel(f"Hints: {self.max_hints - self.hints_used}/{self.max_hints}")
        hint_btn = QPushButton("Use Hint")
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

        # Game board (6x5 grid of tiles)
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

        # Virtual keyboard
        keyboard_widget = QWidget()
        keyboard_layout = QVBoxLayout()
        keyboard_widget.setLayout(keyboard_layout)

        # Create keyboard rows
        self.keyboard_keys = {}

        # Row 1: Q-P
        row1_layout = QHBoxLayout()
        row1_keys = "QWERTYUIOP"
        for key in row1_keys:
            key_btn = KeyboardKey(key, self.key_pressed)
            row1_layout.addWidget(key_btn)
            self.keyboard_keys[key] = key_btn

        # Row 2: A-L
        row2_layout = QHBoxLayout()
        row2_layout.addSpacing(15)
        row2_keys = "ASDFGHJKL"
        for key in row2_keys:
            key_btn = KeyboardKey(key, self.key_pressed)
            row2_layout.addWidget(key_btn)
            self.keyboard_keys[key] = key_btn
        row2_layout.addSpacing(15)

        # Row 3: Enter, Z-M, Backspace
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

        # Add keyboard rows to layout
        keyboard_layout.addLayout(row1_layout)
        keyboard_layout.addLayout(row2_layout)
        keyboard_layout.addLayout(row3_layout)

        # Add widgets to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(board_widget)
        main_layout.addStretch()
        main_layout.addWidget(keyboard_widget)

    def key_pressed(self, key):
        """Handle a key press on the virtual keyboard."""
        if self.game_over:
            return

        if key == "ENTER":
            self.submit_guess()
        elif key == "⌫":
            self.delete_letter()
        else:
            self.add_letter(key)

    def add_letter(self, letter):
        """Add a letter to the current position."""
        if self.current_col < 5:
            self.tiles[self.current_row][self.current_col].set_letter(letter)
            self.current_col += 1

    def delete_letter(self):
        """Delete the last letter entered."""
        if self.current_col > 0:
            self.current_col -= 1
            self.tiles[self.current_row][self.current_col].set_letter("")

    def submit_guess(self):
        """Submit the current guess for evaluation."""
        # Check if the row is complete
        if self.current_col < 5:
            self.show_message("Not enough letters", "Please enter a 5-letter word.")
            return

        # Get the current guess
        guess = ""
        for col in range(5):
            guess += self.tiles[self.current_row][col].letter

        # Evaluate the guess against the target word
        self.evaluate_guess(guess)

        # Check for win or game over
        if guess == self.target_word:
            self.game_win()
        elif self.current_row >= 5:
            self.game_lose()
        else:
            # Move to the next row
            self.current_row += 1
            self.current_col = 0

    def evaluate_guess(self, guess):
        """Evaluate the current guess against the target word."""
        # Create a dictionary to track remaining letters in the target word
        remaining_letters = {}
        for letter in self.target_word:
            remaining_letters[letter] = remaining_letters.get(letter, 0) + 1

        # First pass: mark correct letters
        for col, letter in enumerate(guess):
            if letter == self.target_word[col]:
                self.tiles[self.current_row][col].set_state("correct")
                self.keyboard_keys[letter].set_state("correct")
                remaining_letters[letter] -= 1

        # Second pass: mark present or absent letters
        for col, letter in enumerate(guess):
            if letter == self.target_word[col]:
                # Already marked as correct in the first pass
                continue

            if letter in remaining_letters and remaining_letters[letter] > 0:
                self.tiles[self.current_row][col].set_state("present")
                self.keyboard_keys[letter].set_state("present")
                remaining_letters[letter] -= 1
            else:
                self.tiles[self.current_row][col].set_state("absent")
                self.keyboard_keys[letter].set_state("absent")

    def game_win(self):
        """Handle game win condition."""
        self.game_over = True
        self.win = True
        elapsed_time = time.time() - self.start_time

        # Save game result to database
        try:
            save_game_result(
                self.user_id,
                self.target_word,
                self.language,
                self.current_row + 1,  # Number of attempts
                elapsed_time,
                True,  # Win
                self.hints_used
            )
        except Exception as e:
            print(f"Error saving game result: {e}")

        # Show win message
        self.show_message("Congratulations!", f"You won in {self.current_row + 1} tries!")

    def game_lose(self):
        """Handle game lose condition."""
        self.game_over = True
        self.win = False
        elapsed_time = time.time() - self.start_time

        # Save game result to database
        try:
            save_game_result(
                self.user_id,
                self.target_word,
                self.language,
                6,  # Max attempts
                elapsed_time,
                False,  # Loss
                self.hints_used
            )
        except Exception as e:
            print(f"Error saving game result: {e}")

        # Show lose message
        self.show_message("Game Over", f"The word was {self.target_word}.")

    def use_hint(self):
        """Use a hint to help the player by revealing a letter."""
        if self.hints_used >= self.max_hints or self.game_over:
            return

        # Reveal a letter hint
        self.reveal_letter_hint()

        # Update hint count
        self.hints_used += 1
        self.hints_label.setText(f"Hints: {self.max_hints - self.hints_used}/{self.max_hints}")

        # Disable hint button if all hints used
        if self.hints_used >= self.max_hints:
            self.hint_btn.setEnabled(False)

    def reveal_letter_hint(self):
        """Hint: Reveal a correct letter."""
        # Find letters that haven't been correctly guessed yet
        unguessed_indices = []

        for col in range(5):
            correct = False

            # Check if this letter has been correctly guessed in previous rows
            for row in range(self.current_row):
                if (self.tiles[row][col].letter == self.target_word[col] and
                        self.tiles[row][col].state == "correct"):
                    correct = True
                    break

            if not correct:
                unguessed_indices.append(col)

        if not unguessed_indices:
            self.show_message("Hint", "You've already found all the correct letters!")
            return

        # Choose a random unguessed letter to reveal
        col = random.choice(unguessed_indices)
        letter = self.target_word[col]

        # Show hint message
        position = col + 1
        self.show_message("Letter Hint", f"The letter in position {position} is '{letter}'.")

    def show_message(self, title, message):
        """Show a message dialog to the user."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def back_to_home(self):
        """Return to the home screen."""
        if not self.game_over:
            reply = QMessageBox.question(
                self,
                "Quit Game",
                "Are you sure you want to quit? Your progress will be lost.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                return

        from ui.home import HomeWindow
        self.home_window = HomeWindow(self.user_id, self.is_admin, self.language)
        self.hide()
        self.home_window.show()
