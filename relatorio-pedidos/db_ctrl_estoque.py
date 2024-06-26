import sqlite3

caminho_bd = '//192.168.1.42/producao/controle_estoque/controle_estoque.db'

def create_sqlite_database(filename):
    #Cria conexão com banco de dados SQLite
    conn = None
    try:
        conn = sqlite3.connect(filename)
        print(sqlite3.sqlite_version)
        # criar_tabela()
        add_produto()
        add_sa()
        #getEstoqueCompleto()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def criar_tabela():
    query = [
        """
            CREATE TABLE IF NOT EXISTS ctrl_estoque (
                id INTEGER PRIMARY KEY,
                pkProduto int NOT NULL,
                descricao text NOT NULL,
                saldo int NOT NULL,
                unidade text NOT NULL,
                dataMov text NOT NULL,
                tipoMov text NOT NULL,
                motivo text NOT NULL
                
            );
        """
    ]
    
    try:
        with sqlite3.connect(caminho_bd) as conn:
            cursor = conn.cursor()
            for statement in query:
                cursor.execute(statement)
            conn.commit()
        print("Tabela 'ctrl_estoque' criada.")
    except sqlite3.Error as e:
        print(e)

def criarTblControleSA():
    query = """
        CREATE TABLE IF NOT EXISTS ctrl_semi_acabados (
            id INTEGER PRIMARY KEY,
            idxProduto int NOT NULL,
            descricao text NOT NULL,
            saldo int NOT NULL,
            unidade text NOT NULL,
            dataMov text NOT NULL,
            tipoMov text NOT NULL,
            motivo text NOT NULL
        )
    """
    try:
        with sqlite3.connect(caminho_bd) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
        print("Tabela 'ctrl_semi_acabados' criada.")
    except sqlite3.Error as e:
        print(e)

def adicionarEstoque(att):
    query = '''
        INSERT INTO ctrl_estoque (pkProduto, descricao, saldo, unidade, dataMov, tipoMov, motivo) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    
    try:
        with sqlite3.connect(caminho_bd) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (att['pkProduto'], att['descricao'], att['saldo'], att['unidade'], att['dataMov'],
                                   att['tipoMov'], att['motivo']))
            conn.commit()
    except sqlite3.Error as e:
        print(e)


def addEstoqueSA(att):
    query = '''
        INSERT INTO ctrl_semi_acabados (idxProduto, descricao, saldo, unidade, dataMov, tipoMov, motivo)
            VALUES (?, ?, ?)
    '''
    
    try:
        with sqlite3.connect(caminho_bd) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (att['idxProduto'], att['descricao'], att['saldo'], att['unidade'], att['dataMov'],
                                   att['tipoMov'], att['motivo']))
            conn.commit()
    except sqlite3.Error as e:
        print(e)

def add_produto():
    sql = '''INSERT INTO ctrl_estoque (pkProduto, descricao, saldo, unidade, dataMov, tipoMov, motivo) 
        VALUES (?, ?, ?, ?, ?, ?, ?)'''
    
    try:
        with sqlite3.connect(caminho_bd) as conn:
            #produto = ('Coxinha de Frango com Catupiry', 3500, '2024-06-10')
            lst_produtos = [
                (3851, 'Abacate', 3000, 'UN', '25/06/2024', 'soma', ''),
                (2995, 'Abobora Moranga', 3000, 'UN', '25/06/2024', 'soma', ''),
                (315, 'Açafrão', 3000, 'UN', '25/06/2024', 'soma', '')
            ]
            cursor = conn.cursor()
            for p in lst_produtos:
                cursor.execute(sql, p)
                conn.commit()
        print('Produto criado')
    except sqlite3.Error as e:
        print(e)

def add_sa():
    sql = '''INSERT INTO ctrl_semi_acabados (idxProduto, descricao, saldo, unidade, dataMov, tipoMov, motivo) 
        VALUES (?, ?, ?, ?, ?, ?, ?)'''
    
    try:
        with sqlite3.connect(caminho_bd) as conn:
            #produto = ('Coxinha de Frango com Catupiry', 3500, '2024-06-10')
            lst_produtos = [
                (3030, 'Massa p/ coxinha', 3000, 'KG', '25/06/2024', 'soma', '')
            ]
            cursor = conn.cursor()
            for p in lst_produtos:
                cursor.execute(sql, p)
                conn.commit()
        print('Produto criado')
    except sqlite3.Error as e:
        print(e)

def getEstoqueCompleto():
    try:
        with sqlite3.connect(caminho_bd) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM ctrl_estoque')
            rows = cursor.fetchall()
            produtos = [dict(row) for row in rows]
            return produtos
    except sqlite3.Error as e:
        print(e)

def getEstoqueSA():
    try:
        with sqlite3.connect(caminho_bd) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM ctrl_semi_acabados')
            rows = cursor.fetchall()
            produtos = [dict(row) for row in rows]
            return produtos
    except sqlite3.Error as e:
        print(e)

def buscarProdutoId(produto_id):
    try:
        with sqlite3.connect(caminho_bd) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM ctrl_estoque WHERE pkProduto = {produto_id}')
            row = cursor.fetchone()
            produto = dict(row)
            return produto
    except sqlite3.Error as e:
        print(e)



def atualizarSaldoEstoque(produto_id, qtd):
    try:
        with sqlite3.connect(caminho_bd) as conn:
            cursor = conn.cursor()
            query = f'''
                UPDATE ctrl_estoque SET saldo={qtd} WHERE pkProduto = {produto_id} 
            '''
            cursor.execute(query)
            conn.commit()
    except sqlite3.Error as e:
        print(e)

def excluirLinha(id_linha):
    try:
        with sqlite3.connect(caminho_bd) as conn:
            cursor = conn.cursor()
            query = f'''
                DELETE FROM ctrl_estoque WHERE id = {id_linha}
            '''
            cursor.execute(query)
            conn.commit()
    except sqlite3.Error as e:
        print(e)

def excluirTabela(nome_tabela):
    try:
        with sqlite3.connect(caminho_bd) as conn:
            cursor = conn.cursor()
            query = f'''
                DROP TABLE IF EXISTS {nome_tabela}
            '''
            cursor.execute(query)
            conn.commit()
    except sqlite3.Error as e:
        print(e)

# if __name__ == '__main__':
#     create_sqlite_database("controle_estoque.db")