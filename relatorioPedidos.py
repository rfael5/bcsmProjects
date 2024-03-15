from tkinter import filedialog
from sqlalchemy import create_engine
import pandas as pd
import json
from datetime import datetime
from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import messagebox
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from random import choice

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
produtosAjustados = []

def formatarData(data):
    data_objeto = datetime.strptime(data, '%d/%m/%Y')
    data_formatada = data_objeto.strftime('%Y%m%d')
    return data_formatada

def setarData():
    dataInicio = dtInicio.get()
    dtInicioFormatada = formatarData(dataInicio)
    dataFim = dtFim.get()
    dtFimFormatada = formatarData(dataFim)
    if dtInicioFormatada < dtFimFormatada:
        produtosComposicao = getProdutosComposicao(dtInicioFormatada, dtFimFormatada)
        ajustes = getAjustes(dtInicioFormatada, dtFimFormatada)
        estoque = getEstoque()
        produtosQtdAjustada = calcularQtdProducao(produtosComposicao)
        ajustesAplicados =aplicarAjustes(produtosQtdAjustada, ajustes)
        adicionarEstoque(ajustesAplicados, estoque)
        produtos = somarProdutosEvento(ajustesAplicados)
        return produtos
    else:
        return None
        
    

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
            #rendimento = total / e["rendimento"]
            e["totalProducao"] = total
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
        ws['D1'] = 'Linha'
        ws['E1'] = 'Estoque'
        ws['F1'] = 'Un. Estoque'
        ws['G1'] = 'Qtd. Produção'
        ws['H1'] = 'Unidade'
        
        for cell in ws[1]:
            cell.fill = PatternFill(start_color="FDDA0D", end_color="FDDA0D", fill_type="solid")
        for cell in ws['E'][1:]:
            cell.fill = PatternFill(start_color="5D8AA8", end_color="5D8AA8", fill_type="solid")
        for cell in ws['F'][1:]:
            cell.fill = PatternFill(start_color="5D8AA8", end_color="5D8AA8", fill_type="solid")
        for cell in ws['G'][1:]:
            cell.fill = PatternFill(start_color="6b8e23", end_color="6b8e23", fill_type="solid")
        for cell in ws['H'][1:]:
            cell.fill = PatternFill(start_color="6b8e23", end_color="6b8e23", fill_type="solid")
        
        ws.column_dimensions['A'].width = 10
        ws.column_dimensions['B'].width = 40
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 10
        ws.column_dimensions['F'].width = 15
        ws.column_dimensions['G'].width = 15
        ws.column_dimensions['H'].width = 15
        
        wb.save(caminho)
    else:
        ws['A1'] = 'ID'
        ws['B1'] = 'Nome do produto'
        ws['C1'] = 'Classificação'
        ws['D1'] = 'Estoque'
        ws['E1'] = 'Un. Estoque'
        ws['F1'] = 'Qtd. Produção'
        ws['G1'] = 'Unidade'
        
        for cell in ws[1]:
            cell.fill = PatternFill(start_color="FDDA0D", end_color="FDDA0D", fill_type="solid")
        for cell in ws['D'][1:]:
            cell.fill = PatternFill(start_color="5D8AA8", end_color="5D8AA8", fill_type="solid")
        for cell in ws['E'][1:]:
            cell.fill = PatternFill(start_color="5D8AA8", end_color="5D8AA8", fill_type="solid")
        for cell in ws['F'][1:]:
            cell.fill = PatternFill(start_color="6b8e23", end_color="6b8e23", fill_type="solid")
        for cell in ws['G'][1:]:
            cell.fill = PatternFill(start_color="6b8e23", end_color="6b8e23", fill_type="solid")
        
        ws.column_dimensions['A'].width = 10
        ws.column_dimensions['B'].width = 40
        ws.column_dimensions['C'].width = 25
        ws.column_dimensions['D'].width = 10
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 15
        ws.column_dimensions['G'].width = 10
        
        wb.save(caminho)
    

def gerarArquivoExcel(tipoArquivo, listaProdutos):
    root = Tk()
    root.withdraw()

    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                               filetypes=[("Arquivos Excel", "*.xlsx")],
                                               title="Salvar Arquivo Excel",
                                               initialfile=f"{tipoArquivo}--{recuperarHoraAtual()}")

    if not file_path:
        print("Operação cancelada pelo usuário.")
        return

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
        result = produto['totalProducao'] / 1000 
    else:
        result = produto['totalProducao']
    return round(result, 4)

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
        
        result = result[['idProdutoComposicao', 'nomeProdutoComposicao', 'classificacao', 'linha', 'estoque', 'unidadeEstoque', 'totalProducao', 'unidade']]
        
        resultJson = result.to_json(orient='records')
        dadosDesserializados = json.loads(resultJson)
        dadosOrdenados = sorted(dadosDesserializados, key=lambda p:p['nomeProdutoComposicao'])
        #separarProdutosEvento(dadosDesserializados)
        return dadosOrdenados
    else:
        dfComposicao['unidade'] = dfComposicao['unidadeComposicao'].apply(alterarStringUnidade)
        dfComposicao['totalProducao'] = dfComposicao.apply(converterKg, axis=1)
        
        result = dfComposicao.groupby(['idProdutoComposicao', 'nomeProdutoComposicao', 'classificacao', 'unidade', 'estoque', 'unidadeEstoque'])[['totalProducao']].sum().reset_index()

        result['unidade'] = result['unidade'].apply(mudarUnidade)
        
        result = result[['idProdutoComposicao', 'nomeProdutoComposicao', 'classificacao', 'estoque', 'unidadeEstoque', 'totalProducao', 'unidade']]
        
        resultJson = result.to_json(orient='records')
        dadosDesserializados = json.loads(resultJson)
        dadosOrdenados = sorted(dadosDesserializados, key=lambda p:p['nomeProdutoComposicao'])
        #gerarArquivoExcel('COMPRAS', dadosDesserializados)
        return dadosOrdenados
    

def filtrarListas(tipoFiltro, listaCompleta):
    listaFiltrada = list(filter(lambda produto:produto['linha'] == tipoFiltro, listaCompleta))
    return listaFiltrada

def separarProdutosEvento(listaProdutos):
    if trazerTodos.get() or filtrarSal.get() or  filtrarDoces.get() or filtrarRefeicoes.get() == 1:
        if trazerTodos.get() == 1:       
            gerarArquivoExcel('LISTA_PEDIDOS', listaProdutos)
        if filtrarSal.get() == 1:
            listaSal = filtrarListas('Sal', listaProdutos)
            gerarArquivoExcel('SAL',listaSal)
        if filtrarDoces.get() == 1:
            listaDoces = filtrarListas('Doces', listaProdutos)
            gerarArquivoExcel('DOCES',listaDoces)
        if filtrarRefeicoes.get() == 1:
            listaRefeicoes = filtrarListas('Refeições', listaProdutos)
            gerarArquivoExcel('REFEICOES',listaRefeicoes)
    else:
        messagebox.showinfo("Seleção Inválida", "Selecione o tipo de planilha a ser gerado.")
        return None


def criarTabela():
    global table 
    table = ttk.Treeview(root, columns = ('ID', 'Produto', 'Classificacao', 'Linha', 'Estoque', 'Un. Estoque', 'Qtd. Producao', 'Unidade'), show = 'headings')
    table.heading('ID', text = 'ID')
    table.heading('Produto', text = 'Produto')
    table.heading('Classificacao', text = 'Classificacao')
    table.heading('Linha', text = 'Linha')
    table.heading('Estoque', text = 'Estoque')
    table.heading('Un. Estoque', text = 'Un. Estoque')
    table.heading('Qtd. Producao', text = 'Qtd. Producao')
    table.heading('Unidade', text = 'Unidade')
    table.grid(row=6, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

    table.column('ID', width=80, anchor=CENTER)
    table.column('Produto', width=300, anchor=CENTER)
    table.column('Classificacao', width=160, anchor=CENTER)
    table.column('Linha', width=100, anchor=CENTER)
    table.column('Estoque', width=80, anchor=CENTER)
    table.column('Un. Estoque', width=80, anchor=CENTER)
    table.column('Qtd. Producao', width=100, anchor=CENTER)
    table.column('Unidade', width=80, anchor=CENTER)


def atualizarTabela():
    global table
    if incluirLinhaProducao.get() != 1: 
        table = ttk.Treeview(root, columns = ('ID', 'Produto', 'Classificacao', 'Estoque', 'Un. Estoque', 'Qtd. Producao', 'Unidade'), show = 'headings')
        table.heading('ID', text = 'ID')
        table.heading('Produto', text = 'Produto')
        table.heading('Classificacao', text = 'Classificacao')
        table.heading('Estoque', text = 'Estoque')
        table.heading('Un. Estoque', text = 'Un. Estoque')
        table.heading('Qtd. Producao', text = 'Qtd. Producao')
        table.heading('Unidade', text = 'Unidade')
        table.grid(row=6, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

        table.column('ID', width=80, anchor=CENTER)
        table.column('Produto', width=300, anchor=CENTER)
        table.column('Classificacao', width=160, anchor=CENTER)
        table.column('Estoque', width=80, anchor=CENTER)
        table.column('Un. Estoque', width=80, anchor=CENTER)
        table.column('Qtd. Producao', width=100, anchor=CENTER)
        table.column('Unidade', width=80, anchor=CENTER)
    else:
        criarTabela()

def selecionarOpcao(event):
    todosProdutos = setarData()
    valorSelecionado = combo.get()
    if valorSelecionado == 'Todos os produtos':
        return todosProdutos
    elif valorSelecionado == 'Sal':
        produtosSal = filtrarListas('Sal', todosProdutos)
        return produtosSal
    elif valorSelecionado == 'Doces':
        produtosDoce = filtrarListas('Doces', todosProdutos)
        return produtosDoce
    elif valorSelecionado == 'Refeições':
        produtosRefeicao = filtrarListas('Refeições', todosProdutos)
        return produtosRefeicao
    
    print(f"Opção selecionada: {valorSelecionado}")

def inserirNaLista():
    if incluirLinhaProducao.get() == 1:
        produtos = selecionarOpcao(Event)
    else:
        produtos = setarData()
    produtosOrdenados = sorted(produtos, key=lambda p:p['nomeProdutoComposicao'], reverse=True)
    table.delete(*table.get_children())
    #['idProdutoComposicao', 'nomeProdutoComposicao', 'classificacao', 'estoque', 'unidadeEstoque', 'totalProducao', 'unidade']
    for p in produtosOrdenados:
        if incluirLinhaProducao.get() == 1: 
            id = p['idProdutoComposicao']
            nome = p['nomeProdutoComposicao']
            classificacao = p['classificacao']
            linha = p['linha']
            estoque = p['estoque']
            unidadeEstoque = p['unidadeEstoque']
            totalProducao = p['totalProducao']
            unidade = p['unidade']
            data = (id, nome, classificacao, linha, estoque, unidadeEstoque, totalProducao, unidade)
            table.insert(parent='', index=0, values=data)
        else:
            id = p['idProdutoComposicao']
            nome = p['nomeProdutoComposicao']
            classificacao = p['classificacao']
            estoque = p['estoque']
            unidadeEstoque = p['unidadeEstoque']
            totalProducao = p['totalProducao']
            unidade = p['unidade']
            data = (id, nome, classificacao, estoque, unidadeEstoque, totalProducao, unidade)
            table.insert(parent='', index=0, values=data)
            

def gerarPlanilha():
    produtos = setarData()
    if produtos == None:
        messagebox.showinfo('Data inválida', 'Periodo selecionado inválido')
    else:
        if incluirLinhaProducao.get() == 1:
            separarProdutosEvento(produtos)
        else:
            gerarArquivoExcel('COMPRAS', produtos)


#Tkinter
root = Tk()
root.title("Gerar pedidos de suprimento")
#root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))

incluirLinhaProducao = IntVar(value=1)
semLinhaProducao = IntVar()
filtrarSal = IntVar(value=0)
filtrarDoces = IntVar(value=0)
filtrarRefeicoes = IntVar(value=0)
trazerTodos = IntVar(value=1)

explicacao = Label(root, text="Selecione abaixo o período de tempo para o qual você quer gerar a lista de\n pedidos de suprimento.", font=("Arial", 14))
explicacao.grid(row=0, columnspan=2, padx=(150, 0), pady=10, sticky="nsew")

lbl_dtInicio = Label(root, text="De:", font=("Arial", 14))
lbl_dtInicio.grid(row=1, padx=(0, 190), column=0, sticky="e")

dtInicio = DateEntry(root, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
dtInicio.grid(row=2, column=0, padx=(150, 0), pady=5, sticky="e")

lbl_dtFim = Label(root, text="Até:", font=("Arial", 14))
lbl_dtFim.grid(row=1, column=1, padx=(50, 0), pady=5, sticky="w")

dtFim = DateEntry(root, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
dtFim.grid(row=2, column=1, padx=(50, 0), pady=5, sticky="w")

c1 = Checkbutton(root, text='Gerar documento com linha de produção?',variable=incluirLinhaProducao, onvalue=1, offvalue=0, font=("Arial", 14), height=5, width=5, command=atualizarTabela)
c1.grid(row=3, columnspan=2, padx=(150, 0), pady=2, sticky="nsew")

opcoes = ['Todos os produtos', 'Sal', 'Doces', 'Refeições']
opcaoSelecionada = StringVar()
opcaoSelecionada.set('Todos os produtos')
combo = ttk.Combobox(root, values=opcoes, textvariable=opcaoSelecionada)
combo.grid(row=4, padx=(160, 100), columnspan=2, sticky='nsew')
combo.bind("<<ComboboxSelected>>", selecionarOpcao)

btn_obter_data = Button(root, text="Mostrar lista", bg='#C0C0C0', font=("Arial", 16), command=inserirNaLista)
btn_obter_data.grid(row=5, column=0, columnspan=2, padx=(80, 0), pady=2, sticky='nsew')

txtfiltros = Label(root, text="Selecione os produtos que você deseja filtrar da lista.", font=("Arial", 14))
txtfiltros.grid(row=7, columnspan=2, padx=(150,0), pady=2, sticky="nsew")

c_todos = Checkbutton(root, text='Todos',variable=trazerTodos, onvalue=1, offvalue=0, font=("Arial", 14), height=5, width=5)
c_todos.grid(row=8, column=0, padx=(0,95), pady=0, sticky='e')

c_sal = Checkbutton(root, text='Ref',variable=filtrarRefeicoes, onvalue=1, offvalue=0, font=("Arial", 14), height=5, width=5)
c_sal.grid(row=8, column=0, padx=10, pady=0, sticky='e')

c_doces = Checkbutton(root, text='Doces',variable=filtrarDoces, onvalue=1, offvalue=0, font=("Arial", 14), height=5, width=5)
c_doces.grid(row=8, column=1, padx=(0,0), pady=0, sticky='w')

c_refeicoes = Checkbutton(root, text='Sal',variable=filtrarSal, onvalue=1, offvalue=0, font=("Arial", 14), height=5, width=5)
c_refeicoes.grid(row=8, column=1, padx=(85,0), pady=0, sticky='w')

btn_obter_data = Button(root, text="Gerar Planilhas Excel", bg='#C0C0C0', font=("Arial", 16), command=gerarPlanilha)
btn_obter_data.grid(row=9, column=0, columnspan=2, padx=(80, 0), pady=1, sticky='nsew')

criarTabela()
root.mainloop()


