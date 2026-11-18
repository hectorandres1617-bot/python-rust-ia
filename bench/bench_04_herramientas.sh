#!/bin/bash
# Prueba 4 · herramientas de Python escritas en Rust vs las clásicas: ruff vs flake8 (revisar código) y uv vs pip (instalar paquetes, con caché tibia).
cd "$(dirname "$0")"; V=$HOME/rust-lab/venv; SP=$V/lib/python3.12/site-packages; T=$(mktemp -d)
medir(){ local ini=$(date +%s.%N); "$@" >/dev/null 2>&1; echo "$(echo "$(date +%s.%N) - $ini" | bc -l)"; }
echo "PRUEBA 4 · herramientas"
CODIGO="$SP/transformers $SP/pandas"; N=$(find $CODIGO -name '*.py' | wc -l); L=$(find $CODIGO -name '*.py' | xargs cat | wc -l)
echo "  Código a revisar: $N archivos, $L líneas"
mejor3(){ local b=999; for i in 1 2 3; do local t=$(medir "$@"); b=$(echo "if ($t < $b) $t else $b" | bc -l); done; echo $b; }
RU1=$(RAYON_NUM_THREADS=1 mejor3 $V/bin/ruff check --no-cache --select F --isolated $CODIGO)
RUN=$(mejor3 $V/bin/ruff check --no-cache --select F --isolated $CODIGO)
FL1=$(medir $V/bin/flake8 -j 1 --isolated --select F $CODIGO)
FLN=$(medir $V/bin/flake8 -j $(nproc) --isolated --select F $CODIGO)
printf "  Revisar código, 1 núcleo   · flake8 %7.2f s · ruff %7.3f s -> ruff %.0fx\n" $FL1 $RU1 $(echo "$FL1 / $RU1" | bc -l)
printf "  Revisar código, %s núcleos · flake8 %7.2f s · ruff %7.3f s -> ruff %.1fx\n" $(nproc) $FLN $RUN $(echo "$FLN / $RUN" | bc -l)
echo "  (hallazgos: ruff $($V/bin/ruff check --no-cache --select F --isolated $CODIGO --statistics 2>/dev/null | awk '{s+=$1} END{print s+0}') · flake8 $($V/bin/flake8 -j $(nproc) --isolated --select F $CODIGO | wc -l))"
PAQ="numpy pandas polars requests"
python3 -m venv $T/vp; $T/vp/bin/pip install -q $PAQ >/dev/null 2>&1   # calienta la caché de pip
$V/bin/uv venv -q $T/vu; $V/bin/uv pip install -q --python $T/vu/bin/python $PAQ >/dev/null 2>&1   # calienta la caché de uv
rm -rf $T/vp $T/vu
python3 -m venv $T/vp; P1=$(medir $T/vp/bin/pip install -q $PAQ)
$V/bin/uv venv -q $T/vu; U1=$(medir $V/bin/uv pip install -q --python $T/vu/bin/python $PAQ)
$T/vp/bin/python -c "import numpy,pandas,polars,requests" && $T/vu/bin/python -c "import numpy,pandas,polars,requests" && echo "  (comprobado: los dos entornos importan numpy, pandas, polars y requests)"
printf "  Instalar %s (caché tibia) · pip %6.2f s · uv %6.2f s -> uv %.0fx\n" "$PAQ" $P1 $U1 $(echo "$P1 / $U1" | bc -l)
echo "{\"codigo_archivos\":$N,\"codigo_lineas\":$L,\"flake8_1nucleo_s\":$FL1,\"flake8_todos_s\":$FLN,\"ruff_1nucleo_s\":$RU1,\"ruff_todos_s\":$RUN,\"pip_s\":$P1,\"uv_s\":$U1}" > resultado_04_herramientas.json
rm -rf $T
