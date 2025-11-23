respuestas_locales = {
    "saludos": {
        "Hola": "Saludos cordiales. ¿Cómo se encuentra?",
        "Buenos días": "Muy buenos días. Espero que su jornada sea productiva.",
        "Buenas tardes": "Buenas tardes. Confío en que esté teniendo un día agradable.",
        "Buenas noches": "Buenas noches. Le deseo un descanso reparador."
    },
    "despedidas": {
        "Adios": "Hasta pronto. Cuide su bienestar.",
        "Hasta luego": "Nos vemos más adelante. Que tenga un excelente día.",
        "Nos vemos": "Nos veremos en otra ocasión. Mantenga hábitos saludables.",
        "Gracias": "Con gusto. Estoy aquí para asistirle."
    },
    "informativas": {
        "Fruta": "Las frutas son una fuente importante de fibra, vitaminas y minerales.",
        "Agua": "Es recomendable consumir al menos dos litros de agua diariamente.",
        "Fibra": "La fibra favorece la digestión y contribuye al control de la glucosa.",
        "Verdura": "Las verduras aportan nutrientes esenciales para el organismo.",
        "Ejercicio": "El ejercicio regular fortalece la salud física y mental.",
        "Cena ligera": "Una cena ligera facilita un descanso adecuado.",
        "Desayuno saludable": "Un desayuno equilibrado proporciona energía para iniciar el día."
    },
    "emocionales": {
    "Triste": "Lamento que se sienta así. Una alimentación adecuada puede ayudar a mejorar su estado de ánimo.",
    "Cansado": "Comprendo su cansancio. Un refrigerio saludable puede brindarle energía adicional.",
    "Estresado": "El manejo del estrés se facilita con una dieta balanceada y pausas de relajación.",
    "Desmotivado": "La constancia en pequeños hábitos puede generar grandes cambios positivos.",
    "Feliz": "Me alegra saberlo. Continuemos fomentando su bienestar.",
    "Ansioso": "Una rutina alimenticia equilibrada puede contribuir a la tranquilidad.",
    "Bien": "Me complace saber que se encuentra bien. Mantener hábitos saludables le ayudará a conservar ese estado."
    },
    "cortesia": {
        "Si": "De acuerdo.",
        "Por favor": "Con mucho gusto.",
        "Ok": "Correcto.",
        "Claro": "Por supuesto."
    }
}

def obtener_respuesta_local(entrada: str) -> str | None:
    """
    Busca una respuesta en el diccionario local según la entrada del usuario.
    Acepta tanto mayúsculas como minúsculas sin modificar la entrada original.
    """
    for categoria, frases in respuestas_locales.items():
        for clave, respuesta in frases.items():
            if entrada.casefold() == clave.casefold():  # comparación insensible
                return respuesta
    return None

# -------------------------
# FIN DEL CÓDIGO
# -------------------------