from tkinter import *
from tkinter import ttk

root = Tk()
root.title("Tornar encomenda baixada")

root.geometry("800x500")

lista = Listbox(root, height=15, width=30, font=("Arial", 16))
lista.grid(row=0, column=0, columnspan=1, padx=(150, 0), pady=10, sticky="nsew")

for i in range(1, 11):
    lista.insert(END, f"Item {i}")

def baixar_selecionado():
    # Obter o item selecionado
    selecionado = lista.get(ACTIVE)
    print("Baixar selecionado:", selecionado)

    # Salvar o item selecionado em um arquivo .txt
    with open('Ecs-baixadas-seleção.txt', 'a') as f:
        f.write(selecionado + '\n')

def baixar_tudo():
    # Obter todos os itens
    todos_itens = lista.get(0, END)
    print("Ecs-baixadas-período:", todos_itens)

    # Salvar todos os itens em um arquivo .txt
    with open('Ecs-baixadas-período.txt', 'a') as f:
        for item in todos_itens:
            f.write(item + '\n')

btn_obter_data = Button(root, text="Baixar", bg='#C0C0C0', font=("Arial", 16), command=baixar_selecionado)
btn_obter_data.grid(row=1, column=0, padx=(80, 0), pady=5, sticky='nsew')

btn_obter_data = Button(root, text="Baixar tudo", bg='#C0C0C0', font=("Arial", 16), command=baixar_tudo)
btn_obter_data.grid(row=2, column=0, padx=(80, 0), pady=5, sticky='nsew')

root.mainloop()