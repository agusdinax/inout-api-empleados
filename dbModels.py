from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean # type: ignore
from sqlalchemy.orm import relationship # type: ignore

Base = declarative_base()

#se definen todos los database models
class User(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class Empleado(Base):
    __tablename__ = 'empleados'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    apellido = Column(String)
    uidLlavero = Column(String, unique=True)
    estado = Column(Boolean, default=True)

class JornadaLaboral(Base):
    __tablename__ = 'jornada'
    id = Column(Integer, primary_key=True)
    id_empleado = Column(Integer, ForeignKey('empleados.id'))
    nombre_empleado = Column(String)
    horario_entrada = Column(DateTime)
    horario_salida = Column(DateTime, nullable=True)
    cantidad_horas = Column(Float, nullable=True)

    empleado = relationship("Empleado", back_populates="jornadas")

Empleado.jornadas = relationship("JornadaLaboral", back_populates="empleado")
