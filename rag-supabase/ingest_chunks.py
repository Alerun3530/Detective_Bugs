# Estas líneas importan las herramientas que instalaste con pip
import os
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client

# Carga las credenciales desde el archivo .env
# Sin esto, las variables OPENAI_API_KEY etc. no existen en Python
load_dotenv()

# Crea el cliente de OpenAI usando tu API key
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Crea el cliente de Supabase usando tu URL y tu key
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# ─────────────────────────────────────────────
# CHUNKS — contexto del proyecto para "El Detective de Bugs"
#
# Van acá los 10 errores/vulnerabilidades más importantes que el agente
# debería poder reconocer. Los primeros 3 son los bugs reales plantados
# en el repo víctima (así el agente los reconoce por descripción, no solo
# leyendo el código en el momento). Los otros 7 son categorías generales
# de error/vulnerabilidad de software, para que el agente tenga contexto
# aunque el bug del día no sea exactamente uno de los 3 propios.
#
# Al final hay un chunk aparte, más detallado, con la lógica de negocio
# específica del endpoint /nivel-cliente — ese es el que alimenta el
# caso de alto riesgo que se espera que el agente escale.
# ─────────────────────────────────────────────
chunks = [

    {
        "content": """Bug: ReferenceError por variable mal escrita (typo).
Ejemplo real (repo-victima, endpoint GET /api/usuarios/:id/es-mayor-de-edad):
el código usa "usuarioo.edad" en vez de "usuario.edad" — la variable
"usuarioo" no existe en ningún lado, así que Node.js explota con
"ReferenceError: usuarioo is not defined" apenas se ejecuta esa línea.
Nivel de riesgo: Bajo. Es un error de tipeo puro, sin ambigüedad de
intención — el fix correcto es evidente con solo leer la línea.
Acción esperada del agente: diagnosticar la causa raíz (nombre de
variable incorrecto) y aplicar el fix directamente, sin escalar.""",
        "metadata": {
            "fuente": "repo-victima/src/usuarios.js",
            "seccion": "bug_typo_referencia_indefinida",
            "tipo_error": "ReferenceError",
            "dominio": "calidad_codigo",
            "gravedad": "bajo",
            "endpoint_afectado": "/api/usuarios/:id/es-mayor-de-edad"
        }
    },

    {
        "content": """Bug: falta de validación de entrada nula o vacía.
Ejemplo real (repo-victima, endpoint POST /api/usuarios): el código llama
".trim()" sobre "datos.nombre" y "datos.email" sin comprobar antes que
esos campos existan en el body de la request. Si el cliente manda un
POST sin "nombre" o sin "email", el resultado es
"TypeError: Cannot read properties of undefined (reading 'trim')" y el
servidor responde 500 en vez de un 400 controlado.
Nivel de riesgo: Bajo. Es un problema de falta de guard clause, no de
lógica de negocio — el fix es agregar una validación de campos
requeridos antes de procesar el body.
Acción esperada del agente: diagnosticar y aplicar el fix directamente
(validar presencia de campos, responder 400 con un mensaje claro).""",
        "metadata": {
            "fuente": "repo-victima/src/usuarios.js",
            "seccion": "bug_falta_validacion_input",
            "tipo_error": "TypeError",
            "dominio": "validacion_entrada",
            "gravedad": "bajo",
            "endpoint_afectado": "/api/usuarios"
        }
    },

    {
        "content": """Bug: lógica de negocio ambigua o contradictoria.
Categoría general: cuando una regla de negocio produce un resultado que
"funciona" técnicamente (no tira excepción) pero es cuestionable desde
el punto de vista del negocio, y no está claro si el comportamiento
actual es un error o una decisión intencional (por ejemplo, una regla de
compliance). Este tipo de caso NO se detecta por una excepción — hace
falta un chequeo de negocio específico o un reporte humano/QA para
notarlo.
Nivel de riesgo: Alto. Aplicar un fix sin confirmar la intención puede
introducir un problema peor que el original (por ejemplo, romper una
regla de compliance real).
Acción esperada del agente: diagnosticar con claridad cuál es el
comportamiento actual, cuál sería el esperado según el contexto, y
escalar a un humano para que decida — o, en la variante de "punto medio"
del proyecto, aplicar el fix igual pero marcar confianza baja y explicar
el riesgo en el resumen para el humano.""",
        "metadata": {
            "fuente": "conocimiento_general",
            "seccion": "bug_logica_negocio_ambigua",
            "tipo_error": "ninguno (200 OK con resultado cuestionable)",
            "dominio": "logica_de_negocio",
            "gravedad": "alto"
        }
    },

    {
        "content": """Vulnerabilidad: inyección SQL / NoSQL.
Ocurre cuando el input del usuario se concatena directamente en una
consulta a la base de datos en vez de usar parámetros preparados o un
ORM que escape los valores. Permite a un atacante alterar la consulta
para leer, modificar o borrar datos que no debería poder tocar.
Señal típica: código que arma un string de SQL con template literals o
concatenación usando datos del request (`SELECT * FROM usuarios WHERE
email = '${req.body.email}'`).
Nivel de riesgo: Alto (seguridad). Nunca se aplica un auto-fix sin
revisión humana cuando hay indicios de que el problema es de seguridad,
no solo de funcionalidad.
Acción esperada del agente: señalar el riesgo de seguridad explícitamente
y escalar, incluso si el fix (usar parámetros preparados) parece simple.""",
        "metadata": {
            "fuente": "conocimiento_general",
            "seccion": "vulnerabilidad_inyeccion_sql",
            "tipo_error": "inyección",
            "dominio": "seguridad",
            "gravedad": "alto"
        }
    },

    {
        "content": """Error: manejo de errores que expone información sensible.
Ocurre cuando un endpoint devuelve el stack trace completo, rutas del
sistema de archivos, o detalles internos de la base de datos directamente
en la respuesta HTTP al cliente, en vez de loguearlos internamente y
responder un mensaje genérico.
Señal típica: un middleware de errores que hace
`res.status(500).json({ error: err.message, stack: err.stack })` sin
diferenciar entre entorno de desarrollo y producción.
Nivel de riesgo: Medio (seguridad + buenas prácticas). Útil durante el
desarrollo (de hecho el repo-victima lo usa así a propósito, para que el
simulador de errores tenga un stack trace legible), pero no debería
llegar así a un entorno real de producción.
Acción esperada del agente: si el contexto es "producción", señalar el
riesgo y sugerir separar el log interno de la respuesta pública; si el
contexto es un entorno de desarrollo/demo, puede no ser un bug real.""",
        "metadata": {
            "fuente": "conocimiento_general",
            "seccion": "error_exposicion_stack_trace",
            "tipo_error": "configuración de manejo de errores",
            "dominio": "seguridad",
            "gravedad": "medio"
        }
    },

    {
        "content": """Bug: condición de carrera (race condition).
Ocurre cuando dos operaciones concurrentes leen y escriben el mismo
recurso sin ningún mecanismo de bloqueo o transacción, y el resultado
final depende del orden en que terminan de ejecutarse (que no es
determinístico). Es uno de los bugs más difíciles de reproducir porque
no falla siempre, solo bajo ciertos timings.
Señal típica: un patrón de "leer valor, calcular nuevo valor, escribir
valor" (read-modify-write) sobre un contador o saldo compartido, sin
usar una transacción atómica ni un lock.
Nivel de riesgo: Alto. Requiere entender el flujo completo de
concurrencia del sistema, no solo la línea donde se manifiesta el
síntoma.
Acción esperada del agente: diagnosticar el patrón de acceso concurrente
involucrado y escalar — este tipo de fix casi nunca es una sola línea.""",
        "metadata": {
            "fuente": "conocimiento_general",
            "seccion": "bug_condicion_de_carrera",
            "tipo_error": "concurrencia",
            "dominio": "calidad_codigo",
            "gravedad": "alto"
        }
    },

    {
        "content": """Bug: fuga de memoria / recursos no liberados.
Ocurre cuando el código abre conexiones (a la base de datos, a un socket,
a un archivo) o registra listeners de eventos, y nunca los cierra o
remueve. Con el tiempo, el proceso acumula memoria o handles abiertos
hasta degradar el rendimiento o crashear el servidor completo.
Señal típica: un `setInterval` o un listener de eventos agregado dentro
de una función que se llama repetidamente, sin un `clearInterval` o
`removeListener` correspondiente.
Nivel de riesgo: Medio-Alto, depende de la frecuencia con la que se
dispara el código afectado.
Acción esperada del agente: identificar el recurso que no se libera y
proponer el fix (agregar el cleanup correspondiente), marcando confianza
media si no está seguro de todos los lugares donde se usa ese recurso.""",
        "metadata": {
            "fuente": "conocimiento_general",
            "seccion": "bug_fuga_de_memoria",
            "tipo_error": "gestión de recursos",
            "dominio": "rendimiento",
            "gravedad": "medio"
        }
    },

    {
        "content": """Vulnerabilidad: credenciales o secretos hardcodeados.
Ocurre cuando una API key, contraseña, token o connection string queda
escrita directamente en el código fuente en vez de cargarse desde
variables de entorno o un gestor de secretos. Si el repo es público o se
comparte, el secreto queda expuesto para siempre en el historial de git,
incluso si se borra después.
Señal típica: un string literal que parece una clave (`sk-...`,
`postgres://usuario:password@...`) asignado directamente a una
constante en el código.
Nivel de riesgo: Alto (seguridad). Requiere no solo cambiar el código
sino además rotar la credencial expuesta, porque ya quedó comprometida.
Acción esperada del agente: nunca aplicar el fix solo — señalar el
hallazgo y escalar, porque rotar credenciales es una decisión que un
humano tiene que tomar y ejecutar.""",
        "metadata": {
            "fuente": "conocimiento_general",
            "seccion": "vulnerabilidad_credenciales_hardcodeadas",
            "tipo_error": "exposición de secretos",
            "dominio": "seguridad",
            "gravedad": "alto"
        }
    },

    {
        "content": """Bug: error de límites (off-by-one).
Ocurre cuando un loop o un acceso a un array usa `<=` en vez de `<` (o
viceversa), o arranca en el índice equivocado (0 vs 1), provocando que
se procese un elemento de más, uno de menos, o se acceda a un índice
fuera de rango.
Señal típica: `for (let i = 0; i <= array.length; i++)` — esa condición
hace que en la última vuelta se acceda a `array[array.length]`, que no
existe, y da `undefined` en vez de tirar un error visible inmediatamente.
Nivel de riesgo: Bajo, una vez identificado — pero puede ser difícil de
notar porque el síntoma (un dato faltante o un `undefined` silencioso)
aparece lejos de la línea que lo causa.
Acción esperada del agente: diagnosticar y aplicar el fix directamente,
es un error mecánico sin ambigüedad de intención.""",
        "metadata": {
            "fuente": "conocimiento_general",
            "seccion": "bug_off_by_one",
            "tipo_error": "error de límites",
            "dominio": "calidad_codigo",
            "gravedad": "bajo"
        }
    },

    {
        "content": """Vulnerabilidad: autenticación o autorización rota.
Ocurre cuando un endpoint que debería requerir un usuario autenticado
(o un rol específico) no chequea el token/sesión, o lo chequea pero no
valida que ese usuario tenga permiso sobre el recurso puntual que está
pidiendo (por ejemplo, `GET /api/usuarios/:id` sin validar que el `:id`
corresponda al usuario logueado, permitiendo ver datos de otra persona
solo cambiando el id en la URL — esto se llama IDOR, Insecure Direct
Object Reference).
Nivel de riesgo: Alto (seguridad). Es de los hallazgos más graves porque
compromete la confidencialidad de datos de otros usuarios.
Acción esperada del agente: nunca aplicar un fix de autenticación/
autorización sin supervisión humana — señalar el hallazgo con prioridad
alta y escalar de inmediato.""",
        "metadata": {
            "fuente": "conocimiento_general",
            "seccion": "vulnerabilidad_autenticacion_rota",
            "tipo_error": "control de acceso",
            "dominio": "seguridad",
            "gravedad": "alto"
        }
    },

    {
        "content": """Contexto del proyecto — lógica de negocio específica del endpoint
GET /api/usuarios/:id/nivel-cliente (repo-victima).
Regla implementada actualmente: un usuario obtiene nivel "vip" si tiene
10 o más compras Y es mayor o igual a 18 años. Si tiene 10 o más compras
pero es MENOR de 18 años, el nivel queda forzado a "regular" (no a
"vip", ni siquiera a "frecuente"). Si tiene entre 5 y 9 compras
(sin importar la edad), el nivel es "frecuente". En cualquier otro caso,
el nivel es "regular".
El propio código tiene un comentario TODO dejado por el equipo original,
sin resolver: "revisar con negocio si esto es correcto. Un cliente con
10+ compras claramente es de alto valor, ¿por qué lo bajamos a 'regular'
solo por la edad? ¿O es una regla de compliance que no podemos tocar?".
Esto es exactamente lo que hace que este caso sea de alto riesgo: no se
sabe si la restricción por edad es un bug de programación o una regla
legal/de compliance intencional (por ejemplo, restricciones para
menores en programas de fidelización con beneficios monetarios).
Caso de prueba precargado: usuario id 5 (Sofía Ramos), 16 años, 14
compras — cae en el caso conflictivo y hoy devuelve nivel "regular".
Se detecta con GET /api/monitoreo/anomalias, que chequea este patrón
puntual (compras >= 10 y edad < 18), no por una excepción.""",
        "metadata": {
            "fuente": "repo-victima/src/usuarios.js + src/monitoreo.js",
            "seccion": "contexto_logica_negocio_nivel_cliente",
            "dominio": "logica_de_negocio",
            "gravedad": "alto",
            "endpoint_afectado": "/api/usuarios/:id/nivel-cliente",
            "caso_de_prueba": "usuario_id_5"
        }
    },

]


# ─────────────────────────────────────────────
# FUNCIÓN: get_embedding
# Recibe un texto, lo manda a la API de OpenAI,
# y recibe de vuelta una lista de 1536 números
# que representan el "significado" de ese texto
# ─────────────────────────────────────────────
def get_embedding(text):
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",  # el modelo más eficiente y barato
        input=text
    )
    return response.data[0].embedding   # devuelve la lista de 1536 números

# ─────────────────────────────────────────────
# LOOP PRINCIPAL
# Recorre cada chunk, genera su embedding,
# y lo inserta en la tabla 'documents_bugs' de Supabase
# (esta es la colección de "Contexto del proyecto" del Módulo 4)
# ─────────────────────────────────────────────
print("Iniciando ingesta del contexto del proyecto...\n")

for i, chunk in enumerate(chunks):
    print(f"Procesando chunk {i+1} de {len(chunks)}: {chunk['metadata']['seccion']}")

    # 1. Genera el embedding del texto
    embedding = get_embedding(chunk["content"])

    # 2. Inserta en Supabase: texto + vector + metadata
    supabase.table("documents_bugs").insert({
        "content": chunk["content"],
        "embedding": embedding,
        "metadata": chunk["metadata"]
    }).execute()

    print("   Guardado correctamente\n")

print("Proceso completado. Tu contexto de proyecto está en Supabase listo para búsquedas.")
