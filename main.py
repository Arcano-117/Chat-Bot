from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
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
ventana.title("NutriBot - Asistente de Nutrición")
ventana.geometry("900x500")
ventana.resizable(False, False)

# FUNCION PARA LIMPIAR TODO
def limpiar():
    for widget in ventana.winfo_children():
        widget.destroy()

# Helper seguro para cargar imagen (si falla, devuelve None)
def cargar_imagen_safe(nombre, size=None):
    try:
        img = Image.open(nombre)
        if size:
            img = img.resize(size)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

# ---------------------------
# PANTALLA 1 — INICIO
# ---------------------------
def pantalla_inicio():
    limpiar()

    fondo_tk = cargar_imagen_safe("nutrifit_fondo1.jpeg", (900, 500))
    if fondo_tk:
        lbl_fondo = tk.Label(ventana, image=fondo_tk)
        lbl_fondo.image = fondo_tk
        lbl_fondo.place(x=0, y=0)
    else:
        ventana.configure(bg="#ace1b8")

    crear_tk = cargar_imagen_safe("crear_cuenta.jpeg", (220, 80))
    if crear_tk:
        btn = tk.Button(ventana, image=crear_tk, borderwidth=0, highlightthickness=0, command=pantalla_registro)
        btn.image = crear_tk
        btn.place(relx=0.5, rely=0.75, anchor="center")
    else:
        tk.Button(ventana, text="Crear cuenta", command=pantalla_registro, font=("Arial", 14)).place(relx=0.5, rely=0.75, anchor="center")

# ---------------------------
# PANTALLA 2 — REGISTRO
# ---------------------------
def pantalla_registro():
    limpiar()

    fondo_tk = cargar_imagen_safe("nutrifit_fondo2.jpeg", (900, 500))
    if fondo_tk:
        lbl_fondo = tk.Label(ventana, image=fondo_tk)
        lbl_fondo.image = fondo_tk
        lbl_fondo.place(x=0, y=0)
    else:
        ventana.configure(bg="#ace1b8")

    select_tk = cargar_imagen_safe("select_icon.jpeg", (330, 55))

    entradas = {}

    def campo(nombre, x, y):
        tk.Label(ventana, text=nombre + ":", font=("Arial", 15), bg="#ace1b8").place(x=x, y=y)

        if select_tk:
            box = tk.Label(ventana, image=select_tk, borderwidth=0)
            box.image = select_tk
            box.place(x=x, y=y+35)
        else:
            tk.Label(ventana, bg="#DFFFDD", width=40, height=2).place(x=x, y=y+35)

        entry_widget = tk.Entry(ventana, font=("Arial", 19), bg="#1A1A1A", fg="white", borderwidth=0)
        entry_widget.place(x=x+20, y=y+43, width=290, height=28)
        return entry_widget

    entradas["Nombre"] = campo("Nombre", 100, 140)
    entradas["Altura(cm)"] = campo("Altura(cm)", 100, 240)
    entradas["Alergias"] = campo("Alergias", 100, 340)
    entradas["Peso"] = campo("Peso", 480, 140)
    entradas["Objetivo"] = campo("Objetivo", 480, 240)

    def validar():
        perfil = {}
        try:
            perfil["nombre"]   = entradas["Nombre"].get().strip()
            perfil["altura"]   = int(entradas["Altura(cm)"].get().strip())
            perfil["alergias"] = entradas["Alergias"].get().strip() or "Ninguna"
            perfil["peso"]     = float(entradas["Peso"].get().strip())
            perfil["objetivo"] = entradas["Objetivo"].get().strip()

            if not perfil["nombre"]:
                raise ValueError("El nombre no puede estar vacío.")
            if perfil["altura"] <= 0:
                raise ValueError("La altura debe ser un número positivo.")
            if perfil["peso"] <= 0:
                raise ValueError("El peso debe ser un número positivo.")
            if not perfil["objetivo"]:
                raise ValueError("El objetivo no puede estar vacío.")

            global perfil_usuario
            perfil_usuario = perfil
            messagebox.showinfo("Éxito", "Perfil registrado correctamente.")
            pantalla_chat()

        except ValueError as ve:
            messagebox.showerror("Error de validación", str(ve))
        except Exception:
            messagebox.showerror("Error", "Ocurrió un error al registrar el perfil. Verifique los datos ingresados.")

    sig_tk = cargar_imagen_safe("siguiente.jpeg", (186, 70))
    if sig_tk:
        btn_next = tk.Button(ventana, image=sig_tk, borderwidth=0, command=validar)
        btn_next.image = sig_tk
        btn_next.place(x=520, y=360)
    else:
        tk.Button(ventana, text="Siguiente", command=validar).place(x=520, y=360)

# ---------------------------
# PANTALLA 3 — CHAT 
# ---------------------------
def pantalla_chat():
    limpiar()
    global chat, entry

    fondo_tk = cargar_imagen_safe("nutrifit_fondo3.jpeg", (900, 500))
    if fondo_tk:
        lbl_fondo = tk.Label(ventana, image=fondo_tk)
        lbl_fondo.image = fondo_tk
        lbl_fondo.place(x=0, y=0, relwidth=1, relheight=1)
    else:
        ventana.configure(bg="#ACE1B8")

    chat_frame = tk.Frame(ventana, bg="#ace1b8")
    chat_frame.place(x=50, y=80, width=800, height=280)

    scroll = tk.Scrollbar(chat_frame)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    chat = tk.Text(
        chat_frame,
        yscrollcommand=scroll.set,
        wrap="word",
        bg="#ACE1B8",
        fg="black",
        font=("Arial", 12),
        bd=0
    )
    chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll.config(command=chat.yview)

    # Barra de texto (imagen decorativa)
    barra_tk = cargar_imagen_safe("barrade_texto.jpeg", (700, 70))
    if barra_tk:
        barra_label = tk.Label(ventana, image=barra_tk, borderwidth=0)
        barra_label.image = barra_tk
        barra_label.place(x=50, y=380)
    else:
        tk.Label(ventana, bg="#ACE1B8", width=90, height=3).place(x=50, y=380)

    # Entrada encima de la barra
    entry = tk.Entry(ventana, font=("Arial", 14), bg="#1A1A1A", fg="white", bd=0)
    entry.place(x=80, y=405, width=640, height=30)

    # Botón ENVIAR
    enviar_tk = cargar_imagen_safe("enviar.jpeg", (60, 60))
    if enviar_tk:
        btn_enviar = tk.Button(ventana, image=enviar_tk, borderwidth=0, highlightthickness=0, command=enviar_desde_ui)
        btn_enviar.image = enviar_tk
        btn_enviar.place(x=770, y=390)
    else:
        tk.Button(ventana, text="Enviar", command=enviar_desde_ui).place(x=770, y=405)

def enviar_desde_ui():
    enviar_mensaje()


pantalla_inicio()
ventana.mainloop()
# -------------------------
# FIN DEL CÓDIGO
# -------------------------
