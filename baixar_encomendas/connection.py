from sqlalchemy import create_engine, text
import pandas as pd
import json

#Conexão banco de testes
# conexao = (
#     "mssql+pyodbc:///?odbc_connect=" + 
#     "DRIVER={ODBC Driver 17 for SQL Server};" +
#     "SERVER=192.168.1.137;" +
#     "DATABASE=SOUTTOMAYOR;" +
#     "UID=Sa;" +
#     "PWD=P@ssw0rd2023"
# )

#Conexão no banco principal
conexao = (
    "mssql+pyodbc:///?odbc_connect=" + 
    "DRIVER={ODBC Driver 17 for SQL Server};" +
    "SERVER=192.168.1.43;" +
    "DATABASE=SOUTTOMAYOR;" +
    "UID=Sa;" +
    "PWD=P@ssw0rd2023@#$"
)

engine = create_engine(conexao, pool_pre_ping=True)

#Executa a query e armazena os dados em uma variável
#Retorna os dados convertidos para json
def receberDados(query):
    response = pd.read_sql_query(query, engine)
    resultadosJson = response.to_json(orient='records')
    dadosDesserializados = json.loads(resultadosJson)
    return dadosDesserializados

#Query que busca os produtos usados na composição das receitas
def getEncomendasAutorizadas(dataInicio, dataFim):
    query =  f"""        
        SELECT PK_DOCTOPED AS idEvento, NOME AS nomeEvento, DOCUMENTO, TPDOCTO AS tipoDocumento, DATA AS dataCadastro, 
        SITUACAO FROM TPADOCTOPED 
            WHERE DATA BETWEEN '{dataInicio}' AND '{dataFim}'
        AND SITUACAO = 'Z' AND PARCIAL = 'S'
    """
    encomendas = receberDados(query)

    return encomendas

def getEncomendaEspecifica(n_documento):
    query = f"""
        SELECT PK_DOCTOPED AS idEvento, NOME AS nomeEvento, DOCUMENTO, TPDOCTO AS tipoDocumento, DATA AS dataCadastro, 
        SITUACAO FROM TPADOCTOPED 
            WHERE DOCUMENTO = {n_documento}
        AND SITUACAO = 'Z'
    """
    encomenda = receberDados(query)
    return encomenda

def updateEncomenda(num_documento):
    query = f"""UPDATE TPADOCTOPED
        SET SITUACAO = 'B'
    WHERE DOCUMENTO = :num_documento AND TPDOCTO = 'EC'"""
    print(num_documento)
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query), {"num_documento":num_documento})
            connection.execute(text("COMMIT"))
            print(f"{result.rowcount} linhas foram atualizadas.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")