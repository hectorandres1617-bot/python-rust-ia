#!/bin/bash
# Corre las pruebas. Requisitos y preparación: ver ../README.md
cd "$(dirname "$0")"; PY=${PY:-$HOME/rust-lab/venv/bin/python}
$PY bench_00_producto_punto.py; echo; $PY bench_01_primos.py; echo; $PY bench_02_tokens.py; echo; $PY bench_03_datos.py; echo; ./bench_04_herramientas.sh
