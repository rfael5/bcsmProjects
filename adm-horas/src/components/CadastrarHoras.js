import React, {useState} from "react";

const CadastrarHoras = ({funcionario}) =>{
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

    const [formData, setFormData] = useState({
        idFuncionario: 1,
        horas:'',
        tipoHora:'P',
        unidade: 'Solar das Festas',
        mes: '08',
        nomeMes: 'Agosto',
        ano:'2024'
    })

    const selectMonth = (value) => {
        console.log(value)
    }

    const handleChange = (e) => {
        const {name, value} = e.target;
        setFormData({
            ...formData,
            [name]:value
        })
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        window.api.postHoras(formData)
    }

    const handlePostHoras = () => {
        window.api.postHoras(formData)
    }

    return (
        <div class="mt-4">
            <div class="bg-danger">
                <span>Teste</span>
            {funcionario &&
                (<span>
                    {funcionario.nomeFuncionario}
                </span>)
            }
            </div>
            <button onClick={() => handlePostHoras()}>BTN TESTE</button>
            <form onSubmit={handleSubmit}>
                <div>
                    <select onChange={e => selectMonth(e.target.value)}>
                        {
                            meses.map((mes) => (
                                <option value={[mes.numero, mes.nome]}>{mes.nome}</option>
                            ))
                        }
                        
                    </select>
                </div>
                
                <div class="d-flex flex-column">
                    <div class="d-flex flex-column">
                        <label>Tipo de Horas</label>
                        <select name="tipoHora" defaultValue="P" value={formData.tipoHora} onChange={handleChange}>
                            <option value="P">Positivas</option>
                            <option value="N">Negativas</option>
                        </select>
                    </div>
                    <div class="d-flex flex-column">
                        <label>Horas</label>
                        <input name="horas" value={formData.horas} onChange={handleChange}></input>
                    </div>
                </div>

                <button type="submit">Adicionar horas</button>
            </form>
        </div>
    )
}

export default CadastrarHoras