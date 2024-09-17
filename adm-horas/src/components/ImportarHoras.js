import React, {useState, useEffect} from 'react';
import * as XLSX from 'xlsx';
import { DadosFuncionario } from './Interfaces/dadosFuncionario';

const ImportarHoras = () => {

    const [arquivo, setArquivo] = useState([])
    const [setores, setSetores] = useState([])
    const [select, setSelect] = useState("TODOS")
    const [filtroFuncionarios, setFiltroFuncionarios] = useState([])

    const handleArquivo = (event) => {
        let files = event.target.files;
        let allData = [];
        Array.from(files).forEach((file) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, {type:'array'});

                const firstSheetName = workbook.SheetNames[0];
                const worksheet = workbook.Sheets[firstSheetName];
                let jsonData = XLSX.utils.sheet_to_json(worksheet);

                allData = [...allData, ...jsonData];

                if (file === files[files.length - 1]){
                    let _setores = allData.map(item => item["Departamento"]);
                    const filtroSetores = Array.from(new Set(_setores));
                    filtroSetores.push("TODOS")
                    setSetores(filtroSetores)

                    allData = setarHorasFuncionario(allData);
                    criarObjeto(allData);
                }
            };
            reader.readAsArrayBuffer(file)
        });

    };

    const criarObjeto = (lista) => {
        let novaLista = []
        lista.forEach((f) => {
            let horasFuncionario = lista.filter((row) => f["Matrícula"] == row["Matrícula"])
            f["horas"] = horasFuncionario[0]["horas"]
            let info = new DadosFuncionario(
                f["CPF"],              
                f["Cargo"],
                f["Data de Admissão"],
                f["Departamento"],
                f["Filial"],
                f["Matrícula"],
                f["Nome"],
                f["Pis"],
                f["Regime de trabalho"],
                f["Tipo do banco de horas"],
                f["horas"]
            )
            novaLista.push(info)
        })
        novaLista = removeDuplicates(novaLista, 'matricula')
        // novaLista.forEach((row) => {
        //     row.totalHorasPositivas = somarHoras(row.horas, 'horasPositivas');
        //     row.totalHorasNegativas = somarHoras(row.horas, 'horasNegativas');
        //     row.saldoTotal = calcularSaldoFinal(row.horas)
        // }) 
        setArquivo(novaLista)
        setFiltroFuncionarios(novaLista)
    }

    const somarHoras = (arr, tipo) => {
        const res = arr.reduce((acc, obj) => {
            let ms = convertToMilliseconds(obj[tipo])
            acc[tipo] = (acc[tipo] || 0) + ms
            return acc          
        }, {})
        const horasFormatadas = millisecondsToTime(res[tipo])
        return horasFormatadas
    }

    const calcularSaldoFinal = (arr) => {
        const horasPositivas = somarHoras(arr, "horasPositivas");
        const horasNegativas = somarHoras(arr, "horasNegativas");

        const _horas = {horasPositivas, horasNegativas}
        const saldoFinal = calcularSaldoHoras(_horas)
        return saldoFinal
    }

    function convertToMilliseconds(strTime){

        let [hours, minutes] = strTime.split(':').map(Number);
        if(hours < 0){
            hours = hours * -1
        }else if(minutes < 0){
             minutes = minutes * -1
        }

        const hoursInMs = hours * 60 * 60 * 1000;
        const minutesInMs = minutes * 60 * 1000;

        const totalMs = hoursInMs + minutesInMs
        return totalMs
    }

    const calcularSaldoHoras = (horas) => {
        if(horas === ''){
            return ''
        }else{
            const {horasPositivas, horasNegativas} = horas
            const horasPositivasMS = convertToMilliseconds(horasPositivas)
            const horasNegativasMS = convertToMilliseconds(horasNegativas)
            const saldoFinal = horasPositivasMS - horasNegativasMS
            if(saldoFinal < 0){
                const converterNegativo = saldoFinal * -1
                const saldoHoras = millisecondsToTime(converterNegativo)
                return `- ${saldoHoras}`
            }else{
                const saldoHoras = millisecondsToTime(saldoFinal)
                return saldoHoras
            }
        }
    }

    function millisecondsToTime(ms) {
        // Calculate hours, minutes, and seconds from milliseconds
        const hours = Math.floor(ms / (60 * 60 * 1000));
        const minutes = Math.floor((ms % (60 * 60 * 1000)) / (60 * 1000));
    
        // Format the values as "hh:mm:ss"
        const formattedHours = String(hours).padStart(2, '0');
        const formattedMinutes = String(minutes).padStart(2, '0');
    
        const totalHs = `${formattedHours}:${formattedMinutes}`;
        return totalHs
        
    }

    const removeDuplicates = (arr, key) => {
        return [...new Map(arr.map(item => [item[key], item])).values()];
    }

    const setarHorasFuncionario = (listaFuncionarios) => {
        return listaFuncionarios.map((f) => {
            f["horas"] = []
            let horas = listaFuncionarios.filter(h => h["Matrícula"] === f["Matrícula"])
            horas.forEach((hf) => {
                let mes = hf["Período"]
                let horasPositivas = hf["Horas positivas"]
                let horasNegativas = hf["Horas negativas"]
                let saldo = hf["Saldo"]
                let obj = {horasPositivas, horasNegativas, saldo, mes}
                f["horas"].push(obj)
            })
            f["horas"].sort((a, b) => {
                const dateA = new Date(`01/${a.mes}`);
                const dateB = new Date(`01/${b.mes}`);
                return dateA - dateB;
            })

            return f
        })
    }

    function verArquivo(){
        let teste = arquivo.filter(t => t.matricula === "1531")
        console.log(teste[0].horas)
        calcularSaldoFinal(teste[0].horas)
    }

    const setSelectedField = (value) => {
        setSelect(value)
        if(value !== "TODOS"){
            let listaFiltrada = arquivo.filter(funcionarios => funcionarios.departamento === value)
            setFiltroFuncionarios(listaFiltrada)
        }else{
            setFiltroFuncionarios(arquivo)
        }
    }

    const fillColumn = (arr, _mes) => {
        let mesSelecionado = `0${_mes}/2024`
        let mesColuna = arr.filter(m => m.mes === mesSelecionado)
        if(mesColuna.length == 0){
            return ''
        }else{
            return mesColuna[0]
        }
        
    }

    const createMonthsArray = (arr) => {
        let listaMeses = []
        //console.log(arr)
        for(let x = 0; x <= 11; x++){
            let mesSelecionado = fillColumn(arr, x + 1)
            listaMeses[x] = mesSelecionado
        }
        //console.log(listaMeses)
        return listaMeses
    }

    const exportToExcel = (jsonData, fileName) => {
        const workbook = XLSX.utils.book_new();

        let data = []

        const headers = ['NOME', 'SETOR', '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro', 'Total', 'Saldo', 'DEVERÁ FOLGAR ESTE MÊS', 'ESTE MÊS DEVERÁ FAZER HORA EXTRA']

        data.push(headers);

        jsonData.forEach(item => {
            const horasPorMes = createMonthsArray(item.horas)
            // const row1 = [item.nome, item.departamento, item.horas[0]?.horasPositivas || '', item.horas[1]?.horasPositivas || '', item.horas[2]?.horasPositivas || '', item.horas[3]?.horasPositivas || '']
            const row1 = [
                item.nome, 
                item.departamento,
                'Horas positivas', 
                horasPorMes[0].horasPositivas || '', 
                horasPorMes[1].horasPositivas || '', 
                horasPorMes[2].horasPositivas || '', 
                horasPorMes[3].horasPositivas || '',
                horasPorMes[4].horasPositivas || '',
                horasPorMes[5].horasPositivas || '',
                horasPorMes[6].horasPositivas || '',
                horasPorMes[7].horasPositivas || '',
                horasPorMes[8].horasPositivas || '',
                horasPorMes[9].horasPositivas || '',
                horasPorMes[10].horasPositivas || '',
                horasPorMes[11].horasPositivas || '',
                somarHoras(item.horas, 'horasPositivas'),
                calcularSaldoFinal(item.horas),
                '',
                ''
            ]
            // const row2 = ['', '', item.horas[0]?.horasNegativas || '', item.horas[1]?.horasNegativas || '', item.horas[2]?.horasNegativas || '', item.horas[3]?.horasNegativas || '']
            const row2 = [
                '', 
                '',
                'Horas negativas', 
                horasPorMes[0].horasNegativas || '', 
                horasPorMes[1].horasNegativas || '', 
                horasPorMes[2].horasNegativas || '', 
                horasPorMes[3].horasNegativas || '',
                horasPorMes[4].horasNegativas || '',
                horasPorMes[5].horasNegativas || '',
                horasPorMes[6].horasNegativas || '',
                horasPorMes[7].horasNegativas || '',
                horasPorMes[8].horasNegativas || '',
                horasPorMes[9].horasNegativas || '',
                horasPorMes[10].horasNegativas || '',
                horasPorMes[11].horasNegativas || '',
                somarHoras(item.horas, 'horasNegativas'),
                '',
                '',
                ''
            ]
            
            //const row3 = ['', '', calcularSaldoHoras(item.horas?.[0]) || '', calcularSaldoHoras(item.horas?.[1]) || '', calcularSaldoHoras(item.horas?.[2]) || '', calcularSaldoHoras(item.horas?.[3]) || '']
            const row3 = [
                '', 
                '',
                'Saldo total', 
                calcularSaldoHoras(horasPorMes[0]) || '', 
                calcularSaldoHoras(horasPorMes[1]) || '', 
                calcularSaldoHoras(horasPorMes[2]) || '', 
                calcularSaldoHoras(horasPorMes[3]) || '',
                calcularSaldoHoras(horasPorMes[4]) || '',
                calcularSaldoHoras(horasPorMes[5]) || '',
                calcularSaldoHoras(horasPorMes[6]) || '',
                calcularSaldoHoras(horasPorMes[7]) || '',
                calcularSaldoHoras(horasPorMes[8]) || '',
                calcularSaldoHoras(horasPorMes[9]) || '',
                calcularSaldoHoras(horasPorMes[10]) || '',
                calcularSaldoHoras(horasPorMes[11]) || '',
                calcularSaldoFinal(item.horas),
                '',
                '',
                ''
            ]


            data.push(row1, row2, row3);

            data.push(['', '', '', '', '', '']);
        })

        const worksheet = XLSX.utils.aoa_to_sheet(data);

        worksheet['!cols'] = [
            { wch: 40 }, //A
            { wch: 30 }, //B
            { wch: 20 }, //C
            { wch: 20 }, //D
            { wch: 20 }, //E
            { wch: 20 }, //F
            { wch: 20 }, //G
            { wch: 20 }, //H
            { wch: 20 }, //I
            { wch: 20 }, //J
            { wch: 20 }, //K
            { wch: 20 }, //L
            { wch: 20 }, //M
            { wch: 20 }, //N
            { wch: 20 }, //O
            { wch: 20 }, //P
            { wch: 30 }, //Q
            { wch: 30 }, //R
            { wch: 30 }, //S
        ]

        jsonData.forEach((item, index) => {
            const startRow = index * 4 + 2;

            worksheet[`A${startRow}`] = {t:'s', v:item.nome};
            worksheet[`B${startRow}`] = {t:'s', v:item.departamento};

            // Color the "Horas positivas" row in blue
        for (let i = 3; i <= 14; i++) {  // Starting from 'D' to 'O'
            const cellRef = XLSX.utils.encode_cell({ c: i, r: startRow - 1 });
            if (worksheet[cellRef]) {
                worksheet[cellRef].s = { font: { color: { rgb: "007FFF" } } };
            }
        }

        // Color the "Horas negativas" row in red
        for (let i = 3; i <= 14; i++) {  // Starting from 'D' to 'O'
            const cellRef = XLSX.utils.encode_cell({ c: i, r: startRow });
            if (worksheet[cellRef]) {
                worksheet[cellRef].s = { font: { color: { rgb: "FF0000" } } };
            }
        }

            worksheet['!merges'] = worksheet['!merges'] || [];
            worksheet['!merges'].push(
                { s: { r: startRow - 1, c: 0 }, e: { r: startRow + 2 - 1, c: 0 } },  // Merge 3 rows in column A
                { s: { r: startRow - 1, c: 1 }, e: { r: startRow + 2 - 1, c: 1 } }   // Merge 3 rows in column B
            )
        });

        XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');

        XLSX.writeFile(workbook, `${fileName}.xlsx`);
    };

    return (
        <div>
            <label>Selecionar arquivo</label>
            <input type="file" id="fileInput" onChange={handleArquivo} multiple />

            <button onClick={verArquivo}>Ver arquivo</button>

            <button onClick={() => exportToExcel(filtroFuncionarios, 'teste')}>Gerar Excel</button>

            <div>
                <select value={select} onChange={e => setSelectedField(e.target.value)}>
                    {setores?.map((setor) => (
                        <option key={setor} value={setor}>{setor}</option>
                    ))}
                </select>
            </div>

            

            <div className="d-flex justify-content-center mt-4">
                <table className="table  table-striped table-hover ">

                    <tbody>
                        {
                        filtroFuncionarios.map((func) => (
                            <tr key={func.Matrícula}>
                                <td style={{ width: '60px' }}>{func.nome}</td>
                                <td style={{width: '60px'}}>{func.departamento}</td>
                                <td>
                                    <div className="d-flex flex-row">
                                        {
                                            func.horas?.map((horas) => (
                                                <div key={horas.mes}>
                                                    <div className="me-5">{horas.mes}</div>
                                                    <div className="me-5">{horas.horasPositivas}</div>
                                                    <div className="me-5">{horas.horasNegativas}</div>
                                                    <div className="me-5">{calcularSaldoHoras(horas)}</div>
                                                </div>
                                            ))
                                        }
                                    </div>
                                </td>
                                <td>
                                    <div>
                                        {somarHoras(func.horas, 'horasPositivas')}
                                    </div>
                                    <div>
                                        {`- ${somarHoras(func.horas, "horasNegativas")}`}
                                    </div>
                                    <div>
                                        {calcularSaldoFinal(func.horas)}
                                    </div>
                                </td>
                                
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )   
}

export default ImportarHoras