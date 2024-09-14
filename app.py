from flask import Flask, request, jsonify, abort, render_template, redirect, url_for, flash, session # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from sqlalchemy.exc import OperationalError # type: ignore
from sqlalchemy import text # type: ignore
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
import os
from dotenv import load_dotenv # type: ignore

load_dotenv()

app = Flask(__name__)
app.secret_key = 'secret_key'

# Configurar la conexión a la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@"
    f"{os.getenv('DATABASE_HOST')}/{os.getenv('DATABASE_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definir el modelo para la tabla Empleados
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

# Modelo de usuario
class User(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

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
@app.route('/empleados/<string:uidLlavero>', methods=['GET'])
def get_empleado_by_id(uidLlavero):
    empleado = Empleado.query.filter_by(uidLlavero=uidLlavero).first()
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
            'horario_entrada': nueva_jornada.horario_entrada.strftime("%Y-%m-%dT%H:%M")
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
            'horario_entrada': ultima_jornada.horario_entrada.strftime("%Y-%m-%dT%H:%M")
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
            cantidad_horas = int(tiempo_trabajado.total_seconds() // 3600)  # Horas enteras
            cantidad_minutos = int((tiempo_trabajado.total_seconds() % 3600) // 60)  # Minutos restantes
            jornada.cantidad_horas = cantidad_horas + cantidad_minutos / 60  # Total en horas con fracciones
        # Guardar los cambios en la base de datos
        db.session.commit()

        return jsonify({
            'nombre_empleado': jornada.nombre_empleado,
            'id_empleado': jornada.id_empleado,
            'id_salida': jornada.id,
            'cantidad_horas': jornada.cantidad_horas,
            'horario_entrada': jornada.horario_entrada.strftime("%Y-%m-%dT%H:%M"),
            'horario_salida': jornada.horario_salida.strftime("%Y-%m-%dT%H:%M")
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Ruta para registrar usuarios (opcional, si necesitas crear nuevos usuarios)
@app.route('/register', methods=['POST'])
def register():
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

         # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso')
            return {"message": "El nombre de usuario ya está en uso"}, 200
        
        if not username or not password:
            return {"message": "Nombre de usuario y contraseña son requeridos"}, 400

        # Generar un hash de la contraseña
        hashed_password = generate_password_hash(password)
        
        # Crear un nuevo usuario
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return {"message": "Usuario registrado correctamente"}, 201

    return {"message": "Solicitud debe ser en formato JSON"}, 400

# Ruta para la página de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Buscar usuario en la base de datos
        user = User.query.filter_by(username=username).first()
        
        # Imprimir la contraseña para depuración
        if user:
            print(f"Contraseña almacenada en la base de datos (hash): {user.password}")
        print(f"Contraseña ingresada por el usuario: {password}")

        # Validar usuario y contraseña
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  # Guardar usuario en la sesión
            flash('Inicio de sesión exitoso')
            return redirect(url_for('home'))
        else:
            flash('Usuario o contraseña incorrectos')
    
    return render_template('login.html')

# Ruta para la página principal (home)
@app.route('/home')
def home():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero')
        return redirect(url_for('login'))
    
    users = User.query.all()  # Obtenemos todos los usuarios para mostrar en la tabla
    return render_template('home.html', users=users)

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Eliminar la sesión del usuario
    flash('Has cerrado sesión correctamente')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
