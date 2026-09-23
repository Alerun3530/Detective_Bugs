# El Detective de Bugs — Guía para la clase (todo en Railway, sin Anthropic)

## Repos del proyecto

| Repo | Qué es | Qué hacer con él |
|---|---|---|
| [`Detective_Bugs`](https://github.com/Alerun3530/Detective_Bugs.git) | El repo principal: workflow de n8n, scripts del RAG, esta guía | **Clonar** (el único que se clona) |
| [`Dectective_Bugs_Repo_Victima`](https://github.com/Alerun3530/Dectective_Bugs_Repo_Victima.git) | La API con los 3 bugs plantados | **Fork** a tu cuenta |
| [`Detective_Bugs_Agente`](https://github.com/Alerun3530/Detective_Bugs_Agente.git) | El servidor del agente (Dockerfile + OpenCode) | **Fork** a tu cuenta |

**Por qué fork y no clone en esos dos:** el agente necesita hacer `git
push` sobre repo-victima con TU token de GitHub, y Railway necesita
deployar TU copia del código — si todos los alumnos usaran el mismo
repo original, se pisarían los cambios entre todos.

Todo se despliega en Railway. No hace falta instalar nada localmente
más que lo que ya tenés: `git`.

---

## Parte 0 — Fork y clone

### 0.1 Fork de los 2 repos

1. Andá a [`Dectective_Bugs_Repo_Victima`](https://github.com/Alerun3530/Dectective_Bugs_Repo_Victima.git) → botón **Fork** (arriba a la derecha) → **Create fork**.
2. Andá a [`Detective_Bugs_Agente`](https://github.com/Alerun3530/Detective_Bugs_Agente.git) → **Fork** → **Create fork**.

Ahora tenés `github.com/TU-USUARIO/Dectective_Bugs_Repo_Victima` y
`github.com/TU-USUARIO/Detective_Bugs_Agente` en tu propia cuenta.

### 0.2 Clonar el repo principal

```bash
git clone https://github.com/Alerun3530/Detective_Bugs.git
cd Detective_Bugs
```

Acá adentro vas a encontrar el workflow de n8n (`.json`), el `setup.sql`
y `ingest_chunks.py` del RAG.

---

## Parte 1 — Deployar repo-victima en Railway

### 1.1 Conectar el fork a Railway

1. [railway.com](https://railway.com) → logueate con GitHub (si no tenés cuenta, se crea sola al loguearte).
2. **New Project → Deploy from GitHub repo** → elegí `TU-USUARIO/Dectective_Bugs_Repo_Victima`.
3. Railway detecta que es un proyecto Node y lo buildea solo (`npm install` + `npm start`).

### 1.2 Variables de entorno

Servicio → **Variables**:

```env
N8N_WEBHOOK_URL=https://tu-n8n.up.railway.app/webhook/error-critico
SUPABASE_URL=https://tuproyecto.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
```

(`N8N_WEBHOOK_URL` y las de Supabase las completás en las Partes 2 y 3
— por ahora dejalas con cualquier valor, las volvés a editar después.)

### 1.3 Generar el dominio público

**Settings → Networking → Generate Domain**. Copiá la URL
(`https://repo-victima-production-xxxx.up.railway.app`) — la necesitás
en la Parte 5.

### 1.4 Confirmar

```bash
curl https://TU-REPO-VICTIMA.up.railway.app/api/monitoreo/anomalias
```

Debería devolver `"anomalias_detectadas": 1`.

---

## Parte 2 — Deployar n8n en Railway

### 2.1 Deployar el template

1. En Railway: **New Project** (uno separado del de repo-victima) → buscá el template oficial de n8n en `railway.com/template` (buscá "n8n") → **Deploy on Railway**.
2. En el mismo proyecto: **"+ New" → "Database" → "Add PostgreSQL"**.

### 2.2 Variables de entorno del servicio de n8n

Tomá los datos de conexión de la pestaña **"Connect"** del servicio de Postgres:

```env
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=<host>
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=<db>
DB_POSTGRESDB_USER=<usuario>
DB_POSTGRESDB_PASSWORD=<password>
N8N_HOST=tu-n8n.up.railway.app
N8N_PROTOCOL=https
N8N_EDITOR_BASE_URL=https://tu-n8n.up.railway.app
N8N_ENCRYPTION_KEY=<generalo con: openssl rand -base64 32>
```

### 2.3 Generar dominio y entrar

**Settings → Networking → Generate Domain**. Abrí la URL, creá tu
usuario admin (nombre, email, contraseña).

### 2.4 Importar el workflow

Menú (☰) → **Import from File** → elegí el `.json` del workflow que
está dentro de `Detective_Bugs/` (el repo que clonaste en la Parte 0).

### 2.5 Copiar la URL del webhook

Click en el nodo **`Webhook: error crítico`** → botón **"Copy"** sobre
la URL de producción. La necesitás en la Parte 5.

**No actives el workflow todavía** — le faltan 3 valores (Parte 5).

---

## Parte 3 — RAG en Supabase

### 3.1 Crear el proyecto

[supabase.com](https://supabase.com) → **New Project** → nombre,
contraseña, región → esperá 1-2 minutos.

### 3.2 Sacar las credenciales

**Project Settings → API Keys**:
- URL del proyecto
- Clave **`secret`** (`sb_secret_...`) — para el agente
- Clave **`publishable`** (`sb_publishable_...`) — para repo-victima

### 3.3 Crear las tablas (SQL Editor)

Abrí `Detective_Bugs/rag-supabase/setup.sql` (del repo que clonaste),
copiá todo el contenido, pegalo en el **SQL Editor** de Supabase, y
corré.

Si te tira error de que una función ya existe con otro tipo de
retorno (de un RAG viejo tuyo), corré antes:

```sql
drop function if exists match_documents_bugs;
drop function if exists match_incidentes;
```

y volvé a correr el `setup.sql`.

### 3.4 Cargar los chunks

```bash
cd Detective_Bugs/rag-supabase
cp .env.example .env
```

Completá `.env`:

```env
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://tuproyecto.supabase.co
SUPABASE_KEY=sb_secret_...
```

(Sí necesitás una key de OpenAI acá — es solo para generar los
embeddings del RAG, `text-embedding-3-small`, que es carísimo barato.
No tiene nada que ver con qué modelo usa el agente después.)

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1      # Windows
pip install -r requirements.txt
python ingest_chunks.py
```

### 3.5 Verificar

**Table Editor → `documents_bugs`** en Supabase → deberían aparecer 11 filas.

---

## Parte 4 — Deployar el agente en Railway (modelo gratis de OpenCode)

### 4.1 opencode.json va DENTRO del fork de repo-victima

Andá a tu fork `Dectective_Bugs_Repo_Victima` en GitHub (en la web, no
hace falta clonarlo local) → si no tiene ya un `opencode.json` en la
raíz, crealo con **"Add file → Create new file"**:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "detective-de-bugs": {
      "description": "Diagnostica y arregla bugs en el repo víctima.",
      "mode": "primary",
      "model": "opencode/big-pickle",
      "permission": { "*": "allow" },
      "prompt": "Sos El Detective de Bugs, un agente autónomo de diagnóstico y reparación. Recibís UN error puntual y tenés acceso de lectura y escritura al repositorio.\n\nAlcance: enfocate ÚNICAMENTE en el error específico reportado, no toques otros bugs que veas de paso.\n\n1. Encontrá la causa raíz real.\n2. Aplicá el fix directamente SIEMPRE. \"accion_tomada\" NUNCA puede ser \"escalado\".\n3. Si es lógica de negocio ambigua, igual aplicá el fix, marcá \"confianza\": \"baja\" y explicá el riesgo.\n4. Nunca toques archivos fuera del repo ni ejecutes comandos destructivos.\n\nDevolvé SIEMPRE este JSON:\n{\n  \"diagnostico\": \"causa raíz\",\n  \"accion_tomada\": \"fix_aplicado | solo_diagnostico\",\n  \"confianza\": \"alta | media | baja\",\n  \"archivo_modificado\": \"ruta o null\",\n  \"resumen_para_humano\": \"1-2 frases\"\n}"
    }
  },
  "permission": { "*": "allow" }
}
```

**Commit directo a `main`.**

### 4.2 Conseguir la API key gratis de OpenCode

1. Andá a [opencode.ai/auth](https://opencode.ai/auth).
2. Creá una cuenta (sin tarjeta) → **Create API Key**.
3. Copiala — la variable de entorno siempre se llama `OPENCODE_API_KEY`.

Modelos gratis disponibles ahora mismo (todos con prefijo `opencode/`,
**no** `opencode-go/` que es la suscripción paga):

| Modelo | Uso recomendado |
|---|---|
| `opencode/big-pickle` | General, el que usa esta guía por default |
| `opencode/minimax-m2.5-free` | Alternativa si big-pickle está saturado |
| `opencode/nemotron-3-super-free` | Otra alternativa |

Si querés cambiar el modelo, solo hay que tocar 2 lugares: el `"model"`
de `opencode.json` (4.1) y la variable `AGENTE_MODELO` (4.5) — tienen
que decir lo mismo.

### 4.3 Generar el token de GitHub (para que el agente pushee)

**GitHub → tu foto de perfil → Settings → Developer settings →
Personal access tokens → Tokens (classic) → Generate new token
(classic)** → nombre tipo `agente-detective` → marcá el checkbox
**"repo"** → **Generate token** → **copiá el token ya**, se muestra
una sola vez.

### 4.4 Deployar el fork del agente en Railway

1. Railway → **New Project → Deploy from GitHub repo** → elegí `TU-USUARIO/Detective_Bugs_Agente`.
2. Railway detecta el `Dockerfile` del repo y buildea el contenedor solo (instala OpenCode adentro — no en tu PC).

### 4.5 Variables de entorno del agente

Servicio del agente → **Variables**:

```env
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://tuproyecto.supabase.co
SUPABASE_KEY=sb_secret_...

AGENTE_MODELO=opencode/big-pickle
OPENCODE_API_KEY=<la key gratis del paso 4.2>

GITHUB_REPO_URL=https://TU_TOKEN@github.com/TU-USUARIO/Dectective_Bugs_Repo_Victima.git

AGENT_TOKEN=<generalo con: python -c "import secrets; print(secrets.token_hex(24))">
VENTANA_DEDUP_HORAS=2
```

**Ojo:** `GITHUB_REPO_URL` apunta a **TU FORK**, no al repo original —
si apunta al original, el `git push` va a fallar por falta de permisos
(a menos que seas colaborador del repo original, que no es el caso).

No hace falta `ANTHROPIC_API_KEY` — el único uso de OpenAI acá es para
el embedding del texto que se guarda en `incidentes` (la persistencia),
no para el razonamiento del agente, que corre 100% con el modelo
gratis de OpenCode.

### 4.6 Generar el dominio y confirmar

**Settings → Networking → Generate Domain**. Copiá la URL, y probá:

```bash
curl https://TU-AGENTE.up.railway.app/salud
```

Debería devolver `{"ok": true, ...}`.

---

## Parte 5 — Conectar todo

### 5.1 Actualizar el webhook en repo-victima

Volvé al servicio de `repo-victima` en Railway (Parte 1.2) → **Variables**
→ actualizá:

```env
N8N_WEBHOOK_URL=https://TU-N8N.up.railway.app/webhook/error-critico
```

(la URL exacta que copiaste en la Parte 2.5)

### 5.2 Actualizar las URLs en el workflow de n8n

Volvé al editor de n8n, en el workflow importado:

- **`Consultar monitor anomalías`** → `https://TU-REPO-VICTIMA.up.railway.app/api/monitoreo/anomalias`
- **`Llamar agente (Railway)`**:
  - URL → `https://TU-AGENTE.up.railway.app/procesar`
  - Header `X-Agent-Token` → el mismo valor que pusiste en `AGENT_TOKEN` (Parte 4.5)

### 5.3 Activar el workflow

Toggle **"Active"** arriba a la derecha del editor.

### 5.4 Probar el ciclo completo

1. Abrí `https://TU-REPO-VICTIMA.up.railway.app` → apretá "Disparar" en el Bug 1.
2. n8n → **Executions** → debería correr en menos de un minuto.
3. `curl https://TU-AGENTE.up.railway.app/trabajos/<job_id>` (el `job_id` te lo devuelve el `/procesar` de n8n en la respuesta) para ver el resultado.
4. Si `accion_tomada` fue `fix_aplicado`, Railway redeploya `repo-victima` solo al detectar el push del agente en GitHub.

---

## Resetear los bugs (volver de fábrica)

Cuando el agente arregla un bug, hace un commit en **tu fork** de
`Dectective_Bugs_Repo_Victima`. Para volver a tener los 3 bugs
originales y repetir la demo:

### Opción A — si el agente hizo exactamente 3 commits (uno por bug)

```bash
git clone https://github.com/TU-USUARIO/Dectective_Bugs_Repo_Victima.git
cd Dectective_Bugs_Repo_Victima
git log --oneline -5        # confirmá cuáles son los últimos commits antes de tocar nada
git reset --hard HEAD~3
git push --force
```

Esto borra los últimos 3 commits del historial y fuerza esa versión
vieja de vuelta a GitHub — Railway lo detecta como un push nuevo y
redeploya la versión con los bugs de nuevo.

⚠️ **`--force` reescribe el historial remoto.** Si más de una persona
trabaja sobre el mismo fork, esto le puede borrar commits a otro sin
avisar. Para un fork personal de la clase, es seguro.

### Opción B — si no estás seguro de cuántos commits hizo el agente

```bash
git log --oneline -10
```

Mirá la lista, contá cuántos commits arriba del último "commit humano"
tuyo hizo el agente (van a decir algo como `fix: ...` porque así arma
el mensaje `agent_server.py`), y ajustá el número:

```bash
git reset --hard HEAD~<esa-cantidad>
git push --force
```

### Opción C — la más simple, sin contar commits

Si sabés el hash del último commit tuyo (antes de que el agente tocara
nada), reseteá directo a ese punto:

```bash
git log --oneline           # buscá el hash de tu último commit "bueno"
git reset --hard <ese-hash>
git push --force
```

---

## Checklist final antes de la demo

- [ ] Fork de `Dectective_Bugs_Repo_Victima` y `Detective_Bugs_Agente` hechos
- [ ] `Detective_Bugs` clonado (para el workflow de n8n y el RAG)
- [ ] repo-victima deployado en Railway, `/api/monitoreo/anomalias` responde
- [ ] n8n deployado en Railway con Postgres, workflow importado
- [ ] `opencode.json` commiteado en la raíz del fork de repo-victima
- [ ] 11 chunks cargados en `documents_bugs` (Supabase)
- [ ] Agente deployado en Railway (Dockerfile detectado, build OK), `/salud` responde
- [ ] `OPENCODE_API_KEY` gratis configurada, `AGENTE_MODELO=opencode/big-pickle` (o el que hayas elegido) en `opencode.json` Y en las variables de Railway
- [ ] `GITHUB_REPO_URL` apunta a TU fork, con TU token
- [ ] `AGENT_TOKEN` idéntico en las variables del agente y en el nodo de n8n
- [ ] Workflow de n8n activado
- [ ] `VENTANA_DEDUP_HORAS=0` si vas a repetir pruebas seguidas
- [ ] Comandos de reset (`git reset --hard` + `push --force`) probados una vez antes de la demo en vivo
