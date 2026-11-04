"""Erzeugt alle App-Symbole (public/app) aus scripts/symbol-vorlage.webp. Braucht Pillow.
   Aufruf: python scripts/symbole.py scripts/symbol-vorlage.webp public/app"""
import sys
from PIL import Image, ImageFilter

quelle, ziel = sys.argv[1], sys.argv[2]
BRAUN = (60, 42, 27)
WEISS = (255, 255, 255)

g = Image.open(quelle).convert('L')
# Deckkraft aus Helligkeit: Hintergrund (~254) → 0, Linien (~45) → 255; entfernt Kompressionsrauschen
alpha = g.point(lambda v: max(0, min(255, round((250 - v) * 255 / 190))))
alpha = alpha.crop(alpha.getbbox())


def symbol(groesse, anteil, hintergrund=WEISS, farbe=BRAUN, dicker=0):
    """Katze mittig, Höhe = anteil der Bildgröße. hintergrund=None → transparent."""
    gross = groesse * 4
    h = round(gross * anteil)
    b = round(alpha.width * h / alpha.height)
    a = alpha.resize((b, h), Image.LANCZOS)
    if dicker:
        a = a.filter(ImageFilter.MaxFilter(dicker))
    maske = Image.new('L', (gross, gross), 0)
    maske.paste(a, ((gross - b) // 2, (gross - h) // 2))
    maske = maske.resize((groesse, groesse), Image.LANCZOS)
    if hintergrund is None:
        bild = Image.new('RGBA', (groesse, groesse), farbe + (0,))
        bild.putalpha(maske)
        return bild
    bild = Image.new('RGB', (groesse, groesse), hintergrund)
    bild.paste(Image.new('RGB', (groesse, groesse), farbe), (0, 0), maske)
    return bild


def speichern(bild, name):
    bild.save(f'{ziel}/{name}', optimize=True)


speichern(symbol(192, 0.92), 'icon-192.png')
speichern(symbol(512, 0.92), 'icon-512.png')
speichern(symbol(512, 0.74), 'icon-maskable-512.png')    # innerhalb der Sicherheitszone (Kreis, 80 %)
speichern(symbol(180, 0.90), 'apple-touch-icon.png')
speichern(symbol(32, 0.96, dicker=5), 'favicon-32.png')   # Linien verstärkt, sonst bei 32 px unsichtbar
speichern(symbol(96, 0.94, None, WEISS, dicker=5), 'badge-96.png')  # Mitteilungs-Symbol: nur Form, weiß auf transparent
