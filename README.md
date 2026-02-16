# Imperial League

## Descripción
Una simulación de una compleja liga de fútbol utilizando Python. Permite simular partidos de división, partidos interdivisionales y una postemporada con desempates y penales, generando resultados en Excel con tablas finales y registros de partidos.

## Contenido del repositorio
- `imperial_league_simulation.py` : Código principal.
- `imperial_league_skills.csv` : Datos iniciales y modificables de los equipos, con habilidades de ataque (ATK) y defensa (DEF) y su división.
- `requirements.txt` : Liberías de Python necesarios.

## Características principales
- Simulación de partidos considerando ataque, defensa y ventaja de localía.
- Manejo de empates con desempates y penales.
- Postemporada con ajuste de habilidades según el sembrado de cada equipo.
- Generación de resultados finales en Excel:
  - Tabla general de la liga
  - Tablas por división
  - Registro completo de partidos
  - Resultados de la postemporada
- Código modular y estructurado para fácil reutilización y extensión.

## Dependencias
Para instalar los requerimientos, ejecutar:

```bash
pip install -r requirements.txt
```

## Cómo ejecutar la simulación
1. Asegúrate de tener imperial_league_skills.csv en la misma carpeta que el script.
2. Ejecuta el script principal:
```bash
python imperial_league_simulation.py
```
3. Al finalizar, se generará un archivo imperial_league_results.xlsx.

## Autor
Javier M.
