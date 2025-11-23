import tkinter as tk
from tkinter import messagebox
from nutribot_sql import registrar_usuario, obtener_ultimo_usuario

def mostrar_formulario():
    perfil = {}

    def registrar():
        # Capturar datos del formulario
        datos = {etiqueta: entrada.get().strip() for etiqueta, entrada in campos.items()}

        # Validación de campos obligatorios (excepto alergias)
        obligatorios = ["nombre", "edad", "peso", "altura", "objetivo"]
        for campo in obligatorios:
            if not datos[campo]:
                messagebox.showwarning("Campos incompletos", f"El campo '{campo}' es obligatorio.")
                return

        # Validación de tipos numéricos
        try:
            datos["edad"] = int(datos["edad"])
            datos["peso"] = float(datos["peso"])
            datos["altura"] = float(datos["altura"])
        except ValueError:
            messagebox.showerror(
                "Error de formato",
                "La edad debe ser un número entero, y el peso y la altura deben ser valores numéricos."
            )
            return

        # Normalizar textos
        datos["nombre"] = datos["nombre"].title()
        datos["objetivo"] = datos["objetivo"].title()
        datos["alergias"] = datos["alergias"].title() if datos["alergias"] else ""

        try:
            # Guardar en la base de datos SQL
            usuario_id, respuesta = registrar_usuario(
                datos["nombre"],
                datos["edad"],
                datos["peso"],
                datos["altura"],
                datos["objetivo"],
                datos["alergias"]
            )

            # Actualizar perfil en memoria
            perfil.update(datos)
            perfil["UsuarioID"] = usuario_id

            # Mostrar resumen formal del perfil
            resumen = (
                f"Nombre: {datos['nombre']}\n"
                f"Edad: {datos['edad']} años\n"
                f"Peso: {datos['peso']} kg\n"
                f"Altura: {datos['altura']} cm\n"
                f"Objetivo: {datos['objetivo']}\n"
                f"Alergias: {datos['alergias'] or 'Ninguna'}"
            )
            messagebox.showinfo("Registro exitoso", f"{respuesta}\n\nPerfil registrado:\n{resumen}")
            ventana.destroy()  # Cierra solo el formulario

        except Exception as e:
            messagebox.showerror("Error en registro", f"Ocurrió un problema al registrar el usuario:\n{e}")

    # Ventana secundaria del formulario (no destruye la principal)
    ventana = tk.Toplevel()
    ventana.title("Registro Nutricional")

    # Campos que corresponden a las columnas de la tabla Usuarios
    campos = {
        "nombre": tk.Entry(ventana),
        "edad": tk.Entry(ventana),
        "peso": tk.Entry(ventana),
        "altura": tk.Entry(ventana),
        "objetivo": tk.Entry(ventana),
        "alergias": tk.Entry(ventana)
    }

    for etiqueta, entrada in campos.items():
        tk.Label(ventana, text=etiqueta.capitalize()).pack()
        entrada.pack()

    tk.Label(ventana, text="(Altura en centímetros)").pack()
    tk.Label(ventana, text="Alergias separadas por coma (ej: Gluten, Huevo)").pack()
    tk.Button(ventana, text="Registrar", command=registrar).pack(pady=10)

    # Importante: no uses un segundo mainloop, la ventana principal ya lo tiene
    ventana.grab_set()  # Bloquea interacción con la ventana principal hasta cerrar el formulario

    return perfil

def cargar_ultimo_usuario():
    """Obtiene el último usuario registrado desde la base de datos."""
    return obtener_ultimo_usuario()