#tkinter
from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import messagebox
########################################
root = Tk()
root.title("Gerar pedidos de suprimento")

root.geometry("1150x800")


# Cria os widgets
explicacao = Label(root, text="Selecione abaixo o período de tempo para o qual você quer gerar a lista de\n clientes mais recentes.", font=("Arial", 14))
explicacao.grid(row=0, columnspan=2, padx=(150, 0), pady=10, sticky="nsew")

lbl_dtInicio = Label(root, text="De:", font=("Arial", 14))
lbl_dtInicio.grid(row=1, padx=(0, 190), column=0, sticky="e")

dtInicio = DateEntry(root, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
dtInicio.grid(row=2, column=0, padx=(150, 0), pady=5, sticky="e")

lbl_dtFim = Label(root, text="Até:", font=("Arial", 14))
lbl_dtFim.grid(row=1, column=1, padx=(50, 0), pady=5, sticky="w")

dtFim = DateEntry(root, font=('Arial', 12), width=22, height=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
dtFim.grid(row=2, column=1, padx=(50, 0), pady=5, sticky="w")
btn_obter_data = Button(root, text="Mostrar lista", bg='#C0C0C0', font=("Arial", 16), command="#default")
btn_obter_data.grid(row=3, column=0, columnspan=2, padx=(80, 0), pady=2, sticky='nsew')
# Inicia o loop principal da janela
root.mainloop()