# Showroom Eins – Inhalte pflegen

## Ordnerstruktur

```
content/
├── kuenstler/
│   ├── sybille-hutter/
│   │   └── kuenstler.json
│   ├── sarah-haefner/
│   │   └── kuenstler.json
│   └── ...
├── werke/
│   ├── sre_01_26.json
│   ├── sre_02_26.json
│   └── ...
├── alle-werke.json       ← zentraler Index aller Werke
└── alle-kuenstler.json   ← zentraler Index aller Künstler:innen
```

---

## Werke oder Künstler:innen hinzufügen

Im Terminal (im Projektordner):

```bash
python3 add_content.py
```

Das Script bietet zwei Modi:

### A – Neue Künstler:in anlegen
Fragt nach Name, Bio, Website und Instagram-Handle.  
Legt `content/kuenstler/<slug>/kuenstler.json` an und aktualisiert `alle-kuenstler.json`.

**Portrait danach ablegen unter:**
```
content/kuenstler/<slug>/portrait.jpg
```

### B – Neues Werk anlegen
Fragt nach allen Werkdaten (Titel, Material, Größe, Preis usw.).  
Kopiert das Bild automatisch nach `images/werke/` und legt `content/werke/<id>.json` an.  
Aktualisiert `alle-werke.json` und die `medien`-Liste der Künstler:in.

---

## JSON-Schemas

### kuenstler.json
```json
{
  "id": "sybille-hutter",
  "name": "Sybille Hutter",
  "bio": "",
  "website": "",
  "instagram": "",
  "medien": ["Skulpturen"]
}
```

### werk.json
```json
{
  "id": "sre_01_26",
  "nummer": "SRE_01_26",
  "titel": "Abendkleid",
  "kuenstler_id": "sybille-hutter",
  "jahr": "2021",
  "material": "Grünbrauner Speckstein aus Brazilien",
  "groesse": "45x19x10",
  "auflage": "",
  "preis": "175€",
  "showroom": true,
  "online": false,
  "kategorie": "Skulpturen",
  "bild": "images/werke/sre_01_26.jpg"
}
```

---

## Kategorien

| Slug        | Bedeutung       |
|-------------|-----------------|
| Skulpturen  | 3D-Arbeiten, Stein, Objekte |
| Fotografie  | Fine Art Print, Sofortbild |
| Textilkunst | Stickerei, Weben, Textil |
| Malerei     | Acryl, Öl, Aquarell |
| Druckgrafik | Holzschnitt, Linoldruck, Radierung |
| Zeichnungen | Grafit, Bleistift, Pastellkreide |
| Keramik     | Ton, Porzellan |
| Mixed Media | Kombinierte Techniken |

---

## Bilder

```
assets/images/kuenstler/
├── sybille-hutter/
│   ├── portrait.jpg        ← Portrait der Künstlerin
│   ├── sre_01_26.jpg       ← Werkbild (= Werknummer als Dateiname)
│   └── sre_02_26.jpg
├── sarah-haefner/
│   └── ...
└── ...
```

- Werkbilder → `assets/images/kuenstler/<kuenstler-id>/<werknummer>.jpg`
- Portraits   → `assets/images/kuenstler/<kuenstler-id>/portrait.jpg`
- `add_content.py` kopiert und benennt Bilder automatisch um.
- Empfohlene Auflösung: min. 1200px auf der längsten Seite, JPEG/WebP

---

## Hinweise

- `alle-werke.json` und `alle-kuenstler.json` **immer über `add_content.py` aktualisieren**, nicht manuell – das Script hält die Indizes konsistent.
- Werk-IDs folgen dem Schema `sre_XX_26` (zwei Ziffern, Jahrgang 26).
- Künstler:innen-IDs sind URL-sichere Slugs: Umlaute werden zu ae/oe/ue.
