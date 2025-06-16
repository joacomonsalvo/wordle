# Wordle

[![Ver video demostrativo](https://img.youtube.com/vi/IbtjQq47RCM/0.jpg)](https://youtu.be/IbtjQq47RCM)

*Haz clic en la imagen para ver el video demostrativo*

## 🎮 ¿Qué es Wordle?

Wordle es un juego que consiste en adivinar palabras que pone a prueba tu vocabulario y habilidades de deducción. El objetivo es adivinar una palabra oculta de 5 letras en un máximo de 6 intentos. Es ideal para demostrar tus habilidades lingüísticas.

## ✨ Características Principales

- **Interfaz intuitiva** desarrollada con PyQt6
- **Autenticación** con SHA256
- **Dos idiomas disponibles**: Inglés y Español
- **Sistema de pistas** (3 pistas por juego)
- **Estadísticas detalladas** de tus partidas
- **Exportar Estadísticas** en formato CSV
- **Panel de administración** con métricas avanzadas y acceso al Looker
- **Base de datos en tiempo real** con Supabase

## 🚀 Cómo Jugar

1. **Inicia sesión** o crea una cuenta
2. **Selecciona tu idioma** preferido
3. **Leer las Reglas** del juego
4. **Adivina la palabra** de 5 letras en 6 intentos
5. **Usa las pistas** cuando lo necesites
6. **Ver tus Estadísticas** y mejora tu performance
7. **Exportar tus Estadísticas** en formato CSV

### 🎯 Puntuación por colores

- 🟩 **Verde**: Letra correcta en la posición correcta
- 🟨 **Amarillo**: Letra correcta en posición incorrecta
- ⬜ **Gris**: Letra no está en la palabra

## 💻 Instalación

### Descarga de Binarios (Recomendado)

1. **Descarga la versión para tu sistema operativo** desde la carpeta `bin/`:
   - **Windows**: Descarga `Wordle-Windows-x64.exe`
   - **macOS**: Descarga `Wordle-macOS.dmg` o `Wordle-macOS.app.zip`

2. **Ejecuta el instalador**
   - En Windows: Haz doble clic en el archivo `.exe`
   - En macOS: Arrastra la aplicación a tu carpeta de Aplicaciones

### Instalación desde Código Fuente

#### Requisitos Previos
- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Cuenta en Supabase

#### Pasos para la Instalación

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/joacomonsalvo/wordle.git
   cd wordle
   ```

2. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura las variables de entorno**
   Crea un archivo `.env` en la raíz del proyecto con:
   ```
   SUPABASE_URL=tu_url_de_supabase
   SUPABASE_KEY=tu_clave_de_supabase
   ```

4. **Inicia la aplicación**
   ```bash
   python main.py
   ```

## 🛠 Tecnologías Utilizadas

- **Frontend**: PyQt6
- **Backend**: Python 3.9+
- **Base de Datos**: Supabase (PostgreSQL)
- **Despliegue**: Compatible con Windows y macOS

## 📊 Características Avanzadas

### Para Usuarios
- Historial detallado de partidas
- Estadísticas personales
- Progreso guardado en la nube
- Interfaz amigable y responsiva

### Para Administradores
- Panel de control con métricas
- Estadísticas de juego agregadas
