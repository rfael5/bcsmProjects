const path = require('path');
const sqlite3 = require('sqlite3').verbose();

const getFuncionarios = async () => {
    const dbPath = path.join(__dirname, 'controle_ponto.db');
    let db = new sqlite3.Database(dbPath)
    let query = ('select * from funcionarios');
    db.all(query, [], (err, rows) => {
        if(err){
            throw err;
        }
        rows.forEach((row) => {
            console.log(row)
        })
        let testando = 'ola'
        return testando
    })
    db.close()
}

module.exports = { getFuncionarios }
