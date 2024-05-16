import json
import pandas as pd
from sqlalchemy import create_engine

from conexaobd import ConexaoBD
conexao_bd = ConexaoBD()
conexao = conexao_bd.get_conexao()
engine = create_engine(conexao, pool_pre_ping=True)


def receberDados(query):
    response = pd.read_sql_query(query, engine)
    resultadosJson = response.to_json(orient='records')
    dadosDesserializados = json.loads(resultadosJson)
    return dadosDesserializados