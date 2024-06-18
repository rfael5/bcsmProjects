import db_ctrl_estoque

def addSaldo(produto, qtd):
    db_ctrl_estoque.aumentoSaldoEstoque(produto, qtd)
    print(f"Atualização: {produto}")