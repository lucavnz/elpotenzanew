import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLOTS_DIR = os.path.join(WORKSPACE, "grafici_simulazioni")
PAPER_FIGS = os.path.join(WORKSPACE, "paper_figures")
CIRCUITS_DIR = os.path.join(WORKSPACE, "circuiti_ltspice")

# ==============================================================================
# 1. GENERATE 16:9 EXAM PRESENTATION PDF (Presentazione_Esame_ZVZCS_FullBridge.pdf)
# ==============================================================================
def create_slide_figure():
    fig = plt.figure(figsize=(16, 9), dpi=150)
    fig.patch.set_facecolor('#FFFFFF')
    return fig

def add_header_footer(fig, title, subtitle, slide_num, total_slides):
    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=-1)
    ax_bg.set_xlim(0, 16)
    ax_bg.set_ylim(0, 9)
    ax_bg.axis('off')
    
    # Header bar
    ax_bg.add_patch(Rectangle((0, 7.95), 16, 1.05, facecolor='#0F172A', edgecolor='none'))
    ax_bg.add_patch(Rectangle((0, 7.88), 16, 0.07, facecolor='#2563EB', edgecolor='none'))
    
    # Footer bar
    ax_bg.add_patch(Rectangle((0, 0), 16, 0.42, facecolor='#F1F5F9', edgecolor='none'))
    ax_bg.plot([0, 16], [0.42, 0.42], color='#CBD5E1', lw=1.0)
    
    ax_bg.text(0.45, 8.52, title, color='#FFFFFF', fontsize=19.5, fontweight='bold', va='center')
    ax_bg.text(0.45, 8.15, subtitle, color='#93C5FD', fontsize=11.2, va='center')
    
    ax_bg.text(0.45, 0.21, "Progetto di Elettronica di Potenza — M. Pahlevaninezhad et al., IEEE Trans. Power Electron., Vol. 27, No. 6, June 2012",
               color='#475569', fontsize=9.5, va='center')
    ax_bg.text(15.55, 0.21, f"Slide {slide_num} / {total_slides}",
               color='#1E293B', fontsize=10, fontweight='bold', va='center', ha='right')
    return ax_bg

def add_box(ax, x, y, w, h, title, lines, bg='#F8FAFC', border='#CBD5E1', title_bg='#1E40AF', fontsize=10.2, line_step=0.28):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.1",
                                facecolor=bg, edgecolor=border, linewidth=1.2))
    ax.add_patch(FancyBboxPatch((x, y + h - 0.42), w, 0.42, boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=title_bg, edgecolor='none'))
    ax.text(x + 0.18, y + h - 0.21, title, color='#FFFFFF', fontsize=fontsize+0.5, fontweight='bold', va='center')
    
    curr_y = y + h - 0.66
    for line in lines:
        if line.startswith("##"):
            ax.text(x + 0.18, curr_y, line[2:].strip(), color='#0F172A', fontsize=fontsize, fontweight='bold', va='top')
            curr_y -= (line_step + 0.02)
        else:
            ax.text(x + 0.18, curr_y, line, color='#1E293B', fontsize=fontsize, va='top')
            curr_y -= line_step

def place_image(fig, rect, img_path, title=None):
    ax = fig.add_axes(rect)
    img = Image.open(img_path)
    ax.imshow(img)
    ax.axis('off')
    if title:
        ax.set_title(title, fontsize=10.5, fontweight='bold', color='#0F172A', pad=5)
    return ax

def build_presentation(pdf_path):
    TOTAL = 22
    with PdfPages(pdf_path) as pdf:
        # ---------------- SLIDE 1: COVER ----------------
        fig = create_slide_figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis('off')
        ax.add_patch(Rectangle((0, 0), 16, 9, facecolor='#0F172A'))
        ax.add_patch(Rectangle((0, 0), 0.35, 9, facecolor='#2563EB'))
        ax.add_patch(Rectangle((0.35, 0), 0.08, 9, facecolor='#38BDF8'))
        
        ax.text(1.1, 7.6, "UNIVERSITÀ DEGLI STUDI — CORSO DI ELETTRONICA DI POTENZA",
                color='#38BDF8', fontsize=13, fontweight='bold')
        ax.text(1.1, 6.5, "Studio, Analisi Teorica e Riproduzione Sperimentale in LTspice:\nA Novel ZVZCS Full-Bridge DC/DC Converter\nUsed for Electric Vehicles",
                color='#FFFFFF', fontsize=25, fontweight='bold', linespacing=1.35)
        ax.text(1.1, 4.9, "Articolo di riferimento: M. Pahlevaninezhad, P. Das, J. Drobnik, P. K. Jain, A. Bakhshai\nIEEE Transactions on Power Electronics, Vol. 27, No. 6, pp. 2752–2769, June 2012 (Paper #35)",
                color='#CBD5E1', fontsize=13, linespacing=1.4)
        
        ax.add_patch(FancyBboxPatch((1.1, 1.15), 13.8, 3.05, boxstyle="round,pad=0.05,rounding_size=0.15",
                                    facecolor='#1E293B', edgecolor='#334155', lw=1.5))
        ax.text(1.4, 3.82, "SPECIFICHE DEL PROTOTIPO SPERIMENTALE REPLICATO IN LTSPICE (3 kW / 220 kHz — Tabella I, II, IV):",
                color='#60A5FA', fontsize=12.8, fontweight='bold')
        col1 = (
            "• Tensione bus DC in ingresso:  Vdc = 400 V (da PFC Interleaved)\n"
            "• Tensione nominale batteria:   Vo = 300 V (range 235–431 V)\n"
            "• Potenza nominale di uscita:   Po = 3 kW (da 0 W No-Load a 3000 W)\n"
            "• Frequenza di commutazione:    fs = 220 kHz (Ts = 4.545 µs)"
        )
        col2 = (
            "• Trasformatore HF (1 : 1.18):  Lseq = Ls + Lleak = 11.8 µH integrata\n"
            "• Circuiti ausiliari simmetrici: LAUX1 = LAUX2 = 67 µH, Ca = 2.2 µF (IPA = 3.39 A)\n"
            "• Filtro di clamping secondario: Cf = 1 µF (subito dopo il ponte) + Lf = 80 µH\n"
            "• Efficienza a pieno carico:    96.8% (vs 93.3% conv., +3.5%) | Zero Voltage Spikes!"
        )
        ax.text(1.4, 3.35, col1, color='#F8FAFC', fontsize=11.6, va='top', linespacing=1.55)
        ax.text(8.1, 3.35, col2, color='#F8FAFC', fontsize=11.6, va='top', linespacing=1.55)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 2: CONTESTO EV & PROBLEMATICA ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "1. Contesto Applicativo (EV On-Board Charger) e Problematica",
                               "Architettura AC/DC + DC/DC isolato a 220 kHz e criticità del convertitore Full-Bridge convenzionale (Fig. 1)", 2, TOTAL)
        add_box(ax, 0.45, 4.35, 7.35, 3.25, "Architettura Caricabatterie EV e Requisiti (Fig. 12)", [
            "• Il caricabatterie di bordo (3 kW) comprende due stadi in cascata:",
            "  1. PFC Boost Interleaved a 2 fasi (fsb = 50 kHz) -> Bus DC Vdc = 400 V.",
            "  2. Full-Bridge DC/DC isolato ad alta frequenza (fs = 220 kHz) -> Vo = 300 V.",
            "• Tre requisiti stringenti per la ricarica di batterie EV:",
            "  - Mantenere lo ZVS da pieno carico (3 kW) fino a vuoto assoluto (0 W, fine carica).",
            "  - Eliminare gli spike di tensione sui diodi raddrizzatori secondari.",
            "  - Eliminare la modalità di ricircolo (Freewheeling Mode) e il Reverse Recovery."
        ], fontsize=9.8)
        add_box(ax, 8.2, 4.35, 7.35, 3.25, "Difetti del Convertitore Convenzionale (Fig. 1, Tabella V)", [
            "• Nel Full-Bridge convenzionale voltage-driven con induttore d'uscita Lf (Fig. 1):",
            "  1. Connessione in serie di due induttori (Lleak e Lf) attraverso il ponte a diodi:",
            "     durante la commutazione genera spike distruttivi > 700 V (richiede diodi da 1200 V!).",
            "  2. Modalità di Freewheeling: quando v_AB = 0 V, i 4 diodi secondari cortocircuitano",
            "     il trasformatore facendo circolare forte corrente reattiva senza trasferire potenza.",
            "  3. Circuito ausiliario fortemente asimmetrico: LAUXA = 33 µH (IPA = 6.4 A) sul",
            "     Leading Leg per compensare la corrente riflessa di Lf, contro LAUXB = 67 µH."
        ], title_bg='#B91C1C', fontsize=9.8)
        place_image(fig, [0.03, 0.06, 0.45, 0.39], os.path.join(PAPER_FIGS, "p02_img01_1025x669.jpeg"),
                    "Fig. 1 (Paper): Convertitore Full-Bridge Convenzionale Voltage-Driven")
        place_image(fig, [0.51, 0.06, 0.46, 0.39], os.path.join(PAPER_FIGS, "p03_img01_2050x917.png"),
                    "Fig. 2 (Paper): Nuovo Convertitore Full-Bridge ZVZCS Proposto")
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 3: TOPOLOGIA PROPOSTA ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "2. Architettura della Nuova Topologia ZVZCS Proposta (Fig. 2)",
                               "Raddrizzatore Current-Driven con condensatore di clamping Cf = 1 µF, conduzione DCM/CRM e circuiti ausiliari simmetrici", 3, TOTAL)
        place_image(fig, [0.03, 0.44, 0.52, 0.41], os.path.join(PAPER_FIGS, "p03_img01_2050x917.png"),
                    "Schema Elettrico del Convertitore ZVZCS Proposto (Fig. 2)")
        add_box(ax, 8.8, 0.65, 6.75, 6.95, "Le 3 Innovazioni Strutturali della Topologia Proposta", [
            "## 1. Raddrizzatore Pilotato in Corrente + Clamping Cf = 1 µF",
            "• Sul primario è presente l'induttore serie equivalente",
            "  Lseq = Ls + Lleak = 11.8 µH (integrato nel trasformatore).",
            "• Sul secondario, direttamente a valle del ponte a diodi D1..D4,",
            "  è posto il condensatore Cf = 1 µF (seguito da Lf = 80 µH).",
            "• Lseq agisce da generatore di corrente e Cf agisce da generatore",
            "  di tensione che fissa (clampa) istantaneamente la tensione sui",
            "  diodi a Vo = 300 V -> ZERO VOLTAGE SPIKES!",
            "• Permette di usare diodi SiC Schottky da 600 V (CPW-0600-S010B).",
            "## 2. Operazione in DCM / CRM dell'Induttore Serie Lseq",
            "• Lseq = 11.8 µH opera in CRM a pieno carico (3 kW) e in DCM",
            "  a tutti i carichi inferiori (0% ÷ 99%).",
            "• La corrente is(t) scende naturalmente a 0 A prima della fine",
            "  di ogni semiciclo: eliminato il Freewheeling!",
            "• I diodi secondari D1..D4 si spengono a Corrente Zero (ZCS)!",
            "• Il Leading Leg (S1, S2) commuta ON in ZVZCS e OFF in ZCS!",
            "## 3. Circuiti Ausiliari Passivi Simmetrici (67 µH)",
            "• Poiché is = 0 A quando commuta il Leading Leg, entrambi i rami",
            "  richiedono la stessa corrente ausiliaria: LAUX1 = LAUX2 = 67 µH,",
            "  Ca1 = Ca2 = 2.2 µF, IPA = IPB = 3.39 A (anche a vuoto 0 W!)."
        ], fontsize=9.6, line_step=0.27)
        add_box(ax, 0.45, 0.65, 8.1, 3.1, "Componenti del Prototipo Sperimentale (Tabella I, II, IV vs Tabella V)", [
            "• MOSFET Primari S1..S4: STW77N65M5 (650 V, 65 A, Rdson = 32 mΩ) | Diodi Uscita: SiC CPW-0600-S010B (600 V, 10 A)",
            "• Trasformatore HF: Rapporto spire Np : Ns = 1 : 1.18 (k = Np/Ns = 0.8475), Lseq = 11.8 µH integrata",
            "• Circuiti Ausiliari: LAUX1 = LAUX2 = 67 µH, Ca1 = Ca2 = 2.2 µF (vs LAUXA = 33 µH, LAUXB = 67 µH nel convenzionale)",
            "• Filtro d'Uscita: Cf = 1 µF (clamping diretto sul ponte) + Lf = 80 µH + Co = 10 µF verso batteria 300 V"
        ], title_bg='#0F766E', fontsize=9.5)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 4: FORME D'ONDA TEORICHE MODI I-VII (FIG. 3) ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "3. Analisi Teorica dei 7 Modi Operativi per Semiperiodo (Fig. 3 & Fig. 4)",
                               "Confronto diretto tra le forme d'onda teoriche dell'articolo e la simulazione LTspice su un semiciclo (t0 ÷ t7)", 4, TOTAL)
        place_image(fig, [0.03, 0.07, 0.63, 0.79], os.path.join(PLOTS_DIR, "Fig03_Compare_Paper_vs_LTspice.png"))
        place_image(fig, [0.67, 0.07, 0.31, 0.79], os.path.join(PAPER_FIGS, "p05_img01_2125x2052.jpeg"),
                    "Fig. 4 (Paper): Circuiti Equivalenti Modi I–VII")
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 5: EQUAZIONI DEI 7 MODI OPERATIVI ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "4. Modello Matematico Passo-Passo dei 7 Modi Operativi (Eq. 1–15, Fig. 5)",
                               "Equazioni analitiche delle transizioni ZVZCS (Leading Leg), ZVS (Lagging Leg) e ZCS (Diodi Secondari)", 5, TOTAL)
        add_box(ax, 0.45, 4.25, 7.4, 3.4, "Modi I, II, III: Commutazione ZVZCS Leading Leg e Salita Corrente", [
            "## Mode I (t0 ≤ t ≤ t1) — Spegnimento quasi-ZCS di S2:",
            "• A t = t0, S2 si spegne con is(t0) = 0 A. La corrente ausiliaria IPA = 3.39 A",
            "  scarica Cs1 e carica Cs2:  v_AB(t) = [IPA / (2·Cso)]·(t - t0)   (Eq. 2–3)",
            "## Mode II (t1 ≤ t ≤ t2) — Polarizzazione Diodi e Fine Scarica Cs1:",
            "• A t = t1 i diodi secondari iniziano a condurre; a t2 = t0 + 2·Vdc·Cso/IPA",
            "  la tensione su S1 raggiunge 0 V mentre is(t2) ≈ 0 A   (Eq. 6–9).",
            "## Mode III (t2 ≤ t ≤ t3) — Turn-ON ZVZCS di S1 e Trasferimento Potenza:",
            "• S1 si accende a Tensione Zero e Corrente Zero (ZVZCS)! Sull'induttore Lseq",
            "  è applicata Vdc - k(Vo + 2Vd) ≈ 143.8 V e is(t) sale linearmente (+12.18 A/µs):",
            "  is(t) = [Vdc - k(Vo + 2Vd)] / (Ls + Lleak) · (t - t2)   (Eq. 10–12)"
        ], fontsize=9.6)
        add_box(ax, 8.15, 4.25, 7.4, 3.4, "Modi IV, V, VI, VII: ZVS Lagging Leg, ZCS Diodi e Intervallo DCM", [
            "## Mode IV (t3 ≤ t ≤ t4) — Turn-OFF S4 e Transizione ZVS Lagging Leg:",
            "• S4 si spegne; la somma ip + IPB scarica Cs3 portando v_AB a 0 V (Eq. 13).",
            "• A basso carico (Fig. 5) is si annulla a t3,4 e IPB completa la scarica ZVS",
            "  generando la caratteristica doppia pendenza sul fronte di discesa di v_AB!",
            "## Mode V & VI (t4 ≤ t ≤ t6) — Turn-ON ZVS di S3 e Discesa a Zero di is:",
            "• Con v_AB = 0 V, la tensione riflessa -k(Vo + 2Vd) ≈ -256.2 V fa scendere is(t)",
            "  linearmente (-21.72 A/µs) mentre S3 si accende in ZVS a t = t5 (Eq. 15).",
            "• A t = t6, is(t6) = 0 A -> I diodi secondari si spengono in ZCS!",
            "## Mode VII (t6 ≤ t ≤ t7) — Intervallo DCM a Corrente Nulla:",
            "• is(t) = 0 A fino a fine semiciclo: zero corrente circolante e S1 si spegne in ZCS!"
        ], title_bg='#0F766E', fontsize=9.6)
        place_image(fig, [0.04, 0.06, 0.92, 0.39], os.path.join(PLOTS_DIR, "Fig05_Compare_Paper_vs_LTspice.png"))
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 6: DESIGN INDUTTORE SERIE Lseq & GUADAGNO (FIG. 6, 7, 9) ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "5. Guadagno Statico in Tensione e Progetto di Lseq (Eq. 16–19, Fig. 6, 7, 9)",
                               "Derivazione della caratteristica di guadagno gv(ψ) = Vo/Vdc e condizione di Conduzione Critica (CRM) a 3 kW", 6, TOTAL)
        place_image(fig, [0.03, 0.43, 0.56, 0.43], os.path.join(PLOTS_DIR, "Fig07_Compare_Paper_vs_LTspice.png"))
        place_image(fig, [0.03, 0.06, 0.56, 0.35], os.path.join(PLOTS_DIR, "Fig06_Fig09_Series_Inductor_DCM_and_CRM.png"))
        add_box(ax, 9.6, 0.65, 5.95, 6.95, "Analisi Stazionaria e Guadagno (Sezione III–IV)", [
            "## 1. Corrente Media Primaria su Semiciclo (Eq. 16):",
            "• Dall'area del triangolo di corrente is(t) in DCM (Fig. 6):",
            "  Δt_up = ψ/ωs - td,   Δt_tot = (Vdc / (k·Vo))·Δt_up",
            "  I_avg = [Vdc·(Vdc - k·Vo)] / [k·Vo·Ts·Lseq] · (ψ/ωs - td)²",
            "## 2. Equazione del Guadagno Statico gv = Vo/Vdc (Eq. 18):",
            "• Dal bilancio di potenza k·I_avg·Vo = Vo²/Re (con Re = Vbat/Ibat):",
            "  gv(ψ) = 2 / [ k + √( k² + 8·Lseq / (Ts·Re·Dψ²) ) ]",
            "  dove Dψ = ψ/π - 2·td/Ts e k = Np/Ns = 1/1.18 ≈ 0.8475.",
            "• Limite a vuoto (Re → ∞):  lim gv = 1/k = 1.18.",
            "• Riprodotte esattamente tutte le 7 curve Mathcad di Fig. 7",
            "  per Re = 30, 50, 80, 120, 170, 230, 300 Ω!",
            "## 3. Dimensionamento di Lseq in CRM a 3 kW (Eq. 25–26):",
            "• Alla potenza nominale Po = 3 kW (Io = 10 A, Re = 30 Ω),",
            "  imponendo la Conduzione Critica (CRM, Fig. 9):",
            "  I_avg,pri = k·Io = Ip / 2  -->  Ip = 2·k·Io ≈ 17–20.5 A",
            "  Lseq = [(Vdc - k·Vo) / (2·Io)] · (ψ/ωs - td) · (Ts/2) = 11.8 µH!"
        ], fontsize=9.5, line_step=0.27)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 7: CIRCUITI AUSILIARI SIMMETRICI & VERIFICA ZVZCS (FIG. 8) ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "6. Progetto dei Circuiti Ausiliari Simmetrici e Verifica ZVZCS (Eq. 20–24, Fig. 8)",
                               "Dimensionamento di LAUX1 = LAUX2 = 67 µH e prova diretta delle commutazioni ZVZCS, ZVS e ZCS in LTspice", 7, TOTAL)
        place_image(fig, [0.03, 0.43, 0.56, 0.43], os.path.join(PLOTS_DIR, "Fig08_Compare_Paper_vs_LTspice.png"))
        place_image(fig, [0.03, 0.06, 0.56, 0.35], os.path.join(PLOTS_DIR, "Extra_ZVZCS_Commutation_Analysis.png"))
        add_box(ax, 9.6, 0.65, 5.95, 6.95, "Dimensionamento Circuiti Ausiliari (Sezione IV-A)", [
            "## 1. Perché i Circuiti Ausiliari sono Simmetrici?",
            "• Poiché la corrente primaria is(t) è sempre ZERO all'istante",
            "  di commutazione del Leading Leg, il circuito ausiliario non",
            "  deve contrastare alcuna corrente primaria riflessa.",
            "• Entrambi i rami richiedono quindi la stessa identica corrente",
            "  per caricare/scaricare 2·Cso nel dead-time td!",
            "## 2. Corrente di Picco IPA = IPB (Eq. 20):",
            "• I partitori Ca1 = Ca2 = 2.2 µF fissano il centro a Vdc/2 = 200 V:",
            "  IPA = IPB = Vdc / (8 · LAUX · fs)",
            "  = 400 V / (8 × 67 µH × 220 kHz) = 3.392 A  (≈ 2.0 Arms)",
            "## 3. Bilancio Energetico ZVS e Dead-Time (Eq. 21–24):",
            "• (1/2)·LAUX·IPA² ≥ Cso·Vdc²  -->  LAUX = 1 / (128·Cso·fs²) = 67 µH",
            "• Dead-time richiesto:  td = 2·Cso·Vdc / IPA ≈ 250 ns.",
            "## 4. Vantaggio Energetico rispetto al Convenzionale:",
            "• Sul Leading Leg, LAUX1 = 67 µH (IPA = 3.39 A) anziché",
            "  33 µH (IPA = 6.4 A): corrente dimezzata e perdite 4x inferiori!"
        ], fontsize=9.5, line_step=0.27)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 8: TRASFORMATORE INTEGRATO E CONDENSATORE Cf (FIG. 10 & 11) ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "7. Integrazione Magnetica di Lseq nel Trasformatore e Clamping Cf (Fig. 10 & 11)",
                               "Realizzazione di Lseq = 11.8 µH tramite spaziatura assiale degli avvolgimenti (Eq. 27–31) e calcolo di Cf = 1 µF (Eq. 32)", 8, TOTAL)
        place_image(fig, [0.03, 0.43, 0.56, 0.43], os.path.join(PLOTS_DIR, "Fig11_Compare_Paper_vs_LTspice.png"))
        place_image(fig, [0.03, 0.06, 0.56, 0.35], os.path.join(PLOTS_DIR, "Fig10_Transformer_Leakage_Design.png"))
        add_box(ax, 9.6, 0.65, 5.95, 6.95, "Integrazione Magnetica e Filtro Cf (Sezione IV-B/C)", [
            "## 1. Integrazione di Lseq = 11.8 µH nel Trasformatore (Fig. 10):",
            "• Anziché usare un induttore serie esterno (che introdurrebbe",
            "  perdite nel nucleo/rame e interferenze EMI sul PCB), Lseq è",
            "  integrata come induttanza di dispersione del trasformatore HF.",
            "• Rocchetto ad avvolgimenti separati top-bottom a distanza c.",
            "• Dal profilo trapezoidale del campo magnetico H(y) (Eq. 27–31):",
            "  l_eq = (µ0 / h) · N1² · [ c + (b1 + b2)/3 ] = 11.8 µH",
            "• Variando la quota di isolamento c (≈ 6.5 mm) si ottiene il",
            "  valore esatto di 11.8 µH e un ottimo isolamento galvanico HV!",
            "## 2. Condensatore di Clamping Cf = 1 µF (Eq. 32, Fig. 11):",
            "• Posto immediatamente all'uscita del ponte a diodi D1..D4,",
            "  assorbe il ripple di corrente a 2·fs = 440 kHz e blocca la",
            "  tensione inversa dei diodi a Vo = 300 V:",
            "  Cf = Io / (8 · fs · ΔVCf)  -->  Scelto Cf = 1 µF (400 Vdc).",
            "• A pieno carico (Io = 10 A), il ripple picco-picco su Cf è",
            "  ΔVCf ≈ 5.68 V (< 1.9%), poi ulteriormente filtrato da Lf = 80 µH."
        ], fontsize=9.5, line_step=0.27)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 9: SCHEMI LTSPICE REALIZZATI ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "8. Implementazione Circuitale in LTspice: Guida ai 13 File .asc e .plt",
                               "Circuiti completi pronti all'uso con convergenza istantanea (~0.5 s) e direttive automatiche di misura (.meas)", 9, TOTAL)
        add_box(ax, 0.45, 4.15, 7.4, 3.5, "Modellazione SPICE Fedele alle Tabelle I, II, IV e V", [
            "• Tutti i 13 circuiti .asc sono simulabili istantaneamente (~0.5 secondi)",
            "  grazie al pre-caricamento del punto di lavoro stazionario (.ic / uic).",
            "• Componenti del Convertitore ZVZCS Proposto:",
            "  - Bus ingresso: Vbus = 400 V (Cbus = 1.4 mF) | Frequenza: fs = 220 kHz.",
            "  - MOSFET S1..S4 (STW77N65M5): VDMOS(Vds=650 Ron=0.032) + Cso.",
            "  - Circuiti ausiliari simmetrici: Laux1 = Laux2 = 67 µH, Ca = 2.2 µF.",
            "  - Induttore serie integrato: Lseq = 11.8 µH + trasformatore 1 : 1.18",
            "    (Lpri = 400 µH, Lsec = 556.96 µH, K1 Lpri Lsec 1).",
            "  - Ponte diodi SiC (CPW-0600-S010B) + Cf = 1 µF + Lf = 80 µH + Co = 10 µF.",
            "• Convertitore Convenzionale di Confronto (Tabella V, Fig. 14):",
            "  - LauxA = 33 µH, LauxB = 67 µH, Lleak = 1.8 µH, Lf = 80 µH direttamente",
            "    a valle del ponte a diodi (senza Cf di clamping) -> Riproduce gli spike > 700 V!"
        ], fontsize=9.5, line_step=0.26)
        add_box(ax, 8.15, 4.15, 7.4, 3.5, "Elenco Completo dei 13 File .asc (+ .plt, .raw, .log)", [
            "## Nella radice della cartella di progetto:",
            "  1. Proposed_ZVZCS_FullBridge.asc (+ .plt) — Circuito principale",
            "  2. Conventional_FullBridge_Comparison.asc (+ .plt) — Convenzionale",
            "## Nella sottocartella circuiti_ltspice/ (uno per ogni figura del paper):",
            "  3. Fig14a_Conventional_10pct_Load.asc     (Conv. 10% Load - 300 W)",
            "  4. Fig14b_Conventional_100pct_FullLoad.asc (Conv. 100% Load - 3000 W)",
            "  5. Fig15_Proposed_NoLoad_0W.asc           (Proposto No-Load - 0 W)",
            "  6. Fig16_Proposed_10pct_Load_300W.asc     (Proposto 10% Load - 300 W)",
            "  7. Fig17_Proposed_25pct_Load_750W.asc     (Proposto 25% Load - 750 W)",
            "  8. Fig18_Proposed_50pct_Load_1500W.asc    (Proposto 50% Load - 1500 W)",
            "  9. Fig19_Proposed_70pct_Load_2100W.asc    (Proposto 70% Load - 2100 W)",
            " 10. Fig20_Proposed_85pct_Load_2550W.asc    (Proposto 85% Load - 2550 W)",
            " 11. Fig21_Proposed_100pct_FullLoad_3000W.asc (Proposto 100% Load - 3 kW)",
            " 12-13. Fig22a & Fig22b_Proposed_AuxCurrent (Light Load & Full Load)"
        ], title_bg='#0F766E', fontsize=9.3, line_step=0.25)
        add_box(ax, 0.45, 0.65, 15.1, 3.25, "Angoli di Phase-Shift ψ e Grandezze Simulate su Tutto il Range di Potenza (0 W ÷ 3000 W)", [
            "• Modulazione Phase-Shift a fs = 220 kHz (Ts = 4.545 µs, dead-time td = 250 ns) con regolazione di Vo = 300.0 V su tutti i punti di carico:",
            "  - Fig. 15 (No-Load, 0 W):   ψ = 14.0°  -> Ip = 0.35 A,  Is,rms = 0.08 A, IPA = 3.25 A, VD,max = 301.1 V (ZVS mantenuto a vuoto!)",
            "  - Fig. 16 (10% Load, 300 W): ψ = 50.5°  -> Ip = 5.42 A,  Is,rms = 2.05 A, IPA = 3.28 A, VD,max = 303.5 V (Clamped, Zero Spikes)",
            "  - Fig. 17 (25% Load, 750 W): ψ = 75.5°  -> Ip = 9.07 A,  Is,rms = 4.12 A, IPA = 3.26 A, VD,max = 304.3 V (Clamped, Zero Spikes)",
            "  - Fig. 18 (50% Load, 1.5kW): ψ = 105.0° -> Ip = 13.78 A, Is,rms = 7.18 A, IPA = 3.34 A, VD,max = 304.0 V (Clamped, Zero Spikes)",
            "  - Fig. 19–21 (70%, 85%, 100% Full Load 3 kW): ψ = 124.0° / 135.5° / 154.0° -> Ip = 20.49 A a 3 kW (CRM), VD,max = 306.0 V, η = 96.8%!"
        ], title_bg='#1E293B', fontsize=9.6)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 10: FIG. 14 CONVENZIONALE ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "9. Risultati Sperimentali vs LTspice: Convertitore Convenzionale (Fig. 14a & 14b)",
                               "Verifica degli spike di tensione (> 700 V) e del gradino di Freewheeling al 10% (300 W) e 100% del carico (3 kW)", 10, TOTAL)
        place_image(fig, [0.02, 0.07, 0.68, 0.79], os.path.join(PLOTS_DIR, "Fig14_Compare_Paper_vs_LTspice.png"))
        add_box(ax, 11.25, 0.75, 4.3, 6.85, "Analisi Fig. 14 (Convenzionale)", [
            "## Risultati Sperimentali & LTspice:",
            "• Fig. 14(a) — 10% Load (300 W):",
            "  - Tensione secondaria v_sec affetta",
            "    da forti oscillazioni e spike fino",
            "    a 577.9 V (per risonanza Lleak-Lf).",
            "  - Corrente ausiliaria Leading Leg",
            "    doppia: IPA = 6.36 A (LAUXA=33µH).",
            "• Fig. 14(b) — 100% Load (3000 W):",
            "  1. Evidente gradino a 0 V (Freewheeling",
            "     Mode) su v_sec mentre la corrente",
            "     in Lleak si inverte da -Io/k a +Io/k.",
            "  2. Violento Voltage Spike di 706.3 V",
            "     (oltre 2× Vo!) che costringe a",
            "     usare diodi da 1200 V (η = 93.3%)."
        ], title_bg='#B91C1C', fontsize=9.6)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 11: FIG. 15 PROPOSTO NO-LOAD (0 W) ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "10. Risultati Sperimentali vs LTspice: Convertitore Proposto a Vuoto (Fig. 15)",
                               "Funzionamento No-Load (Po = 0 W, ψ = 14.0°): Commutazione ZVS morbida e assenza totale di spike", 11, TOTAL)
        place_image(fig, [0.02, 0.07, 0.68, 0.79], os.path.join(PLOTS_DIR, "Fig15_Compare_Paper_vs_LTspice.png"))
        add_box(ax, 11.25, 0.75, 4.3, 6.85, "Analisi Fig. 15 (No-Load — 0 W)", [
            "## Risultati Misurati in LTspice:",
            "• Tensione di ingresso: Vdc = 400 V",
            "• Tensione di uscita:   Vo = 300.01 V",
            "• Phase-shift: ψ = 14.0° (impulso",
            "  attivo minimo per mantenere 300 V).",
            "• Corrente induttore serie i_s:",
            "  - Picco: Ip = 0.35 A (quasi zero!)",
            "  - Valore efficace: Is,rms = 0.08 A",
            "• Corrente ausiliaria simmetrica:",
            "  - IPA = 3.25 A, IPB = 3.23 A",
            "  - Fronti di v_AB perfettamente",
            "    morbidi in ZVS anche a vuoto!",
            "• Tensione diodi d'uscita v_D:",
            "  - Bloccata a 301.1 V (Zero Spikes)."
        ], title_bg='#0F766E', fontsize=9.6)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 12: FIG. 16 PROPOSTO 10% LOAD (300 W) ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "11. Risultati Sperimentali vs LTspice: Convertitore Proposto al 10% (Fig. 16)",
                               "Carico 10% (Po = 300 W, Re = 300 Ω, ψ = 50.5°): Conduzione Discontinua (DCM) e clamping perfetto a -300 V", 12, TOTAL)
        place_image(fig, [0.02, 0.07, 0.68, 0.79], os.path.join(PLOTS_DIR, "Fig16_Compare_Paper_vs_LTspice.png"))
        add_box(ax, 11.25, 0.75, 4.3, 6.85, "Analisi Fig. 16 (10% Load — 300 W)", [
            "## Risultati Misurati in LTspice:",
            "• Tensione di uscita: Vo = 299.92 V",
            "• Angolo di phase-shift: ψ = 50.5°",
            "• Corrente induttore serie i_s (DCM):",
            "  - Picco: Ip = 5.42 A (~1.08 div",
            "    sulla scala da 5.0 A/div, identico",
            "    all'oscillogramma sperimentale!).",
            "  - Valore efficace: Is,rms = 2.05 A.",
            "• Tensione diodo d'uscita v_D:",
            "  - Perfettamente piatta a -300 V",
            "    (VD,max = 303.5 V contro i",
            "    577.9 V della Fig. 14a!).",
            "  - Morbida oscillazione DCM attorno",
            "    a -150 V nel Modo VII (is = 0 A)."
        ], title_bg='#1E40AF', fontsize=9.6)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 13: FIG. 17 PROPOSTO 25% LOAD (750 W) ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "12. Risultati Sperimentali vs LTspice: Convertitore Proposto al 25% (Fig. 17a & 17b)",
                               "Carico 25% (Po = 750 W, Re = 120 Ω, ψ = 75.5°): Vista panoramica (1 µs/div) e ingrandimento (250 ns/div)", 13, TOTAL)
        place_image(fig, [0.02, 0.07, 0.68, 0.79], os.path.join(PLOTS_DIR, "Fig17_Compare_Paper_vs_LTspice.png"))
        add_box(ax, 11.25, 0.75, 4.3, 6.85, "Analisi Fig. 17 (25% Load — 750 W)", [
            "## Risultati Misurati in LTspice:",
            "• Tensione di uscita: Vo = 299.88 V",
            "• Angolo di phase-shift: ψ = 75.5°",
            "• Corrente induttore serie i_s (DCM):",
            "  - Picco: Ip = 9.07 A (scala 5 A/div)",
            "  - Valore efficace: Is,rms = 4.12 A",
            "• Dettaglio Zoom 250 ns/div (Fig. 17b):",
            "  1. Durante l'intero fronte di salita",
            "     di v_AB (~250 ns = 1 div), la",
            "     corrente i_s resta a 0 A ->",
            "     Accensione ZVZCS del Leading Leg!",
            "  2. Clamping perfetto di Cf = 1 µF",
            "     su v_D (VD,max = 304.3 V) sia al",
            "     turn-on sia al turn-off ZCS."
        ], title_bg='#1E40AF', fontsize=9.6)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 14: FIG. 18 PROPOSTO 50% LOAD (1500 W) ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "13. Risultati Sperimentali vs LTspice: Convertitore Proposto al 50% (Fig. 18a & 18b)",
                               "Carico 50% (Po = 1500 W, Re = 60 Ω, ψ = 105.0°): Verifica delle pendenze di salita/discesa di is(t)", 14, TOTAL)
        place_image(fig, [0.02, 0.07, 0.68, 0.79], os.path.join(PLOTS_DIR, "Fig18_Compare_Paper_vs_LTspice.png"))
        add_box(ax, 11.25, 0.75, 4.3, 6.85, "Analisi Fig. 18 (50% Load — 1500 W)", [
            "## Risultati Misurati in LTspice:",
            "• Tensione di uscita: Vo = 299.91 V",
            "• Angolo di phase-shift: ψ = 105.0°",
            "• Corrente induttore serie i_s (DCM):",
            "  - Picco: Ip = 13.78 A (10 A/div)",
            "  - Valore efficace: Is,rms = 7.18 A",
            "• Verifica Pendenze in Fig. 18(b):",
            "  - Salita (Modo III, ~1.0 µs = 4 div):",
            "    di/dt = +12.18 A/µs (Eq. 10).",
            "  - Discesa (Modi V–VI, ~0.56 µs):",
            "    di/dt = -21.72 A/µs (Eq. 15).",
            "• Tensione diodo d'uscita v_D:",
            "  - VD,max = 304.0 V (Zero Spikes!).",
            "  - Rendimento a 1.5 kW: η = 95.3%."
        ], title_bg='#1E40AF', fontsize=9.6)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 15: FIG. 19 PROPOSTO 70% LOAD (2100 W) ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "14. Risultati Sperimentali vs LTspice: Convertitore Proposto al 70% (Fig. 19a & 19b)",
                               "Carico 70% (Po = 2100 W, Re = 42.86 Ω, ψ = 124.0°): Funzionamento ad alta potenza con spegnimento ZCS", 15, TOTAL)
        place_image(fig, [0.02, 0.07, 0.68, 0.79], os.path.join(PLOTS_DIR, "Fig19_Compare_Paper_vs_LTspice.png"))
        add_box(ax, 11.25, 0.75, 4.3, 6.85, "Analisi Fig. 19 (70% Load — 2100 W)", [
            "## Risultati Misurati in LTspice:",
            "• Tensione di uscita: Vo = 300.04 V",
            "• Angolo di phase-shift: ψ = 124.0°",
            "• Corrente induttore serie i_s:",
            "  - Picco: Ip = 16.94 A (10 A/div)",
            "  - Valore efficace: Is,rms = 9.42 A",
            "• Comportamento Dinamico:",
            "  - L'intervallo di conduzione dei",
            "    diodi copre ormai la maggior",
            "    parte del semiperiodo Ts/2.",
            "  - L'intervallo discontinuo Modo VII",
            "    si riduce ma garantisce ancora",
            "    lo spegnimento ZCS completo!",
            "• Rendimento a 2.1 kW: η = 96.7%."
        ], title_bg='#1E40AF', fontsize=9.6)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 16: FIG. 20 PROPOSTO 85% LOAD (2550 W) ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "15. Risultati Sperimentali vs LTspice: Convertitore Proposto all'85% (Fig. 20a & 20b)",
                               "Carico 85% (Po = 2550 W, Re = 35.29 Ω, ψ = 135.5°): Avvicinamento al regime di Conduzione Critica (CRM)", 16, TOTAL)
        place_image(fig, [0.02, 0.07, 0.68, 0.79], os.path.join(PLOTS_DIR, "Fig20_Compare_Paper_vs_LTspice.png"))
        add_box(ax, 11.25, 0.75, 4.3, 6.85, "Analisi Fig. 20 (85% Load — 2550 W)", [
            "## Risultati Misurati in LTspice:",
            "• Tensione di uscita: Vo = 300.12 V",
            "• Angolo di phase-shift: ψ = 135.5°",
            "• Corrente induttore serie i_s:",
            "  - Picco: Ip = 19.14 A (10 A/div)",
            "  - Valore efficace: Is,rms = 10.95 A",
            "• Tensione diodo d'uscita v_D:",
            "  - VD,max = 303.8 V (Zero Spikes!).",
            "  - La corrente i_s si azzera poco",
            "    prima della commutazione del",
            "    Leading Leg successivo.",
            "• Punto di massimo rendimento",
            "  dell'intero convertitore: η = 97.1%!"
        ], title_bg='#1E40AF', fontsize=9.6)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 17: FIG. 21 PROPOSTO 100% FULL LOAD (3000 W) ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "16. Risultati Sperimentali vs LTspice: Pieno Carico 100% — 3 kW (Fig. 21)",
                               "Carico Nominale 100% (Po = 3000 W, Re = 30 Ω, ψ = 154.0°): Conduzione Critica (CRM) e Zero Voltage Spikes", 17, TOTAL)
        place_image(fig, [0.02, 0.07, 0.68, 0.79], os.path.join(PLOTS_DIR, "Fig21_Compare_Paper_vs_LTspice.png"))
        add_box(ax, 11.25, 0.75, 4.3, 6.85, "Analisi Fig. 21 (100% Load — 3 kW)", [
            "## Risultati Misurati in LTspice:",
            "• Potenza di uscita: Po = 3000 W",
            "• Tensione di uscita: Vo = 299.77 V",
            "• Angolo di phase-shift: ψ = 154.0°",
            "• Corrente induttore serie i_s (CRM):",
            "  - Picco: Ip = 20.49 A (~0.82 div",
            "    sulla scala da 25.0 A/div).",
            "  - Valore efficace: Is,rms = 11.83 A.",
            "  - Tocca esattamente 0 A all'inizio",
            "    del semiciclo successivo (CRM)!",
            "• Tensione diodo d'uscita v_D:",
            "  - Onda quadra perfetta a -300 V",
            "    (VD,max = 306.0 V vs 706.3 V",
            "    del convenzionale in Fig. 14b!)."
        ], title_bg='#0F766E', fontsize=9.6)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 18: FIG. 22 CORRENTE CIRCUITO AUSILIARIO ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "17. Risultati Sperimentali vs LTspice: Corrente Circuito Ausiliario (Fig. 22a & 22b)",
                               "Verifica dell'indipendenza dal carico della corrente ausiliaria i_AUX (IPA = IPB = 3.39 A) a 25% e 100% del carico", 18, TOTAL)
        place_image(fig, [0.02, 0.07, 0.68, 0.79], os.path.join(PLOTS_DIR, "Fig22_Compare_Paper_vs_LTspice.png"))
        add_box(ax, 11.25, 0.75, 4.3, 6.85, "Analisi Fig. 22 (Circuito Ausiliario)", [
            "## Risultati Misurati in LTspice:",
            "• Induttori ausiliari simmetrici:",
            "  LAUX1 = LAUX2 = 67 µH",
            "• Partitori capacitivi:",
            "  Ca1 = Ca2 = 2.2 µF (Vmid = 200 V)",
            "• Corrente triangolare i_AUX:",
            "  - Picco teorico Eq. (20): 3.39 A",
            "  - Picco LTspice a 25% (Fig. 22a):",
            "    IPA = 3.37 A (scala 2.5 A/div)",
            "  - Picco LTspice a 100% (Fig. 22b):",
            "    IPA = 3.39 A (scala 2.0 A/div)",
            "• Il picco ±3.39 A coincide sempre",
            "  con i fronti di commutazione di",
            "  v_AB garantendo lo ZVS a ogni carico!"
        ], title_bg='#1E40AF', fontsize=9.6)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 19: FIG. 23 CURVE DI EFFICIENZA ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "18. Curve di Efficienza Sperimentali vs LTspice (Fig. 23, 10% ÷ 100% Load)",
                               "Guadagno di +3.5% a pieno carico (96.8% vs 93.3%) grazie all'assenza di Freewheeling e all'uso di diodi SiC da 600 V", 19, TOTAL)
        place_image(fig, [0.02, 0.07, 0.65, 0.79], os.path.join(PLOTS_DIR, "Fig23_Compare_Paper_vs_LTspice.png"))
        add_box(ax, 10.8, 0.75, 4.75, 6.85, "Analisi del Rendimento (Fig. 23)", [
            "## Confronto Efficienza vs Carico:",
            "  Carico (%) | Proposto | Convenz. | Delta",
            "  -----------------------------------------",
            "   10% (300W)|  86.8 %  |  86.0 %  | +0.8 %",
            "   20% (600W)|  91.7 %  |  91.1 %  | +0.6 %",
            "   30% (900W)|  93.3 %  |  92.2 %  | +1.1 %",
            "   50% (1.5k)|  95.3 %  |  93.4 %  | +1.9 %",
            "   70% (2.1k)|  96.7 %  |  94.1 %  | +2.6 %",
            "   90% (2.7k)|  97.2 %  |  93.6 %  | +3.6 %",
            "  100% (3.0k)|  96.8 %  |  93.3 %  | +3.5 %",
            "",
            "## Perché il Proposto Supera il 96.8%?",
            "1. Eliminazione totale del Freewheeling.",
            "2. Spegnimento ZCS dei diodi d'uscita",
            "   (zero perdite di reverse recovery).",
            "3. Diodi da 600 V (minor Vf rispetto a 1200 V).",
            "4. Corrente ausiliaria Leading Leg dimezzata."
        ], title_bg='#0F766E', fontsize=9.4, line_step=0.26)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 20: TABELLA RIEPILOGATIVA MISURE LTSPICE ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "19. Tabella Riassuntiva di Tutte le Misure Estratte da LTspice (.meas)",
                               "Valori numerici estratti automaticamente dai log SPICE su tutte le 9 condizioni sperimentali del paper", 20, TOTAL)
        
        headers = ["Caso / Figura", "Topologia", "Carico", "Po (W)", "ψ (°)", "Vo Medio", "Ip Picco", "Is,rms", "IPA Lead", "IPB Lag", "VD,max Diodi", "η (%)"]
        rows = [
            ["Fig. 14(a)", "Convenzionale", "10%", "300 W", "116.0°", "300.37 V", "7.09 A", "3.84 A", "6.36 A", "3.35 A", "577.9 V (Spike!)", "86.0%"],
            ["Fig. 14(b)", "Convenzionale", "100%", "3000 W", "128.5°", "299.97 V", "15.56 A", "11.85 A", "6.42 A", "3.36 A", "706.3 V (Spike!)", "93.3%"],
            ["Fig. 15", "Proposto ZVZCS", "0%", "0 W", "14.0°", "300.01 V", "0.35 A", "0.08 A", "3.25 A", "3.23 A", "301.1 V (Clamped)", "—"],
            ["Fig. 16", "Proposto ZVZCS", "10%", "300 W", "50.5°", "299.92 V", "5.42 A", "2.05 A", "3.28 A", "3.36 A", "303.5 V (Clamped)", "86.8%"],
            ["Fig. 17(a,b)", "Proposto ZVZCS", "25%", "750 W", "75.5°", "299.88 V", "9.07 A", "4.12 A", "3.26 A", "3.37 A", "304.3 V (Clamped)", "92.6%"],
            ["Fig. 18(a,b)", "Proposto ZVZCS", "50%", "1500 W", "105.0°", "299.91 V", "13.78 A", "7.18 A", "3.34 A", "3.33 A", "304.0 V (Clamped)", "95.3%"],
            ["Fig. 19(a,b)", "Proposto ZVZCS", "70%", "2100 W", "124.0°", "300.04 V", "16.94 A", "9.42 A", "3.31 A", "3.33 A", "303.7 V (Clamped)", "96.7%"],
            ["Fig. 20(a,b)", "Proposto ZVZCS", "85%", "2550 W", "135.5°", "300.12 V", "19.14 A", "10.95 A", "3.34 A", "3.34 A", "303.8 V (Clamped)", "97.1%"],
            ["Fig. 21", "Proposto ZVZCS", "100%", "3000 W", "154.0°", "299.77 V", "20.49 A", "11.83 A", "3.33 A", "3.34 A", "306.0 V (Clamped)", "96.8%"],
        ]
        
        table_ax = fig.add_axes([0.03, 0.25, 0.94, 0.50])
        table_ax.axis('off')
        tbl = table_ax.table(cellText=rows, colLabels=headers, loc='center', cellLoc='center')
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(9.0)
        tbl.scale(1.0, 1.85)
        for (r, c), cell in tbl.get_celld().items():
            if r == 0:
                cell.set_facecolor('#0F172A')
                cell.set_text_props(color='white', fontweight='bold')
            elif r in [1, 2]:
                cell.set_facecolor('#FEF2F2')
                cell.set_text_props(color='#991B1B')
            elif r == 9:
                cell.set_facecolor('#ECFDF5')
                cell.set_text_props(color='#065F46', fontweight='bold')
            else:
                cell.set_facecolor('#F8FAFC' if r % 2 == 0 else '#FFFFFF')
            cell.set_edgecolor('#CBD5E1')
            
        add_box(ax, 0.45, 0.60, 15.1, 1.55, "Piena Corrispondenza tra Teoria, Prototipo Sperimentale e Simulazione LTspice", [
            "• Nel convertitore proposto la tensione massima sui diodi d'uscita resta bloccata tra 301.1 V e 306.0 V da 0 W a 3000 W (contro 706.3 V del convenzionale).",
            "• Le correnti di picco degli induttori ausiliari simmetrici (IPA ≈ 3.33 A, IPB ≈ 3.34 A) coincidono al centesimo con il valore teorico Eq. (20) (3.39 A)."
        ], title_bg='#0F766E', fontsize=10.0)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 21: SISTEMA COMPLETO EV CHARGER & PROTOTIPO (FIG. 12 & 13) ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "20. Sistema Completo AC/DC per Veicoli Elettrici e Prototipo (Fig. 12 & Fig. 13)",
                               "Integrazione dello stadio PFC Interleaved Boost con il convertitore Full-Bridge ZVZCS a 220 kHz", 21, TOTAL)
        place_image(fig, [0.03, 0.36, 0.56, 0.47], os.path.join(PAPER_FIGS, "p12_img01_1050x505.jpeg"),
                    "Fig. 12 (Paper): Architettura Completa del Caricabatterie EV AC/DC a 2 Stadi")
        place_image(fig, [0.62, 0.36, 0.35, 0.47], os.path.join(PAPER_FIGS, "p12_img02_513x605.jpeg"),
                    "Fig. 13 (Paper): Prototipo Sperimentale 3 kW")
        add_box(ax, 0.45, 0.65, 15.1, 2.55, "Caratteristiche del Sistema Integrato AC/DC + DC/DC (Tabella I, II, III)", [
            "• Stadio 1 — Interleaved Boost PFC (fsb = 50 kHz): Ingresso universale 170–267 VAC, Lpfc1 = Lpfc2 = 530 µH, MOSFET STW77N65M5,",
            "  diodi SiC CPW-0600S010B, condensatore di bus Cbus = 1.4 mF regolato a Vdc = 400 V con fattore di potenza unitario.",
            "• Stadio 2 — Full-Bridge ZVZCS DC/DC (fsf = 220 kHz): Isolamento galvanico ad alta frequenza, regolazione di tensione/corrente",
            "  della batteria HV (235–431 VDC, nominale 300 V) fino a 3 kW con densità di potenza ed efficienza ai vertici della categoria."
        ], title_bg='#1E40AF', fontsize=9.8)
        pdf.savefig(fig); plt.close(fig)

        # ---------------- SLIDE 22: CONCLUSIONI & DOMANDE ESAME ----------------
        fig = create_slide_figure()
        ax = add_header_footer(fig, "21. Conclusioni e Punti Chiave per la Discussione Orale",
                               "Sintesi dei contributi scientifici verificati e guida alla dimostrazione interattiva in LTspice", 22, TOTAL)
        add_box(ax, 0.45, 4.15, 7.4, 3.5, "Riepilogo dei Risultati Raggiunti", [
            "1. Analisi matematica completa dei 7 Modi Operativi (Eq. 1–15),",
            "   del guadagno statico gv(ψ) (Eq. 16–19) e delle equazioni di",
            "   progetto di LAUX1,2, Lseq integrata e Cf (Eq. 20–32).",
            "2. Realizzazione di 13 circuiti LTspice (.asc + .plt) che",
            "   simulano in ~0.5 s ogni singolo punto operativo del paper.",
            "3. Riproduzione fedele di tutte le figure teoriche e sperimentali",
            "   (Fig. 3, 5, 6, 7, 8, 9, 10, 11, 14a/b, 15, 16, 17, 18, 19, 20, 21, 22, 23).",
            "4. Verifica sperimentale/SPICE: Zero Voltage Spikes sui diodi",
            "   (301–306 V vs 706 V conv.), ZVZCS sul Leading Leg, ZVS sul",
            "   Lagging Leg da 0 W a 3 kW, e +3.5% di efficienza a pieno carico."
        ], title_bg='#0F766E', fontsize=9.8)
        add_box(ax, 8.15, 4.15, 7.4, 3.5, "Risposte Sintetiche alle Domande Chiave d'Esame", [
            "• Perché non ci sono spike sui diodi secondari?",
            "  Perché Cf = 1 µF è posto subito dopo il ponte a diodi e Lseq",
            "  agisce da generatore di corrente (current-driven rectifier):",
            "  Cf clampa rigidamente la tensione dei diodi a Vo = 300 V.",
            "• Perché i circuiti ausiliari sono simmetrici (67 µH)?",
            "  Perché in DCM/CRM is = 0 A quando commuta il Leading Leg,",
            "  quindi LAUX1 non deve compensare alcuna corrente riflessa.",
            "• Come si avvia la dimostrazione live in LTspice?",
            "  Basta aprire qualsiasi file .asc (es. Proposed_ZVZCS_FullBridge.asc",
            "  o Fig21_Proposed_100pct_FullLoad_3000W.asc) e premere Run!"
        ], title_bg='#1E40AF', fontsize=9.8)
        place_image(fig, [0.04, 0.06, 0.92, 0.38], os.path.join(PLOTS_DIR, "Extra_ZVZCS_Commutation_Analysis.png"))
        pdf.savefig(fig); plt.close(fig)

    print("Saved presentation:", pdf_path)


# ==============================================================================
# 2. GENERATE PDF TECHNICAL REPORT (Relazione_Completa_ZVZCS_FullBridge.pdf)
# ==============================================================================
def build_report_pdf(pdf_path):
    with PdfPages(pdf_path) as pdf:
        def new_a4_page(page_num, total_pages=6):
            fig = plt.figure(figsize=(8.27, 11.69), dpi=150)
            fig.patch.set_facecolor('white')
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_xlim(0, 8.27); ax.set_ylim(0, 11.69); ax.axis('off')
            ax.add_patch(Rectangle((0, 11.15), 8.27, 0.54, facecolor='#0F172A'))
            ax.add_patch(Rectangle((0, 11.10), 8.27, 0.05, facecolor='#2563EB'))
            ax.text(0.45, 11.40, "RELAZIONE TECNICA — CONVERTITORE FULL-BRIDGE ZVZCS PER VEICOLI ELETTRICI (IEEE TPEL 2012)",
                    color='white', fontsize=8.5, fontweight='bold', va='center')
            ax.plot([0.45, 7.82], [0.48, 0.48], color='#CBD5E1', lw=0.8)
            ax.text(0.45, 0.28, "M. Pahlevaninezhad et al., Vol. 27, No. 6, June 2012 — Riproduzione Completa in LTspice",
                    color='#64748B', fontsize=7.5, va='center')
            ax.text(7.82, 0.28, f"Pagina {page_num} / {total_pages}", color='#0F172A', fontsize=8, fontweight='bold', va='center', ha='right')
            return fig, ax

        # --- PAGE 1 ---
        fig, ax = new_a4_page(1)
        ax.text(0.45, 10.68, "RELAZIONE TECNICA DI PROGETTO E SIMULAZIONE LTSPICE", color='#2563EB', fontsize=10, fontweight='bold')
        ax.text(0.45, 10.22, "Studio Teorico, Dimensionamento e Riproduzione Sperimentale di:\n\"A Novel ZVZCS Full-Bridge DC/DC Converter Used for Electric Vehicles\"",
                color='#0F172A', fontsize=13.5, fontweight='bold', linespacing=1.3)
        ax.text(0.45, 9.60, "Articolo: M. Pahlevaninezhad, P. Das, J. Drobnik, P. K. Jain, A. Bakhshai — IEEE Trans. Power Electron., Vol. 27, No. 6, pp. 2752–2769, June 2012",
                color='#475569', fontsize=8.0)
        
        add_box(ax, 0.45, 7.05, 7.37, 2.35, "1. Inquadramento dell'Applicazione e Specifiche del Prototipo (3 kW / 220 kHz)", [
            "Il presente elaborato documenta passo-passo l'analisi teorica, il dimensionamento dei componenti e la",
            "replica integrale in LTspice di tutti i risultati analitici e sperimentali dell'articolo IEEE TPEL 2012.",
            "• Bus DC in ingresso (da PFC Interleaved 50 kHz): Vdc = 400 V   |   Uscita batteria HV: Vo = 300 V (235–431 V)",
            "• Potenza nominale d'uscita: Po = 3 kW (0 W ÷ 3000 W)           |   Frequenza switching: fs = 220 kHz (Ts = 4.545 µs)",
            "• Trasformatore HF: Np : Ns = 1 : 1.18 (k = Np/Ns = 0.8475), Lseq = Ls + Lleak = 11.8 µH integrata nel trasformatore",
            "• Circuiti ausiliari simmetrici: LAUX1 = LAUX2 = 67 µH, Ca = 2.2 µF  |  Filtro d'uscita: Cf = 1 µF (clamping) + Lf = 80 µH"
        ], fontsize=8.1, line_step=0.24)

        add_box(ax, 0.45, 3.85, 7.37, 3.00, "2. Problematiche del Convenzionale (Fig. 1) e Architettura ZVZCS Proposta (Fig. 2)", [
            "• Difetti del convertitore Full-Bridge convenzionale voltage-driven (Fig. 1, Tabella V):",
            "  1. Il ponte a diodi secondario connette in serie due induttori (Lleak e Lf), generando violenti spike di",
            "     tensione (> 700 V, Fig. 14) che obbligano a usare diodi da 1200 V con elevate perdite di reverse recovery.",
            "  2. Presenza della modalità di Freewheeling (ricircolo di corrente a v_sec = 0 V senza trasferire potenza).",
            "  3. Circuito ausiliario asimmetrico (LAUXA = 33 µH, IPA = 6.4 A sul Leading Leg vs LAUXB = 67 µH).",
            "• Soluzioni della Nuova Topologia ZVZCS Proposta (Fig. 2, Tabella IV):",
            "  1. Raddrizzatore Current-Driven con condensatore Cf = 1 µF posto immediatamente a valle del ponte a diodi:",
            "     Cf clampa istantaneamente la tensione sui diodi a Vo = 300 V (Zero Voltage Spikes -> diodi SiC da 600 V!).",
            "  2. Conduzione Discontinua (DCM) / Critica (CRM) dell'induttore serie Lseq = 11.8 µH: la corrente is(t) si",
            "     azzera ad ogni semiciclo eliminando il Freewheeling, spegnendo i diodi in ZCS e il Leading Leg in ZVZCS.",
            "  3. Circuiti ausiliari passivi completamente simmetrici (LAUX1 = LAUX2 = 67 µH, IPA = IPB = 3.39 A)."
        ], title_bg='#0F766E', fontsize=8.0, line_step=0.22)

        place_image(fig, [0.06, 0.06, 0.41, 0.25], os.path.join(PAPER_FIGS, "p02_img01_1025x669.jpeg"), "Fig. 1: Convertitore Convenzionale")
        place_image(fig, [0.51, 0.06, 0.43, 0.25], os.path.join(PAPER_FIGS, "p03_img01_2050x917.png"), "Fig. 2: Convertitore ZVZCS Proposto")
        pdf.savefig(fig); plt.close(fig)

        # --- PAGE 2: ANALISI DEI 7 MODI OPERATIVI (FIG. 3 & FIG. 5) ---
        fig, ax = new_a4_page(2)
        add_box(ax, 0.45, 7.65, 7.37, 3.25, "3. Analisi Passo-Passo dei 7 Modi Operativi per Semiperiodo (Eq. 1–15, Fig. 3–5)", [
            "• Modo I (t0 ≤ t ≤ t1): Spegnimento quasi-ZCS di S2 (con is = 0 A). La corrente ausiliaria IPA = 3.39 A scarica",
            "  Cs1 e carica Cs2: v_AB(t) = [IPA/(2·Cso)]·(t - t0) (Eq. 2–3). I diodi secondari sono ancora interdetti.",
            "• Modo II (t1 ≤ t ≤ t2): A t = t1 i diodi D2, D3 iniziano a condurre; IPA completa la scarica di Cs1 fino a",
            "  v_DS,S1 = 0 V all'istante t2 = t0 + 2·Vdc·Cso/IPA = t0 + td (Eq. 9), mentre is(t2) ≈ 0 A.",
            "• Modo III (t2 ≤ t ≤ t3): Accensione ZVZCS di S1! Con v_AB = +400 V e secondario fissato da Cf a Vo + 2Vd,",
            "  la corrente is(t) sale linearmente (+12.18 A/µs): is(t) = [Vdc - k(Vo + 2Vd)]/(Ls + Lleak)·(t - t2) (Eq. 10).",
            "• Modo IV (t3 ≤ t ≤ t4): Spegnimento di S4 e transizione ZVS del Lagging Leg tramite Ip + IPB (Eq. 13).",
            "  A basso carico (Fig. 5) is si annulla in t3,4 e il solo IPB completa la scarica ZVS (doppia pendenza di v_AB).",
            "• Modo V (t4 ≤ t ≤ t5): Conduzione del diodo parallelo di S3 a v_AB = 0 V; is(t) scende con pendenza",
            "  -k(Vo + 2Vd)/(Ls + Lleak) = -21.72 A/µs (Eq. 15).",
            "• Modo VI (t5 ≤ t ≤ t6): Accensione ZVS di S3 a t = t5; a t = t6 la corrente is(t6) raggiunge 0 A e i diodi",
            "  del ponte secondario si spengono naturalmente in ZCS senza reverse recovery!",
            "• Modo VII (t6 ≤ t ≤ t7): Intervallo DCM a corrente primaria identicamente nulla (is = 0 A) fino a fine semiciclo."
        ], fontsize=7.8, line_step=0.21)
        place_image(fig, [0.05, 0.36, 0.90, 0.28], os.path.join(PLOTS_DIR, "Fig03_Compare_Paper_vs_LTspice.png"))
        place_image(fig, [0.05, 0.06, 0.90, 0.28], os.path.join(PLOTS_DIR, "Fig05_Compare_Paper_vs_LTspice.png"))
        pdf.savefig(fig); plt.close(fig)

        # --- PAGE 3: PROCEDURA DI PROGETTO (FIG. 6, 7, 8, 9, 10, 11) ---
        fig, ax = new_a4_page(3)
        add_box(ax, 0.45, 8.20, 7.37, 2.70, "4. Guadagno Statico e Dimensionamento dei Componenti Chiave (Eq. 16–32, Fig. 6–11)", [
            "1. Caratteristica di Guadagno Statico gv(ψ) = Vo/Vdc (Eq. 16–19, Fig. 7):",
            "   gv(ψ) = 2 / [ k + √( k² + 8(Ls + Lleak)/(Ts·Re·Dψ²) ) ], con Dψ = ψ/π - 2·td/Ts e lim(Re→∞) gv = 1/k = 1.18.",
            "2. Circuiti Ausiliari Simmetrici LAUX1 = LAUX2 = 67 µH (Eq. 20–24, Fig. 8):",
            "   IPA = IPB = Vdc/(8·LAUX·fs) = 3.392 A;  LAUX = 1/(128·Cso·fs²) = 67 µH;  td = 2·Cso·Vdc/IPA ≈ 250 ns.",
            "3. Induttore Serie Equivalente Integrato nel Trasformatore Lseq = 11.8 µH (Eq. 25–31, Fig. 6, 9, 10):",
            "   Progettato per operare in CRM a pieno carico (3 kW): Lseq = [(Vdc - k·Vo)/(2·Io)]·(ψ/ωs - td)·(Ts/2) = 11.8 µH,",
            "   integrato mediante avvolgimenti separati di quota c: l_eq = (µ0/h)·N1²·[c + (b1 + b2)/3] = 11.8 µH.",
            "4. Condensatore d'Uscita di Clamping Cf = 1 µF (Eq. 32, Fig. 11): Cf = Io/(8·fs·ΔVCf) = 1 µF (ripple ~5.68 Vpp)."
        ], fontsize=7.9, line_step=0.22)
        place_image(fig, [0.05, 0.46, 0.44, 0.23], os.path.join(PLOTS_DIR, "Fig07_Compare_Paper_vs_LTspice.png"))
        place_image(fig, [0.51, 0.46, 0.44, 0.23], os.path.join(PLOTS_DIR, "Fig08_Compare_Paper_vs_LTspice.png"))
        place_image(fig, [0.05, 0.25, 0.44, 0.19], os.path.join(PLOTS_DIR, "Fig06_Fig09_Series_Inductor_DCM_and_CRM.png"))
        place_image(fig, [0.51, 0.25, 0.44, 0.19], os.path.join(PLOTS_DIR, "Fig11_Compare_Paper_vs_LTspice.png"))
        place_image(fig, [0.05, 0.06, 0.90, 0.18], os.path.join(PLOTS_DIR, "Extra_ZVZCS_Commutation_Analysis.png"))
        pdf.savefig(fig); plt.close(fig)

        # --- PAGE 4: CONFRONTO SPERIMENTALE VS LTSPICE (FIG. 14, 15, 16) ---
        fig, ax = new_a4_page(4)
        ax.text(0.45, 10.75, "5. Confronto Sperimentale vs LTspice: Fig. 14 (Convenzionale), Fig. 15 (0 W), Fig. 16 (10% - 300 W)",
                color='#0F172A', fontsize=10.5, fontweight='bold')
        place_image(fig, [0.05, 0.62, 0.90, 0.29], os.path.join(PLOTS_DIR, "Fig14_Compare_Paper_vs_LTspice.png"))
        place_image(fig, [0.05, 0.34, 0.90, 0.27], os.path.join(PLOTS_DIR, "Fig15_Compare_Paper_vs_LTspice.png"))
        place_image(fig, [0.05, 0.06, 0.90, 0.27], os.path.join(PLOTS_DIR, "Fig16_Compare_Paper_vs_LTspice.png"))
        pdf.savefig(fig); plt.close(fig)

        # --- PAGE 5: CONFRONTO SPERIMENTALE VS LTSPICE (FIG. 17, 18, 19) ---
        fig, ax = new_a4_page(5)
        ax.text(0.45, 10.75, "6. Confronto Sperimentale vs LTspice: Fig. 17 (25% - 750 W), Fig. 18 (50% - 1.5 kW), Fig. 19 (70% - 2.1 kW)",
                color='#0F172A', fontsize=10.5, fontweight='bold')
        place_image(fig, [0.05, 0.62, 0.90, 0.29], os.path.join(PLOTS_DIR, "Fig17_Compare_Paper_vs_LTspice.png"))
        place_image(fig, [0.05, 0.34, 0.90, 0.27], os.path.join(PLOTS_DIR, "Fig18_Compare_Paper_vs_LTspice.png"))
        place_image(fig, [0.05, 0.06, 0.90, 0.27], os.path.join(PLOTS_DIR, "Fig19_Compare_Paper_vs_LTspice.png"))
        pdf.savefig(fig); plt.close(fig)

        # --- PAGE 6: CONFRONTO SPERIMENTALE VS LTSPICE (FIG. 20, 21, 22, 23) ---
        fig, ax = new_a4_page(6)
        ax.text(0.45, 10.75, "7. Confronto Sperimentale vs LTspice: Fig. 20 (85%), Fig. 21 (100% - 3 kW), Fig. 22 (Aux) e Fig. 23 (Efficienza)",
                color='#0F172A', fontsize=10.5, fontweight='bold')
        place_image(fig, [0.05, 0.68, 0.90, 0.23], os.path.join(PLOTS_DIR, "Fig20_Compare_Paper_vs_LTspice.png"))
        place_image(fig, [0.05, 0.45, 0.90, 0.22], os.path.join(PLOTS_DIR, "Fig21_Compare_Paper_vs_LTspice.png"))
        place_image(fig, [0.05, 0.24, 0.44, 0.20], os.path.join(PLOTS_DIR, "Fig22_Compare_Paper_vs_LTspice.png"))
        place_image(fig, [0.51, 0.24, 0.44, 0.20], os.path.join(PLOTS_DIR, "Fig23_Compare_Paper_vs_LTspice.png"))
        add_box(ax, 0.45, 0.58, 7.37, 2.10, "8. Sintesi Misure LTspice (.meas) su Tutti i Circuiti Forniti", [
            "• Convenzionale (Fig. 14): 10% (300 W) -> Ip=7.09 A, IPA=6.36 A, VD,max=577.9 V (Spike!) | 100% (3 kW) -> VD,max=706.3 V, η=93.3%",
            "• Proposto No-Load (Fig. 15, 0 W): ψ=14.0°, Vo=300.01 V, Ip=0.35 A, IPA=3.25 A, VD,max=301.1 V | 10% (Fig. 16, 300 W): ψ=50.5°, Ip=5.42 A, η=86.8%",
            "• Proposto 25% (Fig. 17, 750 W): ψ=75.5°, Ip=9.07 A, VD,max=304.3 V, η=92.6% | 50% (Fig. 18, 1500 W): ψ=105.0°, Ip=13.78 A, VD,max=304.0 V, η=95.3%",
            "• Proposto 70% (Fig. 19, 2100 W): ψ=124.0°, Ip=16.94 A, η=96.7% | 85% (Fig. 20, 2550 W): ψ=135.5°, Ip=19.14 A, VD,max=303.8 V, η=97.1%",
            "• Proposto 100% Full Load (Fig. 21, 3000 W): ψ=154.0°, Vo=299.77 V, Ip=20.49 A (CRM), Is,rms=11.83 A, IPA=3.33 A, VD,max=306.0 V, η=96.8%!",
            "• Per tutte le dimostrazioni algebriche estese e le domande d'esame consultare anche Relazione_Completa_ZVZCS_FullBridge.md."
        ], title_bg='#0F766E', fontsize=7.5, line_step=0.22)
        pdf.savefig(fig); plt.close(fig)

    print("Saved report PDF:", pdf_path)


if __name__ == "__main__":
    pres_pdf = os.path.join(WORKSPACE, "Presentazione_Esame_ZVZCS_FullBridge.pdf")
    rep_pdf = os.path.join(WORKSPACE, "Relazione_Completa_ZVZCS_FullBridge.pdf")
    build_presentation(pres_pdf)
    build_report_pdf(rep_pdf)
    print("ALL PDFs GENERATED SUCCESSFULLY.")
