// App-Symbol als PNG in der Farbe der Installation – für iPhone (kann kein SVG als Home-Symbol) und Android (maskable).
// Gleiches Motiv wie /app/icon.svg (Briefumschlag auf Farbfläche), ohne Bild-Bibliothek gezeichnet.
import { crc32, deflateSync } from 'node:zlib';

const zwischen = (x, a, b) => Math.min(b, Math.max(a, x));

// Abstand zu einem abgerundeten Rechteck (negativ = innen), alles in Einheiten der 512er-Vorlage
function rundRechteck(px, py, x, y, b, h, r) {
  const qx = Math.abs(px - (x + b / 2)) - (b / 2 - r);
  const qy = Math.abs(py - (y + h / 2)) - (h / 2 - r);
  return Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - r;
}
function strecke(px, py, ax, ay, bx, by) {
  const dx = bx - ax, dy = by - ay;
  const t = zwischen(((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy), 0, 1);
  return Math.hypot(px - ax - t * dx, py - ay - t * dy);
}

function png(groesse, rgba) {
  const zeilen = Buffer.alloc((groesse * 4 + 1) * groesse);
  for (let y = 0; y < groesse; y++) rgba.copy(zeilen, y * (groesse * 4 + 1) + 1, y * groesse * 4, (y + 1) * groesse * 4);
  const block = (typ, daten) => {
    const laenge = Buffer.alloc(4); laenge.writeUInt32BE(daten.length);
    const td = Buffer.concat([Buffer.from(typ), daten]);
    const pruef = Buffer.alloc(4); pruef.writeUInt32BE(crc32(td));
    return Buffer.concat([laenge, td, pruef]);
  };
  const kopf = Buffer.alloc(13);
  kopf.writeUInt32BE(groesse, 0); kopf.writeUInt32BE(groesse, 4);
  kopf[8] = 8; kopf[9] = 6; // 8 Bit, RGBA
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), block('IHDR', kopf), block('IDAT', deflateSync(zeilen)), block('IEND', Buffer.alloc(0))]);
}

// randlos = volle Fläche ohne runde Ecken (iPhone und Android runden selbst ab)
function zeichnen(groesse, farbe, randlos) {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(farbe.slice(i, i + 2), 16));
  const massstab = 512 / groesse, kante = massstab / 2;
  const rgba = Buffer.alloc(groesse * groesse * 4);
  for (let y = 0; y < groesse; y++) {
    for (let x = 0; x < groesse; x++) {
      const px = (x + 0.5) * massstab, py = (y + 0.5) * massstab;
      const flaeche = randlos ? 1 : zwischen(0.5 - rundRechteck(px, py, 0, 0, 512, 512, 112) / massstab, 0, 1);
      const linie = Math.min(
        Math.abs(rundRechteck(px, py, 104, 148, 304, 216, 32)),
        strecke(px, py, 116, 172, 256, 272), strecke(px, py, 256, 272, 396, 172),
      ) - 17;
      const weiss = zwischen(0.5 - linie / (kante * 2), 0, 1);
      const i = (y * groesse + x) * 4;
      rgba[i] = Math.round(r + (255 - r) * weiss);
      rgba[i + 1] = Math.round(g + (255 - g) * weiss);
      rgba[i + 2] = Math.round(b + (255 - b) * weiss);
      rgba[i + 3] = Math.round(255 * flaeche);
    }
  }
  return png(groesse, rgba);
}

const vorrat = new Map();
export function symbolPng(groesse, farbe, randlos = false) {
  const schluessel = `${groesse}|${farbe}|${randlos}`;
  if (!vorrat.has(schluessel)) vorrat.set(schluessel, zeichnen(groesse, farbe, randlos));
  return vorrat.get(schluessel);
}
