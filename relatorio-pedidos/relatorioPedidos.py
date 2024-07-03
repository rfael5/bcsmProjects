import pandas as pd
import numpy as np
import json
from datetime import datetime, timezone
from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import messagebox

import connection
import formatacao_objeto
import tabelas
import criacao_planilha
import db_ctrl_estoque
import controleEstoqueService

# db_ctrl_estoque.excluirTabela('ctrl_estoque')
# db_ctrl_estoque.excluirTabela('ctrl_semi_acabados')
# # controleEstoque = controleEstoqueService.EstoqueService()
# # controleEstoque.formatarProdutosControle()
# db_ctrl_estoque.criar_tabela()
# db_ctrl_estoque.criarTblControleSA()
# db_ctrl_estoque.add_produto()
# db_ctrl_estoque.add_sa()
# db_ctrl_estoque.getEstoqueCompleto()
# db_ctrl_estoque.getEstoqueSA()

#Retornam as datas para um formato legivel
def formatarData(data):
    data_objeto = datetime.strptime(data, '%d/%m/%Y')
    data_formatada = data_objeto.strftime('%Y%m%d')
    return data_formatada

def formatarDataPedido(data):
    milliseconds_since_epoch = data
    seconds_since_epoch = milliseconds_since_epoch / 1000
    date_object = datetime.fromtimestamp(seconds_since_epoch, timezone.utc)
    formatted_date = date_object.strftime('%d/%m/%Y')
    return formatted_date

def recuperarHoraAtual():
    data_hora_atual = datetime.now()
    formato = "%Y-%m-%d_%H-%M-%S"
    data_hora_formatada = data_hora_atual.strftime(formato)
    return data_hora_formatada

#Pega a data inserida na interface, formata ela, e passa como parâmetro
#na função que executa a query.
def setarData(tipo_requisicao):
    dataInicio = dtInicio.get()
    dtInicioFormatada = formatarData(dataInicio)
    dataFim = dtFim.get()
    dtFimFormatada = formatarData(dataFim)
    if dtInicioFormatada < dtFimFormatada:
        global ajustes_periodo
        global ajustes_ano_anterior
        if tipo_requisicao == 'ano-atual':
            #Armazena nas variáveis abaixo a lista de produtos da composição de acabados, 
            #de semi-acabados e de ajustes do periodo.
            produtosComposicao = connection.getProdutosComposicao(dtInicioFormatada, dtFimFormatada)
            composicaoSemiAcabados = connection.getCompSemiAcabados(dtInicioFormatada, dtFimFormatada)
            ajustes = connection.getAjustes(dtInicioFormatada, dtFimFormatada)
        else:
            #Se o parametro tipo_requisicao for diferente de ano-atual, essa função retorna os
            #pedidos do mesmo periodo selecionado, porém para o ano passado.
            n_dt_inicio = int(dtInicioFormatada) - 10000
            n_dt_fim = int(dtFimFormatada) - 10000
            produtosComposicao = connection.getProdutosComposicao(n_dt_inicio, n_dt_fim)
            composicaoSemiAcabados = connection.getCompSemiAcabados(n_dt_inicio, n_dt_fim)
            ajustes = connection.getAjustes(n_dt_inicio, n_dt_fim)
                
        if len(produtosComposicao) == 0:
            tamanhoLista = 0
            tabelas.criarTabela(secondFrame)
            return tamanhoLista
        else:
            #Retorna o saldo de estoque
            estoque = connection.getEstoque()
            
            #Corrige esse valor com os ajustes feitos pelo cliente
            ajustesAplicados = formatacao_objeto.aplicarAjustes(produtosComposicao, ajustes)
            
            #Pega a quantidade de cada produto usado na receita final, e multiplica pelo
            #número de pedidos dessa receita.
            produtosQtdAjustada = formatacao_objeto.calcularQtdProducao(ajustesAplicados)
            
            if tipo_requisicao == 'ano-atual':
                ajustes_periodo = ajustesAplicados
            else:
                ajustes_ano_anterior = ajustesAplicados
            #insere na lista uma coluna com o saldo de estoque
            formatacao_objeto.adicionarEstoque(produtosQtdAjustada, estoque)
            
            #Igualar unidades do produto a unidade de estoque.
            #formatacao_objeto.igualarUnEstoque(produtosQtdAjustada)
            
            #Soma todos os pedidos de cada produto, chegando ao valor total de pedidos para cada um
            mp_acabados = formatacao_objeto.somarProdutosEvento(produtosQtdAjustada)
            #Faz as operações acima com a lista de composição dos semi-acabados
            mp_semiAcabados = criarDictSemiAcabados(mp_acabados, composicaoSemiAcabados, estoque)
            #Une a lista dos acabados com os semi-acabados em uma só, e retorna a lista final
            produtos = formatacao_objeto.unirListasComposicao(mp_acabados, mp_semiAcabados)
            return produtos 
    else:
        tabelas.criarTabela(secondFrame)
        return None

def setarDataMotivo(tipo):
    dataInicioStr = dtInicioMotivos.get()
    dataFimStr = dtFimMotivos.get()

    # Convertendo as strings para objetos datetime
    formato = '%d/%m/%Y'
    dataInicio = datetime.strptime(dataInicioStr, formato)
    dataFim = datetime.strptime(dataFimStr, formato).replace(hour=23, minute=59)
    
    print (dataInicio)
    print (dataFim) 
    
    if(dataInicio < dataFim):
        if(tipo == 'acabados'):
            estoqueCompleto = db_ctrl_estoque.getEstoqueDT(dataInicio, dataFim)
            return estoqueCompleto
        else:
            estoqueCompletoSA = db_ctrl_estoque.getEstoqueDT_SA(dataInicio, dataFim)
            return estoqueCompletoSA
    else:
        return None

#Mesmo fluxo da função acima setarData(), porém para os pedidos feitos
#depois que a lista ja foi gerada para serem entregues naquela mesma semana.
# def setarDataPedidosMeioSemana(tipo_requisicao):
#     if tipo_requisicao == 'btn':
#         dataInicio = dt_inicio_semana.get()
#         dtInicioFormatada = formatarData(dataInicio)
#         dataFim = dt_fim_semana.get()
#         dtFimFormatada = formatarData(dataFim)
#     elif tipo_requisicao == 'timer':
#         data_atual = datetime.now() - timedelta(days=1)
#         dtInicioFormatada = data_atual.strftime('%Y%m%d')
#         #dtInicioFormatada = '20240422'
#         dataFim = dt_fim_semana.get()
#         dtFimFormatada = formatarData(dataFim)

#     #checarEventosNaLista()
#     global ajustes_meio_semana
#     pedidosMeioSemana = connection.getPedidosMeioSemana(dtInicioFormatada, dtFimFormatada)
#     semiacabados = connection.getSemiAcabadosMeioSemana(dtInicioFormatada, dtFimFormatada)
#     ajustes = connection.getAjustes(dtInicioFormatada, dtFimFormatada)
    
#     if len(pedidosMeioSemana) == 0:
#         tamanho_lista = 0
#         return tamanho_lista
#     else:
#         estoque = connection.getEstoque()
#         produtosQtdAjustada = formatacao_objeto.calcularQtdProducao(pedidosMeioSemana)
#         ajustes_meio_semana = formatacao_objeto.aplicarAjustes(produtosQtdAjustada, ajustes)
#         formatacao_objeto.adicionarEstoque(ajustes_meio_semana, estoque)
#         mp_acabados = formatacao_objeto.somarProdutosEvento(ajustes_meio_semana)
#         mp_semiAcabados = criarDictSemiAcabados(mp_acabados, semiacabados, estoque)
#         produtos = formatacao_objeto.unirListasComposicao(mp_acabados, mp_semiAcabados)
        
#         return produtos

#Função para o usuário filtrar a lista e visualizar os produtos
#por linha de produção, caso queiram ver somente os pedidos para
#receitas de sal, doce, confeitaria, etc.
def filtrarListas(tipoFiltro, listaCompleta):
    if listaCompleta == None:
        return None
    elif listaCompleta == 0:
        return 0
    else:
        listaFiltrada = list(filter(lambda produto:produto['linha'] == tipoFiltro, listaCompleta))
        return listaFiltrada

#Função para caso o usuário queira gerar uma planilha excel somente com
#os produtos de determinada linha de produção.
def separarProdutosEvento(listaProdutos):
    if trazerTodos.get() or filtrarSal.get() or filtrarDoces.get() or filtrarConfeitaria.get() or filtrarCanapes.get() or filtrarRefeicoes.get() == 1:
        if trazerTodos.get() == 1:       
            criacao_planilha.gerarArquivoExcel('LISTA_PEDIDOS', listaProdutos)
        if filtrarSal.get() == 1:
            listaSal = filtrarListas('Sal', listaProdutos)
            criacao_planilha.gerarArquivoExcel('SAL',listaSal)
        if filtrarDoces.get() == 1:
            listaDoces = filtrarListas('Doces', listaProdutos)
            criacao_planilha.gerarArquivoExcel('DOCES',listaDoces)
        if filtrarRefeicoes.get() == 1:
            listaRefeicoes = filtrarListas('Refeições', listaProdutos)
            criacao_planilha.gerarArquivoExcel('REFEICOES',listaRefeicoes)
        if filtrarConfeitaria.get() == 1:
            listaConfeitaria = filtrarListas('Confeitaria', listaProdutos)
            criacao_planilha.gerarArquivoExcel('CONFEITARIA',listaConfeitaria)
        if filtrarCanapes.get() == 1:
            listaCanapes = filtrarListas('Canapés', listaProdutos)
            criacao_planilha.gerarArquivoExcel('CANAPES',listaCanapes)
    else:
        messagebox.showinfo("Seleção Inválida", "Selecione o tipo de planilha a ser gerado.")
        return None

#Função que retorna a lista completa ou filtrada para ser inserida na tabela da interface.
def selecionarOpcao(event):
    todosProdutos = setarData('ano-atual')
    valorSelecionado = combo.get()
    if valorSelecionado == 'Todos os produtos':
        return todosProdutos
    else:
        produtos_filtrados = filtrarListas(valorSelecionado, todosProdutos)
        return produtos_filtrados


def formatarDataPedido(data):
    milliseconds_since_epoch = data
    seconds_since_epoch = milliseconds_since_epoch / 1000
    date_object = datetime.fromtimestamp(seconds_since_epoch, timezone.utc)
    formatted_date = date_object.strftime('%d/%m/%Y')
    return formatted_date

#Quando o usuário seleciona um produto na lista e clica no botão 'Ver todos os eventos'
#Essa função é executada e mostra as receitas em que aquele produto vai ser usado, os
#clientes que as pediram, e a data de entrega.
def verTodosEventos(lista_produtos, tabela):
    indice = tabela.selection()
    if indice:
        produto = tabela.item(indice)['values'][0]
        produtosFiltrados = list(filter(lambda evento:int(evento['idProdutoComposicao']) == int(produto), lista_produtos))
        abrirOutraJanela(produtosFiltrados)

#Essa função abre uma nova janela com os dados retornados pela função verTodosEventos()
def abrirOutraJanela(produtosFiltrados):
    nova_janela = Toplevel(root)
    nova_janela.title("Nova Janela")
    nova_janela.geometry("950x400")
    produto_selecionado = produtosFiltrados[0]['nomeProdutoComposicao']
    label = Label(nova_janela, text=f'{produto_selecionado}')
    label.grid(padx=20, pady=20)
    
    tabelas.criarTabelaEvento(nova_janela)
    for x in produtosFiltrados:
        cliente = x['nomeEvento']
        produto = x['nomeProdutoAcabado']
        dataPedido = formatarDataPedido(x['dataPedido'])
        dataPrevisao = formatarDataPedido(x['dataPrevisao'])
        qtdEvento = x['qtdProdutoEvento']
        unidade = x['unidadeAcabado']
        data = (cliente, produto, dataPedido, dataPrevisao, qtdEvento, unidade)
        tabelas.tabelaEventos.insert(parent='', index=0, values=data)
    
#def mensagemBanco():

#verQtdAnoPassado e abrirJanelaAnoAnterior fazem as mesmas coisas das duas funções acima,
#porém mostrando os pedidos do ano passado.
def verQtdAnoPassado():
    tst = tabelas.tabela_atual
    prod_ano_passado = setarData('ano-anterior')
    produto = tst
    produtosFiltrados = list(filter(lambda p:int(p['idProdutoComposicao']) == int(produto), prod_ano_passado))
    abrirJanelaAnoAnterior(produtosFiltrados)

def abrirJanelaAnoAnterior(produtosFiltrados):
    j_ano_anterior = Toplevel(root)
    j_ano_anterior.title("Quantidade ano anterior")
    j_ano_anterior.geometry("1250x400")
    tabelas.criarTabelaAnoAnterior(j_ano_anterior)
    for x in produtosFiltrados:
        id = x['idProdutoComposicao']
        produto = x['nomeProdutoComposicao']
        linha = x['linha']
        total = x['totalProducao']
        unidade = x['unidade']
        if x['produtoAcabado'] == True:
            produto_acabado = 'Comp. acabados'
        else:
            produto_acabado = 'Comp. semi-acabados'            
        data = (id, produto, linha, total, unidade, produto_acabado)
        tabelas.tbl_ano_anterior.insert(parent='', index=0, values=data)


#Recupera os pedidos feitos depois que a lista já foi gerada e insere na
#tabela na interface.
# def inserirTabelaTeste(tipo_requisicao):
#     produtos_meio_semana = setarDataPedidosMeioSemana(tipo_requisicao)
    
#     if produtos_meio_semana == 0 or produtos_meio_semana == None:
#         mensagem_banco.configure(text='Nenhum evento foi marcado hoje para essa semana')
#     else:
#         qtd_eventos_tabela = len(tabelas.tabelaSemana.get_children()) + len(tabelas.tabelaSemana_semi.get_children())
#         qtd_eventos_query = len(produtos_meio_semana)
#         if qtd_eventos_tabela != qtd_eventos_query:
#             mensagem_banco.configure(text='Houve marcação de eventos hoje para essa semana.')
#             tabelas.tabelaSemana.delete(*tabelas.tabelaSemana.get_children())
#             tabelas.tabelaSemana_semi.delete(*tabelas.tabelaSemana_semi.get_children())
#             for p in produtos_meio_semana:
#                 id = p['idProdutoComposicao']
#                 nome = p['nomeProdutoComposicao']
#                 classificacao = p['classificacao']
#                 linha = p['linha']
#                 estoque = p['estoque']
#                 unidadeEstoque = p['unidadeEstoque']
#                 totalProducao = p['totalProducao']
#                 unidade = p['unidade']
#                 data = (id, nome, classificacao, linha, estoque, unidadeEstoque, totalProducao, unidade)
#                 if p['produtoAcabado'] == True:
#                     tabelas.tabelaSemana.insert(parent='', index=0, values=data)
#                 else:
#                     tabelas.tabelaSemana_semi.insert(parent='', index=0, values=data)
#         else:
#             return


def formatarListaSemiAcabados(lista, estoque):
    formatacao_objeto.adicionarEstoque(lista, estoque)
    df = pd.DataFrame(lista)
    df['produtoAcabado'] = False
    #Remove caracteres desnecessários que vem na string do nome do produto e da 
    #unidade de medida do produto.
    df['unidade'] = df['unidadeComposicao'].apply(formatacao_objeto.alterarStringUnidade)
    df['nomeProdutoComposicao'] = df['nomeProdutoComposicao'].apply(formatacao_objeto.alterarStringUnidade)
    df['unidadeEstoque'] = df['unidadeEstoque'].apply(formatacao_objeto.alterarStringUnidade)
    #Converte as quantidades dos produtos que estão em grama e ml para kg e litros.
    df['totalProducao'] = df.apply(formatacao_objeto.converterKg, axis=1)
    df['unidade'] = df['unidade'].apply(formatacao_objeto.mudarUnidade)
    
    #Ordena os dados na ordem que devem aparecer na tabela.
    df = df[['idProdutoComposicao', 'nomeProdutoComposicao', 'classificacao', 'linha', 'estoque', 'unidadeEstoque', 'totalProducao', 'unidade', 'produtoAcabado']]

    result = formatacao_objeto.converterPJson(df)
    return result

#Cria um dicionario para inserir os dados da composição dos semi-acabados
#no mesmo formato da composição dos acabados.
def criarDictSemiAcabados(acabados, semiAcabados, estoque):
    dfAcabados = pd.DataFrame(acabados)

    result = dfAcabados.apply(formatacao_objeto.inserirCol_SemiAcabados, semiAcabados=semiAcabados, axis=1)
    
    resultJson = result.to_json(orient='records')
    dadosDesserializados = json.loads(resultJson)
    
    listaFinal = [p for p in dadosDesserializados if p]
    concatenacao = np.concatenate(listaFinal)
    listaJson = concatenacao.tolist()
    listaFormatada = formatarListaSemiAcabados(listaJson, estoque)
    return listaFormatada

#Insere os produtos na tabela na interface.
def inserirNaLista():
    #Retorna os dados já formatados, sem filtro ou filtrados, para serem inseridos na lista.
    produtos = selecionarOpcao(Event)

    #Caso não tenha nenhum pedido no período selecionado ou o período seja inválido, a interface
    #mostra uma mensagem de erro
    if produtos == None:
        messagebox.showinfo('Data inválida', 'Periodo selecionado inválido')
    elif produtos == 0:
        messagebox.showinfo('Lista vazia', 'Não há eventos nesse período de tempo')    
    else:
        #Produtos são ordenados em ordem alfabetica
        produtosOrdenados = sorted(produtos, key=lambda p:p['nomeProdutoComposicao'], reverse=True)
        
        #Sempre que o usuário faz uma nova pesquisa, a tabela é deletada e criada novamente.
        tabelas.table.delete(*tabelas.table.get_children())
        tabelas.tableSemiAcabados.delete(*tabelas.tableSemiAcabados.get_children())
        for p in produtosOrdenados:
            id = p['idProdutoComposicao']
            nome = p['nomeProdutoComposicao']
            classificacao = p['classificacao']
            linha = p['linha']
            estoque = p['estoque']
            unidadeEstoque = p['unidadeEstoque']
            totalProducao = p['totalProducao']
            unidade = p['unidade']
            data = (id, nome, classificacao, linha, estoque, unidadeEstoque, totalProducao, unidade)
            if p['produtoAcabado'] == True:
                tabelas.table.insert(parent='', index=0, values=data)
            else:
                tabelas.tableSemiAcabados.insert(parent='', index=0, values=data)
            
#Função para caso o usuário queira gerar uma planilha com todos os pedidos.
def gerarPlanilha():
    produtos = setarData('ano-atual')
    if produtos == None:
        messagebox.showinfo('Data inválida', 'Periodo selecionado inválido')
    elif produtos == 0:
        messagebox.showinfo('Lista vazia', 'Não há eventos nesse período de tempo') 
    else:
        if radiobutton_variable.get() == 1:
            composicao_acabados = list(filter(lambda produto:produto['produtoAcabado'] == True, produtos))
            separarProdutosEvento(composicao_acabados) 
        elif radiobutton_variable.get() == 2:
            composicao_semiacabados = list(filter(lambda produto:produto['produtoAcabado'] == False, produtos))
            separarProdutosEvento(composicao_semiacabados)


def inserirTabelaMotivos():
    global motivosAcabados
    global motivosSemiAcabados
    motivos = controleEstoqueService.EstoqueService()
    motivosAcabados = motivos.p_controle
    motivosSemiAcabados = motivos.sa_controle
    
    data = setarDataMotivo('acabados')
    dataSA = setarDataMotivo('semi-acabados')
    
    tabelas.tbl_motivo_acabados.delete(*tabelas.tbl_motivo_acabados.get_children())
    tabelas.tbl_motivo_semi_acabados.delete(*tabelas.tbl_motivo_semi_acabados.get_children())
    
    if data is None and dataSA is None:
        messagebox.showerror('Período inválido.', 
                             'Por favor, verifique se os campos da data estão corretos.')
        return
    if not data and not dataSA:
        messagebox.showinfo('Não há alterações.', 
                             'Não há alterações neste período de tempo.')
        return
    else:
        # Inserir motivos acabados
        if data is not None:
            for x in data:
                horaData = x['dataMov']
                horaDataObj = datetime.strptime(horaData, "%Y-%m-%d %H:%M:%S")
                horaDataFormatada = horaDataObj.strftime("%d/%m/%Y, %H:%M:%S")
                if x['tipoMov'] == 'subtracao':
                    id = x['pkProduto']
                    descricao = x['descricao']
                    motivo = x['motivo']
                    quemSolicitou = x['solicitante']
                    subtracao = x['saldo']
                    data = (id, descricao, motivo, quemSolicitou, subtracao, horaDataFormatada)
                    tabelas.tbl_motivo_acabados.insert(parent='', index=0, values=data)
    
        # Inserir motivos semi-acabados
        if dataSA is not None:
            for y in dataSA:
                horaData = y['dataMov']
                horaDataObj = datetime.strptime(horaData, "%Y-%m-%d %H:%M:%S")
                horaDataFormatada = horaDataObj.strftime("%d/%m/%Y, %H:%M:%S")
                if y['tipoMov'] == 'subtracao':
                    id = y['idxProduto']
                    descricao = y['descricao']
                    motivo = y['motivo']
                    quemSolicitou = y['solicitante']
                    subtracao = y['saldo']
                    data = (id, descricao, motivo, quemSolicitou, subtracao, horaDataFormatada)
                    tabelas.tbl_motivo_semi_acabados.insert(parent='', index=0, values=data)
                    
def inserirTabelaControle():
    global prod_estoque
    controleEstoque = controleEstoqueService.EstoqueService()
    
    controleEstoque.formatarProdutosControle()
    prod_estoque = controleEstoque.ctrl_acabados
    tabelas.tbl_controle.delete(*tabelas.tbl_controle.get_children())
    for produto in prod_estoque:
        id = produto['PK_PRODUTO']
        descricao = produto['DESCRICAO']
        un = produto['UN']
        cod_produto = produto['CODPRODUTO']
        saldo = produto['somaQuantidade']
        if saldo >= 0:
            total = 'black'
        else:
            total = 'red'
        data = (id, descricao, un, cod_produto, saldo)
        tabelas.tbl_controle.insert(parent='', index=0, values=data, tags=total)
        #tabelas.tbl_motivo.insert(parent='', index=0, values=(id, descricao, motivo, recuperarHoraAtual()))
    tabelas.tbl_controle.tag_configure("red", foreground="red")
    
    global saprod_estoque
    saprod_estoque = controleEstoque.ctrl_semiacabados
    tabelas.tbl_ctrl_semi.delete(*tabelas.tbl_ctrl_semi.get_children())
    for sa in saprod_estoque:
        id = sa['IDX_PRODUTO']
        produto = sa['DESCRICAO']
        saldo = sa['totalProducao']
        un = sa['UN']
        if saldo >= 0:
            total_sa = 'black'
        else:
            total_sa = 'red'
        data_sa = (id, produto, saldo, un)
        tabelas.tbl_ctrl_semi.insert(parent='', index=0, values=data_sa, tags=total_sa)
    tabelas.tbl_ctrl_semi.tag_configure("red", foreground="red")

def janelaAttEstoque(_tbl, tp_controle, tp_att):
    dados_prod = tabelas.armazenarInfoProduto(Event, _tbl)
    
    if dados_prod == None:
        messagebox.showinfo('Nenhum produto selecionado', 'Selecione um produto na tabela para alterar seu saldo.')
    else:
        global janela_soma
        janela_soma = Toplevel(root)
        janela_soma.title("Atualização estoque")
        janela_soma.geometry("400x300")
        
        if tp_att == 'soma':
            _titulo = 'Atualizar estoque'
            titulo_botao = 'Adicionar'
        else:
            _titulo = 'Subtrair do estoque'
            titulo_botao = 'Subtrair'
        
        titulo_janela = Label(janela_soma, text=f"{dados_prod[1]}", font=("Arial", 14))
        titulo_janela.grid(row=0, padx=(40, 0), pady=(0,20))
        
        lbl_add_saldo = Label(janela_soma, text = f'{_titulo}:')
        lbl_add_saldo.grid(row=1, padx=(40, 0))
        att_var = ''
        att_saldo = Entry(janela_soma, textvariable=att_var, bd=4)
        att_saldo.grid(row=2, padx=(40, 0), pady=(0,20))
        
        lbl_motivo_explicacao = Label(janela_soma, text="Por favor, escreva o motivo da atualização do estoque:")
        lbl_motivo_explicacao.grid(row=3, padx=(40, 0))
        just_var = ''
        motivo = Entry(janela_soma, textvariable=just_var, bd=4)
        motivo.grid(row=4, padx=(40, 0), pady=(0,20))
        
        lbl_motivo_explicacao = Label(janela_soma, text="Por favor, escreva o nome do solicitante:")
        lbl_motivo_explicacao.grid(row=5, padx=(40, 0))
        solicitante_var = ''
        solicitante = Entry(janela_soma, textvariable=solicitante_var, bd=4)
        solicitante.grid(row=6, padx=(40, 0), pady=(0,20))
        
        btn_add = Button(janela_soma, text=f"{titulo_botao}", bg='#C0C0C0', font=("Arial", 16), command=lambda: attSaldo(dados_prod, att_saldo.get(), tp_controle, tp_att, solicitante.get(), motivo.get()))
        btn_add.grid(row=7, sticky='nsew', padx=(40, 0), pady=(0,20))

def attSaldo(produto, att_saldo, tp_controle, tp_att, motivo, solicitante):
    horaData_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    horaData = datetime.strptime(horaData_str, '%Y-%m-%d %H:%M:%S')
    
    if tp_controle == 'acabados':
        novo_produto = {
            "pkProduto": produto[0],
            "descricao": produto[1],
            "saldo": att_saldo,
            "unidade": produto[2],
            "dataMov": horaData,
            "tipoMov": tp_att,
            "motivo": motivo,
            "solicitante": solicitante
        }
        try:
            if tp_att == 'soma':
                novo_produto['saldo'] = abs(float(novo_produto['saldo']))
                db_ctrl_estoque.adicionarEstoque(novo_produto)
            else:
                if not motivo or not solicitante:
                    messagebox.showinfo(
                        'Nenhum motivo ou solicitante', 'Por favor, verifique se os campos motivos e solicitante estão preenchidos corretamente.'
                        )
                    return
                else:
                    novo_produto['saldo'] = -abs(float(novo_produto['saldo']))
                    db_ctrl_estoque.adicionarEstoque(novo_produto)
            db_ctrl_estoque.getEstoqueCompleto()
            
        except Exception as e:
            messagebox.showerror(
                'Erro', f'Ocorreu um erro ao tentar inserir, verifique se os valores estão corretos. {str(e)}'  
            )
            return
            
    else:
        adicao_saldo = {
            "idxProduto":produto[0],
            "descricao":produto[1],
            "saldo":att_saldo,
            "unidade": produto[3],
            "dataMov": horaData,
            "tipoMov": tp_att,
            "motivo": motivo,
            "solicitante": solicitante
        }
        try:
            if tp_att == 'soma':
                adicao_saldo['saldo'] = abs(float(adicao_saldo['saldo']))
                db_ctrl_estoque.addEstoqueSA(adicao_saldo)
            else:
                if not motivo or not solicitante:
                    messagebox.showinfo(
                            'Nenhum motivo ou solicitante', 'Por favor, verifique se os campos motivos e solicitante estão preenchidos corretamente.'
                            )
                    return
                else:
                    adicao_saldo['saldo'] = -abs(float(adicao_saldo['saldo']))
                    db_ctrl_estoque.addEstoqueSA(adicao_saldo)
            db_ctrl_estoque.getEstoqueSA
            
        except Exception as e:
            messagebox.showerror(
            'Erro', f'Ocorreu um erro ao tentar inserir, verifique se os valores estão corretos. {str(e)}'
            )
            return
    
    inserirTabelaControle()
    inserirTabelaMotivos()
    janela_soma.destroy()

def filtrarListas(event, tipo_tabela):
    if tipo_tabela == 'acabados':
        text = input_saldo.get()
        _estoque = prod_estoque
        prod_filtrados = list(filter(lambda produto: text.lower() in produto['DESCRICAO'].lower(), _estoque))
        tabelas.tbl_controle.delete(*tabelas.tbl_controle.get_children())
        for produto in prod_filtrados:
            id = produto['PK_PRODUTO']
            descricao = produto['DESCRICAO']
            un = produto['UN']
            cod_produto = produto['CODPRODUTO']
            saldo = produto['somaQuantidade']
            data = (id, descricao, un, cod_produto, saldo)
            tabelas.tbl_controle.insert(parent='', index=0, values=data)
            
    elif tipo_tabela == 'semi-acabados':
        text = input_saldo_sa.get()
        _estoquesa = saprod_estoque
        prodsa_filtrados = list(filter(lambda prodsa: text.lower() in prodsa['DESCRICAO'].lower(), _estoquesa))
        tabelas.tbl_ctrl_semi.delete(*tabelas.tbl_ctrl_semi.get_children())
        for semiacabado in prodsa_filtrados:
            id = semiacabado['IDX_PRODUTO']
            produto = semiacabado['DESCRICAO']
            saldo = semiacabado['totalProducao']
            un = semiacabado['UN']
            data_sa = (id, produto, saldo, un)
            tabelas.tbl_ctrl_semi.insert(parent='', index=0, values=data_sa)
            
    elif tipo_tabela == 'motivosAcabados':
        text = input_motivo.get() 
        _motivos = motivosAcabados 
        motivos_filtrados = list(filter(lambda motivo: text.lower() in motivo['descricao'].lower(), _motivos))
        tabelas.tbl_motivo_acabados.delete(*tabelas.tbl_motivo_acabados.get_children())
        for motivoA in motivos_filtrados:
            if(motivoA['tipoMov'] == "subtracao"):
                id = motivoA['pkProduto']
                descricao = motivoA['descricao']
                motivo = motivoA['motivo']
                quemSolicitou = motivoA['solicitante']
                subtracao = motivoA['saldo']
                
                horaData = motivoA['dataMov']
                horaDataObj = datetime.strptime(horaData, "%Y-%m-%d %H:%M:%S")
                horaDataFormatada = horaDataObj.strftime("%d/%m/%Y, %H:%M:%S")
                
                data = (id, descricao, motivo, quemSolicitou, subtracao, horaDataFormatada)
                tabelas.tbl_motivo_acabados.insert(parent='', index=0, values=data)
            
    elif tipo_tabela == 'motivosSemiAcabados':
        text = input_motivoSA.get()  
        _semiacabados = motivosSemiAcabados 
        semiacabados_filtrados = list(filter(lambda motivoSA: text.lower() in motivoSA['descricao'].lower(), _semiacabados))
        tabelas.tbl_motivo_semi_acabados.delete(*tabelas.tbl_motivo_semi_acabados.get_children())  
        for motivoSA in semiacabados_filtrados: 
            if(motivoSA['tipoMov'] == "subtracao"):
                id = motivoSA['idxProduto']
                descricao = motivoSA['descricao']
                motivo = motivoSA['motivo']
                quemSolicitou = motivoSA['solicitante']
                subtracao = motivoSA['saldo']
                
                horaData = motivoSA['dataMov']
                horaDataObj = datetime.strptime(horaData, "%Y-%m-%d %H:%M:%S")
                horaDataFormatada = horaDataObj.strftime("%d/%m/%Y, %H:%M:%S")
                
                data = (id, descricao, motivo, quemSolicitou, subtracao, horaDataFormatada)
                tabelas.tbl_motivo_semi_acabados.insert(parent='', index=0, values=data)

#O código abaixo cria a interface que usamos para testar nosso script.

#Tkinter
root = Tk()
root.title("| Gerar pedidos de suprimento |")

root.geometry("1150x800")

notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True)

page1 = Frame(notebook)
notebook.add(page1, text='| Relatório pedidos de suprimento |')

mainFrame = Frame(page1)
mainFrame.pack(fill=BOTH, expand=1)

canvas = Canvas(mainFrame)
canvas.pack(side=LEFT, fill=BOTH, expand=1)
#canvas.grid(row=0, column=0, sticky=EW)

scrollbar = ttk.Scrollbar(mainFrame, orient=VERTICAL, command=canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)
#scrollbar.grid(row=0, rowspan=10, column=1, sticky="ns")

canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e:canvas.configure(scrollregion=canvas.bbox("all")))

secondFrame = Frame(canvas)
canvas.create_window((0, 0), window=secondFrame, anchor="nw")

#incluirLinhaProducao = IntVar(value=1)
semLinhaProducao = IntVar()
filtrarSal = IntVar(value=0)
filtrarDoces = IntVar(value=0)
filtrarRefeicoes = IntVar(value=0)
filtrarConfeitaria = IntVar(value=0)
filtrarCanapes = IntVar(value=0)
trazerTodos = IntVar(value=1)

explicacao = Label(secondFrame, text="Selecione abaixo o período de tempo para o qual você quer gerar a lista de\n pedidos de suprimento.", font=("Arial", 14))
explicacao.grid(row=0, columnspan=2, padx=(150, 0), pady=10, sticky="nsew")

lbl_dtInicio = Label(secondFrame, text="De:", font=("Arial", 14))
lbl_dtInicio.grid(row=1, padx=(0, 190), column=0, sticky="e")

dtInicio = DateEntry(secondFrame, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
dtInicio.grid(row=2, column=0, padx=(150, 0), pady=5, sticky="e")

lbl_dtFim = Label(secondFrame, text="Até:", font=("Arial", 14))
lbl_dtFim.grid(row=1, column=1, padx=(50, 0), pady=5, sticky="w")

dtFim = DateEntry(secondFrame, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
dtFim.grid(row=2, column=1, padx=(50, 0), pady=5, sticky="w")

# c1 = Checkbutton(secondFrame, text='Gerar documento com linha de produção?',variable=incluirLinhaProducao, onvalue=1, offvalue=0, font=("Arial", 14), height=5, width=5, command= lambda:tabelas.atualizarTabela(secondFrame, incluirLinhaProducao))
# c1.grid(row=3, columnspan=2, padx=(150, 0), pady=2, sticky="nsew")

opcoes = ['Todos os produtos', 'Sal', 'Doces', 'Confeitaria', 'Refeições', 'Canapés']
opcaoSelecionada = StringVar()
opcaoSelecionada.set('Todos os produtos')
combo = ttk.Combobox(secondFrame, values=opcoes, textvariable=opcaoSelecionada)
combo.grid(row=4, padx=(160, 100), columnspan=2, sticky='nsew')
#combo.bind("<<ComboboxSelected>>", selecionarOpcao)

btn_obter_data = Button(secondFrame, text="Mostrar lista", bg='#C0C0C0', font=("Arial", 16), command=inserirNaLista)
btn_obter_data.grid(row=5, column=0, columnspan=2, padx=(80, 0), pady=2, sticky='nsew')

tabela_acabados = Label(secondFrame, text="Composição de produtos acabados", font=("Arial", 14))
tabela_acabados.grid(row=6, columnspan=2, padx=(150, 0), pady=10, sticky="nsew")

#row 7 --> Tabela composição acabados

# btn_mostrar_eventos = Button(secondFrame, text="Ver todos os eventos", bg='#C0C0C0', font=("Arial", 16), command= lambda:verTodosEventos(ajustes_periodo, tabelas.table))
# btn_mostrar_eventos.grid(row=8, column=0)

# btn_abrir_janela = Button(secondFrame, text="Ver qtd. ano anterior", bg='#C0C0C0', font=("Arial", 16), command=verQtdAnoPassado)
# btn_abrir_janela.grid(row=8, column=1)

tabela_semiacabados = Label(secondFrame, text="Composição de produtos semi-acabados", font=("Arial", 14))
tabela_semiacabados.grid(row=9, columnspan=2, padx=(150, 0), pady=10, sticky="nsew")

#row 10 --> Tabela composição semi-acabados

txtfiltros = Label(secondFrame, text="Selecione os produtos que você deseja filtrar da lista.", font=("Arial", 14))
txtfiltros.grid(row=11, columnspan=2, padx=(150,0), pady=2, sticky="nsew")

c_todos = Checkbutton(secondFrame, text='Todos',variable=trazerTodos, onvalue=1, offvalue=0, font=("Arial", 14), height=2, width=5)
c_todos.grid(row=12, column=0, padx=(0,95), pady=0, sticky='e')

c_sal = Checkbutton(secondFrame, text='Ref',variable=filtrarRefeicoes, onvalue=1, offvalue=0, font=("Arial", 14), height=2, width=5)
c_sal.grid(row=12, column=0, padx=10, pady=0, sticky='e')

c_doces = Checkbutton(secondFrame, text='Doces',variable=filtrarDoces, onvalue=1, offvalue=0, font=("Arial", 14), height=2, width=5)
c_doces.grid(row=12, column=1, padx=(0,0), pady=0, sticky='w')

c_refeicoes = Checkbutton(secondFrame, text='Sal',variable=filtrarSal, onvalue=1, offvalue=0, font=("Arial", 14), height=2, width=5)
c_refeicoes.grid(row=12, column=1, padx=(85,0), pady=0, sticky='w')

c_canapes = Checkbutton(secondFrame, text='Canapés',variable=filtrarCanapes, onvalue=1, offvalue=0, font=("Arial", 14), height=2, width=6)
c_canapes.grid(row=13, column=0, sticky='e')

c_confeitaria = Checkbutton(secondFrame, text='Confeitaria',variable=filtrarConfeitaria, onvalue=1, offvalue=0, font=("Arial", 14), height=2, width=8)
c_confeitaria.grid(row=13, column=1, padx=10, sticky='w')

txt_tipo_planilha = Label(secondFrame, text="Qual lista de pedido de suprimento você quer gerar?", font=("Arial", 14))
txt_tipo_planilha.grid(row=14, columnspan=2, padx=(150,0), pady=2, sticky="nsew")

radiobutton_variable = IntVar(value=1)
radio_acabados = Radiobutton(secondFrame, text="Composição acabados", font=("Arial", 14), variable = radiobutton_variable, value = 1)
radio_acabados.grid(row = 15, columnspan=2, padx=(150,0), pady=2, sticky="nsew")
radio_semiacabados = Radiobutton(secondFrame, text="Composição semi-acabados", font=("Arial", 14), variable = radiobutton_variable, value = 2)
radio_semiacabados.grid(row = 16, columnspan=2, padx=(150,0), pady=2, sticky="nsew")

btn_obter_data = Button(secondFrame, text="Gerar Planilhas Excel", bg='#C0C0C0', font=("Arial", 16), command=gerarPlanilha)
btn_obter_data.grid(row=17, column=0, columnspan=2, padx=(80, 0), pady=(10, 30), sticky='nsew')


####################################################
#PÁGINA 2
####################################################

page2 = Frame(notebook)
notebook.add(page2,text='| Controle estoque acabados |')

saldo_var = ''
label_pesquisa_sa = Label(page2, text="Pesquise o produto acabado:", font=('Arial', 12, 'bold'))
label_pesquisa_sa.grid(row=1, column=0, columnspan=2, padx=(80, 0), pady=(10, 0), sticky='nsew')

input_saldo = Entry(page2, textvariable=saldo_var, bd=4)
input_saldo.grid(row=2, column=0, columnspan=2, padx=(80, 0), pady=(10, 30), sticky='nsew')
input_saldo.bind("<KeyRelease>", lambda event: filtrarListas(event, 'acabados'))

#Row 4 - Tabela controle estoque

btn_somar_estoque = Button(page2, text="Adicionar estoque", bg='#C0C0C0', font=("Arial", 16), command=lambda: janelaAttEstoque(tabelas.tbl_controle, 'acabados', 'soma'))
btn_somar_estoque.grid(row=6, column=0, columnspan=2, padx=(80, 0), pady=(10, 30), sticky='nsew')

btn_atualisar = Button(page2, text="Atualizar saldo", bg='#C0C0C0', font=("Arial", 16), command=inserirTabelaControle)
btn_atualisar.grid(row=7, column=0, columnspan=2, padx=(80, 0), pady=(10, 30), sticky='nsew')

btn_acerto_estoque = Button(page2, text="Aplicar acerto de estoque", bg='#C0C0C0', font=("Arial", 16), command=lambda: janelaAttEstoque(tabelas.tbl_controle, 'acabados', 'subtracao'))
btn_acerto_estoque.grid(row=8, column=0, columnspan=2, padx=(80, 0), pady=(10, 30), sticky='nsew')

####################################################
#PÁGINA 3
####################################################

page3 = Frame(notebook)
notebook.add(page3,text='| Controle estoque semi-acabados |')

saldo_var_sa = ''
label_pesquisa_sa = Label(page3, text="Pesquise o produto Semi-acabado:", font=('Arial', 12, 'bold'))
label_pesquisa_sa.grid(row=1, column=0, columnspan=2, padx=(80, 0), pady=(10, 0), sticky='nsew')

input_saldo_sa = Entry(page3, textvariable=saldo_var_sa, bd=4)
input_saldo_sa.grid(row=2, column=0, columnspan=2, padx=(80, 0), pady=(10, 30), sticky='nsew')
input_saldo_sa.bind("<KeyRelease>", lambda event: filtrarListas(event, 'semiacabados'))

#Row 4 - Tabela controle semi-acabados

btn_somar_estoque = Button(page3, text="Adicionar estoque", bg='#C0C0C0', font=("Arial", 16), command=lambda: janelaAttEstoque(tabelas.tbl_ctrl_semi, 'semi_acabados', 'soma'))
btn_somar_estoque.grid(row=6, column=0, columnspan=2, padx=(80, 0), pady=(10, 30), sticky='nsew')

btn_atualisar = Button(page3, text="Atualizar saldo", bg='#C0C0C0', font=("Arial", 16), command=inserirTabelaControle)
btn_atualisar.grid(row=7, column=0, columnspan=2, padx=(80, 0), pady=(10, 30), sticky='nsew')

btn_acerto_estoque = Button(page3, text="Aplicar acerto de estoque", bg='#C0C0C0', font=("Arial", 16), command=lambda: janelaAttEstoque(tabelas.tbl_ctrl_semi, 'semi_acabados', 'subtracao'))
btn_acerto_estoque.grid(row=8, column=0, columnspan=2, padx=(80, 0), pady=(10, 30), sticky='nsew')

####################################################
# PÁGINA 4
####################################################
page4 = Frame(notebook)
notebook.add(page4, text='| Motivos de estoque |')

lbl_dtInicioMotivos = Label(page4, text="De:", font=("Arial", 14))
lbl_dtInicioMotivos.grid(row=1, padx=(0, 190), column=0, sticky="e")

dtInicioMotivos = DateEntry(page4, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/MM/yyyy')
dtInicioMotivos.grid(row=2, column=0, padx=(150, 0), pady=5, sticky="e")

lbl_dtFimMotivos = Label(page4, text="Até:", font=("Arial", 14))
lbl_dtFimMotivos.grid(row=1, column=1, padx=(50, 0), pady=5, sticky="w")

dtFimMotivos = DateEntry(page4, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/MM/yyyy')
dtFimMotivos.grid(row=2, column=1, padx=(50, 0), pady=5, sticky="w")

btn_obter_data = Button(page4, text="Filtrar lista", bg='#C0C0C0', font=("Arial", 16), command=inserirTabelaMotivos)
btn_obter_data.grid(row=4, column=0, columnspan=2, padx=(80, 0), pady=2, sticky='nsew')




input_motivo = Entry(page4, textvariable=saldo_var, bd=4)
input_motivo.grid(row=10, column=0, columnspan=2, padx=(80, 0), pady=(10, 30), sticky='nsew')
input_motivo.bind("<KeyRelease>", lambda event: filtrarListas(event, 'motivosAcabados'))

input_motivoSA = Entry(page4, textvariable=saldo_var, bd=4)
input_motivoSA.grid(row=15, column=0, columnspan=2, padx=(80, 0), pady=(10, 30), sticky='nsew')
input_motivoSA.bind("<KeyRelease>", lambda event: filtrarListas(event, 'motivosSemiAcabados'))

# input_motivo = Entry(page4, textvariable=saldo_var, bd=4)
# input_motivo.grid(row=10, column=0, columnspan=2, padx=(80, 0), pady=(10, 30), sticky='nsew')
# input_motivo.bind("<KeyRelease>", lambda event: filtrarListas(event, 'motivosAcabados'))

# input_motivoSA = Entry(page4, textvariable=saldo_var, bd=4)
# input_motivoSA.grid(row=15, column=0, columnspan=2, padx=(80, 0), pady=(10, 30), sticky='nsew')
# input_motivoSA.bind("<KeyRelease>", lambda event: filtrarListas(event, 'motivosSemiAcabados'))


tabelas.criarTabela(secondFrame)  # Cria uma tabela no secondFrame
tabelas.tabelaControleEstoque(page2)  # Adiciona tabela de controle de estoque na página 2 
tabelas.tabelaCtrlSemiacabados(page3)  # Adiciona tabela de controle de semiacabados na página 3
tabelas.tabelaMotivo(page4)  # Adiciona tabela de motivo na página 4
tabelas.tabelaMotivoSA(page4)  # Adiciona tabela de motivo SA na página 4
inserirTabelaControle() 
#inserirTabelaMotivos()
root.mainloop()  





