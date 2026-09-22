# 🕵️ El Detective de Bugs

Sistema de detección, diagnóstico y reparación automática de errores de
software.

El proyecto integra un **repo víctima**, **n8n en Railway**, un **RAG
con Supabase + pgvector**, un **agente local Flask/OpenCode** y
**Cloudflare Tunnel**.

## Índice

1.  [Arquitectura](#1-arquitectura)
2.  [Estructura del monorepo](#2-estructura-del-monorepo)
3.  [Requisitos](#3-requisitos)
4.  [Repo víctima](#4-repo-víctima)
5.  [n8n en Railway](#5-n8n-en-railway)
6.  [RAG con Supabase](#6-rag-con-supabase)
7.  [Agente local](#7-agente-local)
8.  [OpenCode](#8-opencode)
9.  [Cloudflare Tunnel](#9-cloudflare-tunnel)
10. [Conectar todo](#10-conectar-todo)
11. [Prueba completa](#11-prueba-completa)
12. [Bug de prueba](#12-bug-de-prueba)
13. [Variables de entorno](#13-variables-de-entorno)
14. [Seguridad](#14-seguridad)
15. [Problemas frecuentes](#15-problemas-frecuentes)
16. [Git y monorepo](#16-git-y-monorepo)
17. [Checklist](#17-checklist)
18. [Comandos rápidos](#18-comandos-rápidos)
19. [Archivos importantes](#19-archivos-importantes)

------------------------------------------------------------------------

# 1. Arquitectura

``` text
                    EL DETECTIVE DE BUGS

┌──────────────────────┐
│     REPO VÍCTIMA     │
│ Node.js / Express    │
│     localhost:3000   │
└──────────┬───────────┘
           │ error / anomalía
           ▼
┌──────────────────────┐
│   Cloudflare Tunnel  │
└──────────┬───────────┘
           ▼
┌──────────────────────────────────────┐
│            n8n / Railway             │
│             ORQUESTADOR              │
└────────────┬──────────────┬──────────┘
             │              │
             │ RAG          │ HTTP + token
             ▼              ▼
     ┌──────────────┐  ┌────────────────┐
     │ Supabase     │  │ Agente Flask   │
     │ pgvector     │  │ localhost:5000 │
     │              │  │                │
     │documents_bugs│  │ OpenCode       │
     │ incidentes   │  └───────┬────────┘
     └──────────────┘          │
                               ▼
                         REPO VÍCTIMA
                               │
                               ▼
                              FIX
```

Flujo:

``` text
Bug
 ↓
Express
 ↓
POST /api/error-critico
 ↓
n8n /webhook/error-critico
 ↓
normalización
 ↓
RAG / Supabase
 ↓
contexto
 ↓
agente /procesar
 ↓
OpenCode
 ↓
lee y modifica repo-victima
 ↓
verifica
 ↓
resultado
```

El workflow también consulta anomalías periódicamente:

``` text
Cada 5 minutos
 ↓
/api/monitoreo/anomalias
 ↓
¿Hay anomalías?
 ↓
normalizar
 ↓
RAG
 ↓
agente
```

------------------------------------------------------------------------

# 2. Estructura del monorepo

Este proyecto se organiza actualmente como un único repositorio Git:

``` text
detective-de-bugs/
│
├── .git/
├── .gitignore
│
├── agente-detective/
│   ├── .env.example
│   ├── README.md
│   ├── agent_server.py
│   ├── pipeline.py
│   └── requirements.txt
│
├── rag-supabase/
│   ├── .env.example
│   ├── README.md
│   ├── ingest_chunks.py
│   ├── requirements.txt
│   └── setup.sql
│
└── repo-victima/
    ├── .env.example
    ├── README.md
    ├── bugs-originales/
    ├── diagnostico.json
    ├── opencode.json
    ├── package-lock.json
    ├── package.json
    ├── public/
    └── src/
```

`repo-victima` y `agente-detective` originalmente eran repositorios Git
independientes. Para formar este monorepo se eliminaron los `.git`
internos de las copias incluidas aquí.

Los repositorios originales de GitHub pueden seguir existiendo; este
repositorio contiene ahora el código integrado del sistema completo.

------------------------------------------------------------------------

# 3. Requisitos

Instalar:

-   Git
-   Node.js + npm
-   Python
-   Supabase
-   OpenAI API
-   Railway
-   n8n
-   OpenCode
-   `cloudflared`

Comprobar:

``` powershell
git --version
node --version
npm --version
python --version
cloudflared --version
```

Después de instalar OpenCode:

``` powershell
opencode --version
```

------------------------------------------------------------------------

# 4. Repo víctima

## 4.1. Instalar

Si se trabaja desde el monorepo:

``` powershell
cd repo-victima
npm install
```

Si se clona por separado:

``` powershell
git clone <URL_REPO_VICTIMA>
cd repo-victima
npm install
```

## 4.2. `.env`

Crear el `.env` a partir de `.env.example`.

Para conectar errores críticos con n8n:

``` env
N8N_WEBHOOK_URL=https://TU_DOMINIO_N8N.up.railway.app/webhook/error-critico
```

No subir `.env`.

## 4.3. Ejecutar

``` powershell
npm run dev
```

Debe quedar disponible aproximadamente en:

``` text
http://localhost:3000
```

Endpoint utilizado en la prueba:

``` text
http://localhost:3000/api/usuarios/2/es-mayor-de-edad
```

------------------------------------------------------------------------

# 5. n8n en Railway

## 5.1. Crear n8n

En Railway:

``` text
New Project
  ↓
Template
  ↓
n8n
```

Como alternativa se puede utilizar:

``` text
n8nio/n8n
```

## 5.2. Dominio

En el servicio:

``` text
Settings
  ↓
Networking
  ↓
Generate Domain
```

Ejemplo:

``` text
https://n8n-production-xxxx.up.railway.app
```

## 5.3. Variables

Configuración base:

``` env
N8N_PORT=${{PORT}}
N8N_PROTOCOL=https
WEBHOOK_URL=https://TU_DOMINIO_N8N.up.railway.app
GENERIC_TIMEZONE=America/Bogota
```

La autenticación del editor debe configurarse según el
despliegue/versión de n8n.

## 5.4. Volumen

Crear un Volume:

``` text
/home/node/.n8n
```

Esto conserva workflows, credenciales y datos.

## 5.5. Importar workflow

El workflow utilizado es:

``` text
orquestador-agente-cloudflare.json
```

En n8n:

``` text
Workflows
 ↓
Import from File
 ↓
orquestador-agente-cloudflare.json
```

Contiene:

-   `POST /webhook/error-critico`
-   monitor cada 5 minutos
-   normalización de crashes
-   normalización de anomalías
-   recuperación de contexto RAG
-   llamada al agente
-   `X-Agent-Token`
-   timeout HTTP de `420000 ms`

El `stack_trace` del crash se normaliza a:

``` text
descripcion
```

y se conservan campos como:

``` text
error_id
timestamp
endpoint
severity
origen
```

------------------------------------------------------------------------

# 6. RAG con Supabase

El RAG proporciona contexto para que n8n pueda recuperar información
relacionada con el error.

## 6.1. Supabase

Crear un proyecto en:

``` text
https://supabase.com/
```

## 6.2. Ejecutar SQL

En:

``` text
SQL Editor → New query
```

ejecutar:

``` text
rag-supabase/setup.sql
```

El esquema crea/habilita:

``` text
pgvector
documents_bugs
incidentes
match_documents_bugs
match_incidentes
```

Los embeddings son de:

``` text
1536 dimensiones
```

y utilizan:

``` text
text-embedding-3-small
```

## 6.3. `.env`

Este RAG se ejecuta en un entorno backend/controlado, por lo que utiliza la **Secret API Key de Supabase**, no una clave pública.

Supabase actualmente utiliza:

``` text
Publishable key → para componentes públicos
Secret key      → para backend/servidores
```

La clave secreta tiene el formato:

``` text
sb_secret_...
```

y debe mantenerse únicamente en el backend y en variables de entorno. Supabase está migrando las claves legacy `anon` y `service_role` hacia `publishable` y `secret`. citeturn0search0turn0search1


En `rag-supabase/.env`:

``` env
OPENAI_API_KEY=TU_OPENAI_API_KEY
SUPABASE_URL=https://TU_PROYECTO.supabase.co
SUPABASE_SECRET_KEY=sb_secret_TU_CLAVE_SECRETA
```

Para la ingesta inicial, el README del RAG indica utilizar
`secret key`, no `publishable key`.

Nunca expongas `secret key` en frontend.

## 6.4. Entorno Python

``` powershell
cd rag-supabase
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell no permite activar:

``` cmd
.venv\Scripts\activate
```

## 6.5. Dependencias

``` powershell
pip install -r requirements.txt
```

Dentro de `.venv` no necesitas `--break-system-packages`.

## 6.6. Ingesta

``` powershell
python ingest_chunks.py
```

El script:

1.  carga `.env`;
2.  crea cliente OpenAI;
3.  crea cliente Supabase;
4.  recorre los chunks;
5.  genera embeddings;
6.  inserta en `documents_bugs`.

Resultado esperado:

``` text
11 chunks procesados
Proceso completado.
```

En Supabase:

``` text
documents_bugs
```

debe haber:

``` text
11 filas
```

## 6.7. Recuperación

n8n utiliza:

``` text
Tabla: documents_bugs
Función: match_documents_bugs
```

Flujo:

``` text
error
 ↓
embedding
 ↓
match_documents_bugs
 ↓
chunks similares
 ↓
contexto
 ↓
prompt del agente
```

------------------------------------------------------------------------

# 7. Agente local

El agente es el componente que puede acceder físicamente al repositorio
víctima.

## 7.1. Entorno

``` powershell
cd agente-detective
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 7.2. Dependencias

``` powershell
pip install -r requirements.txt
```

## 7.3. `.env`

Ejemplo:

``` env
OPENAI_API_KEY=TU_OPENAI_API_KEY

AGENT_TOKEN=TU_TOKEN_LARGO_Y_SEGURO

REPO_PATH=C:\Users\TU_USUARIO\OneDrive\Documentos\Detective de bugs\repo-victima

AGENTE_MODELO=opencode/nemotron-3-ultra-free

TIMEOUT_AGENTE_SEG=300
```

`REPO_PATH` debe ser una ruta normal:

``` env
REPO_PATH=C:\Users\...
```

No:

``` env
REPO_PATH=rC:\Users\...
```

La `r` es sintaxis de Python, no de `.env`.

Comprobar:

``` powershell
Test-Path "C:\Users\TU_USUARIO\...\repo-victima"
```

Debe responder:

``` text
True
```

## 7.4. Iniciar

``` powershell
python agent_server.py
```

Objetivo:

``` text
http://localhost:5000
```

------------------------------------------------------------------------

# 8. OpenCode

## 8.1. Instalar

``` powershell
npm install -g @opencode/cli
```

Comprobar:

``` powershell
opencode --version
```

Si no aparece:

``` powershell
where.exe opencode
```

## 8.2. Modelo

Configuración actual:

``` env
AGENTE_MODELO=opencode/nemotron-3-ultra-free
```

## 8.3. `opencode.json`

El agente se llama:

``` text
detective-de-bugs
```

Configuración autónoma:

``` json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "detective-de-bugs": {
      "description": "Diagnostica y arregla bugs en el repo víctima.",
      "mode": "primary",
      "permission": {
        "*": "allow",
        "webfetch": "deny"
      },
      "prompt": "Sos El Detective de Bugs, un agente autónomo de diagnóstico y reparación. Recibís un error con su descripción o stack trace y tenés acceso al repositorio. Investigá directamente el error, leé los archivos relevantes, encontrá la causa raíz y aplicá el fix cuando sea claro y seguro. No preguntes al usuario cuál es el error ni esperes información adicional. Para bugs mecánicos claros como typos o referencias indefinidas, aplicá el fix directamente y usá confianza alta. No modifiques archivos fuera del repositorio, no ejecutes comandos destructivos y no modifiques dependencias sin necesidad. Al terminar, respondé únicamente con JSON válido usando los campos diagnostico, accion_tomada, confianza, archivo_modificado y resumen_para_humano."
    }
  },
  "permission": {
    "*": "allow",
    "webfetch": "deny"
  }
}
```

`* = allow` permite que la ejecución autónoma use herramientas como:

``` text
glob
read
edit
bash
```

`webfetch` permanece denegado.

------------------------------------------------------------------------

# 9. Cloudflare Tunnel

n8n está en Railway y los servicios principales están en local.
Cloudflare permite que Railway pueda acceder a ellos.

## 9.1. Repo víctima

Con el repo funcionando:

``` powershell
cloudflared tunnel --url http://localhost:3000
```

Se obtiene algo como:

``` text
https://xxxxxxxx.trycloudflare.com
```

## 9.2. Agente

Con Flask funcionando:

``` powershell
cloudflared tunnel --url http://localhost:5000
```

Se obtiene:

``` text
https://yyyyyyyy.trycloudflare.com
```

## 9.3. Quick Tunnel

Las URLs `trycloudflare.com` son temporales.

Si se reinicia `cloudflared`, la URL puede cambiar.

Por tanto hay que actualizar en n8n:

``` text
URL del repo víctima
URL del agente
```

No se necesita una credencial de Cloudflare para estos Quick Tunnels.

Para producción conviene utilizar un túnel administrado con hostname
estable.

------------------------------------------------------------------------

# 10. Conectar todo

## 10.1. Repo víctima → n8n

En el `.env`:

``` env
N8N_WEBHOOK_URL=https://TU_DOMINIO_N8N.up.railway.app/webhook/error-critico
```

## 10.2. URL del repo víctima en n8n

Nodo:

``` text
Consultar monitor anomalías
```

Debe utilizar:

``` text
https://xxxxx.trycloudflare.com/api/monitoreo/anomalias
```

## 10.3. URL del agente en n8n

Nodo:

``` text
Llamar agente local (via Cloudflare)
```

Debe utilizar:

``` text
https://yyyyy.trycloudflare.com/procesar
```

## 10.4. Token

Header:

``` text
X-Agent-Token: TU_AGENT_TOKEN
```

Agente:

``` env
AGENT_TOKEN=TU_AGENT_TOKEN
```

Deben coincidir exactamente.

## 10.5. Payload

Para crashes:

``` json
{
  "error_id": "...",
  "timestamp": "...",
  "descripcion": "...",
  "endpoint": "...",
  "severity": "...",
  "origen": "webhook_excepcion"
}
```

Para anomalías:

``` json
{
  "error_id": "...",
  "timestamp": "...",
  "descripcion": "...",
  "endpoint": "...",
  "severity": "...",
  "origen": "monitor_anomalias"
}
```

------------------------------------------------------------------------

# 11. Prueba completa

Se necesitan cuatro terminales locales:

### Terminal 1 --- repo víctima

``` powershell
cd repo-victima
npm run dev
```

### Terminal 2 --- agente

``` powershell
cd agente-detective
.\.venv\Scripts\Activate.ps1
python agent_server.py
```

### Terminal 3 --- Cloudflare repo víctima

``` powershell
cloudflared tunnel --url http://localhost:3000
```

### Terminal 4 --- Cloudflare agente

``` powershell
cloudflared tunnel --url http://localhost:5000
```

Además:

``` text
n8n en Railway
Supabase
```

deben estar configurados.

Flujo esperado:

``` text
1. Se dispara el bug
2. Repo víctima detecta la excepción
3. Se envía el payload a n8n
4. n8n normaliza
5. n8n consulta RAG
6. n8n llama /procesar
7. Cloudflare entrega la petición a Flask
8. Flask valida X-Agent-Token
9. OpenCode analiza repo-victima
10. Encuentra la causa
11. Modifica el archivo
12. Verifica
13. Devuelve JSON
14. n8n recibe el resultado
```

------------------------------------------------------------------------

# 12. Bug de prueba

Bug:

``` js
usuarioo.edad
```

Correcto:

``` js
usuario.edad
```

Error:

``` text
ReferenceError: usuarioo is not defined
```

Endpoint:

``` text
GET /api/usuarios/2/es-mayor-de-edad
```

Flujo:

``` text
usuarioo.edad
 ↓
ReferenceError
 ↓
n8n
 ↓
RAG
 ↓
agente
 ↓
OpenCode
 ↓
usuario.edad
 ↓
verificación
```

Este caso está incluido en el contexto del RAG.

------------------------------------------------------------------------

# 13. Variables de entorno

## Repo víctima

``` env
N8N_WEBHOOK_URL=https://TU_DOMINIO_N8N.up.railway.app/webhook/error-critico
```

## RAG

``` env
OPENAI_API_KEY=TU_OPENAI_API_KEY
SUPABASE_URL=https://TU_PROYECTO.supabase.co
SUPABASE_SECRET_KEY=sb_secret_TU_CLAVE_SECRETA
```

## Agente

``` env
OPENAI_API_KEY=TU_OPENAI_API_KEY
AGENT_TOKEN=TU_TOKEN_LARGO_Y_SEGURO
REPO_PATH=C:\Users\TU_USUARIO\...\repo-victima
AGENTE_MODELO=opencode/nemotron-3-ultra-free
TIMEOUT_AGENTE_SEG=300
```

## n8n

``` env
N8N_PORT=${{PORT}}
N8N_PROTOCOL=https
WEBHOOK_URL=https://TU_DOMINIO_N8N.up.railway.app
GENERIC_TIMEZONE=America/Bogota
```

------------------------------------------------------------------------

# 14. Seguridad

Nunca subir:

``` text
.env
OPENAI_API_KEY
SUPABASE_SECRET_KEY
AGENT_TOKEN
N8N_BASIC_AUTH_PASSWORD
```

Sí subir:

``` text
.env.example
```

`.gitignore` raíz recomendado:

``` gitignore
.env
.env.*
!.env.example

node_modules/

.venv/
venv/
env/

__pycache__/
*.py[cod]

*.log

.DS_Store
Thumbs.db
```

Los `.gitignore` de las subcarpetas también pueden existir; Git los
respeta. Para el monorepo se recomienda mantener las reglas comunes en
el `.gitignore` raíz.

------------------------------------------------------------------------

# 15. Problemas frecuentes

## `npm install` falla

``` powershell
node --version
npm --version
npm install
```

Si `node_modules` está corrupto:

``` powershell
Remove-Item -Recurse -Force node_modules
npm install
```

## Python no se reconoce

``` powershell
python --version
```

o:

``` powershell
py --version
```

Si funciona `py`:

``` powershell
py -m venv .venv
```

## No se puede activar `.venv`

PowerShell:

``` powershell
.\.venv\Scripts\Activate.ps1
```

CMD:

``` cmd
.venv\Scripts\activate
```

## OpenCode no aparece

``` powershell
where.exe opencode
```

Si no aparece:

``` powershell
npm install -g @opencode/cli
opencode --version
```

## OpenCode rechaza herramientas

Revisar:

``` json
"permission": {
  "*": "allow",
  "webfetch": "deny"
}
```

## `REPO_PATH` falla

Correcto:

``` env
REPO_PATH=C:\Users\usuario\...\repo-victima
```

Incorrecto:

``` env
REPO_PATH=rC:\Users\...
```

Comprobar:

``` powershell
Test-Path "C:\Users\usuario\...\repo-victima"
```

## n8n devuelve 401

Comparar:

``` text
X-Agent-Token
```

contra:

``` env
AGENT_TOKEN
```

## Cloudflare no conecta

Probar primero:

``` powershell
curl http://localhost:3000
curl http://localhost:5000
```

Después iniciar nuevamente:

``` powershell
cloudflared tunnel --url http://localhost:3000
```

o:

``` powershell
cloudflared tunnel --url http://localhost:5000
```

## n8n tiene una URL vieja

Los Quick Tunnels cambian de URL. Actualizar los nodos de n8n.

## RAG no encuentra información

Verificar:

``` text
documents_bugs → 11 filas
match_documents_bugs → existe
```

## Error de `SUPABASE_SECRET_KEY`

La ingesta usa `secret key`, no `publishable key`. Nunca exponer esa clave en
frontend.

## Timeout de n8n

El workflow utiliza:

``` text
420000 ms = 7 minutos
```

pero un proxy externo puede tener un límite menor. Durante las pruebas
apareció un límite de proxy de 120 segundos.

Una arquitectura más robusta es asíncrona:

``` text
POST /procesar
 ↓
job_id inmediato
 ↓
trabajo en segundo plano
 ↓
GET /procesar/<job_id>
 ↓
resultado
```

Aumentar el timeout de n8n por sí solo no elimina los límites de proxies
intermedios.

------------------------------------------------------------------------

# 16. Git y monorepo

El objetivo es tener **un único Git en la raíz**:

``` text
detective-de-bugs/
├── .git/
├── agente-detective/
├── rag-supabase/
└── repo-victima/
```

No deben existir `.git` internos si se quiere un monorepo real.

Comprobar:

``` powershell
git status
```

y:

``` powershell
git rev-parse --show-toplevel
```

Agregar cambios:

``` powershell
git add .
```

Commit:

``` powershell
git commit -m "Actualizar Detective de Bugs"
```

Push:

``` powershell
git push
```

Así, un cambio realizado en:

``` text
repo-victima/
```

o:

``` text
agente-detective/
```

pertenece al historial del mismo repositorio.

### Si al crear el monorepo aparece:

``` text
warning: adding embedded git repository
```

significa que una carpeta todavía contiene un `.git`.

Si se quiere un monorepo, primero sacar la carpeta del índice:

``` powershell
git rm --cached -r -f agente-detective
git rm --cached -r -f repo-victima
```

y, únicamente si se confirma que deben dejar de ser repositorios Git
internos, eliminar sus `.git` locales:

``` powershell
Remove-Item -Recurse -Force .\agente-detective\.git
Remove-Item -Recurse -Force .\repo-victima\.git
```

Después:

``` powershell
git add .
git status
```

No se deben eliminar los archivos del proyecto; solamente las carpetas
`.git` internas.

------------------------------------------------------------------------

# 17. Checklist

## Repo víctima

-   [ ] Node.js
-   [ ] npm
-   [ ] `npm install`
-   [ ] `.env`
-   [ ] `N8N_WEBHOOK_URL`
-   [ ] `npm run dev`
-   [ ] puerto 3000

## n8n / Railway

-   [ ] Railway
-   [ ] n8n desplegado
-   [ ] dominio público
-   [ ] `WEBHOOK_URL`
-   [ ] Volume `/home/node/.n8n`
-   [ ] workflow importado
-   [ ] URLs configuradas
-   [ ] Supabase configurado
-   [ ] workflow activo

## RAG

-   [ ] Supabase
-   [ ] `setup.sql`
-   [ ] pgvector
-   [ ] `documents_bugs`
-   [ ] `incidentes`
-   [ ] `match_documents_bugs`
-   [ ] `match_incidentes`
-   [ ] `.venv`
-   [ ] dependencias
-   [ ] `.env`
-   [ ] OpenAI API key
-   [ ] Supabase URL/key
-   [ ] `python ingest_chunks.py`
-   [ ] 11 filas

## Agente

-   [ ] `.venv`
-   [ ] dependencias
-   [ ] OpenCode
-   [ ] `opencode --version`
-   [ ] `REPO_PATH`
-   [ ] `AGENT_TOKEN`
-   [ ] `AGENTE_MODELO`
-   [ ] `opencode.json`
-   [ ] Flask
-   [ ] puerto 5000

## Cloudflare

-   [ ] `cloudflared`
-   [ ] tunnel :3000
-   [ ] URL repo víctima
-   [ ] tunnel :5000
-   [ ] URL agente
-   [ ] URLs actualizadas en n8n

## Git

-   [ ] un solo `.git` raíz
-   [ ] no hay `.git` internos
-   [ ] `.gitignore`
-   [ ] `.env` ignorados
-   [ ] `.env.example` incluidos
-   [ ] commit
-   [ ] remote
-   [ ] push

------------------------------------------------------------------------

# 18. Comandos rápidos

## Repo víctima

``` powershell
cd repo-victima
npm install
npm run dev
```

## RAG

``` powershell
cd rag-supabase
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python ingest_chunks.py
```

## Agente

``` powershell
cd agente-detective
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm install -g @opencode/cli
opencode --version
python agent_server.py
```

## Cloudflare repo víctima

``` powershell
cloudflared tunnel --url http://localhost:3000
```

## Cloudflare agente

``` powershell
cloudflared tunnel --url http://localhost:5000
```

## Git

Desde la raíz:

``` powershell
git status
git add .
git commit -m "Actualizar Detective de Bugs"
git push
```

------------------------------------------------------------------------

# 19. Archivos importantes

## `repo-victima/`

-   `src/server.js` --- servidor Express.
-   `src/errorCritico.js` --- comunicación de errores críticos con n8n.
-   `src/monitoreo.js` --- monitor de anomalías.
-   `src/usuarios.js` --- lógica de usuarios y bug de prueba.
-   `opencode.json` --- configuración del agente OpenCode.

## `rag-supabase/`

-   `setup.sql` --- estructura de Supabase/pgvector.
-   `ingest_chunks.py` --- generación de embeddings e ingesta.
-   `requirements.txt` --- dependencias.

## `agente-detective/`

-   `agent_server.py` --- servidor Flask.
-   `pipeline.py` --- pipeline del agente.
-   `requirements.txt` --- dependencias.

------------------------------------------------------------------------

# 🔗 Flujo final

``` text
                    ┌─────────────────┐
                    │   REPO VÍCTIMA  │
                    │     :3000       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    CLOUDFLARE   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   n8n RAILWAY   │
                    └───────┬─┬───────┘
                            │ │
                 ┌──────────┘ └──────────┐
                 ▼                       ▼
          ┌──────────────┐       ┌────────────────┐
          │   SUPABASE   │       │ AGENTE FLASK   │
          │   pgvector   │       │     :5000      │
          └──────────────┘       └───────┬────────┘
                                         │
                                         ▼
                                  ┌─────────────┐
                                  │   OpenCode  │
                                  └──────┬──────┘
                                         │
                                         ▼
                                  ┌─────────────┐
                                  │ REPO VÍCTIMA│
                                  │     FIX     │
                                  └─────────────┘
```

El resultado esperado es:

``` text
BUG
 ↓
DETECCIÓN
 ↓
RAG
 ↓
DIAGNÓSTICO
 ↓
AGENTE
 ↓
OPENCode
 ↓
CAMBIO
 ↓
VERIFICACIÓN
```

------------------------------------------------------------------------

## Documentación de referencia

Railway:

-   https://docs.railway.com/guides/n8n
-   https://docs.railway.com/quick-start

Cloudflare:

-   https://developers.cloudflare.com/tunnel/get-started/
-   https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/

OpenCode:

-   https://opencode.ai/v2/docs
-   https://opencode.ai/download

Supabase:

-   https://supabase.com/

> Las URLs reales de repositorios, dominios, tokens y credenciales deben
> configurarse en cada instalación. No deben escribirse en este README.

------------------------------------------------------------------------

## Estado

Este README documenta la instalación y arquitectura del **El Detective
de Bugs** como monorepo: repo víctima, RAG, agente local, OpenCode,
n8n/Railway, Supabase y Cloudflare Tunnel.
