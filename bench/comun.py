import time, json, platform, subprocess, os
def mejor(f, *a, n=5, **k):
    """Corre f n veces y devuelve (mejor tiempo en segundos, resultado)."""
    t = []; r = None
    for _ in range(n):
        i = time.perf_counter(); r = f(*a, **k); t.append(time.perf_counter() - i)
    return min(t), r
def maquina():
    cpu = [l.split(":")[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")][0]
    return {"cpu": cpu, "hilos": os.cpu_count(), "python": platform.python_version(), "so": platform.platform()}
def guardar(nombre, datos):
    json.dump(datos, open(os.path.join(os.path.dirname(__file__), f"resultado_{nombre}.json"), "w"), indent=1, ensure_ascii=False)
