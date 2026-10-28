#!/usr/bin/env python3
"""Gerador de e-books BNSJ "Café com SESMT" — v3 "ALTA VISIBILIDADE".
Formato vertical 4:5 (leitura no celular), fundo claro, verde-limão da logo como faixa refletiva,
títulos condensados (Bebas/Oswald), checklist em cards com ícones, CTA com fotos do livro.

Uso:  python3 gerar_ebook.py temas/001_rolo_compressor.json
Tema: campo opcional "capa_imagem" (frame do vídeo, ex. assets/temas/rolo.jpg) e "ilustracao" (chave de ILUSTRACOES).
"""
import base64, io, json, os, re, sys, unicodedata
from datetime import date
from html import escape as e

import qrcode
from weasyprint import HTML

BASE = os.path.dirname(os.path.abspath(__file__))
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
W, H = 190, 237.5  # mm — proporção 4:5 (feed Instagram)


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", t.lower()).strip("_")


def qr_data_uri(url):
    qr = qrcode.QRCode(border=1, box_size=10); qr.add_data(url); qr.make(fit=True)
    img = qr.make_image(fill_color="#242424", back_color="#ffffff")
    buf = io.BytesIO(); img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def img_uri(path):
    p = os.path.join(BASE, path) if path else ""
    if not p or not os.path.exists(p):
        return None
    ext = os.path.splitext(p)[1].lower().strip(".").replace("jpg", "jpeg")
    return f"data:image/{ext};base64," + base64.b64encode(open(p, "rb").read()).decode()


def font_faces():
    f = os.path.join(BASE, "assets", "fonts")
    defs = [("Bebas", "bebas-neue-latin-400-normal.woff2", 400),
            ("Oswald", "oswald-latin-500-normal.woff2", 500),
            ("Oswald", "oswald-latin-600-normal.woff2", 600),
            ("Oswald", "oswald-latin-700-normal.woff2", 700)]
    return "".join(f"@font-face {{ font-family: '{n}'; src: url('file://{os.path.join(f, fn)}') format('woff2'); font-weight: {w}; }}\n"
                   for n, fn, w in defs if os.path.exists(os.path.join(f, fn)))


# ---------------- ícones (traço grafite) ----------------
def ic(path, size=22):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="#242424" stroke-width="1.9" '
            f'stroke-linecap="round" stroke-linejoin="round">{path}</svg>')


ICONES = {
    "pessoas": '<circle cx="9" cy="7" r="3.2"/><path d="M3 20c0-3.6 2.7-6 6-6s6 2.4 6 6"/><circle cx="17.5" cy="8.5" r="2.4"/><path d="M16 14.2c3 .2 5 2.3 5 5.8"/>',
    "equipamento": '<circle cx="12" cy="12" r="3.2"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/>',
    "area": '<path d="M12 3l-6 17h12z"/><path d="M8.2 14h7.6M9.9 9h4.2"/><path d="M3 20.5h18"/>',
    "operacao": '<path d="M4 17h3l2-6h6l2 6h3"/><circle cx="7" cy="18.5" r="2"/><circle cx="17" cy="18.5" r="2"/><path d="M9 11V6h5l1 5"/>',
    "emergencia": '<rect x="3" y="6" width="18" height="14" rx="2"/><path d="M9 6V4h6v2M12 10v6M9 13h6"/>',
    "alerta": '<path d="M12 3L2 20h20z"/><path d="M12 10v4.5M12 17.2v.1"/>',
    "carga": '<path d="M3 8l9-5 9 5v8l-9 5-9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/>',
    "gancho": '<path d="M12 2v6"/><circle cx="12" cy="9.5" r="1.6"/><path d="M12 11v3a3.5 3.5 0 1 1-3.5 3.5"/><path d="M9 2h6"/>',
    "clima": '<path d="M7 17a4 4 0 0 1 .5-8 5.5 5.5 0 0 1 10.5 2 3.5 3.5 0 0 1-.5 7z"/><path d="M8 21l1-2M12 21l1-2M16 21l1-2"/>',
}
ICONE_GRUPO = {"pessoas": "pessoas", "equipamento": "equipamento", "área e circulação": "area",
               "operação": "operacao", "proteção e emergência": "emergencia"}

# ---------------- ilustrações de capa (vetor próprio) ----------------
ILUSTRACOES = {
    "serra_fita": """
<svg viewBox="0 0 420 300" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="210" cy="288" rx="190" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <path d="M10 282 h400" stroke-width="4"/>
  <rect x="150" y="20" width="130" height="80" rx="14" fill="#ffffff"/>
  <circle cx="215" cy="60" r="26" stroke-width="3" opacity=".35"/>
  <rect x="150" y="196" width="130" height="86" rx="10" fill="#ffffff"/>
  <circle cx="215" cy="236" r="26" stroke-width="3" opacity=".35"/>
  <rect x="262" y="100" width="18" height="96" fill="#ffffff"/>
  <path d="M206 100 v96" stroke="#C1FF72" stroke-width="7"/>
  <rect x="196" y="100" width="20" height="44" rx="3" fill="#ffffff"/>
  <path d="M60 182 h300" stroke-width="7"/>
  <rect x="60" y="174" width="300" height="16" rx="3" fill="#ffffff"/>
  <path d="M96 174 v-34 h30 v34" fill="#ffffff"/>
  <path d="M248 142 h56 a22 22 0 0 1 22 22 v10 h-78 z" fill="#C1FF72"/>
  <path d="M300 142 l40 -60 l22 0" stroke-width="7"/>
  <rect x="354" y="72" width="22" height="22" rx="4" fill="#ffffff"/>
  <path d="M120 140 q30 -14 64 -2 q10 18 0 36 h-64 z" fill="#ffffff"/>
  <path d="M136 152 q18 -6 34 0" stroke-width="3" opacity=".5"/>
  <path d="M232 110 l-6 -8 M240 120 l10 -2 M226 128 l-10 4" stroke="#C1FF72" stroke-width="5"/>
</svg>""",
    "contratacao": """
<svg viewBox="0 0 420 300" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="210" cy="288" rx="190" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <path d="M10 282 h400" stroke-width="4"/>
  <rect x="60" y="40" width="170" height="236" rx="10" fill="#ffffff"/>
  <rect x="110" y="26" width="70" height="30" rx="8" fill="#C1FF72"/>
  <circle cx="145" cy="41" r="5" fill="#242424"/>
  <rect x="82" y="84" width="22" height="22" rx="4" fill="#C1FF72"/><path d="M86 95 l6 6 l12 -14" stroke-width="5"/>
  <path d="M118 95 h88" stroke-width="4" opacity=".6"/>
  <rect x="82" y="128" width="22" height="22" rx="4" fill="#C1FF72"/><path d="M86 139 l6 6 l12 -14" stroke-width="5"/>
  <path d="M118 139 h76" stroke-width="4" opacity=".6"/>
  <rect x="82" y="172" width="22" height="22" rx="4" fill="#C1FF72"/><path d="M86 183 l6 6 l12 -14" stroke-width="5"/>
  <path d="M118 183 h84" stroke-width="4" opacity=".6"/>
  <rect x="82" y="216" width="22" height="22" rx="4" fill="#ffffff"/>
  <path d="M118 227 h60" stroke-width="4" opacity=".6"/>
  <path d="M262 236 a62 62 0 0 1 124 0 z" fill="#C1FF72"/>
  <path d="M312 176 v-8 h24 v8" fill="#ffffff"/>
  <path d="M324 176 v58" stroke-width="4"/>
  <path d="M246 236 h156 v14 h-156 z" fill="#ffffff"/>
  <path d="M268 140 l-14 -18 M300 124 l2 -24 M240 166 l-22 -8" stroke="#C1FF72" stroke-width="6"/>
</svg>""",
    "bloqueio": """
<svg viewBox="0 0 420 300" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="210" cy="288" rx="190" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <path d="M10 282 h400" stroke-width="4"/>
  <rect x="70" y="30" width="190" height="252" rx="8" fill="#ffffff"/>
  <path d="M70 70 h190" stroke-width="3" opacity=".35"/>
  <path d="M96 50 h40 M150 50 h12" stroke-width="4"/>
  <rect x="120" y="96" width="90" height="110" rx="10" fill="#C1FF72"/>
  <rect x="150" y="116" width="30" height="58" rx="6" fill="#ffffff"/>
  <path d="M165 128 v20" stroke-width="7"/>
  <path d="M120 186 h-4 M210 186 h4" stroke-width="3"/>
  <path d="M196 186 h64 v26 h-40" stroke-width="6"/>
  <circle cx="232" cy="199" r="5" fill="#242424"/>
  <path d="M262 186 q30 -2 30 30 v20" stroke-width="7"/>
  <rect x="268" y="230" width="48" height="40" rx="6" fill="#C1FF72"/>
  <circle cx="292" cy="246" r="5" fill="#242424"/><path d="M292 250 v10" stroke-width="4"/>
  <path d="M316 214 l40 18 l-14 54 l-46 -20 z" fill="#ffffff"/>
  <circle cx="322" cy="226" r="4"/>
  <path d="M318 244 l22 9 M314 256 l20 9" stroke-width="3" opacity=".6"/>
  <path d="M352 120 l18 -18 M370 140 h24 M344 100 v-24" stroke="#C1FF72" stroke-width="6"/>
  <path d="M370 210 l-20 -10" stroke-width="3" opacity=".5"/>
</svg>""",
    "engrenagem": """
<svg viewBox="0 0 420 300" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="210" cy="288" rx="190" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <g transform="translate(150,150)">
    <path d="M-14 -92 h28 l6 22 a72 72 0 0 1 20 8 l20 -12 l20 20 l-12 20 a72 72 0 0 1 8 20 l22 6 v28 l-22 6 a72 72 0 0 1 -8 20 l12 20 l-20 20 l-20 -12 a72 72 0 0 1 -20 8 l-6 22 h-28 l-6 -22 a72 72 0 0 1 -20 -8 l-20 12 l-20 -20 l12 -20 a72 72 0 0 1 -8 -20 l-22 -6 v-28 l22 -6 a72 72 0 0 1 8 -20 l-12 -20 l20 -20 l20 12 a72 72 0 0 1 20 -8 z" fill="#C1FF72"/>
    <circle r="30" fill="#ffffff"/><circle r="10" fill="#242424"/>
  </g>
  <g transform="translate(292,118)">
    <path d="M-10 -58 h20 l4 14 a46 46 0 0 1 13 5 l13 -8 l14 14 l-8 13 a46 46 0 0 1 5 13 l14 4 v20 l-14 4 a46 46 0 0 1 -5 13 l8 13 l-14 14 l-13 -8 a46 46 0 0 1 -13 5 l-4 14 h-20 l-4 -14 a46 46 0 0 1 -13 -5 l-13 8 l-14 -14 l8 -13 a46 46 0 0 1 -5 -13 l-14 -4 v-20 l14 -4 a46 46 0 0 1 5 -13 l-8 -13 l14 -14 l13 8 a46 46 0 0 1 13 -5 z" fill="#ffffff"/>
    <circle r="16" fill="#242424"/>
  </g>
  <path d="M300 214 q18 -6 40 4 l36 18 q10 6 4 14 q-6 6 -16 2 l-14 -6 l6 14 q4 10 -6 12 q-8 2 -12 -8 l-10 -22" fill="#ffffff"/>
  <path d="M352 196 l14 -20 M372 210 l22 -10 M332 188 l2 -24" stroke="#C1FF72" stroke-width="6"/>
</svg>""",
    "altura": """
<svg viewBox="0 0 420 300" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="210" cy="288" rx="190" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <path d="M10 282 h400" stroke-width="4"/>
  <path d="M40 60 h340" stroke-width="10"/>
  <path d="M70 60 v222 M350 60 v222" stroke-width="8"/>
  <rect x="62" y="44" width="16" height="16" fill="#C1FF72"/>
  <path d="M210 60 v40" stroke-width="4"/>
  <path d="M210 100 q-4 20 -2 30" stroke="#C1FF72" stroke-width="6"/>
  <circle cx="210" cy="150" r="17" fill="#ffffff"/>
  <path d="M190 140 a20 16 0 0 1 40 0 z" fill="#C1FF72"/>
  <path d="M196 170 h28 l6 58 h-40 z" fill="#C1FF72"/>
  <path d="M196 176 l-26 34 M224 176 l26 34"/>
  <path d="M198 228 l-8 44 M222 228 l8 44"/>
  <path d="M200 182 l20 26 M220 182 l-20 26" stroke-width="3"/>
  <path d="M120 200 h40 M260 200 h40" stroke-width="3" opacity=".3"/>
</svg>""",
    "extintor": """
<svg viewBox="0 0 420 300" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="210" cy="288" rx="190" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <path d="M10 282 h400" stroke-width="4"/>
  <rect x="150" y="96" width="92" height="180" rx="40" fill="#C1FF72"/>
  <rect x="150" y="150" width="92" height="56" fill="#ffffff"/>
  <path d="M174 170 h44 M174 188 h30" stroke-width="4"/>
  <rect x="180" y="66" width="32" height="30" rx="4" fill="#ffffff"/>
  <path d="M172 60 h50 l20 -14" stroke-width="7"/>
  <path d="M212 76 q60 0 70 60 q6 40 40 50" stroke-width="7"/>
  <path d="M318 180 l26 6 l-8 18 z" fill="#242424"/>
  <path d="M352 168 q14 -20 0 -40 q22 12 18 40 q14 -10 10 -30 q20 24 0 50 q-14 14 -28 -20 z" fill="#ffffff"/>
  <path d="M362 200 q-6 -16 6 -26 q4 14 14 18" stroke-width="3"/>
</svg>""",
    "tambor": """
<svg viewBox="0 0 420 300" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="210" cy="288" rx="190" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <path d="M10 282 h400" stroke-width="4"/>
  <path d="M110 92 v170 a70 18 0 0 0 140 0 v-170" fill="#ffffff"/>
  <ellipse cx="180" cy="92" rx="70" ry="18" fill="#ffffff"/>
  <path d="M110 148 a70 18 0 0 0 140 0 M110 206 a70 18 0 0 0 140 0" stroke-width="4"/>
  <ellipse cx="208" cy="90" rx="10" ry="4" fill="#242424"/>
  <path d="M138 160 l14 -26 l14 26 z" fill="#C1FF72" stroke-width="3"/>
  <path d="M152 144 v8 M152 156 v1" stroke-width="3"/>
  <path d="M290 160 l40 -40" stroke-width="10"/>
  <path d="M330 120 l20 -20" stroke-width="5"/>
  <path d="M250 182 l26 -14 M250 196 l34 -2 M248 170 l18 -22" stroke="#C1FF72" stroke-width="6"/>
  <path d="M200 40 q-10 -18 4 -30 M224 44 q10 -16 -2 -32" stroke-width="4" opacity=".55"/>
</svg>""",
    "vala": """
<svg viewBox="0 0 420 300" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="210" cy="288" rx="190" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <path d="M10 120 h140 v160 h120 v-160 h140 v162 h-400 z" fill="#ffffff"/>
  <path d="M30 150 l20 6 M70 190 l24 -4 M40 236 l18 8 M330 160 l22 4 M360 206 l-20 6 M318 246 l26 -2" stroke-width="3" opacity=".35"/>
  <path d="M150 120 v160 M270 120 v160" stroke-width="5"/>
  <rect x="158" y="128" width="12" height="146" fill="#C1FF72"/><rect x="250" y="128" width="12" height="146" fill="#C1FF72"/>
  <path d="M170 168 h80 M170 230 h80" stroke-width="9"/>
  <path d="M196 140 v134 M224 140 v134" stroke-width="4"/>
  <path d="M196 152 h28 M196 182 h28 M196 212 h28 M196 242 h28" stroke-width="4"/>
  <path d="M10 120 h140" stroke-width="5"/><path d="M270 120 h140" stroke-width="5"/>
  <path d="M150 120 h-46 M270 120 h46" stroke="#C1FF72" stroke-width="9" stroke-dasharray="8 8"/>
  <path d="M320 120 q30 -46 70 0 z" fill="#C1FF72"/>
  <path d="M20 120 v-46 M20 74 l14 -2 M60 120 v-46 M60 74 l14 -2" stroke-width="4"/>
  <path d="M20 86 h40 M20 104 h40" stroke="#C1FF72" stroke-width="6"/>
  <path d="M114 134 l8 18 l-6 12 l10 20" stroke-width="3"/>
  <path d="M120 40 l20 34 h-40 z" fill="#C1FF72"/><path d="M120 52 v10 M120 67 v1" stroke-width="4"/>
</svg>""",
    "escavadeira": """
<svg viewBox="0 0 420 300" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="210" cy="288" rx="190" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <path d="M10 282 h400" stroke-width="4"/>
  <rect x="40" y="226" width="200" height="40" rx="20" fill="#242424"/>
  <circle cx="70" cy="246" r="9" fill="#C1FF72" stroke="#C1FF72"/><circle cx="210" cy="246" r="9" fill="#C1FF72" stroke="#C1FF72"/>
  <path d="M60 226 v-60 h150 v60" fill="#C1FF72"/>
  <path d="M60 166 h56 v-56 h-40 l-16 20 z" fill="#ffffff"/>
  <rect x="78" y="122" width="30" height="30" rx="3" fill="#eaf7d6"/>
  <path d="M200 176 l90 -90 l20 14 l-86 92" fill="#C1FF72"/>
  <path d="M296 92 l56 90" stroke-width="16"/>
  <path d="M352 182 l-36 6 l10 40 l46 -20 z" fill="#ffffff"/>
  <path d="M330 228 l4 10 M346 224 l6 10 M362 216 l8 8" stroke-width="3"/>
  <path d="M130 40 a110 110 0 0 1 150 0" stroke="#C1FF72" stroke-width="5" stroke-dasharray="10 10"/>
  <path d="M272 30 l10 12 l-16 4" stroke="#C1FF72" stroke-width="5"/>
</svg>""",
    "estante": """
<svg viewBox="0 0 420 300" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="210" cy="288" rx="190" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <path d="M10 282 h400" stroke-width="4"/>
  <path d="M60 30 v252 M220 30 v252 M380 30 v252" stroke-width="8"/>
  <path d="M60 110 h320 M60 196 h320" stroke-width="10" stroke="#C1FF72"/>
  <path d="M60 110 h320 M60 196 h320" stroke-width="3"/>
  <rect x="80" y="56" width="56" height="50" fill="#ffffff"/><rect x="140" y="70" width="60" height="36" fill="#ffffff"/>
  <rect x="80" y="142" width="120" height="50" fill="#ffffff"/>
  <path d="M80 142 l120 50 M200 142 l-120 50" stroke-width="2" opacity=".3"/>
  <rect x="240" y="146" width="60" height="46" fill="#ffffff"/>
  <g transform="rotate(14 330 90)"><rect x="300" y="50" width="62" height="56" fill="#ffffff"/></g>
  <path d="M244 230 h56 M244 250 h56" stroke-width="3" opacity=".4"/>
  <path d="M352 120 l10 14 M370 112 l18 6 M336 124 l-4 16" stroke="#C1FF72" stroke-width="6"/>
  <path d="M228 202 l-12 -10 M226 216 l-18 -2" stroke="#242424" stroke-width="3" opacity=".6"/>
</svg>""",
    "escada_movel": """
<svg viewBox="0 0 420 300" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="210" cy="288" rx="190" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <path d="M10 282 h400" stroke-width="4"/>
  <path d="M40 30 v252 M150 30 v252" stroke-width="8"/>
  <path d="M40 96 h110 M40 166 h110 M40 236 h110" stroke-width="10" stroke="#C1FF72"/>
  <path d="M40 96 h110 M40 166 h110 M40 236 h110" stroke-width="3"/>
  <rect x="52" y="60" width="38" height="32" fill="#ffffff"/><rect x="96" y="68" width="42" height="24" fill="#ffffff"/>
  <rect x="52" y="130" width="86" height="32" fill="#ffffff"/>
  <rect x="58" y="200" width="34" height="32" fill="#ffffff"/><rect x="98" y="206" width="40" height="26" fill="#ffffff"/>
  <path d="M196 262 l34 -200 M300 262 l-20 -200" stroke-width="7"/>
  <path d="M226 82 h56" stroke-width="10" stroke="#C1FF72"/>
  <path d="M226 82 h56" stroke-width="3"/>
  <path d="M222 106 l-6 -40 M286 106 l2 -40" stroke-width="4"/>
  <path d="M220 104 h68" stroke-width="4"/>
  <path d="M226 132 h56 M222 162 h62 M216 192 h70 M210 222 h80" stroke-width="5"/>
  <path d="M196 262 h104" stroke-width="5"/>
  <circle cx="200" cy="272" r="9" fill="#ffffff"/><circle cx="296" cy="272" r="9" fill="#ffffff"/>
  <path d="M186 262 h28 M282 262 h28" stroke="#C1FF72" stroke-width="7"/>
  <path d="M340 282 l14 -50 h12 l14 50 z" fill="#C1FF72"/>
  <path d="M346 262 h28" stroke-width="4" stroke="#ffffff"/>
  <path d="M334 282 h52" stroke-width="5"/>
  <path d="M164 46 l16 10 M168 30 l18 2" stroke="#C1FF72" stroke-width="6"/>
</svg>""",
    "guindaste": """
<svg viewBox="0 0 420 300" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="200" cy="288" rx="190" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <path d="M10 282 h400" stroke-width="4"/>
  <path d="M40 232 h170 v-34 h-60 l-12 -26 h-58 l-14 26 h-26 z" fill="#ffffff"/>
  <rect x="96" y="178" width="42" height="26" rx="3" fill="#eaf7d6"/>
  <path d="M30 232 h10 M210 232 h12" />
  <path d="M28 236 v40 M222 236 v40" stroke-width="6"/>
  <path d="M14 278 h28 M208 278 h28" stroke-width="7"/>
  <circle cx="72" cy="248" r="20" fill="#242424"/><circle cx="72" cy="248" r="8" fill="#C1FF72" stroke="#C1FF72"/>
  <circle cx="178" cy="248" r="20" fill="#242424"/><circle cx="178" cy="248" r="8" fill="#C1FF72" stroke="#C1FF72"/>
  <path d="M168 196 L340 34 l14 12 L184 206 z" fill="#C1FF72"/>
  <path d="M190 196 l-6 -34 l30 -6" />
  <path d="M347 40 V150" stroke-width="3"/>
  <path d="M340 150 h14 v8 a7 7 0 1 1 -14 0" stroke-width="4"/>
  <path d="M347 166 l-28 30 M347 166 l28 30" stroke-width="3"/>
  <rect x="306" y="196" width="82" height="52" rx="3" fill="#ffffff"/>
  <path d="M306 214 h82 M306 232 h82" stroke-width="3" opacity=".5"/>
  <path d="M290 262 l-10 -12 M404 262 l10 -12" stroke="#C1FF72" stroke-width="5"/>
</svg>""",
    "caminhao": """
<svg viewBox="0 0 420 300" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="210" cy="288" rx="190" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <path d="M10 282 h400" stroke-width="4"/>
  <rect x="150" y="70" width="210" height="150" rx="4" fill="#ffffff"/>
  <path d="M150 104 h210 M150 186 h210" stroke-width="3" opacity=".35"/>
  <path d="M360 120 h38 l12 40 v60 h-50 z" fill="#C1FF72"/>
  <rect x="368" y="130" width="26" height="26" rx="3" fill="#eaf7d6"/>
  <rect x="140" y="220" width="272" height="16" fill="#242424"/>
  <circle cx="200" cy="248" r="22" fill="#242424"/><circle cx="200" cy="248" r="9" fill="#C1FF72" stroke="#C1FF72"/>
  <circle cx="370" cy="248" r="22" fill="#242424"/><circle cx="370" cy="248" r="9" fill="#C1FF72" stroke="#C1FF72"/>
  <path d="M136 150 l-26 0 M120 138 l-14 12 l14 12" stroke="#C1FF72" stroke-width="7"/>
  <circle cx="62" cy="168" r="14" fill="#ffffff"/>
  <path d="M50 184 h24 l4 50 h-32 z" fill="#C1FF72"/>
  <path d="M52 236 l-6 40 M72 236 l6 40"/>
  <path d="M74 192 l22 -22 M50 192 l-14 26" />
  <path d="M30 40 l20 34 h-40 z" fill="#C1FF72" stroke-width="4"/>
  <path d="M30 54 v8 M30 67 v1" stroke-width="4"/>
  <path d="M96 120 a40 40 0 0 1 0 60" stroke="#242424" stroke-width="3" stroke-dasharray="6 8" opacity=".5"/>
</svg>""",
    "esmerilhadeira": """
<svg viewBox="0 0 420 300" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="210" cy="288" rx="190" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <path d="M10 282 h400" stroke-width="4"/>
  <rect x="40" y="236" width="340" height="30" fill="#ffffff"/>
  <path d="M40 251 h340" stroke-width="3" opacity=".3"/>
  <rect x="150" y="96" width="200" height="56" rx="26" fill="#ffffff"/>
  <path d="M300 106 v36 M314 106 v36 M328 106 v36" stroke-width="3" opacity=".45"/>
  <rect x="120" y="100" width="44" height="48" rx="6" fill="#C1FF72"/>
  <path d="M150 96 l-6 -46 h-26" stroke-width="10"/>
  <circle cx="132" cy="196" r="50" fill="#C1FF72"/>
  <circle cx="132" cy="196" r="10" fill="#242424"/>
  <path d="M82 196 a50 50 0 0 1 100 0" fill="#ffffff"/>
  <path d="M132 148 v-0" />
  <path d="M152 148 l-6 38" stroke-width="6"/>
  <path d="M176 236 l40 -26 M184 240 l56 -10 M170 232 l24 -42 M190 244 l64 6" stroke="#C1FF72" stroke-width="5"/>
  <path d="M206 220 l6 -4 M232 226 l8 -2 M240 250 l8 2" stroke="#242424" stroke-width="3"/>
</svg>""",
    "primeiros_socorros": """
<svg viewBox="0 0 420 300" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="210" cy="288" rx="190" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <path d="M10 282 h400" stroke-width="4"/>
  <rect x="60" y="130" width="200" height="146" rx="12" fill="#ffffff"/>
  <path d="M126 130 v-24 h68 v24" stroke-width="7"/>
  <rect x="134" y="168" width="52" height="72" rx="4" fill="#C1FF72"/>
  <rect x="124" y="178" width="72" height="52" rx="4" fill="#C1FF72"/>
  <path d="M60 156 h200" stroke-width="3" opacity=".35"/>
  <rect x="290" y="70" width="90" height="150" rx="14" fill="#ffffff"/>
  <rect x="302" y="86" width="66" height="102" rx="4" fill="#eaf7d6"/>
  <path d="M316 116 l14 0 l6 -14 l8 30 l6 -16 h14" stroke-width="4"/>
  <path d="M322 160 h26" stroke-width="4"/>
  <path d="M335 204 v0" stroke-width="8"/>
  <path d="M310 40 q14 -20 26 0 q12 -20 26 0" stroke="#C1FF72" stroke-width="6"/>
</svg>""",
    "rolo": """
<svg viewBox="0 0 420 260" width="100%" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#242424" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="210" cy="246" rx="200" ry="7" fill="#242424" opacity=".08" stroke="none"/>
  <path d="M70 160 h230 l18 -46 h-150 l-14 46" fill="#ffffff"/>
  <rect x="150" y="96" width="150" height="66" rx="8" fill="#C1FF72"/>
  <path d="M160 96 v-62 h112 v62" fill="#ffffff"/>
  <path d="M152 34 h128" stroke-width="8"/>
  <rect x="176" y="48" width="78" height="40" rx="4" fill="#eaf7d6"/>
  <path d="M300 126 h42 v40 h-30" fill="#ffffff"/>
  <path d="M342 118 v-14 h10"/>
  <circle cx="110" cy="190" r="54" fill="#ffffff"/>
  <circle cx="110" cy="190" r="40" fill="#C1FF72"/>
  <path d="M74 190 h72 M110 154 v72" stroke-width="3" opacity=".35"/>
  <path d="M70 160 h-14 v34 h14"/>
  <circle cx="316" cy="204" r="38" fill="#242424"/>
  <circle cx="316" cy="204" r="15" fill="#C1FF72" stroke="#C1FF72"/>
  <path d="M10 244 h400" stroke-width="4"/>
  <g stroke="#C1FF72" stroke-width="5"><path d="M372 70 l26 -12 M376 88 h28 M372 106 l26 12"/></g>
</svg>""",
}

CSS = f"""
@page {{ size: {W}mm {H}mm; margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: 'Inter', sans-serif; color: #242424; font-size: 9.6pt; line-height: 1.5; }}
.page {{ width: {W}mm; height: {H}mm; position: relative; overflow: hidden; page-break-after: always; background: #F6F7F3; }}
.page:last-child {{ page-break-after: auto; }}
.hl {{ background: linear-gradient(transparent 55%, #C1FF72 55%, #C1FF72 92%, transparent 92%); padding: 0 .6mm; }}
/* faixa refletiva (alta visibilidade) */
.tape {{ position: absolute; left: 0; right: 0; height: 6mm;
  background: repeating-linear-gradient(-45deg, #C1FF72 0, #C1FF72 7mm, #242424 7mm, #242424 8.4mm, #dfe3d6 8.4mm, #dfe3d6 11mm, #242424 11mm, #242424 12.4mm); }}
.tape.v {{ width: 6mm; height: auto; top: 0; bottom: 0; left: auto; right: 0; }}
.logo {{ height: 11mm; }}
.selo-w {{ display: flex; align-items: center; gap: 3mm; white-space: nowrap; }} .selo {{ white-space: nowrap; }} .selo-w .simb {{ height: 16mm; width: 16mm; object-fit: cover; border-radius: 3mm; border: .6mm solid #C1FF72; }}
.foot .fm {{ display: flex; align-items: center; gap: 2mm; white-space: nowrap; }} .foot .simb {{ height: 7mm; width: 7mm; object-fit: cover; border-radius: 1.4mm; }}

/* ---------- rodapé ---------- */
.foot {{ position: absolute; left: 12mm; right: 12mm; bottom: 5mm; display: flex; justify-content: space-between; align-items: center;
  font-family: 'Oswald', sans-serif; font-size: 7.4pt; letter-spacing: .14em; text-transform: uppercase; color: #8a8f80; border-top: .3mm solid #d9dccf; padding-top: 3mm; }}
.foot img {{ height: 7.5mm; }}
.foot .pg {{ font-family: 'Bebas', sans-serif; font-size: 14pt; color: #242424; letter-spacing: .04em; }}
.foot .pg b {{ background: #C1FF72; padding: 0 1.6mm; font-weight: 400; }}

/* ---------- CAPA ---------- */
.cover-top {{ padding: 10mm 12mm 0; display: flex; justify-content: space-between; align-items: center; }}
.selo {{ font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 7.6pt; letter-spacing: .18em; text-transform: uppercase; text-align: right; color: #6b7062; line-height: 1.45; }}
.selo b {{ display: block; font-family: 'Bebas', sans-serif; font-weight: 400; font-size: 17pt; letter-spacing: .05em; color: #242424; line-height: 1; }}
.cover-main {{ padding: 4mm 12mm 0; display: flex; gap: 4mm; align-items: flex-end; }}
.cover-txt {{ width: 112mm; }}
.chip {{ display: inline-block; background: #242424; color: #C1FF72; font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 7.6pt; letter-spacing: .16em; text-transform: uppercase; padding: 1.2mm 3mm; border-radius: 10mm; }}
h1 {{ font-family: 'Bebas', 'Oswald', sans-serif; font-weight: 400; font-size: 46pt; line-height: .9; margin: 3mm 0 2.5mm; letter-spacing: .005em; }}
h1 .hl {{ background: linear-gradient(transparent 58%, #C1FF72 58%, #C1FF72 90%, transparent 90%); }}
.cover-sub {{ font-size: 10.2pt; line-height: 1.42; color: #43473c; margin: 0; }}
.cover-art {{ width: 50mm; padding-bottom: 2mm; }}
.cover-art img {{ width: 66mm; height: 66mm; object-fit: cover; border-radius: 4mm; border: 1.2mm solid #C1FF72; }}
.ed-big {{ position: absolute; right: 12mm; top: 30mm; font-family: 'Bebas', sans-serif; font-size: 26pt; color: #242424; background: #C1FF72; padding: .8mm 2.6mm 0; border-radius: 2mm; }}

.intro {{ margin: 5mm 12mm 0; background: #fff; border-radius: 4mm; padding: 4mm 5mm; display: flex; gap: 6mm; box-shadow: 0 .6mm 2mm rgba(0,0,0,.06); }}
.intro .a {{ width: 86mm; }}
.intro .b {{ flex: 1; }}
.lbl {{ font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 7.8pt; letter-spacing: .18em; text-transform: uppercase; color: #5f8f1c; margin-bottom: 1mm; }}
h2 {{ font-family: 'Bebas', 'Oswald', sans-serif; font-weight: 400; font-size: 21pt; line-height: 1; margin: 0 0 2mm; letter-spacing: .02em; }}
.intro p {{ margin: 0; font-size: 8.6pt; line-height: 1.5; color: #3a3d34; }}
.risco {{ display: flex; gap: 2mm; align-items: flex-start; padding: .9mm 0; border-bottom: .25mm solid #eceee6; }}
.risco:last-child {{ border-bottom: 0; }}
.risco .n {{ flex: 0 0 6mm; height: 6mm; border-radius: 50%; background: #242424; color: #C1FF72; font-family: 'Bebas', sans-serif; font-size: 11pt; text-align: center; line-height: 6.4mm; }}
.risco b {{ font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 9pt; text-transform: uppercase; letter-spacing: .03em; }}
.risco span {{ display: block; font-size: 7.9pt; line-height: 1.35; color: #5a5e52; }}

.nrs {{ margin: 4.5mm 12mm 0; }}
.nrs-g {{ display: flex; gap: 2.6mm; margin-top: 1.5mm; }}
.nrc {{ flex: 1; background: #242424; color: #fff; border-radius: 3mm; padding: 3mm 3mm 3.2mm; position: relative; overflow: hidden; }}
.nrc::before {{ content: ""; position: absolute; top: 0; left: 0; right: 0; height: 1.4mm; background: #C1FF72; }}
.nrc .nr {{ font-family: 'Bebas', sans-serif; font-size: 20pt; color: #C1FF72; line-height: 1; margin-top: .8mm; }}
.nrc .t {{ font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 7.6pt; text-transform: uppercase; letter-spacing: .06em; margin: .6mm 0 1mm; }}
.nrc p {{ margin: 0; font-size: 6.9pt; line-height: 1.34; color: #cfd2c8; }}

/* ---------- CHECKLIST ---------- */
.ck-head {{ padding: 9mm 14mm 0 12mm; display: flex; justify-content: space-between; align-items: flex-end; }}
.ck-head h2 {{ font-size: 30pt; line-height: .9; margin: 1mm 0 0; }}
.ck-head .cnt {{ text-align: center; background: #242424; color: #C1FF72; border-radius: 3mm; padding: 1.5mm 4mm 1mm; font-family: 'Oswald', sans-serif; font-size: 6.8pt; letter-spacing: .14em; text-transform: uppercase; }}
.ck-head .cnt b {{ display: block; font-family: 'Bebas', sans-serif; font-weight: 400; font-size: 26pt; line-height: .95; letter-spacing: 0; }}
.ck-sub {{ margin: 2mm 12mm 0; font-size: 8.4pt; color: #5a5e52; }}
.ck {{ padding: 3mm 12mm 0; display: flex; gap: 4mm; }} .ck .col {{ flex: 1; }}
.card {{ background: #fff; border-radius: 3.5mm; padding: 2.4mm 3.2mm 1mm; margin-bottom: 2.6mm; box-shadow: 0 .5mm 1.6mm rgba(0,0,0,.06); }}
.card-h {{ display: flex; align-items: center; gap: 2mm; margin-bottom: 1mm; }}
.card-h .ico {{ width: 7.5mm; height: 7.5mm; border-radius: 2.4mm; background: #C1FF72; display: flex; align-items: center; justify-content: center; }}
.card-h .ico svg {{ width: 5.4mm; height: 5.4mm; }}
.card-h b {{ font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 9.4pt; text-transform: uppercase; letter-spacing: .08em; }}
.item {{ display: flex; gap: 2mm; padding: .9mm 0; border-top: .25mm solid #eef0e8; }}
.box {{ flex: 0 0 3.8mm; height: 3.8mm; border: .45mm solid #242424; border-radius: .8mm; margin-top: .45mm; }}
.num {{ flex: 0 0 5.2mm; font-family: 'Bebas', sans-serif; font-size: 12pt; line-height: 1.05; color: #5f8f1c; }}
.txt {{ font-size: 7.7pt; line-height: 1.34; color: #2e3129; }}
.stop {{ margin: .5mm 12mm 0; background: #242424; border-radius: 3.5mm; color: #fff; display: flex; gap: 4mm; align-items: center; padding: 3.4mm 4.5mm; position: relative; overflow: hidden; }}
.stop .oct {{ flex: 0 0 13mm; height: 13mm; background: #D92D20; color: #fff; font-family: 'Bebas', sans-serif; font-size: 14pt; text-align: center; line-height: 13.6mm; letter-spacing: .04em;
  border-radius: 50%; }}
.stop b {{ display: block; font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 8.6pt; letter-spacing: .14em; text-transform: uppercase; color: #C1FF72; }}
.stop p {{ margin: .4mm 0 0; font-size: 7.9pt; line-height: 1.4; color: #e3e5dc; }}
.refs {{ margin: 2.4mm 12mm 0; font-size: 6.6pt; line-height: 1.4; color: #7a7e72; }}
.refs b {{ color: #242424; }}
.reg {{ margin: 3mm 12mm 0; background: #fff; border-radius: 3.5mm; overflow: hidden; box-shadow: 0 .5mm 1.6mm rgba(0,0,0,.06); }}
.reg-t {{ background: #242424; color: #C1FF72; font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 8pt; letter-spacing: .14em; text-transform: uppercase; padding: 1.6mm 4mm; }}
.reg-g {{ display: flex; flex-wrap: wrap; }}
.reg-c {{ width: 50%; height: 9mm; padding: 1.3mm 4mm; border-bottom: .25mm solid #e3e6dc; font-size: 6.6pt; color: #8a8f80; text-transform: uppercase; letter-spacing: .08em; }}
.reg-c:nth-child(odd) {{ border-right: .25mm solid #e3e6dc; }}
.reg-l {{ width: 100%; height: 11mm; padding: 1.3mm 4mm; font-size: 6.6pt; color: #8a8f80; text-transform: uppercase; letter-spacing: .08em; }}

/* ---------- CTA ---------- */
.cta-top {{ padding: 10mm 12mm 0; }}
.cta-simb {{ position: absolute; right: 12mm; top: 14mm; text-align: center; font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 7pt; letter-spacing: .14em; text-transform: uppercase; line-height: 1.15; color: #5a5e52; }}
.cta-simb .simb {{ display: block; width: 34mm; height: 34mm; object-fit: cover; border-radius: 4mm; border: .8mm solid #C1FF72; margin-bottom: 1.4mm; box-shadow: 0 .8mm 2.4mm rgba(0,0,0,.15); }}
.cta-simb b {{ font-family: 'Bebas', sans-serif; font-weight: 400; font-size: 15pt; letter-spacing: .04em; color: #242424; }}
.cta-top h1 {{ font-size: 36pt; margin: 3mm 0 2mm; max-width: 130mm; }}
.cta-top p {{ margin: 0; font-size: 9.6pt; color: #43473c; max-width: 124mm; }}
.ig {{ margin: 5mm 12mm 0; background: #242424; border-radius: 4mm; display: flex; align-items: center; gap: 5mm; padding: 4mm 5mm; text-decoration: none; color: #fff; position: relative; overflow: hidden; }}
.ig img {{ width: 22mm; height: 22mm; border-radius: 2mm; background: #fff; padding: 1mm; }}
.ig .h {{ font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 7.4pt; letter-spacing: .18em; text-transform: uppercase; color: #C1FF72; }}
.ig .handle {{ font-family: 'Bebas', sans-serif; font-size: 28pt; line-height: 1; margin: .6mm 0 .8mm; }}
.ig p {{ margin: 0; font-size: 8pt; color: #d4d7cd; line-height: 1.4; }}
.ig p b {{ color: #C1FF72; }}
.livro {{ margin: 5mm 12mm 0; background: #fff; border-radius: 4mm; padding: 4.5mm; display: flex; gap: 5mm; box-shadow: 0 .6mm 2mm rgba(0,0,0,.06); }}
.gal {{ flex: 0 0 70mm; height: 88mm; position: relative; }}
.gal .g1 {{ position: absolute; left: 0; top: 0; width: 52mm; height: 69mm; object-fit: cover; border-radius: 3mm; }}
.gal .g2 {{ position: absolute; right: 0; bottom: 0; width: 38mm; height: 50mm; object-fit: cover; border-radius: 3mm; border: 1.2mm solid #C1FF72; }}
.gal .tag {{ position: absolute; left: 2mm; bottom: 3mm; background: #242424; color: #C1FF72; font-family: 'Bebas', sans-serif; font-size: 13pt; padding: .6mm 2.6mm 0; border-radius: 1.5mm; }}
.lt .lbl {{ margin-top: 1mm; }}
.lt h2 {{ font-size: 27pt; line-height: .92; margin: 1mm 0 1.4mm; }}
.lt .st {{ font-family: 'Oswald', sans-serif; font-weight: 500; font-size: 8.6pt; text-transform: uppercase; letter-spacing: .03em; color: #5f8f1c; line-height: 1.3; margin-bottom: 2mm; }}
.lt p {{ margin: 0 0 2mm; font-size: 8.1pt; line-height: 1.45; color: #3a3d34; }}
.lt ul {{ margin: 0 0 3mm; padding: 0; list-style: none; }}
.lt li {{ font-size: 7.9pt; padding: .4mm 0 .4mm 4.2mm; position: relative; color: #3a3d34; }}
.lt li::before {{ content: ""; position: absolute; left: 0; top: 1.6mm; width: 2.2mm; height: 2.2mm; border-radius: 50%; background: #C1FF72; border: .35mm solid #242424; }}
.btn {{ display: block; text-align: center; background: #C1FF72; color: #242424; text-decoration: none; border-radius: 10mm; padding: 2.4mm 3mm 1.6mm; font-family: 'Bebas', sans-serif; font-size: 16pt; letter-spacing: .04em; border: .5mm solid #242424; }}
.site {{ margin: 4.5mm 12mm 0; display: flex; justify-content: space-between; align-items: center; font-size: 8pt; color: #5a5e52; }}
.site b {{ font-family: 'Oswald', sans-serif; font-weight: 600; color: #242424; text-transform: uppercase; letter-spacing: .06em; }}
.site a {{ font-family: 'Oswald', sans-serif; font-weight: 600; color: #242424; text-decoration: none; background: #C1FF72; padding: .8mm 2.6mm; border-radius: 5mm; }}
"""


def build(tema, cfg):
    hoje = date.today()
    data_ed = f"{MESES[hoje.month-1]}/{hoje.year}"
    L, serie = cfg["livro"], e(cfg["serie"])
    logo = img_uri("assets/logo_claro.png")
    simb = img_uri("assets/simbolo/cafe_com_sesmt_foto.jpg") or img_uri("assets/simbolo/cafe_com_sesmt_icone.png")
    simb_tag = f'<img class="simb" src="{simb}">' if simb else ""
    logo_tag = f'<img class="logo" src="{logo}">' if logo else f'<b>{e(cfg["marca"])}</b>'
    foot_logo = f'<img src="{logo}">' if logo else ""

    def foot(n, meio=None):
        meio = meio or f'{serie} · Edição {e(tema["edicao"])} · {e(cfg["instagram"])}'
        return f'<div class="foot">{foot_logo}<span class="fm">{simb_tag}{meio}</span><span class="pg"><b>{n:02d}</b> / 03</span></div>'

    # título: realça a última palavra (marca-texto verde)
    pal = tema["titulo"].split()
    titulo = e(" ".join(pal[:-1])) + f' <span class="hl">{e(pal[-1])}</span>' if len(pal) > 1 else e(tema["titulo"])

    capa_img = img_uri(tema.get("capa_imagem"))
    arte = (f'<img src="{capa_img}">' if capa_img else ILUSTRACOES.get(tema.get("ilustracao", ""), ""))

    riscos = "".join(f'<div class="risco"><div class="n">{i+1}</div><div><b>{e(r["titulo"])}</b><span>{e(r["texto"])}</span></div></div>'
                     for i, r in enumerate(tema["riscos"]))
    nrs = "".join(f'<div class="nrc"><div class="nr">{e(n["nr"])}</div><div class="t">{e(n["tema"])}</div><p>{e(n["texto"])}</p></div>'
                  for n in tema["normas"])
    p1 = f"""
<section class="page">
  <div class="tape" style="top:0"></div>
  <div class="cover-top" style="padding-top:12mm">{logo_tag}<div class="selo-w">{simb_tag}<div class="selo"><b>{serie}</b>Edição {e(tema["edicao"])} · {data_ed}</div></div></div>
  <div class="cover-main">
    <div class="cover-txt">
      <span class="chip">{e(tema["categoria"])}</span>
      <h1>{titulo}</h1>
      <p class="cover-sub">{e(tema["subtitulo"])}</p>
    </div>
    <div class="cover-art">{arte}</div>
  </div>
  <div class="intro">
    <div class="a"><div class="lbl">Por que importa</div><h2>{e(tema.get("abertura_titulo", "Por que este tema importa"))}</h2><p>{e(tema["abertura"])}</p></div>
    <div class="b"><div class="lbl">Principais riscos</div>{riscos}</div>
  </div>
  <div class="nrs"><div class="lbl">Base normativa · o que dizem as NRs</div><div class="nrs-g">{nrs}</div></div>
  {foot(1)}
</section>"""

    # equilibra a altura das 2 colunas (subconjunto ótimo) e numera na ordem de leitura
    grupos = tema["checklist"]
    pesos = [18 + sum(len(x) for x in g["itens"]) / 3.2 for g in grupos]
    tot, melhor = sum(pesos), None
    for m in range(1, 2 ** len(grupos) - 1):
        if not m & 1:  # o 1º grupo sempre abre a coluna esquerda
            continue
        esq = sum(p_ for i, p_ in enumerate(pesos) if m >> i & 1)
        if melhor is None or abs(tot - 2 * esq) < melhor[0]:
            melhor = (abs(tot - 2 * esq), m)
    m = melhor[1] if melhor else 1
    cols = [[g for i, g in enumerate(grupos) if m >> i & 1], [g for i, g in enumerate(grupos) if not m >> i & 1]]
    n = 0; html_cols = []
    for col in cols:
        h = ""
        for g in col:
            key = g.get("icone") or ICONE_GRUPO.get(g["grupo"].lower(), "alerta")
            itens = ""
            for it in g["itens"]:
                n += 1
                itens += f'<div class="item"><div class="box"></div><div class="num">{n:02d}</div><div class="txt">{e(it)}</div></div>'
            h += f'<div class="card"><div class="card-h"><div class="ico">{ic(ICONES[key])}</div><b>{e(g["grupo"])}</b></div>{itens}</div>'
        html_cols.append(h)
    cards = '<div class="col">' + html_cols[0] + '</div><div class="col">' + html_cols[1] + '</div>'
    reg_html = ""
    if n <= tema.get("registro_max_itens", 13) and tema.get("registro"):
        reg_html = '<div class="reg"><div class="reg-t">Registro de campo</div><div class="reg-g">' + "".join(f'<div class="reg-c">{e(c)}</div>' for c in tema["registro"]) + '<div class="reg-l">Pendências e providências</div></div></div>'
    p2 = f"""
<section class="page">
  <div class="tape v"></div>
  <div class="ck-head">
    <div><div class="lbl">Ferramenta de campo · marque, imprima, use</div><h2>{e(tema["checklist_titulo"])}</h2></div>
    <div class="cnt"><b>{n}</b>pontos</div>
  </div>
  <div class="ck-sub"><b>Quando aplicar:</b> {e(tema["aplicacao"])}</div>
  <div class="ck">{cards}</div>
  <div class="stop"><div class="oct">PARE</div><div><b>Critério de paralisação</b><p>{e(tema["paralisacao"])}</p></div></div>
  {reg_html}
  <div class="refs"><b>Referências:</b> {e(tema["referencias"])} <b>Importante:</b> {e(tema["aviso"])}</div>
  {foot(2)}
</section>"""

    capa, foto = img_uri(L.get("capa")), img_uri(L.get("foto_extra"))
    gal = (f'<img class="g1" src="{capa}">' if capa else "") + (f'<img class="g2" src="{foto}">' if foto else "") + '<div class="tag">Já disponível</div>'
    para_quem = "".join(f"<li>{e(x)}</li>" for x in L["para_quem"])
    site_link = (f'<a href="{e(cfg["site_url"])}">{e(re.sub(r"^https?://", "", cfg["site_url"]))} →</a>' if cfg.get("site_url")
                 else f'<a href="{e(cfg["instagram_url"])}">link na bio →</a>')
    p3 = f"""
<section class="page">
  <div class="tape" style="top:0"></div>
  <div class="cta-simb">{simb_tag}<span>Café com<br><b>SESMT</b></span></div>
  <div class="cta-top" style="padding-top:13mm">
    <span class="chip">Continue evoluindo</span>
    <h1>A segurança não termina<br><span class="hl">no checklist.</span></h1>
    <p>Prevenir acidentes exige conhecimento, atenção e atualização constante. A cada novo vídeo, um tema operacional com checklist de campo, base normativa e a visão prática de quem vive a SST no dia a dia.</p>
  </div>
  <a class="ig" href="{e(cfg["instagram_url"])}">
    <img src="{qr_data_uri(cfg["instagram_url"])}">
    <div><div class="h">Siga e acompanhe no Instagram</div><div class="handle">{e(cfg["instagram"])}</div>
    <p>Comente <b>EU QUERO</b> nos próximos vídeos e receba cada novo checklist da série <b>{serie}</b> direto na sua DM.</p></div>
  </a>
  <div class="livro">
    <div class="gal">{gal}</div>
    <div class="lt">
      <div class="lbl">O livro · {e(L["editora"])} {e(L["ano"])}</div>
      <h2>{e(L["titulo"])}</h2>
      <div class="st">{e(L["subtitulo"])}</div>
      <p>{e(L["descricao"])}</p>
      <ul>{para_quem}</ul>
      <a class="btn" href="{e(cfg["instagram_url"])}">Link de compra na bio →</a>
    </div>
  </div>
  <div class="site"><span><b>{e(cfg["site_rotulo"])}</b> · PGR · PCMSO · laudos · AEP · treinamentos NR · perícia</span>{site_link}</div>
  {foot(3, e(cfg["tagline"]))}
</section>"""

    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{e(tema["titulo"])} — {serie}</title>'
            f'<style>{font_faces()}{CSS}</style></head><body>{p1}{p2}{p3}</body></html>')


def main():
    tema = json.load(open(sys.argv[1], encoding="utf-8"))
    cfg = json.load(open(os.path.join(BASE, "config_bnsj.json"), encoding="utf-8"))
    html = build(tema, cfg)
    os.makedirs(os.path.join(BASE, "saida"), exist_ok=True)
    pdf = os.path.join(BASE, "saida", f'EBOOK_BNSJ_{tema["edicao"]}_{slug(tema["titulo"])}.pdf')
    doc = HTML(string=html, base_url=BASE).render()
    doc.write_pdf(pdf)
    print(pdf, "páginas:", len(doc.pages))


if __name__ == "__main__":
    main()
