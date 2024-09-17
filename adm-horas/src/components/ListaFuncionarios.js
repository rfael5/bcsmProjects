import React, { useState, useEffect } from 'react'

const ListaFuncionarios = () => {

    const setores = ['Todos', 'Comercial', 'Qualidade', 'Producao Sal', 'Expedição']

    const [funcionarios, setFuncionarios] = useState([]);
    const [filtroFuncionarios, setFiltroFuncionarios] = useState([]);
    const [horasMes, setHorasMes] = useState({})
    const [select, setSelect] = useState("")

    const buscarFuncionarios = async() => {
        if(select !== ""){
            const res = await window.api.buscarFuncionariosSetor(select)
            setFuncionarios(res)
        }    
    }

    const buscarHorasFuncionarios = async() => {
        if(select !== ""){
            const res = await window.api.buscarTotalHoras(select)
            setHorasMes(res)
        }
    }

    const criarObjFuncionarios = () => {
        let updatedFuncionarios = funcionarios.map((f) => {
            let horas = horasMes.filter(mes => f.idFuncionario === mes.idFuncionario)
            return {...f, horas}
        })
        setFiltroFuncionarios(updatedFuncionarios)
    }

    useEffect(() => {
        buscarFuncionarios()
        buscarHorasFuncionarios()
    }, [select])

    useEffect(() => {
        criarObjFuncionarios()
    }, [funcionarios, horasMes])

    const setSelectedField = (value) => {
        setSelect(value)
        console.log(filtroFuncionarios)
    }

    function millisecondsToTime(ms) {
        // Calculate hours, minutes, and seconds from milliseconds
        const hours = Math.floor(ms / (60 * 60 * 1000));
        const minutes = Math.floor((ms % (60 * 60 * 1000)) / (60 * 1000));
        const seconds = Math.floor((ms % (60 * 1000)) / 1000);
    
        // Format the values as "hh:mm:ss"
        const formattedHours = String(hours).padStart(2, '0');
        const formattedMinutes = String(minutes).padStart(2, '0');
        const formattedSeconds = String(seconds).padStart(2, '0');
    
        const totalHs = `${formattedHours}:${formattedMinutes}:${formattedSeconds}`;
        return totalHs
    }

    const calcularSaldoHoras = (funcionario, _mes) => {
        console.log(funcionario)
        const horasMes = funcionario.filter(mes => mes.mes === _mes)
        console.log(horasMes)
        const {horasPositivasMS, horasNegativasMS} = horasMes[0]
        let saldoFinalMS = horasPositivasMS - horasNegativasMS
        if(saldoFinalMS < 0){
            saldoFinalMS = saldoFinalMS * -1
            const saldoHoras = millisecondsToTime(saldoFinalMS)
            return `- ${saldoHoras}`
        }else{
            const saldoHoras = millisecondsToTime(saldoFinalMS)
            return saldoHoras
        }
    }

    return(
        <div>
            <h3>Funcionários</h3>
            <select defaultValue='Todos' onChange={e => setSelectedField(e.target.value)}>
                {setores.map((setor) => (
                    <option key={setor} value={setor}>{setor}</option>
                ))}
            </select>

            <div className="d-flex justify-content-center mt-4">
                <table className="table  table-striped table-hover ">
                    <tbody>
                        {
                        filtroFuncionarios.map((func) => (
                            <tr key={func.id}>
                                <td style={{ width: '150px' }}>{func.nomeFuncionario}</td>
                                <td style={{width: '150px'}}>{func.setor}</td>
                                <td>
                                    <tr className="d-flex flex-row">
                                        {func.horas?.map((mes) => (
                                            <div key={mes.idFuncionario} className="m-4">
                                                <div>{mes.mes}</div>
                                                <div>{millisecondsToTime(mes.horasPositivasMS)}</div>
                                                <div>{millisecondsToTime(mes.horasNegativasMS)}</div>
                                                <div>{calcularSaldoHoras(func.horas, mes.mes)}</div>
                                            </div>
                                            
                                        ))}
                                        
                                    </tr>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

export default ListaFuncionarios