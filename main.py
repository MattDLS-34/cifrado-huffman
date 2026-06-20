import tkinter as tk
from tkinter import messagebox, filedialog
import heapq
import json
import os

class Nodo:
    contador = 0
    def __init__(self, caracter, frecuencia, es_hoja=True):
        self.caracter = caracter
        self.frecuencia = frecuencia
        self.izq = None
        self.der = None
        self.es_hoja = es_hoja
        self.id = Nodo.contador
        Nodo.contador += 1
    def __lt__(self, otro):
        if self.frecuencia != otro.frecuencia:
            return self.frecuencia < otro.frecuencia
        if self.es_hoja != otro.es_hoja:
            return self.es_hoja 
        if self.es_hoja and otro.es_hoja:
            return self.caracter < otro.caracter
        return self.id < otro.id

frecuencias = {}
codigos = {}
texto_comprimido = ""
raiz = None

def contar(texto):
    frec = {}
    for letra in texto:
        if letra in frec:
            frec[letra] += 1
        else:
            frec[letra] = 1
    return frec

def crear_arbol(frecuencias):
    Nodo.contador = 0
    heap = []
    for letra in sorted(frecuencias.keys()):
        nodo = Nodo(letra, frecuencias[letra], es_hoja=True)
        heapq.heappush(heap, nodo)
    while len(heap) > 1:
        izq = heapq.heappop(heap)
        der = heapq.heappop(heap)
        nuevo = Nodo(None, izq.frecuencia + der.frecuencia, es_hoja=False)
        nuevo.izq = izq
        nuevo.der = der
        heapq.heappush(heap, nuevo)
    return heap[0]

def generar_codigos(nodo, codigo="", tabla=None):
    if tabla is None:
        tabla = {}
    if nodo:
        if nodo.caracter is not None:
            tabla[nodo.caracter] = codigo if codigo else "0"
        generar_codigos(nodo.izq, codigo + "0", tabla)
        generar_codigos(nodo.der, codigo + "1", tabla)
    return tabla

def arbol_a_dict(nodo):
    if nodo is None:
        return None
    return {
        "caracter": nodo.caracter,
        "frecuencia": nodo.frecuencia,
        "izq": arbol_a_dict(nodo.izq),
        "der": arbol_a_dict(nodo.der)
    }

def dict_a_arbol(d):
    if d is None:
        return None
    es_hoja = d["caracter"] is not None
    nodo = Nodo(d["caracter"], d["frecuencia"], es_hoja=es_hoja)
    nodo.izq = dict_a_arbol(d["izq"])
    nodo.der = dict_a_arbol(d["der"])
    return nodo

def descomprimir_con_arbol(codigo_binario, raiz_arbol):
    if raiz_arbol is None:
        return ""
    if raiz_arbol.izq is None and raiz_arbol.der is None:
        return raiz_arbol.caracter * len(codigo_binario)
    resultado = []
    nodo_actual = raiz_arbol
    for bit in codigo_binario:
        if bit == "0":
            nodo_actual = nodo_actual.izq
        else:
            nodo_actual = nodo_actual.der
        if nodo_actual.caracter is not None:
            resultado.append(nodo_actual.caracter)
            nodo_actual = raiz_arbol
    return "".join(resultado)

def procesar():
    global frecuencias, codigos, texto_comprimido, raiz
    texto = entrada.get()
    if texto == "":
        messagebox.showwarning("Aviso", "Ingrese un texto")
        return
    frecuencias = contar(texto)
    raiz = crear_arbol(frecuencias)
    codigos = generar_codigos(raiz)
    texto_comprimido = ""
    for letra in texto:
        texto_comprimido += codigos[letra]
    messagebox.showinfo("Correcto", "Datos generados correctamente")

def ventana_frecuencias():
    if frecuencias == {}:
        messagebox.showwarning("Aviso", "Primero procese el texto")
        return
    ventana2 = tk.Toplevel()
    ventana2.title("Frecuencias")
    ventana2.geometry("400x500")
    ventana2.config(bg="#eaf2ff")
    tk.Label(ventana2, text="FRECUENCIAS", font=("Arial", 13, "bold"),
             bg="#2563eb", fg="white", pady=8).pack(fill="x")
    texto = tk.Text(ventana2, font=("Consolas", 11), bg="white")
    texto.pack(fill="both", expand=True, padx=10, pady=10)
    texto.insert(tk.END, "===== FRECUENCIAS =====\n\n")
    for letra in sorted(frecuencias.keys()):
        texto.insert(tk.END, repr(letra) + " : " + str(frecuencias[letra]) + "\n")

def ventana_arbol():
    if raiz is None:
        messagebox.showwarning("Aviso", "Primero procese el texto")
        return
    ventana3 = tk.Toplevel()
    ventana3.title("Arbol de Huffman")
    ventana3.geometry("900x620")
    ventana3.config(bg="#eaf2ff")
    tk.Label(ventana3, text="ARBOL DE HUFFMAN", font=("Arial", 13, "bold"),
             bg="#2563eb", fg="white", pady=8).pack(fill="x")
    tk.Label(ventana3, text="Izquierda = 0     Derecha = 1     Nodos azules = caracteres",
             font=("Arial", 9), bg="#1d4ed8", fg="#bfdbfe", pady=4).pack(fill="x")
    frame_canvas = tk.Frame(ventana3, bg="#eaf2ff")
    frame_canvas.pack(fill="both", expand=True, padx=8, pady=8)
    posiciones = {}
    SEP_Y = 110
    hoja_actual = [0]
    def asignar_posiciones(nodo, nivel=0):
        if nodo is None:
            return 0
        if nodo.izq is None and nodo.der is None:
            x = hoja_actual[0] * 130 + 80
            y = nivel * SEP_Y + 70
            posiciones[id(nodo)] = (x, y)
            hoja_actual[0] += 1
            return x
        x_izq = asignar_posiciones(nodo.izq, nivel + 1)
        x_der = asignar_posiciones(nodo.der, nivel + 1)
        x = (x_izq + x_der) / 2
        y = nivel * SEP_Y + 70
        posiciones[id(nodo)] = (x, y)
        return x
    asignar_posiciones(raiz)
    canvas_w = max(x for x, y in posiciones.values()) + 150
    canvas_h = max(y for x, y in posiciones.values()) + 120
    sb_y = tk.Scrollbar(frame_canvas, orient="vertical")
    sb_x = tk.Scrollbar(frame_canvas, orient="horizontal")
    sb_y.pack(side="right", fill="y")
    sb_x.pack(side="bottom", fill="x")
    canvas = tk.Canvas(frame_canvas, bg="#1e1e2e",
                       scrollregion=(0, 0, max(canvas_w, 880), max(canvas_h, 540)),
                       yscrollcommand=sb_y.set, xscrollcommand=sb_x.set, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    sb_y.config(command=canvas.yview)
    sb_x.config(command=canvas.xview)
    def _scroll_y(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind("<MouseWheel>", _scroll_y)
    R_HOJA = 26
    R_INTERNO = 20
    def dibujar(nodo):
        if nodo is None:
            return
        x, y = posiciones[id(nodo)]
        es_hoja = nodo.caracter is not None
        if nodo.izq:
            hx, hy = posiciones[id(nodo.izq)]
            canvas.create_line(x, y, hx, hy, fill="#60a5fa", width=2)
            mx = (x + hx) / 2
            my = (y + hy) / 2
            canvas.create_oval(mx-10, my-10, mx+10, my+10, fill="#1e1e2e", outline="#60a5fa", width=2)
            canvas.create_text(mx, my, text="0", font=("Consolas", 10, "bold"), fill="#60a5fa")
        if nodo.der:
            hx, hy = posiciones[id(nodo.der)]
            canvas.create_line(x, y, hx, hy, fill="#f472b6", width=2)
            mx = (x + hx) / 2
            my = (y + hy) / 2
            canvas.create_oval(mx-10, my-10, mx+10, my+10, fill="#1e1e2e", outline="#f472b6", width=2)
            canvas.create_text(mx, my, text="1", font=("Consolas", 10, "bold"), fill="#f472b6")
        r = R_HOJA if es_hoja else R_INTERNO
        fondo = "#2563eb" if es_hoja else "#334155"
        borde = "#93c5fd" if es_hoja else "#64748b"
        canvas.create_oval(x-r, y-r, x+r, y+r, fill=fondo, outline=borde, width=2)
        if es_hoja:
            etiqueta = "esp" if nodo.caracter == " " else nodo.caracter
            canvas.create_text(x, y - 7, text=etiqueta, font=("Consolas", 12, "bold"), fill="white")
            canvas.create_text(x, y + 9, text=str(nodo.frecuencia), font=("Consolas", 9), fill="#93c5fd")
        else:
            canvas.create_text(x, y, text=str(nodo.frecuencia), font=("Consolas", 11, "bold"), fill="#e2e8f0")
        dibujar(nodo.izq)
        dibujar(nodo.der)
    dibujar(raiz)
    leyenda = tk.Frame(ventana3, bg="#eaf2ff")
    leyenda.pack(fill="x", padx=10, pady=(0, 6))
    tk.Label(leyenda,
             text="Nodo azul = caracter     Nodo gris = nodo interno     Linea azul = 0 (izq)     Linea rosa = 1 (der)",
             font=("Arial", 8), bg="#eaf2ff", fg="#374151").pack()

def ventana_codigos():
    if codigos == {}:
        messagebox.showwarning("Aviso", "Primero procese el texto")
        return
    ventana4 = tk.Toplevel()
    ventana4.title("Codigos Huffman")
    ventana4.geometry("400x500")
    ventana4.config(bg="#eaf2ff")
    tk.Label(ventana4, text="CODIGOS HUFFMAN", font=("Arial", 13, "bold"),
             bg="#2563eb", fg="white", pady=8).pack(fill="x")
    texto = tk.Text(ventana4, font=("Consolas", 11), bg="white")
    texto.pack(fill="both", expand=True, padx=10, pady=10)
    texto.insert(tk.END, "===== CODIGOS =====\n\n")
    for letra in sorted(codigos.keys()):
        texto.insert(tk.END, repr(letra) + " = " + codigos[letra] + "\n")

def ventana_compresion():
    if texto_comprimido == "":
        messagebox.showwarning("Aviso", "Primero procese el texto")
        return
    ventana5 = tk.Toplevel()
    ventana5.title("Compresion")
    ventana5.geometry("700x500")
    ventana5.config(bg="#eaf2ff")
    tk.Label(ventana5, text="COMPRESION", font=("Arial", 13, "bold"),
             bg="#2563eb", fg="white", pady=8).pack(fill="x")
    texto = tk.Text(ventana5, font=("Consolas", 10), bg="white")
    texto.pack(fill="both", expand=True, padx=10, pady=10)
    texto.insert(tk.END, "===== COMPRESION =====\n\n")
    texto_original = entrada.get()
    for letra in texto_original:
        texto.insert(tk.END, repr(letra) + " -> " + codigos[letra] + "\n")
    texto.insert(tk.END, "\nResultado final:\n\n")
    texto.insert(tk.END, texto_comprimido)

def ventana_bits():
    if texto_comprimido == "":
        messagebox.showwarning("Aviso", "Primero procese el texto")
        return
    ventana6 = tk.Toplevel()
    ventana6.title("Comparacion de bits")
    ventana6.geometry("450x320")
    ventana6.config(bg="#eaf2ff")
    tk.Label(ventana6, text="COMPARACION DE BITS", font=("Arial", 13, "bold"),
             bg="#2563eb", fg="white", pady=8).pack(fill="x")
    texto = tk.Text(ventana6, font=("Consolas", 11), bg="white")
    texto.pack(fill="both", expand=True, padx=10, pady=10)
    texto_original = entrada.get()
    bits_normal = len(texto_original) * 8
    bits_huffman = len(texto_comprimido)
    ratio = (bits_huffman / bits_normal) * 100
    texto.insert(tk.END, "===== ASCII (8 bits por caracter) =====\n\n")
    texto.insert(tk.END, "{:<6} {:>5}  {:>6}  {}\n".format("Char", "Freq", "Bits/c", "Total"))
    texto.insert(tk.END, "-" * 34 + "\n")
    for char in sorted(set(texto_original)):
        freq = frecuencias[char]
        bits_char = freq * 8
        etiqueta = "esp" if char == " " else char
        texto.insert(tk.END, "{:<6} {:>5}  {:>6}  {} bits\n".format(etiqueta, freq, "8", str(bits_char)))
    texto.insert(tk.END, "-" * 34 + "\n")
    texto.insert(tk.END, "TOTAL ASCII : " + str(bits_normal) + " bits\n")
    texto.insert(tk.END, "\n===== HUFFMAN =====\n\n")
    texto.insert(tk.END, "{:<6} {:>5}  {:>6}  {}\n".format("Char", "Freq", "Bits/c", "Total"))
    texto.insert(tk.END, "-" * 34 + "\n")
    for char in sorted(set(texto_original)):
        freq = frecuencias[char]
        codigo = codigos[char]
        bits_char = freq * len(codigo)
        etiqueta = "esp" if char == " " else char
        texto.insert(tk.END, "{:<6} {:>5}  {:>6}  {} bits\n".format(etiqueta, freq, len(codigo), str(bits_char)))
    texto.insert(tk.END, "-" * 34 + "\n")
    texto.insert(tk.END, "TOTAL Huffman: " + str(bits_huffman) + " bits\n")
    texto.insert(tk.END, "\n===== REDUCCION =====\n\n")
    texto.insert(tk.END, "Reduccion = Huffman / ASCII x 100\n")
    texto.insert(tk.END, "Reduccion = " + str(bits_huffman) + " / " + str(bits_normal) + " x 100\n")
    texto.insert(tk.END, "Reduccion = " + "{:.2f}".format(ratio) + "%")

def exportar_todo():
    if raiz is None or texto_comprimido == "":
        messagebox.showwarning("Aviso", "Primero procese el texto")
        return

    carpeta = filedialog.askdirectory(title="Seleccionar carpeta de destino")
    if not carpeta:
        return

    nombre_carpeta = "huffman_comprimido"
    destino = os.path.join(carpeta, nombre_carpeta)
    os.makedirs(destino, exist_ok=True)

    ruta_arbol = os.path.join(destino, "arbol.json")
    datos = {
        "arbol": arbol_a_dict(raiz),
        "codigos": codigos
    }
    with open(ruta_arbol, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    ruta_codigo = os.path.join(destino, "codigo.txt")
    with open(ruta_codigo, "w", encoding="utf-8") as f:
        f.write(texto_comprimido)

    messagebox.showinfo(
        "Exportado",
        "Carpeta guardada en:\n" + destino +
        "\n\nArchivos:\n  • arbol.json\n  • codigo.txt"
    )

def ventana_descompresion():
    ventana7 = tk.Toplevel()
    ventana7.title("Descompresion")
    ventana7.geometry("700x420")
    ventana7.config(bg="#eaf2ff")
    tk.Label(ventana7, text="DESCOMPRESION", font=("Arial", 13, "bold"),
             bg="#2563eb", fg="white", pady=8).pack(fill="x")

    cuerpo = tk.Frame(ventana7, bg="#eaf2ff")
    cuerpo.pack(fill="both", expand=True, padx=20, pady=15)

    estado = {"raiz": None, "codigo": ""}
    var_estado = tk.StringVar(value="Sin carpeta cargada")

    tk.Label(cuerpo, text="1. Seleccionar carpeta exportada (huffman_comprimido)",
             font=("Arial", 10, "bold"), bg="#eaf2ff").pack(anchor="w")

    frame1 = tk.Frame(cuerpo, bg="#eaf2ff")
    frame1.pack(fill="x", pady=(4, 14))

    lbl_estado = tk.Label(frame1, textvariable=var_estado,
                          font=("Consolas", 9), bg="#eaf2ff", fg="#374151")
    lbl_estado.pack(side="left", expand=True, fill="x")

    def cargar_carpeta():
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta huffman_comprimido")
        if not carpeta:
            return

        ruta_arbol  = os.path.join(carpeta, "arbol.json")
        ruta_codigo = os.path.join(carpeta, "codigo.txt")

        faltantes = []
        if not os.path.exists(ruta_arbol):
            faltantes.append("arbol.json")
        if not os.path.exists(ruta_codigo):
            faltantes.append("codigo.txt")
        if faltantes:
            messagebox.showerror(
                "Error",
                "No se encontraron estos archivos en la carpeta:\n  • " + "\n  • ".join(faltantes)
            )
            return

        try:
            with open(ruta_arbol, "r", encoding="utf-8") as f:
                datos = json.load(f)
            estado["raiz"] = dict_a_arbol(datos["arbol"])

            with open(ruta_codigo, "r", encoding="utf-8") as f:
                estado["codigo"] = f.read().strip()

            var_estado.set("✓ Cargado: " + carpeta)
            lbl_estado.config(fg="#16a34a")
        except Exception as e:
            messagebox.showerror("Error", "No se pudo leer la carpeta:\n" + str(e))

    tk.Button(frame1, text="Cargar carpeta", bg="#2563eb", fg="white",
              font=("Arial", 10, "bold"), command=cargar_carpeta).pack(side="right")

    tk.Label(cuerpo, text="2. Texto recuperado",
             font=("Arial", 10, "bold"), bg="#eaf2ff").pack(anchor="w")

    resultado = tk.Text(cuerpo, font=("Consolas", 11), height=5, bg="white", state="disabled")
    resultado.pack(fill="x", pady=(4, 14))

    def hacer_descompresion():
        if estado["raiz"] is None:
            messagebox.showwarning("Aviso", "Primero carga la carpeta")
            return
        codigo = estado["codigo"]
        if not codigo:
            messagebox.showwarning("Aviso", "El archivo codigo.txt está vacío")
            return
        if not all(c in "01" for c in codigo):
            messagebox.showerror("Error", "El codigo.txt contiene caracteres inválidos (solo debe tener 0s y 1s)")
            return
        try:
            recuperado = descomprimir_con_arbol(codigo, estado["raiz"])
            resultado.config(state="normal")
            resultado.delete(1.0, tk.END)
            resultado.insert(tk.END, recuperado)
            resultado.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", "Error al descomprimir:\n" + str(e))

    tk.Button(cuerpo, text="Descomprimir", bg="#7c3aed", fg="white",
              font=("Arial", 10, "bold"), command=hacer_descompresion).pack(anchor="w")

def limpiar():
    global frecuencias, codigos, texto_comprimido, raiz
    frecuencias = {}
    codigos = {}
    texto_comprimido = ""
    raiz = None
    entrada.delete(0, tk.END)

#PP
ventana = tk.Tk()
ventana.title("Compresor Huffman")
ventana.geometry("900x450")
ventana.config(bg="#eaf2ff")

tk.Label(ventana, text="COMPRESOR DE TEXTO - HUFFMAN",
         font=("Arial", 20, "bold"), bg="#2563eb", fg="white", pady=12).pack(fill="x")

frame = tk.Frame(ventana, bg="#eaf2ff")
frame.pack(pady=40)

tk.Label(frame, text="Ingrese un texto para comprimir",
         font=("Arial", 13, "bold"), bg="#eaf2ff").pack()

entrada = tk.Entry(frame, width=50, font=("Arial", 13))
entrada.pack(pady=15)

frame_botones = tk.Frame(frame, bg="#eaf2ff")
frame_botones.pack(pady=10)

botones = [
    ("Procesar",        "#2563eb", procesar,             0, 0),
    ("Frecuencias",     "#2563eb", ventana_frecuencias,  0, 1),
    ("Arbol",           "#2563eb", ventana_arbol,        0, 2),
    ("Codigos",         "#2563eb", ventana_codigos,      1, 0),
    ("Compresion",      "#2563eb", ventana_compresion,   1, 1),
    ("Bits",            "#2563eb", ventana_bits,         1, 2),
    ("Exportar todo",   "#16a34a", exportar_todo,        2, 0),
    ("Descomprimir",    "#7c3aed", ventana_descompresion,2, 1),
    ("Limpiar",         "#dc2626", limpiar,              2, 2),
]

for texto_btn, color, cmd, fila, col in botones:
    tk.Button(frame_botones, text=texto_btn, width=15, bg=color, fg="white",
              font=("Arial", 10, "bold"), command=cmd
              ).grid(row=fila, column=col, padx=5, pady=5)

tk.Label(ventana, text="El programa permite visualizar cada etapa del algoritmo Huffman.",
         bg="#eaf2ff", font=("Arial", 10)).pack()

ventana.mainloop()
