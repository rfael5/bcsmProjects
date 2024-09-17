import React, { useState, useEffect, useContext } from "react";
import {FContext} from './TabelaFuncionarios'


const HorasFuncionario = ({funcionario}) => {

    const [horasMes, setHorasMes] = useState({})

    const {attHorasMes, setAttHorasMes} = useContext(FContext)

    const buscarHorasFuncionario = async() => {
        if(funcionario.idFuncionario){
            await window.api.buscarHorasFuncionario(funcionario.idFuncionario).then(
                (result) => {
                    setHorasMes(result)
                })
            
        }else{
            return
        }
    }

    const calcularSaldoHoras = (funcionario) => {
        const {horasPositivasMS, horasNegativasMS} = funcionario
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

    useEffect(() => {
        buscarHorasFuncionario()
        console.log(horasMes)
    }, [funcionario.idFuncionario, attHorasMes])

    function convertToMiliseconds(strTime){

        const [hours, minutes, seconds] = strTime.split(':').map(Number);

        const hoursInMs = hours * 60 * 60 * 1000;
        const minutesInMs = minutes * 60 * 1000;
        const secondsInMs = seconds * 1000;

        const totalMs = hoursInMs + minutesInMs + secondsInMs;
        return totalMs
        //millisecondsToTime(totalMs)
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

    function teste(){
        const hour1 = convertToMiliseconds("01:20:18")
        const hour2 = convertToMiliseconds("02:35:02")
        const res = hour1 + hour2
        console.log(res)
        const finalHour = millisecondsToTime(res)
        console.log(finalHour)
    }

    const definirNomeMes = (num_mes) => {
        const dataObj = new Date()
        dataObj.setMonth(num_mes - 1)
        const nomeMes = dataObj.toLocaleString("pt-BR", {month:"long"})
        return nomeMes.charAt(0).toUpperCase() + nomeMes.slice(1);
    } 

    if(Object.keys(funcionario).length > 0){
        return (
            <div>
                <h3>Horas {funcionario.nomeFuncionario}</h3>
    
                <div className="d-flex">
                    <table className="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th>Mês</th>
                                <th>Horas positivas</th>
                                <th>Horas negativas</th>
                                <th>Saldo total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {horasMes.length > 0 &&
                                horasMes.map((mes) => (
                                    <tr key={mes.id}>
                                        <td>{mes.ano} | {definirNomeMes(mes.mes)}</td>
                                        <td className="me-3">{millisecondsToTime(mes.horasPositivasMS)}</td>
                                        <td>{millisecondsToTime(mes.horasNegativasMS)}</td>
                                        <td>{calcularSaldoHoras(mes)}</td>
                                    </tr>
                                ))
                            }
                        </tbody>
                    </table>
                </div>
            </div>
        )
    }
    return(<div></div>)
}

export default HorasFuncionario