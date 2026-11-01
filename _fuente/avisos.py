"""Arma el HTML de un espacio de publicidad según su modo (ver _fuente/publicidad.py)."""
import datetime, html, re
from publicidad import ANUNCIOS, ESPACIOS, ADSENSE_CLIENT

esc = html.escape
VIEJOS = {"en-nota": "nota-medio", "lateral": "nota-lateral"}


def _rel(depth, path=""):
    return ("../" * depth) + path if depth or path else "./"


def _casa(cod, cls, depth, tema):
    return f'''<aside class="ad {cls} ad-house" data-espacio="{cod}" aria-label="Espacio publicitario">
            <span class="ad-label">Publicidad</span>
            <a class="ad-body" href="{_rel(depth, 'publicidad/')}"><span class="ad-txt"><strong>Tu marca, acá</strong><span>Llegá a quienes leen sobre {esc(tema.lower() or "productos con origen")}. Este espacio está disponible.</span><b>Anunciá en Umarti →</b></span></a>
          </aside>'''


def espacio(cod, depth, tema="", categoria=""):
    """HTML del espacio `cod`. `tema` personaliza el texto de la invitación; `categoria` filtra avisos propios."""
    e = ESPACIOS.get(cod)
    if not e or e.get("modo") == "apagado":
        return ""
    cls = "ad-lateral" if e.get("formato") == "lateral" else "ad-en-nota"
    modo = e.get("modo", "propio")
    if modo == "adsense" and ADSENSE_CLIENT and e.get("adsense_slot"):
        return (f'<aside class="ad {cls} ad-adsense" data-espacio="{cod}" aria-label="Publicidad"><span class="ad-label">Publicidad</span>'
                f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>'
                f'<ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_CLIENT}" data-ad-slot="{esc(e["adsense_slot"])}" data-ad-format="auto" data-full-width-responsive="true"></ins>'
                '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script></aside>')
    if modo == "codigo" and e.get("codigo"):
        return f'<aside class="ad {cls} ad-red" data-espacio="{cod}" aria-label="Publicidad"><span class="ad-label">Publicidad</span>{e["codigo"]}</aside>'
    if modo == "propio":
        hoy = datetime.date.today().isoformat()
        for a in ANUNCIOS:
            esp = set(a.get("espacios", [])) | {VIEJOS[f] for f in a.get("formatos", []) if f in VIEJOS}
            if not a.get("activo", True) or cod not in esp:
                continue
            if a.get("categorias") and categoria not in a["categorias"]:
                continue
            if (a.get("desde") and hoy < a["desde"]) or (a.get("hasta") and hoy > a["hasta"]):
                continue
            link = a["link"] if re.match(r"https?:", a["link"]) else _rel(depth, a["link"])
            img = f'<img src="{_rel(depth, a["imagen"])}" alt="" loading="lazy">' if a.get("imagen") else ""
            return f'''<aside class="ad {cls}" data-espacio="{cod}" aria-label="Publicidad">
            <span class="ad-label">Publicidad · {esc(a["anunciante"])}</span>
            <a class="ad-body" href="{esc(link)}" rel="sponsored noopener" target="_blank">{img}<span class="ad-txt"><strong>{esc(a["titulo"])}</strong><span>{esc(a["texto"])}</span><b>{esc(a.get("cta", "Ver más"))} →</b></span></a>
          </aside>'''
    return _casa(cod, cls, depth, tema or categoria)
