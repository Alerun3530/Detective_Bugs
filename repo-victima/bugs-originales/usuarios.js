const express = require("express");
const router = express.Router();
const { getUsuarios, getUsuarioPorId, crearUsuario } = require("./db");

router.get("/", (req, res) => {
  res.json(getUsuarios());
});

router.get("/:id", (req, res) => {
  const usuario = getUsuarioPorId(Number(req.params.id));
  if (!usuario) return res.status(404).json({ error: "Usuario no encontrado" });
  res.json(usuario);
});

// >>> BUG 2 (bajo riesgo): falta validación de null / input vacío <<<
router.post("/", (req, res) => {
  const datos = req.body;
  const nombreLimpio = datos.nombre.trim();
  const emailLimpio = datos.email.trim();

  const nuevoUsuario = crearUsuario({
    nombre: nombreLimpio,
    email: emailLimpio,
    edad: datos.edad,
  });

  res.status(201).json(nuevoUsuario);
});

// >>> BUG 1 (bajo riesgo): typo / variable mal escrita <<<
router.get("/:id/es-mayor-de-edad", (req, res) => {
  const usuario = getUsuarioPorId(Number(req.params.id));
  if (!usuario) return res.status(404).json({ error: "Usuario no encontrado" });

  let esMayor = false;
  if (usuarioo.edad >= 18) {
    esMayor = true;
  }

  res.json({ id: usuario.id, edad: usuario.edad, esMayorDeEdad: esMayor });
});

// >>> BUG 3 (alto riesgo): lógica de negocio ambigua <<<
router.get("/:id/nivel-cliente", (req, res) => {
  const usuario = getUsuarioPorId(Number(req.params.id));
  if (!usuario) return res.status(404).json({ error: "Usuario no encontrado" });

  let nivel = "regular";

  if (usuario.compras >= 10 && usuario.edad >= 18) {
    nivel = "vip";
  } else if (usuario.compras >= 10 && usuario.edad < 18) {
    // TODO: revisar con negocio si esto es correcto. Un cliente con 10+
    // compras claramente es de alto valor, ¿por qué lo bajamos a
    // 'regular' solo por la edad? ¿O es una regla de compliance?
    nivel = "regular";
  } else if (usuario.compras >= 5) {
    nivel = "frecuente";
  }

  res.json({ id: usuario.id, compras: usuario.compras, edad: usuario.edad, nivel });
});

module.exports = router;
