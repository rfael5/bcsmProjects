import React, { useState, useEffect } from "react";
import CadastrarHoras from "./CadastrarHoras";

function TabelaFuncionarios() {

    const setores = ['Todos', 'Comercial', 'Qualidade', 'Producao Sal', 'Expedição']

    const [dadosFuncionario, setDadosFuncionario] = useState({});
    const [funcionarios, setFuncionarios] = useState([]);
    const [filtroFuncionarios, setFiltroFuncionarios] = useState([]);

    useEffect(() => {
        buscarFuncionarios()
    }, []);

    const buscarFuncionarios = async () => {
        await window.api.testInvoke().then((result) => {
            console.log(result)
            setFuncionarios(result)
            setFiltroFuncionarios(result)
        })
    }

    const setSelectedField = (value) => {
        console.log(value)
        if (value !== 'Todos'){
            let listaFiltrada = funcionarios.filter((func) => func.setor === value)
            setFiltroFuncionarios(listaFiltrada)
        }
        else{
            setFiltroFuncionarios(funcionarios)
        }
    }

    const administrarHoras = (value) => {
        setDadosFuncionario(value)
        console.log(value)
    }

    return (
        <div>
            <h3>Funcionários</h3>
            <select defaultValue='Todos' onChange={e => setSelectedField(e.target.value)}>
                {setores.map((setor) => (
                    <option key={setor} value={setor}>{setor}</option>
                ))}
            </select>
            <table>
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Setor</th>
                        <th>Data de Admissão</th>
                        <th>Administrar Horas</th>
                    </tr>
                </thead>
                <tbody>
                    {filtroFuncionarios.map((func) => (
                        <tr key={func.id}>
                            <td>{func.nomeFuncionario}</td>
                            <td>{func.setor}</td>
                            <td>{func.dataAdmissao}</td>
                            <td>
                                <button onClick={() => administrarHoras(func)}>Ver horas</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            <div>
                <CadastrarHoras funcionario={dadosFuncionario} />
            </div>
        </div>
    )
}

export default TabelaFuncionarios