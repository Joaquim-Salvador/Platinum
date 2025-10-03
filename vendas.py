import mysql.connector
import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, END, W
from tkinter import ttk

# Função para obter conexão com o banco de dados
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",      
        password="",    
        database="PLATINUM2"
    )

# ---------------------------
# Funções para o Carrinho de Compras (Tabela lista_compras)
# ---------------------------
def gravarDadosComQuant_db(vnomeDaPeca, vquantidade, vunitario, vsupplier, treeview, label_valor_total):
    nome = vnomeDaPeca.get().strip()
    quantidade = vquantidade.get().strip()
    unitario = vunitario.get().strip()
    fornecedor = vsupplier.get().strip()
    if not (nome and quantidade and unitario and fornecedor):
        messagebox.showwarning("Erro", "Todos os campos devem ser preenchidos!")
        return
    try:
        quantidade = int(quantidade)
        unitario = float(unitario)
    except ValueError:
        messagebox.showwarning("Erro", "Quantidade ou Valor Unitário inválidos!")
        return
    valor_total = unitario * quantidade
    try:
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        # Tenta inserir ou atualizar o item na tabela lista_compras (supondo que nome_peca seja chave primária)
        cursor.execute(
            "INSERT INTO lista_compras (nome_peca, nome_fornecedor, valor_unit, valor_total, quantidade) "
            "VALUES (%s, %s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE quantidade = quantidade + %s, valor_total = valor_unit * quantidade",
            (nome, fornecedor, unitario, valor_total, quantidade, quantidade)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao gravar item: {err}")
        return
    # Atualiza a interface
    carregar_produtos_new_db(treeview)
    calcular_valor_total_new_db(label_valor_total)
    # Limpa os campos
    vnomeDaPeca.delete(0, END)
    vquantidade.delete(0, END)
    vunitario.delete(0, END)
    vsupplier.delete(0, END)

def excluir_produto_new_db(treeview, label_valor_total):
    selected = treeview.selection()
    if not selected:
        messagebox.showwarning("Atenção", "Selecione um produto para deletar.")
        return
    item = treeview.item(selected[0])
    nome = item["values"][0]
    try:
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lista_compras WHERE nome_peca = %s", (nome,))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao deletar produto: {err}")
        return
    carregar_produtos_new_db(treeview)
    calcular_valor_total_new_db(label_valor_total)

def excluir_tudo_new_db(treeview, label_valor_total):
    try:
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lista_compras")
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao excluir todos os produtos: {err}")
        return
    carregar_produtos_new_db(treeview)
    calcular_valor_total_new_db(label_valor_total)

def carregar_produtos_new_db(treeview):
    try:
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM lista_compras")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # Limpa o Treeview
        for item in treeview.get_children():
            treeview.delete(item)
        # Insere os itens
        for row in rows:
            treeview.insert("", tk.END, values=(
                row["nome_peca"],
                row["nome_fornecedor"],
                row["quantidade"],
                f"{row['valor_unit']:.2f}",
                f"{row['valor_total']:.2f}"
            ))
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao carregar produtos: {err}")

def calcular_valor_total_new_db(label):
    try:
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(valor_total) FROM lista_compras")
        total = cursor.fetchone()[0]
        total = total if total is not None else 0.00
        cursor.close()
        conn.close()
        label.config(text=f"Valor Total: R${total:.2f}")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao calcular valor total: {err}")

def marcar_comprado_new_db(treeview, label_valor_total):
    """
    Transfere os itens do carrinho (lista_compras) para o estoque.
    """
    try:
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        # Cria uma lista dos itens do Treeview para evitar problemas ao deletar durante a iteração
        items = list(treeview.get_children())
        for item in items:
            values = treeview.item(item, "values")
            nome_peca = values[0]
            fornecedor = values[1]
            quantidade = int(values[2])
            valor_unit = float(values[3])
            valor_total = float(values[4])
            
            # Verifica se o produto já existe na tabela estoque
            cursor.execute("SELECT quantidade FROM estoque WHERE nome_peca = %s", (nome_peca,))
            row = cursor.fetchone()
            if row:
                nova_quantidade = row[0] + quantidade
                novo_valor_total = valor_unit * nova_quantidade
                cursor.execute(
                    "UPDATE estoque SET quantidade = %s, valor_total = %s WHERE nome_peca = %s", 
                    (nova_quantidade, novo_valor_total, nome_peca)
                )
            else:
                cursor.execute(
                    "INSERT INTO estoque (nome_peca, nome_fornecedor, quantidade, valor_unit, valor_total) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (nome_peca, fornecedor, quantidade, valor_unit, valor_total)
                )
            # Remove o produto da tabela lista_compras
            cursor.execute("DELETE FROM lista_compras WHERE nome_peca = %s", (nome_peca,))
            # Remove o item do Treeview
            treeview.delete(item)
        conn.commit()
        cursor.close()
        conn.close()
        calcular_valor_total_new_db(label_valor_total)
        messagebox.showinfo("Sucesso", "Itens marcados como comprados e transferidos para o estoque.")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao marcar itens como comprados: {err}")

def carrinhoDeCompras():
    aba = Toplevel()
    aba.title("Carrinho de Compras")
    aba.geometry("930x450")

    # Campos de entrada para adicionar item ao carrinho
    Label(aba, text="Nome da peça:", background="#dde", foreground="#009", anchor=W)\
        .grid(row=0, column=0, padx=10, pady=5, sticky="w")
    vnomeDaPeca = Entry(aba)
    vnomeDaPeca.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    
    Label(aba, text="Quantidade:", background="#dde", foreground="#009", anchor=W)\
        .grid(row=0, column=2, padx=10, pady=5, sticky="w")
    vquantidade = Entry(aba)
    vquantidade.grid(row=0, column=3, padx=10, pady=5, sticky="w")
    
    Label(aba, text="Valor Unitário:", background="#dde", foreground="#009", anchor=W)\
        .grid(row=1, column=0, padx=10, pady=5, sticky="w")
    vunitario = Entry(aba)
    vunitario.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    
    Label(aba, text="Nome do fornecedor:", background="#dde", foreground="#009", anchor=W)\
        .grid(row=1, column=2, padx=10, pady=5, sticky="w")
    vsupplier = Entry(aba)
    vsupplier.grid(row=1, column=3, padx=10, pady=5, sticky="w")
    
    # Label para o valor total
    label_valor_total = Label(aba, text="Valor Total: R$0.00", background="#dde", foreground="#009", anchor=W)
    label_valor_total.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")
    
    # Treeview para exibir os itens do carrinho
    colunas_new = ("Nome da Peça", "Fornecedor", "Quantidade", "Valor Unitário", "Valor Total")
    treeview_new = ttk.Treeview(aba, columns=colunas_new, show="headings")
    treeview_new.grid(row=2, column=0, columnspan=6, padx=10, pady=5, sticky="nsew")
    treeview_new.heading("Nome da Peça", text="Nome da Peça")
    treeview_new.heading("Fornecedor", text="Fornecedor")
    treeview_new.heading("Quantidade", text="Quantidade")
    treeview_new.heading("Valor Unitário", text="Valor Unitário")
    treeview_new.heading("Valor Total", text="Valor Total")
    treeview_new.column("Nome da Peça", width=200, anchor=W)
    treeview_new.column("Fornecedor", width=150, anchor=W)
    treeview_new.column("Quantidade", width=100, anchor="center")
    treeview_new.column("Valor Unitário", width=150, anchor="e")
    treeview_new.column("Valor Total", width=150, anchor="e")
    
    scrollbar_tree_new = ttk.Scrollbar(aba, orient="vertical", command=treeview_new.yview)
    treeview_new.configure(yscrollcommand=scrollbar_tree_new.set)
    scrollbar_tree_new.place(x=890, y=150, height=250)
    
    # Botões de ação
    Button(aba, text="Gravar", command=lambda: gravarDadosComQuant_db(
        vnomeDaPeca, vquantidade, vunitario, vsupplier, treeview_new, label_valor_total)
    ).grid(row=0, column=5, padx=10, pady=5)
    
    Button(aba, text="Deletar", command=lambda: excluir_produto_new_db(treeview_new, label_valor_total)
    ).grid(row=1, column=5, padx=10, pady=5)
    
    Button(aba, text="Excluir Tudo", command=lambda: excluir_tudo_new_db(treeview_new, label_valor_total)
    ).grid(row=0, column=7, padx=10, pady=5)
    
    Button(aba, text="Comprado", command=lambda: marcar_comprado_new_db(treeview_new, label_valor_total)
    ).grid(row=1, column=7, padx=10, pady=5)
    
    carregar_produtos_new_db(treeview_new)
    calcular_valor_total_new_db(label_valor_total)
    
    aba.mainloop()

# ---------------------------
# Funções para o Estoque (Tabela estoque)
# ---------------------------
def carregar_estoque_db():
    """
    Consulta a tabela 'estoque' e retorna um dicionário indexado pelo nome da peça.
    Cada registro conterá: Quantidade, Valor Unitário, Valor Total e Nome do fornecedor.
    """
    estoque = {}
    conn = get_db_connection()
    if conn is None:
        return estoque
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM estoque")
        rows = cursor.fetchall()
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
    finally:
        cursor.close()
        conn.close()
    return estoque

def salvar_estoque_db(estoque):
    """
    Atualiza o estoque na tabela 'estoque' conforme os valores do dicionário 'estoque'.
    Se algum produto tiver quantidade 0, ele pode ser removido.
    """
    conn = get_db_connection()
    if conn is None:
        return
    try:
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
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao salvar estoque: {err}")
    finally:
        cursor.close()
        conn.close()

def exibir_estoque_db():
    """
    Exibe todos os itens armazenados no estoque de forma formatada.
    """
    estoque = carregar_estoque_db()
    if not estoque:
        print("O estoque está vazio ou ocorreu um erro ao carregar.")
        return
    print("\nESTOQUE ATUAL:")
    print("-" * 60)
    for nome, detalhes in estoque.items():
        print(f"Peça: {nome}")
        print(f"  Quantidade: {detalhes['Quantidade']}")
        print(f"  Valor Unitário: R${detalhes['Valor Unitário']:.2f}")
        print(f"  Valor Total: R${detalhes['Valor Total']:.2f}")
        print(f"  Nome do Fornecedor: {detalhes['Nome do fornecedor']}")
        print("-" * 60)

# ---------------------------
# Execução Principal
# ---------------------------
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Aplicação de Compras e Estoque")
    Button(root, text="Abrir Carrinho de Compras", command=carrinhoDeCompras).pack(padx=10, pady=10)
    Button(root, text="Exibir Estoque no Console", command=exibir_estoque_db).pack(padx=10, pady=10)
    root.mainloop()
