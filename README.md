# Python y Rust en IA: pruebas de rendimiento (Automátika, 18-nov-2026)
Cuatro pruebas para ver DÓNDE ayuda Rust cuando se usa dentro de Python. No es «Python contra Rust»: es «Python + Rust».

## Preparar (Linux, Python 3.12, Rust instalado con rustup)
Los scripts esperan estar en `~/rust-lab` (cambia las rutas si usas otra carpeta).
```
git clone <este repositorio> ~/rust-lab && cd ~/rust-lab
python3 -m venv venv && ./venv/bin/pip install maturin numpy polars pandas tokenizers transformers huggingface_hub flake8 ruff uv
cd rapido && VIRTUAL_ENV=$PWD/../venv ../venv/bin/maturin develop --release && cd ..     # compila la función en Rust (rapido/src/lib.rs)
./venv/bin/python -c "from huggingface_hub import hf_hub_download as d; [d('bert-base-uncased', f, local_dir='datos') for f in ('vocab.txt','tokenizer.json')]"
bash bench/run_all.sh
```
`bench/bench_00_producto_punto.py` es la prueba extra del producto punto (Python / Rust / NumPy).

## Máquina de la prueba
AMD Ryzen Threadripper 7960X (24 núcleos, 48 hilos), 62 GB de RAM, Ubuntu 24.04, Python 3.12.3, rustc 1.88, pyo3 0.29, polars 2.1.0, pandas 3.1.1, tokenizers 0.23.3, ruff 0.17.5, uv 0.13.9, flake8 7.5.0. Sin GPU. Es UN solo computador: tus números cambiarán.

## Resultados (mejor de varios intentos)
| Prueba | Python / clásico | Rust | Resultado |
|---|---|---|---|
| 1 · contar primos < 200.000 (bucle de CPU) | 243 ms | 9,0 ms | Rust **27×** |
| 2 · tokenizar 3 M de palabras (20,6 MB), BERT, 1 hilo | 2,91 s (Python simple) | 5,7–7,2 s (`tokenizers`) | Python simple **ganó** 2× en 1 hilo |
| 2 · igual, con 48 hilos | 2,91 s | 1,13 s | `tokenizers` **2,6×** |
| 3 · leer CSV de 556 MB (10 M de filas) | pandas 0,594 s | Polars 0,134 s | Polars **4,4×** |
| 3 · agrupar y promediar (1000 grupos) | 0,090 s | 0,062 s | Polars 1,5× |
| 3 · filtrar + ordenar | 0,158 s | 0,041 s | Polars 3,8× |
| 3 · agrupar por texto (5000 clientes) | 0,549 s | 0,141 s | Polars 3,9× |
| 4 · revisar 1,9 M de líneas de código, 1 núcleo | flake8 92,0 s | ruff 0,93 s | ruff **99×** |
| 4 · igual, 48 núcleos | flake8 4,12 s | ruff 0,098 s | ruff **42×** |
| 4 · instalar numpy+pandas+polars+requests (caché tibia) | pip 5,90 s | uv 0,04 s | uv **147×** |
Además (prueba aparte): producto punto de 2 M de números: Python 50,9 ms · Rust desde Python 37,8 ms · **NumPy 3,0 ms** (ganó NumPy, que está escrito en C).

## Cómo leerlo (honestamente)
- Rust brilla en bucles pesados y cuando se puede paralelizar (primos, Polars, ruff, uv).
- Rust NO siempre gana: en la prueba 2 mi tokenizador simple de Python (usa `re`, `unicodedata` y diccionarios, que ya son C) le ganó a `tokenizers` en un hilo, pero `tokenizers` devuelve mucho más (posiciones del texto, tokens especiales, etc.) y gana con varios hilos. Ambos coinciden en el 100 % de 20.000 líneas.
- En la prueba 1, copiar datos entre Python y Rust cuesta: con listas grandes casi no hay ganancia, y NumPy gana.
- Prueba 4: ruff y flake8 no encuentran exactamente lo mismo (ruff 2.845 hallazgos, flake8 5.376 con reglas F) por diferencias en sus reglas por defecto; se compara trabajo parecido, no idéntico. La instalación con uv usa caché tibia (sin descargar); con red y caché fría la diferencia es menor.
- Texto de la prueba 2: documentación en inglés (BERT es inglés), repetida hasta 3 M de palabras. Datos de la prueba 3: sintéticos con semilla fija (42).
- No es un estudio científico: un solo equipo, pocas repeticiones, sin controlar el reloj de la CPU.

## Fuentes de los proyectos mencionados
github.com/huggingface/tokenizers · github.com/pola-rs/polars · github.com/astral-sh/ruff · github.com/astral-sh/uv · github.com/PyO3/pyo3

## Créditos
- Python y Rust son proyectos de código abierto (Python Software Foundation y Rust Foundation). Este proyecto no usa sus logos ni tiene patrocinio ni respaldo oficial.
- Sobre el tuit de Elon Musk de abril de 2023 («Rust», en respuesta a «AGI will be built with Python»): visto en el registro público del tuit mediante un buscador; no se pudo abrir el original.
- Cifras ajenas (Stack Overflow 2025, TIOBE nov-2026, GitHub Octoverse 2026, estrellas de GitHub) tomadas de sus páginas el 18-nov-2026.
- Licencia MIT para el código de este repositorio.
