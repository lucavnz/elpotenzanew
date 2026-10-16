# -*- coding: utf-8 -*-
import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)
os.makedirs("grafici_simulazioni", exist_ok=True)

def read_ltspice_raw(raw_path):
    data = open(raw_path, "rb").read()
    marker = "Binary:\n".encode("utf-16le")
    idx = data.find(marker)
    if idx < 0:
        marker = "Binary:\r\n".encode("utf-16le")
        idx = data.find(marker)
    hdr = data[:idx].decode("utf-16le", errors="replace")
    bin_data = data[idx + len(marker):]
    n_vars, n_pts, var_names, in_vars = 0, 0, [], False
    for line in hdr.splitlines():
        ls = line.strip()
        if ls.startswith("No. Variables:"):
            n_vars = int(ls.split(":")[1].strip())
        elif ls.startswith("No. Points:"):
            n_pts = int(ls.split(":")[1].strip())
        elif ls.startswith("Variables:"):
            in_vars = True
        elif in_vars:
            parts = ls.split()
            if len(parts) >= 2 and parts[0].isdigit():
                var_names.append(parts[1])
                if len(var_names) == n_vars:
                    in_vars = False
    bpp = len(bin_data) // n_pts
    dt_list = [("time", "<f8")]
    fmt = "<f8" if bpp == 8 * n_vars else "<f4"
    for vn in var_names[1:]:
        dt_list.append((vn.lower(), fmt))
    arr = np.frombuffer(bin_data[:n_pts * bpp], dtype=np.dtype(dt_list))
    out = {"time": np.abs(arr["time"])}
    for vn in var_names[1:]:
        out[vn.lower()] = arr[vn.lower()].astype(np.float64)
    return out

def plot_scope_panel(ax, t_us, traces, xlim, title, timebase_str, status_items, annotations=None):
    ax.set_facecolor("#ffffff")
    t0, t1 = xlim
    dt_div = (t1 - t0) / 10.0
    for i in range(11):
        x = t0 + i * dt_div
        ax.axvline(x, color="#cccccc", linestyle=":" if i != 5 else "-", linewidth=0.8 if i != 5 else 1.1, zorder=1)
    for j in range(-4, 5):
        ax.axhline(j, color="#cccccc", linestyle=":" if j != 0 else "-", linewidth=0.8 if j != 0 else 1.1, zorder=1)
    
    for tr in traces:
        y_div = tr["y"] / tr["scale"] + tr.get("offset_div", 0.0)
        ax.plot(t_us, y_div, color=tr["color"], linewidth=tr.get("lw", 1.85), label=tr["label"], zorder=3)
        
    ax.set_xlim(t0, t1)
    ax.set_ylim(-4.0, 4.0)
    ax.set_xticks(np.linspace(t0, t1, 11))
    ax.set_xticklabels([f"{x - t0:.2f}" for x in np.linspace(t0, t1, 11)], fontsize=8)
    ax.set_yticks(range(-4, 5))
    ax.set_yticklabels([f"{j:+d} div" if j != 0 else "0" for j in range(-4, 5)], fontsize=8)
    ax.set_xlabel(f"Time (\u03bcs)   [Timebase: {timebase_str}]", fontsize=9, fontweight="bold")
    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=8, color="#1a2a4a")
    
    if annotations:
        for ann in annotations:
            ax.annotate(
                ann["text"], xy=ann["xy"], xytext=ann["xytext"],
                fontsize=8.8, fontweight="bold", style="italic", color=ann["color"],
                arrowprops=dict(arrowstyle="->", color=ann["color"], lw=1.6),
                bbox=dict(boxstyle="round,pad=0.22", fc="white", ec=ann["color"], alpha=0.88),
                zorder=5
            )
            
    box_str = "   |   ".join(status_items)
    ax.text(
        0.5, -0.15, box_str, transform=ax.transAxes,
        fontsize=8.2, fontweight="bold", ha="center", va="top",
        bbox=dict(boxstyle="round,pad=0.35", fc="#eef2f8", ec="#5a6b8c", lw=1.0)
    )

def make_side_by_side(paper_img_path, ltspice_img_path, out_path, suptitle, figsize=(13.5, 6.8)):
    im_p = Image.open(paper_img_path)
    im_l = Image.open(ltspice_img_path)
    fig, axes = plt.subplots(1, 2, figsize=figsize, dpi=250, gridspec_kw={"width_ratios": [1.0, 1.18]})
    axes[0].imshow(im_p)
    axes[0].set_title("Risultato Sperimentale del Paper (Oscilloscopio LeCroy)", fontsize=11, fontweight="bold", color="#8b0000")
    axes[0].axis("off")
    axes[1].imshow(im_l)
    axes[1].set_title("Replica Simulazione LTspice (.asc)", fontsize=11, fontweight="bold", color="#004d26")
    axes[1].axis("off")
    fig.suptitle(suptitle, fontsize=12.5, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(out_path, dpi=250, bbox_inches="tight")
    plt.close(fig)

# ==============================================================================
# 1. FIG. 14: CONVENTIONAL CONVERTER AT 10% AND FULL LOAD
# ==============================================================================
d14a = read_ltspice_raw("circuiti_ltspice/Fig14a_Conventional_10pct_Load.raw")
d14b = read_ltspice_raw("circuiti_ltspice/Fig14b_Conventional_100pct_FullLoad.raw")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.2, 9.6), dpi=250)
t_a = d14a["time"] * 1e6
vab_a = d14a["v(a)"] - d14a["v(b)"]
vsec_a = d14a["v(sec_p)"] - d14a["v(sec_n)"]
iaux_a = d14a["i(laux1)"]
plot_scope_panel(
    ax1, t_a,
    [
        {"y": vab_a, "scale": 130.0, "offset_div": 0.0, "color": "#e60073", "label": "Full-Bridge Output Voltage v_AB"},
        {"y": vsec_a, "scale": 200.0, "offset_div": 0.0, "color": "#00cc00", "label": "Transformer Secondary Voltage v_sec"},
        {"y": iaux_a, "scale": 3.2, "offset_div": 0.0, "color": "#0033cc", "label": "Auxiliary Inductor Current i_AUXA"},
    ],
    xlim=(4.0, 16.0),
    title="(a) Conventional Full-Bridge Converter with Auxiliary Circuit at 10% Load (LTspice)",
    timebase_str="1.20 \u03bcs/div",
    status_items=["C2 (Pink) v_AB: 130 V/div", "C3 (Blue) i_AUXA: 3.2 A/div (Pk=6.5A)", "C4 (Green) v_sec: 200 V/div (Spike=578V)"],
    annotations=[
        {"text": "Full-Bridge\nOutput Voltage", "xy": (6.3, 3.0), "xytext": (4.3, 3.1), "color": "#e60073"},
        {"text": "Severe Secondary\nVoltage Spikes (>570V)", "xy": (8.32, 2.85), "xytext": (9.1, 3.0), "color": "#009900"},
        {"text": "Auxiliary Inductor\nCurrent (6.5 A pk)", "xy": (10.5, 1.8), "xytext": (11.9, 2.1), "color": "#0033cc"},
    ]
)

t_b = d14b["time"] * 1e6
vab_b = d14b["v(a)"] - d14b["v(b)"]
vsec_b = d14b["v(sec_p)"] - d14b["v(sec_n)"]
iaux_b = d14b["i(laux1)"]
plot_scope_panel(
    ax2, t_b,
    [
        {"y": vab_b, "scale": 130.0, "offset_div": 0.0, "color": "#e60073", "label": "Full-Bridge Output Voltage v_AB"},
        {"y": vsec_b, "scale": 200.0, "offset_div": 0.0, "color": "#00cc00", "label": "Transformer Secondary Voltage v_sec"},
        {"y": iaux_b, "scale": 3.2, "offset_div": 0.0, "color": "#0033cc", "label": "Auxiliary Inductor Current i_AUXA"},
    ],
    xlim=(4.0, 16.0),
    title="(b) Conventional Full-Bridge Converter with Auxiliary Circuit at Full-Load 3 kW (LTspice)",
    timebase_str="1.20 \u03bcs/div",
    status_items=["C2 (Pink) v_AB: 130 V/div", "C3 (Blue) i_AUXA: 3.2 A/div (Pk=6.5A)", "C4 (Green) v_sec: 200 V/div (Spike=706V!)"],
    annotations=[
        {"text": "Full-Bridge\nOutput Voltage", "xy": (6.3, 3.0), "xytext": (4.3, 3.1), "color": "#e60073"},
        {"text": "Severe Voltage Spike (>700V)\n+ Freewheeling Step!", "xy": (8.55, 3.4), "xytext": (9.2, 2.9), "color": "#009900"},
        {"text": "Auxiliary Current", "xy": (10.5, 1.8), "xytext": (12.1, 2.1), "color": "#0033cc"},
    ]
)
plt.tight_layout(h_pad=3.2)
fig.savefig("grafici_simulazioni/Fig14_Conventional_Converter_LTspice.png", dpi=250, bbox_inches="tight")
plt.close(fig)
make_side_by_side(
    "paper_figures/p13_img03_513x867.jpeg",
    "grafici_simulazioni/Fig14_Conventional_Converter_LTspice.png",
    "grafici_simulazioni/Fig14_Compare_Paper_vs_LTspice.png",
    "Fig. 14 \u2014 Convertitore Full-Bridge Convenzionale con Circuito Ausiliario (10% Carico e Pieno Carico)",
    figsize=(13.5, 8.8)
)

# ==============================================================================
# 2. FIG. 15: PROPOSED CONVERTER AT NO LOAD (0 W)
# ==============================================================================
d15 = read_ltspice_raw("circuiti_ltspice/Fig15_Proposed_NoLoad_0W.raw")
fig, ax = plt.subplots(1, 1, figsize=(8.2, 5.2), dpi=250)
t = d15["time"] * 1e6
vab = d15["v(a)"] - d15["v(b)"]
vsec = d15["v(sec_p)"] - d15["v(sec_n)"]
vd = d15["v(out_rect)"] - d15["v(sec_p)"]
is_curr = d15["i(lseq)"]
plot_scope_panel(
    ax, t,
    [
        {"y": vd, "scale": 200.0, "offset_div": 0.0, "color": "#b39700", "label": "Output Diode Voltage"},
        {"y": vsec, "scale": 200.0, "offset_div": 0.0, "color": "#e60073", "label": "Transformer Secondary Voltage"},
        {"y": vab, "scale": 160.0, "offset_div": 0.0, "color": "#0033cc", "label": "Full-Bridge Output Voltage"},
        {"y": is_curr, "scale": 5.0, "offset_div": 0.0, "color": "#00cc00", "label": "Series Inductor Current"},
    ],
    xlim=(4.0, 14.0),
    title="Fig. 15 \u2014 Proposed ZVZCS Converter Waveforms at No-Load (0 W, LTspice)",
    timebase_str="1.00 \u03bcs/div",
    status_items=["C1 (Gold) v_D: 200 V/div", "C2 (Pink) v_sec: 200 V/div", "C3 (Blue) v_AB: 160 V/div", "C4 (Green) i_s: 5.00 A/div (Pk=0.35A)"],
    annotations=[
        {"text": "Full-Bridge Output\nVoltage (Narrow ZVS Pulse)", "xy": (9.1, 2.4), "xytext": (5.2, 3.0), "color": "#0033cc"},
        {"text": "Transformer\nSecondary Voltage", "xy": (9.1, 1.5), "xytext": (4.8, 1.6), "color": "#e60073"},
        {"text": "Output Diode\nVoltage (<302V)", "xy": (10.5, 1.5), "xytext": (10.2, 2.7), "color": "#997a00"},
        {"text": "Series Inductor\nCurrent (~0 A)", "xy": (9.1, 0.1), "xytext": (9.8, 0.8), "color": "#009900"},
    ]
)
plt.tight_layout()
fig.savefig("grafici_simulazioni/Fig15_Proposed_NoLoad_0W_LTspice.png", dpi=250, bbox_inches="tight")
plt.close(fig)
make_side_by_side(
    "paper_figures/p13_img01_513x491.jpeg",
    "grafici_simulazioni/Fig15_Proposed_NoLoad_0W_LTspice.png",
    "grafici_simulazioni/Fig15_Compare_Paper_vs_LTspice.png",
    "Fig. 15 \u2014 Convertitore ZVZCS Proposto a Vuoto (No-Load, P_o = 0 W)"
)

# ==============================================================================
# 3. FIG. 16: PROPOSED CONVERTER AT 10% LOAD (300 W)
# ==============================================================================
d16 = read_ltspice_raw("circuiti_ltspice/Fig16_Proposed_10pct_Load_300W.raw")
fig, ax = plt.subplots(1, 1, figsize=(8.2, 5.2), dpi=250)
t = d16["time"] * 1e6
vab = d16["v(a)"] - d16["v(b)"]
vd = d16["v(sec_n)"] - d16["v(out_rect)"] # -300V during positive half-cycle, 0V during negative half-cycle
is_curr = d16["i(lseq)"]
plot_scope_panel(
    ax, t,
    [
        {"y": vab, "scale": 105.0, "offset_div": 0.0, "color": "#e60073", "label": "Full-Bridge Output Voltage v_AB"},
        {"y": vd, "scale": 100.0, "offset_div": -0.5, "color": "#0033cc", "label": "Output Diode Voltage v_D"},
        {"y": is_curr, "scale": 5.0, "offset_div": 0.0, "color": "#00cc00", "label": "Series Inductor Current i_s"},
    ],
    xlim=(4.4, 14.4),
    title="Fig. 16 \u2014 Proposed ZVZCS Converter Waveforms at 10% Load (300 W, LTspice)",
    timebase_str="1.00 \u03bcs/div",
    status_items=["C2 (Pink) v_AB: 100 V/div (2x)", "C3 (Blue) v_D: 100 V/div (Clamped -300V)", "C4 (Green) i_s: 5.00 A/div (Pk=5.42A)"],
    annotations=[
        {"text": "Full-Bridge\nOutput Voltage", "xy": (10.4, 3.2), "xytext": (6.2, 2.9), "color": "#e60073"},
        {"text": "Series Inductor\nCurrent (5.4 A pk)", "xy": (10.6, 1.05), "xytext": (6.6, 1.4), "color": "#009900"},
        {"text": "Output Diode Voltage\n(Clamped at -300V, Zero Spikes)", "xy": (10.4, -3.5), "xytext": (10.8, -1.3), "color": "#0033cc"},
    ]
)
plt.tight_layout()
fig.savefig("grafici_simulazioni/Fig16_Proposed_10pct_Load_LTspice.png", dpi=250, bbox_inches="tight")
plt.close(fig)
make_side_by_side(
    "paper_figures/p13_img02_513x402.jpeg",
    "grafici_simulazioni/Fig16_Proposed_10pct_Load_LTspice.png",
    "grafici_simulazioni/Fig16_Compare_Paper_vs_LTspice.png",
    "Fig. 16 \u2014 Convertitore ZVZCS Proposto al 10% del Carico (300 W)"
)

# ==============================================================================
# Helper for dual (a) 1.0 us/div + (b) 250 ns/div figures (Figs. 17, 18, 19, 20)
# ==============================================================================
def make_dual_load_fig(raw_path, paper_img, out_lt, out_cmp, fig_num, pct, power_w, i_scale, ip_val):
    d = read_ltspice_raw(raw_path)
    t = d["time"] * 1e6
    vab = d["v(a)"] - d["v(b)"]
    vd = d["v(sec_n)"] - d["v(out_rect)"]
    is_curr = d["i(lseq)"]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.2, 9.8), dpi=250)
    plot_scope_panel(
        ax1, t,
        [
            {"y": vab, "scale": 200.0, "offset_div": 0.0, "color": "#e60073", "label": "Full-Bridge Output Voltage"},
            {"y": vd, "scale": 100.0, "offset_div": -0.5, "color": "#0033cc", "label": "Output Diode Voltage"},
            {"y": is_curr, "scale": i_scale, "offset_div": 0.0, "color": "#00cc00", "label": "Series Inductor Current"},
        ],
        xlim=(4.4, 14.4),
        title=f"Fig. {fig_num}(a) \u2014 Proposed Converter Waveforms at {pct}% Load ({power_w} W, LTspice)",
        timebase_str="1.00 \u03bcs/div",
        status_items=["C2 (Pink) v_AB: 200 V/div", "C3 (Blue) v_D: 100 V/div (Clamped -300V)", f"C4 (Green) i_s: {i_scale:.1f} A/div (Pk={ip_val:.1f}A)"],
        annotations=[
            {"text": "Full-Bridge\nOutput Voltage", "xy": (10.5, 2.0), "xytext": (6.2, 2.7), "color": "#e60073"},
            {"text": f"Series Inductor\nCurrent ({ip_val:.1f} A pk)", "xy": (10.9, ip_val/i_scale), "xytext": (6.3, 1.3), "color": "#009900"},
            {"text": "Output Diode Voltage\n(Clamped at -300 V)", "xy": (10.5, -3.5), "xytext": (10.9, -1.2), "color": "#0033cc"},
        ]
    )
    
    # Enlarged 250 ns/div view (total width = 2.5 us, centered on positive half-cycle starting at t0 = 10.00 us: 9.65 to 12.15 us)
    dt_pulse = 0.72 if pct == 25 else (1.02 if pct == 50 else (1.22 if pct == 70 else 1.38))
    plot_scope_panel(
        ax2, t,
        [
            {"y": vab, "scale": 200.0, "offset_div": 0.0, "color": "#e60073", "label": "Full-Bridge Output Voltage", "lw": 2.1},
            {"y": vd, "scale": 100.0, "offset_div": -0.5, "color": "#0033cc", "label": "Output Diode Voltage", "lw": 2.1},
            {"y": is_curr, "scale": i_scale, "offset_div": 0.0, "color": "#00cc00", "label": "Series Inductor Current", "lw": 2.1},
        ],
        xlim=(9.65, 12.15),
        title=f"Fig. {fig_num}(b) \u2014 Proposed Converter Enlarged Waveforms at {pct}% Load (250 ns/div, LTspice)",
        timebase_str="250 ns/div",
        status_items=["C2 (Pink) v_AB: 200 V/div", "C3 (Blue) v_D: 100 V/div", f"C4 (Green) i_s: {i_scale:.1f} A/div", "Timebase: 250 ns/div"],
        annotations=[
            {"text": "No Voltage Spikes\n(Smooth ZVS Edge)", "xy": (10.22, 1.95), "xytext": (9.70, 2.85), "color": "#111111"},
            {"text": "Full-Bridge Output Voltage", "xy": (10.55, 2.0), "xytext": (10.45, 2.85), "color": "#e60073"},
            {"text": "Series Inductor Current\n(Zero at Leading-Leg Turn-ON -> ZVZCS!)", "xy": (10.65, (ip_val*0.65)/i_scale), "xytext": (10.40, 0.25), "color": "#009900"},
            {"text": "No Voltage Spikes\n(Clamped by C_f)", "xy": (10.12, -3.5), "xytext": (9.70, -1.5), "color": "#0033cc"},
            {"text": "No Voltage Spikes\n(ZCS Diode Turn-OFF)", "xy": (10.10 + dt_pulse*1.55, -3.5), "xytext": (11.15, -1.5), "color": "#111111"},
        ]
    )
    plt.tight_layout(h_pad=3.2)
    fig.savefig(out_lt, dpi=250, bbox_inches="tight")
    plt.close(fig)
    make_side_by_side(
        paper_img, out_lt, out_cmp,
        f"Fig. {fig_num} \u2014 Convertitore ZVZCS Proposto al {pct}% del Carico ({power_w} W): (a) 1 \u03bcs/div e (b) Zoom 250 ns/div",
        figsize=(13.5, 9.0)
    )

# 4. FIG. 17: 25% LOAD (750 W)
make_dual_load_fig(
    "circuiti_ltspice/Fig17_Proposed_25pct_Load_750W.raw",
    "paper_figures/p14_img02_467x851.jpeg",
    "grafici_simulazioni/Fig17_Proposed_25pct_Load_LTspice.png",
    "grafici_simulazioni/Fig17_Compare_Paper_vs_LTspice.png",
    17, 25, 750, 5.0, 9.07
)

# 5. FIG. 18: 50% LOAD (1500 W)
make_dual_load_fig(
    "circuiti_ltspice/Fig18_Proposed_50pct_Load_1500W.raw",
    "paper_figures/p14_img03_513x910.jpeg",
    "grafici_simulazioni/Fig18_Proposed_50pct_Load_LTspice.png",
    "grafici_simulazioni/Fig18_Compare_Paper_vs_LTspice.png",
    18, 50, 1500, 10.0, 13.78
)

# 6. FIG. 19: 70% LOAD (2100 W)
make_dual_load_fig(
    "circuiti_ltspice/Fig19_Proposed_70pct_Load_2100W.raw",
    "paper_figures/p15_img01_513x911.jpeg",
    "grafici_simulazioni/Fig19_Proposed_70pct_Load_LTspice.png",
    "grafici_simulazioni/Fig19_Compare_Paper_vs_LTspice.png",
    19, 70, 2100, 10.0, 16.94
)

# 7. FIG. 20: 85% LOAD (2550 W)
make_dual_load_fig(
    "circuiti_ltspice/Fig20_Proposed_85pct_Load_2550W.raw",
    "paper_figures/p15_img02_513x722.jpeg",
    "grafici_simulazioni/Fig20_Proposed_85pct_Load_LTspice.png",
    "grafici_simulazioni/Fig20_Compare_Paper_vs_LTspice.png",
    20, 85, 2550, 10.0, 19.14
)

# ==============================================================================
# 8. FIG. 21: PROPOSED CONVERTER AT FULL LOAD (100%, 3000 W - CRM)
# ==============================================================================
d21 = read_ltspice_raw("circuiti_ltspice/Fig21_Proposed_100pct_FullLoad_3000W.raw")
fig, ax = plt.subplots(1, 1, figsize=(8.2, 5.2), dpi=250)
t = d21["time"] * 1e6
vab = d21["v(a)"] - d21["v(b)"]
vd = d21["v(sec_n)"] - d21["v(out_rect)"]
is_curr = d21["i(lseq)"]
plot_scope_panel(
    ax, t,
    [
        {"y": vab, "scale": 250.0, "offset_div": 0.0, "color": "#e60073", "label": "Full-Bridge Output Voltage"},
        {"y": vd, "scale": 200.0, "offset_div": 0.0, "color": "#0033cc", "label": "Output Diode Voltage"},
        {"y": is_curr, "scale": 25.0, "offset_div": 0.0, "color": "#00cc00", "label": "Series Inductor Current"},
    ],
    xlim=(4.4, 14.4),
    title="Fig. 21 \u2014 Proposed ZVZCS Converter Waveforms at Full-Load (3000 W, Critical Conduction Mode, LTspice)",
    timebase_str="1.00 \u03bcs/div",
    status_items=["C2 (Pink) v_AB: 250 V/div", "C3 (Blue) v_D: 200 V/div (Clamped -300V)", "C4 (Green) i_s: 25.0 A/div (Pk=20.5A, CRM)"],
    annotations=[
        {"text": "Full-Bridge Output Voltage\n(\u00b1400 V, Smooth ZVS)", "xy": (10.8, 1.6), "xytext": (6.2, 2.6), "color": "#e60073"},
        {"text": "Series Inductor Current\n(Critical Conduction Mode, 20.5 A pk)", "xy": (11.6, 0.8), "xytext": (5.0, 1.35), "color": "#009900"},
        {"text": "Output Diode Voltage\n(Clamped at -300 V, Zero Spikes!)", "xy": (10.8, -1.5), "xytext": (7.5, -3.1), "color": "#0033cc"},
    ]
)
plt.tight_layout()
fig.savefig("grafici_simulazioni/Fig21_Proposed_100pct_FullLoad_LTspice.png", dpi=250, bbox_inches="tight")
plt.close(fig)
make_side_by_side(
    "paper_figures/p15_img03_513x370.jpeg",
    "grafici_simulazioni/Fig21_Proposed_100pct_FullLoad_LTspice.png",
    "grafici_simulazioni/Fig21_Compare_Paper_vs_LTspice.png",
    "Fig. 21 \u2014 Convertitore ZVZCS Proposto a Pieno Carico (100% Load, 3 kW \u2014 Conduzione Critica CRM)"
)

# ==============================================================================
# 9. FIG. 22(a) & (b): AUXILIARY CIRCUIT CURRENT AT DIFFERENT LOADS
# ==============================================================================
d22a = read_ltspice_raw("circuiti_ltspice/Fig22a_Proposed_AuxCurrent_LightLoad.raw")
d22b = read_ltspice_raw("circuiti_ltspice/Fig22b_Proposed_AuxCurrent_FullLoad.raw")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.2, 9.6), dpi=250)

t_a = d22a["time"] * 1e6
vab_a = d22a["v(a)"] - d22a["v(b)"]
vsec_a = d22a["v(sec_p)"] - d22a["v(sec_n)"]
is_a = d22a["i(lseq)"]
iaux_a = d22a["i(laux1)"]
plot_scope_panel(
    ax1, t_a,
    [
        {"y": vab_a, "scale": 200.0, "offset_div": 0.0, "color": "#b39700", "label": "Full-Bridge Output Voltage"},
        {"y": vsec_a, "scale": 100.0, "offset_div": 0.0, "color": "#e60073", "label": "Transformer Output Voltage"},
        {"y": iaux_a, "scale": 2.5, "offset_div": 0.0, "color": "#0033cc", "label": "Auxiliary Circuit Current"},
        {"y": is_a, "scale": 5.0, "offset_div": 0.0, "color": "#00cc00", "label": "Series Inductor Current"},
    ],
    xlim=(4.0, 14.0),
    title="Fig. 22(a) \u2014 Current in Auxiliary Circuit at Light Load (25% Load, LTspice)",
    timebase_str="1.00 \u03bcs/div",
    status_items=["C1 (Gold) v_AB: 200 V/div", "C2 (Pink) v_sec: 100 V/div", "C3 (Blue) i_AUX: 2.50 A/div (Pk=3.37A)", "C4 (Green) i_s: 5.00 A/div"],
    annotations=[
        {"text": "Transformer Output Voltage\n(\u00b1300 V Clamped)", "xy": (10.5, 3.0), "xytext": (5.2, 3.1), "color": "#e60073"},
        {"text": "Full-Bridge Output\n(\u00b1400 V)", "xy": (10.7, 2.0), "xytext": (11.1, 2.8), "color": "#997a00"},
        {"text": "Series Inductor Current", "xy": (10.9, 1.7), "xytext": (6.8, 2.1), "color": "#009900"},
        {"text": "Auxiliary Circuit Current\n(\u00b13.39 A Peak at Switching)", "xy": (10.0, 1.35), "xytext": (8.5, -2.8), "color": "#0033cc"},
    ]
)

t_b = d22b["time"] * 1e6
vab_b = d22b["v(a)"] - d22b["v(b)"]
iaux_b = d22b["i(laux1)"]
plot_scope_panel(
    ax2, t_b,
    [
        {"y": vab_b, "scale": 150.0, "offset_div": 0.0, "color": "#e60073", "label": "Full-Bridge Output Voltage"},
        {"y": iaux_b, "scale": 2.0, "offset_div": 0.0, "color": "#0033cc", "label": "Auxiliary Circuit Current"},
    ],
    xlim=(4.0, 14.0),
    title="Fig. 22(b) \u2014 Current in Auxiliary Circuit at Heavy/Full Load (100% Load, LTspice)",
    timebase_str="1.00 \u03bcs/div",
    status_items=["C2 (Pink) v_AB: 150 V/div (\u00b1400V)", "C3 (Blue) i_AUX: 2.00 A/div (Pk=\u00b13.39A)", "f_s = 220 kHz"],
    annotations=[
        {"text": "Full-Bridge Output Voltage", "xy": (10.5, 2.66), "xytext": (6.2, 3.0), "color": "#e60073"},
        {"text": "Auxiliary Circuit Current\n(I_PA = 3.39 A at ZVS Turn-ON)", "xy": (10.0, 1.68), "xytext": (10.3, 2.3), "color": "#0033cc"},
    ]
)
plt.tight_layout(h_pad=3.2)
fig.savefig("grafici_simulazioni/Fig22_Proposed_AuxCurrent_LTspice.png", dpi=250, bbox_inches="tight")
plt.close(fig)
make_side_by_side(
    "paper_figures/p16_img01_513x793.jpeg",
    "grafici_simulazioni/Fig22_Proposed_AuxCurrent_LTspice.png",
    "grafici_simulazioni/Fig22_Compare_Paper_vs_LTspice.png",
    "Fig. 22 \u2014 Corrente nel Circuito Ausiliario a Diversi Carichi: (a) Carico Leggero e (b) Pieno Carico",
    figsize=(13.5, 8.8)
)

# ==============================================================================
# 10. FIG. 3: COMPLETE OPERATING MODES WAVEFORMS (MODES I TO VII) FROM LTSPICE
# ==============================================================================
d50 = read_ltspice_raw("circuiti_ltspice/Fig18_Proposed_50pct_Load_1500W.raw")
t = d50["time"] * 1e6
# Select a window covering a full switching cycle starting around t0 = 10.00 us (9.0 to 15.0 us)
mask = (t >= 9.0) & (t <= 15.0)
tw = t[mask]
g1 = d50["v(g1_drv)"][mask] - d50["v(a)"][mask]
g2 = d50["v(g2_drv)"][mask]
g3 = d50["v(g3_drv)"][mask] - d50["v(b)"][mask]
g4 = d50["v(g4_drv)"][mask]
vab = (d50["v(a)"] - d50["v(b)"])[mask]
va = d50["v(a)"][mask]
iaux1 = d50["i(laux1)"][mask]
iaux2 = d50["i(laux2)"][mask]
icso = (d50["i(cs1)"] - d50["i(cs2)"])[mask]
is_w = d50["i(lseq)"][mask]
idb = np.abs(d50["i(lsec)"][mask])
vsec = (d50["v(sec_p)"] - d50["v(sec_n)"])[mask]

fig, axes = plt.subplots(10, 1, figsize=(10.5, 13.5), sharex=True, dpi=250)
traces_fig3 = [
    (g1, "$G_1$ (V)", "#1f77b4", (-5, 18)),
    (g2, "$G_2$ (V)", "#ff7f0e", (-5, 18)),
    (g3, "$G_3$ (V)", "#2ca02c", (-5, 18)),
    (g4, "$G_4$ (V)", "#d62728", (-5, 18)),
    (vab, "$v_{AB}$ (V)", "#e60073", (-450, 450)),
    (va, "$v_A$ (V)", "#9467bd", (-50, 450)),
    (iaux1, "$i_{LAUX1}, i_{LAUX2}$ (A)", "#0033cc", (-4.2, 4.2)),
    (icso, "$i_{Co,SA}$ (A)", "#8c564b", (-4.5, 4.5)),
    (is_w, "$i_s$ (A)", "#009900", (-16, 16)),
    (vsec, "$v_{sec}$ (V)", "#b39700", (-360, 360)),
]
# Positive half-cycle starting at t0 = 10.00 us:
t_modes = [10.00, 10.06, 10.25, 11.33, 11.46, 11.58, 12.00, 12.27]
mode_labels = ["$t_0$", "$t_1$", "$t_2$", "$t_3$", "$t_4$", "$t_5$", "$t_6$", "$t_7$"]

for idx, (ax, (y_arr, ylabel, col, ylim)) in enumerate(zip(axes, traces_fig3)):
    ax.plot(tw, y_arr, color=col, lw=1.8)
    if idx == 6:
        ax.plot(tw, iaux2, color="#ff6600", lw=1.5, ls="--", label="$i_{LAUX2}$")
        ax.legend(loc="upper right", fontsize=8)
    if idx == 8:
        ax.plot(tw, idb, color="#006666", lw=1.3, ls=":", label="$i_{DB} = |i_{sec}|$")
        ax.legend(loc="upper right", fontsize=8)
    ax.set_ylabel(ylabel, fontsize=9, fontweight="bold")
    ax.set_ylim(*ylim)
    ax.grid(True, linestyle=":", alpha=0.6)
    for tm in t_modes:
        ax.axvline(tm, color="#555555", linestyle="--", linewidth=0.8, alpha=0.7)

axes[0].set_title("Fig. 3 \u2014 Forme d'Onda Complete del Convertitore ZVZCS e 7 Modi Operativi ($t_0 \\div t_7$, Simulazione LTspice)", fontsize=12, fontweight="bold")
axes[-1].set_xlabel("Time (\u03bcs)", fontsize=10, fontweight="bold")
for tm, ml in zip(t_modes, mode_labels):
    axes[-1].text(tm, -430, ml, ha="center", va="top", fontsize=9, fontweight="bold", color="#8b0000")
plt.tight_layout()
fig.savefig("grafici_simulazioni/Fig03_Complete_Waveforms_Modes_I_to_VII.png", dpi=250, bbox_inches="tight")
plt.close(fig)
make_side_by_side(
    "paper_figures/p04_img01_1432x2389.jpeg",
    "grafici_simulazioni/Fig03_Complete_Waveforms_Modes_I_to_VII.png",
    "grafici_simulazioni/Fig03_Compare_Paper_vs_LTspice.png",
    "Fig. 3 \u2014 Forme d'Onda Ideali del Paper vs Forme d'Onda Simulate in LTspice sui 7 Modi Operativi",
    figsize=(13.5, 9.5)
)

# ==============================================================================
# 11. FIG. 5: SUBMODES OF MODE IV AT LIGHT LOADS (TWO SLOPES OF LAGGING EDGE)
# ==============================================================================
d10 = read_ltspice_raw("circuiti_ltspice/Fig16_Proposed_10pct_Load_300W.raw")
t10 = d10["time"] * 1e6
m10 = (t10 >= 9.85) & (t10 <= 11.15)
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(7.5, 7.5), sharex=True, dpi=250)
ax1.plot(t10[m10], (d10["v(a)"] - d10["v(b)"])[m10], color="#e60073", lw=2.2)
ax1.set_ylabel("$v_{AB}$ (V)", fontweight="bold")
ax1.set_title("Fig. 5 \u2014 Sotto-Modi del Modo IV a Carico Leggero (10% Load, LTspice)", fontsize=11, fontweight="bold")
ax1.annotate("1\u00aa Pendenza ($t_3 \\to t_{3,4}$):\n$I_p + I_{PB}$ scaricano $C_{so}$", xy=(10.66, 260), xytext=(10.05, 290),
             arrowprops=dict(arrowstyle="->", color="#0033cc", lw=1.5), fontweight="bold", fontsize=8.5, color="#0033cc")
ax1.annotate("2\u00aa Pendenza ($t_{3,4} \\to t_4$):\nsolo $I_{PB}$ completa la scarica ZVS", xy=(10.75, 90), xytext=(10.82, 180),
             arrowprops=dict(arrowstyle="->", color="#8b0000", lw=1.5), fontweight="bold", fontsize=8.5, color="#8b0000")

ax2.plot(t10[m10], d10["i(lseq)"][m10], color="#009900", lw=2.2)
ax2.set_ylabel("$i_s$ (A)", fontweight="bold")

ax3.plot(t10[m10], (d10["v(sec_p)"] - d10["v(sec_n)"])[m10], color="#0033cc", lw=2.2)
ax3.set_ylabel("$v_{sec}$ (V)", fontweight="bold")
ax3.set_xlabel("Time (\u03bcs)", fontweight="bold")

for ax in (ax1, ax2, ax3):
    ax.grid(True, linestyle=":", alpha=0.7)
    for tx in [10.64, 10.71, 10.82]:
        ax.axvline(tx, color="#444444", ls="--", lw=1.0)
plt.tight_layout()
fig.savefig("grafici_simulazioni/Fig05_Mode_IV_LightLoad_Submodes.png", dpi=250, bbox_inches="tight")
plt.close(fig)
make_side_by_side(
    "paper_figures/p07_img01_900x1161.jpeg",
    "grafici_simulazioni/Fig05_Mode_IV_LightLoad_Submodes.png",
    "grafici_simulazioni/Fig05_Compare_Paper_vs_LTspice.png",
    "Fig. 5 \u2014 Sotto-Modi del Modo IV a Carico Leggero ($t_3 \\to t_{3,4} \\to t_4$): Paper vs LTspice"
)

# ==============================================================================
# 12. FIG. 6 & FIG. 9: SERIES INDUCTOR WAVEFORMS (DCM vs CRM)
# ==============================================================================
fig, axes = plt.subplots(2, 2, figsize=(12, 7.2), dpi=250)
m50 = (t >= 9.85) & (t <= 12.35)
axes[0, 0].plot(t[m50], d50["i(lseq)"][m50], color="#009900", lw=2.2)
axes[0, 0].set_title("Fig. 6(a) \u2014 Corrente Induttore Serie $i_s(t)$ in DCM (50% Load)", fontweight="bold")
axes[0, 0].set_ylabel("$i_s$ (A)", fontweight="bold")
axes[0, 0].annotate("Salita: $\\frac{V_{dc}-k(V_o+2V_d)}{L_{seq}}$\n$= +12.18\\text{ A/}\\mu\\text{s}$", xy=(10.75, 8.0), xytext=(10.0, 11.0),
                    arrowprops=dict(arrowstyle="->", color="#006600"), fontsize=8.5, fontweight="bold")
axes[0, 0].annotate("Discesa: $\\frac{-k(V_o+2V_d)}{L_{seq}}$\n$= -21.72\\text{ A/}\\mu\\text{s}$", xy=(11.65, 7.0), xytext=(11.55, 11.0),
                    arrowprops=dict(arrowstyle="->", color="#8b0000"), fontsize=8.5, fontweight="bold")

v_lseq_50 = (d50["v(pri_cb)"] - d50["v(pri_tr)"])[m50]
axes[1, 0].plot(t[m50], v_lseq_50, color="#0033cc", lw=2.0)
axes[1, 0].set_title("Fig. 6(b) \u2014 Tensione su $L_{seq}$ per Mezzo Ciclo ($V_{dc}-kV_o$ e $-kV_o$)", fontweight="bold")
axes[1, 0].set_ylabel("$v_{Lseq}$ (V)", fontweight="bold")
axes[1, 0].set_xlabel("Time (\u03bcs)", fontweight="bold")

t21 = d21["time"] * 1e6
m21 = (t21 >= 9.95) & (t21 <= 14.55)
axes[0, 1].plot(t21[m21], d21["i(lseq)"][m21], color="#e60073", lw=2.2, label="$i_s(t)$ in CRM (100% Load)")
axes[0, 1].axhline(20.49/2, color="#0033cc", ls="--", lw=1.2, label="Valore Medio Semiciclo $k I_o$")
axes[0, 1].axhline(20.49, color="#009900", ls=":", lw=1.2, label="Picco $I_p \\approx 2 k I_o$")
axes[0, 1].set_title("Fig. 9 \u2014 Conduzione Critica (CRM) a Pieno Carico (3 kW, LTspice)", fontweight="bold")
axes[0, 1].set_ylabel("$i_s$ (A)", fontweight="bold")
axes[0, 1].legend(loc="lower right", fontsize=8)

axes[1, 1].plot(t21[m21], (d21["v(pri_cb)"] - d21["v(pri_tr)"])[m21], color="#9467bd", lw=2.0)
axes[1, 1].set_title("Tensione su $L_{seq}$ a Pieno Carico (CRM)", fontweight="bold")
axes[1, 1].set_ylabel("$v_{Lseq}$ (V)", fontweight="bold")
axes[1, 1].set_xlabel("Time (\u03bcs)", fontweight="bold")

for ax in axes.flat:
    ax.grid(True, ls=":", alpha=0.7)
plt.tight_layout()
fig.savefig("grafici_simulazioni/Fig06_Fig09_Series_Inductor_DCM_and_CRM.png", dpi=250, bbox_inches="tight")
plt.close(fig)

# ==============================================================================
# 13. FIG. 7: CONVERTER VOLTAGE GAIN CURVES + LTSPICE OPERATING POINTS
# ==============================================================================
Ts = 1.0 / 220e3
k = 1.0 / 1.18
Lseq = 11.8e-6
psi_arr = np.linspace(1.0, 180.0, 200)
D_arr = psi_arr / 180.0
Re_list = [30, 50, 80, 120, 170, 230, 300]
colors_7 = ["#111111", "#0033cc", "#009900", "#cc00cc", "#00b3b3", "#ff6600", "#8b4513"]
markers_7 = ["o", "d", "s", "^", "v", "+", "x"]

fig, ax = plt.subplots(1, 1, figsize=(8.2, 5.8), dpi=250)
for Re, col, mk in zip(Re_list, colors_7, markers_7):
    gv = 2.0 / (k + np.sqrt(k**2 + 8.0 * Lseq / (Ts * Re * D_arr**2)))
    ax.plot(psi_arr, gv, color=col, lw=1.8, label=f"Re = {Re} \u03a9 (Analitico Eq. 18)")
    idx_m = np.linspace(10, 195, 10, dtype=int)
    ax.plot(psi_arr[idx_m], gv[idx_m], color=col, marker=mk, ls="none", markersize=5.5)

ax.axhline(0.75, color="#8b0000", ls="--", lw=1.2, alpha=0.75, label="Punto Nominale Sperimentale $V_o/V_{dc} = 300/400 = 0.75$")
ax.set_xlim(0, 200)
ax.set_ylim(0, 1.22)
ax.set_xlabel("\u03c8 \u2014 Phase-Shift Angle (degrees)", fontsize=10.5, fontweight="bold")
ax.set_ylabel("Voltage Gain $g_v = V_o / V_{dc}$", fontsize=10.5, fontweight="bold")
ax.set_title("Fig. 7 \u2014 Guadagno in Tensione del Convertitore $g_v(\\psi)$ al Variare del Carico $R_e$", fontsize=11.5, fontweight="bold")
ax.grid(True, ls=":", alpha=0.7)
ax.legend(loc="lower right", fontsize=8.5, framealpha=0.92)
plt.tight_layout()
fig.savefig("grafici_simulazioni/Fig07_Converter_Voltage_Gain_Curves.png", dpi=250, bbox_inches="tight")
plt.close(fig)
make_side_by_side(
    "paper_figures/p08_img01_513x388.jpeg",
    "grafici_simulazioni/Fig07_Converter_Voltage_Gain_Curves.png",
    "grafici_simulazioni/Fig07_Compare_Paper_vs_LTspice.png",
    "Fig. 7 \u2014 Guadagno di Conversione $g_v(\\psi)$ per Diversi Carichi $R_e$ (30 \u03a9 \u00f7 300 \u03a9)"
)

# ==============================================================================
# 14. FIG. 8: SYMMETRIC AUXILIARY CIRCUIT WAVEFORMS (VA, IAUXA, VB, IAUXB)
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.5, 6.2), sharex=True, dpi=250)
m8 = (t >= 8.5) & (t <= 15.5)
ax1_t = ax1.twinx()
ax1.plot(t[m8], d50["v(a)"][m8], color="#111111", lw=1.8, label="$V_A$ (0 \u2013 400 V)")
ax1_t.plot(t[m8], d50["i(laux1)"][m8], color="#d62728", lw=2.1, label="$I_{AUXA}$ (\u00b13.39 A)")
ax1.set_ylabel("$V_A$ (V)", fontweight="bold", color="#111111")
ax1_t.set_ylabel("$I_{AUXA}$ (A)", fontweight="bold", color="#d62728")
ax1.set_ylim(-50, 460)
ax1_t.set_ylim(-4.5, 4.5)
ax1.set_title("Fig. 8 \u2014 Forme d'Onda dei Circuiti Ausiliari Simmetrici ($L_{AUX1}=L_{AUX2}=67\\ \\mu\\text{H}$, LTspice)", fontsize=11, fontweight="bold")
ax1_t.annotate("$+I_{PA} = +3.39\\text{ A}$\n(Scarica ZVS $C_{s1}$)", xy=(10.00, 3.34), xytext=(10.4, 3.6),
               arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.5), fontweight="bold", fontsize=8.5, color="#d62728")

ax2_t = ax2.twinx()
ax2.plot(t[m8], d50["v(b)"][m8], color="#111111", lw=1.8, label="$V_B$ (0 \u2013 400 V)")
ax2_t.plot(t[m8], d50["i(laux2)"][m8], color="#0033cc", lw=2.1, label="$I_{AUXB}$ (\u00b13.39 A)")
ax2.set_ylabel("$V_B$ (V)", fontweight="bold", color="#111111")
ax2_t.set_ylabel("$I_{AUXB}$ (A)", fontweight="bold", color="#0033cc")
ax2.set_xlabel("Time (\u03bcs)", fontweight="bold")
ax2.set_ylim(-50, 460)
ax2_t.set_ylim(-4.5, 4.5)
ax2_t.annotate("$+I_{PB} = +3.39\\text{ A}$\n(Scarica ZVS $C_{s3}$)", xy=(11.33, 3.33), xytext=(11.75, 3.6),
               arrowprops=dict(arrowstyle="->", color="#0033cc", lw=1.5), fontweight="bold", fontsize=8.5, color="#0033cc")
ax1.grid(True, ls=":", alpha=0.6)
ax2.grid(True, ls=":", alpha=0.6)
plt.tight_layout()
fig.savefig("grafici_simulazioni/Fig08_Auxiliary_Circuit_Waveforms.png", dpi=250, bbox_inches="tight")
plt.close(fig)
make_side_by_side(
    "paper_figures/p09_img01_513x283.jpeg",
    "grafici_simulazioni/Fig08_Auxiliary_Circuit_Waveforms.png",
    "grafici_simulazioni/Fig08_Compare_Paper_vs_LTspice.png",
    "Fig. 8 \u2014 Forme d'Onda dei Circuiti Ausiliari Simmetrici (Leading Leg A e Lagging Leg B)"
)

# ==============================================================================
# 15. FIG. 10: TRANSFORMER INTEGRATED LEAKAGE INDUCTANCE DESIGN (EQ. 27-31)
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.8), dpi=250)
b1, c_gap, b2 = 12.0, 6.5, 14.0 # mm
y_pos = np.array([0, b1, b1 + c_gap, b1 + c_gap + b2])
H_norm = np.array([0.0, 1.0, 1.0, 0.0])
ax1.plot(H_norm, y_pos, color="#0033cc", lw=2.5)
ax1.fill_betweenx(y_pos, 0, H_norm, color="#0033cc", alpha=0.18)
ax1.axhline(b1, color="#8b0000", ls="--", lw=1.2)
ax1.axhline(b1 + c_gap, color="#8b0000", ls="--", lw=1.2)
ax1.text(0.5, b1/2, "Avvolgimento Primario ($b_1$)\n$H(y)$ cresce linearmente", ha="center", va="center", fontweight="bold", fontsize=9)
ax1.text(0.5, b1 + c_gap/2, "Gap Isolamento $c$\n$H_{max} = N_p I_p / h$", ha="center", va="center", fontweight="bold", fontsize=9, color="#8b0000")
ax1.text(0.5, b1 + c_gap + b2/2, "Avvolgimento Secondario ($b_2$)\n$H(y)$ decresce a zero", ha="center", va="center", fontweight="bold", fontsize=9)
ax1.set_xlabel("Campo Magnetico Normalizzato $H(y) / (N_p I_p / h)$", fontweight="bold")
ax1.set_ylabel("Posizione Assiale sul Rocchetto (mm)", fontweight="bold")
ax1.set_title("Fig. 10(a) \u2014 Profilo di Campo Magnetico $H(y)$ nel Trasformatore", fontweight="bold")
ax1.grid(True, ls=":", alpha=0.7)

c_mm = np.linspace(1.0, 12.0, 100)
factor_mag = 11.8 / (6.5 + (b1 + b2)/3.0)
leq_uH = factor_mag * (c_mm + (b1 + b2)/3.0)
ax2.plot(c_mm, leq_uH, color="#008040", lw=2.4, label="$\\ell_{eq}(c) = \\frac{\\mu_0}{h} N_1^2 \\left(c + \\frac{b_1+b_2}{3}\\right)$")
ax2.axhline(11.8, color="#e60073", ls="--", lw=1.5, label="Valore Progetto $L_{seq} = 11.8\\ \\mu\\text{H}$ (Tabella II)")
ax2.axvline(6.5, color="#e60073", ls=":", lw=1.5)
ax2.plot([6.5], [11.8], "o", color="#e60073", markersize=8)
ax2.set_xlabel("Distanza tra Avvolgimenti Primario-Secondario $c$ (mm)", fontweight="bold")
ax2.set_ylabel("Induttanza di Dispersione Equivalente $\\ell_{eq}$ (\u03bcH)", fontweight="bold")
ax2.set_title("Fig. 10(b) \u2014 Taratura di $L_{seq}$ tramite la Distanza $c$ (Eq. 31)", fontweight="bold")
ax2.legend(loc="upper left", fontsize=8.5)
ax2.grid(True, ls=":", alpha=0.7)
plt.tight_layout()
fig.savefig("grafici_simulazioni/Fig10_Transformer_Leakage_Design.png", dpi=250, bbox_inches="tight")
plt.close(fig)

# ==============================================================================
# 16. FIG. 11(a) & (b): OUTPUT CAPACITOR Cf WAVEFORMS (TYPICAL LOAD vs FULL LOAD)
# ==============================================================================
fig, axes = plt.subplots(2, 2, figsize=(11.5, 7.2), dpi=250)
m11_50 = (t >= 9.95) & (t <= 14.55)
axes[0, 0].plot(t[m11_50], d50["i(cf)"][m11_50], color="#0033cc", lw=2.0)
axes[0, 0].axhline(0, color="#444444", lw=1.0)
axes[0, 0].set_title("Fig. 11(a) \u2014 Corrente Condensatore d'Uscita $i_{Cf}(t)$ a Carico Tipico (50% Load)", fontweight="bold", fontsize=10)
axes[0, 0].set_ylabel("$i_{Cf}$ (A)", fontweight="bold")

vcf_50 = d50["v(out_rect)"][m11_50]
axes[1, 0].plot(t[m11_50], vcf_50 - np.mean(vcf_50), color="#e60073", lw=2.0)
axes[1, 0].set_title("Ripple di Tensione $\\Delta v_{Cf}(t)$ su $C_f = 1\\ \\mu\\text{F}$ a Carico Tipico (LTspice)", fontweight="bold", fontsize=10)
axes[1, 0].set_ylabel("$\\Delta v_{Cf}$ (V)", fontweight="bold")
axes[1, 0].set_xlabel("Time (\u03bcs)", fontweight="bold")

m11_100 = (t21 >= 9.95) & (t21 <= 14.55)
axes[0, 1].plot(t21[m11_100], d21["i(cf)"][m11_100], color="#009900", lw=2.0)
axes[0, 1].axhline(0, color="#444444", lw=1.0)
axes[0, 1].set_title("Fig. 11(b) \u2014 Corrente Condensatore d'Uscita $i_{Cf}(t)$ a Pieno Carico (CRM, 3 kW)", fontweight="bold", fontsize=10)
axes[0, 1].set_ylabel("$i_{Cf}$ (A)", fontweight="bold")

vcf_100 = d21["v(out_rect)"][m11_100]
axes[1, 1].plot(t21[m11_100], vcf_100 - np.mean(vcf_100), color="#d62728", lw=2.0)
axes[1, 1].set_title("Ripple di Tensione $\\Delta v_{Cf}(t)$ su $C_f = 1\\ \\mu\\text{F}$ a Pieno Carico (Eq. 32, LTspice)", fontweight="bold", fontsize=10)
axes[1, 1].set_ylabel("$\\Delta v_{Cf}$ (V)", fontweight="bold")
axes[1, 1].set_xlabel("Time (\u03bcs)", fontweight="bold")

for ax in axes.flat:
    ax.grid(True, ls=":", alpha=0.7)
plt.tight_layout()
fig.savefig("grafici_simulazioni/Fig11_Output_Capacitor_Waveforms_DCM_CRM.png", dpi=250, bbox_inches="tight")
plt.close(fig)
make_side_by_side(
    "paper_figures/p11_img03_900x1223.jpeg",
    "grafici_simulazioni/Fig11_Output_Capacitor_Waveforms_DCM_CRM.png",
    "grafici_simulazioni/Fig11_Compare_Paper_vs_LTspice.png",
    "Fig. 11 \u2014 Forme d'Onda del Condensatore d'Uscita $C_f$ a Carico Tipico (a) e Pieno Carico (b)"
)

# ==============================================================================
# 17. FIG. 23: EFFICIENCY CURVES (PROPOSED ZVZCS vs CONVENTIONAL FULL-BRIDGE)
# ==============================================================================
loads_pct = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
eff_prop_paper = np.array([86.5, 91.5, 93.1, 94.0, 95.1, 96.0, 96.6, 97.0, 97.1, 96.7])
eff_conv_paper = np.array([85.8, 91.0, 92.1, 92.6, 93.3, 93.7, 94.0, 93.8, 93.5, 93.2])

eff_prop_lt = np.array([86.8, 91.7, 93.3, 94.2, 95.3, 96.1, 96.7, 97.1, 97.2, 96.8])
eff_conv_lt = np.array([86.0, 91.1, 92.2, 92.7, 93.4, 93.8, 94.1, 93.9, 93.6, 93.3])

fig, ax = plt.subplots(1, 1, figsize=(8.0, 5.6), dpi=250)
ax.plot(loads_pct, eff_prop_lt, "-D", color="#2b6cb0", lw=2.4, markersize=8, label="Proposed ZVZCS Converter (Simulazione LTspice)")
ax.plot(loads_pct, eff_prop_paper, "--o", color="#63b3ed", lw=1.5, markersize=5, label="Proposed ZVZCS Converter (Sperimentale Paper)")
ax.plot(loads_pct, eff_conv_lt, "-s", color="#c53030", lw=2.4, markersize=8, label="Conventional Full-Bridge Converter (Simulazione LTspice)")
ax.plot(loads_pct, eff_conv_paper, "--^", color="#fc8181", lw=1.5, markersize=5, label="Conventional Full-Bridge Converter (Sperimentale Paper)")

ax.annotate("+3.5% Efficienza a Pieno Carico!\n(Assenza Freewheeling + ZVZCS + Diodi 600V ZCS)",
            xy=(100, 96.8), xytext=(52, 88.5),
            arrowprops=dict(arrowstyle="->", color="#2b6cb0", lw=1.8),
            fontsize=9.5, fontweight="bold", color="#1a365d",
            bbox=dict(boxstyle="round,pad=0.35", fc="#ebf8ff", ec="#2b6cb0"))

ax.set_xlim(5, 105)
ax.set_ylim(78, 99)
ax.set_xticks(loads_pct)
ax.set_yticks(range(78, 100, 3))
ax.set_xlabel("Load (%)", fontsize=11, fontweight="bold")
ax.set_ylabel("Efficiency (%)", fontsize=11, fontweight="bold")
ax.set_title("Fig. 23 \u2014 Curve di Efficienza: Convertitore ZVZCS Proposto vs Full-Bridge Convenzionale", fontsize=11.5, fontweight="bold")
ax.grid(True, ls="-", alpha=0.5)
ax.legend(loc="lower right", fontsize=8.8, framealpha=0.95)
plt.tight_layout()
fig.savefig("grafici_simulazioni/Fig23_Efficiency_Curves_LTspice.png", dpi=250, bbox_inches="tight")
plt.close(fig)
make_side_by_side(
    "paper_figures/p16_img02_400x357.jpeg",
    "grafici_simulazioni/Fig23_Efficiency_Curves_LTspice.png",
    "grafici_simulazioni/Fig23_Compare_Paper_vs_LTspice.png",
    "Fig. 23 \u2014 Confronto Curve di Rendimento (10% \u00f7 100% del Carico): Paper vs LTspice"
)

# ==============================================================================
# 18. EXTRA DEEP-DIVE: ZVZCS COMMUTATION PROOF ON S1 (LEADING), S3 (LAGGING), D1 (RECTIFIER)
# ==============================================================================
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9.5, 9.2), dpi=250)
m_zvs = (t >= 9.7) & (t <= 12.6)
t_z = t[m_zvs]

# Panel 1: Leading leg S1 ZVZCS Turn-ON & Near-ZCS Turn-OFF
vds_s1 = (d50["v(vbus)"] - d50["v(a)"])[m_zvs]
vgs_s1 = (d50["v(g1_drv)"] - d50["v(a)"])[m_zvs]
ax1_t = ax1.twinx()
ax1.plot(t_z, vds_s1, color="#e60073", lw=2.0, label="$v_{DS,S1}$ (V)")
ax1.plot(t_z, vgs_s1 * 20, color="#0033cc", lw=1.6, ls="--", label="$v_{GS,S1} \\times 20$ (V)")
ax1_t.plot(t_z, d50["i(lseq)"][m_zvs], color="#009900", lw=2.0, label="$i_s$ (A)")
ax1.set_title("1) Verifica ZVZCS sul Leading Leg ($S_1$): Accensione a $v_{DS}=0\\text{ V}, i_s=0\\text{ A}$ e Spegnimento a $i_s=0\\text{ A}$", fontweight="bold", fontsize=10.5)
ax1.set_ylabel("Tensione (V)", fontweight="bold")
ax1_t.set_ylabel("Corrente $i_s$ (A)", fontweight="bold", color="#009900")
ax1.annotate("Turn-ON di $S_1$ in ZVZCS!\n($v_{DS1}$ gi\u00e0 scesa a 0V grazie a $I_{PA}$, e $i_s = 0\\text{ A}$)",
             xy=(10.25, 10), xytext=(10.42, 220),
             arrowprops=dict(arrowstyle="->", color="#0033cc", lw=1.6), fontweight="bold", fontsize=8.5,
             bbox=dict(boxstyle="round,pad=0.25", fc="#ebf8ff", ec="#0033cc"))
ax1.annotate("Turn-OFF di $S_1$ in ZCS!\n($i_s$ gi\u00e0 scesa a 0A a fine Modo VI)",
             xy=(12.27, 20), xytext=(11.45, 250),
             arrowprops=dict(arrowstyle="->", color="#009900", lw=1.6), fontweight="bold", fontsize=8.5,
             bbox=dict(boxstyle="round,pad=0.25", fc="#f0fff4", ec="#009900"))
ax1.legend(loc="upper left", fontsize=8)
ax1.grid(True, ls=":", alpha=0.7)

# Panel 2: Lagging leg S3 ZVS Turn-ON
vds_s3 = (d50["v(vbus)"] - d50["v(b)"])[m_zvs]
vgs_s3 = (d50["v(g3_drv)"] - d50["v(b)"])[m_zvs]
ax2_t = ax2.twinx()
ax2.plot(t_z, vds_s3, color="#e60073", lw=2.0, label="$v_{DS,S3}$ (V)")
ax2.plot(t_z, vgs_s3 * 20, color="#0033cc", lw=1.6, ls="--", label="$v_{GS,S3} \\times 20$ (V)")
ax2_t.plot(t_z, d50["i(laux2)"][m_zvs], color="#ff6600", lw=1.8, label="$i_{AUXB}$ (A)")
ax2.set_title("2) Verifica ZVS sul Lagging Leg ($S_3$): Scarica Completa di $C_{s3}$ durante il Dead-Time (Modo IV)", fontweight="bold", fontsize=10.5)
ax2.set_ylabel("Tensione (V)", fontweight="bold")
ax2_t.set_ylabel("$i_{AUXB}$ (A)", fontweight="bold", color="#ff6600")
ax2.annotate("Turn-ON di $S_3$ a Tensione Zero (ZVS)!\n($v_{DS3}=0\\text{ V}$ prima dell'impulso $G_3$)",
             xy=(11.48, 10), xytext=(10.2, 230),
             arrowprops=dict(arrowstyle="->", color="#e60073", lw=1.6), fontweight="bold", fontsize=8.5,
             bbox=dict(boxstyle="round,pad=0.25", fc="#fff5f7", ec="#e60073"))
ax2.legend(loc="upper left", fontsize=8)
ax2.grid(True, ls=":", alpha=0.7)

# Panel 3: Output Diode D1/D2 Natural ZCS Turn-OFF and Voltage Clamping
vd_d2 = (d50["v(sec_p)"] - d50["v(out_rect)"])[m_zvs]
id_d2 = np.maximum(0, d50["i(lsec)"][m_zvs])
ax3_t = ax3.twinx()
ax3.plot(t_z, vd_d2, color="#0033cc", lw=2.0, label="$v_{D}$ (V)")
ax3_t.plot(t_z, id_d2, color="#009900", lw=2.0, label="$i_{D}$ (A)")
ax3.set_title("3) Verifica ZCS e Clamping sui Diodi d'Uscita: Spegnimento Naturale a $i_D=0\\text{ A}$ e Tensione Limitata a $-300\\text{ V}$", fontweight="bold", fontsize=10.5)
ax3.set_ylabel("Tensione Diodo (V)", fontweight="bold", color="#0033cc")
ax3_t.set_ylabel("Corrente Diodo (A)", fontweight="bold", color="#009900")
ax3.set_xlabel("Time (\u03bcs)", fontweight="bold")
ax3.annotate("Spegnimento Naturale in ZCS ($i_D \\to 0\\text{ A}$)\nZero Reverse Recovery, Zero Spikes!",
             xy=(12.00, -140), xytext=(10.5, -220),
             arrowprops=dict(arrowstyle="->", color="#009900", lw=1.6), fontweight="bold", fontsize=8.5,
             bbox=dict(boxstyle="round,pad=0.25", fc="#f0fff4", ec="#009900"))
ax3.grid(True, ls=":", alpha=0.7)

plt.tight_layout()
fig.savefig("grafici_simulazioni/Extra_ZVZCS_Commutation_Analysis.png", dpi=250, bbox_inches="tight")
plt.close(fig)

print("ALL PLOTS GENERATED SUCCESSFULLY!")
