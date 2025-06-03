# Juego Wordle

Una implementación en PyQt6 del popular juego Wordle con integración de Supabase, compatible con idiomas inglés y español.

## Características

- Funcionalidad de inicio de sesión y registro
- Recuperación de contraseña
- Soporte multiidioma (inglés y español)
- Página de reglas del juego
- Seguimiento de estadísticas para usuarios
- Panel de administración con estadísticas mejoradas
- Tres pistas por juego

## Configuración

1. Instala las dependencias requeridas:
```
pip install -r requirements.txt
```

2. Configura las credenciales de Supabase:
Crea un archivo `.env` en el directorio raíz con las siguientes variables:
```
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_clave_de_supabase
```

3. Ejecuta la aplicación:
```
python main.py
```

## Reglas del Juego

Wordle es un juego de adivinar palabras donde tienes 6 intentos para adivinar una palabra de 5 letras:
- Verde: La letra está en la palabra y en la posición correcta
- Amarillo: La letra está en la palabra pero en la posición incorrecta
- Gris: La letra no está en la palabra

## Tecnologías Utilizadas

- Python 3.9+
- PyQt6
- Supabase