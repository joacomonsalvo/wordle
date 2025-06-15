from setuptools import setup, find_packages
import sys
import os
from pathlib import Path
from shutil import copyfile

# Copiar .env a .env.prod si no existe
if not os.path.exists('.env.prod') and os.path.exists('.env'):
    copyfile('.env', '.env.prod')

# Dependencias básicas
install_requires = [
    'PyQt6>=6.4.0',
    'supabase>=1.0.3',
    'python-dotenv>=0.19.0',
    'pyinstaller>=5.0',
]

# Dependencias específicas de Windows
if sys.platform == 'win32':
    install_requires.append('pywin32>=303')

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).parent

setup(
    name="Wordle",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.env*', '*.json', '*.png', '*.ico', '*.icns'],
    },
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'wordle=main:main',
        ],
    },
    author="Joaquin Monsalvo, Felipe Muhlich, Thiago Payba, Juan Pascua",
    description="Wordle: Un juego ludico de palabras!",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
