const express = require("express");
const fs = require("fs");
const path = require("path");
const router = express.Router();
const { resetearDatos } = require("./db");

const CARPETA_ORIGINALES = path.join(__dirname, "..", "bugs-originales");
const CARPETA_SRC = __dirname;
const ARCHIVOS_CON_BUGS = ["usuarios.js", "db.js", "monitoreo.js"];

router.post("/datos", (req, res) => {
  resetearDatos();
  res.json({ ok: true, mensaje: "Datos reiniciados a los valores de fábrica." });
});

router.post("/codigo", (req, res) => {
  try {
    for (const archivo of ARCHIVOS_CON_BUGS) {
      fs.copyFileSync(path.join(CARPETA_ORIGINALES, archivo), path.join(CARPETA_SRC, archivo));
    }
    resetearDatos();
    res.json({
      ok: true,
      mensaje: "Código restaurado a la versión con bugs. Si corrés con 'npm run dev' (nodemon), el server ya se está reiniciando solo.",
      requiere_reinicio: true,
    });
  } catch (err) {
    res.status(500).json({ ok: false, error: err.message });
  }
});

module.exports = router;
