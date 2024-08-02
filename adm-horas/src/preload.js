const { ipcRenderer, contextBridge } = require('electron');

contextBridge.exposeInMainWorld('api', {
  // Invoke Methods
  testInvoke: () => ipcRenderer.invoke('test-invoke').then((result) => {
    return result
  }),
  // Send Methods
  testSend: (args) => ipcRenderer.send('test-send', args).then((result) => {
    console.log(result)
  }),
  // Receive Methods
  //testReceive: (callback) => ipcRenderer.on('test-receive', (event, data) => { callback }),
  postHoras: (data) => ipcRenderer.send('post-horas', data),

  receive: (channel, func) => {
    const validChannels = ['database-data'];
    if (validChannels.includes(channel)){
        ipcRenderer.on(channel, (event, ...args) => func(...args));
    }
  },
  getFuncionarios: () => ipcRenderer.send('get-funcionarios', {}),

  dadosFuncionarios: (args) => ipcRenderer.invoke('dados-funcionarios', args)
});