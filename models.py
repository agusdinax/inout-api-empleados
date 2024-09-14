from flask_sqlalchemy import SQLAlchemy # type: ignore

db = SQLAlchemy()

# ------------------------- Defininicion del modelo de esquema de los datos de la base 
class Empleado(db.Model):
    __tablename__ = 'empleados'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    uidLlavero = db.Column(db.String(100), nullable=False)

class JornadaLaboral(db.Model):
    __tablename__ = 'jornada'
    id = db.Column(db.Integer, primary_key=True)
    id_empleado = db.Column(db.Integer, db.ForeignKey('empleados.id'), nullable=False)
    nombre_empleado = db.Column(db.String(100), nullable=False)
    horario_entrada = db.Column(db.DateTime, nullable=False)
    horario_salida = db.Column(db.DateTime, nullable=False)
    cantidad_horas = db.Column(db.Integer(), nullable=False)

class User(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
