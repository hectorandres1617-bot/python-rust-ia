"""Prueba 0 (extra) · compara la MISMA tarea en Python puro, Rust (llamado desde Python con PyO3) y NumPy. Mide el mejor de 5 intentos."""
import time, random, platform, numpy as np, rapido

def mejor(f, *a, n=5):
    t = []
    for _ in range(n):
        i = time.perf_counter(); r = f(*a); t.append(time.perf_counter() - i)
    return min(t), r

def primos_py(n):
    c = 0
    for i in range(2, n):
        es = True; d = 2
        while d * d <= i:
            if i % d == 0: es = False; break
            d += 1
        if es: c += 1
    return c

def punto_py(a, b):
    s = 0.0
    for x, y in zip(a, b): s += x * y
    return s

print("Python", platform.python_version(), "| NumPy", np.__version__)
N = 200_000
tp, rp = mejor(primos_py, N); tr, rr = mejor(rapido.contar_primos, N)
print(f"\nTAREA 1 · contar primos < {N:,}  (bucle de CPU)")
print(f"  Python puro : {tp*1000:9.1f} ms  -> {rp}")
print(f"  Rust (PyO3) : {tr*1000:9.1f} ms  -> {rr}   ({tp/tr:.0f}x más rápido)")
assert rp == rr

M = 2_000_000
a = [random.random() for _ in range(M)]; b = [random.random() for _ in range(M)]
na, nb = np.array(a), np.array(b)
t1, r1 = mejor(punto_py, a, b); t2, r2 = mejor(rapido.producto_punto, a, b); t3, r3 = mejor(np.dot, na, nb)
print(f"\nTAREA 2 · producto punto de {M:,} números (listas de Python)")
print(f"  Python puro        : {t1*1000:8.1f} ms")
print(f"  Rust (PyO3)        : {t2*1000:8.1f} ms   ({t1/t2:.1f}x vs Python; incluye copiar la lista a Rust)")
print(f"  NumPy (ya en array): {t3*1000:8.1f} ms   ({t1/t3:.0f}x vs Python)")
print(f"  mismos resultados: {abs(r1-r2)<1e-6 and abs(r1-r3)<1e-6}")
