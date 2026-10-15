-- Práctica 10: Fábrica de calzado
CREATE DATABASE IF NOT EXISTS fabrica_calzado CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE fabrica_calzado;

CREATE TABLE IF NOT EXISTS insumos (
  id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(100) NOT NULL, marca VARCHAR(80),
  composicion VARCHAR(120), existencias INT DEFAULT 0, color VARCHAR(40), tamano VARCHAR(40)
);
CREATE TABLE IF NOT EXISTS produccion (
  id INT AUTO_INCREMENT PRIMARY KEY, fecha DATE, hora VARCHAR(10), modelo VARCHAR(80),
  color VARCHAR(40), talla VARCHAR(10), cantidad INT DEFAULT 0, tipo VARCHAR(50)
);
CREATE TABLE IF NOT EXISTS ventas (
  id INT AUTO_INCREMENT PRIMARY KEY, modelo VARCHAR(80), cantidad INT DEFAULT 0,
  nombre VARCHAR(100), tipo VARCHAR(50), talla VARCHAR(10), color VARCHAR(40),
  material VARCHAR(80), precio DECIMAL(10,2) DEFAULT 0
);
CREATE TABLE IF NOT EXISTS recursos_humanos (
  id_emp INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(80), a_pat VARCHAR(80), a_mat VARCHAR(80),
  depto VARCHAR(80), puesto VARCHAR(80), turno VARCHAR(30), sueldo DECIMAL(10,2) DEFAULT 0,
  telefono VARCHAR(30), direccion VARCHAR(160)
);
CREATE TABLE IF NOT EXISTS producto_terminado (
  id INT AUTO_INCREMENT PRIMARY KEY, modelo VARCHAR(80), talla VARCHAR(10), color VARCHAR(40),
  material VARCHAR(80), tipo VARCHAR(50), precio_venta DECIMAL(10,2) DEFAULT 0, ubicacion VARCHAR(60)
);
-- La aplicación inserta 20 registros ficticios por módulo en el primer arranque
-- cuando la tabla insumos está vacía. No se necesita insertar datos manualmente.
