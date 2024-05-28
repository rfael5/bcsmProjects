from sqlalchemy import create_engine
import pandas as pd
import json

#Conexão banco de testes
conexao = (
    "mssql+pyodbc:///?odbc_connect=" + 
    "DRIVER={ODBC Driver 17 for SQL Server};" +
    "SERVER=localhost;" +
    "DATABASE=SOUTTOMAYOR;" +
    "UID=Sa;" +
    "PWD=P@ssw0rd2023"
)

#Conexão no banco principal
# conexao = (
#     "mssql+pyodbc:///?odbc_connect=" + 
#     "DRIVER={ODBC Driver 17 for SQL Server};" +
#     "SERVER=192.168.1.43;" +
#     "DATABASE=SOUTTOMAYOR;" +
#     "UID=Sa;" +
#     "PWD=P@ssw0rd2023@#$"
# )

engine = create_engine(conexao, pool_pre_ping=True)

#Executa a query e armazena os dados em uma variável
#Retorna os dados convertidos para json
def receberDados(query):
    response = pd.read_sql_query(query, engine)
    resultadosJson = response.to_json(orient='records')
    dadosDesserializados = json.loads(resultadosJson)
    return dadosDesserializados

#Query que busca os produtos usados na composição das receitas
def getProdutosComposicao(dataInicio, dataFim):
    queryProdutosComposicao =  f"""
    select 
        e.PK_DOCTOPED as idEvento, e.NOME as nomeEvento, e.DOCUMENTO as documento, e.DTEVENTO as dataEvento, e.DTPREVISAO as dataPrevisao, e.DATA as dataPedido, p.PK_MOVTOPED as idMovtoped, 
        ca.IDX_LINHA as linha, p.DESCRICAO as nomeProdutoAcabado, ca.RENDIMENTO as rendimento, p.UNIDADE as unidadeAcabado, 
        a.RDX_PRODUTO as idProdutoAcabado, c.DESCRICAO as nomeProdutoComposicao, c.IDX_LINHA as classificacao, 
        c.PK_PRODUTO as idProdutoComposicao, a.QUANTIDADE as qtdProdutoComposicao, a.UN as unidadeComposicao, p.L_QUANTIDADE as qtdProdutoEvento, a.DTINC
    from TPAPRODCOMPOSICAO as a 
        inner join TPAPRODUTO as c on a.IDX_PRODUTO = c.PK_PRODUTO
        inner join TPAMOVTOPED as p on a.RDX_PRODUTO = p.IDX_PRODUTO
        inner join TPADOCTOPED as e on p.RDX_DOCTOPED = e.PK_DOCTOPED
        inner join TPAPRODUTO as ca on p.IDX_PRODUTO = ca.PK_PRODUTO
    where e.TPDOCTO = 'EC' 
        and e.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and e.SITUACAO = 'Z'
        and c.OPSUPRIMENTOMP = 'S'
    or e.TPDOCTO = 'EC' 
        and e.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and e.SITUACAO = 'B'
        and c.OPSUPRIMENTOMP = 'S'
    or e.TPDOCTO = 'OR' 
        and e.DTEVENTO between '{dataInicio}' and '{dataFim}'
        and e.SITUACAO = 'V'
        and c.OPSUPRIMENTOMP = 'S'
    or e.TPDOCTO = 'OR' 
        and e.DTEVENTO between '{dataInicio}' and '{dataFim}'
        and e.SITUACAO = 'B'
        and c.OPSUPRIMENTOMP = 'S'
    order by p.DESCRICAO
    """
    produtosComposicao = receberDados(queryProdutosComposicao)
    return produtosComposicao

#Query que busca somente os pedidos feitos no meio do período pesquisado
#para serem entregues naquela semana.
#Com esses dados, mesmo depois que o usuário tiver buscado os pedidos para essa
#semana, caso entre um pedido para aquela semana depois que ele já tiver feito
#a requisição, ele será informado.
def getPedidosMeioSemana(dataInicio, dataFim):
    queryPedidosMeioSemana = f"""
    select 
        e.PK_DOCTOPED as idEvento, e.NOME as nomeEvento, e.DOCUMENTO as documento, e.DTEVENTO as dataEvento, e.DTPREVISAO as dataPrevisao, e.DATA as dataPedido, p.PK_MOVTOPED as idMovtoped, 
        ca.IDX_LINHA as linha, p.DESCRICAO as nomeProdutoAcabado, ca.RENDIMENTO as rendimento, p.UNIDADE as unidadeAcabado, 
        a.RDX_PRODUTO as idProdutoAcabado, c.DESCRICAO as nomeProdutoComposicao, c.IDX_LINHA as classificacao, 
        c.PK_PRODUTO as idProdutoComposicao, a.QUANTIDADE as qtdProdutoComposicao, a.UN as unidadeComposicao, p.L_QUANTIDADE as qtdProdutoEvento, a.DTINC
    from TPAPRODCOMPOSICAO as a 
        inner join TPAPRODUTO as c on a.IDX_PRODUTO = c.PK_PRODUTO
        inner join TPAMOVTOPED as p on a.RDX_PRODUTO = p.IDX_PRODUTO
        inner join TPADOCTOPED as e on p.RDX_DOCTOPED = e.PK_DOCTOPED
        inner join TPAPRODUTO as ca on p.IDX_PRODUTO = ca.PK_PRODUTO
    where e.TPDOCTO = 'EC' 
        and e.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and e.DATA > '{dataInicio}'
        and e.DTPREVISAO < '{dataFim}'
        and e.SITUACAO = 'Z'
        and c.OPSUPRIMENTOMP = 'S'
    or e.TPDOCTO = 'EC' 
        and e.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and e.DATA > '{dataInicio}'
        and e.DTPREVISAO < '{dataFim}'
        and e.SITUACAO = 'B'
        and c.OPSUPRIMENTOMP = 'S'
    or e.TPDOCTO = 'OR' 
        and e.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and e.DATA > '{dataInicio}'
        and e.DTPREVISAO < '{dataFim}'
        and e.SITUACAO = 'V'
        and c.OPSUPRIMENTOMP = 'S'
    or e.TPDOCTO = 'OR' 
        and e.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and e.DATA > '{dataInicio}'
        and e.DTPREVISAO < '{dataFim}'
        and e.SITUACAO = 'B'
        and c.OPSUPRIMENTOMP = 'S'
    order by p.DESCRICAO
    """
    
    pedidosMeioSemana = receberDados(queryPedidosMeioSemana)
    return pedidosMeioSemana

#Query que busca os produtos usados na composição dos semi-acabados, que são
#massas e recheios que vão nas receitas prontas, e que também tem que ser 
#requisitados no estoque.
def getCompSemiAcabados(dataInicio, dataFim):
    queryComposicao = f"""
    SELECT 
    C.IDX_PRODUTO as idProduto, 
    P.DESCRICAO as nomeProdutoComposicao, 
    C.UN as unidadeProdutoComposicao, 
    C.QUANTIDADE as qtdProdutoComposicao, 
    P.IDX_LINHA as classificacao, 
    P2.PK_PRODUTO as idProdutoAcabado, 
    P2.DESCRICAO as nomeProdutoAcabado, 
    P2.RENDIMENTO1 AS rendimento,
    C.DTINC 
FROM 
    TPAPRODCOMPOSICAO AS C
    INNER JOIN TPAPRODUTO AS P ON C.IDX_PRODUTO = P.PK_PRODUTO
    INNER JOIN TPAPRODUTO AS P2 ON C.RDX_PRODUTO = P2.PK_PRODUTO
WHERE 
    C.RDX_PRODUTO IN  (
        SELECT 
            DISTINCT c.PK_PRODUTO
        FROM 
            TPAPRODCOMPOSICAO as a 
            INNER JOIN TPAPRODUTO as c ON a.IDX_PRODUTO = c.PK_PRODUTO
            INNER JOIN TPAMOVTOPED as p ON a.RDX_PRODUTO = p.IDX_PRODUTO
            INNER JOIN TPADOCTOPED as e ON p.RDX_DOCTOPED = e.PK_DOCTOPED
            INNER JOIN TPAPRODUTO as ca ON p.IDX_PRODUTO = ca.PK_PRODUTO
        WHERE 
            e.DTPREVISAO BETWEEN '{dataInicio}' AND '{dataFim}'
            AND e.SITUACAO IN ('Z', 'B', 'V') -- Verifica se SITUACAO está em um conjunto de valores
            AND c.OPSUPRIMENTOMP = 'S'
            AND (e.TPDOCTO = 'EC' OR e.TPDOCTO = 'OR') -- Verifica se TPDOCTO é 'EC' ou 'OR'
    )
    AND P.OPSUPRIMENTOMP = 'S'
ORDER BY P.DESCRICAO;
    """
    composicaoSemiAcabados = receberDados(queryComposicao)
    return composicaoSemiAcabados

#Query que busca os semi-acabados que são pedidos de última hora.
def getSemiAcabadosMeioSemana(dataInicio, dataFim):
    query = f"""
    SELECT 
        C.IDX_PRODUTO as idProduto, 
        P.DESCRICAO as nomeProdutoComposicao, 
        C.UN as unidadeProdutoComposicao, 
        C.QUANTIDADE as qtdProdutoComposicao, 
        P.IDX_LINHA as classificacao, 
        P2.PK_PRODUTO as idProdutoAcabado, 
        P2.DESCRICAO as nomeProdutoAcabado, 
        P2.RENDIMENTO1 AS rendimento,
        C.DTINC  
    FROM 
        TPAPRODCOMPOSICAO AS C
        INNER JOIN TPAPRODUTO AS P ON C.IDX_PRODUTO = P.PK_PRODUTO
        INNER JOIN TPAPRODUTO AS P2 ON C.RDX_PRODUTO = P2.PK_PRODUTO
    WHERE 
    C.RDX_PRODUTO IN  (
        SELECT 
            DISTINCT c.PK_PRODUTO
        FROM 
            TPAPRODCOMPOSICAO as a 
            INNER JOIN TPAPRODUTO as c ON a.IDX_PRODUTO = c.PK_PRODUTO
            INNER JOIN TPAMOVTOPED as p ON a.RDX_PRODUTO = p.IDX_PRODUTO
            INNER JOIN TPADOCTOPED as e ON p.RDX_DOCTOPED = e.PK_DOCTOPED
            INNER JOIN TPAPRODUTO as ca ON p.IDX_PRODUTO = ca.PK_PRODUTO
        WHERE 
            e.DTPREVISAO BETWEEN '{dataInicio}' AND '{dataFim}'
            and e.DATA > '{dataInicio}'
			and e.DTPREVISAO < '{dataFim}'
            AND e.SITUACAO IN ('Z', 'B', 'V') -- Verifica se SITUACAO está em um conjunto de valores
            AND c.OPSUPRIMENTOMP = 'S'
            AND (e.TPDOCTO = 'EC' OR e.TPDOCTO = 'OR') -- Verifica se TPDOCTO é 'EC' ou 'OR'
    )
    AND P.OPSUPRIMENTOMP = 'S'
        ORDER BY 
    P.DESCRICAO;
    """
    
    composicaoSemiAcabados = receberDados(query)
    return composicaoSemiAcabados
    
#Query que busca ajustes feitos nos pedidos, aumentos ou diminuições solicitada
#pelo cliente.
def getAjustes(dataInicio, dataFim):
    queryAjustes = f"""
    select A.IDX_MOVTOPED AS idMovtoped, V.IDX_PRODUTO AS idProduto, V.DESCRICAO AS nomeProduto, A.QUANTIDADE AS ajuste, A.PRECO AS precoAjuste from TPAAJUSTEPEDITEM AS A 
        inner join TPAMOVTOPED AS V ON A.IDX_MOVTOPED = V.PK_MOVTOPED
        inner join TPADOCTOPED AS E ON V.RDX_DOCTOPED = E.PK_DOCTOPED
        inner join TPAPRODUTO AS P ON V.IDX_PRODUTO = P.PK_PRODUTO
    where e.TPDOCTO = 'EC' 
        and E.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and E.SITUACAO = 'Z'
        and P.OPSUPRIMENTOMP = 'S'
    or e.TPDOCTO = 'EC' 
        and E.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and E.SITUACAO = 'B'
        and P.OPSUPRIMENTOMP = 'S'
    or e.TPDOCTO = 'OR' 
        and E.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and E.SITUACAO = 'V'
        and P.OPSUPRIMENTOMP = 'S'
    or e.TPDOCTO = 'OR' 
        and E.DTPREVISAO between '{dataInicio}' and '{dataFim}'
        and E.SITUACAO = 'B'
        and P.OPSUPRIMENTOMP = 'S'
    ORDER BY V.DESCRICAO
    """
    ajustes = receberDados(queryAjustes)
    return ajustes

#Query que busca o saldo de estoque do produto.
def getEstoque():
    queryEstoque = """
    WITH RankedResults AS (
        SELECT 
            E.RDX_PRODUTO,
            E.SALDOESTOQUE,
            E.DTULTCPA,
            P.DESCRICAO,
            P.UN,
            ROW_NUMBER() OVER (PARTITION BY RDX_PRODUTO ORDER BY DTULTCPA DESC) AS Rank
        FROM TPAESTOQUE AS E INNER JOIN TPAPRODUTO AS P ON E.RDX_PRODUTO = P.PK_PRODUTO 
        WHERE E.DTULTCPA IS NOT NULL
    )
    SELECT
        RDX_PRODUTO,
        SALDOESTOQUE,
        DTULTCPA,
        DESCRICAO,
        UN
    FROM RankedResults
    WHERE Rank = 1
    ORDER BY RDX_PRODUTO
    """
    estoque = receberDados(queryEstoque)
    return estoque
