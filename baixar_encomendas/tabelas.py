from tkinter import ttk
from tkinter import *


def criarTabela(frame):
    global table 
    table = ttk.Treeview(frame, columns = ('ID', 'Evento', 'Documento', 'Data Cadastro', 'Situação'), show = 'headings')
    table.heading('ID', text = 'ID')
    table.heading('Evento', text = 'Evento')
    table.heading('Documento', text = 'Documento')
    table.heading('Data Cadastro', text = 'Data Cadastro')
    table.heading('Situação', text = 'Situação')
    table.grid(row=6, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

    table.column('ID', width=80, anchor=CENTER)
    table.column('Evento', width=300, anchor=CENTER)
    table.column('Documento', width=160, anchor=CENTER)
    table.column('Data Cadastro', width=80, anchor=CENTER)
    table.column('Situação', width=80, anchor=CENTER)


