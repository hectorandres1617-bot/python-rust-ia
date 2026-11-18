"""Prueba 1 · bucle de CPU: contar primos < N en Python puro vs Rust (PyO3). Requiere el módulo `rapido` (ver ../lib.rs y README)."""
from comun import *
import rapido
def primos_py(n):
    c = 0
    for i in range(2, n):
        es = True; d = 2
        while d * d <= i:
            if i % d == 0: es = False; break
            d += 1
        if es: c += 1
    return c
N = 200_000
tp, rp = mejor(primos_py, N); tr, rr = mejor(rapido.contar_primos, N); assert rp == rr
print(f"PRUEBA 1 · contar primos < {N:,}\n  Python puro {tp*1000:9.1f} ms\n  Rust (PyO3) {tr*1000:9.1f} ms  -> {tp/tr:.0f}x más rápido")
guardar("01_primos", {"n": N, "resultado": rp, "python_ms": tp*1000, "rust_ms": tr*1000, "veces": tp/tr, "maquina": maquina()})
