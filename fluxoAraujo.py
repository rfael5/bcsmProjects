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
        SELECT D.IDX_ENTIDADE AS ID, D.NOME AS Nome, M.DESCRICAO AS Produto, C.FANTASIA AS Unidade, D.CNPJCPF AS CNPJ, D.DATA AS Data, D.TOTALDOCTO AS totalDocumento, M.L_QUANTIDADE AS qtdProduto, M.L_PRECOVENDA AS precoUnitario, M.L_PRECOTOTAL AS precoTotal FROM TPADOCTOPED AS D
            INNER JOIN TPAMOVTOPED AS M ON PK_DOCTOPED = RDX_DOCTOPED
            INNER JOIN TPACADASTRO AS C ON D.IDX_ENTIDADE = PK_CADASTRO 
        WHERE DTEVENTO BETWEEN '{data_inicio}' AND '{data_fim}' 
            AND D.NOME IN ('Drogaria Araujo SA', 'Drogaria Araujo Sa')
        ORDER BY D.DATA
    """
    
    pedidos = receberDados(query)
    return pedidos

def buscarTotalLojas(data_inicio, data_fim):
    query = f"""
        SELECT D.IDX_ENTIDADE AS ID, D.NOME AS Nome, C.FANTASIA AS Unidade, D.CNPJCPF AS CNPJ, SUM(D.TOTALDOCTO) AS totalPedidos FROM TPADOCTOPED AS D
            INNER JOIN TPACADASTRO AS C ON D.IDX_ENTIDADE = PK_CADASTRO 
        WHERE DTEVENTO BETWEEN '{data_inicio}' AND '{data_fim}'  
            AND D.NOME IN ('Drogaria Araujo SA', 'Drogaria Araujo Sa')
        GROUP BY D.IDX_ENTIDADE, D.NOME, C.FANTASIA, D.CNPJCPF
        ORDER BY C.FANTASIA DESC
    """
    
    lojas = receberDados(query)
    return lojas

def criarTabela():
    global table 
    table = ttk.Treeview(secondFrame, columns = ('ID', 'Unidade', 'CNPJ', 'Total'), show = 'headings')
    table.heading('ID', text = 'ID')
    table.heading('Unidade', text = 'Unidade')
    table.heading('CNPJ', text = 'CNPJ')
    table.heading('Total', text = 'Total')
    table.grid(row=4, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

    table.column('ID', width=80, anchor=CENTER)
    table.column('Unidade', width=300, anchor=CENTER)
    table.column('CNPJ', width=160, anchor=CENTER)
    table.column('Total', width=100, anchor=CENTER)


def atualizarTabela():
    global table
    table = ttk.Treeview(secondFrame, columns = ('ID', 'Unidade', 'CNPJ', 'Total'), show = 'headings')
    table.heading('ID', text = 'ID')
    table.heading('Unidade', text = 'Unidade')
    table.heading('CNPJ', text = 'CNPJ')
    table.heading('Total', text = 'Total')
    table.grid(row=4, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

    table.column('ID', width=80, anchor=CENTER)
    table.column('Unidade', width=300, anchor=CENTER)
    table.column('CNPJ', width=160, anchor=CENTER)
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
    return lojas

def inserirNaLista():
    lojas = setarData()
    for loja in lojas:
        id = loja['ID']
        unidade = loja['Unidade']
        cnpj = loja ['CNPJ']
        total = loja['totalPedidos']
        data = (id, unidade, cnpj, total)
        table.insert(parent='', index=0, values=data)

teste = buscarTotalLojas('20230101', '20240101')
for x in teste:
    print(x)

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
btn_obter_data.grid(row=5, column=0, columnspan=2, padx=(80, 0), pady=1, sticky='nsew')

criarTabela()
root.mainloop()