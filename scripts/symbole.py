"""Erzeugt alle App-Symbole in public/app. Braucht Pillow.
   Aufruf: python scripts/symbole.py

   symbol-vorlage.webp  quadratisches Foto → App-Symbole, Favicon (volle Fläche, die Geräte runden selbst ab)
   badge-vorlage.webp   Strichzeichnung auf Weiß → Mitteilungs-Badge (Android braucht eine einfarbige Form)"""
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps

HIER = Path(__file__).resolve().parent
ZIEL = HIER.parent / 'public' / 'app'

foto = Image.open(HIER / 'symbol-vorlage.webp').convert('RGB')
foto = ImageOps.fit(foto, (min(foto.size),) * 2, Image.LANCZOS)  # mittig quadratisch zuschneiden


def symbol(groesse, ausschnitt=1.0):
    """ausschnitt < 1 zoomt in die Bildmitte."""
    rand = round(foto.width * (1 - ausschnitt) / 2)
    bild = foto.crop((rand, rand, foto.width - rand, foto.height - rand))
    return bild.resize((groesse, groesse), Image.LANCZOS)


def speichern(bild, name):
    bild.save(ZIEL / name, optimize=True)


speichern(symbol(192), 'icon-192.png')
speichern(symbol(512), 'icon-512.png')
speichern(symbol(512), 'icon-maskable-512.png')  # Foto füllt die Fläche, Masken schneiden nur Ränder ab
speichern(symbol(180), 'apple-touch-icon.png')
speichern(symbol(32, 0.8), 'favicon-32.png')     # enger Ausschnitt, damit das Gesicht bei 32 px erkennbar bleibt

# Badge: nur Deckkraft zählt, Farbe setzt das System
g = Image.open(HIER / 'badge-vorlage.webp').convert('L')
alpha = g.point(lambda v: max(0, min(255, round((250 - v) * 255 / 190))))
alpha = alpha.crop(alpha.getbbox())
h = round(96 * 4 * 0.94)
a = alpha.resize((round(alpha.width * h / alpha.height), h), Image.LANCZOS).filter(ImageFilter.MaxFilter(5))
maske = Image.new('L', (96 * 4,) * 2, 0)
maske.paste(a, ((96 * 4 - a.width) // 2, (96 * 4 - a.height) // 2))
badge = Image.new('RGBA', (96, 96), (255, 255, 255, 0))
badge.putalpha(maske.resize((96, 96), Image.LANCZOS))
speichern(badge, 'badge-96.png')
