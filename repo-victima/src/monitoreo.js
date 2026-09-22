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

  const usuarios = getUsuarios();
  const alertas = [];

  // Anomalía 2: Usuarios con edad inválida (negativa o > 120)
  usuarios
    .filter((u) => u.edad < 0 || u.edad > 120)
    .forEach((u) => {
      alertas.push({
        tipo: "edad_invalida",
        usuario_id: u.id,
        descripcion: `Usuario con edad inválida: ${u.edad} años.`,
        endpoint_afectado: `/api/usuarios/${u.id}`,
        severity: "high",
      });
    });

  // Anomalía 3: Compras negativas
  usuarios
    .filter((u) => u.compras < 0)
    .forEach((u) => {
      alertas.push({
        tipo: "compras_negativas",
        usuario_id: u.id,
        descripcion: `Usuario con compras negativas: ${u.compras}.`,
        endpoint_afectado: `/api/usuarios/${u.id}`,
        severity: "high",
      });
    });

  // Anomalía 4: Usuarios sin email o email inválido
  usuarios
    .filter((u) => !u.email || !u.email.includes("@"))
    .forEach((u) => {
      alertas.push({
        tipo: "email_invalido",
        usuario_id: u.id,
        descripcion: `Usuario con email inválido o faltante: "${u.email}".`,
        endpoint_afectado: `/api/usuarios/${u.id}`,
        severity: "medium",
      });
    });

  // Anomalía 5: Usuarios VIP sin compras (inconsistencia de datos)
  usuarios
    .filter((u) => u.compras === 0 && u.edad >= 18) // Solo adultos, menores no pueden ser VIP
    .forEach((u) => {
      alertas.push({
        tipo: "vip_sin_compras",
        usuario_id: u.id,
        descripcion: `Usuario adulto (${u.edad} años) con 0 compras. Verificar si nivel cliente es correcto.`,
        endpoint_afectado: `/api/usuarios/${u.id}/nivel-cliente`,
        severity: "low",
      });
    });

  res.json({
    anomalias_detectadas: alertas.length,
    alertas
  });
});

module.exports = router;