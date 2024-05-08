from tkinter import filedialog
import pandas as pd
import numpy as np
import json
from datetime import datetime, timezone, timedelta
from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import messagebox
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from random import choice

import connection
import formatacao_objeto
import tabelas
import criacao_planilha

def formatarData(data):
    data_objeto = datetime.strptime(data, '%d/%m/%Y')
    data_formatada = data_objeto.strftime('%Y%m%d')
    return data_formatada

def formatarDataPedido(data):
    milliseconds_since_epoch = data
    seconds_since_epoch = milliseconds_since_epoch / 1000
    date_object = datetime.fromtimestamp(seconds_since_epoch, timezone.utc)
    formatted_date = date_object.strftime('%d/%m/%Y')
    return formatted_date 

def setarData(tipo_requisicao):
    dataInicio = dtInicio.get()
    dtInicioFormatada = formatarData(dataInicio)
    dataFim = dtFim.get()
    dtFimFormatada = formatarData(dataFim)
    if dtInicioFormatada < dtFimFormatada:
        global ajustes_periodo
        if tipo_requisicao == 'ano-atual':
            produtosComposicao = connection.getProdutosComposicao(dtInicioFormatada, dtFimFormatada)
            composicaoSemiAcabados = connection.getCompSemiAcabados(dtInicioFormatada, dtFimFormatada)
            ajustes = connection.getAjustes(dtInicioFormatada, dtFimFormatada)
        else:
            n_dt_inicio = int(dtInicioFormatada) - 10000
            n_dt_fim = int(dtFimFormatada) - 10000
            produtosComposicao = connection.getProdutosComposicao(n_dt_inicio, n_dt_fim)
            composicaoSemiAcabados = connection.getCompSemiAcabados(n_dt_inicio, n_dt_fim)
            ajustes = connection.getAjustes(n_dt_inicio, n_dt_fim)

        if len(produtosComposicao) == 0:
            tamanhoLista = 0
            tabelas.criarTabela(secondFrame)
            return tamanhoLista
        else:
            estoque = connection.getEstoque()
            produtosQtdAjustada = formatacao_objeto.calcularQtdProducao(produtosComposicao)
            ajustesAplicados = formatacao_objeto.aplicarAjustes(produtosQtdAjustada, ajustes)
            ajustes_periodo = ajustesAplicados
            # for x in ajustes_periodo:
            #     print(x)
            formatacao_objeto.adicionarEstoque(ajustesAplicados, estoque)
            mp_acabados = formatacao_objeto.somarProdutosEvento(ajustesAplicados, incluirLinhaProducao)
            mp_semiAcabados = criarDictSemiAcabados(mp_acabados, composicaoSemiAcabados, estoque)
            produtos = formatacao_objeto.unirListasComposicao(mp_acabados, mp_semiAcabados, incluirLinhaProducao)
            return produtos 
    else:
        tabelas.criarTabela(secondFrame)
        return None

def formatarDataPedido(data):
    milliseconds_since_epoch = data
    seconds_since_epoch = milliseconds_since_epoch / 1000
    date_object = datetime.fromtimestamp(seconds_since_epoch, timezone.utc)
    formatted_date = date_object.strftime('%d/%m/%Y')
    return formatted_date

def verTodosEventos(lista_produtos, tabela):
    indice = tabela.selection()
    if indice:
        produto = tabela.item(indice)['values'][0]
        produtosFiltrados = list(filter(lambda evento:int(evento['idProdutoComposicao']) == int(produto), lista_produtos))
        abrirOutraJanela(produtosFiltrados)

def verQtdAnoPassado(tabela):
    produtos = setarData('ano-anterior')
    indice = tabela.selection()
    if indice:
        produto = tabela.item(indice)['values'][0]
        produtosFiltrados = list(filter(lambda p:int(p['idProdutoComposicao']) == int(produto), produtos))
        abrirJanelaAnoAnterior(produtosFiltrados)

def abrirJanelaAnoAnterior(produtosFiltrados):
    j_ano_anterior = Toplevel(root)
    j_ano_anterior.title("Quantidade ano anterior")
    j_ano_anterior.geometry("1250x400")
    tabelas.criarTabelaMesAnterior(j_ano_anterior)
    for x in produtosFiltrados:
        id = x['idProdutoComposicao']
        produto = x['nomeProdutoComposicao']
        total = x['totalProducao']
        unidade = x['unidade']
        data = (id, produto, total, unidade)
        tabelas.tbl_ano_anterior.insert(parent='', index=0, values=data)
    

def abrirOutraJanela(produtosFiltrados):
    nova_janela = Toplevel(root)  # Cria uma nova janela
    nova_janela.title("Nova Janela")
    nova_janela.geometry("950x400")
    produto_selecionado = produtosFiltrados[0]['nomeProdutoComposicao']
    # Adicione widgets ou conteúdo à nova janela aqui
    label = Label(nova_janela, text=f'{produto_selecionado}')
    label.grid(padx=20, pady=20)

    tabelas.criarTabelaEvento(nova_janela)
    for x in produtosFiltrados:
        cliente = x['nomeEvento']
        produto = x['nomeProdutoAcabado']
        dataPedido = formatarDataPedido(x['dataPedido'])
        dataPrevisao = formatarDataPedido(x['dataPrevisao'])
        qtdEvento = x['qtdProdutoEvento']
        unidade = x['unidadeAcabado']
        data = (cliente, produto, dataPedido, dataPrevisao, qtdEvento, unidade)
        tabelas.tabelaEventos.insert(parent='', index=0, values=data)


def formatarListaSemiAcabados(lista, estoque):
    formatacao_objeto.adicionarEstoque(lista, estoque)
    df = pd.DataFrame(lista)
    df['produtoAcabado'] = False
    df['unidade'] = df['unidadeComposicao'].apply(formatacao_objeto.alterarStringUnidade)
    df['nomeProdutoComposicao'] = df['nomeProdutoComposicao']. apply(formatacao_objeto.alterarStringUnidade)
    df['unidadeEstoque'] = df['unidadeEstoque'].apply(formatacao_objeto.alterarStringUnidade)
    df['totalProducao'] = df.apply(formatacao_objeto.converterKg, axis=1)
    df['unidade'] = df['unidade'].apply(formatacao_objeto.mudarUnidade)
    
    df = df[['idProdutoComposicao', 'nomeProdutoComposicao', 'negocio', 'classificacao', 'estoque', 'unidadeEstoque', 'totalProducao', 'unidade', 'produtoAcabado']]
    
    result = formatacao_objeto.converterPJson(df)
    return result

def criarDictSemiAcabados(acabados, semiAcabados, estoque):
    dfAcabados = pd.DataFrame(acabados)

    result = dfAcabados.apply(formatacao_objeto.inserirCol_SemiAcabados, semiAcabados=semiAcabados, incluirLinhaProducao=incluirLinhaProducao, axis=1)

    resultJson = result.to_json(orient='records')
    dadosDesserializados = json.loads(resultJson)
    
    listaFinal = [p for p in dadosDesserializados if p]
    concatenacao = np.concatenate(listaFinal)
    listaJson = concatenacao.tolist()
    listaFormatada = formatarListaSemiAcabados(listaJson, estoque)
    return listaFormatada

######## SELECIONAR CLASSIFICAÇÃO PRODUTO RAPHAEL 08/05/2024 ########

def filtrarListas(tipoFiltro, listaCompleta):
    if listaCompleta == None:
        return None
    elif listaCompleta == 0:
        return 0
    else:
        listaFiltrada = list(filter(lambda produto:produto['IDX_CLASSIFICACAO'] == tipoFiltro 
                                    or tipoFiltro in produto['IDX_CLASSIFICACAO'], listaCompleta))
        return listaFiltrada

######## ######## ######## ################ ################ ########

def inserirNaLista():
    produtos = setarData('ano-atual')
    valorSelecionado = combo.get()
    
    
    if produtos == None:
        messagebox.showinfo('Data inválida', 'Periodo selecionado inválido')
    elif produtos == 0:
        messagebox.showinfo('Lista vazia', 'Não há eventos nesse período de tempo')    
    else:
        if valorSelecionado == 'Todos os produtos':
            return produtos
        else:
            produtosFiltrados = filtrarListas(valorSelecionado, produtos)
            
            if produtosFiltrados != None or produtosFiltrados != 0:
                produtosFiltrados = sorted(produtosFiltrados, key=lambda p:p['nomeProdutoComposicao'], reverse=True)
                tabelas.table.delete(*tabelas.table.get_children())
                
                
                for p in produtosFiltrados:
                    id = p['idProdutoComposicao']
                    nome = p['nomeProdutoComposicao']
                    linha = p['classificacao']
                    classificacao = p['IDX_CLASSIFICACAO']
                    estoque = p['estoque']
                    unidadeEstoque = p['unidadeEstoque']
                    totalProducao = p['totalProducao']
                    unidade = p['unidade']
                    data = (id, nome, linha, classificacao, estoque, unidadeEstoque, totalProducao, unidade)
                    tabelas.table.insert(parent='', index=0, values=data)
            else:
                return 'Nenhum produto neste periodo.'

def gerarPlanilha():
    produtos = setarData('ano-atual')
    if produtos == None:
        messagebox.showinfo('Data inválida', 'Periodo selecionado inválido')
    elif produtos == 0:
        messagebox.showinfo('Lista vazia', 'Não há eventos nesse período de tempo') 
    else:
        criacao_planilha.gerarArquivoExcel('COMPRAS', produtos, incluirLinhaProducao) 



#Tkinter
root = Tk()
root.title("Gerar pedidos de suprimento")

root.geometry("1150x800")

notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True)

page1 = Frame(notebook)
notebook.add(page1, text='Página 1')

mainFrame = Frame(page1)
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

incluirLinhaProducao = IntVar(value=0)
semLinhaProducao = IntVar()
filtrarSal = IntVar(value=0)
filtrarDoces = IntVar(value=0)
filtrarRefeicoes = IntVar(value=0)
filtrarConfeitaria = IntVar(value=0)
filtrarCanapes = IntVar(value=0)
trazerTodos = IntVar(value=1)

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

btn_obter_data = Button(secondFrame, text="Mostrar lista", bg='#C0C0C0', font=("Arial", 16), command=inserirNaLista)
btn_obter_data.grid(row=5, column=0, columnspan=2, padx=(80, 0), pady=2, sticky='nsew')


btn_abrir_janela = Button(secondFrame, text="Ver qtd. ano anterior", bg='#C0C0C0', font=("Arial", 16), command=lambda: verQtdAnoPassado(tabelas.table))
btn_abrir_janela.grid(row=8, column=0)


btn_obter_data = Button(secondFrame, text="Gerar Planilhas Excel", bg='#C0C0C0', font=("Arial", 16), command=gerarPlanilha)
btn_obter_data.grid(row=17, column=0, columnspan=2, padx=(80, 0), pady=(10, 30), sticky='nsew')


#Combo box classificação
opcoes = ['Todos os produtos','Acessórios', 'Acompanhamento', 'Bebidas', 'Bolo', 'Buffet', 'Cafeteria', 'Carnes', 
          'Compras Diversas', 'Congelados', 'Conservas', 'Copos', 'Descartáveis', 'Diversos', 'Doces', 
          'Doces Terceirizados', 'embalagem', 'Equip.Segur/EPI/Unif', 'Frete', 'Frios', 'Frutas', 
          'Higiene / Limpeza', 'Hortifrutigranjeiros', 'Laticínios', 'Louças', 'Manutenção', 'Massa', 
          'Materiais', 'Material Escritorio', 'Mercearia', 'Mesa de Antepastos', 'Mesa de Guloseimas', 
          'Pães e Bolos', 'Patê', 'Peças Inox', 'Peixe', 'Pescados', 'Petiscos', 'Petiscos Frios', 'Produtos revenda', 
          'Recheios e Massas', 'Refrigerados', 'Salada', 'Sobremesa', 'Sobremesa Terceiriza', 
          'Sorveteria', 'Utensilios']
opcaoSelecionada = StringVar()
opcaoSelecionada.set('Todos os produtos')
combo = ttk.Combobox(secondFrame, values=opcoes, textvariable=opcaoSelecionada)
combo.grid(row=4, padx=(160, 100), columnspan=2, sticky='nsew')
combo.bind("<<ComboboxSelected>>")
tabelas.criarTabela(secondFrame)

root.mainloop()





