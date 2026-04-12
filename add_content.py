#!/usr/bin/env python3
"""
add_content.py – Interaktives Script zum Pflegen des Showroom-Eins-Inhalts.

Aufruf:
    python3 add_content.py

Wähle dann:
    A – Neue Künstler:in anlegen
    B – Neues Werk anlegen
"""

import json
import os
import re
import shutil
import unicodedata

BASE    = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(BASE, "content")

KATEGORIEN = [
    "Skulpturen", "Fotografie", "Textilkunst", "Malerei",
    "Druckgrafik", "Zeichnungen", "Keramik", "Mixed Media",
]


# ── Hilfsfunktionen ───────────────────────────────────────────────

def slugify(text):
    replacements = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
                    "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"}
    for char, rep in replacements.items():
        text = text.replace(char, rep)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_]+", "-", text)

def prompt(label, required=True, default=None):
    hint = f" [{default}]" if default is not None else ""
    while True:
        val = input(f"  {label}{hint}: ").strip()
        if not val and default is not None:
            return default
        if val or not required:
            return val
        print("  ⚠ Pflichtfeld – bitte eingeben.")

def prompt_yn(label, default=False):
    hint = "[J/n]" if default else "[j/N]"
    val = input(f"  {label} {hint}: ").strip().lower()
    if not val:
        return default
    return val in ("j", "ja", "y", "yes")

def prompt_choice(label, options):
    print(f"\n  {label}")
    for i, opt in enumerate(options, 1):
        print(f"    {i}) {opt}")
    while True:
        val = input("  Auswahl (Nummer): ").strip()
        if val.isdigit() and 1 <= int(val) <= len(options):
            return options[int(val) - 1]
        print("  ⚠ Ungültige Auswahl.")

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def alle_kuenstler():
    path = os.path.join(CONTENT, "alle-kuenstler.json")
    return load_json(path) if os.path.exists(path) else []

def naechste_werknummer():
    """Findet die nächste freie SRE_XX_26-Nummer."""
    werke_dir = os.path.join(CONTENT, "werke")
    existing = [f for f in os.listdir(werke_dir) if f.endswith(".json")]
    nums = []
    for name in existing:
        m = re.match(r"sre_(\d+)_26\.json", name)
        if m:
            nums.append(int(m.group(1)))
    next_num = max(nums) + 1 if nums else 1
    return f"SRE_{next_num:02d}_26"


# ── Modus A: Neue Künstler:in ─────────────────────────────────────

def modus_a():
    print("\n── Neue Künstler:in anlegen ─────────────────────────────\n")

    name      = prompt("Vollständiger Name")
    kid       = slugify(name)
    bio       = prompt("Bio (kurz)", required=False, default="")
    website   = prompt("Website (URL)", required=False, default="")
    instagram = prompt("Instagram (Handle oder URL)", required=False, default="")

    ordner = os.path.join(CONTENT, "kuenstler", kid)
    if os.path.exists(ordner):
        print(f"\n  ⚠ Ordner existiert bereits: content/kuenstler/{kid}/")
        if not prompt_yn("Trotzdem überschreiben?", default=False):
            print("  Abgebrochen.")
            return

    os.makedirs(ordner, exist_ok=True)

    # Bild-Ordner für diese Künstler:in anlegen
    img_ordner = os.path.join(BASE, "assets", "images", "kuenstler", kid)
    os.makedirs(img_ordner, exist_ok=True)

    # Portrait optional gleich kopieren
    portrait_src = prompt("Portrait-Bildpfad (leer = später)", required=False, default="")
    portrait_dest = ""
    if portrait_src:
        portrait_src = os.path.expanduser(portrait_src)
        if os.path.isfile(portrait_src):
            ext = os.path.splitext(portrait_src)[1].lower()
            dest = os.path.join(img_ordner, f"portrait{ext}")
            shutil.copy2(portrait_src, dest)
            portrait_dest = f"assets/images/kuenstler/{kid}/portrait{ext}"
            print(f"  ✓ Portrait kopiert nach {portrait_dest}")
        else:
            print(f"  ⚠ Datei nicht gefunden: {portrait_src}")

    data = {
        "id":        kid,
        "name":      name,
        "bio":       bio,
        "website":   website,
        "instagram": instagram,
        "portrait":  portrait_dest,
        "medien":    [],
    }
    save_json(os.path.join(ordner, "kuenstler.json"), data)

    # Index aktualisieren
    index_path = os.path.join(CONTENT, "alle-kuenstler.json")
    index = alle_kuenstler()
    index = [k for k in index if k["id"] != kid]
    index.append(data)
    index.sort(key=lambda k: k["name"])
    save_json(index_path, index)

    portrait_hint = (
        f"    {portrait_dest}" if portrait_dest
        else f"    assets/images/kuenstler/{kid}/portrait.jpg  ← hier ablegen"
    )
    print(f"""
  ✓ Künstler:in angelegt: content/kuenstler/{kid}/kuenstler.json
  ✓ Bildordner angelegt:  assets/images/kuenstler/{kid}/

  Portrait:
{portrait_hint}
""")


# ── Modus B: Neues Werk ───────────────────────────────────────────

def modus_b():
    print("\n── Neues Werk anlegen ───────────────────────────────────\n")

    kuenstler_list = alle_kuenstler()
    if not kuenstler_list:
        print("  ⚠ Keine Künstler:innen gefunden. Bitte zuerst Modus A ausführen.")
        return

    # Künstler:in wählen
    namen = [k["name"] for k in kuenstler_list]
    k_name = prompt_choice("Künstler:in wählen", namen)
    k_obj  = next(k for k in kuenstler_list if k["name"] == k_name)
    kid    = k_obj["id"]

    vorschlag_nr = naechste_werknummer()
    titel     = prompt("Titel")
    nummer    = prompt("Werknummer", default=vorschlag_nr)
    werk_id   = nummer.lower()
    jahr      = prompt("Jahr", required=False, default="")
    material  = prompt("Material / Technik")
    groesse   = prompt("Größe (in cm, z.B. 40x30)", required=False, default="")
    auflage   = prompt("Auflage (leer = keine)", required=False, default="")
    preis     = prompt("Preis (z.B. 350€ oder 'unverkäuflich')", required=False, default="")
    kategorie = prompt_choice("Kategorie", KATEGORIEN)
    showroom  = prompt_yn("Im Showroom?", default=True)
    online    = prompt_yn("Online sichtbar?", default=False)

    # Bild – Zielordner: assets/images/kuenstler/<kid>/<werknummer>.jpg
    bild_src  = prompt("Bildpfad (absolut oder relativ, leer = später)", required=False, default="")
    bild_dest = ""
    if bild_src:
        bild_src = os.path.expanduser(bild_src)
        if os.path.isfile(bild_src):
            ext      = os.path.splitext(bild_src)[1].lower()
            bild_dir = os.path.join(BASE, "assets", "images", "kuenstler", kid)
            os.makedirs(bild_dir, exist_ok=True)
            bild_name = f"{werk_id}{ext}"
            shutil.copy2(bild_src, os.path.join(bild_dir, bild_name))
            bild_dest = f"assets/images/kuenstler/{kid}/{bild_name}"
            print(f"  ✓ Bild kopiert nach {bild_dest}")
        else:
            print(f"  ⚠ Datei nicht gefunden: {bild_src}  (bild bleibt leer)")

    werk = {
        "id":          werk_id,
        "nummer":      nummer,
        "titel":       titel,
        "kuenstler_id": kid,
        "jahr":        jahr,
        "material":    material,
        "groesse":     groesse,
        "auflage":     auflage,
        "preis":       preis,
        "showroom":    showroom,
        "online":      online,
        "kategorie":   kategorie,
        "bild":        bild_dest,
    }

    # werk.json schreiben
    werk_path = os.path.join(CONTENT, "werke", f"{werk_id}.json")
    save_json(werk_path, werk)

    # alle-werke.json aktualisieren
    index_path = os.path.join(CONTENT, "alle-werke.json")
    index = load_json(index_path) if os.path.exists(index_path) else []
    index = [w for w in index if w["id"] != werk_id]
    index.append(werk)
    index.sort(key=lambda w: w["nummer"])
    save_json(index_path, index)

    # Künstler:in-medien aktualisieren
    k_json_path = os.path.join(CONTENT, "kuenstler", kid, "kuenstler.json")
    if os.path.exists(k_json_path):
        k_data = load_json(k_json_path)
        medien = set(k_data.get("medien", []))
        medien.add(kategorie)
        k_data["medien"] = sorted(medien)
        save_json(k_json_path, k_data)

        # auch in alle-kuenstler.json spiegeln
        k_index = alle_kuenstler()
        for entry in k_index:
            if entry["id"] == kid:
                entry["medien"] = k_data["medien"]
        save_json(os.path.join(CONTENT, "alle-kuenstler.json"), k_index)

    bild_hint = (
        f"  ✓ Bild unter:      {bild_dest}"
        if bild_dest
        else f"  ℹ Bild fehlt noch → assets/images/kuenstler/{kid}/{werk_id}.jpg"
    )
    print(f"""
  ✓ Werk angelegt:   content/werke/{werk_id}.json
  ✓ Index aktualisiert: alle-werke.json
{bild_hint}
""")


# ── Hauptmenü ─────────────────────────────────────────────────────

def main():
    print("\n╔══════════════════════════════════════╗")
    print("║   Showroom Eins – Content Manager    ║")
    print("╚══════════════════════════════════════╝")
    print()
    print("  A  –  Neue Künstler:in anlegen")
    print("  B  –  Neues Werk anlegen")
    print("  Q  –  Beenden")
    print()

    auswahl = input("  Auswahl: ").strip().upper()

    if auswahl == "A":
        modus_a()
    elif auswahl == "B":
        modus_b()
    elif auswahl == "Q":
        print("  Tschüss!\n")
    else:
        print("  ⚠ Unbekannte Auswahl.\n")


if __name__ == "__main__":
    main()
