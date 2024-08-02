import logo from './logo.svg';
import './App.css';
import React, { useEffect } from 'react';
import TabelaFuncionarios from './components/TabelaFuncionarios';
//import { getFuncionarios } from './db/sqlservice';

function App() {
  const teste = async () => {
    await window.api.testInvoke().then((result) => {
      console.log(result)
    });
  }

  return (
    <div className="App">
      <TabelaFuncionarios />
    </div>
  );
}

export default App;
