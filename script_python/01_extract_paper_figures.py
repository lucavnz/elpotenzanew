# -*- coding: utf-8 -*-
"""
Script 01: Estrazione delle 33 figure originali dal paper IEEE TPEL 35.pdf
"""
import fitz, os
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)
doc = fitz.open("35.pdf")
os.makedirs("paper_figures", exist_ok=True)
for page_idx in range(len(doc)):
    page = doc[page_idx]
    for img_idx, img in enumerate(page.get_images(full=True)):
        base = doc.extract_image(img[0])
        w, h, ext = base["width"], base["height"], base["ext"]
        fname = f"paper_figures/p{page_idx+1:02d}_img{img_idx+1:02d}_{w}x{h}.{ext}"
        open(fname, "wb").write(base["image"])
        print(fname)
