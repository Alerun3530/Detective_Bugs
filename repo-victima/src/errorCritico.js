const express = require("express");

const router = express.Router();

router.post("/", async (req, res) => {
  try {
    const webhookUrl = process.env.N8N_WEBHOOK_URL;

    if (!webhookUrl) {
      return res.status(500).json({
        error: "N8N_WEBHOOK_URL no está configurada en el servidor."
      });
    }

    const response = await fetch(webhookUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(req.body)
    });

    const text = await response.text();

    let data;

    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }

    if (!response.ok) {
      return res.status(response.status).json({
        error: "n8n respondió con un error.",
        details: data
      });
    }

    return res.status(200).json(data);

  } catch (error) {
    console.error("Error comunicando con n8n:", error);

    return res.status(500).json({
      error: "No se pudo conectar con n8n.",
      details: error.message
    });
  }
});

module.exports = router;