# Progetto Elettronica di Potenza: Convertitore ZVZCS Full-Bridge DC/DC per Veicoli Elettrici

Replica e validazione del convertitore DC/DC a ponte intero con commutazione dolce ZVZCS (*Zero-Voltage and Zero-Current Switching*) per caricabatterie di bordo (*on-board EV chargers*), basato sull'articolo scientifico IEEE Transactions on Power Electronics:

> **"A Novel ZVZCS Full-Bridge DC/DC Converter Used for Electric Vehicles"**  
> *M. Pahlevaninezhad, P. Das, J. Drobnik, P. K. Jain, A. Bakhshai*  
> IEEE Transactions on Power Electronics, Vol. 27, No. 6, pp. 2752–2769, Giugno 2012.

---

## 📌 Indice dei Contenuti
- [Panoramica del Progetto](#panoramica-del-progetto)
- [Specifiche Tecniche del Convertitore](#specifiche-tecniche-del-convertitore)
- [Struttura della Repository](#struttura-della-repository)
- [Documentazione e Presentazioni](#documentazione-e-presentazioni)
- [Modelli e Simulazioni LTspice](#modelli-e-simulazioni-ltspice)
- [Script Python e Pipeline di Simulazione](#script-python-e-pipeline-di-simulazione)
- [Confronto Risultati Sperimentali vs LTspice](#confronto-risultati-sperimentali-vs-ltspice)
- [Istruzioni per l'Esecuzione](#istruzioni-per-lesecuzione)

---

## ⚡ Panoramica del Progetto

Il progetto analizza in dettaglio il secondo stadio isolato DC/DC del caricabatterie di bordo EV da **3 kW** alimentato dal bus DC PFC a **400 V** e che carica batterie con tensione compresa tra **235 V e 431 V**.

### Caratteristiche Principali:
- **Leading-Leg (S1, S2):** Condizioni di commutazione ZVS (*Zero Voltage Switching*) garantite su tutto il range di carico grazie all'energia immagazzinata nell'induttanza di dispersione $L_{lk}$.
- **Trailing-Leg (S3, S4):** Condizioni di commutazione ZCS (*Zero Current Switching*) ottenute azzerando la corrente primaria prima dell'apertura degli switch, grazie al circuito ausiliario innovativo con condensatore di reset $C_c$.
- **Circuito Ausiliario Ottimizzato:** Nessun dissipatore termico aggiuntivo, basse perdite di conduzione e assenza di spike di sovratensione sui diodi del raddrizzatore secondario.
- **Frequenza di commutazione elevata:** $f_s = 220\text{ kHz}$.

---

## 📊 Specifiche Tecniche del Convertitore

| Parametro | Simbolo | Valore Nominale |
| :--- | :---: | :---: |
| Potenza di Uscita Nominale | $P_o$ | $3\text{ kW}$ |
| Tensione del Bus d'Ingresso | $V_{in} / V_{dc}$ | $400\text{ V}$ |
| Tensione di Uscita (Batteria) | $V_o$ | $235\text{ V} - 431\text{ V}$ (Nom. $350\text{ V}$) |
| Corrente Massima di Uscita | $I_o$ | $8.6\text{ A}$ |
| Frequenza di Commutazione | $f_s$ | $220\text{ kHz}$ |
| Rapporto Spire Trasformatore | $n = N_p / N_s$ | $12 : 14 \approx 0.857$ |
| Induttanza di Dispersione | $L_{lk}$ | $2.5\ \mu\text{H}$ |
| Condensatori Parassiti / Snubber Leading Leg | $C_1, C_2$ | $1.2\text{ nF}$ |
| Condensatori Snubber Trailing Leg | $C_3, C_4$ | $220\text{ pF}$ |
| Condensatore Ausiliario di Reset | $C_c$ | $60\text{ nF}$ |
| Condensatori di Blocco Secondario | $C_{b1}, C_{b2}$ | $200\text{ nF}$ |

---

## 📂 Struttura della Repository

```
progetto_elettronica_di_potenza/
├── Relazione_Completa_ZVZCS_FullBridge.md   # Relazione tecnica completa (markdown)
├── Relazione_Completa_ZVZCS_FullBridge.pdf  # Relazione tecnica impaginata e stampabile
├── Presentazione_Esame_ZVZCS_FullBridge.pdf # Slide di presentazione per l'esame
├── 35.pdf                                   # Articolo IEEE di riferimento (Pahlevaninezhad et al.)
├── Proposed_ZVZCS_FullBridge.asc            # Modello LTspice completo del convertitore proposto
├── Conventional_FullBridge_Comparison.asc   # Modello LTspice del convertitore convenzionale
│
├── circuiti_ltspice/                        # Banchi di test circuitali LTspice (.asc, .plt, .net, .log)
│   ├── Fig14a_Conventional_10pct_Load.asc
│   ├── Fig14b_Conventional_100pct_FullLoad.asc
│   ├── Fig15_Proposed_NoLoad_0W.asc
│   ├── Fig16_Proposed_10pct_Load_300W.asc
│   ├── Fig17_Proposed_25pct_Load_750W.asc
│   ├── Fig18_Proposed_50pct_Load_1500W.asc
│   ├── Fig19_Proposed_70pct_Load_2100W.asc
│   ├── Fig20_Proposed_85pct_Load_2550W.asc
│   ├── Fig21_Proposed_100pct_FullLoad_3000W.asc
│   ├── Fig22a_Proposed_AuxCurrent_LightLoad.asc
│   ├── Fig22b_Proposed_AuxCurrent_FullLoad.asc
│   └── measurements_summary.json
│
├── grafici_simulazioni/                     # Grafici comparativi Paper IEEE vs Replica LTspice
│   ├── Fig07_Converter_Voltage_Gain_Curves.png
│   ├── Fig08_Compare_Paper_vs_LTspice.png
│   ├── Fig10_Transformer_Leakage_Design.png
│   ├── Fig11_Compare_Paper_vs_LTspice.png
│   ├── Fig14_Compare_Paper_vs_LTspice.png
│   ├── Fig15_Compare_Paper_vs_LTspice.png
│   ├── Fig16_Compare_Paper_vs_LTspice.png
│   ├── Fig17_Compare_Paper_vs_LTspice.png
│   ├── Fig18_Compare_Paper_vs_LTspice.png
│   ├── Fig19_Compare_Paper_vs_LTspice.png
│   ├── Fig20_Compare_Paper_vs_LTspice.png
│   ├── Fig21_Compare_Paper_vs_LTspice.png
│   ├── Fig22_Compare_Paper_vs_LTspice.png
│   └── Fig23_Efficiency_Curves_LTspice.png
│
├── paper_figures/                           # Figure estratte ad alta risoluzione dal paper IEEE
│
└── script_python/                           # Pipeline di automazione e post-processing
    ├── 01_extract_paper_figures.py
    ├── 02_generate_and_run_ltspice_circuits.py
    ├── 03_generate_all_plots.py
    ├── 04_generate_pdfs.py
    ├── run_all_pipeline.py
    └── README_SCRIPT_PYTHON.md
```

---

## 📑 Documentazione e Presentazioni

- **[Relazione Tecnica Completa (Markdown)](Relazione_Completa_ZVZCS_FullBridge.md):** Analisi dettagliata di tutti i modi operativi (Modo 1-7), equazioni di progetto, dimensionamento del circuito ausiliario, formule di guadagno, perdite ed efficienza energetica, e domande tipiche d'esame orale.
- **[Relazione Completa (PDF)](Relazione_Completa_ZVZCS_FullBridge.pdf):** Documento formattato ad alta fedeltà pronto per la stampa/consultazione.
- **[Presentazione Esame (PDF)](Presentazione_Esame_ZVZCS_FullBridge.pdf):** Slide animate ed esplicative ideali per l'esposizione orale.

---

## 💻 Script Python e Pipeline di Simulazione

La cartella `script_python/` contiene una pipeline modulare eseguibile per riprodurre tutte le analisi e i grafici:

```bash
cd script_python
python run_all_pipeline.py
```

Gli script eseguono:
1. `01_extract_paper_figures.py`: Estrazione delle immagini dal PDF dell'articolo.
2. `02_generate_and_run_ltspice_circuits.py`: Generazione parametrica dei netlist e lancio automatico delle simulazioni batch in LTspice.
3. `03_generate_all_plots.py`: Estrazione dei file `.raw` e `.log` e rendering dei grafici di confronto con i dati sperimentali del paper.
4. `04_generate_pdfs.py`: Compilazione e generazione automatica dei documenti PDF di relazione e presentazione.

---

## 📈 Risultati Chiave Ottenuti

1. **ZVS su Leading-Leg (S1, S2):** Condizioni ZVS mantenute dal 10% al 100% di carico senza richiedere induttanze ausiliarie pesanti.
2. **ZCS su Trailing-Leg (S3, S4):** Corrente primaria azzerata con successo prima dell'interdizione di S3/S4, azzerando le perdite di turn-off tipiche dei MOSFET ad alta tensione / IGBT.
3. **Efficienza Massima Raggiunta:** $\eta > 97.4\%$ a carico nominale ($3\text{ kW}$), in perfetta concordanza con i rilievi sperimentali del prototipo fisico descritto nell'articolo IEEE.
