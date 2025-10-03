from tkinter import *
import tkcalendar
import os
from tkinter import messagebox

c = os.path.dirname(__file__)
nomeArquivo = c + "\\calendario.txt"

root = Tk()
root.title("Calendario")


def adicionarCompromisso(event):
    def gravarDados():
        with open(nomeArquivo, "a") as arquivoCalendario:
            arquivoCalendario.bind(f"{data.get()}\n")
            arquivoCalendario.write(f"Tipo de compromisso: {compromisso.get()}\n")
            arquivoCalendario.write(f"Descriçao do compromisso: {descricao.get(1.0, END)}\n")
            arquivoCalendario.write("\n")
            messagebox.showinfo("Sucesso", "Compromisso adicionado com sucesso!")
    
    app = Tk()
    app.title("Adicionar Compromisso")
    app.geometry("400x400")
    app.configure(background="#dde")

    Label (app, text='<<CalendarSelected>>', background="#dde", foreground="#009", anchor=W).place(x=30, y=200)
    data = Entry(app)
    data.place(x=30, y=30, width=1, height=100)

    Label(app, text="Tipo de compromisso:", background="#dde", foreground="#009", anchor=W).place(x=30, y=10)
    compromisso = Entry(app)
    compromisso.place(x=10, y=30, width=200, height=100)


    Label(app, text="Descrição do compromisso", background="#dde", foreground="#009", anchor=W).place(x=10, y=160)
    descricao = Text(app)
    descricao.place(x=10, y=180, width=400, height=120)

    # Centralizando o botão
    Button(app, text="Gravar", command=gravarDados).place(x=175, y=330, width=100, height=20)

    app.mainloop()
    print(calendario.get_date())


calendario = tkcalendar.Calendar(root, locale="pt_br")
calendario.pack()

calendario.bind('<<CalendarSelected>>',adicionarCompromisso)


root.mainloop()