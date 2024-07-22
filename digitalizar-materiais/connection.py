from sqlalchemy import create_engine
import pandas as pd
import json
import environment

engine = create_engine(environment.conexao, pool_pre_ping=True)

def getMateriais():
    query = """
        SELECT DESCRICAO FROM TPAPRODUTO WHERE IDX_NEGOCIO = 'Locação de Materiais'
    """
    response = pd.read_sql_query(query, engine)
    resultadosJson = response.to_json(orient='records')
    dadosDesserializados = json.loads(resultadosJson)
    return dadosDesserializados

def getEvento(num_or):
    query = f"""
        SELECT D.NOME, D.DTEVENTO, D.TPDOCTO, D.DOCUMENTO, E.CONVIDADOS, E.LOCAL, T.DESCRICAO, F.NOMEINTERNO FROM TPADOCTOPED AS D
            INNER JOIN TPAFUNCIONARIO AS F ON D.IDX_VENDEDOR1 = F.PK_FUNCIONARIO
            INNER JOIN TPAEVENTOORC AS E ON D.IDX_DOCTOEVENTO = E.PK_EVENTOORC
            INNER JOIN TPAEVENTOTP AS T ON E.IDX_EVENTOTP = T.PK_EVENTOTP
        WHERE D.TPDOCTO = 'OR' AND D.DOCUMENTO = {num_or}
    """
    response = pd.read_sql_query(query, engine)
    resultadosJson = response.to_json(orient='records')
    dadosDesserializados = json.loads(resultadosJson)
    return dadosDesserializados
