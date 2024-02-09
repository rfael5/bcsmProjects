from sqlalchemy import create_engine
import pandas as pd
import requests
import json
from datetime import datetime

conexao = (
    "mssql+pyodbc:///?odbc_connect=" + 
    "DRIVER={ODBC Driver 11 for SQL Server};" +
    "SERVER=localhost;" +
    "DATABASE=SOUTTOMAYOR;" +
    "Trusted_Connection=yes;"
)

engine = create_engine(conexao, pool_pre_ping=True)

#queryTotalAcabados = """"""

queryProdutosComposicao =  """
select 
	 e.PK_DOCTOPED as idEvento, e.NOME as nomeEvento, e.DTEVENTO as dataEvento, p.PK_MOVTOPED as idMovtoped, p.DESCRICAO as nomeProdutoAcabado, p.UNIDADE as unidadeAcabado, a.RDX_PRODUTO as idProdutoAcabado, c.DESCRICAO as nomeProdutoComposicao, c.PK_PRODUTO as idProdutoComposicao, a.QUANTIDADE as qtdProdutoComposicao, a.UN as unidadeComposicao, p.L_QUANTIDADE as qtdProdutoEvento 
from TPAPRODCOMPOSICAO as a 
	inner join TPAPRODUTO as c on a.IDX_PRODUTO = c.PK_PRODUTO
	inner join TPAMOVTOPED as p on a.RDX_PRODUTO = p.IDX_PRODUTO
	inner join TPADOCTOPED as e on p.RDX_DOCTOPED = e.PK_DOCTOPED 
where e.TPDOCTO = 'EC' 
	and e.DTPREVISAO between '20231201' and '20231231'
	and e.SITUACAO = 'Z'
or e.TPDOCTO = 'EC' 
	and e.DTPREVISAO between '20231201' and '20231231'
	and e.SITUACAO = 'B'
or e.TPDOCTO = 'OR' 
	and e.DTPREVISAO between '20231201' and '20231231'
	and e.SITUACAO = 'V'
or e.TPDOCTO = 'OR' 
	and e.DTPREVISAO between '20231201' and '20231231'
	and e.SITUACAO = 'B'
order by p.DESCRICAO
"""

# queryProdutosAcabados = """
# select a.PK_PRODUTO as idProduto, a.DESCRICAO nomeProduto, sum(p.L_QUANTIDADE) as qtdTotal, p.UNIDADE as unidade from TPAPRODUTO as a 
# 	inner join TPAMOVTOPED as p on a.PK_PRODUTO = p.IDX_PRODUTO
# 	inner join TPADOCTOPED as e on p.RDX_DOCTOPED = e.PK_DOCTOPED
# where a.IDX_NEGOCIO = 'Produtos acabados'
# 	and e.DTEVENTO between '20240115' and '20240117'
# 	and e.SITUACAO = 'V'
# 	and e.TPDOCTO = 'OR'
# group by a.PK_PRODUTO, a.DESCRICAO, p.UNIDADE
# order by nomeProduto
# """


queryProdutosAcabados = """
select a.PK_PRODUTO as idProduto, p.PK_MOVTOPED as idMovtoped, p.DESCRICAO as nomeProduto, sum(p.L_QUANTIDADE) as qtdTotal, p.UNIDADE as unidade from TPAPRODUTO as a 
	inner join TPAMOVTOPED as p on a.PK_PRODUTO = p.IDX_PRODUTO
	inner join TPADOCTOPED as e on p.RDX_DOCTOPED = e.PK_DOCTOPED
where e.TPDOCTO = 'EC' 
	and e.DTPREVISAO between '20231201' and '20231231'
	and e.SITUACAO = 'Z' 
	and a.IDX_NEGOCIO = 'Produtos acabados'
or e.TPDOCTO = 'EC' 
	and e.DTPREVISAO between '20231201' and '20231231'
	and e.SITUACAO = 'B' 
	and a.IDX_NEGOCIO = 'Produtos acabados'
or e.TPDOCTO = 'OR' 
	and e.DTPREVISAO between '20231201' and '20231231'
	and e.SITUACAO = 'V' 
	and a.IDX_NEGOCIO = 'Produtos acabados'
or e.TPDOCTO = 'OR' 
	and e.DTPREVISAO between '20231201' and '20231231'
	and e.SITUACAO = 'B' 
	and a.IDX_NEGOCIO = 'Produtos acabados'
group by a.PK_PRODUTO, p.PK_MOVTOPED, p.DESCRICAO, p.UNIDADE
order by nomeProduto
"""

queryComposicao = """
select 
	 c.PK_PRODUTO, c.DESCRICAO, sum(a.QUANTIDADE) as qtdTotalComposicoes, a.UN
from TPAPRODCOMPOSICAO as a 
	inner join TPAPRODUTO as c on a.IDX_PRODUTO = c.PK_PRODUTO
	inner join TPAMOVTOPED as p on a.RDX_PRODUTO = p.IDX_PRODUTO
	inner join TPADOCTOPED as e on p.RDX_DOCTOPED = e.PK_DOCTOPED 
where e.DTPREVISAO between '20231201' and '20231231'
	and e.SITUACAO = 'V'
	and e.TPDOCTO = 'OR'
group by c.PK_PRODUTO, c.DESCRICAO, a.UN
"""

def receberDados(query):
    response = pd.read_sql_query(query, engine)
    resultadosJson = response.to_json(orient='records')
    dadosDesserializados = json.loads(resultadosJson)
    return dadosDesserializados

produtosComposicao = receberDados(queryProdutosComposicao)
totalProdutosEvento = receberDados(queryProdutosAcabados)
totalProdutosComposicao = receberDados(queryComposicao)

qtdTotalProducao = []

def verificarAjustes(evento):
    queryAjustes = f"""select PK_AJUSTEPEDITEM as idAjuste, IDX_MOVTOPED as idMovtoped, QUANTIDADE as qtdAlteracao from TPAAJUSTEPEDITEM where IDX_MOVTOPED = '{evento['idMovtoped']}'"""
    resultado = receberDados(queryAjustes)
    if len(resultado) > 0:
        evento['qtdProdutoEvento'] = evento['qtdProdutoEvento'] + resultado[0]['qtdAlteracao']
    
    #print(resultado[0]["qtdAlteracao"])
    #print(evento['qtdProdutoEvento'])
    #print(resultado)


def recuperarHoraAtual():
    data_hora_atual = datetime.now()
    formato = "%Y-%m-%d_%H-%M-%S"
    data_hora_formatada = data_hora_atual.strftime(formato)
    return data_hora_formatada

# def somarProdutosEvento():
#     df = pd.DataFrame(produtosComposicao)

#     df['unidade'] = alterarStringUnidade(df['unidadeComposicao'])
#     result = df.groupby(['idProdutoComposicao', 'nomeProdutoComposicao', 'unidade'])[['totalProducao']].sum().reset_index()

#     gerarArquivoExcel(result)


def calcularQtdProducao():
    df = pd.DataFrame(produtosComposicao)
    verificarAjustes(df)


# def calcularQtdProducao():
#     for e in produtosComposicao:
#         verificarAjustes(e)
#         if e['unidadeAcabado'] == 'PP':
#             total = e["qtdProdutoComposicao"] * (e["qtdProdutoEvento"] / 10)
#             e["totalProducao"] = total
#         else:
#             total = e["qtdProdutoComposicao"] * e["qtdProdutoEvento"]
#             e["totalProducao"] = total

calcularQtdProducao()

def gerarArquivoExcel(listaProdutos):
    caminho_arquivo_excel = f'C:\\Users\\serverteste\\Desktop\\teste2\\arquivos\\quantidade_final{recuperarHoraAtual()}.xlsx'
    formatoTabela = pd.DataFrame(listaProdutos)
    formatoTabela.to_excel(caminho_arquivo_excel)
    print("ARQUIVO EXCEL GERADO")


def calcularRendimento(unidadeAcabado, quantidade):
    if unidadeAcabado == 'PP':
        return quantidade / 10
    else:
        return quantidade

somaProdutosEventos = []

def alterarStringUnidade(unidade):
    if '\x00' in unidade:
        unidadeCorrigida = unidade.replace('\x00', '')
        return unidadeCorrigida
    else:
        return unidade

def somarProdutosEvento():
    df = pd.DataFrame(produtosComposicao)

    df['unidade'] = alterarStringUnidade(df['unidadeComposicao'])
    result = df.groupby(['idProdutoComposicao', 'nomeProdutoComposicao', 'unidade'])[['totalProducao']].sum().reset_index()

    gerarArquivoExcel(result)



# def somarProdutosEvento():
#     copiaListaProdutos = produtosComposicao
#     listaTotais = []
#     listaOrdenada = []
#     for e in produtosComposicao:
        
#         total = 0
#         for ec in copiaListaProdutos:
#             try:
#                 if e["idProdutoComposicao"] == ec["idProdutoComposicao"]:
#                     total += ec['totalProducao']
#             except KeyError:
#                 print(f'{ec["nomeProdutoAcabado"]} não é produto acabado.')
#         # somaProducao = {
#         #     "idProdutoComposicao": e['idProdutoComposicao'],
#         #     "nomeProdutoComposicao": e['nomeProdutoComposicao'],
#         #     "qtdTotal": calcularRendimento(e['unidadeAcabado'], total),
#         #     "unidade":e['unidadeComposicao']
#         # }
#         somaProducao = {
#             "idProdutoComposicao": e['idProdutoComposicao'],
#             "nomeProdutoComposicao": e['nomeProdutoComposicao'],
#             "qtdTotal": total,
#             "unidade": alterarStringUnidade(e['unidadeComposicao'])
#         }
#         if somaProducao not in listaTotais:
#             listaTotais.append(somaProducao)
#             #somaProdutosEventos.append(somaProducao)
#     # listaOrdenada = sorted(listaTotais, key = lambda d:d['nomeProdutoComposicao'])
#     # for p in listaOrdenada:
#     #     print(f"----{p}")
#     gerarArquivoExcel(listaTotais)
    


somarProdutosEvento()


# for p in totalProdutosEvento:
#     print(f"----{p}")


# for e in produtosComposicao:
#     if e['nomeProdutoComposicao'] == 'Coco Ralado Seco pct 10kg':
#         print(f"----{e}")



# for e in produtosComposicao:
#     if 'totalProducao' not in e:
#         print(e)

# for e in produtosComposicao:
#     if e['idProdutoAcabado'] == '1833':
#         print(e)
    # try:
    #     print(f"----{e['totalProducao']}")
    # except KeyError:
    #     print(f'----{e}')
