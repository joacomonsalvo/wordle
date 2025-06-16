import os
import hashlib
import hmac
from supabase import create_client, Client

# Instancia global de Supabase
_supabase_client = None


def initialize_supabase() -> Client:
    """Inicializar y Devolver Supabase Client"""
    global _supabase_client

    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and key must be set in .env file")

        _supabase_client = create_client(supabase_url, supabase_key)

    return _supabase_client


def get_supabase_client() -> Client:
    """Obtener el cliente Supabase inicializado."""
    global _supabase_client

    if _supabase_client is None:
        return initialize_supabase()

    return _supabase_client


# Funciones de Autenticación de Usuario
def sign_up(username: str, password: str, email: str = None) -> dict:
    """Registrar un nuevo usuario."""
    client = get_supabase_client()

    # Verificar si el nombre de usuario ya existe
    existing = client.table("usuarios").select("id").eq("nombre_usuario", username).execute()
    if existing.data:
        raise ValueError("El nombre de usuario ya existe")

    # Hashear la contraseña
    hashed_password = hash_password(password)

    # Asumir que tipo_usuario_id = 1 es para usuarios no administradores.
    # Debes ajustar esto según la configuración de tu tabla 'tipo_usuario'
    tipo_usuario_id_for_new_user = 1

    # Crear usuario
    result = client.table("usuarios").insert({
        "nombre_usuario": username,
        "contrasena": hashed_password,
        "email": email,
        "tipo_usuario_id": tipo_usuario_id_for_new_user
    }).execute()

    if not result.data or len(result.data) == 0:
        raise ValueError("Error al crear el usuario")

    return result.data[0]


def hash_password(password: str) -> str:
    """Hashear una contraseña usando SHA-256 con una sal."""
    salt = "wordle_salt" 
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


def reset_user_password(username: str, new_password: str) -> dict:
    """Restablecer la contraseña de un usuario en la tabla 'usuarios'"""
    client = get_supabase_client()

    # Verificar si el usuario existe
    user_result = client.table("usuarios").select("id").eq("nombre_usuario", username).execute()
    if not user_result.data or len(user_result.data) == 0:
        raise ValueError("Usuario no encontrado")

    # Hashear la nueva contraseña
    hashed_password = hash_password(new_password)

    # Actualizar la contraseña del usuario
    result = client.table("usuarios").update({"contrasena": hashed_password}).eq("nombre_usuario", username).execute()

    if not result.data or len(result.data) == 0:
        raise ValueError("Error al actualizar la contraseña")

    return result.data[0]


def verify_password(password: str, hashed: str) -> bool:
    """Verificar una contraseña contra su hash."""
    return hmac.compare_digest(hash_password(password), hashed)


def sign_out() -> None:
    """Cerrar sesión del usuario actual."""
    pass


def sign_in(username: str, password: str) -> dict:
    """Iniciar sesión de un usuario existente."""
    client = get_supabase_client()


    user_result = client.table("usuarios").select("id, nombre_usuario, contrasena, email, tipo_usuario_id").eq(
        "nombre_usuario", username).execute()

    if not user_result.data or len(user_result.data) == 0:
        raise ValueError("Nombre de usuario o contraseña invalidos")

    user_data = user_result.data[0]

    # Verificar contraseña
    if not verify_password(password, user_data["contrasena"]):
        raise ValueError("Nombre de usuario o contraseña invalidos")

    # Obtener el tipo de usuario
    tipo_usuario_id = user_data.get("tipo_usuario_id")
    is_admin_status = False
    if tipo_usuario_id:
        tipo_usuario_result = client.table("tipo_usuario").select("es_administrador").eq("id",
                                                                                         tipo_usuario_id).execute()
        if tipo_usuario_result.data and len(tipo_usuario_result.data) > 0:
            is_admin_status = tipo_usuario_result.data[0].get("es_administrador", False)

    # Agregar el estado de administrador al usuario
    user_data['is_admin'] = is_admin_status

    return user_data


def get_user_profile(user_id: int) -> dict:
    """Obtener el perfil de un usuario."""
    client = get_supabase_client()
    result = client.table("usuarios").select("id, nombre_usuario, email, tipo_usuario_id").eq("id", user_id).execute()

    if not result.data or len(result.data) == 0:
        raise ValueError("Usuario no encontrado")

    return result.data[0]


def is_admin(user_id: int) -> bool:
    """Verificar si un usuario es administrador."""
    client = get_supabase_client()
    user_profile = get_user_profile(user_id)

    tipo_usuario_id = user_profile.get("tipo_usuario_id")
    if tipo_usuario_id is None:
        return False

    tipo_usuario_result = client.table("tipo_usuario").select("es_administrador").eq("id", tipo_usuario_id).execute()

    if tipo_usuario_result.data and len(tipo_usuario_result.data) > 0:
        return tipo_usuario_result.data[0].get("es_administrador", False)

    return False


def _get_idioma_id(language_name: str) -> int:
    client = get_supabase_client()
    result = client.table("idiomas").select("id").eq("idioma", language_name).execute()
    if not result.data or len(result.data) == 0:
        raise ValueError(f"Idioma '{language_name}' no encontrado en la tabla 'idiomas'.")
    return result.data[0]['id']


def _get_palabra_id(word_text: str, idioma_id: int) -> int:
    client = get_supabase_client()
    result = client.table("palabras").select("id").eq("palabra", word_text.lower()).eq("idioma_id", idioma_id).execute()
    if not result.data or len(result.data) == 0:
        raise ValueError(f"Palabra '{word_text}' no encontrada para el idioma ID {idioma_id} en la tabla 'palabras'.")
    return result.data[0]['id']


def save_game_result(user_id: int, word: str, language: str, attempts: int, time_taken: float, win: bool,
                     hints_used: int):
    """Guardar el resultado del juego en la tabla 'partidas'"""
    try:
        if not user_id or not word or not language:
            raise ValueError("Faltan parámetros")
            
        client = get_supabase_client()
        if not client:
            raise Exception("Error al Inicializar el Cliente de Supabase")

        idioma_id = _get_idioma_id(language)
        if not idioma_id:
            raise ValueError(f"Idioma '{language}' no encontrado en la tabla 'idiomas'.")

        palabra_id = _get_palabra_id(word, idioma_id)
        if not palabra_id:
            try:
                result = client.table("palabras").insert({
                    "palabra": word.lower(),
                    "idioma_id": idioma_id
                }).execute()
                
                if not result.data:
                    raise Exception("Error al insertar la palabra en la tabla 'palabras'")
                    
                palabra_id = result.data[0]["id"]
            except Exception as e:
                print(f"Error al insertar la palabra en la tabla 'palabras': {str(e)}")

                palabra_id = _get_palabra_id(word, idioma_id)
                if not palabra_id:
                    raise Exception("Error al obtener o crear la palabra en la base de datos")

        result = client.table("partidas").insert({
            "usuario_id": user_id,
            "palabra_id": palabra_id,
            "adivinada": win,
            "intentos": attempts,
            "time_taken": time_taken,
            "hints_used": hints_used
        }).execute()

        if not result.data or len(result.data) == 0:
            raise ValueError("Error al guardar el resultado del juego en la tabla 'partidas'")
            
        return result.data[0]
        
    except Exception as e:
        print(f"Error al guardar el resultado del juego en la tabla 'partidas': {str(e)}")
        raise


def get_user_statistics(user_id: int) -> list:
    """Obtener estadísticas para un usuario específico de la tabla 'partidas'"""
    client = get_supabase_client()

    try:
        result = client.table("partidas").select("*").eq("usuario_id", user_id).execute()
        partidas = result.data if result.data else []

        if not partidas:
            return []

        palabra_ids = [partida["palabra_id"] for partida in partidas]

        palabras_result = client.table("palabras").select("id, palabra, idioma_id").in_("id", palabra_ids).execute()
        palabras = palabras_result.data if palabras_result.data else []

        if not palabras:
            return []

        palabra_map = {palabra["id"]: palabra for palabra in palabras}

        idioma_ids = list(set(palabra["idioma_id"] for palabra in palabras))

        idiomas_result = client.table("idiomas").select("id, idioma").in_("id", idioma_ids).execute()
        idiomas = idiomas_result.data if idiomas_result.data else []

        if not idiomas:
            return []

        idioma_map = {idioma["id"]: idioma["idioma"] for idioma in idiomas}

        formatted_data = []
        for partida in partidas:
            palabra_id = partida["palabra_id"]
            palabra_info = palabra_map.get(palabra_id, {})
            idioma_id = palabra_info.get("idioma_id")
            idioma_name = idioma_map.get(idioma_id, "Unknown")

            formatted_data.append({
                "created_at": partida.get("created_at", ""),
                "word": palabra_info.get("palabra", ""),
                "language": "spanish" if idioma_name and idioma_name.lower() in ["español", "spanish"] else "english",
                "attempts": partida.get("intentos", 0),
                "time_taken": partida.get("time_taken", 0),
                "win": partida.get("adivinada", False),
                "hints_used": partida.get("hints_used", 0)
            })
        return formatted_data
    except Exception as e:
        print(f"Error al obtener las estadísticas del usuario: {e}")
        return []


def get_all_statistics() -> list:
    """Obtener estadísticas para todos los usuarios (solo administrador) de la tabla 'partidas'"""
    client = get_supabase_client()

    try:
        result = client.table("partidas").select("*").execute()
        partidas = result.data if result.data else []

        if not partidas:
            return []

        user_ids = list(set(partida["usuario_id"] for partida in partidas))
        palabra_ids = list(set(partida["palabra_id"] for partida in partidas))

        users_result = client.table("usuarios").select("id, nombre_usuario").in_("id", user_ids).execute()
        users = users_result.data if users_result.data else []

        user_map = {user["id"]: user["nombre_usuario"] for user in users}

        palabras_result = client.table("palabras").select("id, palabra, idioma_id").in_("id", palabra_ids).execute()
        palabras = palabras_result.data if palabras_result.data else []

        palabra_map = {palabra["id"]: palabra for palabra in palabras}

        idioma_ids = list(set(palabra["idioma_id"] for palabra in palabras))

        idiomas_result = client.table("idiomas").select("id, idioma").in_("id", idioma_ids).execute()
        idiomas = idiomas_result.data if idiomas_result.data else []

        idioma_map = {idioma["id"]: idioma["idioma"] for idioma in idiomas}

        formatted_data = []
        for partida in partidas:
            user_id = partida["usuario_id"]
            palabra_id = partida["palabra_id"]

            username = user_map.get(user_id, "Unknown")
            palabra_info = palabra_map.get(palabra_id, {})
            idioma_id = palabra_info.get("idioma_id")
            idioma_name = idioma_map.get(idioma_id, "Unknown")

            formatted_data.append({
                "username": username,
                "created_at": partida.get("created_at", ""),
                "word": palabra_info.get("palabra", ""),
                "language": "spanish" if idioma_name and idioma_name.lower() in ["español", "spanish"] else "english",
                "attempts": partida.get("intentos", 0),
                "time_taken": partida.get("time_taken", 0),
                "win": partida.get("adivinada", False),
                "hints_used": partida.get("hints_used", 0)
            })
        return formatted_data
    except Exception as e:
        print(f"Error al obtener las estadísticas de todos los usuarios: {e}")
        return []


def get_language_distribution() -> list:
    """Obtener estadísticas de distribución de idiomas de la tabla 'partidas', uniendo con 'palabras' y 'idiomas'."""
    client = get_supabase_client()

    try:
        result = client.table("partidas").select("palabra_id").execute()
        partidas = result.data

        if not partidas:
            return []

        palabra_ids = [partida["palabra_id"] for partida in partidas]

        palabras_result = client.table("palabras").select("id, idioma_id").in_("id", palabra_ids).execute()
        palabras = palabras_result.data

        if not palabras:
            return []

        language_distribution = {}

        for palabra in palabras:
            idioma_id = palabra["idioma_id"]
            if idioma_id not in language_distribution:
                language_distribution[idioma_id] = 1
            else:
                language_distribution[idioma_id] += 1

        idiomas_result = client.table("idiomas").select("id, idioma").in_("id",
                                                                          list(language_distribution.keys())).execute()
        idiomas = idiomas_result.data

        if not idiomas:
            return []

        language_distribution_list = []

        for idioma in idiomas:
            idioma_id = idioma["id"]
            idioma_name = idioma["idioma"]
            game_count = language_distribution[idioma_id]
            language_distribution_list.append({
                "language_name": idioma_name,
                "game_count": game_count
            })

        return language_distribution_list
    except Exception as e:
        print(f"Error al obtener las estadísticas de distribución de idiomas: {e}")
        return []


def get_words_for_game(language_name: str, word_length: int = 5):
    """Obtener todas las palabras para un idioma específico de la tabla 'palabras'"""
    try:
        client = get_supabase_client()
        if not client:
            raise Exception("Error al Inicializar el Cliente de Supabase")

        idioma_id = _get_idioma_id(language_name)
        if not idioma_id:
            raise ValueError(f"Idioma Invalido: {language_name}")

        result = client.table("palabras").select("palabra").eq("idioma_id", idioma_id).execute()
        
        if not result.data:
            raise Exception("No data returned from database")
            
        words = [item["palabra"].upper() for item in result.data if len(item["palabra"]) == word_length]

        if not words and result.data:
            words = [item["palabra"].upper() for item in result.data]

        if not words:
            default_words = ["HELLO", "WORLD", "PYTHON", "JAZZY", "QUICK"] if language_name == "english" else \
                          ["HOLA", "MUNDO", "PYTHON", "JAZZ", "RAPID"]
            return default_words

        return words
    except Exception as e:
        print(f"Error al obtener las palabras para el juego: {str(e)}")
        # Return default words in case of any error
        return ["HELLO", "WORLD", "PYTHON", "JAZZY", "QUICK"] if language_name == "english" else \
               ["HOLA", "MUNDO", "PYTHON", "JAZZ", "RAPID"]