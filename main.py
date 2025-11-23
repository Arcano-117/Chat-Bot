import tkinter as tk
import datetime
from registro import mostrar_formulario, cargar_ultimo_usuario
from nutribot_sql import (
    recomendar_platillos,
    obtener_ingredientes,
    agregar_ingrediente,
    eliminar_ingrediente,
    cambiar_ingrediente,
    obtener_nombre_platillo,
    ejecutar_consulta
)
from respuestas_locales import obtener_respuesta_local

# -------------------------
# VARIABLES GLOBALES
# -------------------------
perfil_usuario = cargar_ultimo_usuario() or {}
platillo_seleccionado = None
nombre_platillo_seleccionado = None

# -------------------------
# FUNCIONES AUXILIARES
# -------------------------
def registrar_usuario(chat_widget):
    """
    Abre el formulario de registro y muestra el perfil en el chat principal.
    """
    global perfil_usuario
    perfil_usuario = mostrar_formulario()
    if perfil_usuario:
        resumen = (
            f"Nombre: {perfil_usuario.get('nombre','')}\n"
            f"Edad: {perfil_usuario.get('edad','')} años\n"
            f"Peso: {perfil_usuario.get('peso','')} kg\n"
            f"Altura: {perfil_usuario.get('altura','')} cm\n"
            f"Objetivo: {perfil_usuario.get('objetivo','')}\n"
            f"Alergias: {perfil_usuario.get('alergias','Ninguna')}"
        )
        chat_widget.insert(tk.END, f"\nNutriBot: Perfil registrado:\n{resumen}\n")

def obtener_horario():
    """Devuelve el horario según la hora actual del sistema."""
    hora = datetime.datetime.now().hour
    if 6 <= hora < 12:
        return "Desayuno"
    elif 12 <= hora < 18:
        return "Comida"
    elif 18 <= hora < 22:
        return "Cena"
    else:
        return "Snack"

def mostrar_ingredientes(platillo_id, nombre_platillo):
    ingredientes = obtener_ingredientes(platillo_id)
    if ingredientes:
        detalle = f"Ingredientes de {nombre_platillo}:\n"
        vistos = set()
        for ing in ingredientes:
            if ing.Nombre not in vistos:
                vistos.add(ing.Nombre)
                detalle += f"- {ing.Nombre}: {ing.Cantidad}\n"
        chat.insert(tk.END, f"\nNutriBot: {detalle}\n")
    else:
        chat.insert(tk.END, "\nNutriBot: No encontré ingredientes para ese platillo.\n")

def actualizar_ingredientes(accion, *args):
    global platillo_seleccionado, nombre_platillo_seleccionado
    if not platillo_seleccionado:
        chat.insert(tk.END, "\nNutriBot: Primero seleccione un platillo con su número.\n")
        return

    if accion == "eliminar" and len(args) >= 1:
        respuesta = eliminar_ingrediente(platillo_seleccionado, args[0])

    elif accion == "agregar" and len(args) >= 1:
        existe = ejecutar_consulta("""
            SELECT COUNT(*) FROM Ingredientes
            WHERE PlatilloID = ? AND UPPER(Nombre) = UPPER(?)
        """, (platillo_seleccionado, args[0]), fetchone=True)
        if existe and existe[0] > 0:
            respuesta = f"El ingrediente '{args[0]}' ya existe en el platillo {platillo_seleccionado}."
        else:
            respuesta = agregar_ingrediente(platillo_seleccionado, args[0], "1 unidad")

    elif accion == "cambiar" and len(args) >= 2:
        existe = ejecutar_consulta("""
            SELECT COUNT(*) FROM Ingredientes
            WHERE PlatilloID = ? AND UPPER(Nombre) = UPPER(?)
        """, (platillo_seleccionado, args[0]), fetchone=True)
        if not existe or existe[0] == 0:
            respuesta = f"El ingrediente '{args[0]}' no existe en el platillo {platillo_seleccionado}."
        else:
            duplicado = ejecutar_consulta("""
                SELECT COUNT(*) FROM Ingredientes
                WHERE PlatilloID = ? AND UPPER(Nombre) = UPPER(?)
            """, (platillo_seleccionado, args[1]), fetchone=True)
            if duplicado and duplicado[0] > 0:
                respuesta = f"El ingrediente '{args[1]}' ya está en el platillo {platillo_seleccionado}."
            else:
                respuesta = cambiar_ingrediente(platillo_seleccionado, args[0], args[1], "1 unidad")

    else:
        respuesta = "Acción no reconocida o argumentos insuficientes."

    chat.insert(tk.END, f"\nNutriBot: {respuesta}\n")
    mostrar_ingredientes(platillo_seleccionado, nombre_platillo_seleccionado)

# -------------------------
# CHAT PRINCIPAL
# -------------------------
def enviar_mensaje():
    global platillo_seleccionado, nombre_platillo_seleccionado

    entrada = entry.get().strip()
    chat.insert(tk.END, f"\nUsted: {entrada}\n")

    if "recomiendame" in entrada.lower() or "platillos" in entrada.lower():
        usuario_id = perfil_usuario.get("UsuarioID", 1)
        objetivo = perfil_usuario.get("objetivo", "").strip()
        horario  = obtener_horario()

        resultados = recomendar_platillos(usuario_id, objetivo, horario)

        if resultados:
            chat.insert(tk.END, f"\nNutriBot: Platillos recomendados para {objetivo} en {horario}:\n")
            vistos = set()
            for platillo in resultados:
                if platillo.PlatilloID not in vistos:
                    vistos.add(platillo.PlatilloID)
                    chat.insert(tk.END, f"- {platillo.PlatilloID}: {platillo.Nombre}\n")
            chat.insert(tk.END, "\nEscriba el número del platillo para ver sus ingredientes.\n")
        else:
            chat.insert(tk.END, "\nNutriBot: Primero registre un usuario.\n")

    elif entrada.isdigit():
        platillo_id = int(entrada)
        platillo_seleccionado = platillo_id
        nombre_platillo_seleccionado = obtener_nombre_platillo(platillo_id) or f"Platillo {platillo_id}"
        ingredientes = obtener_ingredientes(platillo_id)
        if ingredientes:
            chat.insert(tk.END, f"\nNutriBot: Ha seleccionado {nombre_platillo_seleccionado}\n")
            mostrar_ingredientes(platillo_id, nombre_platillo_seleccionado)
        else:
            chat.insert(tk.END, "\nNutriBot: No encontré ingredientes para ese platillo.\n")

    elif entrada.lower().startswith("elimina"):
        partes = entrada.split()
        if len(partes) >= 2:
            actualizar_ingredientes("eliminar", partes[-1])
        else:
            chat.insert(tk.END, "\nNutriBot: Para eliminar escriba: elimina [ingrediente]\n")

    elif entrada.lower().startswith("agrega"):
        partes = entrada.split()
        if len(partes) >= 2:
            actualizar_ingredientes("agregar", partes[-1])
        else:
            chat.insert(tk.END, "\nNutriBot: Para agregar escriba: agrega [ingrediente]\n")

    elif entrada.lower().startswith("cambia"):
        partes = entrada.split()
        if len(partes) >= 3:
            actualizar_ingredientes("cambiar", partes[1], partes[2])
        else:
            chat.insert(tk.END, "\nNutriBot: Para cambiar escriba: cambia [ingrediente_viejo] [ingrediente_nuevo]\n")

    else:
        respuesta = obtener_respuesta_local(entrada)
        if respuesta:
            chat.insert(tk.END, f"\nNutriBot: {respuesta}\n")
        else:
            chat.insert(tk.END, "\nNutriBot: No comprendí su mensaje. Puede solicitar recomendaciones de platillos o registrar alergias.\n")

    entry.delete(0, tk.END)

# -------------------------
# INTERFAZ GRÁFICA
# -------------------------
ventana = tk.Tk()
ventana.title("NutriBot - Chat Nutricional")

chat = tk.Text(ventana, height=40, width=100)
chat.pack()

entry = tk.Entry(ventana, width=40)
entry.pack()

tk.Button(ventana, text="Registrar Usuario", command=lambda: registrar_usuario(chat)).pack()
tk.Button(ventana, text="Enviar", command=enviar_mensaje).pack()

ventana.mainloop()
# -------------------------
# FIN DEL CÓDIGO
# -------------------------