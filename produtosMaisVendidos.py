from sqlalchemy import create_engine
import pandas as pd
import requests
import json
from datetime import datetime
from collections import defaultdict
import numpy as np

conexao = (
    "mssql+pyodbc:///?odbc_connect=" + 
    "DRIVER={ODBC Driver 11 for SQL Server};" +
    "SERVER=localhost;" +
    "DATABASE=SOUTTOMAYOR;" +
    "Trusted_Connection=yes;"
)

engine = create_engine(conexao, pool_pre_ping=True)
###############################################################################################################################

#-----PRINCIPAL ---------
queryMaisVendidos = """SELECT V.PK_MOVTOPED as idMovtoped, V.IDX_PRODUTO AS idProduto, E.NOME, P.DESCRICAO as nomeProduto, V.L_QUANTIDADE as qtdEvento, V.L_PRECOUNI as precoUnitario, V.L_PRECOTOTAL as totalPrecoEvento  from TPAMOVTOPED AS V
	INNER JOIN TPADOCTOPED AS E ON V.RDX_DOCTOPED = PK_DOCTOPED
	INNER JOIN TPAPRODUTO AS P ON V.IDX_PRODUTO = P.PK_PRODUTO
WHERE E.TPDOCTO = 'EC'
	AND E.DTPREVISAO BETWEEN '20230901' AND '20231001'
	AND P.IDX_NEGOCIO = 'Produtos Acabados'
	and E.SITUACAO = 'Z'
OR E.TPDOCTO = 'EC'
	AND E.DTPREVISAO BETWEEN '20230901' AND '20231001'
	AND P.IDX_NEGOCIO = 'Produtos Acabados'
	and E.SITUACAO = 'B'
OR E.TPDOCTO = 'OR'
	AND E.DTEVENTO BETWEEN '20230901' AND '20231001'
	AND P.IDX_NEGOCIO = 'Produtos Acabados'
	and E.SITUACAO = 'V'
OR E.TPDOCTO = 'OR'
	AND E.DTEVENTO BETWEEN '20230901' AND '20231001'
	AND P.IDX_NEGOCIO = 'Produtos Acabados'
	and E.SITUACAO = 'B'
ORDER BY V.DESCRICAO
"""

queryAjustes = """
select A.IDX_MOVTOPED AS idMovtoped, V.IDX_PRODUTO AS idProduto, V.DESCRICAO AS nomeProduto, A.QUANTIDADE AS ajuste, A.PRECO AS precoAjuste from TPAAJUSTEPEDITEM AS A 
	inner join TPAMOVTOPED AS V ON A.IDX_MOVTOPED = V.PK_MOVTOPED
	inner join TPADOCTOPED AS E ON V.RDX_DOCTOPED = E.PK_DOCTOPED
	inner join TPAPRODUTO AS P ON V.IDX_PRODUTO = P.PK_PRODUTO
WHERE E.TPDOCTO = 'EC'
	AND E.DTPREVISAO BETWEEN '20230901' AND '20231001'
	AND P.IDX_NEGOCIO = 'Produtos Acabados'
	and E.SITUACAO = 'Z'
OR E.TPDOCTO = 'EC'
	AND E.DTPREVISAO BETWEEN '20230901' AND '20231001'
	AND P.IDX_NEGOCIO = 'Produtos Acabados'
	and E.SITUACAO = 'B' 
OR E.TPDOCTO = 'OR'
	AND E.DTEVENTO BETWEEN '20230901' AND '20231001'
	AND P.IDX_NEGOCIO = 'Produtos Acabados'
	and E.SITUACAO = 'V'
OR E.TPDOCTO = 'OR'
	AND E.DTEVENTO BETWEEN '20230901' AND '20231001'
	AND P.IDX_NEGOCIO = 'Produtos Acabados'
	and E.SITUACAO = 'B'
ORDER BY V.DESCRICAO
"""


###############################################################################################################################

# queryMaisVendidosValor = """
# SELECT V.IDX_PRODUTO AS idProduto, V.DESCRICAO AS nomeProduto, SUM(V.L_QUANTIDADE) AS qtdVendida, SUM(V.L_PRECOTOTAL) AS valorTotal from TPAMOVTOPED AS V
# 	INNER JOIN TPADOCTOPED AS E ON V.RDX_DOCTOPED = PK_DOCTOPED
# 	INNER JOIN TPAPRODUTO AS P ON V.IDX_PRODUTO = P.PK_PRODUTO
# WHERE E.TPDOCTO = 'EC'
# 	AND E.DTPREVISAO BETWEEN '20230101' AND '20230201'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'Z'
# OR E.TPDOCTO = 'EC'
# 	AND E.DTPREVISAO BETWEEN '20230101' AND '20230201'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'B' 
# OR E.TPDOCTO = 'OR'
# 	AND E.DTEVENTO BETWEEN '20230101' AND '20230201'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'V'
# OR E.TPDOCTO = 'OR'
# 	AND E.DTEVENTO BETWEEN '20230101' AND '20230201'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'B' 
# GROUP BY V.IDX_PRODUTO, V.DESCRICAO
# ORDER BY nomeProduto
# """

# queryMaisVendidosQtd = """
# SELECT V.IDX_PRODUTO AS idProduto, V.DESCRICAO AS nomeProduto, SUM(V.L_QUANTIDADE) AS qtdVendida, SUM(V.L_PRECOTOTAL) AS valorTotal from TPAMOVTOPED AS V
# 	INNER JOIN TPADOCTOPED AS E ON V.RDX_DOCTOPED = PK_DOCTOPED
# 	INNER JOIN TPAPRODUTO AS P ON V.IDX_PRODUTO = P.PK_PRODUTO
# WHERE E.TPDOCTO = 'EC'
# 	AND E.DTPREVISAO BETWEEN '20230101' AND '20231231'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'Z'
# OR E.TPDOCTO = 'EC'
# 	AND E.DTPREVISAO BETWEEN '20230101' AND '20231231'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'B' 
# OR E.TPDOCTO = 'OR'
# 	AND E.DTEVENTO BETWEEN '20230101' AND '20231231'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'V'
# OR E.TPDOCTO = 'OR'
# 	AND E.DTEVENTO BETWEEN '20230101' AND '20231231'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'B' 
# GROUP BY V.IDX_PRODUTO, V.DESCRICAO
# ORDER BY nomeProduto
# """


# queryAjustes = """
# select A.IDX_MOVTOPED AS idMovtoped, V.IDX_PRODUTO AS idProduto, V.DESCRICAO AS nomeProduto, SUM(A.QUANTIDADE) AS totalAjustes from TPAAJUSTEPEDITEM AS A 
# 	inner join TPAMOVTOPED AS V ON A.IDX_MOVTOPED = V.PK_MOVTOPED
# 	inner join TPADOCTOPED AS E ON V.RDX_DOCTOPED = E.PK_DOCTOPED
# 	inner join TPAPRODUTO AS P ON V.IDX_PRODUTO = P.PK_PRODUTO
# WHERE E.TPDOCTO = 'EC'
# 	AND E.DTPREVISAO BETWEEN '20230101' AND '20240101'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'Z'
# OR E.TPDOCTO = 'EC'
# 	AND E.DTPREVISAO BETWEEN '20230101' AND '20240101'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'B' 
# OR E.TPDOCTO = 'OR'
# 	AND E.DTEVENTO BETWEEN '20230101' AND '20240101'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'V'
# OR E.TPDOCTO = 'OR'
# 	AND E.DTEVENTO BETWEEN '20230101' AND '20240101'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'B'
# GROUP BY V.IDX_PRODUTO, V.DESCRICAO
# ORDER BY V.DESCRICAO
# """


#########################################################################################################################################

# ----- SEM OR BAIXADOS

# queryMaisVendidos = """SELECT V.PK_MOVTOPED as idMovtoped, V.IDX_PRODUTO AS idProduto, E.NOME, V.DESCRICAO as nomeProduto, V.L_QUANTIDADE as qtdEvento, V.L_PRECOUNI as precoUnitario, V.L_PRECOTOTAL as totalPrecoEvento  from TPAMOVTOPED AS V
# 	INNER JOIN TPADOCTOPED AS E ON V.RDX_DOCTOPED = PK_DOCTOPED
# 	INNER JOIN TPAPRODUTO AS P ON V.IDX_PRODUTO = P.PK_PRODUTO
# WHERE E.TPDOCTO = 'EC'
# 	AND E.DTPREVISAO BETWEEN '20230501' AND '20230601'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'Z'
# OR E.TPDOCTO = 'EC'
# 	AND E.DTPREVISAO BETWEEN '20230501' AND '20230601'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'B'
# OR E.TPDOCTO = 'OR'
# 	AND E.DTEVENTO BETWEEN '20230501' AND '20230601'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'V'
# ORDER BY V.DESCRICAO
# """

# queryAjustes = """
# select A.IDX_MOVTOPED AS idMovtoped, V.IDX_PRODUTO AS idProduto, V.DESCRICAO AS nomeProduto, A.QUANTIDADE AS ajuste, A.PRECO AS precoAjuste from TPAAJUSTEPEDITEM AS A 
# 	inner join TPAMOVTOPED AS V ON A.IDX_MOVTOPED = V.PK_MOVTOPED
# 	inner join TPADOCTOPED AS E ON V.RDX_DOCTOPED = E.PK_DOCTOPED
# 	inner join TPAPRODUTO AS P ON V.IDX_PRODUTO = P.PK_PRODUTO
# WHERE E.TPDOCTO = 'EC'
# 	AND E.DTPREVISAO BETWEEN '20230501' AND '20230601'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'Z'
# OR E.TPDOCTO = 'EC'
# 	AND E.DTPREVISAO BETWEEN '20230501' AND '20230601'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'B' 
# OR E.TPDOCTO = 'OR'
# 	AND E.DTEVENTO BETWEEN '20230501' AND '20230601'
# 	AND P.IDX_NEGOCIO = 'Produtos Acabados'
# 	and E.SITUACAO = 'V'
# ORDER BY V.DESCRICAO
# """

##########################################################################################################################################


def receberDados(query):
    response = pd.read_sql_query(query, engine)
    resultadosJson = response.to_json(orient='records')
    dadosDesserializados = json.loads(resultadosJson)
    return dadosDesserializados

maisVendidos = receberDados(queryMaisVendidos)
ajustes = receberDados(queryAjustes)

valoresFinais = maisVendidos

def recuperarHoraAtual():
    data_hora_atual = datetime.now()
    formato = "%Y-%m-%d_%H-%M-%S"
    data_hora_formatada = data_hora_atual.strftime(formato)
    return data_hora_formatada

def gerarArquivoExcel(tipoTabela, listaProdutos):
    caminho_arquivo_excel = f'C:\\Users\\serverteste\\Desktop\\teste2\\arquivosMaisVendidos\\{tipoTabela}{recuperarHoraAtual()}.xlsx'
    formatoTabela = pd.DataFrame(listaProdutos)
    formatoTabela.to_excel(caminho_arquivo_excel)
    print("ARQUIVO EXCEL GERADO")


def verificarAjustes(evento):
    queryAjustes = f"""select PK_AJUSTEPEDITEM as idAjuste, IDX_MOVTOPED as idMovtoped, QUANTIDADE as qtdAlteracao from TPAAJUSTEPEDITEM where IDX_MOVTOPED = '{evento['idMovtoped']}'"""
    resultado = receberDados(queryAjustes)
    if len(resultado) > 0:
        evento['qtdProdutoEvento'] = evento['qtdProdutoEvento'] + resultado[0]['qtdAlteracao']

def ajustarValores():
    for p in valoresFinais:
        p['totalEvento'] = 0
        p['valorCorrigido'] = 0
        for a in ajustes:
            if p['idMovtoped'] == a['idMovtoped']:
                attQuantidade = p['qtdEvento'] + a['ajuste']
                p["totalEvento"] = attQuantidade * p['precoUnitario']
                p["qtdEvento"] = attQuantidade
                correcaoPrecoEvento = a['ajuste'] * a['precoAjuste']
                p['valorCorrigido'] = p['totalPrecoEvento'] + correcaoPrecoEvento
                
    somarPedidos()

def calcularPareto(tipoPareto, listaValores):
    listaOrdenada = sorted(listaValores, reverse=True, key = lambda d:d[tipoPareto])
    totalVendas = sum(produto[tipoPareto] for produto in listaOrdenada)
    vinteVendas = totalVendas * 0.8
    somaVendas = 0
    listaVinteVendas = []
    for p in listaOrdenada:
        if somaVendas < vinteVendas:
            somaVendas = somaVendas + p[tipoPareto]
            listaVinteVendas.append(p)
    print(vinteVendas)
    print(somaVendas)
    totalVendasVinte = sum(produto[tipoPareto] for produto in listaVinteVendas)
    print(totalVendasVinte)
    confirmarPorcentagem = (totalVendasVinte * 100) / totalVendas
    print(confirmarPorcentagem)

    if tipoPareto == 'qtdEvento':
        gerarArquivoExcel('vinte_Quantidade_Setembro', listaVinteVendas)
    else:
        gerarArquivoExcel('vinte_Monetario_Setembro', listaVinteVendas)




qtdFinal = defaultdict(int)
valorVendasFinal = defaultdict(int)


def somarPedidos():
    df = pd.DataFrame(valoresFinais)

    df['totalVendas'] = df.apply(lambda row: row['totalPrecoEvento'] if row['totalEvento'] == 0 else row['totalEvento'], axis=1)

    result = df.groupby(['idProduto', 'nomeProduto'])[['qtdEvento', 'totalVendas']].sum().reset_index()
    gerarArquivoExcel('total-vendas-setembro', result)
    listaJson = result.to_json(orient='records')
    resultadoDesserializado = json.loads(listaJson)
    calcularPareto('totalVendas', resultadoDesserializado)
    calcularPareto('qtdEvento', resultadoDesserializado)     


ajustarValores()


