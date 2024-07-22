from tkinter import *
from tkinter import ttk

#As funçãos nesse arquivo servem somente para criar as tabelas
#na nossa interface.

#Cria tabelas de produtos acabados e semi acabados
def criarTabela(frame):
    global table
    table = ttk.Treeview(frame, columns = ('Produto', 'Quantidade'), show = 'headings')
    table.heading('Produto', text = 'Produto')
    table.heading('Quantidade', text = 'Classificacao')

    table.grid(row=12, column=0, columnspan=2, pady=10, sticky="nsew")


    table.column('Produto', width=200, anchor=CENTER)
    table.column('Quantidade', width=80, anchor=CENTER)
