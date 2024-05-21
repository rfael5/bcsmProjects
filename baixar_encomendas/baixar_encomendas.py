from datetime import datetime, timezone
from tkinter import messagebox
import connection
import tabelas

from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry

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

def setarData():
    dataInicio = dtInicio.get()
    dtInicioFormatada = formatarData(dataInicio)
    dataFim = dtFim.get()
    dtFimFormatada = formatarData(dataFim)
    
    lista_encomendas = connection.getEncomendasAutorizadas(dtInicioFormatada, dtFimFormatada)
    
    return lista_encomendas

def inserirNaLista():
    global lista_encomendas
    lista_encomendas = setarData()
    tabelas.table.delete(*tabelas.table.get_children())
    for encomenda in lista_encomendas:
        id = encomenda['idEvento']
        evento = encomenda['nomeEvento']
        doc = encomenda['DOCUMENTO']
        data_cadastro = formatarDataPedido(encomenda['dataCadastro'])
        if encomenda['SITUACAO'] == 'Z':
            situacao = 'Autorizado'
        elif encomenda['SITUACAO'] == 'B':
            situacao = 'Baixado'
        data = (id, evento, doc, data_cadastro, situacao)
        tabelas.table.insert(parent='', index=0, values=data)

def armazenarInfoEvento(event):
    indice = tabelas.table.selection()
    if indice:
        info_encomenda = tabelas.table.item(indice)['values'][2]
        abrirOutraJanela(info_encomenda)
        

def abrirOutraJanela(encomenda):
    global nova_janela
    nova_janela = Toplevel(root)
    nova_janela.title("Nova Janela")
    nova_janela.geometry("500x300")

    label = Label(nova_janela, text=f'Deseja baixar a encomenda {encomenda}?', font=("Arial", 14))
    label.grid(row=0, column=0, columnspan=2, padx=(80, 0), pady=2, sticky='nsew')
    
    btn_baixar = Button(nova_janela, text=f'Baixar encomenda', bg='#C0C0C0', font=("Arial", 16), command=lambda:baixarEncomenda(nova_janela, encomenda))
    btn_baixar.grid(row=1, column=0, columnspan=2, padx=(80, 0), pady=2, sticky='nsew')


def baixarEncomenda(janela, num_documento):
    connection.updateEncomenda(num_documento)
    inserirNaLista()
    janela.destroy()
    messagebox.showinfo('', f'Encomenda {num_documento} baixada.')

def buscarEncomenda():
    doc = txt_filtro.get()
    lista_filtrada = list(filter(lambda evento:int(evento['DOCUMENTO']) == int(doc), lista_encomendas))
    tabelas.table.delete(*tabelas.table.get_children())

    for encomenda in lista_filtrada:
        id = encomenda['idEvento']
        evento = encomenda['nomeEvento']
        doc = encomenda['DOCUMENTO']
        data_cadastro = formatarDataPedido(encomenda['dataCadastro'])
        if encomenda['SITUACAO'] == 'Z':
            situacao = 'Autorizado'
        elif encomenda['SITUACAO'] == 'B':
            situacao = 'Baixado'
        data = (id, evento, doc, data_cadastro, situacao)
        tabelas.table.insert(parent='', index=0, values=data)

def buscarEncomendaEspecifica():
    doc = txt_filtro.get()
    encomenda = connection.getEncomendaEspecifica(doc)
    if len(encomenda) == 0:
        messagebox.showinfo('Não encontrado', f'Não foi encontrada nenhuma encomenda autorizada\n com o número {doc}.')
    else:
        abrirJanelaConfirmacao(encomenda[0])

def abrirJanelaConfirmacao(encomenda):
    global janela_conf
    janela_conf = Toplevel(root)
    janela_conf.title("Confirmar baixa")
    janela_conf.geometry("500x300")
    
    label = Label(janela_conf, text=f'Deseja baixar a encomenda abaixo?', font=("Arial", 14))
    label.grid(row=0, column=0, columnspan=2, padx=20, pady=2, sticky='nsew')
    
    lb = Listbox(janela_conf, height=8)
    lb.grid(row=1, column=0, columnspan=2, padx=20, sticky='nsew')
    lb.insert(1, f"Nome: {encomenda['nomeEvento']}")
    lb.insert(2, f"Documento: {encomenda['DOCUMENTO']}")
    lb.insert(3, f"Data registro: {formatarDataPedido(encomenda['dataCadastro'])}")
    
    btn_b = Button(janela_conf, text=f'Baixar encomenda', bg='#C0C0C0', font=("Arial", 16), command=lambda:baixarEncomenda(janela_conf, encomenda['DOCUMENTO']))
    btn_b.grid(row=2, column=0, columnspan=2, padx=20, pady=2, sticky='nsew')


def baixarTodasEncomendas():
    for row in tabelas.table.get_children():
        n_doc = tabelas.table.item(row)["values"][2]
        print(n_doc)
        connection.updateEncomenda(n_doc)
    
    inserirNaLista()

#Tkinter
root = Tk()
root.title("Baixar encomendas")

root.geometry("1150x800")

notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True)

page1 = Frame(notebook)
notebook.add(page1, text='Página 1')

mainFrame = Frame(page1)
mainFrame.pack(fill=BOTH, expand=1)

canvas = Canvas(mainFrame)
canvas.pack(side=LEFT, fill=BOTH, expand=1)

scrollbar = ttk.Scrollbar(mainFrame, orient=VERTICAL, command=canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)

canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e:canvas.configure(scrollregion=canvas.bbox("all")))

secondFrame = Frame(canvas)
canvas.create_window((0, 0), window=secondFrame, anchor="nw")

explicacao = Label(secondFrame, text="Selecione abaixo o período de tempo para o qual você quer buscar a lista de\n encomendas.", font=("Arial", 14))
explicacao.grid(row=0, columnspan=2, padx=(150, 0), pady=10, sticky="nsew")

lbl_dtInicio = Label(secondFrame, text="De:", font=("Arial", 14))
lbl_dtInicio.grid(row=1, padx=(0, 190), column=0, sticky="e")

dtInicio = DateEntry(secondFrame, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
dtInicio.grid(row=2, column=0, padx=(150, 0), pady=5, sticky="e")

lbl_dtFim = Label(secondFrame, text="Até:", font=("Arial", 14))
lbl_dtFim.grid(row=1, column=1, padx=(50, 0), pady=5, sticky="w")

dtFim = DateEntry(secondFrame, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
dtFim.grid(row=2, column=1, padx=(50, 0), pady=5, sticky="w")

btn_obter_data = Button(secondFrame, text="Mostrar encomendas", bg='#C0C0C0', font=("Arial", 16), command=inserirNaLista)
btn_obter_data.grid(row=3, column=0, columnspan=2, padx=(80, 0), pady=2, sticky='nsew')

txt_filtro = Entry(secondFrame, borderwidth=2, relief="groove")
txt_filtro.grid(row=4, column=0, pady=10, sticky="e")

btn_filtrar = Button(secondFrame, text="Baixar encomenda", bg='#C0C0C0', height=0, font=("Arial", 16), command=buscarEncomendaEspecifica)
btn_filtrar.grid(row=4, column=1, pady=10, sticky="w")

exp_baixar_encomenda = Label(secondFrame, text="Para baixar uma das encomendas abaixo, clique duas vezes\n sobre ele.", font=("Arial", 14))
exp_baixar_encomenda.grid(row=5, columnspan=2, padx=(150, 0), pady=10, sticky="nsew")

#row 6 - Tabela

btn_baixar_todos = Button(secondFrame, text="Baixar todos", bg='#C0C0C0', height=0, font=("Arial", 16), command=baixarTodasEncomendas)
btn_baixar_todos.grid(row=7, column=0, columnspan=2, padx=(80, 0), pady=2, sticky='nsew')

tabelas.criarTabela(secondFrame)
tabelas.table.bind("<Double-Button-1>", lambda event: armazenarInfoEvento(event))

root.mainloop()
