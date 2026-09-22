# RAG en Supabase — Módulo 4 (Contexto del proyecto)

Carga los 10 chunks de vulnerabilidades/errores más importantes (incluidos
los 3 bugs reales del repo víctima) + 1 chunk con el detalle de la lógica
de negocio del endpoint `/nivel-cliente`, como colección de "Contexto del
proyecto" (se carga una sola vez al inicio, según el plan).

## Orden de ejecución

1. **Crear el proyecto en Supabase** (si no lo tenés ya) en supabase.com.

2. **Correr `setup.sql`** en Supabase → SQL Editor. Esto:
   - habilita `pgvector`
   - crea la tabla `documents_bugs` (contexto del proyecto)
   - crea la tabla `incidentes` (historial — se llena después, en el
     Módulo 6/Flujo B, no ahora)
   - crea las funciones `match_documents_bugs` / `match_incidentes` para la
     búsqueda por similitud (esto es lo que usa el nodo Vector Store de
     n8n, o cualquier retrieval manual)

3. **Configurar credenciales**: copiar `.env.example` a `.env` y completar:
   - `OPENAI_API_KEY`: desde platform.openai.com
   - `SUPABASE_URL` y `SUPABASE_KEY`: Supabase → Project Settings → API
     (usar la **service_role key**, no la anon key, porque el script
     inserta datos desde un entorno de confianza, no desde el browser)

4. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```
   (sacá `--break-system-packages` si estás en un entorno virtual)

5. **Correr la ingesta**:
   ```bash
   python ingest_chunks.py
   ```
   Deberías ver "Procesando chunk 1 de 11..." hasta el 11, y al final
   "Proceso completado."

6. **Verificar en Supabase** → Table Editor → `documents_bugs` → deberían
   aparecer 11 filas.

## Los 10 (+1) chunks incluidos

| # | Tema | Gravedad |
|---|------|----------|
| 1 | Bug real: ReferenceError por typo (`usuarioo`) | Bajo |
| 2 | Bug real: falta de validación null/vacío en POST | Bajo |
| 3 | Bug real (categoría general): lógica de negocio ambigua | Alto |
| 4 | Inyección SQL/NoSQL | Alto |
| 5 | Exposición de stack trace en la respuesta | Medio |
| 6 | Condición de carrera (race condition) | Alto |
| 7 | Fuga de memoria / recursos no liberados | Medio-Alto |
| 8 | Credenciales hardcodeadas | Alto |
| 9 | Error de límites (off-by-one) | Bajo |
| 10 | Autenticación/autorización rota (IDOR) | Alto |
| 11 | Contexto detallado: regla de negocio real de `/nivel-cliente` | Alto |

## Cómo lo usa n8n (Módulo 4, sub-flujo de consulta)

En el nodo de Vector Store (Supabase) de n8n, apuntá a la tabla
`documents_bugs` y la función `match_documents_bugs`. Cuando llega un error nuevo,
n8n genera el embedding del error y llama a esa función — trae los N
chunks más parecidos, que se usan como contexto adicional en el prompt
final antes de mandarlo al agente (Módulo 5).
