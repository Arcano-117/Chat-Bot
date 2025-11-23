-- -------------------------
-- USUARIOS
-- -------------------------
CREATE TABLE Usuarios (
    UsuarioID INT PRIMARY KEY IDENTITY(1,1),
    Nombre NVARCHAR(100) NOT NULL,
    Edad INT CHECK (Edad > 0),
    Peso FLOAT CHECK (Peso > 0),
    Altura FLOAT CHECK (Altura > 0),
    Alergias NVARCHAR(500) NULL
);

-- -------------------------
-- OBJETIVOS
-- -------------------------
CREATE TABLE Objetivos (
    ObjetivoID INT PRIMARY KEY IDENTITY(1,1),
    Nombre NVARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE UsuarioObjetivos (
    UsuarioID INT FOREIGN KEY REFERENCES Usuarios(UsuarioID) ON DELETE CASCADE,
    ObjetivoID INT FOREIGN KEY REFERENCES Objetivos(ObjetivoID) ON DELETE CASCADE,
    PRIMARY KEY (UsuarioID, ObjetivoID)
);

-- -------------------------
-- PLATILLOS
-- -------------------------
CREATE TABLE Platillos (
    PlatilloID INT PRIMARY KEY IDENTITY(1,1),
    Nombre NVARCHAR(200) NOT NULL
);

CREATE TABLE PlatilloObjetivos (
    PlatilloID INT FOREIGN KEY REFERENCES Platillos(PlatilloID) ON DELETE CASCADE,
    ObjetivoID INT FOREIGN KEY REFERENCES Objetivos(ObjetivoID) ON DELETE CASCADE,
    PRIMARY KEY (PlatilloID, ObjetivoID)
);

-- -------------------------
-- HORARIOS
-- -------------------------
CREATE TABLE Horarios (
    HorarioID INT PRIMARY KEY IDENTITY(1,1),
    Nombre NVARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE PlatilloHorarios (
    PlatilloID INT FOREIGN KEY REFERENCES Platillos(PlatilloID) ON DELETE CASCADE,
    HorarioID INT FOREIGN KEY REFERENCES Horarios(HorarioID) ON DELETE CASCADE,
    PRIMARY KEY (PlatilloID, HorarioID)
);

-- -------------------------
-- ALERGIAS
-- -------------------------
CREATE TABLE Alergias (
    AlergiaID INT PRIMARY KEY IDENTITY(1,1),
    Nombre NVARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE UsuarioAlergias (
    UsuarioID INT FOREIGN KEY REFERENCES Usuarios(UsuarioID) ON DELETE CASCADE,
    AlergiaID INT FOREIGN KEY REFERENCES Alergias(AlergiaID) ON DELETE CASCADE,
    PRIMARY KEY (UsuarioID, AlergiaID)
);

CREATE TABLE PlatilloAlergias (
    PlatilloID INT FOREIGN KEY REFERENCES Platillos(PlatilloID) ON DELETE CASCADE,
    AlergiaID INT FOREIGN KEY REFERENCES Alergias(AlergiaID) ON DELETE CASCADE,
    PRIMARY KEY (PlatilloID, AlergiaID)
);

-- -------------------------
-- INGREDIENTES
-- -------------------------
CREATE TABLE Ingredientes (
    IngredienteID INT PRIMARY KEY IDENTITY(1,1),
    PlatilloID INT FOREIGN KEY REFERENCES Platillos(PlatilloID) ON DELETE CASCADE,
    Nombre NVARCHAR(100) NOT NULL,
    Cantidad NVARCHAR(100)
);

-- -------------------------
-- HISTORIAL DE MODIFICACIONES
-- -------------------------
CREATE TABLE HistorialModificaciones (
    ModificacionID INT PRIMARY KEY IDENTITY(1,1),
    UsuarioID INT FOREIGN KEY REFERENCES Usuarios(UsuarioID),
    PlatilloID INT FOREIGN KEY REFERENCES Platillos(PlatilloID),
    Fecha DATETIME DEFAULT GETDATE(),
    Tipo NVARCHAR(50), -- Ej: "Agregar", "Eliminar", "Cambiar"
    IngredienteOriginal NVARCHAR(100),
    IngredienteNuevo NVARCHAR(100),
    Cantidad NVARCHAR(100),
    AccionRealizadaPor NVARCHAR(50) -- Ej: "Usuario", "Bot"
);

-- -------------------------
-- CONVERSACIONES
-- -------------------------
CREATE TABLE Conversaciones (
    MensajeID INT PRIMARY KEY IDENTITY(1,1),
    UsuarioID INT FOREIGN KEY REFERENCES Usuarios(UsuarioID),
    Fecha DATETIME DEFAULT GETDATE(),
    MensajeUsuario NVARCHAR(MAX),
    RespuestaBot NVARCHAR(MAX),
    EmocionDetectada NVARCHAR(100),
    IntentoDetectado NVARCHAR(100) -- Ej: "agregar ingrediente", "recomendar platillo"
);

-- Objetivos
INSERT INTO Objetivos (Nombre) VALUES
('Bajar de peso'),        -- ID = 1
('Ganar musculo'),        -- ID = 2
('Controlar la glucosa'), -- ID = 3
('Mantener el peso'),     -- ID = 4
('Energia diaria');       -- ID = 5

INSERT INTO Horarios (Nombre) VALUES
('Desayuno'),
('Comida'),
('Cena'),
('Snack');

INSERT INTO Alergias (Nombre) VALUES
('Lacteos'),       -- será ID 1
('Nueces'),        -- será ID 2
('Huevo'),         -- será ID 3
('Soya'),          -- será ID 4
('Gluten');        -- será ID 5

-- Platillo 1
INSERT INTO Platillos (Nombre) VALUES ('Ensalada de Atun con Vegetales');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(1, 'Atun', '100 g'),
(1, 'Lechuga', '1 taza'),
(1, 'Tomate', '1 pieza'),
(1, 'Pepino', '1/2 pieza');
INSERT INTO PlatilloObjetivos VALUES (1,1),(1,4); -- Bajar de peso, Mantener el peso
INSERT INTO PlatilloHorarios VALUES (1,2),(1,3); -- Comida, Cena

-- Platillo 2
INSERT INTO Platillos (Nombre) VALUES ('Ensalada de Espinacas con Pollo');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(2, 'Espinaca', '2 tazas'),
(2, 'Pollo', '100 g'),
(2, 'Aceite de oliva', '1 cucharada'),
(2, 'Limon', '1 cucharadita de jugo');
INSERT INTO PlatilloObjetivos VALUES (2,1),(2,3); -- Bajar de peso, Controlar la glucosa
INSERT INTO PlatilloHorarios VALUES (2,2),(2,3); -- Comida, Cena

-- Platillo 3
INSERT INTO Platillos (Nombre) VALUES ('Tacos de Lechuga con Carne Magra');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(3, 'Lechuga', '4 hojas'),
(3, 'Carne de res magra', '120 g'),
(3, 'Jitomate', '1/2 pieza'),
(3, 'Cebolla', '1/4 pieza');
INSERT INTO PlatilloObjetivos VALUES (3,2),(3,1); -- Ganar musculo, Bajar de peso
INSERT INTO PlatilloHorarios VALUES (3,2),(3,3); -- Comida, Cena

-- Platillo 4
INSERT INTO Platillos (Nombre) VALUES ('Yogur Natural con Nueces y Arandanos');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(4, 'Yogur', '1 taza'),
(4, 'Nueces', '1 cucharada'),
(4, 'Arandanos', '2 cucharadas');
INSERT INTO PlatilloObjetivos VALUES (4,2); -- Ganar musculo
INSERT INTO PlatilloHorarios VALUES (4,1),(4,4); -- Desayuno, Snack
INSERT INTO PlatilloAlergias VALUES (4,1),(4,2); -- Lacteos, Nueces

-- Platillo 5
INSERT INTO Platillos (Nombre) VALUES ('Quinoa con Verduras Asadas y Garbanzos');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(5, 'Quinoa', '1/2 taza cocida'),
(5, 'Zanahoria', '1 pieza'),
(5, 'Brocoli', '1 taza'),
(5, 'Garbanzos', '1/2 taza cocidos');
INSERT INTO PlatilloObjetivos VALUES (5,3),(5,1); -- Controlar la glucosa, Bajar de peso
INSERT INTO PlatilloHorarios VALUES (5,2),(5,3); -- Comida, Cena

-- Platillo 6
INSERT INTO Platillos (Nombre) VALUES ('Pescado al Horno con Brocoli y Arroz Integral');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(6, 'Pescado', '150 g'),
(6, 'Brocoli', '1 taza'),
(6, 'Arroz integral', '1/2 taza cocido');
INSERT INTO PlatilloObjetivos VALUES (6,3),(6,2); -- Controlar la glucosa, Ganar musculo
INSERT INTO PlatilloHorarios VALUES (6,2); -- Comida

-- Platillo 7
INSERT INTO Platillos (Nombre) VALUES ('Avena con Platano y Canela');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(7, 'Avena', '1/2 taza'),
(7, 'Platano', '1/2 pieza'),
(7, 'Canela', '1/2 cucharadita');
INSERT INTO PlatilloObjetivos VALUES (7,1),(7,3); -- Bajar de peso, Controlar la glucosa
INSERT INTO PlatilloHorarios VALUES (7,1); -- Desayuno

-- Platillo 8
INSERT INTO Platillos (Nombre) VALUES ('Smoothie de Espinaca y Mango');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(8, 'Espinaca', '1 taza'),
(8, 'Mango', '1/2 pieza'),
(8, 'Agua', '200 ml'),
(8, 'Semillas de chia', '1 cucharada');
INSERT INTO PlatilloObjetivos VALUES (8,1),(8,3); -- Bajar de peso, Controlar la glucosa
INSERT INTO PlatilloHorarios VALUES (8,1),(8,4); -- Desayuno, Snack

-- Platillo 9
INSERT INTO Platillos (Nombre) VALUES ('Omelette de Claras con Vegetales');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(9, 'Claras de huevo', '3 unidades'),
(9, 'Espinaca', '1 taza'),
(9, 'Pimiento', '1/4 pieza'),
(9, 'Cebolla', '1/4 pieza');
INSERT INTO PlatilloObjetivos VALUES (9,2),(9,1); -- Ganar musculo, Bajar de peso
INSERT INTO PlatilloHorarios VALUES (9,1),(9,3); -- Desayuno, Cena
INSERT INTO PlatilloAlergias VALUES (9,3); -- Huevo

-- Platillo 10
INSERT INTO Platillos (Nombre) VALUES ('Tofu Salteado con Arroz Integral');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(10, 'Tofu', '100 g'),
(10, 'Brocoli', '1 taza'),
(10, 'Zanahoria', '1 pieza'),
(10, 'Arroz integral', '1/2 taza cocido');
INSERT INTO PlatilloObjetivos VALUES (10,2),(10,3); -- Ganar musculo, Controlar la glucosa
INSERT INTO PlatilloHorarios VALUES (10,2),(10,3); -- Comida, Cena
INSERT INTO PlatilloAlergias VALUES (10,4); -- Soya

-- Platillo 11
INSERT INTO Platillos (Nombre) VALUES ('Sopa de Lentejas con Verduras');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(11, 'Lentejas', '1/2 taza cocida'),
(11, 'Zanahoria', '1 pieza'),
(11, 'Apio', '1 rama'),
(11, 'Cebolla', '1/4 pieza');
INSERT INTO PlatilloObjetivos VALUES (11,3),(11,1); -- Controlar la glucosa, Bajar de peso
INSERT INTO PlatilloHorarios VALUES (11,2),(11,3); -- Comida, Cena

-- Platillo 12
INSERT INTO Platillos (Nombre) VALUES ('Rodajas de Manzana con Mantequilla de Almendra');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(12, 'Manzana', '1 pieza'),
(12, 'Mantequilla de almendra', '1 cucharada');
INSERT INTO PlatilloObjetivos VALUES (12,1),(12,5); -- Bajar de peso, Energia diaria
INSERT INTO PlatilloHorarios VALUES (12,4); -- Snack
INSERT INTO PlatilloAlergias VALUES (12,2); -- Nueces

-- Platillo 13
INSERT INTO Platillos (Nombre) VALUES ('Rollitos de Pavo con Pepino');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(13, 'Pavo', '80 g'),
(13, 'Pepino', '1/2 pieza'),
(13, 'Lechuga', '2 hojas');
INSERT INTO PlatilloObjetivos VALUES (13,2),(13,4); -- Ganar musculo, Mantener el peso
INSERT INTO PlatilloHorarios VALUES (13,4); -- Snack

-- Platillo 14
INSERT INTO Platillos (Nombre) VALUES ('Mix de Frutos Secos y Semillas');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(14, 'Nueces', '1 cucharada'),
(14, 'Almendras', '1 cucharada'),
(14, 'Semillas de girasol', '1 cucharada');
INSERT INTO PlatilloObjetivos VALUES (14,5); -- Energia diaria
INSERT INTO PlatilloHorarios VALUES (14,4); -- Snack
INSERT INTO PlatilloAlergias VALUES (14,2); -- Nueces

-- Platillo 15
INSERT INTO Platillos (Nombre) VALUES ('Gelatina Natural con Fruta');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(15, 'Gelatina sin azucar', '1 porcion'),
(15, 'Fruta variada', '1/2 taza');
INSERT INTO PlatilloObjetivos VALUES (15,1),(15,3); -- Bajar de peso, Controlar la glucosa
INSERT INTO PlatilloHorarios VALUES (15,4),(15,3); -- Snack, Cena

-- Platillo 16
INSERT INTO Platillos (Nombre) VALUES ('Ensalada de Garbanzos con Tomate y Pepino');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(16, 'Garbanzos', '1 taza cocidos'),
(16, 'Tomate', '1 pieza'),
(16, 'Pepino', '1/2 pieza'),
(16, 'Aceite de oliva', '1 cucharada');
INSERT INTO PlatilloObjetivos VALUES (16,1),(16,3); -- Bajar de peso, Controlar la glucosa
INSERT INTO PlatilloHorarios VALUES (16,2),(16,3); -- Comida, Cena

-- Platillo 17
INSERT INTO Platillos (Nombre) VALUES ('Wrap Integral de Pollo y Aguacate');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(17, 'Tortilla integral', '1 pieza'),
(17, 'Pollo', '100 g'),
(17, 'Aguacate', '1/4 pieza'),
(17, 'Lechuga', '2 hojas');
INSERT INTO PlatilloObjetivos VALUES (17,2),(17,4); -- Ganar musculo, Mantener el peso
INSERT INTO PlatilloHorarios VALUES (17,2); -- Comida
INSERT INTO PlatilloAlergias VALUES (17,5); -- Gluten

-- Platillo 18
INSERT INTO Platillos (Nombre) VALUES ('Arroz Integral con Verduras y Huevo');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(18, 'Arroz integral', '1 taza cocido'),
(18, 'Zanahoria', '1 pieza'),
(18, 'Brocoli', '1 taza'),
(18, 'Huevo', '1 unidad');
INSERT INTO PlatilloObjetivos VALUES (18,5),(18,4); -- Energia diaria, Mantener el peso
INSERT INTO PlatilloHorarios VALUES (18,2),(18,3); -- Comida, Cena
INSERT INTO PlatilloAlergias VALUES (18,3); -- Huevo

-- Platillo 19
INSERT INTO Platillos (Nombre) VALUES ('Crema de Calabaza con Semillas');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(19, 'Calabaza', '1 taza'),
(19, 'Cebolla', '1/4 pieza'),
(19, 'Semillas de calabaza', '1 cucharada'),
(19, 'Caldo de verduras', '1 taza');
INSERT INTO PlatilloObjetivos VALUES (19,3),(19,1); -- Controlar la glucosa, Bajar de peso
INSERT INTO PlatilloHorarios VALUES (19,3); -- Cena

-- Platillo 20
INSERT INTO Platillos (Nombre) VALUES ('Batido de Platano y Avena');
INSERT INTO Ingredientes (PlatilloID, Nombre, Cantidad) VALUES
(20, 'Platano', '1 pieza'),
(20, 'Avena', '1/2 taza'),
(20, 'Leche', '200 ml'),
(20, 'Canela', '1/2 cucharadita');
INSERT INTO PlatilloObjetivos VALUES (20,5),(20,2); -- Energia diaria, Ganar musculo
INSERT INTO PlatilloHorarios VALUES (20,1),(20,4); -- Desayuno, Snack
INSERT INTO PlatilloAlergias VALUES (20,1); -- Lacteos