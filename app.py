from flask import Flask, request, jsonify, abort # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from sqlalchemy.exc import OperationalError # type: ignore
from sqlalchemy import text # type: ignore
from datetime import datetime

app = Flask(__name__)

# Configurar la conexión a la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Test5678@127.0.0.1/inoutempleados'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definir el modelo para la tabla Empleados
class Empleado(db.Model):
    __tablename__ = 'tbl_Empleados'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    uidLlavero = db.Column(db.String(100), nullable=False)

class JornadaLaboral(db.Model):
    __tablename__ = 'tbl_jornadalaboral'
    id = db.Column(db.Integer, primary_key=True)
    id_empleado = db.Column(db.Integer, db.ForeignKey('tbl_Empleados.id'), nullable=False)
    nombre_empleado = db.Column(db.String(100), nullable=False)
    horario_entrada = db.Column(db.DateTime, nullable=False)
    horario_salida = db.Column(db.DateTime, nullable=False)
    cantidad_horas = db.Column(db.Integer(), nullable=False)

# Ruta para verificar la conexión a la base de datos
@app.route('/health', methods=['GET'])
def health_check():
    try:
        db.session.execute(text('SELECT 1'))  # Ejecutar una consulta simple para verificar la conexión
        return jsonify({'status': 'ok', 'message': 'Conexión a la base de datos exitosa'}), 200
    except OperationalError:
        return jsonify({'status': 'error', 'message': 'No se puede conectar a la base de datos'}), 500

# Ruta para obtener todos los empleados
@app.route('/empleados', methods=['GET'])
def get_empleados():
    empleados = Empleado.query.all()
    return jsonify([{
        'id': e.id,
        'nombre': e.nombre,
        'apellido': e.apellido,
        'uidLlavero': e.uidLlavero
    } for e in empleados])

# Ruta para obtener un empleado por ID
@app.route('/empleados/<int:id>', methods=['GET'])
def get_empleado_by_id(id):
    empleado = Empleado.query.get(id)
    if empleado is None:
        abort(404, description="Empleado no encontrado")
    return jsonify({
        'id': empleado.id,
        'nombre': empleado.nombre,
        'apellido': empleado.apellido,
        'uidLlavero': empleado.uidLlavero
    })

# Ruta para insertar una entrada de empleado
@app.route('/entrada_empleado', methods=['POST'])
def entrada_empleado():
    data = request.json

    # Validar que el JSON tenga los campos requeridos
    if 'id_empleado' not in data:
        return jsonify({'error': 'Falta el campo id_empleado en la solicitud'}), 400

    # Consultar el empleado para verificar que exista
    empleado = Empleado.query.get(data['id_empleado'])
    if empleado is None:
        return jsonify({'error': 'Empleado no encontrado'}), 404

    # Crear una nueva instancia de JornadaLaboral
    nueva_jornada = JornadaLaboral(
        id_empleado=data['id_empleado'],
        nombre_empleado=f"{empleado.nombre} {empleado.apellido}",
        horario_entrada=datetime.now()
    )

    # Insertar la nueva jornada laboral en la base de datos
    try:
        db.session.add(nueva_jornada)
        db.session.commit()
        return jsonify({
            'id': nueva_jornada.id,
            'id_empleado': nueva_jornada.id_empleado,
            'nombre_empleado': nueva_jornada.nombre_empleado,
            'horario_entrada': nueva_jornada.horario_entrada.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Ruta para obtener la última entrada de un empleado
@app.route('/ultima_entrada/<int:id_empleado>', methods=['GET'])
def ultima_entrada(id_empleado):
    try:
        # Consultar la última entrada de jornada laboral del empleado
        ultima_jornada = JornadaLaboral.query.filter_by(id_empleado=id_empleado).order_by(JornadaLaboral.horario_entrada.desc()).first()

        if ultima_jornada is None:
            return jsonify({'error': 'No se encontraron entradas para el empleado con el ID proporcionado'}), 404

        return jsonify({
            'id': ultima_jornada.id,
            'id_empleado': ultima_jornada.id_empleado,
            'nombre_empleado': ultima_jornada.nombre_empleado,
            'horario_entrada': ultima_jornada.horario_entrada.isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Ruta para registrar la salida de un empleado
@app.route('/salida_empleado', methods=['POST'])
def salida_empleado():
    data = request.json

    # Validar que el JSON tenga los campos necesarios
    if 'id_empleado' not in data or 'id_entrada' not in data:
        return jsonify({'error': 'Faltan campos en la solicitud'}), 400

    try:
        # Consultar la entrada de jornada laboral correspondiente
        jornada = JornadaLaboral.query.get(data['id_entrada'])
        if jornada is None or jornada.id_empleado != data['id_empleado']:
            return jsonify({'error': 'Entrada no encontrada o ID de empleado no coincide'}), 404

        # Actualizar el horario de salida
        jornada.horario_salida = datetime.now()

        # Calcular la cantidad de horas trabajadas
        if jornada.horario_entrada and jornada.horario_salida:
            tiempo_trabajado = jornada.horario_salida - jornada.horario_entrada
            cantidad_horas = int(tiempo_trabajado.total_seconds() // 3600)  # Convertir segundos a horas enteras
            jornada.cantidad_horas = cantidad_horas

        # Guardar los cambios en la base de datos
        db.session.commit()

        return jsonify({
            'nombre_empleado': jornada.nombre_empleado,
            'id_empleado': jornada.id_empleado,
            'id_salida': jornada.id,
            'cantidad_horas': jornada.cantidad_horas,
            'horario_entrada': jornada.horario_entrada.isoformat(),
            'horario_salida': jornada.horario_salida.isoformat()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
