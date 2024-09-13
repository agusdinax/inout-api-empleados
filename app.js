const express = require('express');
const mysql = require('mysql2');
const bodyParser = require('body-parser');
const app = express();

// Configurar body-parser para analizar JSON en solicitudes
app.use(bodyParser.json());

// Configuración de la conexión a la base de datos MySQL
const db = mysql.createConnection({
    host: '34.44.192.81',
    user: 'clockinoutdb',
    password: 'Test5678',
    database: 'dbINOClockinout'
});

// Verificar la conexión a la base de datos
db.connect((err) => {
    if (err) {
        console.error('Error al conectar a la base de datos:', err);
    } else {
        console.log('Conectado a la base de datos');
    }
});

// Ruta para verificar el estado de la conexión
app.get('/health', (req, res) => {
    db.query('SELECT 1', (err, result) => {
        if (err) {
            res.status(500).json({ status: 'error', message: 'No se puede conectar a la base de datos' });
        } else {
            res.status(200).json({ status: 'ok', message: 'Conexión a la base de datos exitosa' });
        }
    });
});

// Ruta para obtener todos los empleados
app.get('/empleados', (req, res) => {
    db.query('SELECT * FROM empleados', (err, results) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        const empleados = results.map((empleado) => ({
            id: empleado.id,
            nombre: empleado.nombre,
            apellido: empleado.apellido,
            uidLlavero: empleado.uidLlavero
        }));
        res.status(200).json(empleados);
    });
});

// Ruta para obtener un empleado por uidLlavero
app.get('/empleados/:uidLlavero', (req, res) => {
    const { uidLlavero } = req.params;
    db.query('SELECT * FROM empleados WHERE uidLlavero = ?', [uidLlavero], (err, results) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (results.length === 0) {
            return res.status(404).json({ error: 'Empleado no encontrado' });
        }
        const empleado = results[0];
        res.status(200).json({
            id: empleado.id,
            nombre: empleado.nombre,
            apellido: empleado.apellido,
            uidLlavero: empleado.uidLlavero
        });
    });
});

// Ruta para insertar una entrada de empleado
app.post('/entrada_empleado', (req, res) => {
    const { id_empleado } = req.body;
    if (!id_empleado) {
        return res.status(400).json({ error: 'Falta el campo id_empleado en la solicitud' });
    }

    // Consultar si el empleado existe
    db.query('SELECT * FROM empleados WHERE id = ?', [id_empleado], (err, results) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (results.length === 0) {
            return res.status(404).json({ error: 'Empleado no encontrado' });
        }
        const empleado = results[0];

        const nombre_empleado = `${empleado.nombre} ${empleado.apellido}`;
        const horario_entrada = new Date();
        const query = `INSERT INTO jornada (id_empleado, nombre_empleado, horario_entrada, horario_salida, cantidad_horas) 
                       VALUES (?, ?, ?, ?, ?)`;
        db.query(query, [id_empleado, nombre_empleado, horario_entrada, horario_entrada, 0], (err, result) => {
            if (err) {
                return res.status(500).json({ error: err.message });
            }
            res.status(201).json({
                id: result.insertId,
                id_empleado,
                nombre_empleado,
                horario_entrada
            });
        });
    });
});

// Ruta para obtener la última entrada de un empleado
app.get('/ultima_entrada/:id_empleado', (req, res) => {
    const { id_empleado } = req.params;
    db.query('SELECT * FROM jornada WHERE id_empleado = ? ORDER BY horario_entrada DESC LIMIT 1', [id_empleado], (err, results) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (results.length === 0) {
            return res.status(404).json({ error: 'No se encontraron entradas para el empleado' });
        }
        const ultima_jornada = results[0];
        res.status(200).json({
            id: ultima_jornada.id,
            id_empleado: ultima_jornada.id_empleado,
            nombre_empleado: ultima_jornada.nombre_empleado,
            horario_entrada: ultima_jornada.horario_entrada
        });
    });
});

// Ruta para registrar la salida de un empleado
app.post('/salida_empleado', (req, res) => {
    const { id_empleado, id_entrada } = req.body;
    if (!id_empleado || !id_entrada) {
        return res.status(400).json({ error: 'Faltan campos en la solicitud' });
    }

    db.query('SELECT * FROM jornada WHERE id = ? AND id_empleado = ?', [id_entrada, id_empleado], (err, results) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (results.length === 0) {
            return res.status(404).json({ error: 'Entrada no encontrada o ID de empleado no coincide' });
        }

        const jornada = results[0];
        const horario_salida = new Date();
        const tiempo_trabajado = (horario_salida - new Date(jornada.horario_entrada)) / (1000 * 60 * 60); // En horas

        db.query('UPDATE jornada SET horario_salida = ?, cantidad_horas = ? WHERE id = ?', [horario_salida, tiempo_trabajado, id_entrada], (err) => {
            if (err) {
                return res.status(500).json({ error: err.message });
            }
            res.status(200).json({
                nombre_empleado: jornada.nombre_empleado,
                id_empleado,
                id_salida: id_entrada,
                cantidad_horas: tiempo_trabajado,
                horario_entrada: jornada.horario_entrada,
                horario_salida
            });
        });
    });
});

// Iniciar el servidor
app.listen(8080, () => {
    console.log('Servidor corriendo en http://localhost:8080');
});
