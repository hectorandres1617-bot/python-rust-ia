use pyo3::prelude::*;

/// Producto punto de dos listas (a mano, como lo haría un bucle).
#[pyfunction]
fn producto_punto(a: Vec<f64>, b: Vec<f64>) -> f64 {
    a.iter().zip(b.iter()).map(|(x, y)| x * y).sum()
}

/// Cuenta cuántos números primos hay por debajo de n (tarea de CPU pura).
#[pyfunction]
fn contar_primos(n: u64) -> u64 {
    let mut c = 0;
    for i in 2..n {
        let mut es = true;
        let mut d = 2;
        while d * d <= i {
            if i % d == 0 { es = false; break; }
            d += 1;
        }
        if es { c += 1; }
    }
    c
}

#[pymodule]
fn rapido(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(producto_punto, m)?)?;
    m.add_function(wrap_pyfunction!(contar_primos, m)?)?;
    Ok(())
}
