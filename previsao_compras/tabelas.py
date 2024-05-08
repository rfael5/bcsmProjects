from tkinter import *
from tkinter import ttk

def criarTabela(frame):
    global table 
    table = ttk.Treeview(frame, columns = ('ID', 'Produto', 'Linha', 'Classificacao', 'Estoque', 'Un. Estoque', 'Qtd. Producao', 'Unidade', 'Pç Ultima Compra'), show = 'headings', height=25)
    table.heading('ID', text = 'ID')
    table.heading('Produto', text = 'Produto')
    table.heading('Linha', text = 'Linha')
    table.heading('Classificacao', text = 'Classificacao')
    table.heading('Estoque', text = 'Estoque')
    table.heading('Un. Estoque', text = 'Un. Estoque')
    table.heading('Qtd. Producao', text = 'Qtd. Producao')
    table.heading('Unidade', text = 'Unidade')
    table.heading('Pç Ultima Compra', text = 'Pç Ultima Compra')
    table.grid(row=7, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

    table.column('ID', width=60, anchor=CENTER)
    table.column('Produto', width=300, anchor=CENTER)
    table.column('Linha', width=160, anchor=CENTER)
    table.column('Classificacao', width=160, anchor=CENTER)
    table.column('Estoque', width=70, anchor=CENTER)
    table.column('Un. Estoque', width=80, anchor=CENTER)
    table.column('Qtd. Producao', width=100, anchor=CENTER)
    table.column('Unidade', width=70, anchor=CENTER)
    table.column('Pç Ultima Compra', width=120, anchor=CENTER)
 

