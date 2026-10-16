# -*- coding: utf-8 -*-
"""
Script 02: Generazione automatica dei 13 schemi LTspice (.asc) e configurazioni oscilloscopio (.plt),
esecuzione batch in LTspice (-b) ed estrazione delle misure (.meas) in measurements_summary.json.
"""
import subprocess, os, re, json, shutil

ltspice_exe = os.path.expandvars(r"%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe")
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)
os.makedirs("circuiti_ltspice", exist_ok=True)

def create_plt(plt_path, panes):
    # panes is a list of lists of trace expressions, e.g. [["V(A,B)"], ["I(Lseq)"], ["V(sec_p,out_rect)"]]
    lines = ["[Transient Analysis]", "{", f"   Npanes: {len(panes)}"]
    for idx, traces in enumerate(panes):
        lines.append("   {")
        t_str = f"      traces: {len(traces)} " + " ".join(
            [f'{{52429{i},0,"{tr}"}}' for i, tr in enumerate(traces)]
        )
        lines.append(t_str)
        lines.append("   }")
    lines.append("}")
    with open(plt_path, "w", encoding="latin1") as f:
        f.write("\n".join(lines) + "\n")

def generate_asc(path, mode="proposed", load_pct=100, psi_deg=148.0, tstop="60u", tstart="40u", title_comment=""):
    lines = ["Version 4", "SHEET 1 2400 1500"]
    def wire(x1, y1, x2, y2): lines.append(f"WIRE {x1} {y1} {x2} {y2}")
    def flag(x, y, name): lines.append(f"FLAG {x} {y} {name}")
    def sym(st, x, y, rot, name, val):
        lines.append(f"SYMBOL {st} {x} {y} {rot}")
        lines.append(f"SYMATTR InstName {name}")
        lines.append(f"SYMATTR Value {val}")
    def text(x, y, txt, size=2):
        lines.append(f"TEXT {x} {y} Left {size} {txt}")

    # 1. Input DC Bus (Vdc = 400V, Cbus = 1.4mF)
    sym("voltage", 160, 240, "R0", "Vbus", "{Vdc}")
    wire(160, 160, 160, 256)
    wire(160, 336, 160, 480)
    flag(160, 480, "0")
    flag(160, 160, "Vbus")

    sym("cap", 256, 256, "R0", "Cbus", "1.4m ic=400")
    wire(160, 160, 272, 160)
    wire(272, 160, 272, 256)
    wire(272, 320, 272, 480)
    wire(160, 480, 272, 480)

    # 2. Leading Leg Auxiliary Circuit (Ca1_H, Ca1_L, Laux1)
    sym("cap", 368, 192, "R0", "Ca1_H", "2.2u ic=200")
    wire(272, 160, 384, 160)
    wire(384, 160, 384, 192)
    wire(384, 256, 384, 304)
    flag(384, 304, "MID_A")

    sym("cap", 368, 352, "R0", "Ca1_L", "2.2u ic=200")
    wire(384, 304, 384, 352)
    wire(384, 416, 384, 480)
    wire(272, 480, 384, 480)

    if mode == "proposed":
        sym("ind", 400, 320, "R270", "Laux1", "{Laux1_val} ic=3.39 Rser=50m")
    else:
        sym("ind", 400, 320, "R270", "Laux1", "{Laux1_val} ic=6.78 Rser=50m")
    wire(384, 304, 416, 304)
    wire(496, 304, 592, 304)

    # 3. Full-Bridge Leading Leg A (S1, S2 + Cs1, Cs2)
    sym("nmos", 544, 176, "R0", "S1", "STW77N65M5")
    wire(384, 160, 592, 160)
    wire(592, 160, 592, 176)
    wire(512, 256, 544, 256)
    flag(512, 256, "G1_drv")
    wire(592, 272, 592, 304)
    flag(592, 304, "A")

    sym("cap", 640, 192, "R0", "Cs1", "{Cso}")
    wire(592, 160, 656, 160)
    wire(656, 160, 656, 192)
    wire(656, 256, 656, 304)
    wire(592, 304, 656, 304)

    sym("nmos", 544, 352, "R0", "S2", "STW77N65M5")
    wire(592, 304, 592, 352)
    wire(512, 432, 544, 432)
    flag(512, 432, "G2_drv")
    wire(592, 448, 592, 480)
    wire(384, 480, 592, 480)

    sym("cap", 640, 368, "R0", "Cs2", "{Cso}")
    wire(656, 304, 656, 368)
    wire(656, 432, 656, 480)
    wire(592, 480, 656, 480)

    # 4. Full-Bridge Lagging Leg B (S3, S4 + Cs3, Cs4)
    sym("nmos", 800, 176, "R0", "S3", "STW77N65M5")
    wire(656, 160, 848, 160)
    wire(848, 160, 848, 176)
    wire(768, 256, 800, 256)
    flag(768, 256, "G3_drv")
    wire(848, 272, 848, 336)
    flag(848, 336, "B")

    sym("cap", 896, 192, "R0", "Cs3", "{Cso}")
    wire(848, 160, 912, 160)
    wire(912, 160, 912, 192)
    wire(912, 256, 912, 336)
    wire(848, 336, 912, 336)

    sym("nmos", 800, 352, "R0", "S4", "STW77N65M5")
    wire(848, 336, 848, 352)
    wire(768, 432, 800, 432)
    flag(768, 432, "G4_drv")
    wire(848, 448, 848, 480)
    wire(656, 480, 848, 480)

    sym("cap", 896, 368, "R0", "Cs4", "{Cso}")
    wire(912, 336, 912, 368)
    wire(912, 432, 912, 480)
    wire(848, 480, 912, 480)

    # 5. Lagging Leg Auxiliary Circuit (Laux2, Ca2_H, Ca2_L)
    sym("ind", 1056, 320, "R90", "Laux2", "{Laux2_val} ic={3.39*(1-2*psi_deg/180)} Rser=50m")
    wire(912, 336, 960, 336)
    wire(1040, 336, 1072, 336)
    flag(1072, 336, "MID_B")

    sym("cap", 1056, 192, "R0", "Ca2_H", "2.2u ic=200")
    wire(912, 160, 1072, 160)
    wire(1072, 160, 1072, 192)
    wire(1072, 256, 1072, 336)

    sym("cap", 1056, 368, "R0", "Ca2_L", "2.2u ic=200")
    wire(1072, 336, 1072, 368)
    wire(1072, 432, 1072, 480)
    wire(912, 480, 1072, 480)

    # 6. Transformer Primary Tank (Cb, Lseq / Lleak, Lpri)
    flag(1168, 240, "A")
    flag(1168, 400, "B")

    sym("cap", 1200, 256, "R270", "Cb", "4.7u ic=0")
    wire(1168, 240, 1200, 240)
    wire(1264, 240, 1296, 240)
    flag(1296, 240, "pri_cb")

    sym("ind", 1296, 256, "R270", "Lseq", "{Lseq} Rser=15m")
    wire(1296, 240, 1312, 240)
    wire(1392, 240, 1440, 240)
    flag(1440, 240, "pri_tr")

    sym("ind2", 1424, 272, "R0", "Lpri", "400u")
    wire(1440, 240, 1440, 288)
    wire(1440, 368, 1440, 400)
    wire(1168, 400, 1440, 400)

    sym("ind2", 1536, 272, "R0", "Lsec", "556.96u")
    wire(1552, 240, 1552, 288)
    wire(1552, 368, 1552, 400)
    flag(1552, 240, "sec_p")
    flag(1552, 400, "sec_n")

    # 7. Output Diode Bridge (D1, D2, D3, D4)
    sym("diode", 1680, 224, "R180", "D1", "CPW0600S010B")
    wire(1664, 160, 1792, 160)
    wire(1664, 224, 1664, 240)
    wire(1552, 240, 1664, 240)

    sym("diode", 1680, 448, "R180", "D2", "CPW0600S010B")
    wire(1664, 240, 1664, 384)
    wire(1664, 448, 1664, 480)
    flag(1664, 480, "0")

    sym("diode", 1808, 224, "R180", "D3", "CPW0600S010B")
    wire(1792, 224, 1792, 400)
    wire(1552, 400, 1792, 400)

    sym("diode", 1808, 448, "R180", "D4", "CPW0600S010B")
    wire(1792, 448, 1792, 480)
    wire(1664, 480, 1792, 480)

    # 8. Output Filter (Cf, Lf, Cbat/Co, Rload)
    wire(1792, 160, 1904, 160)
    flag(1904, 160, "out_rect")

    if mode == "proposed":
        sym("cap", 1888, 288, "R0", "Cf", "1u ic=300 Rser=10m")
        sym("ind", 1920, 176, "R270", "Lf", "80u ic={Po/Vo_nom} Rser=15m")
        sym("cap", 2032, 288, "R0", "Cbat", "100u ic=300")
    else:
        # Conventional voltage-driven rectifier: no clamping capacitor Cf at diode bridge output (only stray capacitance), Co=140uF after Lf=80uH!
        sym("cap", 1888, 288, "R0", "Cstray", "1.2n ic=300 Rser=8")
        sym("ind", 1920, 176, "R270", "Lf", "80u ic={Po/Vo_nom} Rser=25m")
        sym("cap", 2032, 288, "R0", "Co", "140u ic=300")

    wire(1904, 160, 1904, 288)
    wire(1904, 352, 1904, 480)
    wire(1792, 480, 1904, 480)

    wire(1904, 160, 1936, 160)
    wire(2016, 160, 2112, 160)
    flag(2112, 160, "Vo")

    wire(2048, 160, 2048, 288)
    wire(2048, 352, 2048, 480)
    wire(1904, 480, 2048, 480)

    sym("res", 2096, 272, "R0", "Rload", "{Re}")
    wire(2112, 160, 2112, 288)
    wire(2112, 368, 2112, 480)
    wire(2048, 480, 2112, 480)

    # 9. Gate Drive Sources (Vg1..Vg4)
    sym("voltage", 320, 640, "R0", "Vg1", "PULSE(-2 15 {td} 15n 15n {Ts/2 - td} {Ts})")
    wire(320, 624, 320, 656)
    flag(320, 624, "G1_drv")
    wire(320, 736, 320, 768)
    flag(320, 768, "A")

    sym("voltage", 560, 640, "R0", "Vg2", "PULSE(-2 15 {Ts/2 + td} 15n 15n {Ts/2 - td} {Ts})")
    wire(560, 624, 560, 656)
    flag(560, 624, "G2_drv")
    wire(560, 736, 560, 768)
    flag(560, 768, "0")

    sym("voltage", 800, 640, "R0", "Vg3", "PULSE(-2 15 {t_psi + td} 15n 15n {Ts/2 - td} {Ts})")
    wire(800, 624, 800, 656)
    flag(800, 624, "G3_drv")
    wire(800, 736, 800, 768)
    flag(800, 768, "B")

    sym("voltage", 1040, 640, "R0", "Vg4", "PULSE(15 -2 {t_psi} 15n 15n {Ts/2 + td - 30n} {Ts})")
    wire(1040, 624, 1040, 656)
    flag(1040, 624, "G4_drv")
    wire(1040, 736, 1040, 768)
    flag(1040, 768, "0")

    # 10. Directives
    text(160, 830, f";{title_comment}")
    text(160, 865, "!K1 Lpri Lsec 1")
    if mode == "proposed":
        text(160, 900, "!.param Vdc=400 Vo_nom=300 fs=220k Ts={1/fs} Laux1_val=67u Laux2_val=67u Lseq=11.8u Cso=850p td=250n")
        text(160, 935, f"!.param LOAD_PCT={load_pct} psi_deg={psi_deg}")
        text(160, 970, "!.param Po={3000 * max(LOAD_PCT, 0.05) / 100} Re={Vo_nom*Vo_nom / Po} t_psi={(psi_deg/180)*(Ts/2)}")
        text(160, 1005, "!.model STW77N65M5 VDMOS(Rg=1.5 Vto=4.0 Rd=0.016 Rs=0.016 Rb=0.025 Kp=45 Cgdmax=400p Cgdmin=15p Cgs=4500p Cjo=350p Is=1e-12 Vds=650 Ron=0.032)")
        text(160, 1040, "!.model CPW0600S010B D(Is=1e-12 Rs=0.035 N=1.05 Vj=0.95 Cjo=180p M=0.45 Eg=3.26 Tt=1n Bv=650 Ibv=100u)")
    else:
        text(160, 900, "!.param Vdc=400 Vo_nom=300 fs=220k Ts={1/fs} Laux1_val=33u Laux2_val=67u Lseq=1.8u Cso=850p td=250n")
        text(160, 935, f"!.param LOAD_PCT={load_pct} psi_deg={psi_deg}")
        text(160, 970, "!.param Po={3000 * max(LOAD_PCT, 0.05) / 100} Re={Vo_nom*Vo_nom / Po} t_psi={(psi_deg/180)*(Ts/2)}")
        text(160, 1005, "!.model STW77N65M5 VDMOS(Rg=1.5 Vto=4.0 Rd=0.022 Rs=0.022 Rb=0.035 Kp=45 Cgdmax=400p Cgdmin=15p Cgs=4500p Cjo=350p Is=1e-12 Vds=650 Ron=0.044)")
        text(160, 1040, "!.model CPW0600S010B D(Is=1e-12 Rs=0.065 N=1.25 Vj=1.1 Cjo=120p M=0.45 Eg=1.11 Tt=35n Bv=1200 Ibv=100u)")

    text(160, 1075, "!.options cshunt=1p gmin=1e-9 reltol=0.005 abstol=1e-7 vntol=1e-3")
    text(160, 1110, f"!.tran 0 {tstop} {tstart} 8n uic")
    text(160, 1145, "!.meas tran Vo_avg AVG V(Vo)")
    text(160, 1175, "!.meas tran Io_avg AVG I(Rload)")
    text(160, 1205, "!.meas tran ILf_avg AVG I(Lf)")
    text(160, 1235, "!.meas tran Ip_peak MAX I(Lseq)")
    text(160, 1265, "!.meas tran Is_rms RMS I(Lseq)")
    text(160, 1295, "!.meas tran IauxA_pk MAX I(Laux1)")
    text(160, 1325, "!.meas tran IauxB_pk MAX I(Laux2)")
    text(160, 1355, "!.meas tran Vd_max MAX V(out_rect, sec_p)")
    text(160, 1385, "!.meas tran Vsec_pk MAX V(sec_p, sec_n)")
    text(160, 1415, "!.meas tran Vcf_pp PP V(out_rect)")

    with open(path, "w", encoding="latin1") as f:
        f.write("\n".join(lines) + "\n")

configs = [
    ("circuiti_ltspice/Fig14a_Conventional_10pct_Load.asc", "conventional", 10, 116.0,
     [["V(a,b)"], ["V(sec_p,sec_n)"], ["I(Laux1)"]],
     "Fig. 14(a) - Conventional Full-Bridge Converter with Asymmetric Auxiliary Circuit at 10% Load (300 W)"),
    ("circuiti_ltspice/Fig14b_Conventional_100pct_FullLoad.asc", "conventional", 100, 128.5,
     [["V(a,b)"], ["V(sec_p,sec_n)"], ["I(Laux1)"]],
     "Fig. 14(b) - Conventional Full-Bridge Converter with Asymmetric Auxiliary Circuit at Full-Load (3000 W)"),
    ("circuiti_ltspice/Fig15_Proposed_NoLoad_0W.asc", "proposed", 0, 14.0,
     [["V(a,b)"], ["V(sec_p,sec_n)"], ["V(sec_p,out_rect)"], ["I(Lseq)"]],
     "Fig. 15 - Proposed ZVZCS Full-Bridge Converter at No-Load (0 W)"),
    ("circuiti_ltspice/Fig16_Proposed_10pct_Load_300W.asc", "proposed", 10, 50.5,
     [["V(a,b)"], ["I(Lseq)"], ["V(sec_p,out_rect)"]],
     "Fig. 16 - Proposed ZVZCS Full-Bridge Converter at 10% Load (300 W)"),
    ("circuiti_ltspice/Fig17_Proposed_25pct_Load_750W.asc", "proposed", 25, 75.5,
     [["V(a,b)"], ["I(Lseq)"], ["V(sec_p,out_rect)"]],
     "Fig. 17 - Proposed ZVZCS Full-Bridge Converter at 25% Load (750 W)"),
    ("circuiti_ltspice/Fig18_Proposed_50pct_Load_1500W.asc", "proposed", 50, 105.0,
     [["V(a,b)"], ["I(Lseq)"], ["V(sec_p,out_rect)"]],
     "Fig. 18 - Proposed ZVZCS Full-Bridge Converter at 50% Load (1500 W)"),
    ("circuiti_ltspice/Fig19_Proposed_70pct_Load_2100W.asc", "proposed", 70, 124.0,
     [["V(a,b)"], ["I(Lseq)"], ["V(sec_p,out_rect)"]],
     "Fig. 19 - Proposed ZVZCS Full-Bridge Converter at 70% Load (2100 W)"),
    ("circuiti_ltspice/Fig20_Proposed_85pct_Load_2550W.asc", "proposed", 85, 135.5,
     [["V(a,b)"], ["I(Lseq)"], ["V(sec_p,out_rect)"]],
     "Fig. 20 - Proposed ZVZCS Full-Bridge Converter at 85% Load (2550 W)"),
    ("circuiti_ltspice/Fig21_Proposed_100pct_FullLoad_3000W.asc", "proposed", 100, 154.0,
     [["V(a,b)"], ["I(Lseq)"], ["V(sec_p,out_rect)"]],
     "Fig. 21 - Proposed ZVZCS Full-Bridge Converter at Full-Load (3000 W - Critical Conduction Mode)"),
    ("circuiti_ltspice/Fig22a_Proposed_AuxCurrent_LightLoad.asc", "proposed", 25, 75.5,
     [["V(a,b)", "V(sec_p,sec_n)"], ["I(Lseq)", "I(Laux1)"]],
     "Fig. 22(a) - Proposed ZVZCS Converter Auxiliary Circuit Current at Light Load (25%)"),
    ("circuiti_ltspice/Fig22b_Proposed_AuxCurrent_FullLoad.asc", "proposed", 100, 154.0,
     [["V(a,b)"], ["I(Laux1)", "I(Laux2)"]],
     "Fig. 22(b) - Proposed ZVZCS Converter Auxiliary Circuit Current at Full Load (100%)"),
]

# Also create the two main circuits in the workspace root!
configs.append((
    "Proposed_ZVZCS_FullBridge.asc", "proposed", 100, 154.0,
    [["V(a,b)"], ["I(Lseq)"], ["V(sec_p,out_rect)"], ["I(Laux1)", "I(Laux2)"]],
    "Main Circuit: Proposed ZVZCS Full-Bridge DC/DC Converter (IEEE TPEL Vol. 27, No. 6, June 2012)"
))
configs.append((
    "Conventional_FullBridge_Comparison.asc", "conventional", 100, 128.5,
    [["V(a,b)"], ["V(sec_p,sec_n)"], ["I(Laux1)", "I(Laux2)"]],
    "Comparison Circuit: Conventional Full-Bridge DC/DC Converter with Asymmetric Auxiliary Circuit (Table V)"
))

results = {}
for asc_path, mode, pct, psi, panes, comment in configs:
    generate_asc(asc_path, mode=mode, load_pct=pct, psi_deg=psi, title_comment=comment)
    plt_path = asc_path.replace(".asc", ".plt")
    create_plt(plt_path, panes)
    subprocess.run([ltspice_exe, "-b", asc_path], timeout=15, check=True)
    log_path = asc_path.replace(".asc", ".log")
    log = open(log_path, errors="replace").read()
    meas = {}
    for m in re.finditer(r"^([a-z0-9_]+):\s*.*?=([-\d\.eE\+]+)", log, re.M | re.I):
        meas[m.group(1).lower()] = float(m.group(2))
    results[os.path.basename(asc_path)] = meas
    print(f"OK: {asc_path} -> Vo={meas.get('vo_avg',0):.2f}V, ILf={meas.get('ilf_avg',0):.2f}A, Ip={meas.get('ip_peak',0):.2f}A, Vd_max={meas.get('vd_max',0):.1f}V")

with open("circuiti_ltspice/measurements_summary.json", "w") as f:
    json.dump(results, f, indent=2)

if os.path.exists("test_lt"):
    shutil.rmtree("test_lt")
