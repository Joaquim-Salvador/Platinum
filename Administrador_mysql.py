from tkinter import *
import os
import tkcalendar
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import Tk, Toplevel, Label, Button, Entry, Frame, Text, CENTER, END, W
from PIL import Image, ImageTk
from datetime import datetime
import difflib
import re
import unicodedata
import builtins
import mysql.connector
from tkcalendar import Calendar
from vendas import carrinhoDeCompras


def carregar_imagem(caminho, largura, altura):
    imagem = Image.open(caminho)
    imagem = imagem.resize((largura, altura), Image.ANTIALIAS)
    return ImageTk.PhotoImage(imagem)

# Função para obter conexão com o banco de dados
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",      
        password="",    
        database="PLATINUM2"
    )

# Função para adicionar um carro (insere na tabela 'carro')
def adicionarCarro():
    def gravarDados():
        # Obtem os dados digitados na interface
        nome_cliente = vnome.get().strip()
        marca_modelo = vmodelo.get().strip()
        placa = vplaca.get().strip()
        if not nome_cliente or not marca_modelo or not placa:
            messagebox.showwarning("Erro", "Todos os campos são obrigatórios!")
            return

        # Conecta ao banco e verifica se já existe um carro com a mesma placa
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT placa FROM carro WHERE placa = %s", (placa,))
        if cursor.fetchone():
            messagebox.showwarning("Erro", "Carro com esta placa já existe!")
            cursor.close()
            conn.close()
            return

        # Insere os dados na tabela 'carro'
        cursor.execute(
            "INSERT INTO carro (placa, nome_cliente, marca_modelo) VALUES (%s, %s, %s)",
            (placa, nome_cliente, marca_modelo)
        )
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Sucesso", "Carro adicionado com sucesso!")
        app.destroy()

    app = Toplevel()
    app.title("Adicionar Carro")
    app.geometry("400x400")
    app.configure(background="#dde")

    largura_janela = 400
    largura_widget = 300
    altura_widget = 20

    Label(app, text="Nome do dono(a):", background="#dde", foreground="#009", anchor="w")\
        .place(x=(largura_janela - largura_widget) // 2, y=10)
    vnome = Entry(app)
    vnome.place(x=(largura_janela - largura_widget) // 2, y=30, width=largura_widget, height=altura_widget)

    Label(app, text="Modelo:", background="#dde", foreground="#009", anchor="w")\
        .place(x=(largura_janela - largura_widget) // 2, y=60)
    vmodelo = Entry(app)
    vmodelo.place(x=(largura_janela - largura_widget) // 2, y=80, width=largura_widget, height=altura_widget)

    Label(app, text="Placa:", background="#dde", foreground="#009", anchor="w")\
        .place(x=(largura_janela - largura_widget) // 2, y=110)
    vplaca = Entry(app)
    vplaca.place(x=(largura_janela - largura_widget) // 2, y=130, width=largura_widget, height=altura_widget)

    Button(app, text="Gravar", command=gravarDados)\
        .place(x=(largura_janela - 100) // 2, y=330, width=100, height=20)

# Função para verificar se um carro existe (pela placa)
def carro_existe(placa):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT placa FROM carro WHERE placa = %s", (placa,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

# Função para consultar carros e exibir serviços associados
def consultaCarros():
    # Função para normalizar textos (usada na busca)
    def normalize(text):
        return unicodedata.normalize('NFKD', text)\
                            .encode('ASCII', 'ignore')\
                            .decode('utf-8')\
                            .lower()\
                            .strip()

    # Consulta todos os carros cadastrados
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT placa, nome_cliente, marca_modelo FROM carro")
    carros = cursor.fetchall()
    cursor.close()
    conn.close()

    def carregar_detalhes(car):
        nome_dono_var.set(car.get("nome_cliente", ""))
        placa_var.set(car.get("placa", ""))
        modelo_var.set(car.get("marca_modelo", ""))
        # Limpa a Treeview e a área de descrição
        for row in tree.get_children():
            tree.delete(row)
        descricao_texto.delete(1.0, END)
        # Consulta os serviços associados a este carro
        conn2 = get_db_connection()
        cursor2 = conn2.cursor(dictionary=True)
        cursor2.execute("SELECT id_serviço, forma_pagamento, valor_total, descricao FROM serviços WHERE placa = %s", (car.get("placa"),))
        services = cursor2.fetchall()
        cursor2.close()
        conn2.close()
        if services:
            for i, s in enumerate(services):
                tree.insert("", "end", values=(s.get("id_serviço", ""), s.get("forma_pagamento", ""), s.get("valor_total", "")))
                descricao_texto.insert(END, f"{i+1}. {s.get('descricao', '')}\n\n")
        else:
            descricao_texto.insert(END, "Nenhum serviço encontrado para este carro.")

    def update_options(event):
        search_text = vconsulta.get().strip().lower()
        listbox_options.delete(0, tk.END)
        for car in carros:
            if search_text in normalize(car.get("nome_cliente", "")) \
               or search_text in normalize(car.get("placa", "")) \
               or search_text in normalize(car.get("marca_modelo", "")):
                display_text = f"{car.get('nome_cliente', '')} - {car.get('placa', '')} - {car.get('marca_modelo', '')}"
                listbox_options.insert(tk.END, display_text)

    def on_option_select(event):
        selection = listbox_options.curselection()
        if selection:
            index = selection[0]
            sel_text = listbox_options.get(index)
            for car in carros:
                display_text = f"{car.get('nome_cliente', '')} - {car.get('placa', '')} - {car.get('marca_modelo', '')}"
                if display_text == sel_text:
                    carregar_detalhes(car)
                    break

    app = Toplevel()
    app.title("Consulta de Carros")
    app.geometry("800x450")
    app.configure(background="#f2f2f2")

    Label(app, text="Digite o nome do dono, placa ou modelo do carro:")\
        .place(x=10, y=10)
    vconsulta = Entry(app, font=("Arial", 10))
    vconsulta.place(x=10, y=40, width=380, height=30)
    vconsulta.bind("<KeyRelease>", update_options)

    listbox_options = Listbox(app, font=("Arial", 10))
    listbox_options.place(x=10, y=80, width=480, height=60)
    listbox_options.bind("<Double-Button-1>", on_option_select)

    Button(app, text="Buscar", command=lambda: update_options(None))\
        .place(x=400, y=40, width=80, height=30)

    # Campos para exibir as informações do carro selecionado
    nome_dono_var = tk.StringVar()
    placa_var = tk.StringVar()
    modelo_var = tk.StringVar()

    Label(app, text="Nome do dono(a):").place(x=500, y=10)
    Entry(app, textvariable=nome_dono_var, font=("Arial", 10), state='readonly')\
        .place(x=600, y=10, width=180, height=25)
    Label(app, text="Placa:").place(x=500, y=40)
    Entry(app, textvariable=placa_var, font=("Arial", 10), state='readonly')\
        .place(x=600, y=40, width=180, height=25)
    Label(app, text="Modelo:").place(x=500, y=70)
    Entry(app, textvariable=modelo_var, font=("Arial", 10), state='readonly')\
        .place(x=600, y=70, width=180, height=25)

    # Área para exibir os serviços associados (Treeview e Text)
    columns = ("data_e_hora", "forma_de_pagamento", "valor")
    tree = ttk.Treeview(app, columns=columns, show="headings")
    tree.heading("data_e_hora", text="Id serviço")
    tree.heading("forma_de_pagamento", text="Forma de Pagamento")
    tree.heading("valor", text="Valor")
    tree.column("data_e_hora", width=150, anchor="center")
    tree.column("forma_de_pagamento", width=150, anchor="center")
    tree.column("valor", width=100, anchor="center")
    tree.place(x=10, y=150, width=480, height=250)

    vsb = ttk.Scrollbar(app, orient="vertical", command=tree.yview)
    vsb.place(x=490, y=150, height=250)
    tree.configure(yscrollcommand=vsb.set)

    descricao_texto = tk.Text(app, font=("Arial", 10))
    descricao_texto.place(x=510, y=150, width=280, height=250)

    update_options(None)

# Função para excluir um carro (remove da tabela 'carro')
def excluirCarro():
    # Consulta os carros cadastrados
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT placa, nome_cliente, marca_modelo FROM carro")
    carros = cursor.fetchall()
    cursor.close()
    conn.close()

    app = Toplevel()
    app.title("Excluir Carro")
    app.geometry("500x400")
    app.configure(background="#f2f2f2")

    Label(app, text="Digite o nome do dono ou a placa do carro para excluir:",
          font=("Arial", 10), bg="#f2f2f2")\
          .place(x=10, y=10)
    vconsulta = Entry(app, font=("Arial", 10))
    vconsulta.place(x=10, y=40, width=380, height=30)

    listbox_sugestoes = Listbox(app, font=("Arial", 10))
    listbox_sugestoes.place(x=10, y=80, width=380, height=80)

    lbl_carro_info = Label(app, text="Informações do carro:", font=("Arial", 10),
                           bg="#f2f2f2", justify="left", anchor="w")
    lbl_carro_info.place(x=10, y=170, width=380, height=60)

    selected_car = {}

    def update_suggestions(event):
        search_text = vconsulta.get().strip().lower()
        listbox_sugestoes.delete(0, END)
        filtered = [car for car in carros if search_text in car.get("nome_cliente", "").lower() \
                    or search_text in car.get("placa", "").lower()]
        for car in filtered:
            listbox_sugestoes.insert(END, f"{car.get('nome_cliente', '')} - {car.get('placa', '')}")

    vconsulta.bind("<KeyRelease>", update_suggestions)

    def on_suggestion_select(event):
        selection = listbox_sugestoes.curselection()
        if selection:
            index = selection[0]
            sel_text = listbox_sugestoes.get(index)
            for car in carros:
                if f"{car.get('nome_cliente', '')} - {car.get('placa', '')}" == sel_text:
                    selected_car.clear()
                    selected_car.update(car)
                    info_text = (f"Nome: {car.get('nome_cliente', '')}\n"
                                 f"Modelo: {car.get('marca_modelo', '')}\n"
                                 f"Placa: {car.get('placa', '')}")
                    lbl_carro_info.config(text=info_text)
                    break

    listbox_sugestoes.bind("<Double-Button-1>", on_suggestion_select)

    def excluir_selected():
        if not selected_car:
            messagebox.showwarning("Erro", "Nenhum carro selecionado.")
            return
        confirm = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Você realmente deseja excluir o seguinte carro?\n\n"
            f"Nome: {selected_car.get('nome_cliente', '')}\n"
            f"Modelo: {selected_car.get('marca_modelo', '')}\n"
            f"Placa: {selected_car.get('placa', '')}\n"
        )
        if confirm:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM carro WHERE placa = %s", (selected_car.get("placa"),))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Sucesso", "Carro excluído com sucesso!")
            app.destroy()
        else:
            messagebox.showinfo("Cancelado", "Exclusão cancelada.")

    Button(app, text="Excluir", command=excluir_selected, font=("Arial", 10))\
        .place(x=400, y=40, width=80, height=30)
    Button(app, text="Pesquisar", command=lambda: update_suggestions(None), font=("Arial", 10))\
        .place(x=400, y=80, width=80, height=30)

    update_suggestions(None)

# Função principal que abre a aba do administrador com os botões de gerenciamento
def carros():
    abaAdiministrador = Toplevel()
    abaAdiministrador.title("Aba Administrador")
    abaAdiministrador.geometry("700x300")
    abaAdiministrador.config(bg="DimGray")


    img_adicionar = carregar_imagem("Adicionarcarro.png", 200, 200)
    img_excluir   = carregar_imagem("Excluircarro.png", 200, 200)
    img_consultar = carregar_imagem("Texto do seu parágrafo.png", 200, 200)

    frame = Frame(abaAdiministrador, bg="DimGray")
    frame.place(relx=0.5, rely=0.5, anchor="center")

    btn_adicionar = Button(frame,
                           text="Adicionar carro",
                           command=adicionarCarro,
                           fg="Black",
                           bg="SlateGray1",
                           font=("Helvetica", 10, "bold"),
                           width=200,
                           height=200,
                           image=img_adicionar)
    btn_adicionar.image = img_adicionar
    btn_adicionar.grid(row=0, column=0, padx=5, pady=5)


    btn_consultar = Button(frame,
                           text="Consultar carro",
                           command=consultaCarros,
                           fg="Black",
                           bg="SlateGray1",
                           font=("Helvetica", 10, "bold"),
                           width=200,
                           height=200,
                           image=img_consultar)
    btn_consultar.image = img_consultar
    btn_consultar.grid(row=0, column=2, padx=5, pady=5)


# =========================
# Função para Adicionar Cliente
# =========================
def adicionarcliente():
    app = Toplevel()
    app.title("Adicionar Cliente")
    app.geometry("400x500")
    app.configure(background="#dde")

    largura_janela = 400
    largura_widget = 300
    altura_widget = 20

    # Campos de entrada
    Label(app, text="Nome do cliente:", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura_janela - largura_widget) // 2, y=10)
    vnome = Entry(app)
    vnome.place(x=(largura_janela - largura_widget) // 2, y=30, width=largura_widget, height=altura_widget)

    Label(app, text="Telefone:", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura_janela - largura_widget) // 2, y=60)
    vtelefone = Entry(app)
    vtelefone.place(x=(largura_janela - largura_widget) // 2, y=80, width=largura_widget, height=altura_widget)

    Label(app, text="CPF:", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura_janela - largura_widget) // 2, y=110)
    vcpf = Entry(app)
    vcpf.place(x=(largura_janela - largura_widget) // 2, y=130, width=largura_widget, height=altura_widget)

    Label(app, text="Endereço:", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura_janela - largura_widget) // 2, y=160)
    vendereco = Entry(app)
    vendereco.place(x=(largura_janela - largura_widget) // 2, y=180, width=largura_widget, height=altura_widget)

    Label(app, text="E-mail:", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura_janela - largura_widget) // 2, y=210)
    vemail = Entry(app)
    vemail.place(x=(largura_janela - largura_widget) // 2, y=230, width=largura_widget, height=altura_widget)

    # No banco, usamos a coluna 'placa' para armazenar o carro do cliente
    Label(app, text="Carro do cliente (Placa):", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura_janela - largura_widget) // 2, y=260)
    vplaca = Entry(app)
    vplaca.place(x=(largura_janela - largura_widget) // 2, y=280, width=largura_widget, height=altura_widget)

    def gravarDados():
        nome = vnome.get().strip()
        telefone = vtelefone.get().strip()
        cpf = vcpf.get().strip()
        endereco = vendereco.get().strip()
        email = vemail.get().strip()
        placa = vplaca.get().strip()

        if not nome or not telefone or not cpf or not endereco or not email or not placa:
            messagebox.showwarning("Erro", "Todos os campos são obrigatórios!")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Inserir registro na tabela 'cliente'
            cursor.execute(
                "INSERT INTO cliente (nome_cliente, placa, cpf, telefone, endereço, email) VALUES (%s, %s, %s, %s, %s, %s)",
                (nome, placa, cpf, telefone, endereco, email)
            )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Sucesso", "Cliente adicionado com sucesso!")
            app.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao adicionar cliente: {err}")

    Button(app, text="Gravar", command=gravarDados)\
        .place(x=(largura_janela - 100) // 2, y=380, width=100, height=20)

    app.mainloop()

# =========================
# Função para Consultar Clientes (com opção de atualizar)
# =========================
def consultaclientes():
    app = Toplevel()
    app.title("Consulta de Clientes")
    app.geometry("500x600")
    app.configure(background="#f2f2f2")

    Label(app, text="Digite o nome do cliente ou CPF:").place(x=10, y=10)
    vconsulta = Entry(app, font=("Arial", 10))
    vconsulta.place(x=10, y=40, width=380, height=30)

    resultado_texto = tk.Text(app, font=("Arial", 10), height=15)
    resultado_texto.place(x=10, y=80, width=460, height=400)

    def consultar():
        query = vconsulta.get().strip()
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            if query:
                like_query = "%" + query.lower() + "%"
                cursor.execute("SELECT * FROM cliente WHERE LOWER(nome_cliente) LIKE %s OR LOWER(cpf) LIKE %s", (like_query, like_query))
            else:
                cursor.execute("SELECT * FROM cliente")
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            resultado_texto.delete(1.0, END)
            if results:
                for cli in results:
                    resultado_texto.insert(END, f"Nome do cliente: {cli.get('nome_cliente','')}\n")
                    resultado_texto.insert(END, f"Telefone: {cli.get('telefone','')}\n")
                    resultado_texto.insert(END, f"CPF: {cli.get('cpf','')}\n")
                    resultado_texto.insert(END, f"E-mail: {cli.get('email','')}\n")
                    resultado_texto.insert(END, f"Endereço: {cli.get('endereço','')}\n")
                    resultado_texto.insert(END, f"Carro do cliente (Placa): {cli.get('placa','')}\n")
                    resultado_texto.insert(END, "-" * 40 + "\n")
            else:
                resultado_texto.insert(END, "Nenhum cliente encontrado.\n")
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao consultar clientes: {err}")

    vconsulta.bind("<KeyRelease>", lambda event: consultar())
    Button(app, text="Buscar", command=consultar)\
        .place(x=400, y=40, width=80, height=30)

    # ========= Atualização =========
    def atualizar_cliente():
        update_win = Toplevel(app)
        update_win.title("Atualizar Cliente")
        update_win.geometry("400x600")
        update_win.configure(background="#dde")

        Label(update_win, text="Digite o CPF do cliente a atualizar:", background="#dde", foreground="#009")\
            .place(x=10, y=10)
        vconsulta_update = Entry(update_win, font=("Arial", 10))
        vconsulta_update.place(x=10, y=40, width=380, height=30)

        def buscar_cliente():
            cpf_query = vconsulta_update.get().strip()
            if not cpf_query:
                messagebox.showwarning("Erro", "Digite o CPF para buscar o cliente.")
                return
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM cliente WHERE cpf = %s", (cpf_query,))
                cli = cursor.fetchone()
                cursor.close()
                conn.close()
                if cli:
                    entry_nome.delete(0, END)
                    entry_nome.insert(0, cli.get("nome_cliente", ""))
                    entry_telefone.delete(0, END)
                    entry_telefone.insert(0, cli.get("telefone", ""))
                    entry_cpf.delete(0, END)
                    entry_cpf.insert(0, cli.get("cpf", ""))
                    entry_email.delete(0, END)
                    entry_email.insert(0, cli.get("email", ""))
                    entry_endereco.delete(0, END)
                    entry_endereco.insert(0, cli.get("endereço", ""))
                    entry_placa.delete(0, END)
                    entry_placa.insert(0, cli.get("placa", ""))
                else:
                    messagebox.showinfo("Info", "Cliente não encontrado.")
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao buscar cliente: {err}")

        Button(update_win, text="Buscar", command=buscar_cliente)\
            .place(x=300, y=40, width=80, height=30)

        Label(update_win, text="Nome do cliente:", background="#dde", foreground="#009")\
            .place(x=10, y=90)
        entry_nome = Entry(update_win, font=("Arial", 10))
        entry_nome.place(x=10, y=110, width=380, height=20)

        Label(update_win, text="Telefone:", background="#dde", foreground="#009")\
            .place(x=10, y=140)
        entry_telefone = Entry(update_win, font=("Arial", 10))
        entry_telefone.place(x=10, y=160, width=380, height=20)

        Label(update_win, text="CPF:", background="#dde", foreground="#009")\
            .place(x=10, y=190)
        entry_cpf = Entry(update_win, font=("Arial", 10))
        entry_cpf.place(x=10, y=210, width=380, height=20)

        Label(update_win, text="E-mail:", background="#dde", foreground="#009")\
            .place(x=10, y=240)
        entry_email = Entry(update_win, font=("Arial", 10))
        entry_email.place(x=10, y=260, width=380, height=20)

        Label(update_win, text="Endereço:", background="#dde", foreground="#009")\
            .place(x=10, y=290)
        entry_endereco = Entry(update_win, font=("Arial", 10))
        entry_endereco.place(x=10, y=310, width=380, height=20)

        Label(update_win, text="Carro do cliente (Placa):", background="#dde", foreground="#009")\
            .place(x=10, y=340)
        entry_placa = Entry(update_win, font=("Arial", 10))
        entry_placa.place(x=10, y=360, width=380, height=20)

        def salvar_atualizacao():
            novo_nome = entry_nome.get().strip()
            novo_telefone = entry_telefone.get().strip()
            novo_cpf = entry_cpf.get().strip()
            novo_email = entry_email.get().strip()
            novo_endereco = entry_endereco.get().strip()
            novo_placa = entry_placa.get().strip()

            if not novo_nome or not novo_telefone or not novo_cpf or not novo_email or not novo_endereco or not novo_placa:
                messagebox.showwarning("Erro", "Todos os campos são obrigatórios!")
                return
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE cliente SET nome_cliente=%s, telefone=%s, cpf=%s, email=%s, endereço=%s, placa=%s WHERE cpf=%s",
                    (novo_nome, novo_telefone, novo_cpf, novo_email, novo_endereco, novo_placa, vconsulta_update.get().strip())
                )
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")
                update_win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao atualizar cliente: {err}")

        Button(update_win, text="Salvar Informações", command=salvar_atualizacao)\
            .place(x=150, y=400, width=130, height=30)

        update_win.mainloop()

    Button(app, text="Atualizar Cliente", command=atualizar_cliente)\
        .place(x=10, y=500, width=460, height=30)

    app.mainloop()

# =========================
# Função para Excluir Cliente
# =========================
def excluircliente():
    app = Toplevel()
    app.title("Excluir Cliente")
    app.geometry("500x400")
    app.configure(background="#f2f2f2")

    Label(app, text="Digite o nome ou o CPF do cliente para excluir:", font=("Arial", 10), bg="#f2f2f2")\
        .place(x=10, y=10)
    vconsulta = Entry(app, font=("Arial", 10))
    vconsulta.place(x=10, y=40, width=380, height=30)

    listbox_sugestoes = Listbox(app, font=("Arial", 10))
    listbox_sugestoes.place(x=10, y=80, width=380, height=80)

    lbl_cliente_info = Label(app, text="Informações do cliente:", font=("Arial", 10), bg="#f2f2f2", justify="left", anchor="w")
    lbl_cliente_info.place(x=10, y=170, width=380, height=90)

    selected_cli = {}

    def update_suggestions(event):
        search_text = vconsulta.get().strip().lower()
        listbox_sugestoes.delete(0, END)
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            like_query = "%" + search_text + "%"
            cursor.execute("SELECT * FROM cliente WHERE LOWER(nome_cliente) LIKE %s OR LOWER(cpf) LIKE %s", (like_query, like_query))
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            for cli in results:
                listbox_sugestoes.insert(END, f"{cli.get('nome_cliente','')} - {cli.get('cpf','')}")
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao buscar clientes: {err}")

    vconsulta.bind("<KeyRelease>", update_suggestions)

    def on_suggestion_select(event):
        selection = listbox_sugestoes.curselection()
        if selection:
            index = selection[0]
            sel_text = listbox_sugestoes.get(index)
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cpf_selected = sel_text.split(" - ")[1]
                cursor.execute("SELECT * FROM cliente WHERE cpf = %s", (cpf_selected,))
                cli = cursor.fetchone()
                cursor.close()
                conn.close()
                if cli:
                    selected_cli.clear()
                    selected_cli.update(cli)
                    info_text = (f"Nome: {cli.get('nome_cliente','')}\n"
                                 f"CPF: {cli.get('cpf','')}\n"
                                 f"E-mail: {cli.get('email','')}\n"
                                 f"Endereço: {cli.get('endereço','')}\n"
                                 f"Carro do cliente (Placa): {cli.get('placa','')}")
                    lbl_cliente_info.config(text=info_text)
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao buscar cliente: {err}")

    listbox_sugestoes.bind("<Double-Button-1>", on_suggestion_select)

    def excluir_selected():
        if not selected_cli:
            messagebox.showwarning("Erro", "Nenhum cliente selecionado.")
            return
        confirm = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Você realmente deseja excluir o seguinte cliente?\n\n"
            f"Nome: {selected_cli.get('nome_cliente','')}\n"
            f"CPF: {selected_cli.get('cpf','')}\n"
            f"E-mail: {selected_cli.get('email','')}\n"
            f"Endereço: {selected_cli.get('endereço','')}\n"
            f"Carro do cliente (Placa): {selected_cli.get('placa','')}\n"
        )
        if confirm:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cliente WHERE cpf = %s", (selected_cli.get("cpf"),))
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")
                app.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao excluir cliente: {err}")
        else:
            messagebox.showinfo("Cancelado", "Exclusão cancelada.")

    Button(app, text="Excluir", command=excluir_selected, font=("Arial", 10))\
        .place(x=400, y=40, width=80, height=30)
    Button(app, text="Pesquisar", command=lambda: update_suggestions(None), font=("Arial", 10))\
        .place(x=400, y=80, width=80, height=30)

    app.mainloop()

# =========================
# Função Principal de Gerenciamento de Clientes
# =========================


def clientes():
    abaAdiministrador = Toplevel()
    abaAdiministrador.title("Aba Administrador - Clientes")
    abaAdiministrador.geometry("700x300")
    abaAdiministrador.config(bg="DimGray")

    img_adicionar = carregar_imagem("Adicionarcliente.png", 200, 200)
    img_excluir   = carregar_imagem("Excluircliente.png", 200, 200)
    img_consultar = carregar_imagem("Consultarcliente.png", 200, 200)

    frame = Frame(abaAdiministrador, bg="DimGray")
    frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    btn_adicionar = Button(frame,
                           text="Adicionar cliente",
                           command=adicionarcliente,
                           fg="Black",
                           bg="SlateGray1",
                           font=("Helvetica", 10, "bold"),
                           width=200,
                           height=200,
                           image=img_adicionar)
    btn_adicionar.image = img_adicionar
    btn_adicionar.grid(row=0, column=0, padx=5, pady=5)

    btn_consultar = Button(frame,
                           text="Consultar cliente",
                           command=consultaclientes,
                           fg="Black",
                           bg="SlateGray1",
                           font=("Helvetica", 10, "bold"),
                           width=200,
                           height=200,
                           image=img_consultar)
    btn_consultar.image = img_consultar
    btn_consultar.grid(row=0, column=2, padx=5, pady=5)

def carregar_estoque_db():
    """
    Consulta a tabela 'estoque' e retorna um dicionário indexado pelo nome da peça.
    Cada registro conterá: Quantidade, Valor Unitário, Valor Total e Nome do fornecedor.
    """
    estoque = {}
    try:
        conn = get_db_connection()
        if conn is None:
            return estoque
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM estoque")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        for row in rows:
            nome = row["nome_peca"]
            estoque[nome] = {
                "Quantidade": row["quantidade"],
                "Valor Unitário": row["valor_unit"],
                "Valor Total": row["valor_total"],
                "Nome do fornecedor": row["nome_fornecedor"]
            }
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao carregar estoque: {err}")
    return estoque

def salvar_estoque_db(estoque):
    """
    Atualiza o estoque na tabela 'estoque' conforme os valores do dicionário 'estoque'.
    Se algum produto tiver quantidade 0, ele é removido.
    """
    try:
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        for nome, prod in estoque.items():
            qtd = prod.get("Quantidade", 0)
            if qtd <= 0:
                cursor.execute("DELETE FROM estoque WHERE nome_peca = %s", (nome,))
            else:
                cursor.execute(
                    "UPDATE estoque SET quantidade=%s, valor_unit=%s, valor_total=%s, nome_fornecedor=%s WHERE nome_peca=%s",
                    (qtd, prod.get("Valor Unitário", 0.0), prod.get("Valor Total", 0.0), prod.get("Nome do fornecedor", ""), nome)
                )
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao salvar estoque: {err}")

def mostrar_estoque_aba():
    """
    Abre uma nova janela que exibe os itens do estoque (nome, quantidade disponível e fornecedor)
    e permite que o usuário informe uma quantidade para deletar.
    """
    aba = Toplevel()
    aba.title("Estoque")
    aba.geometry("600x400")

    # Treeview para exibir os itens
    tree = ttk.Treeview(aba, columns=("Nome", "Quantidade", "Fornecedor"), show="headings")
    tree.heading("Nome", text="Nome do Produto")
    tree.heading("Quantidade", text="Quantidade Disponível")
    tree.heading("Fornecedor", text="Fornecedor")
    tree.column("Nome", width=250)
    tree.column("Quantidade", width=150, anchor="center")
    tree.column("Fornecedor", width=150)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    def carregar_estoque():
        # Limpa a Treeview
        for item in tree.get_children():
            tree.delete(item)
        estoque = carregar_estoque_db()
        for nome, info in estoque.items():
            tree.insert("", "end", values=(nome, info["Quantidade"], info["Nome do fornecedor"]))

    carregar_estoque()

    # Frame para o campo de quantidade e botão
    frame_deletar = tk.Frame(aba)
    frame_deletar.pack(pady=10)

    Label(frame_deletar, text="Quantidade para deletar:").pack(side="left", padx=5)
    qtd_entry = Entry(frame_deletar, width=10)
    qtd_entry.pack(side="left", padx=5)

    def deletar_quantidade():
        # Verifica se algum item está selecionado
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um produto para deletar quantidade.")
            return

        # Valida a quantidade informada
        try:
            del_qtd = int(qtd_entry.get())
            if del_qtd <= 0:
                messagebox.showwarning("Atenção", "Informe um valor positivo para deletar.")
                return
        except ValueError:
            messagebox.showwarning("Atenção", "Informe um valor numérico para deletar.")
            return

        # Obtém o nome do produto selecionado
        item = tree.item(selected[0])
        nome_produto = item["values"][0]

        try:
            conn = get_db_connection()
            if conn is None:
                return
            cursor = conn.cursor()
            # Consulta a quantidade atual e o valor unitário do produto
            cursor.execute("SELECT quantidade, valor_unit FROM estoque WHERE nome_peca = %s", (nome_produto,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Erro", "Produto não encontrado no estoque.")
                return
            current_qtd, valor_unit = result
            new_qtd = current_qtd - del_qtd

            if new_qtd > 0:
                novo_valor_total = valor_unit * new_qtd
                cursor.execute(
                    "UPDATE estoque SET quantidade = %s, valor_total = %s WHERE nome_peca = %s",
                    (new_qtd, novo_valor_total, nome_produto)
                )
            else:
                # Se a quantidade chegar a zero ou negativa, remove o produto
                cursor.execute("DELETE FROM estoque WHERE nome_peca = %s", (nome_produto,))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Sucesso", f"Quantidade atualizada para o produto {nome_produto}.")
            carregar_estoque()  # Atualiza a Treeview
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao deletar quantidade: {err}")

    Button(frame_deletar, text="Deletar", command=deletar_quantidade).pack(side="left", padx=5)

    aba.mainloop()


# ---------------------------
# FUNÇÃO: Adicionar Fornecedor
# ---------------------------
def adicionar_fornecedor():
    app = tk.Toplevel()
    app.title("Adicionar Fornecedor")
    app.geometry("400x400")
    app.configure(background="#dde")

    largura_janela = 400
    largura_widget = 300
    altura_widget = 20

    # Campos de entrada
    tk.Label(app, text="Nome do fornecedor:", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura_janela - largura_widget)//2, y=10)
    vnome = Entry(app)
    vnome.place(x=(largura_janela - largura_widget)//2, y=30, width=largura_widget, height=altura_widget)

    tk.Label(app, text="Produto:", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura_janela - largura_widget)//2, y=60)
    vproduto = Entry(app)
    vproduto.place(x=(largura_janela - largura_widget)//2, y=80, width=largura_widget, height=altura_widget)

    tk.Label(app, text="Telefone:", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura_janela - largura_widget)//2, y=110)
    vtelefone = Entry(app)
    vtelefone.place(x=(largura_janela - largura_widget)//2, y=130, width=largura_widget, height=altura_widget)

    tk.Label(app, text="CNPJ:", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura_janela - largura_widget)//2, y=160)
    vcnpj = Entry(app)
    vcnpj.place(x=(largura_janela - largura_widget)//2, y=180, width=largura_widget, height=altura_widget)

    tk.Label(app, text="Endereço:", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura_janela - largura_widget)//2, y=210)
    # Área de texto para o endereço
    obs_frame = tk.Frame(app)
    obs_frame.place(x=(largura_janela - largura_widget)//2, y=230, width=largura_widget, height=80)
    vobs = Text(obs_frame, wrap="word")
    vobs.pack(side="left", fill="both", expand=True)
    obs_scroll = Scrollbar(obs_frame, command=vobs.yview)
    obs_scroll.pack(side="right", fill="y")
    vobs.config(yscrollcommand=obs_scroll.set)

    def gravarDados():
        nome = vnome.get().strip()
        produto = vproduto.get().strip()
        telefone = vtelefone.get().strip()
        cnpj = vcnpj.get().strip()
        endereco = vobs.get("1.0", END).strip()

        if not nome or not produto or not telefone or not cnpj or not endereco:
            messagebox.showwarning("Erro", "Todos os campos são obrigatórios!")
            return

        # Conversão de telefone e CNPJ para inteiro (se necessário)
        try:
            telefone_int = int(telefone)
            cnpj_int = int(cnpj)
        except ValueError:
            messagebox.showerror("Erro", "Telefone e CNPJ devem ser numéricos!")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Verifica se o fornecedor já existe
            cursor.execute("SELECT nome_fornecedor FROM fornecedor WHERE LOWER(nome_fornecedor) = %s", (nome.lower(),))
            if cursor.fetchone():
                messagebox.showwarning("Erro", "Fornecedor já cadastrado!")
                cursor.close()
                conn.close()
                return

            cursor.execute(
                "INSERT INTO fornecedor (nome_fornecedor, endereço, produto, CNPJ, telefone) VALUES (%s, %s, %s, %s, %s)",
                (nome, endereco, produto, cnpj_int, telefone_int)
            )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Sucesso", "Fornecedor adicionado com sucesso!")
            app.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao adicionar fornecedor: {err}")

    tk.Button(app, text="Gravar", command=gravarDados)\
        .place(x=(largura_janela-100)//2, y=340, width=100, height=20)

    app.mainloop()

# ---------------------------
# FUNÇÃO: Verificar se o fornecedor já existe
# ---------------------------
def fornecedor_existe(nome):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nome_fornecedor FROM fornecedor WHERE LOWER(nome_fornecedor)=%s", (nome.lower(),))
        existe = cursor.fetchone() is not None
        cursor.close()
        conn.close()
        return existe
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro na verificação do fornecedor: {err}")
        return False

# ---------------------------
# FUNÇÃO: Consultar/Atualizar Fornecedores
# ---------------------------
def consultaFornecedores():
    # Função de busca que utiliza o banco de dados
    def buscar():
        consulta = vconsulta.get().strip().lower()
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            if consulta:
                query = "SELECT * FROM fornecedor WHERE LOWER(nome_fornecedor) LIKE %s OR LOWER(produto) LIKE %s"
                like_term = "%" + consulta + "%"
                cursor.execute(query, (like_term, like_term))
            else:
                cursor.execute("SELECT * FROM fornecedor")
            resultados = cursor.fetchall()
            cursor.close()
            conn.close()
            resultado_texto.delete("1.0", END)
            if resultados:
                for f in resultados:
                    resultado_texto.insert(END, f"Nome do fornecedor: {f.get('nome_fornecedor','')}\n")
                    resultado_texto.insert(END, f"Produto: {f.get('produto','')}\n")
                    resultado_texto.insert(END, f"Telefone: {f.get('telefone','')}\n")
                    resultado_texto.insert(END, f"CNPJ: {f.get('CNPJ','')}\n")
                    resultado_texto.insert(END, f"Endereço: {f.get('endereço','')}\n")
                    resultado_texto.insert(END, "-"*40 + "\n")
            else:
                resultado_texto.insert(END, "Nenhum fornecedor encontrado.\n")
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao buscar fornecedores: {err}")

    # Função para atualizar fornecedor (janela de edição)
    def atualizar_fornecedor():
        update_win = Toplevel()
        update_win.title("Atualizar Fornecedor")
        update_win.geometry("400x600")
        update_win.configure(background="#dde")

        # Campo de pesquisa pelo fornecedor (usaremos o CNPJ como identificador único)
        Label(update_win, text="Digite o CNPJ do fornecedor a atualizar:", background="#dde", foreground="#009")\
            .place(x=10, y=10)
        vconsulta_update = Entry(update_win, font=("Arial", 10))
        vconsulta_update.place(x=10, y=40, width=380, height=30)

        def buscar_fornecedor():
            cnpj_query = vconsulta_update.get().strip()
            if not cnpj_query:
                messagebox.showwarning("Erro", "Digite o CNPJ para buscar o fornecedor.")
                return
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM fornecedor WHERE CNPJ = %s", (cnpj_query,))
                fornecedor = cursor.fetchone()
                cursor.close()
                conn.close()
                if fornecedor:
                    entry_nome.delete(0, END)
                    entry_nome.insert(0, fornecedor.get("nome_fornecedor", ""))
                    entry_produto.delete(0, END)
                    entry_produto.insert(0, fornecedor.get("produto", ""))
                    entry_telefone.delete(0, END)
                    entry_telefone.insert(0, fornecedor.get("telefone", ""))
                    entry_cnpj.delete(0, END)
                    entry_cnpj.insert(0, fornecedor.get("CNPJ", ""))
                    entry_endereco.delete(0, END)
                    entry_endereco.insert(0, fornecedor.get("endereço", ""))
                else:
                    messagebox.showinfo("Info", "Fornecedor não encontrado.")
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao buscar fornecedor: {err}")

        Button(update_win, text="Buscar", command=buscar_fornecedor)\
            .place(x=300, y=40, width=80, height=30)

        Label(update_win, text="Nome do fornecedor:", background="#dde", foreground="#009")\
            .place(x=10, y=90)
        entry_nome = Entry(update_win, font=("Arial", 10))
        entry_nome.place(x=10, y=110, width=380, height=20)

        Label(update_win, text="Produto:", background="#dde", foreground="#009")\
            .place(x=10, y=140)
        entry_produto = Entry(update_win, font=("Arial", 10))
        entry_produto.place(x=10, y=160, width=380, height=20)

        Label(update_win, text="Telefone:", background="#dde", foreground="#009")\
            .place(x=10, y=190)
        entry_telefone = Entry(update_win, font=("Arial", 10))
        entry_telefone.place(x=10, y=210, width=380, height=20)

        Label(update_win, text="CNPJ:", background="#dde", foreground="#009")\
            .place(x=10, y=240)
        entry_cnpj = Entry(update_win, font=("Arial", 10))
        entry_cnpj.place(x=10, y=260, width=380, height=20)

        Label(update_win, text="Endereço:", background="#dde", foreground="#009")\
            .place(x=10, y=290)
        entry_endereco = Entry(update_win, font=("Arial", 10))
        entry_endereco.place(x=10, y=310, width=380, height=20)

        def salvar_atualizacao():
            novo_nome = entry_nome.get().strip()
            novo_produto = entry_produto.get().strip()
            novo_telefone = entry_telefone.get().strip()
            novo_cnpj = entry_cnpj.get().strip()
            novo_endereco = entry_endereco.get().strip()
            if not (novo_nome and novo_produto and novo_telefone and novo_cnpj and novo_endereco):
                messagebox.showwarning("Erro", "Todos os campos são obrigatórios!")
                return
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE fornecedor SET nome_fornecedor=%s, produto=%s, telefone=%s, CNPJ=%s, endereço=%s WHERE CNPJ=%s",
                    (novo_nome, novo_produto, novo_telefone, novo_cnpj, novo_endereco, vconsulta_update.get().strip())
                )
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Sucesso", "Fornecedor atualizado com sucesso!")
                update_win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao atualizar fornecedor: {err}")

        Button(update_win, text="Salvar Informações", command=salvar_atualizacao)\
            .place(x=150, y=360, width=130, height=30)

        update_win.mainloop()

    # Janela principal de consulta de fornecedores
    app = Toplevel()
    app.title("Consulta de Fornecedores")
    app.geometry("500x600")
    app.configure(background="#f2f2f2")

    Label(app, text="Digite o produto ou o nome do fornecedor:").place(x=10, y=10)
    vconsulta = Entry(app, font=("Arial", 10))
    vconsulta.place(x=10, y=40, width=380, height=30)
    vconsulta.bind("<KeyRelease>", lambda event: buscar())

    Button(app, text="Buscar", command=buscar).place(x=400, y=40, width=80, height=30)
    Button(app, text="Atualizar Fornecedor", command=atualizar_fornecedor)\
        .place(x=10, y=530, width=460, height=30)

    resultado_texto = Text(app, font=("Arial", 10))
    resultado_texto.place(x=10, y=80, width=460, height=440)
    scrollbar_text = Scrollbar(app, command=resultado_texto.yview)
    scrollbar_text.place(x=470, y=80, height=440)
    resultado_texto.config(yscrollcommand=scrollbar_text.set)

    app.mainloop()

# ---------------------------
# FUNÇÃO: Excluir Fornecedor
# ---------------------------
def excluirFornecedor():
    app = Toplevel()
    app.title("Excluir Fornecedor")
    app.geometry("500x400")
    app.configure(background="#f2f2f2")

    Label(app, text="Digite o nome ou o CNPJ do fornecedor para excluir:", font=("Arial", 10), bg="#f2f2f2")\
        .place(x=10, y=10)
    vconsulta = Entry(app, font=("Arial", 10))
    vconsulta.place(x=10, y=40, width=380, height=30)

    listbox_sugestoes = Listbox(app, font=("Arial", 10))
    listbox_sugestoes.place(x=10, y=80, width=380, height=80)

    lbl_fornecedor_info = Label(app, text="Informações do fornecedor:", font=("Arial", 10), bg="#f2f2f2", justify="left", anchor="w")
    lbl_fornecedor_info.place(x=10, y=170, width=380, height=150)

    selected_for = {}

    def update_suggestions(event):
        search_text = vconsulta.get().strip().lower()
        listbox_sugestoes.delete(0, END)
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            like_term = "%" + search_text + "%"
            cursor.execute("SELECT * FROM fornecedor WHERE LOWER(nome_fornecedor) LIKE %s OR CAST(CNPJ AS CHAR) LIKE %s", (like_term, like_term))
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            for f in results:
                listbox_sugestoes.insert(END, f"{f.get('nome_fornecedor','')} - {f.get('CNPJ','')}")
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao buscar fornecedores: {err}")

    vconsulta.bind("<KeyRelease>", update_suggestions)

    def on_suggestion_select(event):
        selection = listbox_sugestoes.curselection()
        if selection:
            index = selection[0]
            sel_text = listbox_sugestoes.get(index)
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                # Assume que o CNPJ está após " - "
                cnpj_selected = sel_text.split(" - ")[1]
                cursor.execute("SELECT * FROM fornecedor WHERE CNPJ = %s", (cnpj_selected,))
                f = cursor.fetchone()
                cursor.close()
                conn.close()
                if f:
                    selected_for.clear()
                    selected_for.update(f)
                    info_text = (f"Nome: {f.get('nome_fornecedor','')}\n"
                                 f"Produto: {f.get('produto','')}\n"
                                 f"Telefone: {f.get('telefone','')}\n"
                                 f"CNPJ: {f.get('CNPJ','')}\n"
                                 f"Endereço: {f.get('endereço','')}")
                    lbl_fornecedor_info.config(text=info_text)
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao buscar fornecedor: {err}")

    listbox_sugestoes.bind("<Double-Button-1>", on_suggestion_select)

    def excluir_selected():
        if not selected_for:
            messagebox.showwarning("Erro", "Nenhum fornecedor selecionado.")
            return
        confirm = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Você realmente deseja excluir o seguinte fornecedor?\n\n"
            f"Nome: {selected_for.get('nome_fornecedor','')}\n"
            f"Produto: {selected_for.get('produto','')}\n"
            f"Telefone: {selected_for.get('telefone','')}\n"
            f"CNPJ: {selected_for.get('CNPJ','')}\n"
            f"Endereço: {selected_for.get('endereço','')}\n"
        )
        if confirm:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM fornecedor WHERE CNPJ = %s", (selected_for.get("CNPJ"),))
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Sucesso", "Fornecedor excluído com sucesso!")
                app.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao excluir fornecedor: {err}")
        else:
            messagebox.showinfo("Cancelado", "Exclusão cancelada.")

    Button(app, text="Excluir", command=excluir_selected, font=("Arial", 10))\
        .place(x=400, y=40, width=80, height=30)
    Button(app, text="Pesquisar", command=lambda: update_suggestions(None), font=("Arial", 10))\
        .place(x=400, y=80, width=80, height=30)

    app.mainloop()

# ---------------------------
# FUNÇÃO: Aba Administrador de Fornecedores
# ---------------------------
def fornecedores():
    admin_window = Toplevel()
    admin_window.title("Aba Administrador - Fornecedores")
    admin_window.geometry("700x300")
    admin_window.config(bg="DimGray") 

    img_adicionar = carregar_imagem("Adicionarfornecedor.png", 200, 200)
    img_excluir   = carregar_imagem("Excluirfornecedor.png", 200, 200)
    img_consultar = carregar_imagem("Consultarfornecedor.png", 200, 200)

    frame = tk.Frame(admin_window, bg="DimGray")
    frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    btn_adicionar = tk.Button(frame,
                              text="",
                              command=adicionar_fornecedor,
                              fg="Black",
                              bg="DimGray",
                              font=("Helvetica", 10, "bold"),
                              width=200,
                              height=200,
                              image=img_adicionar,
                              compound=tk.TOP)
    btn_adicionar.image = img_adicionar  
    btn_adicionar.grid(row=0, column=0, padx=5, pady=5)


    btn_consultar = tk.Button(frame,
                              text="",
                              command=consultaFornecedores,
                              fg="Black",
                              bg="DimGray",
                              font=("Helvetica", 10, "bold"),
                              width=200,
                              height=200,
                              image=img_consultar,
                              compound=tk.TOP)
    btn_consultar.image = img_consultar
    btn_consultar.grid(row=0, column=2, padx=5, pady=5)

    admin_window.mainloop()


# ---------------------------
# FUNÇÃO: Adicionar Funcionário
# ---------------------------
def adicionarFuncionario():
    app = Toplevel()
    app.title("Adicionar Funcionário")
    app.geometry("400x450")
    app.configure(background="#dde")

    largura = 400
    widget_width = 300
    widget_height = 20

    Label(app, text="Nome:", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura - widget_width)//2, y=10)
    vnome = Entry(app)
    vnome.place(x=(largura - widget_width)//2, y=30, width=widget_width, height=widget_height)

    Label(app, text="Telefone:", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura - widget_width)//2, y=60)
    vfone = Entry(app)
    vfone.place(x=(largura - widget_width)//2, y=80, width=widget_width, height=widget_height)

    Label(app, text="CPF:", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura - widget_width)//2, y=110)
    vcpf = Entry(app)
    vcpf.place(x=(largura - widget_width)//2, y=130, width=widget_width, height=widget_height)

    Label(app, text="E-mail:", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura - widget_width)//2, y=160)
    vemail = Entry(app)
    vemail.place(x=(largura - widget_width)//2, y=180, width=widget_width, height=widget_height)

    Label(app, text="Endereço:", background="#dde", foreground="#009", anchor=W)\
        .place(x=(largura - widget_width)//2, y=210)
    vobs = Text(app)
    vobs.place(x=(largura - widget_width)//2, y=230, width=widget_width, height=80)

    def gravarDados():
        nome = vnome.get().strip()
        telefone = vfone.get().strip()
        cpf = vcpf.get().strip()
        email = vemail.get().strip()
        endereco = vobs.get("1.0", END).strip()

        if not (nome and telefone and cpf and email and endereco):
            messagebox.showwarning("Erro", "Todos os campos são obrigatórios!")
            return
        try:
            telefone_int = int(telefone)
        except ValueError:
            messagebox.showerror("Erro", "Telefone deve ser numérico!")
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Verifica se já existe um funcionário com o mesmo CPF
            cursor.execute("SELECT cpf FROM colaborador WHERE cpf = %s", (cpf,))
            if cursor.fetchone():
                messagebox.showwarning("Erro", "Funcionário com esse CPF já existe!")
                cursor.close()
                conn.close()
                return
            cursor.execute(
                "INSERT INTO colaborador (nome_colaborador, cpf, telefone, email, endereço) VALUES (%s, %s, %s, %s, %s)",
                (nome, cpf, telefone_int, email, endereco)
            )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Sucesso", "Funcionário adicionado com sucesso!")
            app.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao adicionar funcionário: {err}")

    Button(app, text="Gravar", command=gravarDados)\
        .place(x=(largura - 100)//2, y=320, width=100, height=20)

    app.mainloop()

# ---------------------------
# FUNÇÃO: Consultar e Atualizar Funcionários
# ---------------------------
def consultaFuncionarios():
    def buscar():
        consulta = vconsulta.get().strip().lower()
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            if consulta:
                term = "%" + consulta + "%"
                cursor.execute(
                    "SELECT * FROM colaborador WHERE LOWER(nome_colaborador) LIKE %s OR cpf LIKE %s OR telefone LIKE %s",
                    (term, term, term)
                )
            else:
                cursor.execute("SELECT * FROM colaborador")
            resultados = cursor.fetchall()
            cursor.close()
            conn.close()
            resultado_texto.delete("1.0", END)
            if resultados:
                for func in resultados:
                    resultado_texto.insert(END, f"Nome: {func.get('nome_colaborador','')}\n")
                    resultado_texto.insert(END, f"Telefone: {func.get('telefone','')}\n")
                    resultado_texto.insert(END, f"CPF: {func.get('cpf','')}\n")
                    resultado_texto.insert(END, f"E-mail: {func.get('email','')}\n")
                    resultado_texto.insert(END, f"Endereço: {func.get('endereço','')}\n")
                    resultado_texto.insert(END, "-"*40 + "\n")
            else:
                resultado_texto.insert(END, "Nenhum funcionário encontrado.\n")
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao buscar funcionários: {err}")

    def atualizar_funcionario():
        update_win = Toplevel()
        update_win.title("Atualizar Funcionário")
        update_win.geometry("400x600")
        update_win.configure(background="#dde")

        Label(update_win, text="Digite o CPF do funcionário a atualizar:", background="#dde", foreground="#009")\
            .place(x=10, y=10)
        vconsulta_update = Entry(update_win, font=("Arial", 10))
        vconsulta_update.place(x=10, y=40, width=380, height=30)

        def buscar_funcionario():
            cpf_query = vconsulta_update.get().strip()
            if not cpf_query:
                messagebox.showwarning("Erro", "Digite o CPF para buscar o funcionário.")
                return
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM colaborador WHERE cpf = %s", (cpf_query,))
                func = cursor.fetchone()
                cursor.close()
                conn.close()
                if func:
                    entry_nome.delete(0, END)
                    entry_nome.insert(0, func.get("nome_colaborador", ""))
                    entry_telefone.delete(0, END)
                    entry_telefone.insert(0, func.get("telefone", ""))
                    entry_cpf.delete(0, END)
                    entry_cpf.insert(0, func.get("cpf", ""))
                    entry_email.delete(0, END)
                    entry_email.insert(0, func.get("email", ""))
                    entry_endereco.delete(0, END)
                    entry_endereco.insert(0, func.get("endereço", ""))
                else:
                    messagebox.showinfo("Info", "Funcionário não encontrado.")
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao buscar funcionário: {err}")

        Button(update_win, text="Buscar", command=buscar_funcionario)\
            .place(x=300, y=40, width=80, height=30)

        Label(update_win, text="Nome:", background="#dde", foreground="#009")\
            .place(x=10, y=90)
        entry_nome = Entry(update_win, font=("Arial", 10))
        entry_nome.place(x=10, y=110, width=380, height=20)

        Label(update_win, text="Telefone:", background="#dde", foreground="#009")\
            .place(x=10, y=140)
        entry_telefone = Entry(update_win, font=("Arial", 10))
        entry_telefone.place(x=10, y=160, width=380, height=20)

        Label(update_win, text="CPF:", background="#dde", foreground="#009")\
            .place(x=10, y=190)
        entry_cpf = Entry(update_win, font=("Arial", 10))
        entry_cpf.place(x=10, y=210, width=380, height=20)

        Label(update_win, text="E-mail:", background="#dde", foreground="#009")\
            .place(x=10, y=240)
        entry_email = Entry(update_win, font=("Arial", 10))
        entry_email.place(x=10, y=260, width=380, height=20)

        Label(update_win, text="Endereço:", background="#dde", foreground="#009")\
            .place(x=10, y=290)
        entry_endereco = Entry(update_win, font=("Arial", 10))
        entry_endereco.place(x=10, y=310, width=380, height=20)

        def salvar_atualizacao():
            novo_nome = entry_nome.get().strip()
            novo_telefone = entry_telefone.get().strip()
            novo_cpf = entry_cpf.get().strip()
            novo_email = entry_email.get().strip()
            novo_endereco = entry_endereco.get().strip()
            if not (novo_nome and novo_telefone and novo_cpf and novo_email and novo_endereco):
                messagebox.showwarning("Erro", "Todos os campos são obrigatórios!")
                return
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE colaborador SET nome_colaborador=%s, telefone=%s, cpf=%s, email=%s, endereço=%s WHERE cpf=%s",
                    (novo_nome, novo_telefone, novo_cpf, novo_email, novo_endereco, vconsulta_update.get().strip())
                )
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Sucesso", "Funcionário atualizado com sucesso!")
                update_win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao atualizar funcionário: {err}")

        Button(update_win, text="Salvar Informações", command=salvar_atualizacao)\
            .place(x=150, y=360, width=130, height=30)

        update_win.mainloop()

    app = Toplevel()
    app.title("Consulta de Funcionários")
    app.geometry("500x600")
    app.configure(background="#f2f2f2")

    Label(app, text="Digite o nome, telefone ou CPF:").place(x=10, y=10)
    vconsulta = Entry(app, font=("Arial", 10))
    vconsulta.place(x=10, y=40, width=380, height=30)
    vconsulta.bind("<KeyRelease>", lambda event: buscar())

    Button(app, text="Buscar", command=buscar)\
        .place(x=400, y=40, width=80, height=30)
    Button(app, text="Atualizar Funcionário", command=atualizar_funcionario)\
        .place(x=10, y=500, width=460, height=30)

    resultado_texto = Text(app, font=("Arial", 10))
    resultado_texto.place(x=10, y=80, width=460, height=400)

    app.mainloop()

# ---------------------------
# FUNÇÃO: Excluir Funcionário
# ---------------------------
def excluirFuncionario():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM colaborador")
        funcionarios = cursor.fetchall()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao carregar funcionários: {err}")
        return

    app = Toplevel()
    app.title("Excluir Funcionário")
    app.geometry("500x400")
    app.configure(background="#f2f2f2")

    Label(app, text="Digite o nome ou CPF do funcionário para excluir:", font=("Arial", 10), bg="#f2f2f2")\
        .place(x=10, y=10)
    vconsulta = Entry(app, font=("Arial", 10))
    vconsulta.place(x=10, y=40, width=380, height=30)

    listbox_sugestoes = Listbox(app, font=("Arial", 10))
    listbox_sugestoes.place(x=10, y=80, width=380, height=80)

    lbl_info = Label(app, text="Informações do funcionário:", font=("Arial", 10), bg="#f2f2f2", justify="left", anchor="w")
    lbl_info.place(x=10, y=170, width=380, height=150)

    selected_fun = {}

    def update_suggestions(event):
        search_text = vconsulta.get().strip().lower()
        listbox_sugestoes.delete(0, END)
        filtered = [f for f in funcionarios if search_text in f.get("nome_colaborador", "").lower() or search_text in f.get("cpf", "").lower()]
        for f in filtered:
            listbox_sugestoes.insert(END, f"{f.get('nome_colaborador','')} - {f.get('cpf','')}")
    vconsulta.bind("<KeyRelease>", update_suggestions)

    def on_suggestion_select(event):
        selection = listbox_sugestoes.curselection()
        if selection:
            index = selection[0]
            sel_text = listbox_sugestoes.get(index)
            for f in funcionarios:
                if f"{f.get('nome_colaborador','')} - {f.get('cpf','')}" == sel_text:
                    selected_fun.clear()
                    selected_fun.update(f)
                    info_text = (f"Nome: {f.get('nome_colaborador','')}\n"
                                 f"Telefone: {f.get('telefone','')}\n"
                                 f"CPF: {f.get('cpf','')}\n"
                                 f"E-mail: {f.get('email','')}\n"
                                 f"Endereço: {f.get('endereço','')}\n")
                    lbl_info.config(text=info_text)
                    break
    listbox_sugestoes.bind("<Double-Button-1>", on_suggestion_select)

    def excluir_selected():
        if not selected_fun:
            messagebox.showwarning("Erro", "Nenhum funcionário selecionado.")
            return
        confirm = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Você realmente deseja excluir o seguinte funcionário?\n\n"
            f"Nome: {selected_fun.get('nome_colaborador','')}\n"
            f"Telefone: {selected_fun.get('telefone','')}\n"
            f"CPF: {selected_fun.get('cpf','')}\n"
            f"E-mail: {selected_fun.get('email','')}\n"
            f"Endereço: {selected_fun.get('endereço','')}\n"
        )
        if confirm:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM colaborador WHERE cpf = %s", (selected_fun.get("cpf"),))
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Sucesso", "Funcionário excluído com sucesso!")
                app.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao excluir funcionário: {err}")
        else:
            messagebox.showinfo("Cancelado", "Exclusão cancelada.")

    Button(app, text="Excluir", command=excluir_selected, font=("Arial", 10))\
        .place(x=400, y=40, width=80, height=30)
    Button(app, text="Pesquisar", command=lambda: update_suggestions(None), font=("Arial", 10))\
        .place(x=400, y=80, width=80, height=30)

    app.mainloop()

# ---------------------------
# FUNÇÃO: Aba Administrador de Funcionários
# ---------------------------
def funcionarios():
    admin_window = Toplevel()
    admin_window.title("Aba Administrador - Funcionários")
    admin_window.geometry("700x300")
    admin_window.config(bg="DimGray")

    img_adicionar = carregar_imagem("Adicionarfuncionario.png", 200, 200)
    img_excluir   = carregar_imagem("Excluirfuncionario.png", 200, 200)
    img_consultar = carregar_imagem("Consultarfuncionario.png", 200, 200)

    frame = tk.Frame(admin_window, bg="DimGray")
    frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    btn_adicionar = Button(frame,
                           text="",
                           command=adicionarFuncionario,
                           fg="Black",
                           bg="SlateGray1",
                           font=("Helvetica", 10, "bold"),
                           width=200,
                           height=200,
                           image=img_adicionar,
                           compound=tk.TOP)
    btn_adicionar.image = img_adicionar
    btn_adicionar.grid(row=0, column=0, padx=5, pady=5)

    btn_excluir = Button(frame,
                         text="",
                         command=excluirFuncionario,
                         fg="Black",
                         bg="SlateGray1",
                         font=("Helvetica", 10, "bold"),
                         width=200,
                         height=200,
                         image=img_excluir,
                         compound=tk.TOP)
    btn_excluir.image = img_excluir
    btn_excluir.grid(row=0, column=1, padx=5, pady=5)

    btn_consultar = Button(frame,
                           text="",
                           command=consultaFuncionarios,
                           fg="Black",
                           bg="SlateGray1",
                           font=("Helvetica", 10, "bold"),
                           width=200,
                           height=200,
                           image=img_consultar,
                           compound=tk.TOP)
    btn_consultar.image = img_consultar
    btn_consultar.grid(row=0, column=2, padx=5, pady=5)

    admin_window.mainloop()


# Função para atualizar (ou cadastrar) o fornecedor na tabela 'fornecedor'
def atualizar_fornecedor_db(novo_produto, fornecedor):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Procura o fornecedor (comparação case-insensitive)
        cursor.execute("SELECT produto FROM fornecedor WHERE LOWER(nome_fornecedor)=%s", (fornecedor.lower(),))
        row = cursor.fetchone()
        if row:
            # Se já existir, atualiza a lista de produtos (supondo que estejam separados por vírgula)
            prod_str = row.get("produto", "")
            produtos = [p.strip() for p in prod_str.split(",") if p.strip()] if prod_str else []
            if novo_produto.lower() not in [p.lower() for p in produtos]:
                novos_produtos = ", ".join(produtos + [novo_produto]) if produtos else novo_produto
                cursor.execute("UPDATE fornecedor SET produto=%s WHERE LOWER(nome_fornecedor)=%s", 
                               (novos_produtos, fornecedor.lower()))
        else:
            # Se não existir, insere um novo registro com valores padrão para os demais campos
            # (endereço, CNPJ e telefone são obrigatórios – aqui usamos valores padrão)
            cursor.execute(
                "INSERT INTO fornecedor (nome_fornecedor, endereço, produto, CNPJ, telefone) VALUES (%s, %s, %s, %s, %s)",
                (fornecedor, "N/A", novo_produto, 0, 0)
            )
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao atualizar fornecedor: {err}")

# ===================================================
# FUNÇÃO: Vendas (Interface de Vendas com Estoque e Pagamento)
# ===================================================

# Função de vendas (janela com banco de dados) – layout igual ao da versão com TXT
def vendas():
    estoque_temp = carregar_estoque_db()

    root = tk.Tk()
    root.title("Venda")
    root.geometry("1050x700")
    root.configure(bg="DimGray")

    # Configuração do canvas com scrollbar para suportar janelas grandes
    canvas = tk.Canvas(root, bg="DimGray")
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)
    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.bind("<Configure>", on_configure)
    frame_principal = tk.Frame(canvas, bg="DimGray")
    canvas.create_window((0, 0), window=frame_principal, anchor="nw")

    # Função para limpar os campos e recarregar o estoque
    def limpar():
        carro_entry.delete(0, END)
        placa_entry.delete(0, END)
        valor_entry.delete(0, END)
        descricao_entry.delete("1.0", END)
        pecas_selecionadas.clear()
        for item in selected_treeview.get_children():
            selected_treeview.delete(item)
        nonlocal estoque_temp
        estoque_temp = carregar_estoque_db()
        atualizar_sugestoes(None)

    # Frame superior para dados e pagamento
    frame_superior = tk.Frame(canvas, bg="DimGray")
    frame_superior.place(x=500, y=10)

    # Widgets para os dados do carro e serviço
    frame_dados = tk.Frame(frame_superior, bg="DimGray")
    frame_dados.pack(side=tk.LEFT, padx=10)
    Label(frame_dados, text="Nome do dono(a):", font=("Arial", 12), bg="DimGray", fg="white")\
        .grid(row=0, column=0, sticky="w", pady=5)
    carro_entry = Entry(frame_dados, font=("Arial", 12), width=25)
    carro_entry.grid(row=1, column=0, pady=5)
    Label(frame_dados, text="Placa do carro:", font=("Arial", 12), bg="DimGray", fg="white")\
        .grid(row=2, column=0, sticky="w", pady=5)
    placa_entry = Entry(frame_dados, font=("Arial", 12), width=25)
    placa_entry.grid(row=3, column=0, pady=5)
    Label(frame_dados, text="Valor do Serviço:", font=("Arial", 12), bg="DimGray", fg="white")\
        .grid(row=4, column=0, sticky="w", pady=5)
    valor_entry = Entry(frame_dados, font=("Arial", 12), width=25)
    valor_entry.grid(row=5, column=0, pady=5)
    Label(frame_dados, text="Descrição do Serviço:", font=("Arial", 12), bg="DimGray", fg="white")\
        .grid(row=6, column=0, sticky="w", pady=5)
    descricao_entry = Text(frame_dados, font=("Arial", 12), width=25, height=20)
    descricao_entry.grid(row=7, column=0, pady=5)

    # Frame de pagamento
    frame_pagamento = tk.LabelFrame(frame_superior, text="Forma de Pagamento", font=("Arial", 12),
                                    bg="DimGray", fg="white")
    frame_pagamento.pack(side=TOP, padx=10)
    forma_pagamento_var = tk.StringVar()
    metodos_pagamento = ["Cartão Crédito", "Cartão Débito", "Dinheiro", "PIX",
                         "TEF Crédito", "TEF Débito", "TEF PIX"]
    def set_pagamento(metodo):
        forma_pagamento_var.set(metodo)
        label_pagamento.config(text=f"Pagamento selecionado: {metodo}")
    for i, metodo in enumerate(metodos_pagamento):
        btn = Button(frame_pagamento, text=metodo, command=lambda m=metodo: set_pagamento(m),
                     bg="DimGray", fg="white", font=("Arial", 12))
        btn.grid(row=i, column=0, sticky="w", padx=10, pady=2)
    label_pagamento = Label(frame_pagamento, text="Pagamento selecionado: ", font=("Arial", 10), bg="DimGray", fg="white")
    label_pagamento.grid(row=len(metodos_pagamento), column=0, pady=5)

    frame_botoes = tk.Frame(frame_pagamento, bg="DimGray")
    frame_botoes.grid(row=len(metodos_pagamento)+1, column=0, pady=20)
    Button(frame_botoes, text="CANCELAR", width=20, command=limpar,
           bg="red", fg="white").pack(pady=5)
    Button(frame_botoes, text="LIMPAR", width=20, command=limpar,
           bg="yellow").pack(pady=5)

    # Função para salvar os dados do serviço no banco
    def salvar_dados(carro, placa, descricao_servico, forma_pagamento, valor_servico):
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO serviços (nome_cliente, placa, valor_total, descricao, forma_pagamento) VALUES (%s, %s, %s, %s, %s)",
                (carro, placa, float(valor_servico), descricao_servico, forma_pagamento)
            )
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao salvar serviço: {err}")

    # Finaliza o pagamento: verifica campos, chama função de salvar dados e atualiza estoque
    def finalizar_pagamento():
        forma_pagamento = forma_pagamento_var.get()
        descricao_servico = descricao_entry.get("1.0", END).strip()
        valor_servico = valor_entry.get().strip()
        carro_val = carro_entry.get().strip()
        placa_val = placa_entry.get().strip()
        if not (carro_val and placa_val and descricao_servico and valor_servico and forma_pagamento):
            messagebox.showwarning("Erro", "Todos os campos devem ser preenchidos!")
            return

        if not carro_existe(placa_val):
            if messagebox.askyesno("Carro não cadastrado", "O carro não está cadastrado. Deseja cadastrá-lo agora?"):
                adicionarCarro()
            return

        salvar_dados(carro_val, placa_val, descricao_servico, forma_pagamento, valor_servico)
        if pecas_selecionadas:
            salvar_estoque_db(estoque_temp)
        messagebox.showinfo("Pagamento", "Pagamento Finalizado")
        limpar()

    Button(frame_botoes, text="FINALIZAR PAGAMENTO", width=20,
           command=finalizar_pagamento, bg="green", fg="white").pack(pady=10)

    # --- PEÇAS UTILIZADAS ---
    pecas_selecionadas = []
    frame_pecas = tk.LabelFrame(canvas, text="Peças Utilizadas", font=("Arial", 12),
                                bg="DimGray", fg="white")
    frame_pecas.place(x=0, y=10)
    Label(frame_pecas, text="Digite a peça utilizada:", font=("Arial", 12),
          bg="DimGray", fg="white").pack(anchor="w", padx=10, pady=5)
    peca_entry = Entry(frame_pecas, font=("Arial", 12), width=30)
    peca_entry.pack(padx=10, pady=5)
    sug_frame = tk.Frame(frame_pecas, bg="DimGray")
    sug_frame.pack(padx=10, pady=5, fill="both")
    suggestion_listbox = Listbox(sug_frame, font=("Arial", 12), width=30, height=5)
    suggestion_listbox.pack(side="left", fill="both", expand=True)
    sug_scrollbar = Scrollbar(sug_frame, orient="vertical", command=suggestion_listbox.yview)
    sug_scrollbar.pack(side="right", fill="y")
    suggestion_listbox.config(yscrollcommand=sug_scrollbar.set)

    def on_suggestion_select(event):
        selection = suggestion_listbox.curselection()
        if selection:
            index = suggestion_listbox.curselection()[0]
            item_str = suggestion_listbox.get(index)
            nome = item_str.split(" (Qtd:")[0]
            adicionar_peca_por_nome(nome)
            peca_entry.delete(0, END)
            suggestion_listbox.delete(0, END)
    suggestion_listbox.bind("<Double-Button-1>", on_suggestion_select)

    def atualizar_sugestoes(event):
        texto = peca_entry.get().lower().strip()
        suggestion_listbox.delete(0, END)
        matching_pecas = []
        for nome, prod in estoque_temp.items():
            if prod.get("Quantidade", 0) > 0:
                if texto == "" or texto in nome.lower():
                    matching_pecas.append(f"{nome} (Qtd: {prod.get('Quantidade',0)})")
        for item in matching_pecas:
            suggestion_listbox.insert(END, item)
    peca_entry.bind("<KeyRelease>", atualizar_sugestoes)
    atualizar_sugestoes(None)

    def adicionar_peca_por_nome(nome):
        if nome not in estoque_temp:
            messagebox.showwarning("Atenção", "Peça não encontrada no estoque!")
            return
        prod = estoque_temp[nome]
        if prod.get("Quantidade", 0) <= 0:
            messagebox.showwarning("Atenção", "Peça não disponível ou sem estoque!")
            return
        qtd = simpledialog.askinteger("Quantidade", f"Informe a quantidade para '{nome}':",
                                      minvalue=1, maxvalue=prod.get("Quantidade", 0))
        if not qtd:
            return
        if qtd > prod.get("Quantidade", 0):
            messagebox.showwarning("Atenção", "Quantidade solicitada excede a quantidade disponível!")
            return
        unitario = prod.get("Valor Unitário", 0.0)
        total_valor = unitario * qtd
        item = {"nome": nome, "unitario": unitario, "quantidade": qtd, "total": total_valor}
        pecas_selecionadas.append(item)
        prod["Quantidade"] -= qtd
        atualizar_sugestoes(None)
        selected_treeview.insert("", "end", values=(nome, f"{unitario:.2f}", f"{total_valor:.2f}", qtd))

    def remover_peca():
        selected = selected_treeview.selection()
        if selected:
            item_id = selected[0]
            vals = selected_treeview.item(item_id, "values")
            nome = vals[0]
            qtd_removida = int(vals[3])
            for i, item in enumerate(pecas_selecionadas):
                if item["nome"] == nome and item["quantidade"] == qtd_removida:
                    del pecas_selecionadas[i]
                    break
            if nome in estoque_temp:
                estoque_temp[nome]["Quantidade"] += qtd_removida
            atualizar_sugestoes(None)
            selected_treeview.delete(item_id)

    Label(frame_pecas, text="Peças Selecionadas:", font=("Arial", 12),
          bg="DimGray", fg="white").pack(anchor="w", padx=10, pady=5)
    sel_frame = tk.Frame(frame_pecas, bg="DimGray")
    sel_frame.pack(padx=10, pady=5, fill="both")
    columns = ("Produto", "Valor Unitário", "Valor Total", "Quantidade")
    selected_treeview = ttk.Treeview(sel_frame, columns=columns, show="headings", height=5)
    for col in columns:
        selected_treeview.heading(col, text=col)
        if col == "Produto":
            selected_treeview.column(col, width=150)
        else:
            selected_treeview.column(col, width=100, anchor="center")
    selected_treeview.pack(side="left", fill="both", expand=True)
    sel_scroll = Scrollbar(sel_frame, orient="vertical", command=selected_treeview.yview)
    sel_scroll.pack(side="right", fill="y")
    selected_treeview.config(yscrollcommand=sel_scroll.set)

    Button(frame_pecas, text="Remover Peça", font=("Arial", 12),
           command=remover_peca, bg="orange", fg="white").pack(padx=10, pady=5)

    root.mainloop()
# ===================================================
# (Funções auxiliares para carrinho já convertidas anteriormente)
# As funções abaixo (excluir_produto_new_db, excluir_tudo_new_db, marcar_comprado_new_db,
# carregar_produtos_new_db e calcular_valor_total_new_db) foram adaptadas para operar via DB.
# ===================================================

def excluir_produto_new_db(treeview_new, label_valor_total):
    selected = treeview_new.selection()
    if not selected:
        messagebox.showwarning("Aviso", "Selecione um produto para excluir.")
        return
    item = treeview_new.item(selected[0])
    prod = item["values"][0]
    fornec = item["values"][1]
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lista_compras WHERE LOWER(nome_peca)=%s AND LOWER(nome_fornecedor)=%s",
                       (prod.lower(), fornec.lower()))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao excluir produto: {err}")
        return
    carregar_produtos_new_db(treeview_new)
    calcular_valor_total_new_db(label_valor_total)

def excluir_tudo_new_db(treeview_new, label_valor_total):
    resposta = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir todos os itens?")
    if resposta:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM lista_compras")
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao excluir todos os produtos: {err}")
            return
        carregar_produtos_new_db(treeview_new)
        calcular_valor_total_new_db(label_valor_total)

def marcar_comprado_new_db(treeview_new, label_valor_total):
    selected = treeview_new.selection()
    if not selected:
        messagebox.showwarning("Aviso", "Selecione um item para marcar como comprado.")
        return
    for sel in selected:
        item = treeview_new.item(sel)
        prod = item["values"][0]
        fornec = item["values"][1]
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM lista_compras WHERE LOWER(nome_peca)=%s AND LOWER(nome_fornecedor)=%s",
                           (prod.lower(), fornec.lower()))
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao marcar como comprado: {err}")
    carregar_produtos_new_db(treeview_new)
    calcular_valor_total_new_db(label_valor_total)

def carregar_produtos_new_db(treeview_new):
    treeview_new.delete(*treeview_new.get_children())
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM lista_compras")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        for row in rows:
            treeview_new.insert("", "end", values=(
                row["nome_peca"],
                row["nome_fornecedor"],
                row["quantidade"],
                f"{row['valor_unit']:.2f}",
                f"{row['valor_total']:.2f}"
            ))
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao carregar produtos: {err}")

def calcular_valor_total_new_db(label_valor_total):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(valor_total) FROM lista_compras")
        row = cursor.fetchone()
        total = row[0] if row and row[0] is not None else 0
        cursor.close()
        conn.close()
        label_valor_total.config(text=f"Valor Total: R${total:.2f}")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao calcular valor total: {err}")


# ---------------------------
# FUNÇÃO: Gravar Compromisso no Banco de Dados
# ---------------------------
def gravarDados(data_selecionada, tipo, descricao):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO compromissos (data_compromisso, tipo, descricao) VALUES (%s, %s, %s)",
            (data_selecionada, tipo, descricao)
        )
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Sucesso", "Compromisso adicionado com sucesso!")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao gravar compromisso: {err}")

# ---------------------------
# FUNÇÃO: Carregar Compromissos para uma Data
# ---------------------------
def carregarCompromissos(data_selecionada):
    lista = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM compromissos WHERE data_compromisso = %s",
            (data_selecionada,)
        )
        lista = cursor.fetchall()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao carregar compromissos: {err}")
    return lista

# ---------------------------
# FUNÇÃO: Exibir Compromissos na Lista
# ---------------------------
def exibirCompromissos(data_selecionada, listbox):
    listbox.delete(0, END)
    comps = carregarCompromissos(data_selecionada)
    for comp in comps:
        listbox.insert(END, f"Tipo: {comp.get('tipo','')}")
        listbox.insert(END, f"Descrição: {comp.get('descricao','')}")
        listbox.insert(END, "-" * 40)

# ---------------------------
# FUNÇÃO: Adicionar Compromisso (janela para uma data selecionada)
# ---------------------------
def adicionarCompromisso(event):
    # Utiliza o widget que disparou o evento (o calendário) para obter a data selecionada
    data_selecionada_str = event.widget.get_date()
    try:
        # Converte para objeto date (formato dd/mm/yyyy)
        data_db = datetime.strptime(data_selecionada_str, "%d/%m/%Y").date()
    except Exception as e:
        messagebox.showerror("Erro", f"Data inválida: {e}")
        return

    app = Toplevel()
    app.title(f"Adicionar Compromisso - {data_selecionada_str}")
    app.geometry("600x600")
    app.configure(background="#f0f4f8")
    
    Label(app, text="Compromissos para hoje", font=("Arial", 16, "bold"),
          background="#f0f4f8", foreground="#5c6bc0").place(x=10, y=10)
    
    Label(app, text="Compromissos existentes:", background="#f0f4f8",
          foreground="#00796b", font=("Arial", 12)).place(x=10, y=50)
    
    # Frame para a lista de compromissos com barra de rolagem
    frame_lista = tk.Frame(app)
    frame_lista.place(x=10, y=80, width=560, height=150)
    compromisso_lista = tk.Listbox(frame_lista, width=60, height=10, font=("Arial", 12),
                                   bd=0, selectmode=SINGLE, bg="#ffffff", fg="#00796b")
    compromisso_lista.pack(side="left", fill=BOTH, expand=True)
    scrollbar_lista = tk.Scrollbar(frame_lista, orient=VERTICAL, command=compromisso_lista.yview)
    scrollbar_lista.pack(side="right", fill=Y)
    compromisso_lista.config(yscrollcommand=scrollbar_lista.set)
    
    # Carregar compromissos existentes para a data selecionada
    exibirCompromissos(data_db, compromisso_lista)
    
    Label(app, text="Tipo de compromisso:", background="#f0f4f8",
          foreground="#00796b", font=("Arial", 12)).place(x=10, y=300)
    tipo_entry = Entry(app, font=("Arial", 12), bd=2, relief="solid")
    tipo_entry.place(x=10, y=320, width=460, height=30)
    
    Label(app, text="Descrição do compromisso:", background="#f0f4f8",
          foreground="#00796b", font=("Arial", 12)).place(x=10, y=380)
    frame_descricao = tk.Frame(app)
    frame_descricao.place(x=10, y=400, width=560, height=100)
    descricao_entry = Text(frame_descricao, height=4, width=50, font=("Arial", 12),
                           bd=2, relief="solid")
    descricao_entry.pack(side="left", fill=BOTH, expand=True)
    scrollbar_descricao = tk.Scrollbar(frame_descricao, orient=VERTICAL, command=descricao_entry.yview)
    scrollbar_descricao.pack(side="right", fill=Y)
    descricao_entry.config(yscrollcommand=scrollbar_descricao.set)
    
    def salvar_comp():
        tipo = tipo_entry.get().strip()
        descricao = descricao_entry.get("1.0", END).strip()
        if tipo and descricao:
            gravarDados(data_db, tipo, descricao)
            exibirCompromissos(data_db, compromisso_lista)
            tipo_entry.delete(0, END)
            descricao_entry.delete("1.0", END)
        else:
            messagebox.showwarning("Erro", "Por favor, preencha todos os campos!")
    
    btn_salvar = Button(app, text="Gravar compromisso", command=salvar_comp,
                        font=("Arial", 12), bg="#5c6bc0", fg="white", relief="solid", bd=2)
    btn_salvar.place(x=200, y=510, width=160, height=30)
    btn_salvar.bind("<Enter>", lambda e: btn_salvar.config(background='#3f51b5'))
    btn_salvar.bind("<Leave>", lambda e: btn_salvar.config(background='#5c6bc0'))
    
    app.mainloop()

# ---------------------------
# FUNÇÃO: Compromissos – Janela Principal (Calendário)
# ---------------------------
def compromissos():
    root = tk.Tk()
    root.title("Calendário")
    root.geometry("400x400")
    root.configure(background="#f0f4f8")
    
    Label(root, text="Calendário de Compromissos", font=("Arial", 18, "bold"),
          background="#f0f4f8", foreground="#5c6bc0").pack(pady=20)
    
    calendario = Calendar(root, locale="pt_br", selectmode="day",
                          date_pattern="dd/mm/yyyy", background="#ffffff",
                          foreground="#00796b", bordercolor="#00796b",
                          headersbackground="#5c6bc0", weekendbackground="#f0f4f8")
    calendario.pack(padx=10, pady=10)
    
    calendario.bind("<<CalendarSelected>>", adicionarCompromisso)
    
    root.mainloop()

def sair_fullscreen(event=None):
    main_window.attributes("-fullscreen", False)
    if login_window is not None:
        login_window.destroy()


def carregar_imagem(caminho, largura, altura):
    pil_image = Image.open(caminho)
    pil_image = pil_image.resize((largura, altura), Image.LANCZOS)
    return ImageTk.PhotoImage(pil_image)


# Função para verificar o login (admin = "1234", funcionário = "5678")
def verificar_login():
    username = user_type.get()
    password = password_entry.get()
    if username == "Administrador" and password == "1234":
        login_window.destroy()  # Fecha a janela de login
        criar_interface_principal()  # Abre a interface do administrador
    elif username == "Funcionário" and password == "5678":
        login_window.destroy()
        criar_interface_principal_funcionario()
    else:
        messagebox.showerror("Falha no Login", "Nome de usuário ou senha incorretos.")




# Cria a janela principal (Tk) e a oculta até que o login seja validado
main_window = tk.Tk()
main_window.withdraw()


# ------------------------- Janela de Login -------------------------
login_window = tk.Toplevel(main_window)
login_window.title("Formulário de Login")
login_window.geometry("1000x600")
login_window.attributes("-fullscreen", True)
login_window.bind("<Escape>", sair_fullscreen)
login_window.config(bg="DimGray")


# Cabeçalho com a imagem Platinum (igual à interface do administrador)
top_frame = tk.Frame(login_window, bg="DarkOrchid4", height=100)
top_frame.pack(side="top", fill="x")


frame_imagem = tk.Frame(login_window, bg="DimGray", height=1000, width=300)
frame_imagem.place(x=0, y=0)
imagem_platinum = carregar_imagem('PLATINUM.png', 250, 170)
label_imagem = tk.Label(frame_imagem, image=imagem_platinum, bg="DimGray")
label_imagem.image = imagem_platinum  # mantém referência
label_imagem.pack(side="left", padx=10)


# --- Novo Frame de Login com tamanho aumentado ---
# Tamanho fixo (por exemplo, 500x300) e sem propagação de tamanho dos widgets internos
frame_login = tk.Frame(login_window, bg="#444", padx=20, pady=20, width=500, height=300)
frame_login.pack(expand=True)
frame_login.pack_propagate(False)


# Widgets de login
tk.Label(frame_login, text="Usuário", bg="#444", fg="#fff",
         font=("Helvetica", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0,10))
user_type = tk.StringVar(value="Administrador")
user_type_menu = tk.OptionMenu(frame_login, user_type, "Administrador", "Funcionário")
user_type_menu.config(font=("Helvetica", 12), width=18)
user_type_menu.grid(row=1, column=0, pady=5)


tk.Label(frame_login, text="Senha", bg="#444", fg="#fff",
         font=("Helvetica", 14, "bold")).grid(row=2, column=0, sticky="w", pady=(20,5))
password_entry = tk.Entry(frame_login, show="*", font=("Helvetica", 12), width=22)
password_entry.grid(row=3, column=0, pady=5)


login_button = tk.Button(frame_login, text="LOGIN", bg="#008CBA", fg="#fff",
                         font=("Helvetica", 14, "bold"), command=verificar_login,
                         width=8, height=1)
login_button.grid(row=4, column=0, pady=20)


# ------------------------- Interface do Administrador -------------------------
def criar_interface_principal():
    main_window.deiconify()  # Exibe a janela principal
    main_window.title("Aba Administrador")
    main_window.geometry("1000x600")
    main_window.attributes("-fullscreen", True)
    main_window.bind("<Escape>", sair_fullscreen)
    main_window.config(bg="DimGray")
    
    # Cabeçalho com a imagem Platinum
    top_frame = tk.Frame(main_window, bg="DarkOrchid4", height=100)
    top_frame.pack(side="top", fill="x")
    
    frame_imagem = tk.Frame(main_window, bg="DimGray", height=1000, width=300)
    frame_imagem.place(x=0, y=0)
    imagem_platinum = carregar_imagem('PLATINUM.png', 250, 170)
    label_imagem = tk.Label(frame_imagem, image=imagem_platinum, bg="DimGray")
    label_imagem.image = imagem_platinum  
    label_imagem.pack(side="left", padx=10)
    
    # Frame para os botões (interface do administrador)
    frame = tk.Frame(main_window, bg="DimGray")
    frame.place(relx=0.5, rely=0.55, anchor="center")
    
    main_window.imagens = {}
    main_window.imagens['clientes']     = carregar_imagem('Cliente.png', 220, 200)
    main_window.imagens['funcionarios']   = carregar_imagem('Funcionario.png', 220, 200)
    main_window.imagens['carros']         = carregar_imagem('Carro.png', 220, 200)
    main_window.imagens['fornecedores']   = carregar_imagem('Fornecedor.png', 220, 200)
    main_window.imagens['carrinho']       = carregar_imagem('Lista de compras.png', 220, 200)
    main_window.imagens['compromissos']   = carregar_imagem('Compromissos.png', 220, 200)
    main_window.imagens['vendas']         = carregar_imagem('Servico.png', 220, 200)
    main_window.imagens['estoque']        = carregar_imagem('Estoque.png', 220, 200)
    
    global botao_clientes, botao_funcionarios, botao_carros, botao_fornecedores
    global botao_carrinho, botao_compromissos, botao_vendas, botao_consulta_estoque
    
    botao_clientes = tk.Button(frame, command=clientes, fg="Black", bg="SlateGray1",
                               image=main_window.imagens['clientes'])
    botao_clientes.grid(row=0, column=0, padx=5, pady=5)
    
    botao_funcionarios = tk.Button(frame, command=funcionarios, fg="Black", bg="SlateGray1",
                                   image=main_window.imagens['funcionarios'])
    botao_funcionarios.grid(row=0, column=1, padx=5, pady=5)
    
    botao_carros = tk.Button(frame, command=carros, fg="Black", bg="SlateGray1",
                             image=main_window.imagens['carros'])
    botao_carros.grid(row=0, column=2, padx=5, pady=5)
    
    botao_fornecedores = tk.Button(frame, command=fornecedores, fg="Black", bg="SlateGray1",
                                   image=main_window.imagens['fornecedores'])
    botao_fornecedores.grid(row=1, column=0, padx=5, pady=5)
    
    botao_carrinho = tk.Button(frame, command=carrinhoDeCompras, fg="Black", bg="SlateGray1",
                               image=main_window.imagens['carrinho'])
    botao_carrinho.grid(row=1, column=1, padx=5, pady=5)
    
    botao_compromissos = tk.Button(frame, command=compromissos, fg="Black", bg="SlateGray1",
                                   image=main_window.imagens['compromissos'])
    botao_compromissos.grid(row=1, column=2, padx=5, pady=5)
    
    botao_vendas = tk.Button(frame, command=vendas, fg="Black", bg="SlateGray1",
                             image=main_window.imagens['vendas'])
    botao_vendas.grid(row=0, column=3, padx=5, pady=5)
    
    botao_consulta_estoque = tk.Button(frame, command=mostrar_estoque_aba, fg="Black", bg="SlateGray1",
                                       image=main_window.imagens['estoque'])
    botao_consulta_estoque.grid(row=1, column=3, padx=5, pady=5)


# ------------------------- Interface do Funcionário -------------------------
def criar_interface_principal_funcionario():
    main_window.deiconify()
    main_window.title("Aba Funcionário")
    main_window.geometry("1000x600")
    main_window.attributes("-fullscreen", True)
    main_window.bind("<Escape>", sair_fullscreen)
    main_window.config(bg="DimGray")
    
    top_frame = tk.Frame(main_window, bg="DarkOrchid4", height=100)
    top_frame.pack(side="top", fill="x")
    
    frame_imagem = tk.Frame(main_window, bg="DimGray", height=1000, width=300)
    frame_imagem.place(x=0, y=0)
    imagem_platinum = carregar_imagem('PLATINUM.png', 250, 170)
    label_imagem = tk.Label(frame_imagem, image=imagem_platinum, bg="DimGray")
    label_imagem.image = imagem_platinum
    label_imagem.pack(side="left", padx=10)
    
    frame = tk.Frame(main_window, bg="DimGray")
    frame.place(relx=0.5, rely=0.55, anchor="center")
    
    main_window.imagens = {}
    main_window.imagens['clientes']   = carregar_imagem('Cliente.png', 220, 200)
    main_window.imagens['carros']       = carregar_imagem('Carro.png', 220, 200)
    main_window.imagens['fornecedores'] = carregar_imagem('Fornecedor.png', 220, 200)
    main_window.imagens['carrinho']     = carregar_imagem('Lista de compras.png', 220, 200)
    main_window.imagens['compromissos'] = carregar_imagem('Compromissos.png', 220, 200)
    main_window.imagens['vendas']       = carregar_imagem('Servico.png', 220, 200)
    main_window.imagens['estoque']      = carregar_imagem('Estoque.png', 220, 200)
    
    global botao_clientes, botao_carros, botao_fornecedores, botao_carrinho
    global botao_compromissos, botao_vendas, botao_consulta_estoque
    
    botao_clientes = tk.Button(frame, command=clientes, fg="Black", bg="SlateGray1",
                               image=main_window.imagens['clientes'])
    botao_clientes.grid(row=0, column=0, padx=5, pady=5)
    
    botao_carros = tk.Button(frame, command=carros, fg="Black", bg="SlateGray1",
                             image=main_window.imagens['carros'])
    botao_carros.grid(row=0, column=1, padx=5, pady=5)
    
    botao_fornecedores = tk.Button(frame, command=fornecedores, fg="Black", bg="SlateGray1",
                                   image=main_window.imagens['fornecedores'])
    botao_fornecedores.grid(row=1, column=0, padx=5, pady=5)
    
    botao_carrinho = tk.Button(frame, command=carrinhoDeCompras, fg="Black", bg="SlateGray1",
                               image=main_window.imagens['carrinho'])
    botao_carrinho.grid(row=1, column=1, padx=5, pady=5)
    
    botao_compromissos = tk.Button(frame, command=compromissos, fg="Black", bg="SlateGray1",
                                   image=main_window.imagens['compromissos'])
    botao_compromissos.grid(row=1, column=2, padx=5, pady=5)
    
    botao_vendas = tk.Button(frame, command=vendas, fg="Black", bg="SlateGray1",
                             image=main_window.imagens['vendas'])
    botao_vendas.grid(row=0, column=2, padx=5, pady=5)
    
    botao_consulta_estoque = tk.Button(frame, command=mostrar_estoque_aba, fg="Black", bg="SlateGray1",
                                       image=main_window.imagens['estoque'])
    botao_consulta_estoque.grid(row=0, column=3, padx=5, pady=5)


# Inicia o loop principal
main_window.mainloop()
