# TP2 A - Desarrollo Cliente Servidor REST

## 1. Analisis de Flask basico

`app = Flask(__name__)` crea la aplicacion Flask. El parametro `__name__` le permite a Flask ubicar recursos del proyecto, como templates y archivos estaticos.

`@app.route("/")` registra una ruta HTTP. Cuando el cliente pide esa URL, Flask ejecuta la funcion decorada y devuelve su respuesta.

`jsonify()` transforma diccionarios o listas de Python en una respuesta JSON con el tipo de contenido correcto. Es la forma usual de responder desde una API REST.

`debug=True` activa el modo de desarrollo: muestra errores detallados y recarga el servidor al detectar cambios. No debe usarse en produccion.

## 2. API REST de sensores

La API REST se implementa con rutas para una coleccion de sensores:

- `GET /sensors`: lista sensores.
- `GET /sensors/<id>`: obtiene un sensor por identificador.
- `POST /sensors`: crea un sensor a partir de JSON.
- `PUT /sensors/<id>`: modifica un sensor existente.
- `DELETE /sensors/<id>`: elimina un sensor.

El archivo `Prueba_Flask_Routes_02.py` contiene una version en memoria. El archivo `sensor_editar_tabla_r1B_geo.py` extiende la idea usando SQLite para persistencia.

## 3. Manejo seguro de IDs

No conviene acceder a una lista con `sensors[id]`, porque eso confunde el identificador logico con la posicion interna de la lista. Si se borra un elemento, las posiciones cambian.

La solucion es buscar el sensor por el campo `id` y devolver `404` cuando no existe. Esto evita errores de indice y hace que la API tenga un comportamiento HTTP correcto.

## 4. GET vs POST en Flask

En una ruta GET, los parametros viajan en la URL y se leen con `request.args`. Es util para consultas, filtros y enlaces compartibles.

En una ruta POST, los datos viajan en el cuerpo de la solicitud y se leen con `request.form` o `request.get_json()`. Es mas adecuado para crear recursos, enviar formularios o mandar datos que no deben quedar visibles en la URL.

GET no deberia modificar estado del servidor. POST si puede crear datos o disparar acciones.

## 5. Persistencia en SQLite

La tabla `lectura_sensores` guarda lecturas con campos como `co2`, `temp`, `hum`, `fecha`, `lugar`, `altura`, `presion`, `presion_nm` y `temp_ext`.

En `sensor_editar_tabla_r1B_geo.py`, la funcion `create_table()` crea la tabla si no existe, `insertar_lectura()` guarda registros y `obtener_registros()` los consulta.

## 6. Simulacion de sensores

La funcion `simular_lectura()` genera valores aleatorios de CO2, temperatura y humedad. La ruta `POST /api/capturar` permite configurar:

- `cantidad`: numero de lecturas a generar.
- `intervalo`: segundos entre capturas.
- `lugar`: ubicacion descriptiva.
- `altura`: altura del sensor.

## 7. Clima externo

La integracion real con OpenWeather queda preparada mediante `OPENWEATHER_API_KEY`. Hasta crear la API key, el sistema usa un modo simulado para no bloquear el resto del TP.

Cuando se configure la variable de entorno, se podra usar `modo=auto` para intentar obtener datos reales por ciudad o por geolocalizacion IP.

## 8. Arquitectura Cliente Servidor REST

El servidor es la aplicacion Flask. Define endpoints, procesa solicitudes HTTP, consulta o modifica datos y devuelve respuestas JSON o HTML.

El cliente puede ser el navegador, un formulario HTML, `curl`, Postman o codigo JavaScript que consume la API con `fetch()`.

Es REST porque modela recursos, usa HTTP como protocolo de comunicacion y diferencia acciones mediante metodos como GET, POST, PUT y DELETE. Las respuestas JSON representan el estado de los recursos.

Elementos que se cumplen:

- Separacion cliente-servidor.
- Uso de HTTP.
- Uso de recursos identificados por URLs.
- Operaciones mediante metodos HTTP.
- Respuestas estructuradas en JSON.

Elementos que podrian mejorarse:

- Validacion mas estricta de datos.
- Autenticacion y autorizacion.
- Paginacion y filtros en todas las consultas.
- Manejo formal de versiones de API.

## 9. Comparacion con TP1

En TP1 se trabaja mas cerca del nivel de sockets. El cliente y el servidor intercambian mensajes usando conexiones TCP, UDP o raw sockets, y el protocolo de aplicacion debe definirse manualmente.

En TP2 se usa HTTP sobre TCP. Flask abstrae buena parte del manejo de sockets y permite concentrarse en rutas, metodos, JSON y persistencia.

TP1 ayuda a entender la comunicacion de bajo nivel. TP2 muestra una arquitectura de aplicacion web mas cercana a sistemas reales con APIs REST y bases de datos.

## 10. Cliente visual WebSocket

El repo ya incluye una base para WebSocket:

- `server_ws.js`: servidor WebSocket con Node.js y `ws`.
- `cliente.py`: cliente Flask que se conecta a un WebSocket.
- `Cliente_Servidor_Websockets_R2.ipynb`: notebook de referencia.

Esto cubre la parte de comunicacion en tiempo real, distinta del modelo REST porque mantiene una conexion abierta para enviar y recibir mensajes sin una solicitud HTTP nueva por cada intercambio.
