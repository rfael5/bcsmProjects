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

def setarData():
    dataInicio = dtInicio.get()
    dtInicioFormatada = formatarData(dataInicio)
    dataFim = dtFim.get()
    dtFimFormatada = formatarData(dataFim)
    if dtInicioFormatada < dtFimFormatada:
        global ajustes_periodo
        
        produtosComposicao = connection.getProdutosComposicao(dtInicioFormatada, dtFimFormatada)
        composicaoSemiAcabados = connection.getCompSemiAcabados(dtInicioFormatada, dtFimFormatada)
        ajustes = connection.getAjustes(dtInicioFormatada, dtFimFormatada)

        if len(produtosComposicao) == 0:
            tamanhoLista = 0
            tabelas.criarTabela(secondFrame)
            return tamanhoLista
        else:
            estoque = connection.getEstoque()
            produtosQtdAjustada = formatacao_objeto.calcularQtdProducao(produtosComposicao)
            ajustesAplicados = formatacao_objeto.aplicarAjustes(produtosQtdAjustada, ajustes)
            ajustes_periodo = ajustesAplicados

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


def formatarListaSemiAcabados(lista, estoque):
    formatacao_objeto.adicionarEstoque(lista, estoque)
    df = pd.DataFrame(lista)
    df['produtoAcabado'] = False
    df['unidade'] = df['unidadeComposicao'].apply(formatacao_objeto.alterarStringUnidade)
    df['nomeProdutoComposicao'] = df['nomeProdutoComposicao']. apply(formatacao_objeto.alterarStringUnidade)
    df['unidadeEstoque'] = df['unidadeEstoque'].apply(formatacao_objeto.alterarStringUnidade)
    df['totalProducao'] = df.apply(formatacao_objeto.converterKg, axis=1)
    df['unidade'] = df['unidade'].apply(formatacao_objeto.mudarUnidade)
    
    df = df[['idProdutoComposicao', 'nomeProdutoComposicao', 'negocio', 'classificacao', 'IDX_CLASSIFICACAO', 'estoque', 'unidadeEstoque', 'totalProducao', 'unidade', 'produtoAcabado']]
    
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

def inserirNaLista():
    produtos = selecionarOpcao(Event)
    
    if produtos == None:
        messagebox.showinfo('Data inválida', 'Periodo selecionado inválido')
    elif produtos == 0:
        messagebox.showinfo('Lista vazia', 'Não há eventos nesse período de tempo')    
    else:
        produtosOrdenados = sorted(produtos, key=lambda p:p['nomeProdutoComposicao'], reverse=True)
        
        tabelas.table.delete(*tabelas.table.get_children())
        for p in produtosOrdenados:
            id = p['idProdutoComposicao']
            nome = p['nomeProdutoComposicao']
            linha = p['classificacao']
            classificacao = p['IDX_CLASSIFICACAO']
            estoque = p['estoque']
            unidadeEstoque = p['unidadeEstoque']
            totalProducao = p['totalProducao']
            unidade = p['unidade']
            preco_ultima_compra = p['precoUltimaCompra']
            data = (id, nome, linha, classificacao, estoque, unidadeEstoque, totalProducao, unidade, preco_ultima_compra)
            tabelas.table.insert(parent='', index=0, values=data)


def gerarPlanilha():
    produtos = setarData()
    if produtos == None:
        messagebox.showinfo('Data inválida', 'Periodo selecionado inválido')
    elif produtos == 0:
        messagebox.showinfo('Lista vazia', 'Não há eventos nesse período de tempo') 
    else:
        criacao_planilha.gerarArquivoExcel('COMPRAS', produtos, incluirLinhaProducao) 

def filtrarListas(tipoFiltro, listaCompleta):
    if listaCompleta == None:
        return None
    elif listaCompleta == 0:
        return 0
    else:
        listaFiltrada = list(filter(lambda produto:produto['IDX_CLASSIFICACAO'] == tipoFiltro or tipoFiltro in produto['IDX_CLASSIFICACAO'], listaCompleta))
        return listaFiltrada

def selecionarOpcao(event):
    todosProdutos = setarData()
    valorSelecionado = combo.get()
    #print(f"Opção selecionada: {valorSelecionado}")
    if valorSelecionado == 'Todos os produtos':
        return todosProdutos
    else:
        produtos_filtrados = filtrarListas(valorSelecionado, todosProdutos)
        return produtos_filtrados
    
    


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

opcoes = [
    'Todos os produtos',
    'Acessórios',
    'Acompanhamento',
    'Bebidas',
    'Bolo',
    'Buffet',
    'Cafeteria',
    'Carnes',
    'Compras Diversas',
    'Congelados',
    'Conservas',
    'Copos',
    'Descartáveis',
    'Diversos',
    'Doces',
    'Doces Terceirizados',
    'embalagem',
    'Equip.Segur/EPI/Unif',
    'Frete',
    'Frios',
    'Frutas',
    'Higiene / Limpeza',
    'Hortifrutigranjeiros',
    'Laticínios',
    'Louças',
    'Manutenção',
    'Massa',
    'Materiais',
    'Material Escritorio',
    'Mercearia',
    'Mesa de Antepastos',
    'Mesa de Guloseimas',
    'Pães e Bolos',
    'Patê',
    'Peças Inox',
    'Peixe',
    'Pescados',
    'Petiscos',
    'Petiscos Frios',
    'Produtos revenda',
    'Recheios e Massas',
    'Refrigerados',
    'Salada',
    'Sobremesa',
    'Sobremesa Terceiriza',
    'Sorveteria',
    'Utensilios'
]
opcaoSelecionada = StringVar()
opcaoSelecionada.set('Todos os produtos')
combo = ttk.Combobox(secondFrame, values=opcoes, textvariable=opcaoSelecionada)
combo.grid(row=4, padx=(160, 100), columnspan=2, sticky='nsew')
combo.bind("<<ComboboxSelected>>", selecionarOpcao)

#row 7 --> Tabela composição acabados

# btn_mostrar_eventos = Button(secondFrame, text="Ver todos os eventos", bg='#C0C0C0', font=("Arial", 16), command= lambda:verTodosEventos(ajustes_periodo, tabelas.table))
# btn_mostrar_eventos.grid(row=8)

#row 10 --> Tabela composição semi-acabados

btn_obter_data = Button(secondFrame, text="Gerar Planilhas Excel", bg='#C0C0C0', font=("Arial", 16), command=gerarPlanilha)
btn_obter_data.grid(row=17, column=0, columnspan=2, padx=(80, 0), pady=(10, 30), sticky='nsew')


####################################################
#PÁGINA 2
####################################################

# page2 = Frame(notebook)
# notebook.add(page2,text='Página 2')

# lb1 = Label(page2, text='I am page 2')
# lb1.grid(pady=20)

# hora_ultima_checagem = Label(page2, text='', bg='#C0C0C0', font=("Arial", 16))
# hora_ultima_checagem.grid(row=0, column=0)

# mensagem_banco = Label(page2, text='', font=("Arial", 16))
# mensagem_banco.grid(row=1, column=0)

# dt_inicio_semana = Label(page2, text="De:", font=("Arial", 14))
# dt_inicio_semana.grid(row=2, padx=(0, 190), column=0, sticky="e")

# dt_inicio_semana = DateEntry(page2, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
# dt_inicio_semana.grid(row=3, column=0, padx=(150, 0), pady=5, sticky="e")

# dt_fim_semana = Label(page2, text="Até:", font=("Arial", 14))
# dt_fim_semana.grid(row=2, column=1, padx=(50, 0), pady=5, sticky="w")

# dt_fim_semana = DateEntry(page2, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
# dt_fim_semana.grid(row=3, column=1, padx=(50, 0), pady=5, sticky="w")

# btn_pedidos_semana = Button(page2, text="Ver pedidos meio semana", bg='#C0C0C0', font=("Arial", 16), command= lambda: inserirTabelaTeste('btn'))
# btn_pedidos_semana.grid(row=4)
# #verTodosEventos
# btn_mostrar_eventos = Button(page2, text="Ver todos os eventos", bg='#C0C0C0', font=("Arial", 16), command= lambda:verTodosEventos(ajustes_meio_semana, tabelas.tabelaSemana))
# btn_mostrar_eventos.grid(row=7)

#tabelas.criarTabelaMeioSemana(page2)
tabelas.criarTabela(secondFrame)

#consultarAttBanco()

root.mainloop()





