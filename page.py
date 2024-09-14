from flask import Blueprint, request, jsonify, render_template, redirect, url_for # type: ignore
from models import db, JornadaLaboral

# Crear un Blueprint para las nuevas rutas
page_bp = Blueprint('page_bp', __name__)

@page_bp.route('/jornadas', methods=['GET'])
def get_jornadas():
    # Obtener 15 jornadas laborales ordenadas por horario_entrada
    jornadas = JornadaLaboral.query.order_by(JornadaLaboral.horario_entrada.desc()).limit(15).all()
    
    # Convertir las jornadas a un formato JSON
    jornadas_data = [{
        'id': jornada.id,
        'fecha': jornada.horario_entrada.strftime('%d-%m-%Y %H:%M'),
    } for jornada in jornadas]
    
    return jsonify({'jornadas': jornadas_data})

@page_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def update_jornada(id):
    jornada = JornadaLaboral.query.get(id)
    if not jornada:
        return redirect(url_for('page_bp.get_jornadas'))

    if request.method == 'POST':
        descripcion = request.form['descripcion']
        jornada.descripcion = descripcion
        db.session.commit()
        return redirect(url_for('page_bp.get_jornadas'))

    return render_template('update_jornada.html', jornada=jornada)
