# Arquitectura original restaurada

El archivo activo `/Users/diegosilva12/base-pdf/app.py` es una copia exacta del incluido en `Base.rar`. Se comprobó byte por byte contra el archivo extraído del RAR. La adaptación anterior de Ollama se conserva en un respaldo dentro de `originales/`.

## Ejecutar

Configurar `GOOGLE_API_KEY` en el archivo local `.env` y ejecutar:

```sh
cd /Users/diegosilva12/base-pdf
./iniciar.command
```

El lanzador únicamente carga las variables de `.env` y ejecuta el archivo original; no añade instrucciones de conversación ni modifica su cadena RAG. Si falta la clave, informa ese requisito antes de iniciar.

El original utiliza Gemini para las respuestas y los embeddings: `gemini-2.5-flash` y `gemini-embedding-2`. Los nombres están escritos en el programa. Una configuración de Ollama en un PDF o en `.env` no cambia esas clases ni modelos. La generación contra Gemini no se ha validado: no hay una clave configurada en este proyecto ni en el entorno actual.

## Depuración local con Ollama

Para la prueba temporal, abrir Ollama y ejecutar:

```sh
cd /Users/diegosilva12/base-pdf
./probar_ollama.command
```

El lanzador opcional ejecuta `debug_ollama/ejecutar.py`. Este adaptador verifica que `app.py` coincide con el original, conecta sus dos proveedores con Ollama únicamente dentro del proceso de prueba y ejecuta el archivo original mediante `runpy`. Al terminar, comprueba otra vez el SHA-256. No escribe cambios en `app.py`, en su prompt ni en el lanzador de Gemini.

Se conserva el flujo original: mismos PDF, división de 1000 caracteres con solapamiento de 200, FAISS, recuperación de cuatro fragmentos, plantilla de conversación, cadena LCEL y ciclo interactivo. No se incorpora la lógica conversacional de la adaptación anterior. La entrada procede de lo que la persona escriba en la terminal; el adaptador no fabrica sus respuestas.

La prueba usa los modelos locales ya instalados `qwen3:4b-instruct` y `embeddinggemma:300m`, mediante las API oficiales de [chat](https://docs.ollama.com/api/chat) y [embeddings](https://docs.ollama.com/api/embed). No requiere clave de Google. Los modelos y el servidor de Ollama deben estar disponibles antes de abrir la prueba.

Los archivos de prueba se guardan en `debug_ollama/runtime/`: su índice FAISS y un manifiesto de los PDF y del modelo de embeddings. Si cambian los documentos o el modelo, el adaptador respalda y regenera ese índice. Nunca carga ni escribe el índice de producción `base-pdf/faiss_index/`.

Los resultados sirven para revisar el recorrido documental y detectar errores de contenido o de recuperación. Al usar otros embeddings, los fragmentos recuperados pueden cambiar; las respuestas de Qwen tampoco demuestran cómo contestará Gemini 2.5 Flash. La validación final se realizará con Gemini cuando se configure su clave.

Para reproducir esta prueba en otra copia de la base, descomprimir `Depuracion_Ollama_Base_Original.zip` en la raíz del proyecto. Contiene `probar_ollama.command`, `debug_ollama/ejecutar.py` y una guía; no reemplaza `app.py`. Reutiliza las dependencias Python de la base. El lanzador `.command` es para macOS; el adaptador también puede ejecutarse con Python y `--project` apuntando a la carpeta de la base.

En otro equipo, usar la ruta de su propio proyecto en lugar de la ruta absoluta de este Mac. Los pesos de los modelos, el entorno virtual y los índices no están incluidos en el paquete de depuración.

## Comprobaciones realizadas con Ollama

- Se procesaron los tres PDF y se generaron 157 fragmentos en el índice de prueba. En la siguiente ejecución se reutilizó ese índice.
- La pregunta sobre la persona encargada y el correo de Primer Contacto devolvió los datos que aparecen en el PDF UDG.
- La petición de escribir código Python para una tarea de la UDG fue rechazada en esta prueba por ser ajena al contexto documental. Una prueba no garantiza el rechazo de cualquier consulta ajena.
- Ante el relato ambiguo de la captura, Ollama confundió D01 con un artículo e inventó la expansión «Comité Universitario de Tonalá». Son errores del modelo, no información documentada ni una ruta institucional válida. Esa respuesta no debe utilizarse como orientación.
- `app.py` permaneció idéntico al del RAR y no se creó ni alteró el índice de Gemini. Las respuestas de Gemini quedan pendientes de una prueba con su API.

## Documentación

Los tres PDF corregidos permanecen en `conocimientos/discriminacion/`: PERSONAL (19 páginas), UDG (25) y LEGAL (25). Se eliminaron los diálogos simulados y se conservaron las fuentes y criterios de orientación y seguimiento. El documento personal contiene resultados agregados de tres respuestas sustantivas; el registro de prueba se excluyó y no se entregan los testimonios individuales.

Para integrarlos en la base de otro compañero, copiar los tres PDF de `conocimientos/` del paquete documental a su carpeta de conocimientos y crear allí un índice con los embeddings de esa base.

El índice anterior de EmbeddingGemma/Ollama fue trasladado al respaldo para evitar cargarlo con Gemini. Cuando se ejecute el original con credenciales válidas, intentará crear un nuevo índice FAISS con los PDF disponibles. Si los PDF vuelven a cambiar, el original no detecta ese cambio: respaldar el índice y regenerarlo con el mismo modelo.

## Alcance de la versión original

El original no tiene historial entre preguntas ni los comandos `casos`, `retomar`, `--check`, `--index` o `--ask` de la adaptación anterior. Para continuar un caso, incluir en la pregunta los antecedentes relevantes. Las instrucciones y pruebas de aquella adaptación no describen esta versión.

Los PDF y `POLITICA_DISCRIMINACION.txt` contienen criterios propuestos para atender únicamente discriminación, responder al relato real y volver al tema. Son propuestas del autor, distintas de normas oficiales. FAISS solo recupera algunos fragmentos; incluir una política en un PDF no garantiza que llegue al modelo en cada consulta ni la convierte automáticamente en una instrucción del sistema. El rechazo estricto de temas ajenos y el seguimiento automático no se han validado con esta base.

El paquete `Documentacion_Discriminacion_Base_Fija.zip` contiene únicamente los tres PDF, la política y esta guía. La copia `app_original.py` entregada por separado es idéntica al archivo del RAR.

Se preservaron el programa anterior, su índice, configuración, lanzador y README dentro de `originales/restauracion_original_…/`. No se borraron los modelos de Ollama ni el entorno virtual.
