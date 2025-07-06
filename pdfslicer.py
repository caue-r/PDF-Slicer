import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
import gc

def dividir_pdf(pdf_path, destino_path, tamanho_max_mb):
    reader = PdfReader(pdf_path)
    num_paginas = len(reader.pages)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    tamanho_max_bytes = tamanho_max_mb * 1024 * 1024

    tamanho_pdf = os.path.getsize(pdf_path)
    tamanho_medio_pagina = tamanho_pdf // num_paginas
    paginas_por_parte = max(1, tamanho_max_bytes // max(tamanho_medio_pagina, 1))

    parte = 1
    pagina_atual = 0

    while pagina_atual < num_paginas:
        writer = PdfWriter()
        paginas_adicionadas = 0
        while paginas_adicionadas < paginas_por_parte and pagina_atual < num_paginas:
            writer.add_page(reader.pages[pagina_atual])
            paginas_adicionadas += 1
            pagina_atual += 1

        output_path = os.path.join(destino_path, f"{base_name}_parte{parte}.pdf")
        with open(output_path, 'wb') as f_out:
            writer.write(f_out)
        parte += 1

        del writer
        gc.collect()

    return parte - 1

def selecionar_pdf():
    path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if path:
        pdf_path_var.set(path)

def selecionar_destino():
    path = filedialog.askdirectory()
    if path:
        destino_path_var.set(path)

def iniciar_divisao():
    pdf_path = pdf_path_var.get()
    destino_path = destino_path_var.get()
    try:
        tamanho_max_mb = float(tamanho_var.get())
    except:
        messagebox.showerror("Erro", "Digite um tamanho válido (número).")
        return

    if not pdf_path or not destino_path:
        messagebox.showerror("Erro", "Selecione o PDF e a pasta de destino.")
        return

    try:
        partes = dividir_pdf(pdf_path, destino_path, tamanho_max_mb)
        messagebox.showinfo("Concluído", f"PDF dividido em {partes} parte(s)!")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("PDF Slicer")

    try:
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, "pdfslicericon.ico")
        else:
            icon_path = "pdfslicericon.ico"
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Não foi possível carregar o ícone: {e}")

    pdf_path_var = tk.StringVar()
    destino_path_var = tk.StringVar()
    tamanho_var = tk.StringVar(value="150")

    tk.Label(root, text="PDF de origem:").grid(row=0, column=0, sticky="w")
    tk.Entry(root, textvariable=pdf_path_var, width=50).grid(row=0, column=1)
    tk.Button(root, text="Selecionar PDF", command=selecionar_pdf).grid(row=0, column=2)

    tk.Label(root, text="Pasta de destino:").grid(row=1, column=0, sticky="w")
    tk.Entry(root, textvariable=destino_path_var, width=50).grid(row=1, column=1)
    tk.Button(root, text="Selecionar Pasta", command=selecionar_destino).grid(row=1, column=2)

    tk.Label(root, text="Tamanho máximo por parte (MB):").grid(row=2, column=0, sticky="w")
    tk.Entry(root, textvariable=tamanho_var, width=10).grid(row=2, column=1, sticky="w")

    tk.Button(root, text="Iniciar divisão", command=iniciar_divisao, bg="lightgreen").grid(row=3, column=1, pady=10)

    root.mainloop()
