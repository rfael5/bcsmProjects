from sqlalchemy import create_engine
import pandas as pd
import requests
import json
from datetime import datetime

import openpyxl
from openpyxl.styles import PatternFill

conexao = (
    "mssql+pyodbc:///?odbc_connect=" + 
    "DRIVER={ODBC Driver 11 for SQL Server};" +
    "SERVER=localhost;" +
    "DATABASE=SOUTTOMAYOR;" +
    "Trusted_Connection=yes;"
)

engine = create_engine(conexao, pool_pre_ping=True)

queryProdutosComposicao =  """
select 
	 e.PK_DOCTOPED as idEvento, e.NOME as nomeEvento, e.DTEVENTO as dataEvento, p.PK_MOVTOPED as idMovtoped, c .IDX_LINHA as linha, p.DESCRICAO as nomeProdutoAcabado, ca.RENDIMENTO as rendimento, p.UNIDADE as unidadeAcabado, a.RDX_PRODUTO as idProdutoAcabado, c.DESCRICAO as nomeProdutoComposicao, c.PK_PRODUTO as idProdutoComposicao, a.QUANTIDADE as qtdProdutoComposicao, a.UN as unidadeComposicao, p.L_QUANTIDADE as qtdProdutoEvento 
from TPAPRODCOMPOSICAO as a 
	inner join TPAPRODUTO as c on a.IDX_PRODUTO = c.PK_PRODUTO
	inner join TPAMOVTOPED as p on a.RDX_PRODUTO = p.IDX_PRODUTO
	inner join TPADOCTOPED as e on p.RDX_DOCTOPED = e.PK_DOCTOPED
    inner join TPAPRODUTO as ca on p.IDX_PRODUTO = ca.PK_PRODUTO
where e.TPDOCTO = 'EC' 
	and e.DTPREVISAO between '20240227' and '20240228'
	and e.SITUACAO = 'Z'
    and c.OPSUPRIMENTOMP = 'S'
or e.TPDOCTO = 'EC' 
	and e.DTPREVISAO between '20240227' and '20240228'
	and e.SITUACAO = 'B'
    and c.OPSUPRIMENTOMP = 'S'
or e.TPDOCTO = 'OR' 
	and e.DTPREVISAO between '20240227' and '20240228'
	and e.SITUACAO = 'V'
    and c.OPSUPRIMENTOMP = 'S'
or e.TPDOCTO = 'OR' 
	and e.DTPREVISAO between '20240227' and '20240228'
	and e.SITUACAO = 'B'
    and c.OPSUPRIMENTOMP = 'S'
order by p.DESCRICAO
"""

queryProdutosAcabados = """
select a.PK_PRODUTO as idProduto, p.PK_MOVTOPED as idMovtoped, p.DESCRICAO as nomeProduto, a.IDX_LINHA as linha, sum(p.L_QUANTIDADE) as qtdTotal, p.UNIDADE as unidade, a.IDX_NEGOCIO as negocio from TPAPRODUTO as a 
	inner join TPAMOVTOPED as p on a.PK_PRODUTO = p.IDX_PRODUTO
	inner join TPADOCTOPED as e on p.RDX_DOCTOPED = e.PK_DOCTOPED
where e.TPDOCTO = 'EC' 
	and e.DTPREVISAO between '20240227' and '20240228'
	and e.SITUACAO = 'Z' 
	and a.IDX_NEGOCIO = 'Produtos acabados'
or e.TPDOCTO = 'EC' 
	and e.DTPREVISAO between '20240227' and '20240228'
	and e.SITUACAO = 'B' 
	and a.IDX_NEGOCIO = 'Produtos acabados'
or e.TPDOCTO = 'OR' 
	and e.DTPREVISAO between '20240227' and '20240228'
	and e.SITUACAO = 'V' 
	and a.IDX_NEGOCIO = 'Produtos acabados'
or e.TPDOCTO = 'OR' 
	and e.DTPREVISAO between '20240227' and '20240228'
	and e.SITUACAO = 'B' 
	and a.IDX_NEGOCIO = 'Produtos acabados'
group by a.PK_PRODUTO, p.PK_MOVTOPED, p.DESCRICAO, p.UNIDADE, a.IDX_LINHA, a.IDX_NEGOCIO
order by nomeProduto
"""

queryComposicao = """
select 
	 c.PK_PRODUTO, c.DESCRICAO, sum(a.QUANTIDADE) as qtdTotalComposicoes, a.UN
from TPAPRODCOMPOSICAO as a 
	inner join TPAPRODUTO as c on a.IDX_PRODUTO = c.PK_PRODUTO
	inner join TPAMOVTOPED as p on a.RDX_PRODUTO = p.IDX_PRODUTO
	inner join TPADOCTOPED as e on p.RDX_DOCTOPED = e.PK_DOCTOPED 
where e.DTPREVISAO between '20240227' and '20240228'
	and e.SITUACAO = 'V'
	and e.TPDOCTO = 'OR'
    and c.OPSUPRIMENTOMP = 'S'
group by c.PK_PRODUTO, c.DESCRICAO, a.UN
"""

def receberDados(query):
    response = pd.read_sql_query(query, engine)
    resultadosJson = response.to_json(orient='records')
    dadosDesserializados = json.loads(resultadosJson)
    return dadosDesserializados

produtosComposicao = receberDados(queryProdutosComposicao)
totalProdutosEvento = receberDados(queryProdutosAcabados)

qtdTotalProducao = []

def verificarAjustes(evento):
    queryAjustes = f"""select PK_AJUSTEPEDITEM as idAjuste, IDX_MOVTOPED as idMovtoped, QUANTIDADE as qtdAlteracao from TPAAJUSTEPEDITEM where IDX_MOVTOPED = '{evento['idMovtoped']}'"""
    resultado = receberDados(queryAjustes)
    if len(resultado) > 0:
        evento['qtdProdutoEvento'] = evento['qtdProdutoEvento'] + resultado[0]['qtdAlteracao']


def recuperarHoraAtual():
    data_hora_atual = datetime.now()
    formato = "%Y-%m-%d_%H-%M-%S"
    data_hora_formatada = data_hora_atual.strftime(formato)
    return data_hora_formatada


def calcularQtdProducao():
    for e in produtosComposicao:
        verificarAjustes(e)
        if e['unidadeAcabado'] == 'PP':
            #total = e["qtdProdutoComposicao"] * (e["qtdProdutoEvento"] / 10)
            #CALCULO PARA RENDIMENTO: [(qtdEvento / 10) * qtdProdutoComposicao] / rendimento
            total = (e["qtdProdutoEvento"] / 10) * e["qtdProdutoComposicao"]
            rendimento = total / e["rendimento"]
            e["totalProducao"] = rendimento
        elif e['unidadeAcabado'] == 'UN':
            rendimento = (e['qtdProdutoComposicao'] * e['qtdProdutoEvento']) / e['rendimento']
            e['totalProducao'] = rendimento
        else:
            total = e["qtdProdutoComposicao"] * e["qtdProdutoEvento"]
            e["totalProducao"] = total


calcularQtdProducao()

def gerarArquivoExcel(tipoArquivo, listaProdutos):
    caminho_arquivo_excel = f'C:\\Users\\serverteste\\Desktop\\teste2\\arquivos\\{tipoArquivo}--{recuperarHoraAtual()}.xlsx'
    formatoTabela = pd.DataFrame(listaProdutos)
    formatoTabela.to_excel(caminho_arquivo_excel)
    print("ARQUIVO EXCEL GERADO")


def formatarExcel(caminhoArquivo):
    workbook = openpyxl.load_workbook('caminhoArquivo')
    
    sheet = workbook.active


def calcularRendimento(unidadeAcabado, quantidade):
    if unidadeAcabado == 'PP':
        return quantidade / 10
    else:
        return quantidade

somaProdutosEventos = []

def mudarUnidade(unidade):
    if unidade == 'GR':
        return 'KG'
    elif unidade == 'ML':
        return 'LT'
    else:
        return unidade

def alterarStringUnidade(unidade):
    if '\x00' in unidade:
        unidadeCorrigida = unidade.replace('\x00', '')
        return unidadeCorrigida
    else:
        return unidade   

def converterKg(produto):
    if str(produto['unidade']) == "GR" or str(produto['unidade']) == "ML":
        return produto['totalProducao'] / 1000
    else:
        return produto['totalProducao']

def agruparLinhas(produto):
    
    if '\x00' in produto['linha']:
        produto['linha'] = produto['linha'].replace('\x00', '')
        
    for x in range(1, 7):
        if produto['linha'] == f'S{x}':
            produto['linha'] = 'Sal'
    
    for x in range(1, 7):
        if produto['linha'] == f'M-{x}':
            produto['linha'] = 'Doces'
    
    for x in range(1, 4):
        if produto['linha'] == f'C-{x}' or produto['linha'] == 'Doce Geral':
            produto['linha'] = 'Doces'
    
    if produto['linha'] == 'S7' or produto['linha'] == 'S8':
        produto['linha'] = 'Refeições'           


#e.PK_DOCTOPED as idEvento, e.NOME as nomeEvento, e.DTEVENTO as dataEvento, p.PK_MOVTOPED as idMovtoped, c.IDX_LINHA as linha, p.DESCRICAO as nomeProdutoAcabado, ca.RENDIMENTO as rendimento, p.UNIDADE as unidadeAcabado, a.RDX_PRODUTO as idProdutoAcabado, c.DESCRICAO as nomeProdutoComposicao, c.PK_PRODUTO as idProdutoComposicao, a.QUANTIDADE as qtdProdutoComposicao, a.UN as unidadeComposicao, p.L_QUANTIDADE as qtdProdutoEvento 

def somarProdutosEvento():
    dfComposicao = pd.DataFrame(produtosComposicao)
    
    #dfComposicao = dfComposicao.groupby(['idEvento', 'nomeEvento', 'dataEvento', 'idMovtoped', 'linha', 'nomeProdutoAcabado', 'rendimento', 'unidadeAcabado', 'idProdutoAcabado', 'nomeProdutoComposicao', 'idProdutoComposicao', 'qtdProdutoComposicao', 'unidadeComposicao', 'qtdProdutoEvento' ]).reset_index()
    dfComposicao.drop_duplicates(inplace=True)
    novaLista = []

    dfComposicao['unidade'] = dfComposicao['unidadeComposicao'].apply(alterarStringUnidade)
    dfComposicao['totalProducao'] = dfComposicao.apply(converterKg, axis=1)
    
    result = dfComposicao.groupby(['idProdutoComposicao', 'nomeProdutoComposicao', 'unidade', 'linha', 'idProdutoAcabado', 'nomeProdutoAcabado'])[['totalProducao']].sum().reset_index()

    result['unidade'] = result['unidade'].apply(mudarUnidade)
    
    resultJson = result.to_json(orient='records')
    dadosDesserializados = json.loads(resultJson)

    for p in dadosDesserializados:
        for pa in totalProdutosEvento:
            if p['idProdutoAcabado'] == pa['idProduto'] and 'Produtos acabados' in pa['negocio']:
                p['linha'] = pa['linha']
                if p not in novaLista:
                    novaLista.append(p)
    
    for p in novaLista:
        agruparLinhas(p)
    
    # for p in produtosComposicao:
    #     if 'Lombo de Bacalhau Saithe Congelado' in p['nomeProdutoComposicao']:
    #         print(p)
    
    dfNovaLista = pd.DataFrame(novaLista)
    resultFinal = dfNovaLista.groupby(['idProdutoComposicao', 'nomeProdutoComposicao', 'unidade', 'linha'])[['totalProducao']].sum().reset_index()
    
    rFinalJson = resultFinal.to_json(orient='records')
    rFinalDesserializados = json.loads(rFinalJson)
    
    #separarProdutosEvento(rFinalDesserializados)
    
    

def filtrarListas(tipoFiltro, listaCompleta):
    listaFiltrada = list(filter(lambda produto:produto['linha'] == tipoFiltro, listaCompleta))
    return listaFiltrada


def separarProdutosEvento(listaProdutos):
    listaSal = filtrarListas('Sal', listaProdutos)
    listaDoces = filtrarListas('Doces', listaProdutos)
    listaRefeicoes = filtrarListas('Refeições', listaProdutos)
    
    gerarArquivoExcel('TODOS-PRODUDOS', listaProdutos)
    gerarArquivoExcel('SAL',listaSal)
    gerarArquivoExcel('DOCES',listaDoces)
    gerarArquivoExcel('REFEICOES',listaRefeicoes)

somarProdutosEvento()


for p in produtosComposicao:
        if 'Alho Porró unid' in p['nomeProdutoComposicao']:
            print(p)
