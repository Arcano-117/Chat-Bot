import pyodbc

# -------------------------
# CONEXIÓN
# -------------------------

def conectar_bd():
    """Establece conexión con SQL Server."""
    try:
        conn = pyodbc.connect(
            "Driver={SQL Server};"
            "Server=EBENPEREZ;"
            "Database=NutriBot;"
            "Trusted_Connection=yes;"
        )
        return conn
    except Exception as e:
        print("Error de conexión:", e)
        return None

def ejecutar_consulta(query, params=(), fetchone=False, fetchall=False, commit=False):
    """
    Ejecuta una consulta SQL con parámetros opcionales.
    Puede devolver un solo registro, todos los registros o simplemente ejecutar la consulta.
    """
    conn = conectar_bd()
    if not conn:
        return None

    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if commit:
            conn.commit()
            return cursor.rowcount  # número de filas afectadas
        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()
        return None
    except Exception as e:
        print("Error al ejecutar consulta:", e)
        return None
    finally:
        cursor.close()
        conn.close()

# -------------------------
# UTILIDADES
# -------------------------
def normalizar_texto(texto):
    """Limpia y capitaliza texto para consistencia en la base."""
    return texto.strip().title()

# -------------------------
# USUARIOS
# -------------------------
def tabla_tiene_columna(nombre_tabla, columna):
    fila = ejecutar_consulta("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = ? AND COLUMN_NAME = ?
    """, (nombre_tabla, columna), fetchone=True)
    return bool(fila and fila[0] == 1)

def registrar_usuario(nombre, edad, peso, altura, objetivo, alergias):
    nombre = normalizar_texto(nombre)
    objetivo = normalizar_texto(objetivo)

    # 1) Inserta solo columnas que EXISTEN realmente
    columnas = ["Nombre", "Edad", "Peso", "Altura"]
    valores  = [nombre,      edad,    peso,    altura]

    if tabla_tiene_columna("Usuarios", "Objetivo"):
        columnas.append("Objetivo")
        valores.append(objetivo)

    placeholders = ", ".join(["?"] * len(columnas))
    columnas_sql = ", ".join(columnas)

    ejecutar_consulta(f"""
        INSERT INTO Usuarios ({columnas_sql})
        VALUES ({placeholders})
    """, tuple(valores), commit=True)

    # 2) Obtén el usuario_id
    usuario = obtener_ultimo_usuario()
    usuario_id = usuario["usuario_id"]

    # 3) Inserta alergias evitando duplicados
    if alergias:
        lista = [normalizar_texto(a.strip()) for a in alergias.split(",") if a.strip()]
        for alergia in lista:
            row = ejecutar_consulta("""
                SELECT AlergiaID FROM Alergias WHERE UPPER(Nombre) = UPPER(?)
            """, (alergia,), fetchone=True)
            if not row:
                continue
            alergia_id = row[0]

            existe = ejecutar_consulta("""
                SELECT COUNT(*) FROM UsuarioAlergias
                WHERE UsuarioID = ? AND AlergiaID = ?
            """, (usuario_id, alergia_id), fetchone=True)

            if not existe or existe[0] == 0:
                ejecutar_consulta("""
                    INSERT INTO UsuarioAlergias (UsuarioID, AlergiaID)
                    VALUES (?, ?)
                """, (usuario_id, alergia_id), commit=True)

    return usuario_id, "Usuario registrado exitosamente."

def obtener_usuario(usuario_id):
    row = ejecutar_consulta("""
        SELECT UsuarioID, Nombre, Edad, Peso, Altura, Alergias
        FROM Usuarios WHERE UsuarioID = ?
    """, (usuario_id,), fetchone=True)
    if row:
        return {
            "usuario_id": row[0],
            "nombre": row[1],
            "edad": row[2],
            "peso": row[3],
            "altura": row[4],
            "alergias": row[5]
        }
    return None

def obtener_ultimo_usuario():
    row = ejecutar_consulta("""
        SELECT TOP 1 UsuarioID, Nombre, Edad, Peso, Altura, Alergias
        FROM Usuarios ORDER BY UsuarioID DESC
    """, fetchone=True)
    if row:
        return {
            "usuario_id": row[0],
            "nombre": row[1],
            "edad": row[2],
            "peso": row[3],
            "altura": row[4],
            "alergias": row[5]
        }
    return None

# -------------------------
# ALERGIAS
# -------------------------
def obtener_alergias_usuario(usuario_id):
    """
    Devuelve la lista de alergias registradas para el usuario.
    """
    rows = ejecutar_consulta("""
        SELECT a.Nombre
        FROM UsuarioAlergias ua
        JOIN Alergias a ON ua.AlergiaID = a.AlergiaID
        WHERE ua.UsuarioID = ?
    """, (usuario_id,), fetchall=True)
    return [r.Nombre for r in rows] if rows else []

def agregar_alergia_usuario(usuario_id, alergia_nombre):
    alergia_nombre = normalizar_texto(alergia_nombre)
    row = ejecutar_consulta("SELECT AlergiaID FROM Alergias WHERE UPPER(Nombre) = UPPER(?)", (alergia_nombre,), fetchone=True)
    if row:
        ejecutar_consulta("""
            INSERT INTO UsuarioAlergias (UsuarioID, AlergiaID)
            VALUES (?, ?)
        """, (usuario_id, row[0]), commit=True)
        return f"Alergia '{alergia_nombre}' agregada al usuario {usuario_id}."
    return f"Alergia '{alergia_nombre}' no encontrada."

# -------------------------
# PLATILLOS
# -------------------------

def recomendar_platillos(usuario_id, objetivo, horario):
    """
    Recomienda platillos según objetivo y horario SIN filtrar alergias.
    """
    rows = ejecutar_consulta("""
        SELECT DISTINCT p.PlatilloID, p.Nombre
        FROM Platillos p
        JOIN PlatilloObjetivos po ON p.PlatilloID = po.PlatilloID
        JOIN Objetivos o ON po.ObjetivoID = o.ObjetivoID
        JOIN PlatilloHorarios ph ON p.PlatilloID = ph.PlatilloID
        JOIN Horarios h ON ph.HorarioID = h.HorarioID
        WHERE o.Nombre = ? AND h.Nombre = ?
    """, (objetivo, horario), fetchall=True)
    return rows


def recomendar_platillos_seguro(usuario_id, objetivo, horario):
    """
    Recomienda platillos según objetivo y horario, excluyendo los que tengan alergias del usuario.
    """
    # Obtener alergias del usuario
    alergias_usuario = obtener_alergias_usuario(usuario_id)

    # Construir filtro dinámico
    alergias_param = ','.join(alergias_usuario) if alergias_usuario else ''

    query = """
        SELECT DISTINCT p.PlatilloID, p.Nombre
        FROM Platillos p
        JOIN PlatilloObjetivos po ON p.PlatilloID = po.PlatilloID
        JOIN Objetivos o ON po.ObjetivoID = o.ObjetivoID
        JOIN PlatilloHorarios ph ON p.PlatilloID = ph.PlatilloID
        JOIN Horarios h ON ph.HorarioID = h.HorarioID
        WHERE o.Nombre = ? AND h.Nombre = ?
          AND NOT EXISTS (
              SELECT 1
              FROM PlatilloAlergias pa
              JOIN Alergias a ON pa.AlergiaID = a.AlergiaID
              WHERE pa.PlatilloID = p.PlatilloID
                AND a.Nombre IN (
                    SELECT value FROM STRING_SPLIT(?, ',')
                )
          )
    """

    rows = ejecutar_consulta(query, (objetivo, horario, alergias_param), fetchall=True)
    return rows

def agregar_ingrediente(platillo_id, ingrediente_nombre, cantidad):
    ingrediente_nombre = normalizar_texto(ingrediente_nombre)

    # 1. Verificar alergias del platillo
    alergias = obtener_alergias_usuario(platillo_id)

    if ingrediente_nombre in alergias:
        return f"No se puede agregar el ingrediente '{ingrediente_nombre}' debido a alergias registradas."
    
    # 2. Verificar si ya existe en el platillo
    existe = ejecutar_consulta("""
        SELECT COUNT(*) FROM Ingredientes
        WHERE PlatilloID = ? AND UPPER(Nombre) = UPPER(?)
    """, (platillo_id, ingrediente_nombre), fetchone=True)

    if existe and existe[0] > 0:
        return f"El ingrediente '{ingrediente_nombre}' ya existe en el platillo {platillo_id}."

    # 3. Insertar si no existe
    ejecutar_consulta("""
        INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad)
        VALUES (?, ?, ?)
    """, (platillo_id, ingrediente_nombre, cantidad), commit=True)

    return f"Ingrediente '{ingrediente_nombre}' agregado al platillo {platillo_id} con cantidad {cantidad}."


def cambiar_ingrediente(platillo_id, original_nombre, nuevo_nombre, cantidad):
    original_nombre = normalizar_texto(original_nombre)
    nuevo_nombre = normalizar_texto(nuevo_nombre)

    # 1. Verificar alergias del platillo
    alergias = obtener_alergias_usuario(platillo_id)
    if nuevo_nombre in alergias:
        return f"No se puede cambiar al ingrediente '{nuevo_nombre}' debido a alergias registradas."
    
    # 2. Verificar si el ingrediente original existe
    existe = ejecutar_consulta("""
        SELECT COUNT(*) FROM Ingredientes
        WHERE PlatilloID = ? AND UPPER(Nombre) = UPPER(?)
    """, (platillo_id, original_nombre))

    if existe[0][0] == 0:  # no se encontró
        return f"El ingrediente '{original_nombre}' no existe en el platillo {platillo_id}."

    # 3. Verificar si el nuevo nombre ya está en el platillo
    duplicado = ejecutar_consulta("""
        SELECT COUNT(*) FROM Ingredientes
        WHERE PlatilloID = ? AND UPPER(Nombre) = UPPER(?)
    """, (platillo_id, nuevo_nombre))

    if duplicado[0][0] > 0:
        return f"El ingrediente '{nuevo_nombre}' ya está en el platillo {platillo_id}."

    # 4. Si pasa las validaciones, actualizar
    ejecutar_consulta("""
        UPDATE Ingredientes SET Nombre = ?, Cantidad = ?
        WHERE PlatilloID = ? AND UPPER(Nombre) = UPPER(?)
    """, (nuevo_nombre, cantidad, platillo_id, original_nombre), commit=True)

    return f"Ingrediente '{original_nombre}' cambiado por '{nuevo_nombre}' en el platillo {platillo_id}."


def eliminar_ingrediente(usuario_id, ingrediente_nombre):
    ingrediente_nombre = normalizar_texto(ingrediente_nombre)
    if eliminar_ingrediente is None:
        return f"No hay ingredientes para eliminar."
    else:
        row = ejecutar_consulta("SELECT IngredienteID FROM Ingredientes WHERE UPPER(Nombre) = UPPER(?)", (ingrediente_nombre,), fetchone=True)
    if row:
        ejecutar_consulta("""
            DELETE FROM UsuarioIngredientes
            WHERE UsuarioID = ? AND IngredienteID = ?
        """, (usuario_id, row[0]), commit=True)
        return f"Ingrediente '{ingrediente_nombre}' eliminado del usuario {usuario_id}."
    return f"Ingrediente '{ingrediente_nombre}' no encontrado."


def obtener_ingredientes(platillo_id):
    rows = ejecutar_consulta("""
        SELECT DISTINCT i.Nombre, i.Cantidad, p.Nombre AS PlatilloNombre
        FROM Ingredientes i
        JOIN Platillos p ON i.PlatilloID = p.PlatilloID
        WHERE i.PlatilloID = ?
    """, (platillo_id,), fetchall=True)
    return rows


def obtener_nombre_platillo(platillo_id):
    row = ejecutar_consulta("SELECT Nombre FROM Platillos WHERE PlatilloID = ?", (platillo_id,), fetchone=True)
    return row[0] if row else None

# -------------------------
# INGREDIENTES
# -------------------------
def agregar_ingrediente(platillo_id, nombre, cantidad):
    nombre = normalizar_texto(nombre)
    ejecutar_consulta("""
        INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad)
        VALUES (?, ?, ?)
    """, (platillo_id, nombre, cantidad), commit=True)
    return f"Ingrediente '{nombre}' agregado con cantidad {cantidad} al platillo {platillo_id}."

def eliminar_ingrediente(platillo_id, nombre):
    nombre = normalizar_texto(nombre)
    ejecutar_consulta("""
        DELETE FROM Ingredientes WHERE PlatilloID = ? AND UPPER(Nombre) = UPPER(?)
    """, (platillo_id, nombre), commit=True)
    return f"Ingrediente '{nombre}' eliminado del platillo {platillo_id}."

def cambiar_ingrediente(platillo_id, original, nuevo, cantidad):
    original = normalizar_texto(original)
    nuevo = normalizar_texto(nuevo)
    ejecutar_consulta("""
        UPDATE Ingredientes SET Nombre = ?, Cantidad = ?
        WHERE PlatilloID = ? AND UPPER(Nombre) = UPPER(?)
    """, (nuevo, cantidad, platillo_id, original), commit=True)
    return f"Ingrediente '{original}' cambiado por '{nuevo}' en el platillo {platillo_id}."
# -------------------------
# FIN DEL CÓDIGO
# -------------------------