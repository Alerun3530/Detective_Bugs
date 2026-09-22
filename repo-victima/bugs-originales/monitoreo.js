const express = require("express");

const router = express.Router();

const { getUsuarios } = require("./db");

// Bug 3 permanece desactivado hasta que el usuario
// presione el botón "Consultar monitor".
let bug3Activado = false;

// Activar el escenario del Bug 3
router.post("/activar-bug3", (req, res) => {
  bug3Activado = true;

  res.json({
    ok: true,
    mensaje: "Bug 3 activado."
  });
});

// Endpoint que consulta n8n
router.get("/anomalias", (req, res) => {

  // Antes de presionar el botón no se reporta ninguna anomalía.
  if (!bug3Activado) {
    return res.json({
      anomalias_detectadas: 0,
      alertas: []
    });
  }

  const alertas = getUsuarios()
    .filter((u) => u.compras >= 10 && u.edad < 18)
    .map((u) => ({
      tipo: "nivel_cliente_inconsistente",
      usuario_id: u.id,
      descripcion: `Usuario con ${u.compras} compras (alto valor) pero nivel forzado a "regular" por ser menor de edad. Revisar si la regla de negocio en /nivel-cliente es intencional.`,
      endpoint_afectado: `/api/usuarios/${u.id}/nivel-cliente`,
      severity: "medium",
    }));

  res.json({
    anomalias_detectadas: alertas.length,
    alertas
  });
});

module.exports = router;