# -------------------------
# INICIO DEL CÓDIGO
# -------------------------

from nutribot_sql import recomendar_platillos, obtener_ingredientes

def recomendar_para_usuario(perfil_usuario, horario="Cena"):
    """
    Recomienda platillos para un usuario según su perfil y horario.
    - perfil_usuario: diccionario con claves 'UsuarioID', 'objetivo', 'alergias'
    - horario: nombre del horario (ej. 'Desayuno', 'Comida', 'Cena')
    """
    usuario_id = perfil_usuario.get("UsuarioID", 1)
    objetivo = perfil_usuario.get("objetivo", "Bajar de peso")
    alergias = perfil_usuario.get("alergias", "")

    # Llamada a la función SQL
    platillos = recomendar_platillos(usuario_id, objetivo, horario)

    # Filtrar platillos según alergias (si se usan como texto libre)
    if alergias:
        alergias_lista = [a.strip().lower() for a in alergias.split(",")]
        platillos = [
            p for p in platillos
            if not any(alergia in p.Nombre.lower() for alergia in alergias_lista)
        ]

    return platillos


def mostrar_detalle_platillo(platillo_id):
    """
    Devuelve los ingredientes de un platillo específico.
    """
    ingredientes = obtener_ingredientes(platillo_id)
    if ingredientes:
        detalle = f"Ingredientes del platillo {platillo_id}:\n"
        for ing in ingredientes:
            detalle += f"- {ing.Nombre}: {ing.Cantidad}\n"
        return detalle
    else:
        return "No se encontraron ingredientes para este platillo."
    
# -------------------------
# FIN DEL CÓDIGO
# -------------------------