import React, { useState, useEffect, createContext, useContext, useRef } from "react";
import InputMask from 'react-input-mask';
import { Modal, Button } from 'react-bootstrap';
import {FContext} from './TabelaFuncionarios'



const CadastrarHoras = ({funcionario}) =>{

    const style = {
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: 400,
        bgcolor: 'background.paper',
        border: '2px solid #000',
        boxShadow: 24,
        p: 4,
      };

    const [currentMonth, setCurrentMonth] = useState(() => defineCurrentMonth())
    const [currentYear, setCurrentYear] = useState(() => new Date().getFullYear())
    const {attHorasMes, setAttHorasMes} = useContext(FContext)

    function defineCurrentMonth() {
        let date = new Date()
        let _currentMonth = date.getMonth() + 1
        return _currentMonth
    }

    useEffect(() => {
        formData.idFuncionario = funcionario.idFuncionario
    }, [funcionario.idFuncionario])


    const meses = [
        { numero: 1, nome: 'Janeiro' },
        { numero: 2, nome: 'Fevereiro' },
        { numero: 3, nome: 'Março' },
        { numero: 4, nome: 'Abril' },
        { numero: 5, nome: 'Maio' },
        { numero: 6, nome: 'Junho' },
        { numero: 7, nome: 'Julho' },
        { numero: 8, nome: 'Agosto' },
        { numero: 9, nome: 'Setembro' },
        { numero: 10, nome: 'Outubro' },
        { numero: 11, nome: 'Novembro' },
        { numero: 12, nome: 'Dezembro' }
    ];

    const hp_ref = useRef()
    const hn_ref = useRef()

    const [formData, setFormData] = useState({
        idFuncionario: funcionario.idFuncionario,
        horasPositivas:'',
        horasPositivasMS:'',
        horasNegativas:'',
        horasNegativasMS: '',
        mes: currentMonth.toString(),
        ano: currentYear.toString()
    })

    const selectMonth = (value) => {
        formData.mes = value
        let nomeMes = meses.filter((mes) => mes.numero === Number(value))
        formData.nomeMes = nomeMes[0].nome
    }

    const handleChange = (e) => {
        const {name, value} = e.target;
        setFormData({
            ...formData,
            [name]:value
        })
    }

    function isNullOrEmpty(value) {
        return value === null || value === undefined || value === '';
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        if(error.horasPositivas == null && error.horasNegativas == null){
                formData.horasPositivasMS = await convertToMilliseconds(formData.horasPositivas)
                formData.horasNegativasMS = await convertToMilliseconds(formData.horasNegativas)
                await window.api.postHoras(formData)
                const horasAtualizadas = await window.api.buscarHorasFuncionario(funcionario.idFuncionario)
                setAttHorasMes(horasAtualizadas)
                mostrarModal("success")
                hp_ref.current.value = ""
                hn_ref.current.value = ""
        }
        else{
            console.log("Formato de horas inválido. Verifique se você digitou as horas nos campos corretamente.")
            mostrarModal("erro")
        }
        
    }

    const [time, setTime] = useState('');
    const [error, setError] = useState({
        horasPositivas: null,
        horasNegativas: null
    });

    const handleTimeInput = async (event) => {
        const {inputValue} = event.target.value;
        const {name, value} = event.target;
        const pattern = /^(\d{2}):(\d{2}):(\d{2})$/;
        const msgErro = "Formato de horas invalido. Verifique se você preencheu os campos corretamente"

        formData[name] = value

        if (pattern.test(value)) {
            const [hours, minutes, seconds] = value.split(':').map(Number);

            if (hours >= 0 && minutes >= 0 && minutes < 60 && seconds >= 0 && seconds < 60){
                setTime(inputValue);
                //error[name] = null;
                if(name === 'horasPositivas'){
                    error.horasPositivas = null
                }else if(name == 'horasNegativas'){
                    error.horasNegativas = null
                }
                //formData.horasPositivas = value
                setFormData({
                    ...formData,
                    [name]:value
                })
                
            }else {
                if(name === 'horasPositivas'){
                    error.horasPositivas = msgErro
                }else if(name === 'horasNegativas'){
                    error.horasNegativas = msgErro
                }
            }
        }else {
            error[name] = msgErro;
       }
    }

    function convertToMilliseconds(strTime){

        const [hours, minutes, seconds] = strTime.split(':').map(Number);

        const hoursInMs = hours * 60 * 60 * 1000;
        const minutesInMs = minutes * 60 * 1000;
        const secondsInMs = seconds * 1000;

        const totalMs = hoursInMs + minutesInMs + secondsInMs;
        return totalMs.toString()
        //millisecondsToTime(totalMs)
    }

    const [show, setShow] = useState(false);
    const [modalTitle, setModalTitle] = useState("");
    const [modalMessage, setModalMessage] = useState("");

    const handleClose = () => setShow(false);
    const handleShow = () => setShow(true);

    const mostrarModal = (estado_req) => {
        if(estado_req === "success"){
            setModalTitle("Cadastro concluído")
            setModalMessage(`Banco de horas de ${funcionario.nomeFuncionario} atualizado com sucesso.`)
            handleShow()
        }else if(estado_req === "vazio"){
            setModalTitle("Erro")
            setModalMessage("Ambos os campos de horas estão vazios.")
        }
        else{
            setModalTitle("Erro")
            setModalMessage("Verifique se você preencheu todos os campos corretamente.")
            handleShow()
        }
    }
        
    if (Object.keys(funcionario).length !== 0){
        return (
            <div className="mt-4">

                <Modal
                        show={show}
                        onHide={handleClose}
                        backdrop="static"
                        keyboard={false}
                    >
                        <Modal.Header closeButton>
                            <Modal.Title>{modalTitle}</Modal.Title>
                        </Modal.Header>
                        <Modal.Body>
                            {modalMessage}
                        </Modal.Body>
                        <Modal.Footer>
                            <Button variant="secondary" onClick={handleClose}>
                                Ok
                            </Button>
                        </Modal.Footer>
                </Modal>
                
                <div>
                    {funcionario &&
                        (<span>
                            {funcionario.nomeFuncionario}
                        </span>)
                    }
                </div>
                <form onSubmit={handleSubmit}>
                    <div>
                        <select style={{width:'250px'}} defaultValue={currentMonth} onChange={e => selectMonth(e.target.value)}>
                            {
                                meses.map((mes) => (
                                    <option key={mes.numero} value={mes.numero}>{mes.nome}</option>
                                ))
                            }
                            
                        </select>
                    </div>
                    
                    <div className="d-flex flex-column mb-3">
                        <div className="d-flex flex-column align-items-center">
                            <label>Horas positivas: </label>
                            <InputMask 
                                style={{width:'250px'}} 
                                name="horasPositivas" 
                                mask="99:99:99" 
                                onChange={handleTimeInput} 
                                //value={formData.horasPositivas} 
                                placeholder="hh:mm:ss"
                                ref={hp_ref}
                                readOnly={false} 
                            />
                        </div>
                        <div className="d-flex flex-column align-items-center">
                            <label>Horas negativas: </label>
                            <InputMask 
                                style={{width:'250px'}} 
                                name="horasNegativas" 
                                mask="99:99:99"
                                onChange={handleTimeInput} 
                                //value={formData.horasNegativas} 
                                placeholder="hh:mm:ss"
                                ref={hn_ref} 
                                readOnly={false} />
                        </div>
                        {error.horasPositivas !== null || error.horasNegativas !== null && <div style={{color:'red'}}>Formato de horas invalido. Verifique se você preencheu os campos corretamente</div>}
                    </div>
                    <div>
                        <button className="btn btn-primary" type="submit">Adicionar horas</button>
                    </div>
                    
                </form>

            </div>
        )
    }
    return (<div></div>)
}

export default CadastrarHoras
