const mysql = require('mysql');

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

module.exports = db;
