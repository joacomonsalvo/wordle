import sys
import os
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator, QLocale

from ui.login import LoginWindow
from database.supabase_client import initialize_supabase

def get_base_path():
    # When running as a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    # When running as a normal Python script
    return os.path.abspath(".")

def main():
    # Load environment variables
    # Load .env from the bundle
    env_path = os.path.join(get_base_path(), ".env")
    prod_path = os.path.join(get_base_path(), ".env.prod")

    if os.path.exists(prod_path):
        load_dotenv(prod_path)
    elif os.path.exists(env_path):
        load_dotenv(env_path)
    
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