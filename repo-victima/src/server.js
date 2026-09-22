require("dotenv").config();

const express = require("express");
const path = require("path");

const usuariosRouter = require("./usuarios");
const monitoreoRouter = require("./monitoreo");
const resetRouter = require("./reset");
const configRouter = require("./config");
const errorCriticoRouter = require("./errorCritico");

const app = express();

app.use(express.json());

app.use(
  express.static(path.join(__dirname, "..", "public"))
);

app.use("/api/usuarios", usuariosRouter);

app.use("/api/monitoreo", monitoreoRouter);

app.use("/api/reset", resetRouter);

app.use("/api/config", configRouter);

app.use("/api/error-critico", errorCriticoRouter);

// historial.html vive en src/, no en public/
app.get("/historial.html", (req, res) => {
  res.sendFile(path.join(__dirname, "historial.html"));
});

// Manejo de errores
app.use((err, req, res, next) => {
  console.error(err.stack);

  res.status(500).json({
    error: err.message,
    stack: err.stack
  });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(
    `repo-victima corriendo en http://localhost:${PORT}`
  );
});