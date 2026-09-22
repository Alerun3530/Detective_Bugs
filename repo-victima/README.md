# repo-victima

API chica de usuarios (Node/Express) usada como "repo víctima" para el proyecto
**El Detective de Bugs**. Contiene 3 bugs plantados a propósito, con distinto
nivel de gravedad, para que el agente (OpenCode / Claude Code) los diagnostique
y decida si los arregla solo o los escala.

## Instalación

```bash
cd repo-victima
npm install
npm start
```

El servidor levanta en `http://localhost:3000`, con un front sencillo servido
en la raíz: lista los usuarios y trae un botón por cada bug para dispararlo
sin usar curl. También incluye `/historial.html`, que lee directo de la
tabla `incidentes` de Supabase y muestra cada acción real que tomó el
agente (necesita la URL y la clave `sb_publishable_...` de tu proyecto
Supabase — nunca la `secret`, esa no va en el navegador).

Nota: por default, una tabla nueva en Supabase no tiene Row Level Security
activado, así que la clave publishable ya puede leerla. Si en algún momento
activás RLS en `incidentes`, vas a necesitar agregar una policy de lectura
pública para que esta página siga funcionando.

## Endpoints

- `GET /api/usuarios` — lista todos los usuarios.
- `GET /api/usuarios/:id` — detalle de un usuario.
- `POST /api/usuarios` — crea un usuario (body: `{ "nombre", "email", "edad" }`).
- `GET /api/usuarios/:id/es-mayor-de-edad` — chequea si el usuario es mayor de edad.
- `GET /api/usuarios/:id/nivel-cliente` — calcula el nivel/tier del cliente.

## Bugs

Ver `README_BUGS.md` (uso interno del equipo) para el detalle de cada bug
plantado, dónde está en el código, y qué se espera que haga el agente con
cada uno.

## Volver todo a fábrica

Dos botones en la consola (`/`), o directo por API:

- **Restaurar datos** (`POST /api/reset/datos`) — reinicia los 5 usuarios
  en memoria a sus valores originales. Al toque, sin reiniciar nada. Sirve
  si el Bug 1 pisó la edad de algún usuario, o si creaste usuarios de
  prueba de más.
- **Restaurar código** (`POST /api/reset/codigo`) — pisa `usuarios.js`,
  `db.js` y `monitoreo.js` con las copias originales guardadas en
  `bugs-originales/`, deshaciendo cualquier fix que haya aplicado el
  agente. **Requiere reiniciar el servidor** para que tome el cambio
  (Node ya tiene el código viejo cargado en memoria).

Para que el reinicio sea automático en vez de manual, corré el servidor
con `npm run dev` en vez de `npm start` (usa `nodemon`, que reinicia
solo cuando detecta que un archivo cambió).
