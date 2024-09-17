import React, { useState, useEffect, createContext, useContext } from "react";
import CadastrarHoras from "./CadastrarHoras";
import HorasFuncionario from "./HorasFuncionario";

export const FContext = createContext({})

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
            setFuncionarios(result)
            setFiltroFuncionarios(result)
        })
    }

    const setSelectedField = (value) => {
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
    }

    const [attHorasMes, setAttHorasMes] = useState({})

    return (
        <div>
            <h3>Funcionários</h3>
            <select defaultValue='Todos' onChange={e => setSelectedField(e.target.value)}>
                {setores.map((setor) => (
                    <option key={setor} value={setor}>{setor}</option>
                ))}
            </select>
            <div className="d-flex justify-content-center mt-4">
                <table className="table  table-striped table-hover ">
                    <thead>
                        <tr>
                            <th style={{ width: '150px' }}>Nome</th>
                            <th style={{width: '150px'}}>Setor</th>
                            <th style={{width: '150px'}}>Data de Admissão</th>
                            <th>Administrar Horas</th>
                        </tr>
                    </thead>
                    <tbody>
                        {
                        filtroFuncionarios.map((func) => (
                            <tr key={func.id}>
                                <td style={{ width: '150px' }}>{func.nomeFuncionario}</td>
                                <td style={{width: '150px'}}>{func.setor}</td>
                                <td style={{width: '150px'}}>{func.dataAdmissao}</td>
                                <td style={{width: '150px'}}>
                                    <button className="btn btn-primary" onClick={() => administrarHoras(func)}>Adicionar horas</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            
            <FContext.Provider value={{attHorasMes, setAttHorasMes}}>
                <div className="row d-flex">
                    <div className="col-8">
                        <HorasFuncionario funcionario={dadosFuncionario} />
                    </div>
                    <div className="col-4">
                        <CadastrarHoras funcionario={dadosFuncionario} />
                    </div>
                </div>
            </FContext.Provider>

            
            
        </div>
    )
}

export default TabelaFuncionarios