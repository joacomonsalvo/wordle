# Wordle Game

A PyQt6 implementation of the popular Wordle game with Supabase integration, supporting both English and Spanish languages.

## Features

- Login and signup functionality
- Password recovery
- Multilingual support (English and Spanish)
- Game rules page
- Statistics tracking for users
- Admin panel with enhanced statistics
- Three hints per game

## Setup

1. Install the required dependencies:
```
pip install -r requirements.txt
```

2. Set up Supabase credentials:
Create a `.env` file in the root directory with the following variables:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

3. Run the application:
```
python main.py
```

## Game Rules

Wordle is a word-guessing game where you have 6 attempts to guess a 5-letter word:
- Green: Letter is in the word and in the correct position
- Yellow: Letter is in the word but in the wrong position
- Gray: Letter is not in the word

## Technologies Used

- Python 3.9+
- PyQt6
- Supabase
