const electron = require('electron');
// Módulo para controlar a vida a aplicação.
const app = electron.app;
// Módulo para criar uma janela de browser nativa.
const BrowserWindow = electron.BrowserWindow;

const path = require('path');
const url = require('url');
const sqlite3 = require('sqlite3').verbose();
const dbPath = '//192.168.1.42/publico/adm-horas-db/controle_ponto.db';

let mainWindow;

function createWindow() {
    // Criar a janela do browser.
    mainWindow = new BrowserWindow(
        {width: 800, 
         height: 600,
         webPreferences:{
            preload:path.join(__dirname, 'preload.js'),
            contextIsolation:true,
            enableRemoteModule: false,
            nodeIntegration:false
         }

        });
    console.log(__dirname)

    // e carregar o index.html da aplicação.
    const startUrl = process.env.ELECTRON_START_URL || url.format({
        pathname: path.join(__dirname, '/../build/index.html'),
        protocol: 'file:',
        slashes: true
    });
    mainWindow.loadURL(startUrl);

    // Abrir o DevTools.
    mainWindow.webContents.openDevTools();

    // mainWindow.webContents.send('database-data', rows)
    //             electron.ipcMain.on('dados-funcionarios', (args) => {
    //                 return rows
    //             })
    

    // Emitido quando a janela é fechada.
    mainWindow.on('closed', function () {
        // Desreferenciar o objeto da janela, geralmente irás armazenar as janelas
        // em um array caso a tua aplicação suporte várias janelas, esta é a altura
        // em que deves apagar o elemento correspondente.
        mainWindow = null
    })
}

// Este método será chamado quando o Electron tiver terminado
// a inicialização e estiver pronto para criar janelas de browser.
// Algumas APIs podem ser utilizadas apenas após este evento ocorrer.
app.on('ready', createWindow);

// Saír assim que todas as janelas estejam fechadas.
app.on('window-all-closed', function () {
    // No Sistema Operativo X é comum que as aplicações e a sua barra de menu
    // fiquem ativas até que o utilizador saia explicitamente com o Cmd + Q
    if (process.platform !== 'darwin') {
        app.quit()
    }
});

app.on('activate', function () {
    // No Sistema Operativo X é comum recriar uma janela na aplicação quando o
    // icon do dock é clicado e não existem outras janelas abertas.
    if (mainWindow === null) {
        createWindow()
    }
});

electron.ipcMain.on('post-horas', (event, data) => {
    cadastrarHoras(data)
    console.log("POST REALIZADO")
})

electron.ipcMain.on('get-funcionarios', () => {
    //const dbPath = path.join(__dirname, 'db/controle_ponto.db');
    let db = new sqlite3.Database(dbPath)
    let query = ('select * from funcionarios');
    db.all(query, [], (err, rows) => {
        if(err){
            throw err;
        }
        rows.forEach((row) => {
            console.log(row)
        })
    })
    db.close()
})

electron.ipcMain.handle('test-invoke', async (event) => {
    const result = await getFuncionarios()
    return result
})

const getFuncionarios = async () => {
    //const dbPath = path.join(__dirname, 'db/controle_ponto.db');
    let db = new sqlite3.Database(dbPath)
    let res =  new Promise((resolve, reject) => {
        let query = 'select * from funcionarios';
        db.all(query, [], (err, rows) => {
            if (err) {
                reject(err);
                return;
            }
            resolve(rows);
        });
        db.close();
    });
    return res
}

const cadastrarHoras = async (horas_funcionario) => {
    //const dbPath = path.join(__dirname, 'db/controle_ponto.db');
    let db = new sqlite3.Database(dbPath)
    try {
        db.run(`INSERT INTO ctrl_ponto (idFuncionario, horas, tipoHora, unidade, mes, nomeMes, ano) 
        VALUES (?, ?, ?, ?, ?, ?, ?)`, 
        [horas_funcionario.idFuncionario, horas_funcionario.horas, 
        horas_funcionario.tipoHora, horas_funcionario.unidade, 
        horas_funcionario.mes, horas_funcionario.nomeMes, 
        horas_funcionario.ano], function(err) {
            if (err){
                return console.log(err.message);
            }
            console.log(`A linha foi inserida com sucesso.`);
        });
        db.close()
    }catch(err){
        console.error(err)
    }
    
} 


// Podes incluir neste ficheiro o restante código específico do processo principal da tua
// aplicação. Também podes colocá-los em ficheiros diferentes e pedi-los aqui.