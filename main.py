import tkinter as tk

def atualizar_codigo(*args):
    """Lê a grade atual e gera o código em MikroBasic."""
    linhas = []
    for r in range(8):
        # Transforma o estado booleano da linha em uma string binária (ex: "00011000")
        bits = "".join("1" if matriz[r][c].get() else "0" for c in range(8))
        linhas.append(f"%{bits}")

    nome_var = entrada_nome.get()
    if not nome_var.strip():
        nome_var = "NOVA_LETRA"

    # Monta a string final
    codigo = f"const {nome_var} as byte[8] = ({','.join(linhas)})"
    
    # Atualiza o campo de texto
    texto_saida.delete("1.0", tk.END)
    texto_saida.insert(tk.END, codigo)

def alternar_pixel(r, c):
    """Inverte o estado do botão clicado (Liga/Desliga)."""
    atual = matriz[r][c].get()
    matriz[r][c].set(not atual)
    
    # Muda a cor do botão: Vermelho para ligado, Branco para desligado
    botoes[r][c].config(bg="#ff3333" if not atual else "white")
    atualizar_codigo()

# Configuração da janela principal
root = tk.Tk()
root.title("Gerador de Matriz 8x8 - MikroBasic")
root.geometry("600x450")

# Variáveis que guardam o estado (0 ou 1) de cada LED
matriz = [[tk.BooleanVar(value=False) for _ in range(8)] for _ in range(8)]
botoes = []

# --- Interface ---
frame_topo = tk.Frame(root)
frame_topo.pack(pady=10)

tk.Label(frame_topo, text="Nome da Variável Constante:", font=("Arial", 12)).pack(side=tk.LEFT)
entrada_nome = tk.Entry(frame_topo, font=("Arial", 12))
entrada_nome.insert(0, "CUSTOM")
entrada_nome.pack(side=tk.LEFT, padx=10)
entrada_nome.bind("<KeyRelease>", atualizar_codigo)

frame_matriz = tk.Frame(root, bg="black", bd=2)
frame_matriz.pack(pady=10)

# Criando a grade de botões 8x8
for r in range(8):
    linha_botoes = []
    for c in range(8):
        btn = tk.Button(frame_matriz, width=4, height=2, bg="white", relief="flat",
                        command=lambda r=r, c=c: alternar_pixel(r, c))
        btn.grid(row=r, column=c, padx=1, pady=1)
        linha_botoes.append(btn)
    botoes.append(linha_botoes)

tk.Label(root, text="Código Gerado (Copie e cole no MikroBasic):", font=("Arial", 12)).pack()

texto_saida = tk.Text(root, height=3, width=70, font=("Courier", 10))
texto_saida.pack(pady=5)

# Gera o código inicial
atualizar_codigo()

# Inicia o loop do aplicativo
root.mainloop()