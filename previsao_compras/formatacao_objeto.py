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

import connection

def adicionarAjustes(evento, ajustes):
    for a in ajustes:
        if a['idMovtoped'] == evento['idMovtoped']:
            evento['qtdProdutoEvento'] = evento['qtdProdutoEvento'] + a['ajuste']

def inserirCol_SemiAcabados(row, semiAcabados, incluirLinhaProducao):
    listaComposicao = []
    listaOrdenada = sorted(semiAcabados, key=lambda p:p['nomeProdutoAcabado'])
    for p in listaOrdenada:
        if p['idProdutoAcabado'] == row['idProdutoComposicao']:  
            comp_semiacabados = {}  
            comp_semiacabados['idProdutoComposicao'] = p['idProduto']
            comp_semiacabados['nomeProdutoComposicao'] = p['nomeProdutoComposicao']
            comp_semiacabados['negocio'] = p['negocio']
            comp_semiacabados['qtdComposicao'] = p['qtdProdutoComposicao']
            comp_semiacabados['unidadeComposicao'] = p['unidadeProdutoComposicao']
            comp_semiacabados['classificacao'] = p['classificacao']
            comp_semiacabados['IDX_CLASSIFICACAO'] = p['IDX_CLASSIFICACAO']
            comp_semiacabados['idProdutoAcabado'] = p['idProdutoAcabado']
            comp_semiacabados['nomeProdutoAcabado'] = p['nomeProdutoAcabado']
            comp_semiacabados['qtdProducao'] = row['totalProducao']
            comp_semiacabados['unidadeAcabado'] = row['unidade']
            comp_semiacabados['precoUltimaCompra'] = p['precoUltimaCompra']
            comp_semiacabados['totalProducao'] = (p['qtdProdutoComposicao'] * row['totalProducao']) / p['rendimento']
            if comp_semiacabados != []:
                listaComposicao.append(comp_semiacabados)
    
    return listaComposicao


def converterPJson(lista):
    resultJson = lista.to_json(orient='records')
    dadosDesserializados = json.loads(resultJson)
    return dadosDesserializados


def alterarStringUnidade(unidade):
    if '\x00' in unidade:
        unidadeCorrigida = unidade.replace('\x00', '')
        return unidadeCorrigida
    else:
        return unidade   

def converterKg(produto):
    if str(produto['unidade']) == "GR" or str(produto['unidade']) == "ML":
        result = produto['totalProducao'] / 1000 
    else:
        result = produto['totalProducao']
    return round(result, 4)

def mudarUnidade(unidade):
    if unidade == 'GR':
        return 'KG'
    elif unidade == 'ML':
        return 'LT'
    else:
        return unidade

    
def calcularQtdProducao(produtosComposicao):
    for e in produtosComposicao:
        if e['unidadeAcabado'] == 'PP':
            total = (e["qtdProdutoEvento"] / 10) * e["qtdProdutoComposicao"]
            e["totalProducao"] = total
        elif e['unidadeAcabado'] == 'UD':
            total = (e['qtdProdutoEvento'] / 100) * e['qtdProdutoComposicao']
            e['totalProducao'] = total
        elif e['unidadeAcabado'] == 'UM':
            total = (e['qtdProdutoEvento'] / 10) * e['qtdProdutoComposicao']
            e['totalProducao'] = total
        else:
            total = e["qtdProdutoComposicao"] * e["qtdProdutoEvento"]
            e["totalProducao"] = total
    return produtosComposicao


def aplicarAjustes(produtosComposicao, ajustes):
    for p in produtosComposicao:
        adicionarAjustes(p, ajustes)
    return produtosComposicao

def adicionarEstoque(produtos, estoque):
    for p in produtos:
        p['estoque'] = 0
        p['unidadeEstoque'] = ''
        for e in estoque:
            if p['idProdutoComposicao'] == e['RDX_PRODUTO']:
                p['estoque'] = e['SALDOESTOQUE']
                p['unidadeEstoque'] = e['UN']

def agruparLinhas(produto):
    if '\x00' in produto['linha']:
        produto['linha'] = produto['linha'].replace('\x00', '')
        
    for x in range(1, 5):
        if produto['linha'] == f'S{x}' or produto['linha'] == 'S6':
            return 'Sal'
    
    for x in range(1, 7):
        if produto['linha'] == f'M-{x}' or produto['linha'] == 'Doce Geral':
            return 'Doces'
    
    for x in range(1, 4):
        if produto['linha'] == f'C-{x}':
            return 'Confeitaria'
    
    if produto['linha'] == 'S5':
        return 'Canapés'
    
    if produto['linha'] == 'S7' or produto['linha'] == 'S8':
        return 'Refeições'           

def unirListasComposicao(acabados, semiAcabados, incluirLinhaProducao):
    for p in acabados:
        p['produtoAcabado'] = True
    for p in semiAcabados:
        acabados.append(p)
    
    #list(filter(lambda produto:produto['linha'] == tipoFiltro, listaCompleta))
    filtrar_semi_acabados = list(filter(lambda produto:'Produtos Semi Acab.' not in produto['negocio'], acabados))
    
    df = pd.DataFrame(filtrar_semi_acabados)   

    result = df.groupby(['idProdutoComposicao', 'nomeProdutoComposicao', 'classificacao', 'IDX_CLASSIFICACAO', 'unidade', 'estoque', 'unidadeEstoque', 'precoUltimaCompra'])[['totalProducao']].sum().reset_index()
    result = result[['idProdutoComposicao', 'nomeProdutoComposicao', 'classificacao', 'IDX_CLASSIFICACAO', 'estoque', 'unidadeEstoque', 'totalProducao', 'unidade', 'precoUltimaCompra']]
    
    res = converterPJson(result)
    dadosOrdenados = sorted(res, key=lambda p:p['nomeProdutoComposicao'])
    return dadosOrdenados   


def somarProdutosEvento(produtosComposicao, incluirLinhaProducao):
    dfComposicao = pd.DataFrame(produtosComposicao)
    dfComposicao.drop_duplicates(inplace=True)
    dfComposicao['produtoAcabado'] = True
    dfComposicao['unidade'] = dfComposicao['unidadeComposicao'].apply(alterarStringUnidade)
    dfComposicao['totalProducao'] = dfComposicao.apply(converterKg, axis=1)
    
    result = dfComposicao.groupby(['idProdutoComposicao', 'nomeProdutoComposicao', 'negocio', 'classificacao', 'IDX_CLASSIFICACAO', 'unidade', 'estoque', 'unidadeEstoque', 'produtoAcabado', 'precoUltimaCompra'])[['totalProducao']].sum().reset_index()

    result['unidade'] = result['unidade'].apply(mudarUnidade)
    
    result = result[['idProdutoComposicao', 'nomeProdutoComposicao', 'negocio', 'classificacao', 'IDX_CLASSIFICACAO', 'estoque', 'unidadeEstoque', 'totalProducao', 'unidade', 'produtoAcabado', 'precoUltimaCompra']]
    
    resultJson = result.to_json(orient='records')
    dadosDesserializados = json.loads(resultJson)
    dadosOrdenados = sorted(dadosDesserializados, key=lambda p:p['nomeProdutoComposicao'])
    return dadosOrdenados
