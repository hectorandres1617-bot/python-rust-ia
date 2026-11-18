"""Prueba 3 · procesar datos tabulares: pandas (núcleo C/Cython/Arrow) vs Polars (núcleo Rust). Datos sintéticos con semilla fija."""
from comun import *
import numpy as np, pandas as pd, polars as pl, tempfile, os
rng = np.random.default_rng(42); N = 10_000_000
cat = rng.integers(0, 1000, N); x = rng.random(N); y = rng.normal(size=N); txt = np.array([f"cliente_{i%5000}" for i in range(N)])
df_pd = pd.DataFrame({"grupo": cat, "x": x, "y": y, "cliente": txt}); df_pl = pl.DataFrame({"grupo": cat, "x": x, "y": y, "cliente": txt})
ruta = os.path.join(tempfile.gettempdir(), "bench_datos.csv"); df_pd.to_csv(ruta, index=False); mb = os.path.getsize(ruta)/1e6
print(f"Datos: {N:,} filas · CSV de {mb:.0f} MB")
R = {}
def comparar(nombre, fp, fl, n=3):
    a, ra = mejor(fp, n=n); b, rb = mejor(fl, n=n); R[nombre] = {"pandas_s": a, "polars_s": b, "veces": a/b}
    print(f"  {nombre:34s} pandas {a:7.3f} s · Polars {b:7.3f} s  -> Polars {a/b:4.1f}x")
print("PRUEBA 3 · pandas vs Polars (mejor de 3)")
comparar("leer CSV", lambda: pd.read_csv(ruta), lambda: pl.read_csv(ruta))
comparar("agrupar y promediar (1000 grupos)", lambda: df_pd.groupby("grupo")[["x", "y"]].mean(), lambda: df_pl.group_by("grupo").agg(pl.col("x").mean(), pl.col("y").mean()))
comparar("filtrar + ordenar", lambda: df_pd[df_pd.x > 0.9].sort_values("y"), lambda: df_pl.filter(pl.col("x") > 0.9).sort("y"))
comparar("agrupar por texto (5000 clientes)", lambda: df_pd.groupby("cliente")["x"].sum(), lambda: df_pl.group_by("cliente").agg(pl.col("x").sum()))
os.remove(ruta); R["_meta"] = {"filas": N, "csv_mb": mb, "pandas": pd.__version__, "polars": pl.__version__, "maquina": maquina()}
guardar("03_datos", R)
