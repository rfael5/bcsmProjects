class ConexaoBD:
    def __init__(self):
        self.conexao = (
            "mssql+pyodbc:///?odbc_connect=" + 
            "DRIVER={ODBC Driver 17 for SQL Server};" +
            "SERVER=localhost;" +
            "DATABASE=SOUTTOMAYOR;" +
            "UID=Sa;" +
            "PWD=P@ssw0rd2023"
        )

    def get_conexao(self):
        return self.conexao
    
    
    