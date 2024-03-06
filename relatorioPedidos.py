from tkinter import filedialog
from sqlalchemy import create_engine
import pandas as pd
import json
from datetime import datetime
from tkinter import *
from tkcalendar import DateEntry
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

conexao = (
    "mssql+pyodbc:///?odbc_connect=" + 
    "DRIVER={ODBC Driver 17 for SQL Server};" +
    "SERVER=192.168.1.137;" +
    "DATABASE=SOUTTOMAYOR;" +
    "UID=Sa;" +
    "PWD=P@ssw0rd2023"
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
    estoque = getEstoque()
    produtosQtdAjustada = calcularQtdProducao(produtosComposicao)
    ajustesAplicados =aplicarAjustes(produtosQtdAjustada, ajustes)
    adicionarEstoque(ajustesAplicados, estoque)
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

def getEstoque():
    queryEstoque = """
    WITH RankedResults AS (
        SELECT 
            E.RDX_PRODUTO,
            E.SALDOESTOQUE,
            E.DTULTCPA,
            P.DESCRICAO,
            P.UN,
            ROW_NUMBER() OVER (PARTITION BY RDX_PRODUTO ORDER BY DTULTCPA DESC) AS Rank
        FROM TPAESTOQUE AS E INNER JOIN TPAPRODUTO AS P ON E.RDX_PRODUTO = P.PK_PRODUTO 
        WHERE E.DTULTCPA IS NOT NULL
    )
    SELECT
        RDX_PRODUTO,
        SALDOESTOQUE,
        DTULTCPA,
        DESCRICAO,
        UN
    FROM RankedResults
    WHERE Rank = 1
    ORDER BY RDX_PRODUTO
    """
    estoque = receberDados(queryEstoque)
    return estoque


def adicionarAjustes(evento, ajustes):
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


def aplicarAjustes(produtosComposicao, ajustes):
    for p in produtosComposicao:
        adicionarAjustes(p, ajustes)
    return produtosComposicao


def adicionarEstoque(produtos, estoque):
    for p in produtos:
        p['estoque'] = 0
        p['unidadeEstoque'] = ''
        for e in estoque:
            if p['idProdutoComposicao'] == e['RDX_PRODUTO']:
                p['estoque'] = e['SALDOESTOQUE']
                p['unidadeEstoque'] = e['UN']

def formatarTabela(caminho):
    wb = load_workbook(caminho)
    ws = wb.active
    
    if incluirLinhaProducao.get() ==1:
        ws['A1'] = 'ID'
        ws['B1'] = 'Nome do produto'
        ws['C1'] = 'Classificação'
        ws['D1'] = 'Unidade'
        ws['E1'] = 'Linha'
        ws['F1'] = 'Estoque'
        ws['G1'] = 'Un. Estoque'
        ws['H1'] = 'Qtd. Produção'
        
        for cell in ws[1]:
            cell.fill = PatternFill(start_color="FDDA0D", end_color="FDDA0D", fill_type="solid")
        for cell in ws['F'][1:]:
            cell.fill = PatternFill(start_color="5D8AA8", end_color="5D8AA8", fill_type="solid")
        for cell in ws['G'][1:]:
            cell.fill = PatternFill(start_color="5D8AA8", end_color="5D8AA8", fill_type="solid")
        for cell in ws['H'][1:]:
            cell.fill = PatternFill(start_color="6b8e23", end_color="6b8e23", fill_type="solid")
        
        ws.column_dimensions['A'].width = 10
        ws.column_dimensions['B'].width = 40
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 10
        ws.column_dimensions['G'].width = 15
        ws.column_dimensions['H'].width = 15
        
        wb.save(caminho)
    else:
        ws['A1'] = 'ID'
        ws['B1'] = 'Nome do produto'
        ws['C1'] = 'Classificação'
        ws['D1'] = 'Unidade'
        ws['E1'] = 'Estoque'
        ws['F1'] = 'Un. Estoque'
        ws['G1'] = 'Qtd. Produção'
        
        for cell in ws[1]:
            cell.fill = PatternFill(start_color="FDDA0D", end_color="FDDA0D", fill_type="solid")
        for cell in ws['E'][1:]:
            cell.fill = PatternFill(start_color="5D8AA8", end_color="5D8AA8", fill_type="solid")
        for cell in ws['F'][1:]:
            cell.fill = PatternFill(start_color="5D8AA8", end_color="5D8AA8", fill_type="solid")
        for cell in ws['G'][1:]:
            cell.fill = PatternFill(start_color="6b8e23", end_color="6b8e23", fill_type="solid")
        
        ws.column_dimensions['A'].width = 10
        ws.column_dimensions['B'].width = 40
        ws.column_dimensions['C'].width = 25
        ws.column_dimensions['D'].width = 10
        ws.column_dimensions['E'].width = 10
        ws.column_dimensions['F'].width = 15
        ws.column_dimensions['G'].width = 15
        
        wb.save(caminho)
    

def gerarArquivoExcel(tipoArquivo, listaProdutos):
    root = Tk()
    root.withdraw()

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
        
    formatoTabela = pd.DataFrame(listaProdutos)
    formatoTabela.to_excel(file_path, index=False)
    formatarTabela(file_path)
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
    
    if incluirLinhaProducao.get() == 1:
        dfComposicao['unidade'] = dfComposicao['unidadeComposicao'].apply(alterarStringUnidade)
        dfComposicao['totalProducao'] = dfComposicao.apply(converterKg, axis=1)
        dfComposicao['linha'] = dfComposicao.apply(agruparLinhas, axis=1)
        
        result = dfComposicao.groupby(['idProdutoComposicao', 'nomeProdutoComposicao', 'classificacao', 'unidade', 'linha', 'estoque', 'unidadeEstoque'])[['totalProducao']].sum().reset_index()

        result['unidade'] = result['unidade'].apply(mudarUnidade)
        
        resultJson = result.to_json(orient='records')
        dadosDesserializados = json.loads(resultJson)
        
        separarProdutosEvento(dadosDesserializados)
    
    else:
        dfComposicao['unidade'] = dfComposicao['unidadeComposicao'].apply(alterarStringUnidade)
        dfComposicao['totalProducao'] = dfComposicao.apply(converterKg, axis=1)
        
        result = dfComposicao.groupby(['idProdutoComposicao', 'nomeProdutoComposicao', 'classificacao', 'unidade', 'estoque', 'unidadeEstoque'])[['totalProducao']].sum().reset_index()

        result['unidade'] = result['unidade'].apply(mudarUnidade)
        
        resultJson = result.to_json(orient='records')
        dadosDesserializados = json.loads(resultJson)
        
        gerarArquivoExcel('COMPRAS', dadosDesserializados)
    

def filtrarListas(tipoFiltro, listaCompleta):
    listaFiltrada = list(filter(lambda produto:produto['linha'] == tipoFiltro, listaCompleta))
    return listaFiltrada


def separarProdutosEvento(listaProdutos):
    listaSal = filtrarListas('Sal', listaProdutos)
    listaDoces = filtrarListas('Doces', listaProdutos)
    listaRefeicoes = filtrarListas('Refeições', listaProdutos)
    
    gerarArquivoExcel('LISTA_PEDIDOS', listaProdutos)
    gerarArquivoExcel('SAL',listaSal)
    gerarArquivoExcel('DOCES',listaDoces)
    gerarArquivoExcel('REFEICOES',listaRefeicoes)


# Inicia o loop principal
root = Tk()
root.title("Gerar pedidos de suprimento")
root.geometry('500x400')

# tipoRelatorio = Label(root, text="Gerar documento com linha de produção?", bg="#333333", fg="#FFFFFF", font=("Arial", 14))
# tipoRelatorio.grid(row=0, columnspan=2, padx=10, pady=10, sticky="nsew")

incluirLinhaProducao = IntVar(value=1)
semLinhaProducao = IntVar()

# c2 = Checkbutton(root, text='Não',variable=semLinhaProducao, onvalue=1, offvalue=0, bg="#333333", font=("Arial", 14))
# c2.grid()

explicacao = Label(root, text="Selecione abaixo o periodo de tempo\n para o qual você quer gerar a lista de\n pedidos de suprimento.", font=("Arial", 14))
explicacao.grid(row=2, columnspan=2, padx=10, pady=10, sticky="nsew")

lbl_dtInicio = Label(root, text="De:", font=("Arial", 14))
lbl_dtInicio.grid(row=3, column=0, padx=10, pady=5, sticky="w")

# Cria o widget tkcalendar
dtInicio = DateEntry(root, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
dtInicio.grid(row=4, column=0, padx=10, pady=10, sticky="w")

lbl_dtFim = Label(root, text="Até:", font=("Arial", 14))
lbl_dtFim.grid(row=3, column=1, padx=10, pady=5, sticky="w")

dtFim = DateEntry(root, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
dtFim.grid(row=4, column=1, padx=10, pady=10, sticky="w")

c1 = Checkbutton(root, text='Gerar documento com linha de produção?',variable=incluirLinhaProducao, onvalue=1, offvalue=0, font=("Arial", 14), height=5, width=5)
c1.grid(row=5, columnspan=2, padx=10, pady=10, sticky="nsew")

btn_obter_data = Button(root, text="Gerar Planilhas", font=("Arial", 16), command=setarData)
btn_obter_data.grid(row=6, columnspan=2, padx=50, pady=30, sticky="nsew")

root.mainloop()

