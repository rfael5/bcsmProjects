from tkinter import filedialog
from sqlalchemy import create_engine
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


def atualizarTabela(frame, incluirLinhaProducao):
    global table
    global tableSemiAcabados
    if incluirLinhaProducao.get() != 1: 
        table = ttk.Treeview(frame, columns = ('ID', 'Produto', 'Classificacao', 'Estoque', 'Un. Estoque', 'Qtd. Producao', 'Unidade'), show = 'headings')
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
        
        tableSemiAcabados = ttk.Treeview(frame, columns = ('ID', 'Produto', 'Classificacao', 'Estoque', 'Un. Estoque', 'Qtd. Producao', 'Unidade'), show = 'headings')
        tableSemiAcabados.heading('ID', text = 'ID')
        tableSemiAcabados.heading('Produto', text = 'Produto')
        tableSemiAcabados.heading('Classificacao', text = 'Classificacao')
        tableSemiAcabados.heading('Estoque', text = 'Estoque')
        tableSemiAcabados.heading('Un. Estoque', text = 'Un. Estoque')
        tableSemiAcabados.heading('Qtd. Producao', text = 'Qtd. Producao')
        tableSemiAcabados.heading('Unidade', text = 'Unidade')
        tableSemiAcabados.grid(row=9, column=0, columnspan=2, padx=(80, 0), pady=10, sticky="nsew")

        tableSemiAcabados.column('ID', width=80, anchor=CENTER)
        tableSemiAcabados.column('Produto', width=300, anchor=CENTER)
        tableSemiAcabados.column('Classificacao', width=160, anchor=CENTER)
        tableSemiAcabados.column('Estoque', width=80, anchor=CENTER)
        tableSemiAcabados.column('Un. Estoque', width=80, anchor=CENTER)
        tableSemiAcabados.column('Qtd. Producao', width=100, anchor=CENTER)
        tableSemiAcabados.column('Unidade', width=80, anchor=CENTER)
    else:
        criarTabela()
