#!/usr/bin/env python3
"""
Create new artist pages for Alexandra Kunz and Thilda Golly.
Uses johanna-mangold.html as template (female artist, similar structure).
Run with: python3 create_artist_pages.py
"""

import os
import re

BASE = os.path.join(os.path.dirname(__file__), 'kuenstler')
TEMPLATE_FILE = os.path.join(BASE, 'johanna-mangold.html')

NEW_ARTISTS = [
    {
        'id': 'alexandra-kunz',
        'name': 'Alexandra Kunz',
        'name_old': 'Johanna Mangold',
        'gender': 'f',
        'medium_de': 'Keramik',
        'medium_en': 'Ceramics',
        'bio_de': '',
        'bio_en': '',
        'vermittlung_text_de': 'Showroom Eins vermittelt auf Anfrage den direkten Kontakt zur Künstlerin. Wir sind kein Kunsthandel – alle Verkäufe laufen direkt zwischen Ihnen und der Künstlerin ab.',
        'vermittlung_text_en': 'Showroom Eins facilitates direct contact with the artist upon request. We are not an art dealer – all sales take place directly between you and the artist.',
        'gallery_items': [
            {'category': 'Keramik', 'title': 'Werk 1', 'year': '2024', 'material': 'Keramik', 'size': '–', 'price': ''},
        ],
    },
    {
        'id': 'thilda-golly',
        'name': 'Thilda Golly',
        'name_old': 'Johanna Mangold',
        'gender': 'f',
        'medium_de': 'Aquarell',
        'medium_en': 'Watercolour',
        'bio_de': '',
        'bio_en': '',
        'vermittlung_text_de': 'Showroom Eins vermittelt auf Anfrage den direkten Kontakt zur Künstlerin. Wir sind kein Kunsthandel – alle Verkäufe laufen direkt zwischen Ihnen und der Künstlerin ab.',
        'vermittlung_text_en': 'Showroom Eins facilitates direct contact with the artist upon request. We are not an art dealer – all sales take place directly between you and the artist.',
        'gallery_items': [
            {'category': 'Aquarell', 'title': 'Werk 1', 'year': '2024', 'material': 'Aquarell', 'size': '–', 'price': ''},
        ],
    },
]

ALL_ARTISTS = [
    ('cedric-pintarelli', 'Cedric Pintarelli'),
    ('chaz-bargainer', 'Chaz Bargainer'),
    ('cholud-kassem', 'Cholud Kassem'),
    ('johanna-mangold', 'Johanna Mangold'),
    ('philipp-diefenbacher', 'Philipp Diefenbacher'),
    ('ralf-diefenbacher', 'Ralf Diefenbacher'),
    ('sarah-haefner', 'Sarah Häfner'),
    ('siegmund-schlag', 'Siegmund Schlag'),
    ('sybille-hutter', 'Sybille Hutter'),
    ('alexandra-kunz', 'Alexandra Kunz'),
    ('thilda-golly', 'Thilda Golly'),
]


def make_footer_artists(current_id):
    lines = []
    for aid, aname in ALL_ARTISTS:
        if aid == current_id:
            continue
        lines.append(f'        <a href="../kuenstler/{aid}.html" class="footer-col-link">{aname}</a>')
    return '\n'.join(lines)


def make_nav_overlay_artists(current_id):
    lines = []
    for aid, aname in ALL_ARTISTS:
        lines.append(f'      <li><a href="{aid}.html">{aname}</a></li>')
    return '\n'.join(lines)


def build_gallery_items(items, artist_name):
    parts = []
    for item in items:
        price_attr = f' data-price="{item["price"]}"' if item.get('price') else ''
        parts.append(
            f'      <div class="gallery-item" data-category="{item["category"]}" data-title="{item["title"]}"'
            f' data-artist="{artist_name}" data-gender="f"'
            f' data-year="{item["year"]}" data-material="{item["material"]}" data-size="{item["size"]}"{price_attr}>'
            f'<img src="../assets/platzhalter_werke.jpg" alt="{item["title"]}"></div>'
        )
    return '\n'.join(parts)


def create_page(template_content, artist):
    content = template_content

    # Title
    content = content.replace(
        '<title>Johanna Mangold – Showroom Eins</title>',
        f'<title>{artist["name"]} – Showroom Eins</title>'
    )

    # H1
    content = content.replace(
        '<h1 class="artist-h1">Johanna Mangold</h1>',
        f'<h1 class="artist-h1">{artist["name"]}</h1>'
    )

    # Gallery items - replace all existing gallery items
    gallery_block = build_gallery_items(artist['gallery_items'], artist['name'])
    content = re.sub(
        r'(<div class="gallery-scatter" id="galleryGrid">).*?(</div>\s*\n\s*<div class="load-more-wrap")',
        r'\1\n' + gallery_block + r'\n    \2',
        content,
        flags=re.DOTALL
    )

    # Translation strings - DE bio
    content = content.replace(
        "'artist-bio': \"Johanna Mangold beschäftigt",
        f"'artist-bio': \"{artist['bio_de']}"
    )
    # Handle the case where bio_de is empty and we need to close it
    # Actually replace the full DE bio line
    content = re.sub(
        r"('artist-bio': \")Johanna Mangold[^\"]*(\",)",
        r"\g<1>" + artist['bio_de'].replace('\\', '\\\\').replace('"', '\\"') + r'",',
        content,
        count=1
    )

    # EN bio
    content = re.sub(
        r"('artist-bio': \")Johanna Mangold[^\"]*(\",)",
        r"\g<1>" + artist['bio_en'].replace('\\', '\\\\').replace('"', '\\"') + r'",',
        content,
        count=1
    )

    # Vermittlung text DE
    old_verm_de = "Showroom Eins vermittelt auf Anfrage den direkten Kontakt zur Künstlerin. Wir sind kein Kunsthandel – alle Verkäufe laufen direkt zwischen Ihnen und der Künstlerin ab."
    content = content.replace(old_verm_de, artist['vermittlung_text_de'])

    # Vermittlung text EN (in T object)
    old_verm_en = 'Showroom Eins facilitates direct contact with the artist upon request. We are not an art dealer – all sales take place directly between you and the artist.'
    content = content.replace(old_verm_en, artist['vermittlung_text_en'])

    # HTML vermittlung-text paragraph
    content = re.sub(
        r'(<p class="vermittlung-text"[^>]*>)[^<]*(</p>)',
        r'\1' + artist['vermittlung_text_de'] + r'\2',
        content
    )

    # Footer artists column - replace the existing list
    footer_artists = make_footer_artists(artist['id'])
    content = re.sub(
        r'(<div class="footer-col footer-col-artists">\s*<span class="footer-col-label">Künstler:innen</span>).*?(</div>\s*\n\s*<div class="footer-col footer-col-legal">)',
        r'\1\n' + footer_artists + r'\n      \2',
        content,
        flags=re.DOTALL
    )

    # Mobile nav overlay artists list
    nav_artists = make_nav_overlay_artists(artist['id'])
    content = re.sub(
        r'(<ul class="nav-overlay-artists">).*?(</ul>)',
        r'\1\n' + nav_artists + r'\n    \2',
        content,
        flags=re.DOTALL
    )

    return content


def main():
    print(f'Reading template: {TEMPLATE_FILE}')
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()

    for artist in NEW_ARTISTS:
        out_path = os.path.join(BASE, f'{artist["id"]}.html')
        print(f'\nCreating {out_path}...')
        page = create_page(template, artist)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(page)
        print(f'  Created successfully.')

    print('\nDone.')
    print('\nNote: Also run update_bios.py to update bio texts in existing pages.')
    print('  python3 update_bios.py')


if __name__ == '__main__':
    main()
