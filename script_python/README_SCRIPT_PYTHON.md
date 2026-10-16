# Script Python del Progetto (`script_python/`)

Questa cartella contiene tutti gli script Python sviluppati e utilizzati per:
1. Estrarre le immagini dal paper IEEE `35.pdf`;
2. Generare programmaticamente tutti i **13 circuiti LTspice (`.asc`)** e i relativi file di configurazione delle tracce (`.plt`), eseguirli in modalità batch tramite `LTspice.exe -b` ed estrarre tutte le misure `.meas`;
3. Leggere direttamente i file binari `.raw` di LTspice e generare tutti i **28 grafici ad alta risoluzione (`250 DPI`)** e i confronti fianco-a-fianco Paper vs. LTspice nella cartella `grafici_simulazioni/`;
4. Generare i PDF finali della presentazione d'esame (`Presentazione_Esame_ZVZCS_FullBridge.pdf`) e della relazione tecnica (`Relazione_Completa_ZVZCS_FullBridge.pdf`).

## Elenco degli Script

| File | Descrizione |
| :--- | :--- |
| `01_extract_paper_figures.py` | Estrae tutte le 33 figure originali dal PDF `35.pdf` nella cartella `paper_figures/`. |
| `02_generate_and_run_ltspice_circuits.py` | Costruisce i 13 schemi elettrici LTspice (`.asc` + `.plt`) nella radice e in `circuiti_ltspice/`, avvia `LTspice.exe -b` su ciascuno e salva tutte le misure `.meas` in `circuiti_ltspice/measurements_summary.json`. |
| `03_generate_all_plots.py` | Legge i file `.raw` prodotti da LTspice e genera tutti i 28 grafici analitici, sperimentali e comparativi in `grafici_simulazioni/`. |
| `04_generate_pdfs.py` | Compila la presentazione d'esame 16:9 a 22 slide (`Presentazione_Esame_ZVZCS_FullBridge.pdf`) e la relazione tecnica in PDF (`Relazione_Completa_ZVZCS_FullBridge.pdf`). |
| `run_all_pipeline.py` | Script master che esegue in sequenza automatica tutti gli script `01` $\to$ `04`. |

## Come Eseguire gli Script

Dalla cartella principale del progetto (`progetto_elettronica_di_potenza`), puoi eseguire un singolo script oppure l'intera pipeline con:

```powershell
python script_python/run_all_pipeline.py
```
