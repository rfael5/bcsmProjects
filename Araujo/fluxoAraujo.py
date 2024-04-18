from tkinter import filedialog
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
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

def receberDados(query):
    response = pd.read_sql_query(query, engine)
    resultadosJson = response.to_json(orient='records')
    dadosDesserializados = json.loads(resultadosJson)
    return dadosDesserializados

def buscarPedidosProdutos(data_inicio, data_fim):
    query = f"""
        SELECT D.IDX_ENTIDADE AS ID, M.PK_MOVTOEST AS idPedido, D.NOME AS Nome, M.IDX_PRODUTO AS idProduto, M.DESCRICAO AS Produto, C.FANTASIA AS Unidade, D.TPENTIDADE AS tipoOperacao, 
        D.CNPJCPF AS CNPJ, D.TOTALDOCTO AS totalDocumento, M.L_QUANTIDADE AS qtdProduto, 
        M.L_PRECOVENDA AS precoUnitario, M.L_PRECOTOTAL AS precoTotal, D.PRODVALOR AS totalCompra FROM TPADOCTOEST AS D
            INNER JOIN TPAMOVTOEST AS M ON PK_DOCTOEST = RDX_DOCTOEST
            INNER JOIN TPACADASTRO AS C ON D.IDX_ENTIDADE = PK_CADASTRO 
        WHERE DTEVENTO BETWEEN '{data_inicio}' AND '{data_fim}' 
            AND D.NOME IN ('Drogaria Araujo SA', 'Drogaria Araujo Sa')
            AND D.TPENTIDADE = 'C'

        UNION

        SELECT D.IDX_ENTIDADE AS ID, M.PK_MOVTOEST AS idPedido, D.NOME AS Nome, M.IDX_PRODUTO AS idProduto, M.DESCRICAO AS Produto, C.FANTASIA AS Unidade, D.TPENTIDADE AS tipoOperacao, 
        D.CNPJCPF AS CNPJ, D.TOTALDOCTO AS totalDocumento, M.L_QUANTIDADE AS qtdProduto, 
        M.L_PRECOVENDA AS precoUnitario, M.L_PRECOTOTAL AS precoTotal, D.PRODVALOR AS totalCompra FROM TPADOCTOEST AS D
            INNER JOIN TPAMOVTOEST AS M ON PK_DOCTOEST = RDX_DOCTOEST
            INNER JOIN TPACADASTRO AS C ON D.IDX_ENTIDADE = PK_CADASTRO 
        WHERE DTEVENTO BETWEEN '{data_inicio}' AND '{data_fim}' 
            AND D.NOME IN ('Drogaria Araujo SA', 'Drogaria Araujo Sa')
            AND D.TPENTIDADE = 'F'
        ORDER BY M.DESCRICAO
    """
    
    pedidos = receberDados(query)
    return pedidos

def buscarTotalLojas(data_inicio, data_fim):
    query = f"""
        SELECT D.IDX_ENTIDADE AS ID, D.NOME AS Nome, C.FANTASIA AS Unidade, D.TPENTIDADE AS tipoOperacao, D.CNPJCPF AS CNPJ, SUM(D.TOTALDOCTO) AS totalPedidos, SUM(D.PRODVALOR) AS totalOperacao FROM TPADOCTOEST AS D
            INNER JOIN TPACADASTRO AS C ON D.IDX_ENTIDADE = PK_CADASTRO 
        WHERE DTEVENTO BETWEEN '{data_inicio}' AND '{data_fim}'  
            AND D.NOME IN ('Drogaria Araujo SA', 'Drogaria Araujo Sa')
            AND D.TPENTIDADE = 'C'
        GROUP BY D.IDX_ENTIDADE, D.NOME, C.FANTASIA, D.CNPJCPF, D.TPENTIDADE

        UNION

        SELECT D.IDX_ENTIDADE AS ID, D.NOME AS Nome, C.FANTASIA AS Unidade, D.TPENTIDADE AS tipoOperacao, D.CNPJCPF AS CNPJ, SUM(D.TOTALDOCTO) AS totalPedidos, SUM(D.PRODVALOR) AS totalOperacao FROM TPADOCTOEST AS D
            INNER JOIN TPACADASTRO AS C ON D.IDX_ENTIDADE = PK_CADASTRO 
        WHERE DTEVENTO BETWEEN '{data_inicio}' AND '{data_fim}'  
            AND D.NOME IN ('Drogaria Araujo SA', 'Drogaria Araujo Sa')
            AND D.TPENTIDADE = 'F'
        GROUP BY D.IDX_ENTIDADE, D.NOME, C.FANTASIA, D.CNPJCPF, D.TPENTIDADE
        ORDER BY C.FANTASIA DESC
    """
    
    lojas = receberDados(query)
    return lojas

def criarTabela():
    global table 
    table = ttk.Treeview(secondFrame, columns = ('ID', 'Nome', 'Unidade', 'CNPJ', 'Compra', 'Venda', 'Total'), show = 'headings')
    table.heading('ID', text = 'ID')
    table.heading('Nome', text = 'Nome')
    table.heading('Unidade', text = 'Unidade')
    table.heading('CNPJ', text = 'CNPJ')
    table.heading('Compra', text = 'Compra')
    table.heading('Venda', text = 'Venda')
    table.heading('Total', text = 'Total')
    table.grid(row=4, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

    table.column('ID', width=80, anchor=CENTER)
    table.column('Nome', width=80, anchor=CENTER)
    table.column('Unidade', width=300, anchor=CENTER)
    table.column('CNPJ', width=160, anchor=CENTER)
    table.column('Compra', width=100, anchor=CENTER)
    table.column('Venda', width=100, anchor=CENTER)
    table.column('Total', width=100, anchor=CENTER)
    
def criarTabelaProduto():
    global tableProduto 
    tableProduto = ttk.Treeview(secondFrame, columns = ('ID', 'Nome', 'Un Compradas', 'Un Vendidas', 'Total Unidades', 'Compra', 'Venda', 'Total'), show = 'headings')
    tableProduto.heading('ID', text = 'ID')
    tableProduto.heading('Nome', text = 'Nome')
    tableProduto.heading('Un Compradas', text = 'Un Compradas')
    tableProduto.heading('Un Vendidas', text = 'Un Vendidas')
    tableProduto.heading('Total Unidades', text = 'Total Unidades')
    tableProduto.heading('Compra', text = 'Compra')
    tableProduto.heading('Venda', text = 'Venda')
    tableProduto.heading('Total', text = 'Total')
    tableProduto.grid(row=6, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

    tableProduto.column('ID', width=80, anchor=CENTER)
    tableProduto.column('Nome', width=80, anchor=CENTER)
    tableProduto.column('Un Compradas', width=80, anchor=CENTER)
    tableProduto.column('Un Vendidas', width=80, anchor=CENTER)
    tableProduto.column('Total Unidades', width=80, anchor=CENTER)
    tableProduto.column('Compra', width=80, anchor=CENTER)
    tableProduto.column('Venda', width=80, anchor=CENTER)
    tableProduto.column('Total', width=80, anchor=CENTER)


def atualizarTabela():
    global table
    
    table = ttk.Treeview(secondFrame, columns = ('ID', 'Nome', 'Unidade', 'CNPJ', 'Valor Compra', 'Valor Venda', 'Total'), show = 'headings')
    table.heading('ID', text = 'ID')
    table.heading('Nome', text = 'Nome')
    table.heading('Unidade', text = 'Unidade')
    table.heading('CNPJ', text = 'CNPJ')
    table.heading('Compra', text = 'Compra')
    table.heading('Venda', text = 'Venda')
    table.heading('Total', text = 'Total')
    table.grid(row=4, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

    table.column('ID', width=80, anchor=CENTER)
    table.column('Nome', width=80, anchor=CENTER)
    table.column('Unidade', width=300, anchor=CENTER)
    table.column('CNPJ', width=160, anchor=CENTER)
    table.column('Compra', width=100, anchor=CENTER)
    table.column('Venda', width=100, anchor=CENTER)
    table.column('Total', width=100, anchor=CENTER)

def formatarData(data):
    data_objeto = datetime.strptime(data, '%d/%m/%Y')
    data_formatada = data_objeto.strftime('%Y%m%d')
    return data_formatada


def setarData():
    dataInicio = dtInicio.get()
    dtInicioFormatada = formatarData(dataInicio)
    dataFim = dtFim.get()
    dtFimFormatada = formatarData(dataFim)
    
    lojas = buscarTotalLojas(dtInicioFormatada, dtFimFormatada)
    if len(lojas) <= 0:
        print('Não houveram pedidos nesse periodo')
        messagebox.showinfo('Lista vazia', 'Não houve transações nesse periodo de tempo.')
        return []
    else:
        lojas_formatadas = criarListaLojas(lojas)
        return lojas_formatadas

def setarDataProd():
    dataInicio = dtInicio.get()
    dtInicioFormatada = formatarData(dataInicio)
    dataFim = dtFim.get()
    dtFimFormatada = formatarData(dataFim)
    Produtos = buscarPedidosProdutos(dtInicioFormatada, dtFimFormatada)
    produtos_formatados = criarListaProdutos(Produtos)
    return produtos_formatados

def unirCompraVenda(row, copia_lista):
    for produto in copia_lista:
        if row['ID'] == produto['ID'] and row['idProduto'] == produto['idProduto'] and row['idPedido'] == produto['idPedido']:
            if row['tipoOperacao'] == 'C':
                produto['qtdVenda'] = row['qtdProduto']
                produto['valorVenda'] = row['precoTotal']
            elif row['tipoOperacao'] == 'F':
                produto['qtdCompra'] = row['qtdProduto']
                produto['valorCompra'] = row['precoTotal']
    return copia_lista


def unirFluxoUnidades(row, copia_lista):
    for unidade in copia_lista:
        if row['ID'] == unidade['ID'] and row['tipoOperacao'] == 'C':
            unidade['totalVenda'] = row['totalOperacao']
        elif row['ID'] == unidade['ID'] and row['tipoOperacao'] == 'F':
                unidade['totalCompra'] = row['totalOperacao']
    return copia_lista

def diferencaCompraVenda(row):
    resultado = row['valorVenda'] - row['valorCompra']
    return resultado

def criarListaLojas(lista_lojas):
    copia_lista = lista_lojas
    df = pd.DataFrame(lista_lojas)
    result = df.apply(unirFluxoUnidades, copia_lista=copia_lista, axis=1)
    r_json = converterPJson(result)
    sem_duplicados = deletarDuplicados(r_json)
    return sem_duplicados

def deletarDuplicados(lista_unidades):
    df = pd.DataFrame(lista_unidades)
    sem_duplicados = df.drop_duplicates(subset=['ID'])
    resultJson = sem_duplicados.to_json(orient='records')
    dadosDesserializados = json.loads(resultJson)
    return dadosDesserializados

def criarListaProdutos(lista_produtos):
    copia_lista = lista_produtos
    df = pd.DataFrame(lista_produtos)
    result = df.apply(unirCompraVenda, copia_lista=copia_lista, axis=1)
    r_json = converterPJson(result)
    lista_ordenada = ordenarLista(r_json)
    
    return lista_ordenada

def ordenarLista(lista):
    df = pd.DataFrame(lista)
    resultJson = df.to_json(orient='records')
    dadosDesserializados = json.loads(resultJson)
    return dadosDesserializados

def serialize(obj):
    if isinstance(obj, dict):
        return {str(k): v for k, v in obj.items()}
    raise TypeError('Object of type {} is not JSON serializable'.format(type(obj)))

def converterPJson(lista):
    dict_data = json.dumps(lista[0])
    final = json.loads(dict_data)
    
    return final

def inserirNaLista():
    lojas = setarData()
    
    table.delete(*table.get_children())
    for loja in lojas:
        id = loja['ID']
        nome = loja['Nome']
        unidade = loja['Unidade']
        cnpj = loja ['CNPJ']
        if 'totalCompra' in loja:
            compra = loja['totalCompra']
        else:
            compra = 0
        if 'totalVenda' in loja:
            venda = loja['totalVenda']
        else:
            venda = 0
        if venda == None:
            venda = 0
        if compra == None:
            compra = 0
        total = venda - compra
        data = (id, nome, unidade, cnpj, compra, venda, round(total, 2))
        table.insert(parent='', index=0, values=data)

def verificarExistenciaColuna(row):
    if 'qtdCompra' not in row:
        row['qtdCompra'] = 0
    if 'qtdVenda' not in row:
        row['qtdVenda'] = 0
    if 'valorCompra' not in row:
        row['valorCompra'] = 0
    if 'valorVenda' not in row:
        row['valorVenda'] = 0

def checarColunas(lista):
    for produto in lista:
        if 'qtdCompra' not in produto:
            produto['qtdCompra'] = 0
        if 'qtdVenda' not in produto:
            produto['qtdVenda'] = 0
        if 'valorCompra' not in produto:
            produto['valorCompra'] = 0
        if 'valorVenda' not in produto:
            produto['valorVenda'] = 0


def somarVendasProdutos(produtos):
    checarColunas(produtos)
    df = pd.DataFrame(produtos)
    #df = df.apply(verificarExistenciaColuna, axis=1)
    result = df.groupby(['ID', 'CNPJ', 'Produto'])[['qtdCompra', 'qtdVenda', 'valorCompra', 'valorVenda']].sum().reset_index()
    result['resultadoFinal'] = result.apply(diferencaCompraVenda, axis=1) 
    resultJson = result.to_json(orient='records')
    dadosDesserializados = json.loads(resultJson)

    return dadosDesserializados

def inserirNaListaProd(row):
    #inserirNaListaProd(p['ID'], p['Produto'], p['qtdCompra'], p['qtdVenda'], p['valorCompra'], p['valorVenda'], p['resultadoFinal'])
    id = row['ID']
    nome = row['Produto']
    if 'qtdCompra' in row:
        qtdCompra = row['qtdCompra']
    else:
        qtdCompra = 0
    if 'qtdVenda' in row:
        qtdVenda = row['qtdVenda']
    else:
        qtdVenda = 0
    if 'valorCompra' in row:
        compra = row['valorCompra']
    else:
        compra = 0
    if 'valorVenda' in row:
        venda = row['valorVenda']
    else:
        venda = 0
    total = venda - compra
    total_un_vendidas = qtdVenda - qtdCompra
    dataProd = (id, nome, qtdCompra, qtdVenda, total_un_vendidas, compra, venda, round(total, 2))
    tableProduto.insert(parent='', index=0, values=dataProd)
        
def obter_objeto():
    tableProduto.delete(*tableProduto.get_children())
    Produtos = setarDataProd()
    indice = table.selection()
    produtos_somados = somarVendasProdutos(Produtos)
    if indice:
        objeto = table.item(indice)['values'][3]
        objFiltrado = list(filter(lambda produto:str(produto['CNPJ']) == str(objeto), produtos_somados))
        for p in objFiltrado:
            #inserirNaListaProd(p['ID'], p['Produto'], p['qtdCompra'], p['qtdVenda'], p['valorCompra'], p['valorVenda'], p['resultadoFinal'])
            inserirNaListaProd(p)
    else:
        print("Nenhum objeto selecionado.")

root = Tk()
root.title("Gerar pedidos de suprimento")

root.geometry("1150x800")

mainFrame = Frame(root)
mainFrame.pack(fill=BOTH, expand=1)

canvas = Canvas(mainFrame)
canvas.pack(side=LEFT, fill=BOTH, expand=1)
#canvas.grid(row=0, column=0, sticky=EW)

scrollbar = ttk.Scrollbar(mainFrame, orient=VERTICAL, command=canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)
#scrollbar.grid(row=0, rowspan=10, column=1, sticky="ns")

canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e:canvas.configure(scrollregion=canvas.bbox("all")))

secondFrame = Frame(canvas)
canvas.create_window((0, 0), window=secondFrame, anchor="nw")

explicacao = Label(secondFrame, text="Selecione abaixo o período de tempo para o qual você quer gerar a lista de\n pedidos de suprimento.", font=("Arial", 14))
explicacao.grid(row=0, columnspan=2, padx=(150, 0), pady=10, sticky="nsew")

lbl_dtInicio = Label(secondFrame, text="De:", font=("Arial", 14))
lbl_dtInicio.grid(row=1, padx=(0, 190), column=0, sticky="e")

dtInicio = DateEntry(secondFrame, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
dtInicio.grid(row=2, column=0, padx=(150, 0), pady=5, sticky="e")

lbl_dtFim = Label(secondFrame, text="Até:", font=("Arial", 14))
lbl_dtFim.grid(row=1, column=1, padx=(50, 0), pady=5, sticky="w")

dtFim = DateEntry(secondFrame, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
dtFim.grid(row=2, column=1, padx=(50, 0), pady=5, sticky="w")


btn_obter_data = Button(secondFrame, text="Listar resultados", bg='#C0C0C0', font=("Arial", 16), command=inserirNaLista)
btn_obter_data.grid(row=3, column=0, columnspan=2, padx=(80, 0), pady=1, sticky='nsew')


btn_obter_selected = Button(secondFrame, text="Selecionar loja", bg='#C0C0C0', font=("Arial", 16), command=obter_objeto)
btn_obter_selected.grid(row=5, column=0, columnspan=2, padx=(80, 0), pady=1, sticky='nsew')

criarTabela()
criarTabelaProduto()
root.mainloop()