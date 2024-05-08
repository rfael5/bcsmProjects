from tkinter import *
from tkinter import ttk

def criarTabela(frame):
    global table 
    table = ttk.Treeview(frame, columns = ('ID', 'Produto', 'Classificacao', 'Estoque', 'Un. Estoque', 'Qtd. Producao', 'Unidade'), show = 'headings', height=25)
    table.heading('ID', text = 'ID')
    table.heading('Produto', text = 'Produto')
    table.heading('Classificacao', text = 'Classificacao')
    table.heading('Estoque', text = 'Estoque')
    table.heading('Un. Estoque', text = 'Un. Estoque')
    table.heading('Qtd. Producao', text = 'Qtd. Producao')
    table.heading('Unidade', text = 'Unidade')
    table.grid(row=7, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

    table.column('ID', width=80, anchor=CENTER)
    table.column('Produto', width=300, anchor=CENTER)
    table.column('Classificacao', width=160, anchor=CENTER)
    table.column('Estoque', width=80, anchor=CENTER)
    table.column('Un. Estoque', width=80, anchor=CENTER)
    table.column('Qtd. Producao', width=100, anchor=CENTER)
    table.column('Unidade', width=80, anchor=CENTER)

def criarTabelaMeioSemana(frame):
    global tabelaSemana
    tabelaSemana = ttk.Treeview(frame, columns = ('ID', 'Produto', 'Classificacao', 'Estoque', 'Un. Estoque', 'Qtd. Producao', 'Unidade'), show = 'headings')
    tabelaSemana.heading('ID', text = 'ID')
    tabelaSemana.heading('Produto', text = 'Produto')
    tabelaSemana.heading('Classificacao', text = 'Classificacao')
    tabelaSemana.heading('Estoque', text = 'Estoque')
    tabelaSemana.heading('Un. Estoque', text = 'Un. Estoque')
    tabelaSemana.heading('Qtd. Producao', text = 'Qtd. Producao')
    tabelaSemana.heading('Unidade', text = 'Unidade')
    tabelaSemana.grid(row=5, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

    tabelaSemana.column('ID', width=80, anchor=CENTER)
    tabelaSemana.column('Produto', width=300, anchor=CENTER)
    tabelaSemana.column('Classificacao', width=160, anchor=CENTER)
    tabelaSemana.column('Estoque', width=80, anchor=CENTER)
    tabelaSemana.column('Un. Estoque', width=80, anchor=CENTER)
    tabelaSemana.column('Qtd. Producao', width=100, anchor=CENTER)
    tabelaSemana.column('Unidade', width=80, anchor=CENTER)
 

def criarTabelaEvento(nova_janela):
    global tabelaEventos
    tabelaEventos = ttk.Treeview(nova_janela, columns = ('Cliente', 'Produto', 'Data pedido', 'Data previsão', 'Qtd Evento', 'Unidade'), show = 'headings')
    tabelaEventos.heading('Cliente', text = 'Cliente')
    tabelaEventos.heading('Produto', text = 'Produto')
    tabelaEventos.heading('Data pedido', text = 'Data pedido')
    tabelaEventos.heading('Data previsão', text = 'Data previsão')
    tabelaEventos.heading('Qtd Evento', text = 'Qtd Evento')
    tabelaEventos.heading('Unidade', text = 'Unidade')
    tabelaEventos.grid(row=1, column=0, padx=(80, 0), pady=10, sticky="nsew")

    tabelaEventos.column('Cliente', width=160, anchor=CENTER)
    tabelaEventos.column('Produto', width=320, anchor=CENTER)
    tabelaEventos.column('Data pedido', width=80, anchor=CENTER)
    tabelaEventos.column('Data previsão', width=80, anchor=CENTER)
    tabelaEventos.column('Qtd Evento', width=80, anchor=CENTER)
    tabelaEventos.column('Unidade', width=60, anchor=CENTER)

def criarTabelaMesAnterior(nova_janela):
    global tbl_ano_anterior
    tbl_ano_anterior = ttk.Treeview(nova_janela, columns = ('ID', 'Produto', 'Total ano anterior', 'unidade'), show='headings')
    tbl_ano_anterior.heading('ID', text='ID')
    tbl_ano_anterior.heading('Produto', text='Produto')
    tbl_ano_anterior.heading('Total ano anterior', text='Total ano anterior')
    tbl_ano_anterior.heading('unidade', text='unidade')
    tbl_ano_anterior.grid(row=1, column=0, padx=(80, 0), pady=10, sticky="nsew")
    
    tbl_ano_anterior.column('ID', width=70, anchor=CENTER)
    tbl_ano_anterior.column('Produto', width=100, anchor=CENTER)
    tbl_ano_anterior.column('Total ano anterior', width=130, anchor=CENTER)
    tbl_ano_anterior.column('unidade', width=100, anchor=CENTER)
    
