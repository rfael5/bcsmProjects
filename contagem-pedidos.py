from datetime import datetime, timezone
from sqlalchemy import create_engine
import pandas as pd
import json

from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import messagebox

# conexao = (
#     "mssql+pyodbc:///?odbc_connect=" + 
#     "DRIVER={ODBC Driver 17 for SQL Server};" +
#     "SERVER=192.168.1.43;" +
#     "DATABASE=SOUTTOMAYOR;" +
#     "UID=Sa;" +
#     "PWD=P@ssw0rd2023@#$"
# )

conexao = (
    "mssql+pyodbc:///?odbc_connect=" + 
    "DRIVER={ODBC Driver 17 for SQL Server};" +
    "SERVER=localhost;" +
    "DATABASE=SOUTTOMAYOR;" +
    "UID=Sa;" +
    "PWD=P@ssw0rd2023"
)

engine = create_engine(conexao, pool_pre_ping=True)

#Formata a data para ser usada na interface
def formatarData(data):
    data_objeto = datetime.strptime(data, '%d/%m/%Y')
    data_formatada = data_objeto.strftime('%Y%m%d')
    return data_formatada

#Executa a query, recebe os dados e converte para json
#Retorna os dados convertidos
def receberDados(query):
    response = pd.read_sql_query(query, engine)
    resultadosJson = response.to_json(orient='records')
    dadosDesserializados = json.loads(resultadosJson)
    return dadosDesserializados


#Query que busca as compras dos clientes
def executarQuery(dt_inicio, dt_fim):
    query_pedidos = f"""
    SELECT CAST(D.IDX_ENTIDADE AS INTEGER) AS IDX_ENTIDADE, D.NOME, D.CNPJCPF, C.PESSOAFJ, 
    D.TPDOCTO, COUNT(D.CNPJCPF) AS QTDPEDIDOS, SUM(D.TOTALDOCTO) AS TOTAL_VENDAS
    FROM TPADOCTOPED AS D
        INNER JOIN TPACADASTRO AS C ON D.IDX_ENTIDADE = C.PK_CADASTRO
        INNER JOIN TPAFUNCIONARIO AS F ON D.IDX_VENDEDOR1 = F.PK_FUNCIONARIO
    WHERE DATA BETWEEN '{dt_inicio}' AND '{dt_fim}'
        AND TPDOCTO IN ('OR', 'EC')
        AND SITUACAO IN ('V', 'B', 'Z')
    GROUP BY D.NOME, D.CNPJCPF, C.PESSOAFJ, D.TPDOCTO, F.NOME, D.IDX_ENTIDADE
    ORDER BY QTDPEDIDOS
    """
    
    res = receberDados(query_pedidos)

    return res

def queryVerTodasCompras(dt_inicio, dt_fim):
    query = f"""
        SELECT D.PK_DOCTOPED, D.IDX_ENTIDADE, D.NOME, D.CNPJCPF, 
        C.PESSOAFJ, D.TPDOCTO, D.DATA, D.TOTALDOCTO FROM TPADOCTOPED AS D
            INNER JOIN TPACADASTRO AS C ON D.IDX_ENTIDADE = C.PK_CADASTRO
            INNER JOIN TPAFUNCIONARIO AS F ON D.IDX_VENDEDOR1 = F.PK_FUNCIONARIO
        WHERE DATA BETWEEN '{dt_inicio}' AND '{dt_fim}'
            AND TPDOCTO IN ('OR', 'EC')
            AND SITUACAO IN ('V', 'B', 'Z')
    """
    
    res = receberDados(query)
    return res
    

#Executa a query usando as datas definidas na interface
def buscarPedidos(dt_inicio, dt_fim):
    dtInicioFormatada = formatarData(dt_inicio)
    dtFimFormatada = formatarData(dt_fim)
    
    lista_pedidos = executarQuery(dtInicioFormatada, dtFimFormatada)
    lista_agrupada = somarPedidos(lista_pedidos)
    return lista_agrupada

def somarPedidos(lista):
    df = pd.DataFrame(lista)
    response = df.groupby(['IDX_ENTIDADE', 'NOME', 'CNPJCPF', 'PESSOAFJ', 'TPDOCTO'])[['QTDPEDIDOS', 'TOTAL_VENDAS']].sum().reset_index()
    resultadosJson = response.to_json(orient='records')
    dados_desserializados = json.loads(resultadosJson)
    dados_ordenados = sorted(dados_desserializados, key=lambda p:p['QTDPEDIDOS'])
    return dados_ordenados


#Insere os dados na interface criada
def inserirNaLista():
    pedidos = selecionarOpcao(Event)
    table.delete(*table.get_children())
    for pedido in pedidos:
        id = pedido['IDX_ENTIDADE']
        nome = pedido['NOME']
        cpf_cnpj = pedido['CNPJCPF']
        if pedido['PESSOAFJ'] == 'F':
            tipo_cliente = 'CPF'
        else:
            tipo_cliente = 'CNPJ'
        tipo_encomenda = pedido['TPDOCTO']
        qtd_pedidos = pedido['QTDPEDIDOS']
        total_vendas = pedido['TOTAL_VENDAS']
        data = (id, nome, cpf_cnpj, tipo_cliente, tipo_encomenda, qtd_pedidos, total_vendas)
        table.insert(parent='', index=0, values=data)



def criarTabela(frame):
    global table 
    table = ttk.Treeview(frame, columns = ('ID_CLIENTE','NOME', 'CNPJCPF', 'PESSOAFJ', 'TPDOCTO', 'QTDPEDIDOS', 'TOTAL_COMPRAS'), show = 'headings')
    table.heading('ID_CLIENTE', text = 'ID_CLIENTE')
    table.heading('NOME', text = 'NOME')
    table.heading('CNPJCPF', text = 'CNPJCPF')
    table.heading('PESSOAFJ', text = 'PESSOAFJ')
    table.heading('TPDOCTO', text = 'TPDOCTO')
    table.heading('QTDPEDIDOS', text = 'QTDPEDIDOS')
    table.heading('TOTAL_COMPRAS', text = 'TOTAL_COMPRAS')
    table.grid(row=12, column=0, columnspan=3, padx=(80, 0), pady=10, sticky="nsew")

    table.column('ID_CLIENTE', width=60, anchor=CENTER)
    table.column('NOME', width=200, anchor=CENTER)
    table.column('CNPJCPF', width=95, anchor=CENTER)
    table.column('PESSOAFJ', width=60, anchor=CENTER)
    table.column('TPDOCTO', width=60, anchor=CENTER)
    table.column('QTDPEDIDOS', width=85, anchor=CENTER)
    table.column('TOTAL_COMPRAS', width=85, anchor=CENTER)

def criarTabelaIndividual(frame):
    global tbl_individuais
    tbl_individuais = ttk.Treeview(frame, columns = ('ID_PEDIDO', 'CLIENTE', 'TIPO', 'DATA', 'VALOR_VENDA'), show = 'headings')
    tbl_individuais.heading('ID_PEDIDO', text = 'ID_PEDIDO')
    tbl_individuais.heading('CLIENTE', text = 'CLIENTE')
    tbl_individuais.heading('TIPO', text = 'TIPO')
    tbl_individuais.heading('DATA', text = 'DATA')
    tbl_individuais.heading('VALOR_VENDA', text = 'VALOR_VENDA')
    tbl_individuais.grid(row=1, column=0, columnspan=3, padx=(80, 0), pady=10, sticky="nsew")
    
    tbl_individuais.column('ID_PEDIDO', width=80, anchor=CENTER)
    tbl_individuais.column('CLIENTE', width=260, anchor=CENTER)
    tbl_individuais.column('TIPO', width=120, anchor=CENTER)
    tbl_individuais.column('DATA', width=100, anchor=CENTER)
    tbl_individuais.column('VALOR_VENDA', width=100, anchor=CENTER)

def filtrarListas(cnpjcpf, tpdocto):
    _listaPedidos = obter_lista_pedidos()
    if _listaPedidos == None:
        return None
    elif _listaPedidos == 0:
        return 0
    else:
        listaFiltrada = list(filter(lambda pedido:pedido['PESSOAFJ'] == cnpjcpf and pedido['TPDOCTO'] == tpdocto, _listaPedidos))

    return listaFiltrada

def selecionarOpcao(event):
    #opcoes = ['Encomendas CPF', 'Encomendas CNPJ', 'Orçamentos CPF', 'Orçamentos CNPJ']
    
    valor_selecionado = combo.get()
    if valor_selecionado == 'Encomendas CPF':
        lista_filtrada = filtrarListas('F', 'EC')
    elif valor_selecionado == 'Encomendas CNPJ':
        lista_filtrada = filtrarListas('J', 'EC')
    elif valor_selecionado == 'Orçamentos CPF':
        lista_filtrada = filtrarListas('F', 'OR')
    elif valor_selecionado == 'Orçamentos CNPJ':
        lista_filtrada = filtrarListas('J', 'OR')
    
    return lista_filtrada
    #table.delete()
        

def verComprasIndividuais():
    dt_inicio = dtInicio.get()
    dt_fim = dtFim.get()
    dt_inicio_formatada = formatarData(dt_inicio)
    dt_fim_formatada = formatarData(dt_fim)
    indice = table.selection()
    if indice:
        id_cliente = table.item(indice)['values'][0]
        todos_pedidos = queryVerTodasCompras(dt_inicio_formatada, dt_fim_formatada)
        for x in todos_pedidos:
            if 'Bac Veiculos Ltda' in x['NOME']:
                print(x)
        pedidos_filtrados = list(filter(lambda p:int(p['IDX_ENTIDADE']) == id_cliente, todos_pedidos))
        abrirJanelaIndividual(pedidos_filtrados)


def abrirJanelaIndividual(pedidos_filtrados):
    janela = Toplevel(root)
    janela.title("Quantidade ano anterior")
    janela.geometry("1250x400")
    criarTabelaIndividual(janela)
    for pedido in pedidos_filtrados:
        id_pedido = pedido['PK_DOCTOPED']
        nome = pedido['NOME']
        if pedido['TPDOCTO'] == 'EC':
            tipo = 'Encomenda'
        else:
            tipo = 'Orçamento'
        data_pedido = formatarDataPedido(pedido['DATA'])
        valor_venda = pedido['TOTALDOCTO']
        dados = (id_pedido, nome, tipo, data_pedido, valor_venda)
        tbl_individuais.insert(parent='', index=0, values=dados)

def criar_interface():
    global root
    root = Tk()
    root.title("Gerar pedidos de suprimento")
    root.geometry("1150x800")

    # Cria os widgets
    explicacao = Label(root, text="Selecione abaixo o período de tempo para o qual você quer gerar a lista de\n clientes mais recentes.", font=("Arial", 14))
    explicacao.grid(row=0, columnspan=2, padx=(150, 0), pady=10, sticky="nsew")

    lbl_dtInicio = Label(root, text="De:", font=("Arial", 14))
    lbl_dtInicio.grid(row=1, padx=(0, 190), column=0, sticky="e")

    global dtInicio
    dtInicio = DateEntry(root, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
    dtInicio.grid(row=2, column=0, padx=(150, 0), pady=5, sticky="e")

    lbl_dtFim = Label(root, text="Até:", font=("Arial", 14))
    lbl_dtFim.grid(row=1, column=1, padx=(50, 0), pady=5, sticky="w")

    global dtFim
    dtFim = DateEntry(root, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
    dtFim.grid(row=2, column=1, padx=(50, 0), pady=5, sticky="w")
    
    titulo_ec = Label(root, text='Quantidade EC', font=("Arial", 18))
    titulo_ec.grid(row=4, column=0)
    
    #EC UNICOS CPF
    global qtd_ec_unicos_cpf
    qtd_ec_unicos_cpf = Label(root, text="Pedidos unicos CPF: 0", font=("Arial", 16))
    qtd_ec_unicos_cpf.grid(row=5, column=0)
    
    #EC UNICOS CNPJ
    global qtd_ec_unicos_cnpj
    qtd_ec_unicos_cnpj = Label(root, text="Pedidos unicos CNPJ: 0", font=("Arial", 16))
    qtd_ec_unicos_cnpj.grid(row=5, column=1)
    
    #EC MULTIPLOS CPF
    global qtd_ec_multiplos_cpf
    qtd_ec_multiplos_cpf = Label(root, text="Pedidos multiplos CPF: 0", font=("Arial", 16))
    qtd_ec_multiplos_cpf.grid(row=6, column=0)
    
    #EC MULTIPLOS CNPJ
    global qtd_ec_multiplos_cnpj
    qtd_ec_multiplos_cnpj = Label(root, text="Pedidos multiplos CNPJ: 0", font=("Arial", 16))
    qtd_ec_multiplos_cnpj.grid(row=6, column=1)
    
    titulo_or = Label(root, text='Quantidade OR', font=("Arial", 18))
    titulo_or.grid(row=7, column=0)
    
    #OR UNICOS CPF
    global qtd_or_unicos_cpf
    qtd_or_unicos_cpf = Label(root, text="Pedidos unicos CPF: 0", font=("Arial", 16))
    qtd_or_unicos_cpf.grid(row=8, column=0)
    
    #OR UNICOS CNPJ
    global qtd_or_unicos_cnpj
    qtd_or_unicos_cnpj = Label(root, text="Pedidos unicos CNPJ: 0", font=("Arial", 16))
    qtd_or_unicos_cnpj.grid(row=8, column=1)
    
    #OR MULTIPLOS CPF
    global qtd_or_multiplos_cpf
    qtd_or_multiplos_cpf = Label(root, text="Pedidos multiplos CPF: 0", font=("Arial", 16))
    qtd_or_multiplos_cpf.grid(row=9, column=0)    
    
    #OR MULTIPOS CNPJ
    global qtd_or_multiplos_cnpj
    qtd_or_multiplos_cnpj = Label(root, text="Pedidos unicos CNPJ: 0", font=("Arial", 16))
    qtd_or_multiplos_cnpj.grid(row=9, column=1)
    
    opcoes = ['Encomendas CPF', 'Encomendas CNPJ', 'Orçamentos CPF', 'Orçamentos CNPJ']
    opcaoSelecionada = StringVar()
    opcaoSelecionada.set('Encomendas CPF')
    global combo
    combo = ttk.Combobox(root, values=opcoes, textvariable=opcaoSelecionada)
    combo.grid(row=10, padx=(160, 100), columnspan=2, sticky='nsew')
    combo.bind("<<ComboboxSelected>>", selecionarOpcao)
    
    btn_obter_data = Button(root, text="Mostrar lista", bg='#C0C0C0', font=("Arial", 16), command=inserirNaLista)
    btn_obter_data.grid(row=11, column=0, columnspan=2, padx=(80, 0), pady=2, sticky='nsew')
    
    #TABELA - ROW 12
    
    btn_ver_compras = Button(root, text="Ver compras individuais", bg='#C0C0C0', font=("Arial", 16), command=verComprasIndividuais)
    btn_ver_compras.grid(row=13, column=0, columnspan=2, padx=(80, 0), pady=2, sticky='nsew')

    criarTabela(root)
    # Inicia o loop principal da janela
    root.mainloop()

def formatarDataPedido(data):
    milliseconds_since_epoch = data
    seconds_since_epoch = milliseconds_since_epoch / 1000
    date_object = datetime.fromtimestamp(seconds_since_epoch, timezone.utc)
    formatted_date = date_object.strftime('%d/%m/%Y')
    return formatted_date 


def obter_lista_pedidos():
    dataInicio = dtInicio.get()
    dataFim = dtFim.get()
    pedidos = buscarPedidos(dataInicio, dataFim)

    return pedidos

criar_interface()

#Filtra os dados na lista dependendo se o cliente é pessoa física
#ou juridica, se é orçamento ou encomenda, e se o cliente comprou
#com a BCSM uma vez ou mais. Em seguida, insere esses dados na 
#interface.
# def obter_lista_pedidos():
#     dataInicio = dtInicio.get()
#     dataFim = dtFim.get()
#     pedidos = buscarPedidos(dataInicio, dataFim)
#     inserirNaLista(pedidos)

#     #EC - CPF - SOMENTE UM PEDIDO
#     ec_unico_cpf = list(filter(lambda pedido: pedido['QTDPEDIDOS'] == 1 
#                                and pedido['PESSOAFJ'] == 'F' 
#                                and pedido['TPDOCTO'] == 'EC', pedidos))
#     encomendas_cpf_unicos = len(ec_unico_cpf)
#     #EC - CPF - MAIS DE UM PEDIDO
#     ec_multiplos_cpf = list(filter(lambda pedido: pedido['QTDPEDIDOS'] > 1
#                                 and pedido['PESSOAFJ'] == 'F'
#                                 and pedido['TPDOCTO'] == 'EC', pedidos))
#     encomendas_cpf_multiplos = len(ec_multiplos_cpf)
#     #EC - CNPJ - SOMENTE UM PEDIDO
#     ec_unico_cnpj = list(filter(lambda pedido: pedido['QTDPEDIDOS'] == 1
#                                 and pedido['PESSOAFJ'] == 'J'
#                                 and pedido['TPDOCTO'] == 'EC', pedidos))
#     encomendas_cnpj_unicos = len(ec_unico_cnpj)
#     #EC - CNPJ - MAIS DE UM PEDIDO
#     ec_multiplos_cnpj = list(filter(lambda pedido: pedido['QTDPEDIDOS'] > 1
#                                     and pedido['PESSOAFJ'] == 'J'
#                                     and pedido['TPDOCTO'] == 'EC', pedidos))
#     encomendas_cnpj_multiplos = len(ec_multiplos_cnpj)    
#     #OR - CPF - SOMENTE UM PEDIDO
#     or_unico_cpf = list(filter(lambda pedido:pedido['QTDPEDIDOS'] == 1
#                                    and pedido['PESSOAFJ'] == 'F'
#                                    and pedido['TPDOCTO'] == 'OR', pedidos))
#     orcamentos_cpf_unicos = len(or_unico_cpf) 
    
#     #OR - CPF - MAIS DE UM PEDIDO
#     or_multiplos_cpf = list(filter(lambda pedido:pedido['QTDPEDIDOS'] > 1
#                                    and pedido['PESSOAFJ'] == 'F'
#                                    and pedido['TPDOCTO'] == 'OR', pedidos))
#     orcamentos_cpf_multiplos = len(or_multiplos_cpf)
    
#     #OR - CNPJ - SOMENTE UM PEDIDO
#     or_unico_cnpj = list(filter(lambda pedido:pedido['QTDPEDIDOS'] == 1
#                                    and pedido['PESSOAFJ'] == 'J'
#                                    and pedido['TPDOCTO'] == 'OR', pedidos))
#     orcamentos_cnpj_unicos = len(or_unico_cnpj)
    
#     #OR - CNPJ - MAIS DE UM PEDIDO
#     or_multiplos_cnpj = list(filter(lambda pedido:pedido['QTDPEDIDOS'] > 1
#                                    and pedido['PESSOAFJ'] == 'J'
#                                    and pedido['TPDOCTO'] == 'OR', pedidos))
#     orcamentos_cnpj_multiplos = len(or_multiplos_cnpj)

#     qtd_ec_unicos_cpf.configure(text=f'Pedidos unicos CPF: {encomendas_cpf_unicos}')
#     qtd_ec_multiplos_cpf.configure(text=f'Pedidos multiplos CPF: {encomendas_cpf_multiplos}')
#     qtd_ec_unicos_cnpj.configure(text=f'Pedidos unicos CNPJ: {encomendas_cnpj_unicos}')
#     qtd_ec_multiplos_cnpj.configure(text=f'Pedidos multiplos CNPJ: {encomendas_cnpj_multiplos}')
#     qtd_or_unicos_cpf.configure(text=f'Pedidos unicos CPF: {orcamentos_cpf_unicos}')
#     qtd_or_multiplos_cpf.configure(text=f'Pedidos multiplos CPF: {orcamentos_cpf_multiplos}')
#     qtd_or_unicos_cnpj.configure(text=f'Pedidos unicos CNPJ: {orcamentos_cnpj_unicos}')
#     qtd_or_multiplos_cnpj.configure(text=f'Pedidos multiplos CNPJ: {orcamentos_cnpj_multiplos}')

# Cria a interface

