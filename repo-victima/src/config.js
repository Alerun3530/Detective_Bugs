const express = require("express");

const router = express.Router();

// GET /api/config
// Expone únicamente información que es segura para el navegador.
router.get("/", (req, res) => {
  res.json({
    supabaseUrl: process.env.SUPABASE_URL || null,
    supabaseKey: process.env.SUPABASE_PUBLISHABLE_KEY || null
  });
});

module.exports = router;