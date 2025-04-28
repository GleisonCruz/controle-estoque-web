import tkinter as tk
from tkinter import messagebox, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
from datetime import datetime
import os

# Caminho do arquivo de histórico
CAMINHO_HISTORICO = "historico_estoque.csv"

# Carregar dados existentes se houver
if os.path.exists(CAMINHO_HISTORICO):
    estoque = pd.read_csv(CAMINHO_HISTORICO)
else:
    estoque = pd.DataFrame(columns=["Descrição", "Quantidade", "Movimento", "Data", "Setor"])

def salvar_estoque():
    estoque.to_csv(CAMINHO_HISTORICO, index=False)

def registrar_movimento():
    global estoque
    descricao = entry_descricao.get()
    quantidade = entry_quantidade.get()
    movimento = var_movimento.get()
    setor = var_setor.get()
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if descricao and quantidade:
        try:
            quantidade = int(quantidade)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número inteiro")
            return

        novo_movimento = pd.DataFrame([[descricao, quantidade, movimento, data, setor]], columns=estoque.columns)
        estoque = pd.concat([estoque, novo_movimento], ignore_index=True)

        salvar_estoque()
        atualizar_tabela()
        messagebox.showinfo("Sucesso", f"{movimento} registrada com sucesso.")
        limpar_campos()
    else:
        messagebox.showerror("Erro", "Preencha todos os campos.")

def atualizar_tabela():
    for widget in tabela_frame.winfo_children():
        widget.destroy()

    for i, col in enumerate(estoque.columns):
        label = ttk.Label(tabela_frame, text=col, font=("Segoe UI", 10, "bold"))
        label.grid(row=0, column=i, padx=5, pady=5)

    for i, row in estoque.iterrows():
        for j, value in enumerate(row):
            label = ttk.Label(tabela_frame, text=value, font=("Segoe UI", 10))
            label.grid(row=i+1, column=j, padx=5, pady=2)

def gerar_relatorio():
    if estoque.empty:
        messagebox.showwarning("Aviso", "Sem dados para gerar o relatório.")
    else:
        estoque.to_excel("relatorio_estoque.xlsx", index=False)
        messagebox.showinfo("Sucesso", "Relatório gerado: relatorio_estoque.xlsx")

def excluir_produto():
    global estoque
    descricao = simpledialog.askstring("Excluir Produto", "Digite a descrição do produto para excluir:")

    if descricao:
        encontrados = estoque[estoque["Descrição"].str.lower() == descricao.lower()]

        if encontrados.empty:
            messagebox.showwarning("Aviso", "Produto não encontrado.")
            return

        confirm = messagebox.askyesno("Confirmação", f"Deseja realmente excluir {len(encontrados)} registro(s) com descrição '{descricao}'?")
        if confirm:
            estoque = estoque[estoque["Descrição"].str.lower() != descricao.lower()]
            salvar_estoque()
            atualizar_tabela()
            messagebox.showinfo("Sucesso", "Produto(s) excluído(s) com sucesso.")

def limpar_campos():
    entry_descricao.delete(0, tk.END)
    entry_quantidade.delete(0, tk.END)

# Janela principal (tela de sistema padrão)
root = ttk.Window(themename="darkly")
root.title("Controle de Estoque - Almoxarifado e Farmácia")
root.geometry("1000x700")  # Tamanho tradicional de sistema

# Centralizar a janela
root.update_idletasks()
largura = root.winfo_width()
altura = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (largura // 2)
y = (root.winfo_screenheight() // 2) - (altura // 2)
root.geometry(f"{largura}x{altura}+{x}+{y}")

# Frame Entrada
frame_entrada = ttk.Frame(root)
frame_entrada.pack(pady=10)

ttk.Label(frame_entrada, text="Descrição", font=("Segoe UI", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_descricao = ttk.Entry(frame_entrada, font=("Segoe UI", 12), width=40)
entry_descricao.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(frame_entrada, text="Quantidade", font=("Segoe UI", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_quantidade = ttk.Entry(frame_entrada, font=("Segoe UI", 12), width=20)
entry_quantidade.grid(row=1, column=1, padx=10, pady=5, sticky="w")

# Movimento
var_movimento = tk.StringVar(value="Entrada")
ttk.Label(frame_entrada, text="Movimento", font=("Segoe UI", 12)).grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
ttk.Radiobutton(frame_entrada, text="Entrada", variable=var_movimento, value="Entrada").grid(row=2, column=1, padx=10, sticky="w")
ttk.Radiobutton(frame_entrada, text="Saída", variable=var_movimento, value="Saída").grid(row=2, column=1, padx=100, sticky="w")

# Setor
var_setor = tk.StringVar(value="Almoxarifado")
ttk.Label(frame_entrada, text="Setor", font=("Segoe UI", 12)).grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")
ttk.Radiobutton(frame_entrada, text="📦 Almoxarifado", variable=var_setor, value="Almoxarifado").grid(row=3, column=1, padx=10, sticky="w")
ttk.Radiobutton(frame_entrada, text="💊 Farmácia", variable=var_setor, value="Farmácia").grid(row=3, column=1, padx=140, sticky="w")

# Botões com estilo
ttk.Button(root, text="✅ Registrar Movimento", bootstyle="success", command=registrar_movimento).pack(pady=10)
ttk.Button(root, text="📊 Gerar Relatório Excel", bootstyle="info", command=gerar_relatorio).pack(pady=5)
ttk.Button(root, text="❌ Excluir Produto", bootstyle="danger", command=excluir_produto).pack(pady=5)

# Tabela com Scroll
tabela_canvas = tk.Canvas(root, bg="#1e1e1e", highlightthickness=0)
scroll_y = ttk.Scrollbar(root, orient="vertical", command=tabela_canvas.yview)
tabela_canvas.configure(yscrollcommand=scroll_y.set)

tabela_frame = ttk.Frame(tabela_canvas)
tabela_canvas.create_window((0, 0), window=tabela_frame, anchor="nw")

def on_frame_configure(event):
    tabela_canvas.configure(scrollregion=tabela_canvas.bbox("all"))

# ROLAGEM COM SCROLL DO MOUSE
def _on_mousewheel(event):
    tabela_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

tabela_frame.bind("<Configure>", on_frame_configure)
tabela_canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows

tabela_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
scroll_y.pack(side="right", fill="y")

# Rodapé
ttk.Label(root, text="👨‍💻 Desenvolvedor: Gleison Cruz", font=("Segoe UI", 10)).pack(side="bottom", pady=10)

# Exibir dados na tabela
atualizar_tabela()

# Iniciar interface
root.mainloop()

from firebase_config import db
import pandas as pd

def carregar_df(usuario):
    # Acesse a coleção do Firestore com base no nome do usuário
    ref = db.collection(f'historico_{usuario}')
    
    # Obtém os documentos da coleção
    docs = ref.stream()
    
    # Lista para armazenar os dados
    dados = []
    
    # Converte os documentos para um formato de dicionário
    for doc in docs:
        dados.append(doc.to_dict())
    
    # Se houver dados, cria o DataFrame
    if dados:
        return pd.DataFrame(dados)
    else:
        return pd.DataFrame(columns=["Descrição", "Quantidade", "Movimento", "Data", "Setor"])
def salvar_df(usuario, df):
    # Acesse a coleção do Firestore do usuário
    ref = db.collection(f'historico_{usuario}')
    
    # Limpar os dados antigos (opcional, se quiser substituir os dados toda vez)
    ref.delete()

    # Adiciona os dados novos ao Firestore
    for _, row in df.iterrows():
        ref.add({
            "descricao": row['Descrição'],
            "quantidade": row['Quantidade'],
            "movimento": row['Movimento'],
            "data": row['Data'],
            "setor": row['Setor']
        })




