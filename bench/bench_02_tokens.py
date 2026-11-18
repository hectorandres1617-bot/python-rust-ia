"""Prueba 2 · tokenizar texto para un modelo de lenguaje (WordPiece de BERT): Python puro vs `tokenizers` de Hugging Face (núcleo en Rust).
Texto: prosa en inglés de documentación de paquetes instalados (el modelo BERT es en inglés). El Python puro es una implementación simple escrita aquí (greedy longest-match)."""
from comun import *
import glob, re, unicodedata, sys, os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from tokenizers import Tokenizer
base = os.path.expanduser("~/rust-lab")
# --- corpus
archivos = sorted(glob.glob(base + "/venv/lib/python3.12/site-packages/**/*.md", recursive=True) + glob.glob(base + "/venv/lib/python3.12/site-packages/**/*.rst", recursive=True))
texto = "\n".join(open(f, encoding="utf-8", errors="ignore").read() for f in archivos)
palabras = len(texto.split())
objetivo = 3_000_000  # palabras
while palabras < objetivo: texto += "\n" + texto; palabras *= 2
lineas = [l for l in texto.split("\n") if l.strip()]
tot = 0; sel = []
for l in lineas:
    sel.append(l); tot += len(l.split())
    if tot >= objetivo: break
corpus = sel; nbytes = sum(len(l.encode()) for l in corpus)
print(f"Corpus: {len(corpus):,} líneas, {tot:,} palabras, {nbytes/1e6:.1f} MB (de {len(archivos)} archivos de documentación)")
# --- Rust (tokenizers)
tk = Tokenizer.from_file(base + "/datos/tokenizer.json")
vocab = {l.rstrip("\n"): i for i, l in enumerate(open(base + "/datos/vocab.txt", encoding="utf-8"))}
# --- Python puro (BERT uncased: minúsculas, sin acentos, separar puntuación, WordPiece)
def limpiar(t):
    t = unicodedata.normalize("NFD", t.lower()); return "".join(c for c in t if unicodedata.category(c) != "Mn")
PAL = re.compile(r"[^\W_]+|[^\s\w]|_", re.UNICODE)   # palabras (sin _) | símbolo suelto | guion bajo (BERT lo separa)
def wordpiece(w):
    if len(w) > 100: return [vocab["[UNK]"]]
    out = []; i = 0
    while i < len(w):
        j = len(w); hallado = None
        while i < j:
            s = w[i:j] if i == 0 else "##" + w[i:j]
            if s in vocab: hallado = vocab[s]; break
            j -= 1
        if hallado is None: return [vocab["[UNK]"]]
        out.append(hallado); i = j
    return out
def tok_py(lineas):
    ids = 0
    for l in lineas:
        for w in PAL.findall(limpiar(l)): ids += len(wordpiece(w))
    return ids
def tok_rust_1hilo(lineas): return sum(len(e.ids) for e in tk.encode_batch(lineas, add_special_tokens=False))
# comprobar que coinciden en una muestra
muestra = corpus[:2000]
a = tok_py(muestra); b = tok_rust_1hilo(muestra)
print(f"Control de coincidencia (2.000 líneas): Python {a:,} tokens · Rust {b:,} tokens · diferencia {abs(a-b)/b*100:.2f}%")
# --- control de coincidencia línea por línea (muestra grande)
m2 = corpus[:20000]; iguales = sum(1 for l in m2 if tok_py([l]) == len(tk.encode(l, add_special_tokens=False).ids))
print(f"Control: {iguales/len(m2)*100:.1f}% de {len(m2):,} líneas dan exactamente el mismo número de tokens en ambos")
# --- medición
def rust_lote(c): return sum(len(e.ids) for e in tk.encode_batch(c, add_special_tokens=False))
def rust_rapido(c): return sum(len(e.ids) for e in tk.encode_batch_fast(c, add_special_tokens=False))   # modo rápido: sin posiciones de texto
t_py, n_py = mejor(tok_py, corpus, n=1)
t_r1, n_r1 = mejor(lambda c: sum(len(tk.encode(l, add_special_tokens=False).ids) for c_ in [c] for l in c_), corpus, n=2)   # una línea por llamada
os.environ["TOKENIZERS_PARALLELISM"] = "false"; t_rb1, n_rb1 = mejor(rust_lote, corpus, n=3)   # lote, 1 hilo
os.environ["TOKENIZERS_PARALLELISM"] = "true";  t_rn, n_rn = mejor(rust_lote, corpus, n=3)    # lote, todos los hilos
os.environ["TOKENIZERS_PARALLELISM"] = "false"; t_rf1, n_rf1 = mejor(rust_rapido, corpus, n=3)
os.environ["TOKENIZERS_PARALLELISM"] = "true";  t_rfn, n_rfn = mejor(rust_rapido, corpus, n=3)
print(f"PRUEBA 2 · tokenizar {tot:,} palabras ({nbytes/1e6:.1f} MB)")
for nom, t, n in (("Python puro (1 hilo)", t_py, n_py), ("Rust, 1 línea por llamada", t_r1, n_r1), ("Rust, en lote, 1 hilo", t_rb1, n_rb1), (f"Rust, en lote, {os.cpu_count()} hilos", t_rn, n_rn), ("Rust modo rápido, 1 hilo", t_rf1, n_rf1), (f"Rust modo rápido, {os.cpu_count()} hilos", t_rfn, n_rfn)):
    print(f"  {nom:30s} {t:7.2f} s  {nbytes/1e6/t:7.2f} MB/s  {t_py/t:5.1f}x  ({n:,} tokens)")
guardar("02_tokens", {"palabras": tot, "mb": nbytes/1e6, "coincidencia_pct": iguales/len(m2)*100, "python_s": t_py, "rust_1_por_llamada_s": t_r1, "rust_lote_1hilo_s": t_rb1, "rust_lote_todos_s": t_rn, "rust_rapido_1hilo_s": t_rf1, "rust_rapido_todos_s": t_rfn, "tokens_py": n_py, "tokens_rust": n_rn, "maquina": maquina()})
