# AGENTS.md — proyecto facturas

- Python 3.11+, sin dependencias externas salvo pytest.
- Tests: `python -m pytest -q`. Ejecútalos siempre después de cambiar código.
- Importes en euros con 2 decimales y redondeo half-up (usa `decimal`, nunca `round()` sobre floats).
- No cambies los tests existentes para que pasen: arregla el código.
