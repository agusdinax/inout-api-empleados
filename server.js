const express = require('express');
const bodyParser = require('body-parser');
const session = require('express-session');
const mysql = require('mysql');
const app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(session({
    secret: 'supersecretkey',
    resave: false,
    saveUninitialized: true
}));

const db = mysql.createConnection({
    host: '34.44.192.81',
    user: 'root',
    password: 'Test5678',
    database: 'dbINOClockinout'
});

db.connect(err => {
    if (err) throw err;
    console.log('Connected to database');
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    const query = 'SELECT * FROM users WHERE username = ? AND password = ?';
    
    db.query(query, [username, password], (err, results) => {
        if (err) throw err;
        if (results.length > 0) {
            req.session.username = username;
            res.redirect('/dashboard');
        } else {
            res.status(401).send({ error: 'Nombre de usuario o contraseña incorrectos' });
        }
    });
});

app.get('/dashboard', (req, res) => {
    if (!req.session.username) {
        return res.redirect('/');
    }
    
    // Aquí puedes agregar lógica para recuperar datos para la tabla
    const data = [
        { id: 1, name: 'Producto 1', price: 10.00 },
        { id: 2, name: 'Producto 2', price: 20.00 }
    ];
    
    res.json(data);
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
