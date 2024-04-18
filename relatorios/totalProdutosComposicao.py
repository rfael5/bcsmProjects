from tkinter import filedialog
from sqlalchemy import create_engine
import pandas as pd
import json
from datetime import datetime
from tkinter import *
from tkcalendar import DateEntry


conexao = (
    "mssql+pyodbc:///?odbc_connect=" + 
    "DRIVER={ODBC Driver 11 for SQL Server};" +
    "SERVER=localhost;" +
    "DATABASE=SOUTTOMAYOR;" +
    "Trusted_Connection=yes;"
)

engine = create_engine(conexao, pool_pre_ping=True)

dataInicio = ''
dataFim = ''

def formatarData(data):
    data_objeto = datetime.strptime(data, '%d/%m/%Y')
    data_formatada = data_objeto.strftime('%Y%m%d')
    return data_formatada

def setarData():
    
    dataInicio = dtInicio.get()
    dtInicioFormatada = formatarData(dataInicio)
    dataFim = dtFim.get()
    dtFimFormatada = formatarData(dataFim)
    produtosComposicao = getProdutosComposicao(dtInicioFormatada, dtFimFormatada)
    ajustes = getAjustes(dtInicioFormatada, dtFimFormatada)
    produtosQtdAjustada = calcularQtdProducao(produtosComposicao)
    ajustesAplicados =aplicarAjustes(produtosQtdAjustada, ajustes)
    somarProdutosEvento(ajustesAplicados)

def receberDados(query):
    response = pd.read_sql_query(query, engine)
    resultadosJson = response.to_json(orient='records')
    dadosDesserializados = json.loads(resultadosJson)
    return dadosDesserializados

def getProdutosComposicao(dataInicio, dataFim):
    queryProdutosComposicao =  f"""
    select 
        e.PK_DOCTOPED as idEvento, e.NOME as nomeEvento, e.DTEVENTO as dataEvento, p.PK_MOVTOPED as idMovtoped, ca.IDX_LINHA as linha, p.DESCRICAO as nomeProdutoAcabado, ca.RENDIMENTO as rendimento, p.UNIDADE as unidadeAcabado, a.RDX_PRODUTO as idProdutoAcabado, c.DESCRICAO as nomeProdutoComposicao, c.IDX_LINHA as classificacao, c.PK_PRODUTO as idProdutoComposicao, a.QUANTIDADE as qtdProdutoComposicao, a.UN as unidadeComposicao, p.L_QUANTIDADE as qtdProdutoEvento
    from TPAPRODCOMPOSICAO as a 
        inner join TPAPRODUTO as c on a.IDX_PRODUTO = c.PK_PRODUTO
        inner join TPAMOVTOPED as p on a.RDX_PRODUTO = p.IDX_PRODUTO
        inner join TPADOCTOPED as e on p.RDX_DOCTOPED = e.PK_DOCTOPED
        inner join TPAPRODUTO as ca on p.IDX_PRODUTO = ca.PK_PRODUTO
    where e.TPDOCTO = 'EC' 
        and e.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and e.SITUACAO = 'Z'
        and c.OPSUPRIMENTOMP = 'S'
    or e.TPDOCTO = 'EC' 
        and e.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and e.SITUACAO = 'B'
        and c.OPSUPRIMENTOMP = 'S'
    or e.TPDOCTO = 'OR' 
        and e.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and e.SITUACAO = 'V'
        and c.OPSUPRIMENTOMP = 'S'
    or e.TPDOCTO = 'OR' 
        and e.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and e.SITUACAO = 'B'
        and c.OPSUPRIMENTOMP = 'S'
    order by p.DESCRICAO
    """
    produtosComposicao = receberDados(queryProdutosComposicao)
    return produtosComposicao

def getAjustes(dataInicio, dataFim):
    queryAjustes = f"""
    select A.IDX_MOVTOPED AS idMovtoped, V.IDX_PRODUTO AS idProduto, V.DESCRICAO AS nomeProduto, A.QUANTIDADE AS ajuste, A.PRECO AS precoAjuste from TPAAJUSTEPEDITEM AS A 
        inner join TPAMOVTOPED AS V ON A.IDX_MOVTOPED = V.PK_MOVTOPED
        inner join TPADOCTOPED AS E ON V.RDX_DOCTOPED = E.PK_DOCTOPED
        inner join TPAPRODUTO AS P ON V.IDX_PRODUTO = P.PK_PRODUTO
    where e.TPDOCTO = 'EC' 
        and E.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and E.SITUACAO = 'Z'
        and P.OPSUPRIMENTOMP = 'S'
    or e.TPDOCTO = 'EC' 
        and E.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and E.SITUACAO = 'B'
        and P.OPSUPRIMENTOMP = 'S'
    or e.TPDOCTO = 'OR' 
        and E.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and E.SITUACAO = 'V'
        and P.OPSUPRIMENTOMP = 'S'
    or e.TPDOCTO = 'OR' 
        and E.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and E.SITUACAO = 'B'
        and P.OPSUPRIMENTOMP = 'S'
    ORDER BY V.DESCRICAO
    """ 
    ajustes = receberDados(queryAjustes)
    return ajustes
        

def executarQueries(dataInicio, dataFim):
    global produtosComposicao
    global ajustes    
    
    for p in produtosComposicao:
        print(p)


# def verificarAjustes(evento):
#     queryAjustes = f"""select PK_AJUSTEPEDITEM as idAjuste, IDX_MOVTOPED as idMovtoped, QUANTIDADE as qtdAlteracao from TPAAJUSTEPEDITEM where IDX_MOVTOPED = '{evento['idMovtoped']}'"""
#     resultado = receberDados(queryAjustes)
#     if len(resultado) > 0:
#         evento['qtdProdutoEvento'] = evento['qtdProdutoEvento'] + resultado[0]['qtdAlteracao']


def adicionarAjustes(evento, ajustes):
    global produtosComposicao
    for a in ajustes:
        if a['idMovtoped'] == evento['idMovtoped']:
            evento['qtdProdutoEvento'] = evento['qtdProdutoEvento'] + a['ajuste']


def recuperarHoraAtual():
    data_hora_atual = datetime.now()
    formato = "%Y-%m-%d_%H-%M-%S"
    data_hora_formatada = data_hora_atual.strftime(formato)
    return data_hora_formatada


def calcularQtdProducao(produtosComposicao):
    for e in produtosComposicao:
        if e['unidadeAcabado'] == 'PP':
            total = (e["qtdProdutoEvento"] / 10) * e["qtdProdutoComposicao"]
            rendimento = total / e["rendimento"]
            e["totalProducao"] = rendimento
        elif e['unidadeAcabado'] == 'UD':
            total = (e['qtdProdutoEvento'] / 100) * e['qtdProdutoComposicao']
            e['totalProducao'] = total
        elif e['unidadeAcabado'] == 'UM':
            total = (e['qtdProdutoEvento'] / 10) * e['qtdProdutoComposicao']
            e['totalProducao'] = total
        else:
            total = e["qtdProdutoComposicao"] * e["qtdProdutoEvento"]
            e["totalProducao"] = total
    
    return produtosComposicao

#calcularQtdProducao()


def aplicarAjustes(produtosComposicao, ajustes):
    for p in produtosComposicao:
        adicionarAjustes(p, ajustes)
    return produtosComposicao

#aplicarAjustes()

def gerarArquivoExcel(tipoArquivo, listaProdutos):
    # Abre a janela de seleção de arquivo
    root = Tk()
    root.withdraw()  # Oculta a janela principal do Tkinter

    # Pede ao usuário para escolher o local e o nome do arquivo
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                               filetypes=[("Arquivos Excel", "*.xlsx")],
                                               title="Salvar Arquivo Excel",
                                               initialfile=f"{tipoArquivo}--{recuperarHoraAtual()}")

    # Verifica se o usuário cancelou a operação
    if not file_path:
        print("Operação cancelada pelo usuário.")
        return

    # Adiciona uma extensão se não for fornecida pelo usuário
    if not file_path.endswith(".xlsx"):
        file_path += ".xlsx"
        
    #caminho_arquivo_excel = f'C:\\Users\\serverteste\\Desktop\\teste2\\arquivos\\{tipoArquivo}--{recuperarHoraAtual()}.xlsx'
    formatoTabela = pd.DataFrame(listaProdutos)
    formatoTabela.to_excel(file_path, index=False)
    print(f"Arquivo salvo em: {file_path}")

somaProdutosEventos = []

def mudarUnidade(unidade):
    if unidade == 'GR':
        return 'KG'
    elif unidade == 'ML':
        return 'LT'
    else:
        return unidade

def alterarStringUnidade(unidade):
    if '\x00' in unidade:
        unidadeCorrigida = unidade.replace('\x00', '')
        return unidadeCorrigida
    else:
        return unidade   

def converterKg(produto):
    if str(produto['unidade']) == "GR" or str(produto['unidade']) == "ML":
        return produto['totalProducao'] / 1000
    else:
        return produto['totalProducao']

def agruparLinhas(produto):
    
    if '\x00' in produto['linha']:
        produto['linha'] = produto['linha'].replace('\x00', '')
        
    for x in range(1, 7):
        if produto['linha'] == f'S{x}':
            return 'Sal'
    
    for x in range(1, 7):
        if produto['linha'] == f'M-{x}':
            return 'Doces'
    
    for x in range(1, 4):
        if produto['linha'] == f'C-{x}' or produto['linha'] == 'Doce Geral':
            return 'Doces'
    
    if produto['linha'] == 'S7' or produto['linha'] == 'S8':
        return 'Refeições'           


def somarProdutosEvento(produtosComposicao):
        
    dfComposicao = pd.DataFrame(produtosComposicao)

    dfComposicao.drop_duplicates(inplace=True)

    dfComposicao['unidade'] = dfComposicao['unidadeComposicao'].apply(alterarStringUnidade)
    dfComposicao['totalProducao'] = dfComposicao.apply(converterKg, axis=1)
    dfComposicao['linha'] = dfComposicao.apply(agruparLinhas, axis=1)
    
    result = dfComposicao.groupby(['idProdutoComposicao', 'nomeProdutoComposicao', 'classificacao', 'unidade', 'linha'])[['totalProducao']].sum().reset_index()

    result['unidade'] = result['unidade'].apply(mudarUnidade)
    
    resultJson = result.to_json(orient='records')
    dadosDesserializados = json.loads(resultJson)
    
    separarProdutosEvento(dadosDesserializados)
    

def filtrarListas(tipoFiltro, listaCompleta):
    listaFiltrada = list(filter(lambda produto:produto['linha'] == tipoFiltro, listaCompleta))
    return listaFiltrada


def separarProdutosEvento(listaProdutos):
    listaSal = filtrarListas('Sal', listaProdutos)
    listaDoces = filtrarListas('Doces', listaProdutos)
    listaRefeicoes = filtrarListas('Refeições', listaProdutos)
    
    gerarArquivoExcel('TODOS-PRODUDOS', listaProdutos)
    gerarArquivoExcel('SAL',listaSal)
    gerarArquivoExcel('DOCES',listaDoces)
    gerarArquivoExcel('REFEICOES',listaRefeicoes)

#somarProdutosEvento()

# for p in produtosComposicao:
#     print(p)

# def buscarData():
#     data_selecionada = cal.get_date()
#     print(data_selecionada)


# Inicia o loop principal
root = Tk()
root.title("Input de Data")

# Cria o widget tkcalendar
dtInicio = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
dtInicio.grid(padx=10, pady=10)

dtFim = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
dtFim.grid(padx=10, pady=10)

btn_obter_data = Button(root, text="Obter Data", command=setarData)
btn_obter_data.grid(pady=10)
root.mainloop()

