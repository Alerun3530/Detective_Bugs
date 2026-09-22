// Base de datos en memoria — simple a propósito, no es el foco del proyecto.

function usuariosDeFabrica() {
  return [
    { id: 1, nombre: "Ana Torres", email: "ana@example.com", edad: 29, compras: 7, descuentoAplicado: false },
    { id: 2, nombre: "Luis Pérez", email: "luis@example.com", edad: 17, compras: 2, descuentoAplicado: false },
    { id: 3, nombre: "Marta Gómez", email: "marta@example.com", edad: 41, compras: 12, descuentoAplicado: false },
    { id: 4, nombre: "Carlos Ruiz", email: "carlos@example.com", edad: 22, compras: 0, descuentoAplicado: false },
    // Precargado a propósito para disparar el Bug 3 sin pasos extra:
    // 10+ compras pero menor de edad.
    { id: 5, nombre: "Sofía Ramos", email: "sofia@example.com", edad: 16, compras: 14, descuentoAplicado: false },
  ];
}

let usuarios = usuariosDeFabrica();
let nextId = 6;

function resetearDatos() {
  usuarios = usuariosDeFabrica();
  nextId = 6;
}

function getUsuarios() {
  return usuarios;
}

function getUsuarioPorId(id) {
  return usuarios.find((u) => u.id === id);
}

function crearUsuario(datos) {
  const nuevo = {
    id: nextId++,
    nombre: datos.nombre,
    email: datos.email,
    edad: datos.edad,
    compras: 0,
    descuentoAplicado: false,
  };
  usuarios.push(nuevo);
  return nuevo;
}

module.exports = { usuarios, getUsuarios, getUsuarioPorId, crearUsuario, resetearDatos };
