#!/usr/bin/env python3
"""Construit index.html a partir de l'essai en Markdown.

Usage : python3 build/build.py [chemin/vers/article.md]

Sans dependance. Convertit le sous-ensemble de Markdown employe par l'essai
(titres, paragraphes, italique, gras, citations, listes, tableaux), masque les
statuts de citation entre crochets, et insere les images decrites dans
build/images.json.
"""
import html
import json
import os
import re
import struct
import sys
import time
import unicodedata

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
ARTICLE = os.path.expanduser(
    "~/Documents/litterature/articles/2026-10-11-sortir-de-la-religion.md")
MOTS_MINUTE = 230
BASE_URL = "https://thomasgourouza.github.io/sortir-de-la-religion/"
RESUME = "L'essai en dix minutes"
NOMBRES = {1: "une", 2: "deux", 3: "trois", 4: "quatre", 5: "cinq", 6: "six", 7: "sept",
           8: "huit", 9: "neuf", 10: "dix", 11: "onze", 12: "douze"}


def slug(t):
    t = t.split(" : ")[0]
    t = re.sub(r"\([^)]*\)", "", t)
    t = t.replace("ø", "o").replace("Ø", "O").replace("æ", "ae").replace("œ", "oe").replace("Œ", "Oe")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t.lower()).strip("-")


STATUT = re.compile(r"vérifi|cité|mémoire|paraphras|selon|d'après|\blues?\b|\blue\b|attest|traduis|source|sic|optique|graphie|ponctuation|OCR|numéris|même", re.I)


def masquer_statuts(t):
    """Retire les crochets de statut, garde les ellipses et les courtes insertions."""
    def remplace(m):
        c = m.group(1).strip()
        if c in ("...", "…"):
            return "[…]"
        if len(c) <= 12 and not STATUT.search(c) and not re.search(r"\d", c):
            return m.group(0)
        return ""
    t = re.sub(r"\s*\[((?:[^\[\]]|\[[^\[\]]*\]){0,900})\](?!\(#)", remplace, t)
    t = re.sub(r"`[^`]*`", "", t)
    t = re.sub(r"[ \t]+([,.)])", r"\1", t)
    t = re.sub(r"([.!?…]\s?»)\s?\.", r"\1", t)
    t = re.sub(r"\(\s*\)", "", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    return t


def en_ligne(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"(https?://[^\s<;,)]+[^\s<;,.)])", r'<a href="\1" rel="noopener">\1</a>', t)
    t = re.sub(r"\[([^\[\]]+)\]\(#([A-Za-z0-9-]+)\)", r'<a href="#\2" data-target="\2">\1</a>', t)
    return t


def mots(t):
    """Compte les mots hors balises ; les encadres litteraires n'entrent pas dans les temps de lecture."""
    t = re.sub(r'<aside class="lettres">.*?</aside>', " ", t, flags=re.S)
    return len(re.sub(r"<[^>]+>", " ", t).split())


def blocs(lignes):
    """Decoupe une suite de lignes en blocs (paragraphe, liste, tableau, citation)."""
    out, cur, kind = [], [], None

    def flush():
        nonlocal cur, kind
        if cur:
            out.append((kind, cur))
        cur, kind = [], None

    for l in lignes:
        s = l.rstrip("\n")
        if not s.strip():
            flush()
            continue
        k = "table" if s.startswith("|") else "list" if re.match(r"^\s*[-*] ", s) \
            else "quote" if s.startswith(">") else "p"
        if kind and k != kind and not (kind == "p" and k == "p"):
            flush()
        kind = k
        cur.append(s)
    flush()
    return out


def rendre_table(rows):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    cells = [c for c in cells if not all(re.fullmatch(r":?-{2,}:?", x) for x in c)]
    head, body = cells[0], cells[1:]
    h = ['<div class="table-wrap"><table class="cards"><thead><tr>']
    h += ["<th>%s</th>" % en_ligne(masquer_statuts(x)) for x in head]
    h.append("</tr></thead><tbody>")
    for r in body:
        h.append("<tr>" + "".join(
            '<td data-label="%s">%s</td>' % (html.escape(head[i] if i < len(head) else ""),
                                             en_ligne(masquer_statuts(x)))
            for i, x in enumerate(r)) + "</tr>")
    h.append("</tbody></table></div>")
    return "".join(h)


LETTRES_MARQUE = re.compile(r"^>\s*\*\*En littérature\.\*\*\s*")
LETTRES_OEUVRE = re.compile(r"^(.+?), (?:\*(.+?)\*|« (.+?) »)(.*?)\s*(?:\((\d[^)]*)\))?\s*$")
LETTRES_BUF = []  # oeuvres des encadres de la section en cours (auteur, titre, date)


def encadre_lettres(ls):
    """Rend un bloc « > **En littérature.** ... » en encadre repliable.

    Premiere ligne : les oeuvres, « Auteur, *Titre* (date) » separees par « ; ».
    Paragraphes separes par une ligne « > » vide ; le dernier commence par « Source ».
    """
    paras, cur = [], []
    for x in ls:
        x = re.sub(r"^>\s?", "", x)
        if not x.strip():
            if cur:
                paras.append(" ".join(cur))
            cur = []
        else:
            cur.append(x)
    if cur:
        paras.append(" ".join(cur))
    titre = LETTRES_MARQUE.sub("", "> " + paras[0]) if paras else ""
    for elt in [e.strip() for e in titre.split(" ; ") if e.strip()]:
        m = LETTRES_OEUVRE.match(elt)
        if not m:
            print("  encadré littéraire : ligne de titre inanalysable :", elt)
            continue
        LETTRES_BUF.append((m.group(1).strip(), m.group(2) or m.group(3), m.group(4).strip(), m.group(5) or ""))
    corps = []
    for p in paras[1:]:
        classe = ' class="lettres-source"' if re.match(r"Sources?\s*:", p) else ""
        corps.append("<p%s>%s</p>" % (classe, en_ligne(masquer_statuts(p).strip())))
    return ('<aside class="lettres"><details><summary><span class="lettres-label">En littérature</span> '
            '<span class="lettres-titre">%s</span></summary><div class="lettres-corps">%s</div></details></aside>' % (
                en_ligne(masquer_statuts(titre).strip()), "".join(corps)))


def rendre_blocs(lignes):
    h = []
    for kind, ls in blocs(lignes):
        if kind == "table":
            h.append(rendre_table(ls))
        elif kind == "list":
            items = [re.sub(r"^\s*[-*] ", "", x) for x in ls]
            h.append("<ul>" + "".join("<li>%s</li>" % en_ligne(masquer_statuts(i))
                                      for i in items) + "</ul>")
        elif kind == "quote" and LETTRES_MARQUE.match(ls[0]):
            h.append(encadre_lettres(ls))
        elif kind == "quote":
            txt = " ".join(re.sub(r"^>\s?", "", x) for x in ls)
            parts = [p for p in re.split(r"\s{2,}|(?<=\.)\s(?=\*\*)", txt) if p.strip()]
            body = "".join("<p>%s</p>" % en_ligne(masquer_statuts(p)) for p in parts)
            h.append('<blockquote>%s</blockquote>' % body)
        else:
            txt = masquer_statuts(" ".join(ls)).strip()
            if txt:
                h.append("<p>%s</p>" % en_ligne(txt))
    return h


def lire_article(chemin):
    s = open(chemin, encoding="utf-8").read()
    if s.startswith("---"):
        s = s.split("\n---\n", 1)[1]
    return s.split("\n")


def structurer(lignes):
    """Renvoie titre, sous-titre, intro (lignes) et la liste des parties."""
    titre, sous_titre, intro, parties = "", "", [], []
    part = sec = None
    for l in lignes:
        if l.startswith("# "):
            titre = l[2:].strip()
            continue
        if l.startswith("## "):
            part = {"titre": l[3:].strip(), "lignes": [], "sections": []}
            parties.append(part)
            sec = None
            continue
        if l.startswith("### ") and part is not None:
            sec = {"titre": l[4:].strip(), "lignes": []}
            part["sections"].append(sec)
            continue
        if part is None:
            if not sous_titre and re.match(r"^\*[^*].*\*$", l.strip()):
                sous_titre = l.strip().strip("*")
            else:
                intro.append(l)
        elif sec is None:
            part["lignes"].append(l)
        else:
            sec["lignes"].append(l)
    return titre, sous_titre, intro, parties


def analyser_titre(t):
    """'Hegel (1770-1831) : formule' -> (nom, dates, formule)."""
    nom, _, formule = t.partition(" : ")
    dates = "; ".join(re.findall(r"\(([^)]*\d[^)]*)\)", nom))
    nom = re.sub(r"\s*\([^)]*\)", "", nom).strip()
    return nom, dates, formule.strip()


def initiales(nom):
    ws = [w for w in re.split(r"[\s-]+", nom) if w and w[0].isupper()]
    return "".join(w[0] for w in ws[:2]) or nom[:1]


_DIMS = {}


def dimensions(chemin):
    """Largeur et hauteur d'un JPEG ou d'un PNG, sans dependance."""
    if chemin in _DIMS:
        return _DIMS[chemin]
    w = h = 0
    try:
        with open(os.path.join(RACINE, chemin), "rb") as f:
            d = f.read()
        if d[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", d[16:24])
        elif d[:2] == b"\xff\xd8":
            i = 2
            while i < len(d) - 9:
                if d[i] != 0xFF:
                    i += 1
                    continue
                m = d[i + 1]
                if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7 or m == 0xFF:
                    i += 1 if m == 0xFF else 2
                    continue
                n = struct.unpack(">H", d[i + 2:i + 4])[0]
                if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
                    h, w = struct.unpack(">HH", d[i + 5:i + 9])
                    break
                i += 2 + n
    except OSError:
        pass
    _DIMS[chemin] = (w, h)
    return w, h


def attr_dims(chemin):
    w, h = dimensions(chemin)
    return ' width="%d" height="%d"' % (w, h) if w and h else ""


def lien_btn(cible):
    return ('<button class="lien-btn" type="button" data-lien="%s" aria-label="Copier le lien de cette section">'
            '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true"><path d="M10 14a4 4 0 0 0 5.66 0l3-3a4 4 0 0 0-5.66-5.66l-1 1M14 10a4 4 0 0 0-5.66 0l-3 3a4 4 0 0 0 5.66 5.66l1-1" '
            'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>') % cible


def charger_images():
    p = os.path.join(ICI, "images.json")
    if not os.path.exists(p):
        return []
    imgs = json.load(open(p, encoding="utf-8"))
    return [i for i in imgs if os.path.exists(os.path.join(RACINE, i["file"]))]


def figure(img, classe="figure"):
    charge = 'loading="eager" fetchpriority="high"' if classe == "cover" else 'loading="lazy" decoding="async"'
    return ('<figure class="%s"><img src="%s" alt="%s"%s %s>'
            '<figcaption>%s<span class="credit">%s</span></figcaption></figure>') % (
        classe, html.escape(img["file"]), html.escape(img.get("alt", "")), attr_dims(img["file"]), charge,
        en_ligne(img.get("caption", "")), html.escape(img.get("credit", "")))


def inserer_figures(blocs_html, figs):
    """Repartit les figures dans la section : apres le 1er paragraphe, puis espacees."""
    if not figs:
        return blocs_html
    out = list(blocs_html)
    n = sum(1 for b in out if not b.startswith("<aside"))  # les encadres ne deplacent pas les figures
    pos = [min(n, 1 + i * max(2, n // (len(figs) + 1))) for i in range(len(figs))]
    for k, (p, f) in enumerate(sorted(zip(pos, figs), key=lambda x: -x[0])):
        out.insert(p, figure(f))
    return out


def charger(nom, defaut):
    p = os.path.join(ICI, nom)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else defaut


def slug_terme(t):
    t = unicodedata.normalize("NFKD", t.replace("œ", "oe")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t.lower()).strip("-")


def lier_lexique(h):
    """Relie la premiere occurrence de chaque terme du lexique, hors liens, titres et legendes."""
    termes = charger("lexique.json", [])
    motifs = []
    for e in termes:
        for m in e.get("motifs", []):
            fl = 0 if m[:1].isupper() and not m.isupper() and m not in ("Logos",) else re.I
            motifs.append((slug_terme(e["terme"]), re.compile(r"(?<![\w-])(%s)(?![\w-])" % re.escape(html.escape(m, quote=False)), fl)))
    faits = set()
    morceaux = re.split(r"(<[^>]+>)", h)
    bloque = 0
    for i, m in enumerate(morceaux):
        if m.startswith("<"):
            nom = re.match(r"</?\s*([a-zA-Z0-9]+)", m)
            if nom and nom.group(1).lower() in ("a", "summary", "figcaption", "h1", "h2", "h3", "h4", "th", "button", "aside"):
                bloque += -1 if m.startswith("</") else (0 if m.endswith("/>") else 1)
            continue
        if bloque > 0 or not m.strip():
            continue
        poses = []
        for sl, rx in motifs:
            if sl in faits:
                continue
            r = rx.search(m)
            if r and not any(a < r.end() and r.start() < b for a, b, _ in poses):
                poses.append((r.start(), r.end(), sl))
                faits.add(sl)
        for a, b, sl in sorted(poses, reverse=True):
            m = m[:a] + '<a class="lex" href="lexique.html#%s" title="Voir le lexique">%s</a>' % (sl, m[a:b]) + m[b:]
        morceaux[i] = m
    return "".join(morceaux)


ROMAINS = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV",
           "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI"]


def siecle(y):
    n = (-y - 1) // 100 + 1 if y < 0 else (y - 1) // 100 + 1
    nom = "Ier" if n == 1 else ROMAINS[n] + "e"
    return "%s siècle%s" % (nom, " av. J.-C." if y < 0 else "")


def annee(dates):
    """Annee de tri tiree d'une chaine de dates ('428/427-348/347 av. J.-C.', 'né en 1946', 'v. 1260-1328')."""
    m = re.search(r"(\d{1,4})", dates)
    if not m:
        return None
    y = int(m.group(1))
    avant = re.match(r"^\D*\d+(?:/\d+)?\s*av\. J\.-C\.", dates) or ("av. J.-C." in dates and "ap." not in dates)
    return -y if avant else y


def personnes(titre):
    """'Strauss (1808-1874) et Bauer (1809-1882) : ...' -> [(nom, dates)]."""
    tete = titre.split(" : ")[0]
    return [(re.sub(r"^(et|,)\s+", "", n.strip()), d.strip())
            for n, d in re.findall(r"([^()]+?)\s*\(([^)]*\d[^)]*)\)", tete)]


def page_outil(nom, titre_page, intro, description, contenu, titre, og_image, version):
    tpl = open(os.path.join(ICI, "page.template.html"), encoding="utf-8").read()
    nav = " ".join('<a class="chip%s" href="%s">%s</a>' % (" actif" if f == nom else "", f, l)
                   for f, l in (("index.html", "L'essai"), ("frise.html", "Frise"), ("reponses.html", "Réponses"), ("lexique.html", "Lexique"),
                                ("bibliotheque.html", "Bibliothèque")))
    rempl = {"TITRE_PAGE": titre_page, "TITRE_BRUT": html.escape(titre), "DESCRIPTION": description,
             "OG_IMAGE": og_image, "NAV": nav, "INTRO": intro, "CONTENU": contenu}
    for k, v in rempl.items():
        tpl = tpl.replace("{{%s}}" % k, v)
    tpl = tpl.replace('href="css/style.css"', 'href="css/style.css?v=%s"' % version).replace(
        'src="js/pages.js"', 'src="js/pages.js?v=%s"' % version)
    open(os.path.join(RACINE, nom), "w", encoding="utf-8").write(tpl)


PARTICULES = ("La", "Le", "Les", "Du", "Des", "De", "Saint", "Sainte", "Van", "Von", "Di", "Da", "Del", "Della", "Mac", "Mc")
CLES_AUTEURS = {"Jean de la Croix": "jean de la croix", "Dante": "dante", "Jean Paul": "jean paul", "Angelus Silesius": "silesius",
                "Al-Maʿarrī": "maarri", "Abû l-ʿAlâʾ al-Maʿarrî": "maarri", "Lucien de Samosate": "lucien", "Rûmî": "rumi",
                "Omar Khayyâm": "khayyam", "Mme de Staël": "stael"}


def cle_auteur(nom):
    """Cle de tri d'un nom d'ecrivain : nom de famille (avec sa particule capitalisee), puis nom complet."""
    if nom in CLES_AUTEURS:
        return CLES_AUTEURS[nom]
    ws = nom.split()
    last = ws[-1]
    if len(ws) >= 2 and ws[-2] in PARTICULES:
        last = ws[-2] + " " + last
    return slug_terme(last) + " " + slug_terme(nom)


def pages_outils(titre, infos, version, og_image, ids, lettres=()):
    # ---------------------------------------------------------------- frise
    dates_sup = charger("auteurs.json", {})
    gens = []
    for s in infos:
        if s["id"] in dates_sup:
            for nom, d, y in dates_sup[s["id"]]:
                gens.append((y, nom, d, s))
            continue
        for nom, d in personnes(s["titre"]):
            y = annee(d)
            if y is not None:
                gens.append((y, nom, d, s))
    vus, uniques = set(), []
    for g in sorted(gens, key=lambda g: (g[0], g[1])):
        if g[1] in vus:
            continue
        vus.add(g[1])
        uniques.append(g)
    parties = []
    for s in infos:
        if s["partie"] not in [p[0] for p in parties]:
            parties.append((s["partie"], s["partie_titre"]))
    opts = '<option value="">Toutes les parties</option>' + "".join(
        '<option value="%s">%s</option>' % (pid, html.escape(pt.split(" : ")[0])) for pid, pt in parties
        if "partie" in pt.lower())
    h, cur = [], None
    for y, nom, d, s in uniques:
        sc = siecle(y)
        if sc != cur:
            if cur:
                h.append("</ol></section>")
            h.append('<section class="siecle" data-groupe><h2>%s</h2><ol class="frise">' % sc)
            cur = sc
        h.append('<li data-item data-partie="%s"><a href="index.html#%s"><span class="f-nom">%s</span>'
                 '<span class="f-dates">%s</span><span class="f-partie">%s</span></a></li>' % (
                     s["partie"], s["id"], html.escape(nom), html.escape(d), html.escape(s["partie_titre"])))
    h.append("</ol></section>")
    filtres = ('<div class="outil-filtres"><input type="search" data-filtre-texte placeholder="Chercher un auteur…" '
               'aria-label="Chercher un auteur"><select data-filtre-partie aria-label="Filtrer par partie">%s</select></div>' % opts)
    page_outil("frise.html", "Frise chronologique",
               "Les %d auteurs de l'essai, du plus ancien au plus récent. Un toucher sur un nom ouvre sa section." % len(uniques),
               "Frise chronologique des auteurs de l'essai.", filtres + "".join(h) + '<p id="aucun" hidden>Aucun auteur ne correspond.</p>',
               titre, og_image, version)

    # ---------------------------------------------------------------- reponses
    rel = charger("reponses.json", [])
    for r in rel:
        if r["section"] not in ids:
            print("  reponses.json : section inconnue", r["section"])
    noms = []
    for r in rel:
        for n in (r["de"], r["a"]):
            if n not in noms:
                noms.append(n)
    noms.sort(key=lambda n: slug_terme(n))
    cartes = []
    for n in noms:
        sort = [r for r in rel if r["de"] == n]
        entre = [r for r in rel if r["a"] == n]

        def li(r, autre):
            lab = "réponse attestée" if r["type"] == "attestee" else "confrontation construite"
            return ('<li data-item data-type="%s"><span class="r-type %s">%s</span> <a href="index.html#%s">%s</a>'
                    '<span class="r-note">%s</span></li>') % (r["type"], r["type"], lab, r["section"], html.escape(autre), en_ligne(r["note"]))
        blocs_html = ""
        if sort:
            blocs_html += "<h3>répond à</h3><ul>%s</ul>" % "".join(li(r, r["a"]) for r in sort)
        if entre:
            blocs_html += "<h3>reçoit une réponse de</h3><ul>%s</ul>" % "".join(li(r, r["de"]) for r in entre)
        cartes.append('<section class="rep-carte" data-groupe id="%s"><h2>%s</h2>%s</section>' % (slug_terme(n), html.escape(n), blocs_html))
    att = sum(1 for r in rel if r["type"] == "attestee")
    filtres = ('<div class="outil-filtres"><input type="search" data-filtre-texte placeholder="Chercher un auteur…" aria-label="Chercher">'
               '<div class="chips"><button class="chip" data-filtre-type="tous" aria-pressed="true">Toutes</button>'
               '<button class="chip" data-filtre-type="attestee" aria-pressed="false">Attestées</button>'
               '<button class="chip" data-filtre-type="construite" aria-pressed="false">Construites</button></div></div>')
    page_outil("reponses.html", "Qui répond à qui",
               "Les %d échanges que l'essai met en scène : %d réponses attestées, quand un auteur a réellement lu un autre et lui a répondu, et %d confrontations construites, quand l'essai fait se rencontrer deux pensées que l'histoire n'a pas mises face à face." % (len(rel), att, len(rel) - att),
               "Carte des réponses entre les auteurs de l'essai.", filtres + "".join(cartes) + '<p id="aucun" hidden>Aucun échange ne correspond.</p>',
               titre, og_image, version)

    # ---------------------------------------------------------------- lexique
    lex = sorted(charger("lexique.json", []), key=lambda e: slug_terme(e["terme"]))
    items = []
    for e in lex:
        if e["section"] not in ids:
            print("  lexique.json : section inconnue", e["section"])
        items.append('<div class="lex-entree" data-item id="%s"><dt>%s%s</dt><dd>%s <a class="lex-voir" href="index.html#%s">Lire dans l\'essai</a></dd></div>' % (
            slug_terme(e["terme"]), html.escape(e["terme"]),
            ' <span class="lex-langue">%s</span>' % en_ligne(e["langue"]) if e.get("langue") else "",
            en_ligne(e["definition"]), e["section"]))
    page_outil("lexique.html", "Lexique",
               "%d notions de l'essai, définies brièvement. Dans le texte, la première occurrence de chacune renvoie ici." % len(lex),
               "Lexique des notions de l'essai.",
               '<div class="outil-filtres"><input type="search" data-filtre-texte placeholder="Chercher une notion…" aria-label="Chercher une notion"></div>'
               '<dl class="lexique">%s</dl><p id="aucun" hidden>Aucune notion ne correspond.</p>' % "".join(items),
               titre, og_image, version)

    # ---------------------------------------------------------------- bibliotheque
    auteurs = {}
    for l in lettres:
        for aut, tit, reste, date in l["oeuvres"]:
            o = auteurs.setdefault(aut, {}).setdefault((tit, date), {"reste": reste, "sections": []})
            if (l["id"], l["nom"]) not in o["sections"]:
                o["sections"].append((l["id"], l["nom"]))
    cartes = []
    for aut in sorted(auteurs, key=cle_auteur):
        lis = []
        for (tit, date), o in sorted(auteurs[aut].items(), key=lambda kv: (kv[0][1], slug_terme(kv[0][0]))):
            liens = " · ".join('<a href="index.html#%s">%s</a>' % (sid, html.escape(nom)) for sid, nom in o["sections"])
            lis.append('<li data-item><em>%s</em>%s%s <span class="bib-liens">%s</span></li>' % (
                html.escape(tit), " " + html.escape(o["reste"]) if o["reste"] else "",
                " (%s)" % html.escape(date) if date else "", liens))
        cartes.append('<section class="rep-carte" data-groupe id="%s"><h2>%s</h2><ul class="bib-oeuvres">%s</ul></section>' % (
            slug_terme(aut), html.escape(aut), "".join(lis)))
    nb_oeuvres = sum(len(v) for v in auteurs.values())
    page_outil("bibliotheque.html", "Bibliothèque",
               "Les %d œuvres de %d écrivains convoquées dans les encadrés « En littérature » de l'essai, classées par auteur. "
               "Chaque œuvre renvoie à la section qui la cite." % (nb_oeuvres, len(auteurs)),
               "Bibliothèque des œuvres littéraires citées dans l'essai.",
               '<div class="outil-filtres"><input type="search" data-filtre-texte placeholder="Chercher un auteur ou une œuvre…" '
               'aria-label="Chercher un auteur ou une œuvre"></div>' + "".join(cartes) + '<p id="aucun" hidden>Aucune œuvre ne correspond.</p>',
               titre, og_image, version)


def construire(chemin, version=None):
    """Rend l'essai (index.html)."""
    titre, sous_titre, intro, parties = structurer(lire_article(chemin))
    images = charger_images()
    par_section = {}
    for im in images:
        par_section.setdefault((im["section"], im["role"]), []).append(im)

    ids_vus = set()

    def uid(base, prefixe):
        i = base or "section"
        if i in ids_vus:
            i = "%s-%s" % (prefixe, base)
        n = 2
        while i in ids_vus:
            i = "%s-%d" % (base, n)
            n += 1
        ids_vus.add(i)
        return i

    # Note d'introduction : on garde la convention de debat, pas celle des citations.
    a_propos = []
    for kind, ls in blocs(intro):
        if kind == "quote":
            txt = " ".join(re.sub(r"^>\s?", "", x) for x in ls)
            m = re.search(r"\*\*Convention de débat\.\*\*(.*)", txt)
            if m:
                a_propos.append(en_ligne(masquer_statuts(m.group(1)).strip()))

    sources_html, toc, corps, cartes = "", [], [], []
    total_mots, nb_parties = 0, 0
    infos = []  # sections, pour la frise
    lettres = []  # encadres litteraires, pour la bibliotheque
    for part in parties:
        pid = uid(slug(part["titre"]), "p")
        ptitre = part["titre"]
        if ptitre.startswith(RESUME):
            continue  # le resume de dix minutes n'est pas publie : seule la version integrale l'est
        if pid == "sources":
            secs = []
            for sec in part["sections"]:
                secs.append("<h3>%s</h3>" % en_ligne(sec["titre"]))
                secs += rendre_blocs(sec["lignes"])
            sources_html = "\n".join(rendre_blocs(part["lignes"]) + secs)
            continue
        label, _, sous = ptitre.partition(" : ")
        if "partie" in label.lower():
            nb_parties += 1
        intro_p = rendre_blocs(part["lignes"])
        pmots = sum(mots(x) for x in intro_p)
        secs_html, toc_secs, nb_auteurs = [], [], 0
        for f in par_section.get((pid, "figure"), []):
            intro_p.insert(min(1, len(intro_p)), figure(f))
        for sec in part["sections"]:
            base = slug(sec["titre"])
            sid = uid(base, pid)
            nom, dates, formule = analyser_titre(sec["titre"])
            infos.append({"id": sid, "titre": sec["titre"], "partie": pid, "partie_titre": ptitre})
            del LETTRES_BUF[:]
            corps_sec = rendre_blocs(sec["lignes"])
            if LETTRES_BUF:
                lettres.append({"id": sid, "nom": nom if dates else sec["titre"], "oeuvres": list(LETTRES_BUF)})
            smots = sum(mots(x) for x in corps_sec)
            pmots += smots
            portraits = par_section.get((base, "portrait"), [])
            est_auteur = bool(dates) or bool(portraits)
            nb_auteurs += 1 if est_auteur else 0
            corps_sec = inserer_figures(corps_sec, par_section.get((base, "figure"), []))
            if est_auteur:
                if portraits:
                    av = "".join('<img class="avatar" src="%s" alt="%s"%s loading="lazy">' % (
                        html.escape(p["file"]), html.escape(p.get("alt", nom)), attr_dims(p["file"])) for p in portraits)
                else:
                    av = '<span class="avatar avatar-init" aria-hidden="true">%s</span>' % html.escape(initiales(nom))
                head = ('<span class="avatars">%s</span><span class="sec-titles">'
                        '<span class="sec-nom">%s</span>%s%s</span>') % (
                    av, en_ligne(nom),
                    '<span class="sec-dates">%s</span>' % html.escape(dates) if dates else "",
                    '<span class="sec-formule">%s</span>' % en_ligne(formule) if formule else "")
                credits = "".join('<p class="portrait-credit">Portrait : %s</p>' % html.escape(p.get("credit", ""))
                                  for p in portraits)
            else:
                head = '<span class="sec-titles"><span class="sec-nom">%s</span></span>' % en_ligne(sec["titre"])
                credits = ""
            secs_html.append(
                '<details class="section%s" id="%s" data-partie="%s" open><summary>%s'
                '<span class="sec-side"><span class="sec-time">%d min</span>%s</span></summary>'
                '<div class="sec-body">%s%s</div></details>' % (
                    " auteur" if est_auteur else "", sid, pid, head,
                    max(1, round(smots / MOTS_MINUTE)), lien_btn(sid), "\n".join(corps_sec), credits))
            toc_secs.append('<li><a href="#%s" data-target="%s">%s%s</a></li>' % (
                sid, sid, en_ligne(nom if est_auteur else sec["titre"]),
                ' <small>%s</small>' % html.escape(dates) if dates else ""))
        total_mots += pmots
        minutes = max(1, round(pmots / MOTS_MINUTE))
        meta = "%s%d min de lecture" % ("%d auteurs · " % nb_auteurs if nb_auteurs else "", minutes)
        corps.append(
            '<details class="partie" id="%s"><summary><span class="part-label">%s</span>'
            '<span class="part-sub">%s</span><span class="part-meta">%s</span>%s</summary>'
            '<div class="part-body">%s%s<p class="part-end"><a href="#%s" data-target="%s">Haut de la partie</a></p></div></details>' % (
                pid, en_ligne(label), en_ligne(sous), meta, lien_btn(pid),
                "\n".join(intro_p), "\n".join(secs_html), pid, pid))
        toc.append('<li class="toc-part"><a href="#%s" data-target="%s">%s%s</a>%s</li>' % (
            pid, pid, en_ligne(ptitre),
            '<span class="toc-count" data-count="%s"></span>' % pid if toc_secs else "",
            "<ul>%s</ul>" % "".join(toc_secs) if toc_secs else ""))
        card_img = par_section.get((pid, "partcard"), [])
        cartes.append(
            '<a class="card" href="#%s" data-target="%s">%s<span class="card-text">'
            '<span class="card-label">%s</span><span class="card-sub">%s</span>'
            '<span class="card-meta">%s</span></span></a>' % (
                pid, pid,
                '<img src="%s" alt=""%s loading="lazy">' % (html.escape(card_img[0]["file"]), attr_dims(card_img[0]["file"])) if card_img else "",
                en_ligne(label), en_ligne(sous), meta))

    credits_imgs = "".join(
        '<li><a href="%s" rel="noopener">%s</a> : %s</li>' % (
            html.escape(i.get("source", "")), html.escape(i.get("alt", "") or i["file"]),
            html.escape(i.get("credit", "")))
        for i in images)
    cover = par_section.get(("cover", "cover"), [])
    heures = total_mots / MOTS_MINUTE / 60
    corps_html = lier_lexique("\n".join(corps))
    tpl = open(os.path.join(ICI, "template.html"), encoding="utf-8").read()
    version = version or str(int(time.time()))
    duree = "%d h %02d" % divmod(round(heures * 60), 60)
    comment = ("<p>L'essai se compose d'un prologue, de %s parties et d'une conclusion. "
               "Chaque partie se déplie d'un toucher ; à l'intérieur, chaque auteur a sa section, elle aussi repliable. "
               "Le bouton en haut à gauche ouvre le sommaire, où l'on peut chercher un auteur par son nom, et la loupe cherche dans tout le texte. "
               "La page retient où vous en êtes, et le sommaire coche les sections déjà lues. Le petit bouton en forme de chaîne, "
               "à côté de chaque titre, copie le lien direct vers la section. Depuis le sommaire, on peut aussi rendre tout l'essai, "
               "images comprises, lisible hors connexion. Les encadrés « En littérature », repliés, proposent dans chaque section "
               "une ou plusieurs œuvres littéraires qui illustrent le propos ; on peut les ouvrir ou les ignorer. "
               "Une frise, une carte des réponses, un lexique et une bibliothèque des œuvres citées "
               "complètent la lecture.</p>") % NOMBRES.get(nb_parties, str(nb_parties))
    rempl = {
        "TITRE": en_ligne(titre),
        "TITRE_BRUT": html.escape(titre),
        "SOUS_TITRE": en_ligne(sous_titre),
        "COUVERTURE": figure(cover[0], "cover") if cover else "",
        "MOTS": "{:,}".format(total_mots).replace(",", " "),
        "DUREE": duree,
        "COMMENT_LIRE": comment,
        "STORE": "sdr-",
        "TITRE_ONGLET": html.escape(titre),
        "PAGE": "index.html",
        "A_PROPOS": "".join("<p>%s</p>" % x for x in a_propos),
        "CARTES": "\n".join(cartes),
        "TOC": "\n".join(toc),
        "CORPS": corps_html,
        "SOURCES": sources_html,
        "CREDITS": "<ul>%s</ul>" % credits_imgs if credits_imgs else "<p>Aucune image.</p>",
        "NB_PARTIES": NOMBRES.get(nb_parties, str(nb_parties)),
        "BASE_URL": BASE_URL,
        "OG_IMAGE": BASE_URL + (cover[0]["file"] if cover else ""),
        "OG_W": str(dimensions(cover[0]["file"])[0]) if cover else "",
        "OG_H": str(dimensions(cover[0]["file"])[1]) if cover else "",
    }
    tpl = tpl.replace('href="css/style.css"', 'href="css/style.css?v=%s"' % version).replace('src="js/app.js"', 'src="js/app.js?v=%s"' % version)
    for k, v in rempl.items():
        tpl = tpl.replace("{{%s}}" % k, v)
    open(os.path.join(RACINE, "index.html"), "w", encoding="utf-8").write(tpl)
    print("index.html : %d mots, %d parties, %s de lecture" % (total_mots, len(corps), duree))
    return {"titre": titre, "infos": infos, "ids": ids_vus, "version": version, "og": rempl["OG_IMAGE"], "duree": duree,
            "lettres": lettres}


def tout_construire(article=ARTICLE):
    version = str(int(time.time()))
    r = construire(article, version=version)
    pages_outils(r["titre"], r["infos"], version, r["og"], r["ids"], r["lettres"])
    sw = open(os.path.join(ICI, "sw.template.js"), encoding="utf-8").read()
    open(os.path.join(RACINE, "sw.js"), "w", encoding="utf-8").write(sw.replace("{{VERSION}}", version))


if __name__ == "__main__":
    tout_construire(sys.argv[1] if len(sys.argv) > 1 else ARTICLE)
