"""
Einmalig ausführen: Liest werksliste.csv und legt die komplette
content/-Ordnerstruktur mit allen JSON-Dateien an.
"""

import csv
import json
import os
import re
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE, "content", "werksliste.csv")
CONTENT = os.path.join(BASE, "content")


# ── Hilfsfunktionen ───────────────────────────────────────────────

def slugify(text):
    """'Sybille Hutter' → 'sybille-hutter'"""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[\s_]+", "-", text)
    return text

def clean_artist_name(raw):
    """Entfernt Nickname in Anführungszeichen: 'Cedric Pintarelli "Sweet Uno"' → 'Cedric Pintarelli'"""
    return re.sub(r'\s*"[^"]*"', "", raw).strip()

def parse_bool(val):
    return "✓" in val if val else False

def kategorisieren(titel, material):
    """Leitet Kategorie aus Titel + Material ab."""
    t = titel.lower()
    m = material.lower()

    # Reihenfolge wichtig – spezifischer zuerst
    if "speckstein" in m or "granit" in m or "stein" in m:
        return "Skulpturen"
    if "sofortbild" in t or "instant" in t:
        return "Fotografie"
    if "fine art print" in m or "fotokarton" in m:
        return "Fotografie"
    if "stickerei" in m:
        return "Textilkunst"
    if "holzschnitt" in m or "linoldruck" in m or "radierung" in m or "druckgrafik" in m:
        return "Druckgrafik"
    if "grafit" in m or "bleistift" in m or "pastellkreide" in m:
        return "Zeichnungen"
    if "keramik" in m or "ton" in m or "porzellan" in m:
        return "Keramik"
    if "mixed" in m:
        return "Mixed Media"
    # Aquarell, Öl, Acryl, Dispersion → Malerei
    if any(x in m for x in ["acryl", "öl", "aquarell", "pastell", "dispersion", "gesso", "leinwand"]):
        return "Malerei"
    return "Mixed Media"


# ── CSV einlesen ──────────────────────────────────────────────────

werke = []
with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        nummer   = row["Nummer"].strip()
        artist   = clean_artist_name(row["Künstler"].strip())
        titel    = row["Werktitel"].strip()
        jahr     = row["Jahr"].strip()
        material = row["Material"].strip().replace("\n", " ").replace("  ", " ")
        groesse  = row["Größe (in cm)"].strip().replace("\n", " / ").replace("  ", " ")
        auflage  = row.get("Auflage", "").strip()
        preis    = row["Preis"].strip()
        showroom = parse_bool(row["Showroom"])
        online   = parse_bool(row["Online"])
        werk_id  = nummer.lower()  # sre_01_26
        kat      = kategorisieren(titel, material)

        werke.append({
            "id":           werk_id,
            "nummer":       nummer,
            "titel":        titel,
            "kuenstler_id": slugify(artist),
            "kuenstler":    artist,         # nur für Index-Aufbau, nicht im Schema
            "jahr":         jahr,
            "material":     material,
            "groesse":      groesse,
            "auflage":      auflage,
            "preis":        preis,
            "showroom":     showroom,
            "online":       online,
            "kategorie":    kat,
            "bild":         "",
        })


# ── Künstler:innen ableiten ───────────────────────────────────────

kuenstler_map = {}
for w in werke:
    kid = w["kuenstler_id"]
    if kid not in kuenstler_map:
        kuenstler_map[kid] = {
            "id":       kid,
            "name":     w["kuenstler"],
            "bio":      "",
            "website":  "",
            "instagram": "",
            "medien":   set(),
        }
    kuenstler_map[kid]["medien"].add(w["kategorie"])

# set → sortierte Liste
for k in kuenstler_map.values():
    k["medien"] = sorted(k["medien"])


# ── Ordner anlegen ────────────────────────────────────────────────

for kid in kuenstler_map:
    os.makedirs(os.path.join(CONTENT, "kuenstler", kid), exist_ok=True)

os.makedirs(os.path.join(CONTENT, "werke"), exist_ok=True)


# ── kuenstler.json schreiben ──────────────────────────────────────

for kid, k in kuenstler_map.items():
    data = {
        "id":        k["id"],
        "name":      k["name"],
        "bio":       k["bio"],
        "website":   k["website"],
        "instagram": k["instagram"],
        "medien":    k["medien"],
    }
    path = os.path.join(CONTENT, "kuenstler", kid, "kuenstler.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✓  kuenstler/{kid}/kuenstler.json")


# ── werk.json schreiben ───────────────────────────────────────────

# Internes Feld "kuenstler" entfernen
werk_schema_keys = ["id","nummer","titel","kuenstler_id","jahr","material",
                    "groesse","auflage","preis","showroom","online","kategorie","bild"]

for w in werke:
    data = {k: w[k] for k in werk_schema_keys}
    path = os.path.join(CONTENT, "werke", f"{w['id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✓  werke/{w['id']}.json")


# ── Index-Dateien ─────────────────────────────────────────────────

alle_werke = [{k: w[k] for k in werk_schema_keys} for w in werke]
with open(os.path.join(CONTENT, "alle-werke.json"), "w", encoding="utf-8") as f:
    json.dump(alle_werke, f, ensure_ascii=False, indent=2)
print("  ✓  alle-werke.json")

alle_kuenstler = [
    {k: v for k, v in k_data.items() if k != "kuenstler"}
    for k_data in kuenstler_map.values()
]
with open(os.path.join(CONTENT, "alle-kuenstler.json"), "w", encoding="utf-8") as f:
    json.dump(alle_kuenstler, f, ensure_ascii=False, indent=2)
print("  ✓  alle-kuenstler.json")

print("\nFertig! Alle Dateien wurden angelegt.")
print(f"  {len(werke)} Werke, {len(kuenstler_map)} Künstler:innen")
