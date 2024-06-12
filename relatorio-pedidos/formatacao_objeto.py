import math
from sqlalchemy import create_engine
import pandas as pd
import json

from tkinter import *

#Calcula a quantidade final dos pedidos considerando os ajustes.
def adicionarAjustes(evento, ajustes):
    for a in ajustes:
        if a['idMovtoped'] == evento['idMovtoped']:
            evento['qtdProdutoEvento'] = evento['qtdProdutoEvento'] + a['ajuste']

#Cria um dicionário com a composição dos produtos semi-acabados no mesmo formato
#da composição dos acabados.
def inserirCol_SemiAcabados(row, semiAcabados):
    listaComposicao = []
    listaOrdenada = sorted(semiAcabados, key=lambda p:p['nomeProdutoAcabado'])
    for p in listaOrdenada:
        if p['idProdutoAcabado'] == row['idProdutoComposicao']:  
            comp_semiacabados = {}  
            comp_semiacabados['idProdutoComposicao'] = p['idProduto']
            comp_semiacabados['nomeProdutoComposicao'] = p['nomeProdutoComposicao']
            comp_semiacabados['qtdComposicao'] = p['qtdProdutoComposicao']
            comp_semiacabados['unidadeComposicao'] = p['unidadeProdutoComposicao']
            comp_semiacabados['classificacao'] = p['classificacao']
            comp_semiacabados['linha'] = row['linha']
            comp_semiacabados['idProdutoAcabado'] = p['idProdutoAcabado']
            comp_semiacabados['nomeProdutoAcabado'] = p['nomeProdutoAcabado']
            comp_semiacabados['qtdProducao'] = row['totalProducao']
            comp_semiacabados['unidadeAcabado'] = row['unidade']
            comp_semiacabados['totalProducao'] = (p['qtdProdutoComposicao'] * row['totalProducao']) / p['rendimento']
            if comp_semiacabados != []:
                listaComposicao.append(comp_semiacabados)
    
    return listaComposicao


def converterPJson(lista):
    resultJson = lista.to_json(orient='records')
    dadosDesserializados = json.loads(resultJson)
    return dadosDesserializados

#Remove caracteres das strings que atrapalhavam na manipulação dos dados.
def alterarStringUnidade(unidade):
    if '\x00' in unidade:
        unidadeCorrigida = unidade.replace('\x00', '')
        return unidadeCorrigida
    else:
        return unidade   
            
#Converte as medidas dos produtos de gramas e ml para quilos e litros.
def converterKg(produto):     
    if str(produto['unidade']) == "GR" or str(produto['unidade']) == "ML":
        result = produto['totalProducao'] / 1000 
    else:
        result = produto['totalProducao']
    return round(result, 2)

#Muda a string para a unidade de medida correta.
def mudarUnidade(unidade):
    if unidade == 'GR':
        return 'KG'
    elif unidade == 'ML':
        return 'LT'
    else:
        return unidade
    
#Arredondar o valor da quantidade total de pedidos para 'mais'
def arredondarValor(row):
    if row['unidade'] != 'KG' and row['unidade'] != 'ML':
        return math.ceil(row['totalProducao'])
    else:
        return row['totalProducao']
    
#Multiplica a quantidade do produto que vai na receita pela quantidade
#de pedidos da receita final.
#Dependendo da unidade de medida em que o produto é vendido, a quantidade
#total tem que ser dividida por 10 ou por 100. 
def calcularQtdProducao(produtosComposicao):
    for e in produtosComposicao:
        if e['unidadeAcabado'] == 'PP':
            total = (e["qtdProdutoEvento"] / 10) * e["qtdProdutoComposicao"]
            e["totalProducao"] = total
        elif e['unidadeAcabado'] == 'CT':
            total = e['qtdProdutoComposicao'] * e['qtdProdutoEvento']
            e['totalProducao'] = total
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

def converterUnidadeDiferente(produtos):
     for produto in produtos:
        try:
            #Aplicando a alterarStringUnidade a todos os campos necessarios da lista PRODUTO
            unidadeEstoque = alterarStringUnidade(produto['unidadeEstoque'])
            unidadeComposicao =  alterarStringUnidade(produto['unidadeComposicao'])
            
            if unidadeEstoque != unidadeComposicao or unidadeEstoque != '':
                print("Unidade de estoque diferente da unidade de composição", produto['nomeProdutoComposicao'], unidadeEstoque, unidadeComposicao)
                print("(1" ,unidadeEstoque, " de equivale a) ->", produto['PROPPRODUCAO'], produto['unidadeComposicao'])
                print("(id do Evento) ->", produto['idEvento'], "(Nome do evento) -> ", produto['nomeEvento'],"(Nome do produto) ->", produto['DESCRICAO'], "(Qtd produto que o evento vai usar) ->", produto['qtdProdutoEvento'])
                    
                produto['unidadeComposicao'] = produto['unidadeEstoque']
                                
                print("Calculo da funcao Antes ---->", produto['totalProducao'])
                a = calcularQtdProducao([produto])[0]
                print("Calculo da funcao depois ---->", a['totalProducao'])
                        
                result = produto['totalProducao'] / produto['PROPPRODUCAO']
                print("Divisao -->", result)
                produto['totalProducao'] = result
                    
                if(produto['unidadeAcabado']) == 'CT':
                        print("CT ->")
                elif(produto['unidadeAcabado']) == 'PP':
                        print("PP ->")
                elif(produto['unidadeAcabado']) == 'UD':
                        print("UD ->")
                elif(produto['unidadeAcabado']) == 'UM':
                        print("UM ->")
              
                print("------------------------------------------------------------")
                    
        except KeyError as e:
            print(f"Key {e} not found in produto {produto['nomeProdutoComposicao']}.")

#Executa a função que calcula o ajuste em cada produto da lista.
def aplicarAjustes(produtosComposicao, ajustes):
    for p in produtosComposicao:
        adicionarAjustes(p, ajustes)
    return produtosComposicao

#Insere a coluna com o saldo de estoque em cada produto da lista.
def adicionarEstoque(produtos, estoque):
    for p in produtos:
        p['estoque'] = 0
        p['unidadeEstoque'] = ''
        for e in estoque:
            if p['idProdutoComposicao'] == e['RDX_PRODUTO']:
                p['estoque'] = e['SALDOESTOQUE']
                p['unidadeEstoque'] = e['UN']

#Junta as subdivisões da linha de produção das receitas em um só grupo.
#Por exemplo, as linhas de S1 até S6, são agrupadas apenas como sal.
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

#Junta as listas de composição de acabados e de semi-acabados em uma só.
def unirListasComposicao(acabados, semiAcabados):
    for p in acabados:
        p['produtoAcabado'] = True
    for p in semiAcabados:
        acabados.append(p)
    
    df = pd.DataFrame(acabados)
    result = df.groupby(['idProdutoComposicao', 'nomeProdutoComposicao', 'classificacao', 'unidade', 'linha', 'estoque', 'unidadeEstoque','produtoAcabado'])[['totalProducao']].sum().reset_index()
    result = result[['idProdutoComposicao', 'nomeProdutoComposicao', 'classificacao', 'linha', 'estoque', 'unidadeEstoque', 'totalProducao', 'unidade', 'produtoAcabado']]
    result['totalProducao'] = result['totalProducao'].round(4)
    res = converterPJson(result)
    dadosOrdenados = sorted(res, key=lambda p:p['nomeProdutoComposicao'])
    return dadosOrdenados   

#Remove versões alteradas de uma receita e deixa somente uma receita original
def removerReceitasAlteradas(lista_completa:list):
    copia_lista = lista_completa
    for p_copia in copia_lista:
        for p_original in lista_completa:
            if p_original['idProdutoAcabado'] == p_copia['idProdutoAcabado'] and p_original['DTINC'] > p_copia['DTINC']:
                lista_completa.remove(p_original)
            else:
                return


#Função que soma a quantidade total de cada pedido
def somarProdutosEvento(produtosComposicao):
       
    removerReceitasAlteradas(produtosComposicao)
    
    dfComposicao = pd.DataFrame(produtosComposicao)
    dfComposicao.drop_duplicates(inplace=True)
    dfComposicao['produtoAcabado'] = True
    
    #Remove caracteres desnecessários da string da unidade de medida
    dfComposicao['unidade'] = dfComposicao['unidadeComposicao'].apply(alterarStringUnidade)
    #Convert unidades GR e ML para KG e LT
    dfComposicao['totalProducao'] = dfComposicao.apply(converterKg, axis=1)
    #Agrupa as linhas de produção sob um só tipo, como sal, doce, confeitaria, etc.
    dfComposicao['linha'] = dfComposicao.apply(agruparLinhas, axis=1)
    
    #Soma a quantidade total de pedidos de suprimento para cada produto
    result = dfComposicao.groupby(['idProdutoComposicao', 'nomeProdutoComposicao', 'classificacao', 'unidade', 'linha', 'estoque', 'unidadeEstoque', 'produtoAcabado'])[['totalProducao']].sum().reset_index()

    #Muda a string de unidade de medida de GR para KG.
    result['unidade'] = result['unidade'].apply(mudarUnidade)
    
    #converte os valores para mais
    result['totalProducao'] = result.apply(arredondarValor, axis=1)
    
    
    #Organiza as colunas na ordem que devem aparecer na tabela.
    result = result[['idProdutoComposicao', 'nomeProdutoComposicao', 'classificacao', 'linha', 'estoque', 'unidadeEstoque', 'totalProducao', 'unidade', 'produtoAcabado']]
    
    resultJson = result.to_json(orient='records')
    dadosDesserializados = json.loads(resultJson)
    #Ordena os produtos em ordem alfabetica.
    dadosOrdenados = sorted(dadosDesserializados, key=lambda p:p['nomeProdutoComposicao'])
    
    return dadosOrdenados
