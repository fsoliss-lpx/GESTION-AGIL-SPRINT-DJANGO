create database trabajos13;
use trabajos13

CREATE TABLE Marca (
    id_marca      INT PRIMARY KEY,
    nom_marca     VARCHAR(50) NOT NULL
);
 
CREATE TABLE Producto (
    id_producto   INT PRIMARY KEY,
    id_marca      INT NOT NULL,
    nombre        VARCHAR(100) NOT NULL,
    detalle       VARCHAR(100),
    tipo          VARCHAR(20) NOT NULL
        CHECK (tipo IN ('ingrediente','desechable','bebida')),
    CONSTRAINT FK_Producto_Marca FOREIGN KEY (id_marca)
        REFERENCES Marca(id_marca)
);
 
CREATE TABLE Medida (
    id_medida     INT PRIMARY KEY,
    nom_medida    VARCHAR(30) NOT NULL
);
 
CREATE TABLE Comida (
    id_comida     INT PRIMARY KEY,
    nombre        VARCHAR(100) NOT NULL,
    detalles      VARCHAR(200),
    precio        DECIMAL(10,2) NOT NULL,
    foto          VARCHAR(100)
);
 
CREATE TABLE Receta_Producto (
    id_comida     INT NOT NULL,
    id_producto   INT NOT NULL,
    id_medida     INT NOT NULL,
    orden_prepar  INT NOT NULL,
    cantidad      DECIMAL(10,2) NOT NULL,
    CONSTRAINT PK_Receta_Producto PRIMARY KEY (id_comida, id_producto, id_medida),
    CONSTRAINT FK_RP_Comida   FOREIGN KEY (id_comida)   REFERENCES Comida(id_comida),
    CONSTRAINT FK_RP_Producto FOREIGN KEY (id_producto) REFERENCES Producto(id_producto),
    CONSTRAINT FK_RP_Medida   FOREIGN KEY (id_medida)   REFERENCES Medida(id_medida)
);
----- insert datos doc
INSERT INTO Marca VALUES (1, 'NESTLE');
INSERT INTO Producto VALUES (1, 1, 'Leche Entera', '1 Litro', 'ingrediente');
INSERT INTO Medida VALUES (1, 'Gramos');
INSERT INTO Comida VALUES (1, 'Batido de Fresa', 'Bebida fria con fruta natural', 2.50, 'foto01.jpg');
INSERT INTO Receta_Producto VALUES (1, 1, 1, 1, 500);
---MARCA
INSERT INTO Marca VALUES
(2, 'COCA-COLA'),
(3, 'PEPSI'),
(4, 'ALPINA'),
(5, 'MCCORMICK'),
(6, 'LA FABRIL'),
(7, 'GUSTADINA'),
(8, 'TONYS');
SELECT*FROM Marca
----COMIDA
INSERT INTO Comida VALUES
(2, 'Hamburguesa Especial', 'Hamburguesa doble carne y queso, edicion Especial', 6.50, 'foto02.jpg'),
(3, 'Pizza Margarita', 'Pizza clasica con tomate y queso', 8.00, 'foto03.jpg'),
(4, 'Ensalada Cesar', 'Ensalada fresca con pollo a la plancha', 4.50, 'foto04.jpg'),
(5, 'Combo Especial Familiar', 'Combo Especial para 4 personas', 15.00, 'foto05.jpg'),
(6, 'Cafe Americano', 'Cafe negro tradicional', 1.75, 'foto06.jpg'),
(7, 'Sanduche Club', 'Sanduche triple con jamon y queso', 5.25, 'foto07.jpg'),
(8, 'Jugo Natural', 'Jugo de frutas de temporada', 2.00, 'foto08.jpg');
SELECT*FROM Comida

--- Manipulación de Datos
--- INSERTAR 5 productos nuevos, misma marca (id_marca = 1, NESTLE),en una sola sentencia
INSERT INTO Producto VALUES
(2, 1, 'Azucar Blanca',       '1 Kg',  'ingrediente'),
(3, 1, 'Harina de Trigo',     '1 Kg',  'ingrediente'),
(4, 1, 'Mantequilla',         '500 Gr','ingrediente'),
(5, 1, 'Cafe Molido',         '1 Lb',  'ingrediente'),
(6, 1, 'Chocolate en Polvo',  '8 Oz',  'ingrediente');
SELECT*FROM Producto


-- 2 productos extra de otras marcas/tipos (completar 8 registros
-- en la tabla Producto y tener tipos 'bebida' y 'desechable')
INSERT INTO Producto VALUES
(7, 2, 'Coca Cola Original', '350 ml', 'bebida'),
(8, 6, 'Vaso Desechable',    '16 oz',  'desechable');
SELECT*FROM Producto

-- 3 medidas nuevas (Kg, Lb, Oz), en una sola sentencia INSERT
INSERT INTO Medida VALUES
(2, 'Kilogramos'),
(3, 'Libras'),
(4, 'Onzas');
SELECT*FROM Medida

--DATOS ADICIONALAS PARA COMPLETAR LOS 8 REGISTROS
-- 4 medidas extra 
INSERT INTO Medida VALUES
(5, 'Mililitros'),
(6, 'Litros'),
(7, 'Unidades'),
(8, 'Cucharadas');
SELECT*FROM Medida
-- Recetas adicionales 
INSERT INTO Receta_Producto VALUES
(1, 2, 2, 2, 0.05),  
(2, 3, 1, 1, 200),    
(2, 4, 1, 2, 50),     
(3, 3, 1, 1, 300),    
(3, 6, 1, 2, 30),     
(5, 7, 6, 1, 2),     
(5, 8, 7, 2, 4);    
SELECT*FROM Receta_Producto

--ACTUALIZACION DE PRECIOS
-- a) Modificar el precio de una Comida especifica buscando por su ID
UPDATE Comida SET precio = 3.00 WHERE id_comida = 1;
SELECT*FROM Comida
-- b) Incrementar en un 10% el precio de todas las comidas cuya descripcion (detalles) contenga la palabra "Especial"
UPDATE Comida SET precio = precio * 1.10 WHERE detalles LIKE '%Especial%';
SELECT*FROM Comida
---ELIMINACION DE REGISTROS
--a) Eliminar un producto especifico que no se utilice en ninguna receta (Cafe Molido, id_producto = 5, no aparece en Receta_Producto)
DELETE FROM Producto
WHERE id_producto = 5
  AND NOT EXISTS (
      SELECT 1 FROM Receta_Producto rp
      WHERE rp.id_producto = Producto.id_producto
  );
  SELECT*FROM Producto
-- b)Eliminar todas las recetas de comida que tengan una cantidad de ingredientes superior a 10
DELETE FROM Receta_Producto
WHERE id_comida IN (
    SELECT id_comida
    FROM Receta_Producto
    GROUP BY id_comida
    HAVING COUNT(*) > 10
);
SELECT*FROM Comida

---RESOLUCION DE CONSULTAS
---Consultar todos los productos que pertenecen a la marca con ID = 1 (o nombre 'NESTLE') y que sean del tipo 'ingrediente'
SELECT p.id_producto, p.nombre, p.detalle, p.tipo, m.nom_marca
FROM Producto p
JOIN Marca m ON p.id_marca = m.id_marca
WHERE m.id_marca = 1
  AND p.tipo = 'ingrediente';
---Consultar el nombre de la comida, el nombre del producto y la cantidad necesaria, pero sólo para aquellas comidas cuyo precio de venta sea mayor a $5.00
SELECT c.nombre AS comida, p.nombre AS producto, rp.cantidad
FROM Comida c
JOIN Receta_Producto rp ON c.id_comida = rp.id_comida
JOIN Producto p ON rp.id_producto = p.id_producto
WHERE c.precio > 5.00;

---Listar los nombres de los productos junto con su medida (nom_medida) y el orden de preparación, filtrando solo los productos que se midan en 'Gramos'.
SELECT p.nombre AS producto, med.nom_medida, rp.orden_prepar
FROM Producto p
JOIN Receta_Producto rp ON p.id_producto = rp.id_producto
JOIN Medida med ON rp.id_medida = med.id_medida
WHERE med.nom_medida = 'Gramos';
---Listar el nombre de la comida y el total de la suma de las cantidades de productos utilizados, agrupado por el nombre de la comida.
SELECT c.nombre AS comida, SUM(rp.cantidad) AS total_cantidad
FROM Comida c
JOIN Receta_Producto rp ON c.id_comida = rp.id_comida
GROUP BY c.nombre;