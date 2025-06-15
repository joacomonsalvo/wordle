import sys
import os
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator, QLocale

from ui.login import LoginWindow
from database.supabase_client import initialize_supabase

def main():
    # Load environment variables
    load_dotenv()
    
    # Check if Supabase credentials are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("Error: Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY in .env file.")
        sys.exit(1)
    
    # Initialize Supabase client
    initialize_supabase()
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set up translator for internationalization
    translator = QTranslator()
    app.installTranslator(translator)
    
    # Show login window
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()