# -*- coding: utf-8 -*-
"""
Master Script: Esegue l'intera pipeline del progetto in sequenza:
1. Estrazione figure originali da 35.pdf (01_extract_paper_figures.py)
2. Generazione dei 13 circuiti LTspice (.asc + .plt) e simulazione batch (02_generate_and_run_ltspice_circuits.py)
3. Lettura dei file binari .raw e generazione dei 28 grafici a 250 DPI (03_generate_all_plots.py)
4. Impaginazione PDF della Presentazione (22 slide 16:9) e della Relazione Tecnica (04_generate_pdfs.py)
"""
import os
import subprocess
import sys

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

scripts = [
    "script_python/01_extract_paper_figures.py",
    "script_python/02_generate_and_run_ltspice_circuits.py",
    "script_python/03_generate_all_plots.py",
    "script_python/04_generate_pdfs.py",
]

for sc in scripts:
    print("=" * 72)
    print(f"ESECUZIONE: {sc}")
    print("=" * 72)
    subprocess.run([sys.executable, sc], check=True)

print("\nPIPELINE COMPLETATA CON SUCCESSO!")
