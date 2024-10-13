from fastapi import FastAPI, HTTPException, Depends, Request, status # type: ignore
from fastapi.responses import JSONResponse # type: ignore # type: ignore
from fastapi.templating import Jinja2Templates # type: ignore
from sqlalchemy import text # type: ignore
from sqlalchemy.orm import Session # type: ignore
from dbModels import User, JornadaLaboral, Empleado
from sqlalchemy.exc import OperationalError # type: ignore
from datetime import datetime
from werkzeug.security import generate_password_hash # type: ignore
from pydantic import BaseModel # type: ignore
from flash import Flash
from dbConfig import get_db

app = FastAPI(
    title="API Control de empleados INOUT-Arduino",
    description="Esta es la api para el proyecto de INOUT de control de entrada y salida de empleados realizada con Arduino",
    version="1.0.0"
)
templates = Jinja2Templates(directory="templates")
flash = Flash()

def get_flashed_messages(request: Request):
    messages = request.session.get("messages", [])
    request.session["messages"] = []  
    return messages

# ------------------------- Ruta para verificar la conexión a la base de datos GET /health
@app.get("/health",
          summary="Verifica la conexión a la base de datos",
          description="Controla si se puede conectar a la base de datos.",
          response_description="200 STATUS OK si se conecta exitosamente.",
          responses={
              200: {
                  "description": "Conexión exitosa a la base de datos",
                  "content": {
                      "application/json": {
                          "example": {
                              "status": "ok",
                              "message": "Conexión a la base de datos exitosa"
                          }
                      }
                  }
              },
              500: {
                  "description": "Error al conectar a la base de datos",
                  "content": {
                      "application/json": {
                          "example": {
                              "detail": "No se puede conectar a la base de datos"
                          }
                      }
                  }
              }
          })
async def health_check(db: Session = Depends(get_db)):
    """
    Verifica la conexión a la base de datos.
    Este endpoint realiza una simple consulta a la base de datos para
    asegurarse de que está activa y accesible. Si la conexión es exitosa,
    devuelve un mensaje de estado. Si hay un problema con la conexión,
    lanza una excepción con un código de estado 500.
    - **Response**:
        - **200 OK**: Si se puede conectar a la base de datos.
        - **500 Internal Server Error**: Si no se puede conectar a la base de datos.
    - **Ejemplo de respuesta exitosa**:
    ```json
    {
        "status": "ok",
        "message": "Conexión a la base de datos exitosa"
    }
    ```
    - **Ejemplo de respuesta con error**:
    ```json
    {
        "detail": "No se puede conectar a la base de datos"
    }
    ```
    """
    try:
        db.execute(text('SELECT 1'))
        return {"status": "ok", "message": "Conexión a la base de datos exitosa"}
    except OperationalError:
        raise HTTPException(status_code=500, detail="No se puede conectar a la base de datos")

# ------------------------- Ruta para obtener todos los empleados GET /empleados
@app.get("/empleados",
          summary="Obtiene todos los empleados ingresados al sistema",
          description="Este endpoint retorna una lista de todos los empleados que han sido ingresados al sistema.",
          response_description="Lista de empleados.",
          responses={
              200: {
                  "description": "Consulta exitosa, retorna la lista de empleados.",
                  "content": {
                      "application/json": {
                          "example": [
                              {
                                  "id": 1,
                                  "nombre": "Juan",
                                  "apellido": "Pérez",
                                  "uidLlavero": "1234-5678",
                                  "estado": "activo"
                              },
                              {
                                  "id": 2,
                                  "nombre": "María",
                                  "apellido": "Gómez",
                                  "uidLlavero": "8765-4321",
                                  "estado": "inactivo"
                              }
                          ]
                      }
                  }
              },
              500: {
                  "description": "Error al obtener la lista de empleados.",
                  "content": {
                      "application/json": {
                          "example": {
                              "detail": "No se pudo obtener la lista de empleados"
                          }
                      }
                  }
              }
          })
async def get_empleados(db: Session = Depends(get_db)):
    """
    Obtiene todos los empleados ingresados al sistema.
    Este endpoint realiza una consulta a la base de datos para recuperar
    todos los registros de empleados. Si la consulta es exitosa,
    devuelve una lista de empleados. Si hay un problema, lanza
    una excepción con un código de estado 500.
    
    - **Response**:
        - **200 OK**: Si se obtiene correctamente la lista de empleados.
        - **500 Internal Server Error**: Si no se puede obtener la lista de empleados.
    
    - **Ejemplo de respuesta exitosa**:
    ```json
    [
        {
            "id": 1,
            "nombre": "Juan",
            "apellido": "Pérez",
            "uidLlavero": "1234-5678",
            "estado": "activo"
        },
        {
            "id": 2,
            "nombre": "María",
            "apellido": "Gómez",
            "uidLlavero": "8765-4321",
            "estado": "inactivo"
        }
    ]
    ```
    - **Ejemplo de respuesta con error**:
    ```json
    {
        "detail": "No se pudo obtener la lista de empleados"
    }
    ```
    """
    empleados = db.query(Empleado).all()
    return [
        {
            "id": e.id,
            "nombre": e.nombre,
            "apellido": e.apellido,
            "uidLlavero": e.uidLlavero,
            "estado": e.estado
        }
        for e in empleados
    ]

# ------------------------- Ruta para obtener un empleado por ID GET /empleados/{uidLlavero}
@app.get("/empleados/{uidLlavero}",
          summary="Se realiza una búsqueda por el empleado enviando el UIDLlavero",
          description="Este endpoint permite obtener los detalles de un empleado específico utilizando su UIDLlavero.",
          response_description="Detalles del empleado solicitado.",
          responses={
              200: {
                  "description": "Consulta exitosa, retorna los detalles del empleado.",
                  "content": {
                      "application/json": {
                          "example": {
                              "id": 1,
                              "nombre": "Juan",
                              "apellido": "Pérez",
                              "uidLlavero": "1234-5678",
                              "estado": "activo"
                          }
                      }
                  }
              },
              404: {
                  "description": "Empleado no encontrado.",
                  "content": {
                      "application/json": {
                          "example": {
                              "detail": "Empleado no encontrado"
                          }
                      }
                  }
              }
          })
async def get_empleado_by_id(uidLlavero: str, db: Session = Depends(get_db)):
    """
    Obtiene los detalles de un empleado específico utilizando su UIDLlavero.
    
    Este endpoint realiza una consulta a la base de datos para buscar un empleado
    basado en su UIDLlavero. Si el empleado se encuentra, se devuelve su información.
    Si no se encuentra, se lanza una excepción con un código de estado 404.

    - **Path Parameters**:
        - **uidLlavero** (str): El UIDLlavero del empleado que se desea obtener.

    - **Response**:
        - **200 OK**: Si se encuentra correctamente el empleado, retorna sus detalles.
        - **404 Not Found**: Si no se encuentra un empleado con el UIDLlavero proporcionado.

    - **Ejemplo de respuesta exitosa**:
    ```json
    {
        "id": 1,
        "nombre": "Juan",
        "apellido": "Pérez",
        "uidLlavero": "1234-5678",
        "estado": "activo"
    }
    ```

    - **Ejemplo de respuesta con error**:
    ```json
    {
        "detail": "Empleado no encontrado"
    }
    ```
    """
    empleado = db.query(Empleado).filter_by(uidLlavero=uidLlavero).first()
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return {
        "id": empleado.id,
        "nombre": empleado.nombre,
        "apellido": empleado.apellido,
        "uidLlavero": empleado.uidLlavero,
        "estado": empleado.estado
    }


# ------------------------- Ruta para insertar una entrada de empleado POST /entrada_empleado
@app.post(
    "/entrada_empleado",
    summary="Se realiza una entrada del empleado a una jornada laboral",
    description="Este endpoint permite registrar la entrada de un empleado a una jornada laboral. "
                "El usuario debe proporcionar el ID del empleado en el cuerpo de la solicitud. "
                "Si el empleado se encuentra y no hay errores, se registrará su entrada.",
    response_description="Detalles de la jornada laboral registrada.",
    responses={
        200: {
            "description": "Entrada registrada exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "id_empleado": 1,
                        "nombre_empleado": "Juan Pérez",
                        "horario_entrada": "2024-10-13T09:00",
                        "estado": True
                    }
                }
            }
        },
        400: {
            "description": "Falta el campo id_empleado en la solicitud.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Falta el campo id_empleado en la solicitud"
                    }
                }
            }
        },
        404: {
            "description": "Empleado no encontrado.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Empleado no encontrado"
                    }
                }
            }
        },
        500: {
            "description": "Error al registrar la entrada del empleado.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error al registrar entrada del empleado: [mensaje de error]"
                    }
                }
            }
        }
    }
)
async def entrada_empleado(data: dict, db: Session = Depends(get_db)):
    """
    Registra la entrada de un empleado a una jornada laboral.

    Este endpoint realiza las siguientes validaciones:
    1. Verifica que el campo `id_empleado` esté presente en los datos de la solicitud.
    2. Busca al empleado en la base de datos utilizando su ID.
    3. Si el empleado no se encuentra, lanza una excepción 404.
    4. Cambia el estado del empleado a `True`, indicando que está activo.
    5. Crea un nuevo registro de `JornadaLaboral` con la hora de entrada actual.
    6. Si se registra la entrada con éxito, devuelve los detalles de la jornada laboral.

    - **Request Body**:
        - **id_empleado** (int): El ID del empleado cuya entrada se desea registrar.

    - **Response**:
        - **200 OK**: Si se registra la entrada correctamente.
        - **400 Bad Request**: Si falta el campo `id_empleado` en la solicitud.
        - **404 Not Found**: Si no se encuentra el empleado con el ID proporcionado.
        - **500 Internal Server Error**: Si ocurre un error al intentar registrar la entrada.

    - **Ejemplo de solicitud**:
    ```json
    {
        "id_empleado": 1
    }
    ```

    - **Ejemplo de respuesta exitosa**:
    ```json
    {
        "id": 1,
        "id_empleado": 1,
        "nombre_empleado": "Juan Pérez",
        "horario_entrada": "2024-10-13T09:00",
        "estado": true
    }
    ```

    - **Ejemplo de respuesta con error (400)**:
    ```json
    {
        "detail": "Falta el campo id_empleado en la solicitud"
    }
    ```

    - **Ejemplo de respuesta con error (404)**:
    ```json
    {
        "detail": "Empleado no encontrado"
    }
    ```

    - **Ejemplo de respuesta con error (500)**:
    ```json
    {
        "detail": "Error al registrar entrada del empleado: [mensaje de error]"
    }
    """
    if "id_empleado" not in data:
        raise HTTPException(status_code=400, detail="Falta el campo id_empleado en la solicitud")

    empleado = db.query(Empleado).get(data["id_empleado"])
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    # Set employee state to True
    empleado.estado = True

    nueva_jornada = JornadaLaboral(
        id_empleado=data["id_empleado"],
        nombre_empleado=f"{empleado.nombre} {empleado.apellido}",
        horario_entrada=datetime.now()
    )

    try:
        db.add(nueva_jornada)
        db.commit()
        return {
            "id": nueva_jornada.id,
            "id_empleado": nueva_jornada.id_empleado,
            "nombre_empleado": nueva_jornada.nombre_empleado,
            "horario_entrada": nueva_jornada.horario_entrada.strftime("%Y-%m-%dT%H:%M"),
            "estado": empleado.estado
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al registrar entrada del empleado: " + str(e))

# -------------------------Ruta para obtener la última entrada de un empleado GET /ultima_entrada/{id_empleado}
class UltimaEntradaResponse(BaseModel):
    id: int
    id_empleado: int
    nombre_empleado: str
    horario_entrada: str
    estado: bool  

@app.get(
    "/ultima_entrada/{id_empleado}",
    response_model=UltimaEntradaResponse,
    summary="Se obtiene información sobre la última entrada del empleado",
    description="Este endpoint permite obtener la última entrada registrada de un empleado en la base de datos. "
                "Se busca la jornada laboral más reciente para el empleado especificado utilizando su ID.",
    responses={
        200: {
            "description": "Última entrada obtenida exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "id_empleado": 1,
                        "nombre_empleado": "Juan Pérez",
                        "horario_entrada": "2024-10-13T09:00",
                        "estado": True
                    }
                }
            }
        },
        404: {
            "description": "No se encontraron entradas para el empleado o empleado no encontrado.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No se encontraron entradas para el empleado con el ID proporcionado"
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor al procesar la solicitud.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "[mensaje de error]"
                    }
                }
            }
        }
    }
)
async def ultima_entrada(id_empleado: int, db: Session = Depends(get_db)):
    """
    Obtiene la información sobre la última entrada de un empleado.

    Este endpoint realiza las siguientes acciones:
    1. Busca la última jornada laboral registrada para el empleado usando su ID.
    2. Si no se encuentra ninguna entrada, lanza una excepción 404.
    3. Si se encuentra la entrada, busca al empleado correspondiente.
    4. Si el empleado no se encuentra, lanza una excepción 404.
    5. Devuelve un objeto `UltimaEntradaResponse` con la información de la última entrada.

    - **Path Parameters**:
        - **id_empleado** (int): El ID del empleado cuya última entrada se desea obtener.

    - **Response**:
        - **200 OK**: Si se encuentra correctamente la última entrada del empleado.
        - **404 Not Found**: Si no se encuentra la entrada o el empleado.
        - **500 Internal Server Error**: Si ocurre un error al procesar la solicitud.

    - **Ejemplo de solicitud**:
    ```http
    GET /ultima_entrada/1
    ```

    - **Ejemplo de respuesta exitosa**:
    ```json
    {
        "id": 1,
        "id_empleado": 1,
        "nombre_empleado": "Juan Pérez",
        "horario_entrada": "2024-10-13T09:00",
        "estado": true
    }
    ```

    - **Ejemplo de respuesta con error (404)**:
    ```json
    {
        "detail": "No se encontraron entradas para el empleado con el ID proporcionado"
    }
    ```

    - **Ejemplo de respuesta con error (500)**:
    ```json
    {
        "detail": "Error al procesar la solicitud: [mensaje de error]"
    }
    """
    try:
        ultima_jornada = db.query(JornadaLaboral).filter_by(id_empleado=id_empleado).order_by(JornadaLaboral.horario_entrada.desc()).first()

        if ultima_jornada is None:
            raise HTTPException(status_code=404, detail="No se encontraron entradas para el empleado con el ID proporcionado")

        empleado = db.query(Empleado).filter_by(id=ultima_jornada.id_empleado).first()
        if empleado is None:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        return UltimaEntradaResponse(
            id=ultima_jornada.id,
            id_empleado=ultima_jornada.id_empleado,
            nombre_empleado=ultima_jornada.nombre_empleado,
            horario_entrada=ultima_jornada.horario_entrada.strftime("%Y-%m-%dT%H:%M"),
            estado=empleado.estado
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------Ruta para insertar una salida de empleado POST /salida_empleado
class SalidaEmpleado(BaseModel):
    id_empleado: int
    id_entrada: int

@app.post(
    "/salida_empleado",
    summary="Se realiza una salida del empleado a una jornada laboral",
    description="Este endpoint permite registrar la salida de un empleado de su jornada laboral. "
                "Se necesita proporcionar el ID del empleado y el ID de la entrada correspondiente.",
    responses={
        200: {
            "description": "Salida registrada exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "nombre_empleado": "Juan Pérez",
                        "id_empleado": 1,
                        "id_salida": 1,
                        "cantidad_horas": 8.0,
                        "horario_entrada": "2024-10-13T09:00",
                        "horario_salida": "2024-10-13T17:00",
                        "estado": False
                    }
                }
            }
        },
        404: {
            "description": "Entrada no encontrada o ID de empleado no coincide.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Entrada no encontrada o ID de empleado no coincide"
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor al procesar la solicitud.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error al registrar salida del empleado: [mensaje de error]"
                    }
                }
            }
        }
    }
)
async def salida_empleado(data: SalidaEmpleado, db: Session = Depends(get_db)):
    """
    Registra la salida de un empleado de su jornada laboral.

    Este endpoint realiza las siguientes acciones:
    1. Busca la jornada laboral correspondiente al ID de entrada proporcionado.
    2. Verifica que la jornada existe y que el ID del empleado coincide.
    3. Actualiza la hora de salida y calcula las horas trabajadas.
    4. Cambia el estado del empleado a inactivo (False).
    5. Registra los cambios en la base de datos.

    - **Request Body**:
        - **id_empleado** (int): ID del empleado que está registrando su salida.
        - **id_entrada** (int): ID de la entrada correspondiente a la jornada laboral.

    - **Response**:
        - **200 OK**: Si se registra correctamente la salida del empleado.
        - **404 Not Found**: Si la entrada no se encuentra o el ID de empleado no coincide.
        - **500 Internal Server Error**: Si ocurre un error al procesar la solicitud.

    - **Ejemplo de solicitud**:
    ```http
    POST /salida_empleado
    Content-Type: application/json

    {
        "id_empleado": 1,
        "id_entrada": 1
    }
    ```

    - **Ejemplo de respuesta exitosa**:
    ```json
    {
        "nombre_empleado": "Juan Pérez",
        "id_empleado": 1,
        "id_salida": 1,
        "cantidad_horas": 8.0,
        "horario_entrada": "2024-10-13T09:00",
        "horario_salida": "2024-10-13T17:00",
        "estado": false
    }
    ```

    - **Ejemplo de respuesta con error (404)**:
    ```json
    {
        "detail": "Entrada no encontrada o ID de empleado no coincide"
    }
    ```

    - **Ejemplo de respuesta con error (500)**:
    ```json
    {
        "detail": "Error al registrar salida del empleado: [mensaje de error]"
    }
    """
    try:
        jornada = db.query(JornadaLaboral).get(data.id_entrada)
        if jornada is None or jornada.id_empleado != data.id_empleado:
            raise HTTPException(status_code=404, detail="Entrada no encontrada o ID de empleado no coincide")

        # Update exit time
        jornada.horario_salida = datetime.now()

        # Calculate hours worked
        if jornada.horario_entrada and jornada.horario_salida:
            tiempo_trabajado = jornada.horario_salida - jornada.horario_entrada
            jornada.cantidad_horas = tiempo_trabajado.total_seconds() / 3600

        empleado = db.query(Empleado).get(data.id_empleado)
        if empleado is not None:
            empleado.estado = False  # Cambiar estado a false al registrar salida

        db.commit()

        return {
            'nombre_empleado': jornada.nombre_empleado,
            'id_empleado': jornada.id_empleado,
            'id_salida': jornada.id,
            'cantidad_horas': jornada.cantidad_horas,
            'horario_entrada': jornada.horario_entrada.strftime("%Y-%m-%dT%H:%M"),
            'horario_salida': jornada.horario_salida.strftime("%Y-%m-%dT%H:%M"),
            'estado': empleado.estado
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al registrar salida del empleado: " + str(e))

# -------------------------Ruta para registrar usuarios POST /register
class RegisterUser(BaseModel):
    username: str
    password: str

@app.post(
    "/register",
    summary="Se realiza el registro de un nuevo usuario a la web",
    description="Este endpoint permite registrar un nuevo usuario en la aplicación. "
                "Se requiere que se proporcionen un nombre de usuario y una contraseña.",
    responses={
        201: {
            "description": "Usuario registrado correctamente.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Usuario registrado correctamente"
                    }
                }
            }
        },
        400: {
            "description": "Faltan datos requeridos.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Nombre de usuario y contraseña son requeridos"
                    }
                }
            }
        },
        200: {
            "description": "El nombre de usuario ya está en uso.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "El nombre de usuario ya está en uso"
                    }
                }
            }
        }
    }
)
async def register(data: RegisterUser, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en la aplicación.

    Este endpoint realiza las siguientes acciones:
    1. Verifica que se proporcionen un nombre de usuario y una contraseña.
    2. Comprueba si el nombre de usuario ya está en uso.
    3. Si el nombre de usuario está disponible, genera un hash de la contraseña.
    4. Crea un nuevo usuario y lo guarda en la base de datos.

    - **Request Body**:
        - **username** (str): Nombre de usuario del nuevo usuario.
        - **password** (str): Contraseña del nuevo usuario.

    - **Response**:
        - **201 Created**: Si el usuario se registra correctamente.
        - **400 Bad Request**: Si faltan datos requeridos.
        - **200 OK**: Si el nombre de usuario ya está en uso.

    - **Ejemplo de solicitud**:
    ```http
    POST /register
    Content-Type: application/json

    {
        "username": "nuevo_usuario",
        "password": "contraseña_segura"
    }
    ```

    - **Ejemplo de respuesta exitosa (201)**:
    ```json
    {
        "message": "Usuario registrado correctamente"
    }
    ```

    - **Ejemplo de respuesta con error (400)**:
    ```json
    {
        "detail": "Nombre de usuario y contraseña son requeridos"
    }
    ```

    - **Ejemplo de respuesta con error (200)**:
    ```json
    {
        "message": "El nombre de usuario ya está en uso"
    }
    """
    username = data.username
    password = data.password

    if not username or not password:
        raise HTTPException(status_code=400, detail="Nombre de usuario y contraseña son requeridos")

    if db.query(User).filter_by(username=username).first():
        return JSONResponse(content={"message": "El nombre de usuario ya está en uso"}, status_code=status.HTTP_200_OK)

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()
    return JSONResponse(content={"message": "Usuario registrado correctamente"}, status_code=status.HTTP_201_CREATED)