import os
import hashlib
import hmac
from supabase import create_client, Client

# Global Supabase client instance
_supabase_client = None


def initialize_supabase() -> Client:
    """Initialize and return the Supabase client."""
    global _supabase_client

    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and key must be set in .env file")

        _supabase_client = create_client(supabase_url, supabase_key)

    return _supabase_client


def get_supabase_client() -> Client:
    """Get the initialized Supabase client."""
    global _supabase_client

    if _supabase_client is None:
        return initialize_supabase()

    return _supabase_client


# User Authentication Functions
def sign_up(username: str, password: str, email: str = None) -> dict:
    """Register a new user."""
    client = get_supabase_client()

    # Check if username already exists
    existing = client.table("usuarios").select("id").eq("nombre_usuario", username).execute()
    if existing.data:
        raise ValueError("Username already exists")

    # Hash the password
    hashed_password = hash_password(password)

    # Assume tipo_usuario_id = 1 is for non-admin users.
    # You might need to adjust this based on your 'tipo_usuario' table setup.
    tipo_usuario_id_for_new_user = 1

    # Create user
    result = client.table("usuarios").insert({
        "nombre_usuario": username,
        "contrasena": hashed_password,
        "email": email,
        "tipo_usuario_id": tipo_usuario_id_for_new_user
    }).execute()

    if not result.data or len(result.data) == 0:
        raise ValueError("Failed to create user")

    return result.data[0]


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a salt."""
    salt = "wordle_salt"  # In a real app, use a unique salt per user
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


def reset_user_password(username: str, new_password: str) -> dict:
    """Reset a user's password in the usuarios table."""
    client = get_supabase_client()

    # First check if the user exists
    user_result = client.table("usuarios").select("id").eq("nombre_usuario", username).execute()
    if not user_result.data or len(user_result.data) == 0:
        raise ValueError("User not found")

    # Hash the new password
    hashed_password = hash_password(new_password)

    # Update the user's password
    result = client.table("usuarios").update({"contrasena": hashed_password}).eq("nombre_usuario", username).execute()

    if not result.data or len(result.data) == 0:
        raise ValueError("Failed to update password")

    return result.data[0]


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return hmac.compare_digest(hash_password(password), hashed)


def sign_out() -> None:
    """Sign out the current user."""
    # Since we're using custom auth, we just need to clear any local state
    # No need to call Supabase auth signout
    pass


def sign_in(username: str, password: str) -> dict:
    """Sign in an existing user."""
    client = get_supabase_client()

    # Get user by username and join with tipo_usuario to get admin status Adjust the select query if your Supabase
    # client library has a different way to do joins or select specific columns from joined tables. This is a
    # conceptual representation. The actual Supabase query might need to be structured differently, possibly using a
    # view or an RPC function if direct join syntax in select isn't straightforward. For now, we'll fetch from
    # 'usuarios' and then separately query 'tipo_usuario' or assume 'tipo_usuario_id' directly maps to admin status
    # if simple.

    user_result = client.table("usuarios").select("id, nombre_usuario, contrasena, email, tipo_usuario_id").eq(
        "nombre_usuario", username).execute()

    if not user_result.data or len(user_result.data) == 0:
        raise ValueError("Invalid username or password")

    user_data = user_result.data[0]

    # Verify password
    if not verify_password(password, user_data["contrasena"]):
        raise ValueError("Invalid username or password")

    # Fetch admin status from tipo_usuario table
    tipo_usuario_id = user_data.get("tipo_usuario_id")
    is_admin_status = False
    if tipo_usuario_id:
        tipo_usuario_result = client.table("tipo_usuario").select("es_administrador").eq("id",
                                                                                         tipo_usuario_id).execute()
        if tipo_usuario_result.data and len(tipo_usuario_result.data) > 0:
            is_admin_status = tipo_usuario_result.data[0].get("es_administrador", False)

    # Add admin status to the user data to be returned
    user_data['is_admin'] = is_admin_status

    return user_data


def get_user_profile(user_id: int) -> dict:
    """Get user profile data from 'usuarios' table."""
    client = get_supabase_client()
    result = client.table("usuarios").select("id, nombre_usuario, email, tipo_usuario_id").eq("id", user_id).execute()

    if not result.data or len(result.data) == 0:
        # Changed to check for empty data list as .single() is removed
        raise ValueError("User not found")

    return result.data[0]


def is_admin(user_id: int) -> bool:
    """Check if user is an administrator by looking up their tipo_usuario_id."""
    client = get_supabase_client()
    user_profile = get_user_profile(user_id)  # This now fetches from 'usuarios'

    tipo_usuario_id = user_profile.get("tipo_usuario_id")
    if tipo_usuario_id is None:
        return False

    tipo_usuario_result = client.table("tipo_usuario").select("es_administrador").eq("id", tipo_usuario_id).execute()

    if tipo_usuario_result.data and len(tipo_usuario_result.data) > 0:
        return tipo_usuario_result.data[0].get("es_administrador", False)

    return False


# Helper function to get idioma_id from language name
def _get_idioma_id(language_name: str) -> int:
    client = get_supabase_client()
    result = client.table("idiomas").select("id").eq("idioma", language_name).execute()
    if not result.data or len(result.data) == 0:
        raise ValueError(f"Language '{language_name}' not found in 'idiomas' table.")
    return result.data[0]['id']


# Helper function to get palabra_id from word string and idioma_id
def _get_palabra_id(word_text: str, idioma_id: int) -> int:
    client = get_supabase_client()
    result = client.table("palabras").select("id").eq("palabra", word_text.lower()).eq("idioma_id", idioma_id).execute()
    if not result.data or len(result.data) == 0:
        raise ValueError(f"Word '{word_text}' not found for language ID {idioma_id} in 'palabras' table.")
    return result.data[0]['id']


# Game Data Functions
def save_game_result(user_id: int, word: str, language: str, attempts: int, time_taken: float, win: bool,
                     hints_used: int):
    """Save game result to 'partidas' table."""
    client = get_supabase_client()

    idioma_id = _get_idioma_id(language)  # 'English' or 'Spanish'
    palabra_id = _get_palabra_id(word, idioma_id)

    result = client.table("partidas").insert({
        "usuario_id": user_id,
        "palabra_id": palabra_id,
        "adivinada": win,
        "intentos": attempts,
        "time_taken": time_taken,
        "hints_used": hints_used
    }).execute()

    if not result.data or len(result.data) == 0:
        raise ValueError("Failed to save game result to 'partidas' table.")
    return result.data[0]


def get_user_statistics(user_id: int) -> list:
    """Get statistics for a specific user from 'partidas' table."""
    client = get_supabase_client()

    try:
        # Get all partidas for this user
        result = client.table("partidas").select("*").eq("usuario_id", user_id).execute()
        partidas = result.data if result.data else []

        if not partidas:
            return []

        # Get palabra_ids from partidas
        palabra_ids = [partida["palabra_id"] for partida in partidas]

        # Get palabras information
        palabras_result = client.table("palabras").select("id, palabra, idioma_id").in_("id", palabra_ids).execute()
        palabras = palabras_result.data if palabras_result.data else []

        if not palabras:
            return []

        # Create a mapping of palabra_id to palabra info
        palabra_map = {palabra["id"]: palabra for palabra in palabras}

        # Get idioma_ids from palabras
        idioma_ids = list(set(palabra["idioma_id"] for palabra in palabras))

        # Get idiomas information
        idiomas_result = client.table("idiomas").select("id, idioma").in_("id", idioma_ids).execute()
        idiomas = idiomas_result.data if idiomas_result.data else []

        if not idiomas:
            return []

        # Create a mapping of idioma_id to idioma name
        idioma_map = {idioma["id"]: idioma["idioma"] for idioma in idiomas}

        # Format the data for the UI
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
        print(f"Error getting user statistics: {e}")
        return []


def get_all_statistics() -> list:
    """Get statistics for all users (admin only) from 'partidas' table."""
    client = get_supabase_client()

    try:
        # Get all partidas
        result = client.table("partidas").select("*").execute()
        partidas = result.data if result.data else []

        if not partidas:
            return []

        # Get all unique user_ids and palabra_ids
        user_ids = list(set(partida["usuario_id"] for partida in partidas))
        palabra_ids = list(set(partida["palabra_id"] for partida in partidas))

        # Get user information
        users_result = client.table("usuarios").select("id, nombre_usuario").in_("id", user_ids).execute()
        users = users_result.data if users_result.data else []

        # Create a mapping of user_id to username
        user_map = {user["id"]: user["nombre_usuario"] for user in users}

        # Get palabras information
        palabras_result = client.table("palabras").select("id, palabra, idioma_id").in_("id", palabra_ids).execute()
        palabras = palabras_result.data if palabras_result.data else []

        # Create a mapping of palabra_id to palabra info
        palabra_map = {palabra["id"]: palabra for palabra in palabras}

        # Get idioma_ids from palabras
        idioma_ids = list(set(palabra["idioma_id"] for palabra in palabras))

        # Get idiomas information
        idiomas_result = client.table("idiomas").select("id, idioma").in_("id", idioma_ids).execute()
        idiomas = idiomas_result.data if idiomas_result.data else []

        # Create a mapping of idioma_id to idioma name
        idioma_map = {idioma["id"]: idioma["idioma"] for idioma in idiomas}

        # Format the data for the UI
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
        print(f"Error getting all statistics: {e}")
        return []


def get_language_distribution() -> list:
    """Get language distribution statistics from 'partidas', joining with 'palabras' and 'idiomas'."""
    client = get_supabase_client()
    # This requires joining 'partidas' with 'palabras' then 'idiomas' and grouping by 'idiomas.idioma'. This might be
    # best done with an SQL view or an RPC function in Supabase for simplicity here. For example, an RPC function
    # 'get_language_game_counts()'. A simplified version for now, assuming direct query capabilities or that the UI
    # can process raw IDs: This is a conceptual query. The actual implementation might require an RPC call for this
    # aggregation. result = client.rpc('get_language_distribution_stats').execute() Fallback: Fetch all partidas and
    # process in Python, or adjust if your client supports complex joins for aggregation. The direct Supabase query
    # for this is non-trivial with group by on a joined table's column. Let's assume we have an RPC or will process
    # this client-side for now. As a placeholder, returning raw language IDs from 'palabras' referenced in
    # 'partidas': This is NOT the final desired output but a step if direct complex query is not used. A proper
    # solution would be an RPC: CREATE FUNCTION get_lang_distro() RETURNS TABLE(language_name TEXT, game_count
    # BIGINT) ... For now, we'll return something that the admin panel might need to further process or we can refine
    # this with an RPC call. Since we don't have an RPC function, we'll implement this in Python by fetching the
    # necessary data and processing it.
    try:
        result = client.table("partidas").select("palabra_id").execute()
        partidas = result.data

        if not partidas:
            return []

        palabra_ids = [partida["palabra_id"] for partida in partidas]

        # Fetch palabras and their corresponding idioma_ids
        palabras_result = client.table("palabras").select("id, idioma_id").in_("id", palabra_ids).execute()
        palabras = palabras_result.data

        if not palabras:
            return []

        # Create a dictionary to store language distribution
        language_distribution = {}

        for palabra in palabras:
            idioma_id = palabra["idioma_id"]
            if idioma_id not in language_distribution:
                language_distribution[idioma_id] = 1
            else:
                language_distribution[idioma_id] += 1

        # Fetch idioma names from idiomas table
        idiomas_result = client.table("idiomas").select("id, idioma").in_("id",
                                                                          list(language_distribution.keys())).execute()
        idiomas = idiomas_result.data

        if not idiomas:
            return []

        # Create a list to store language distribution with names
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
        print(
            f"Error calling RPC get_language_stats: {e}. Returning empty list. You may need to create this RPC "
            f"function in Supabase.")
        return []


def get_words_for_game(language_name: str, word_length: int = 5) -> list:
    """Get all words for a specific language from the 'palabras' table."""
    client = get_supabase_client()

    try:
        # Get the idioma_id for the specified language
        idioma_id = _get_idioma_id(language_name)

        # Get all words for this language
        result = client.table("palabras").select("palabra").eq("idioma_id", idioma_id).execute()

        if not result.data:
            return []

        # Filter words by length and convert to uppercase
        words = [word["palabra"].upper() for word in result.data if len(word["palabra"]) == word_length]

        return words
    except Exception as e:
        print(f"Error getting words for game: {e}")
        return []
