from tkinter import *
from tkinter import ttk

#As funçãos nesse arquivo servem somente para criar as tabelas
#na nossa interface.

#Cria tabelas de produtos acabados e semi acabados
def criarTabela(frame):
    global table 
    table = ttk.Treeview(frame, columns = ('ID', 'Produto', 'Classificacao', 'Linha', 'Estoque', 'Un. Estoque', 'Qtd. Producao', 'Unidade'), show = 'headings')
    table.heading('ID', text = 'ID')
    table.heading('Produto', text = 'Produto')
    table.heading('Classificacao', text = 'Classificacao')
    table.heading('Linha', text = 'Linha')
    table.heading('Estoque', text = 'Estoque')
    table.heading('Un. Estoque', text = 'Un. Estoque')
    table.heading('Qtd. Producao', text = 'Qtd. Producao')
    table.heading('Unidade', text = 'Unidade')
    table.grid(row=7, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

    table.column('ID', width=80, anchor=CENTER)
    table.column('Produto', width=300, anchor=CENTER)
    table.column('Classificacao', width=160, anchor=CENTER)
    table.column('Linha', width=100, anchor=CENTER)
    table.column('Estoque', width=80, anchor=CENTER)
    table.column('Un. Estoque', width=80, anchor=CENTER)
    table.column('Qtd. Producao', width=100, anchor=CENTER)
    table.column('Unidade', width=80, anchor=CENTER)
    table.bind("<ButtonRelease>", lambda event: armazenarIdProduto(event, table))
    
    global tableSemiAcabados 
    tableSemiAcabados = ttk.Treeview(frame, columns = ('ID', 'Produto', 'Classificacao', 'Linha', 'Estoque', 'Un. Estoque', 'Qtd. Producao', 'Unidade'), show = 'headings')
    tableSemiAcabados.heading('ID', text = 'ID')
    tableSemiAcabados.heading('Produto', text = 'Produto')
    tableSemiAcabados.heading('Classificacao', text = 'Classificacao')
    tableSemiAcabados.heading('Linha', text = 'Linha')
    tableSemiAcabados.heading('Estoque', text = 'Estoque')
    tableSemiAcabados.heading('Un. Estoque', text = 'Un. Estoque')
    tableSemiAcabados.heading('Qtd. Producao', text = 'Qtd. Producao')
    tableSemiAcabados.heading('Unidade', text = 'Unidade')
    tableSemiAcabados.grid(row=9, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

    tableSemiAcabados.column('ID', width=80, anchor=CENTER)
    tableSemiAcabados.column('Produto', width=300, anchor=CENTER)
    tableSemiAcabados.column('Classificacao', width=160, anchor=CENTER)
    tableSemiAcabados.column('Linha', width=100, anchor=CENTER)
    tableSemiAcabados.column('Estoque', width=80, anchor=CENTER)
    tableSemiAcabados.column('Un. Estoque', width=80, anchor=CENTER)
    tableSemiAcabados.column('Qtd. Producao', width=100, anchor=CENTER)
    tableSemiAcabados.column('Unidade', width=80, anchor=CENTER)
    tableSemiAcabados.bind("<ButtonRelease>", lambda event: armazenarIdProduto(event, tableSemiAcabados))

#Seleciona a linha de uma tabela
def armazenarIdProduto(event, tabela):
    global tabela_atual
    indice = tabela.selection()
    if indice:
        tabela_atual = tabela.item(indice)['values'][0]
        print(tabela_atual)

#Recria uma tabela sempre que há uma atualização ou que o usuário realiza uma
#nova pesquisa.
def atualizarTabela(frame):
    global table
    global tableSemiAcabados

    criarTabela(frame)

#Cria a tabela dos pedidos feitos após o início do perído da pesquisa para serém
#entregues antes do pediodo da pesquisa.
def criarTabelaMeioSemana(frame):
    global tabelaSemana
    tabelaSemana = ttk.Treeview(frame, columns = ('ID', 'Produto', 'Classificacao', 'Linha', 'Estoque', 'Un. Estoque', 'Qtd. Producao', 'Unidade'), show = 'headings')
    tabelaSemana.heading('ID', text = 'ID')
    tabelaSemana.heading('Produto', text = 'Produto')
    tabelaSemana.heading('Classificacao', text = 'Classificacao')
    tabelaSemana.heading('Linha', text = 'Linha')
    tabelaSemana.heading('Estoque', text = 'Estoque')
    tabelaSemana.heading('Un. Estoque', text = 'Un. Estoque')
    tabelaSemana.heading('Qtd. Producao', text = 'Qtd. Producao')
    tabelaSemana.heading('Unidade', text = 'Unidade')
    tabelaSemana.grid(row=5, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

    tabelaSemana.column('ID', width=80, anchor=CENTER)
    tabelaSemana.column('Produto', width=300, anchor=CENTER)
    tabelaSemana.column('Classificacao', width=160, anchor=CENTER)
    tabelaSemana.column('Linha', width=100, anchor=CENTER)
    tabelaSemana.column('Estoque', width=80, anchor=CENTER)
    tabelaSemana.column('Un. Estoque', width=80, anchor=CENTER)
    tabelaSemana.column('Qtd. Producao', width=100, anchor=CENTER)
    tabelaSemana.column('Unidade', width=80, anchor=CENTER)
 
    global tabelaSemana_semi
    tabelaSemana_semi = ttk.Treeview(frame, columns = ('ID', 'Produto', 'Classificacao', 'Linha', 'Estoque', 'Un. Estoque', 'Qtd. Producao', 'Unidade'), show = 'headings')
    tabelaSemana_semi.heading('ID', text = 'ID')
    tabelaSemana_semi.heading('Produto', text = 'Produto')
    tabelaSemana_semi.heading('Classificacao', text = 'Classificacao')
    tabelaSemana_semi.heading('Linha', text = 'Linha')
    tabelaSemana_semi.heading('Estoque', text = 'Estoque')
    tabelaSemana_semi.heading('Un. Estoque', text = 'Un. Estoque')
    tabelaSemana_semi.heading('Qtd. Producao', text = 'Qtd. Producao')
    tabelaSemana_semi.heading('Unidade', text = 'Unidade')
    tabelaSemana_semi.grid(row=6, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

    tabelaSemana_semi.column('ID', width=80, anchor=CENTER)
    tabelaSemana_semi.column('Produto', width=300, anchor=CENTER)
    tabelaSemana_semi.column('Classificacao', width=160, anchor=CENTER)
    tabelaSemana_semi.column('Linha', width=100, anchor=CENTER)
    tabelaSemana_semi.column('Estoque', width=80, anchor=CENTER)
    tabelaSemana_semi.column('Un. Estoque', width=80, anchor=CENTER)
    tabelaSemana_semi.column('Qtd. Producao', width=100, anchor=CENTER)
    tabelaSemana_semi.column('Unidade', width=80, anchor=CENTER)

#Cria a tabela que mostra os eventos e as receitas finais em que cada
#produto da tabela será usado
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

#Cria a tabela que mostra a quantidade daquele produto pedida no mesmo período do ano anterior.
def criarTabelaAnoAnterior(nova_janela):
    global tbl_ano_anterior
    tbl_ano_anterior = ttk.Treeview(nova_janela, columns = ('ID', 'Produto', 'Linha', 'Total ano anterior', 'Unidade', 'Composição acabado'), show='headings')
    tbl_ano_anterior.heading('ID', text='ID')
    tbl_ano_anterior.heading('Produto', text='Produto')
    tbl_ano_anterior.heading('Linha', text='Linha')
    tbl_ano_anterior.heading('Total ano anterior', text='Total ano anterior')
    tbl_ano_anterior.heading('Unidade', text='Unidade')
    tbl_ano_anterior.heading('Composição acabado', text='Composição acabado')
    tbl_ano_anterior.grid(row=1, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")
    
    tbl_ano_anterior.column('ID', width=70, anchor=CENTER)
    tbl_ano_anterior.column('Produto', width=100, anchor=CENTER)
    tbl_ano_anterior.column('Linha', width=100, anchor=CENTER)
    tbl_ano_anterior.column('Total ano anterior', width=130, anchor=CENTER)
    tbl_ano_anterior.column('Unidade', width=100, anchor=CENTER)
    tbl_ano_anterior.column('Composição acabado', width=200, anchor=CENTER)

    