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


def rendre_blocs(lignes):
    h = []
    for kind, ls in blocs(lignes):
        if kind == "table":
            h.append(rendre_table(ls))
        elif kind == "list":
            items = [re.sub(r"^\s*[-*] ", "", x) for x in ls]
            h.append("<ul>" + "".join("<li>%s</li>" % en_ligne(masquer_statuts(i))
                                      for i in items) + "</ul>")
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
    n = len(out)
    pos = [min(n, 1 + i * max(2, n // (len(figs) + 1))) for i in range(len(figs))]
    for k, (p, f) in enumerate(sorted(zip(pos, figs), key=lambda x: -x[0])):
        out.insert(p, figure(f))
    return out


def construire(chemin):
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
    total_mots, nb_parties, resume_id = 0, 0, ""
    for part in parties:
        pid = uid(slug(part["titre"]), "p")
        ptitre = part["titre"]
        if pid == "sources":
            secs = []
            for sec in part["sections"]:
                secs.append("<h3>%s</h3>" % en_ligne(sec["titre"]))
                secs += rendre_blocs(sec["lignes"])
            sources_html = "\n".join(rendre_blocs(part["lignes"]) + secs)
            continue
        label, _, sous = ptitre.partition(" : ")
        est_resume = ptitre.startswith(RESUME)
        if est_resume:
            resume_id = pid
            label, sous = "Pour commencer", ptitre
        elif "partie" in label.lower():
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
            corps_sec = rendre_blocs(sec["lignes"])
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
        if est_resume:
            meta = "%d min de lecture" % minutes
        corps.append(
            '<details class="partie%s" id="%s"%s><summary><span class="part-label">%s</span>'
            '<span class="part-sub">%s</span><span class="part-meta">%s</span>%s</summary>'
            '<div class="part-body">%s%s<p class="part-end"><a href="#%s" data-target="%s">Haut de la partie</a></p></div></details>' % (
                " resume" if est_resume else "", pid, " open" if est_resume else "",
                en_ligne(label), en_ligne(sous), meta, lien_btn(pid),
                "\n".join(intro_p), "\n".join(secs_html), pid, pid))
        toc.append('<li class="toc-part"><a href="#%s" data-target="%s">%s%s</a>%s</li>' % (
            pid, pid, en_ligne(ptitre),
            '<span class="toc-count" data-count="%s"></span>' % pid if toc_secs else "",
            "<ul>%s</ul>" % "".join(toc_secs) if toc_secs else ""))
        if est_resume:
            continue
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
    tpl = open(os.path.join(ICI, "template.html"), encoding="utf-8").read()
    version = str(int(time.time()))
    rempl = {
        "TITRE": en_ligne(titre),
        "TITRE_BRUT": html.escape(titre),
        "SOUS_TITRE": en_ligne(sous_titre),
        "COUVERTURE": figure(cover[0], "cover") if cover else "",
        "MOTS": "{:,}".format(total_mots).replace(",", " "),
        "DUREE": "%d h %02d" % divmod(round(heures * 60), 60),
        "A_PROPOS": "".join("<p>%s</p>" % x for x in a_propos),
        "CARTES": "\n".join(cartes),
        "TOC": "\n".join(toc),
        "CORPS": "\n".join(corps),
        "SOURCES": sources_html,
        "CREDITS": "<ul>%s</ul>" % credits_imgs if credits_imgs else "<p>Aucune image.</p>",
        "NB_PARTIES": NOMBRES.get(nb_parties, str(nb_parties)),
        "RESUME_BTN": ('<a class="btn" href="#%s" data-target="%s">%s</a>' % (resume_id, resume_id, RESUME)) if resume_id else "",
        "BASE_URL": BASE_URL,
        "OG_IMAGE": BASE_URL + (cover[0]["file"] if cover else ""),
        "OG_W": str(dimensions(cover[0]["file"])[0]) if cover else "",
        "OG_H": str(dimensions(cover[0]["file"])[1]) if cover else "",
    }
    tpl = tpl.replace('href="css/style.css"', 'href="css/style.css?v=%s"' % version).replace('src="js/app.js"', 'src="js/app.js?v=%s"' % version)
    for k, v in rempl.items():
        tpl = tpl.replace("{{%s}}" % k, v)
    open(os.path.join(RACINE, "index.html"), "w", encoding="utf-8").write(tpl)
    sw = open(os.path.join(ICI, "sw.template.js"), encoding="utf-8").read()
    sw = sw.replace("{{VERSION}}", version)
    open(os.path.join(RACINE, "sw.js"), "w", encoding="utf-8").write(sw)
    print("index.html : %d mots, %d parties, %d images" % (total_mots, len(corps), len(images)))


if __name__ == "__main__":
    construire(sys.argv[1] if len(sys.argv) > 1 else ARTICLE)
