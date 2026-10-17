#!/usr/bin/env python3
"""Construit index.html et les pages outils a partir de l'essai en Markdown.

Usage : python3 build/build.py [chemin/vers/article.md]

Sans dependance. Convertit le sous-ensemble de Markdown employe par l'essai
(titres, paragraphes, italique, gras, citations, listes, tableaux), masque les
statuts de citation entre crochets, et insere les images decrites dans
build/images.json. Les annexes (build/annexes/*.md) donnent la page annexes.html.
"""
import hashlib
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
ARTICLE = os.path.join(RACINE, "texte", "sortir-de-la-religion.md")
BASE_URL = "https://thomasgourouza.github.io/sortir-de-la-religion/"
RESUME = "L'essai en dix minutes"

# ---------------------------------------------------------------- langues
# Le français est la source et l'identité du site : ids, portraits, dates de tri, écrivains, artistes se résolvent
# toujours par la structure française. Une traduction (i18n/<langue>/) ne fournit que l'affichage ; le build
# l'aligne par position sur la source française et la publie dans le dossier <langue>/ avec les mêmes fichiers.
LANGUES = (("fr", "Français", "fr_FR"), ("en", "English", "en_GB"), ("ru", "Русский", "ru_RU"),
           ("de", "Deutsch", "de_DE"), ("es", "Español", "es_ES"))
LANG = "fr"
LANGUES_CONSTRUITES = ["fr"]
I18N = {}


def dossier_langue(l):
    return os.path.join(RACINE, "i18n", l)


def langue_disponible(l):
    return l == "fr" or os.path.exists(os.path.join(dossier_langue(l), "article.md"))


def charger_langue(l):
    """Rend la langue l courante : tables de l'interface, des noms, des dates, des légendes, des notes, du lexique."""
    global LANG, I18N
    LANG, I18N = l, {}
    _MOTIFS_COMPILES.clear()
    if l == "fr":
        return
    d = dossier_langue(l)

    def j(nom, defaut):
        p = os.path.join(d, nom)
        return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else defaut
    I18N["ui"] = j("ui.json", {})
    donnees = j("donnees-noms.json", {})
    I18N["noms"] = donnees.get("noms", {})
    I18N["dates"] = donnees.get("dates", {})
    I18N["reponses"] = donnees.get("reponses", [])
    I18N["images"] = j("donnees-images.json", {})
    lex = []
    dl = os.path.join(d, "lexique")
    for f in sorted(os.listdir(dl)) if os.path.isdir(dl) else []:
        if f.endswith(".json"):
            lex += json.load(open(os.path.join(dl, f), encoding="utf-8"))
    I18N["lexique"] = {e["fr"]: e for e in lex}
    exacts, motifs = {}, []
    for k, v in I18N["ui"].items():
        if "{n}" in k or "{s}" in k:
            rx = re.escape(k).replace(re.escape("{n}"), r"(\d+)").replace(re.escape("{s}"), r"(.+?)")
            motifs.append((re.compile("^" + rx + "$", re.S), v))
        else:
            exacts[k] = v
    table = dict(I18N["noms"])
    table.update(I18N["dates"])
    table.update(exacts)
    I18N["table"], I18N["motifs_ui"] = table, motifs


def T(s):
    """Une chaîne de l'interface dans la langue courante (le français si elle n'est pas traduite)."""
    return I18N.get("ui", {}).get(s, s) if LANG != "fr" else s


def N(nom):
    """Un nom propre dans la langue courante."""
    return I18N.get("noms", {}).get(nom, nom) if LANG != "fr" else nom


def _traduire_texte(s):
    t = I18N["table"]
    if s in t:
        return t[s]
    u = html.unescape(s)
    if u in t:
        return html.escape(t[u], quote=False)
    for rx, v in I18N["motifs_ui"]:
        m = rx.match(u)
        if m:
            out, i = v, 0
            for g in m.groups():
                out = re.sub(r"\{[ns]\}", lambda _: g, out, count=1)
            return html.escape(out, quote=False)
    return None


ATTRS_TRADUITS = re.compile(r'\b(aria-label|placeholder|title|content|data-label)="([^"]*)"')


def localiser(h):
    """Traduit l'interface d'une page déjà rendue (nœuds de texte et attributs entiers) et pointe ses ressources
    vers la racine du site. Le contenu traduit vient d'ailleurs : ici, seules les chaînes exactes changent."""
    if LANG == "fr":
        return h
    h = re.sub(r'((?:src|href|data-grand)=")(?=(?:css|js|images)/|favicon\.svg|apple-touch-icon\.png)', r"\1../", h)
    code = next(c for c, _, _ in LANGUES if c == LANG)
    h = h.replace('<html lang="fr">', '<html lang="%s" data-racine="../">' % code, 1)
    h = h.replace('content="fr_FR"', 'content="%s"' % next(loc for c, _, loc in LANGUES if c == LANG))
    morceaux = re.split(r"(<[^>]+>)", h)
    dans_script = False
    for i, m in enumerate(morceaux):
        if m.startswith("<"):
            low = m[:8].lower()
            if low.startswith("<script") or low.startswith("<style"):
                dans_script = True
            elif low.startswith("</scrip") or low.startswith("</style"):
                dans_script = False
            elif "=" in m:
                def attr(a):
                    v = _traduire_texte(a.group(2).strip())
                    return '%s="%s"' % (a.group(1), html.escape(html.unescape(v), quote=True)) if v is not None else a.group(0)
                morceaux[i] = ATTRS_TRADUITS.sub(attr, m)
            continue
        if dans_script or not m.strip():
            continue
        s = m.strip()
        v = _traduire_texte(s)
        if v is not None:
            morceaux[i] = m.replace(s, v, 1)
    return "".join(morceaux)


def sortie(nom):
    """Chemin d'écriture d'une page dans la langue courante."""
    d = RACINE if LANG == "fr" else os.path.join(RACINE, LANG)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, nom)


def ecrire_page(nom, contenu):
    open(sortie(nom), "w", encoding="utf-8").write(localiser(contenu))


def selecteur_langues(page):
    """Menu des langues construites, chacune liée à la même page (l'ancre est ajoutée au clic par sauts.js)."""
    if len(LANGUES_CONSTRUITES) < 2:
        return ""
    liens = []
    for code, nom, _ in LANGUES:
        if code in LANGUES_CONSTRUITES:
            href = ("" if LANG == "fr" else "../") + ("" if code == "fr" else code + "/") + page
            liens.append('<a class="langue" href="%s" hreflang="%s" lang="%s" data-langue="%s"%s>%s</a>' % (
                href, code, code, code, ' aria-current="true"' if code == LANG else "", nom))
    return ('<div class="langues"><button class="icon-btn langue-btn" type="button" aria-haspopup="true" aria-expanded="false" '
            'aria-label="Changer de langue">%s</button><div class="langues-menu" hidden>%s</div></div>') % (LANG.upper(), "".join(liens))


def hreflangs(page):
    """Balises <link rel="alternate" hreflang> de la page dans toutes les langues construites."""
    out = []
    for code, _, _ in LANGUES:
        if code in LANGUES_CONSTRUITES and len(LANGUES_CONSTRUITES) > 1:
            out.append('<link rel="alternate" hreflang="%s" href="%s%s%s">' % (code, BASE_URL, "" if code == "fr" else code + "/", page))
    if out:
        out.append('<link rel="alternate" hreflang="x-default" href="%s%s">' % (BASE_URL, page))
    return "\n".join(out)


def ui_js():
    """Table des chaînes de l'interface pour les scripts (window.SDR_UI)."""
    return json.dumps(I18N.get("ui", {}), ensure_ascii=False).replace("</", "<\\/") if LANG != "fr" else "{}"

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
    """Retire les commentaires HTML et les crochets de statut, garde les ellipses et les courtes insertions."""
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
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
LETTRES_OEUVRE = re.compile(r"^(.+?), (?:\*(.+?)\*|«\s?(.+?)\s?»|“(.+?)”|„(.+?)“)(.*?)\s*(?:\((\d[^)]*)\))?\s*$")
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
        LETTRES_BUF.append((m.group(1).strip(), m.group(2) or m.group(3) or m.group(4) or m.group(5), m.group(6).strip(), m.group(7) or ""))
    corps = []
    for p in paras[1:]:
        classe = ' class="lettres-source"' if re.match(r"(?:Sources?|Источник(?:и)?|Quellen?|Fuentes?)\s*:", p) else ""
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


def partition_titre(t):
    """Coupe un titre à son premier deux-points : « Nom : formule » en français, « Name: formula » ailleurs."""
    if " : " in t:
        return t.partition(" : ")
    a, s, c = t.partition(": ")
    return (a, " : ", c) if s else (t, "", "")


def analyser_titre(t):
    """'Hegel (1770-1831) : formule' -> (nom, dates, formule)."""
    nom, _, formule = partition_titre(t)
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


_EMPREINTES = {}


def src_img(chemin):
    """URL d'une image avec une empreinte de son contenu : le service worker garde les images en cache
    tant que l'URL ne change pas, l'empreinte force le rechargement d'un fichier remplacé sous le même nom."""
    if chemin not in _EMPREINTES:
        p = os.path.join(RACINE, chemin)
        _EMPREINTES[chemin] = hashlib.sha1(open(p, "rb").read()).hexdigest()[:8] if os.path.exists(p) else ""
    e = _EMPREINTES[chemin]
    return html.escape(chemin) + ("?h=" + e if e else "")


def lien_btn(cible):
    return ('<button class="lien-btn" type="button" data-lien="%s" aria-label="Copier le lien de cette section">'
            '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true"><path d="M10 14a4 4 0 0 0 5.66 0l3-3a4 4 0 0 0-5.66-5.66l-1 1M14 10a4 4 0 0 0-5.66 0l-3 3a4 4 0 0 0 5.66 5.66l1-1" '
            'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>') % cible


def charger_images():
    p = os.path.join(ICI, "images.json")
    if not os.path.exists(p):
        return []
    imgs = [i for i in json.load(open(p, encoding="utf-8")) if os.path.exists(os.path.join(RACINE, i["file"]))]
    for i in imgs:
        i["alt_fr"] = i.get("alt", "")
        tr = I18N.get("images", {}).get(i["file"]) or I18N.get("images", {}).get(i["file"].replace("-grand.", "."))
        if LANG != "fr" and tr:
            i["caption"], i["alt"] = tr.get("caption", i.get("caption", "")), tr.get("alt", i.get("alt", ""))
    return imgs


def figure(img, classe="figure"):
    charge = 'loading="eager" fetchpriority="high"' if classe == "cover" else 'loading="lazy" decoding="async"'
    position = ' style="object-position:%s"' % html.escape(img["position"]) if img.get("position") else ""  # point de cadrage
    return ('<figure class="%s"><img src="%s" alt="%s"%s %s%s>'
            '<figcaption>%s<span class="credit">%s</span></figcaption></figure>') % (
        classe, src_img(img["file"]), html.escape(img.get("alt", "")), attr_dims(img["file"]), charge, position,
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


CATEGORIES = (("theories", "Théories des auteurs"), ("bible", "Bible : les textes"), ("histoire", "Histoire"),
              ("disciplines", "Disciplines et méthodes"), ("courants", "Courants et doctrines"))
CHAMPS_LISTE = ("sections", "motifs", "references", "oeuvres")


def lexique_courant():
    """Le lexique dans la langue courante : entrées françaises (section d'ancrage, ordre), texte traduit s'il existe."""
    lex = charger("lexique.json", [])
    if LANG == "fr":
        return lex
    out = []
    for e in lex:
        tr = I18N.get("lexique", {}).get(e["terme"])
        if not tr:
            print("  lexique %s : notion non traduite, gardée en français : %s" % (LANG, e["terme"]))
            out.append(e)
            continue
        n = dict(e)
        for k in ("terme", "motifs", "definition"):
            n[k] = tr.get(k, e[k])
        if tr.get("langue") or e.get("langue"):
            n["langue"] = tr.get("langue", e.get("langue", ""))
        n["slug"] = slug_terme(e["terme"])  # ancre identique dans toutes les langues
        out.append(n)
    return out


def charger_annexes():
    """Lit build/annexes/*.md : un article par fichier, en-tete entre deux lignes ---, puis le corps en Markdown.

    Champs de l'en-tete : titre et categorie (obligatoires), ordre (entier), sections (ids de sections ou de
    parties de l'essai), motifs (chaines a relier dans le texte), references ; les listes sont separees par « ; ».
    """
    dossier = os.path.join(ICI, "annexes")
    out = []
    if not os.path.isdir(dossier):
        return out
    for f in sorted(os.listdir(dossier)):
        if not f.endswith(".md"):
            continue
        source = os.path.join(dossier, f)
        if LANG != "fr":
            tr = os.path.join(dossier_langue(LANG), "annexes", f)
            if os.path.exists(tr):
                a_fr = lire_annexe(source, f, verifier=False)
                a = lire_annexe(tr, f, verifier=False)
                if a and a_fr:
                    for k in ("categorie", "ordre", "sections", "oeuvres"):
                        a[k] = a_fr[k]
                    out.append(a)
                    continue
            print("  annexes %s : article non traduit, gardé en français : %s" % (LANG, f))
        a = lire_annexe(source, f, verifier=LANG == "fr")
        if a:
            out.append(a)
    out.sort(key=lambda a: (a["ordre"], slug_terme(a["titre"])))
    return out


def lire_annexe(chemin, f, verifier=True):
    """Un article d'annexe : en-tête entre deux lignes ---, puis le corps en Markdown."""
    if True:
        lignes = open(chemin, encoding="utf-8").read().split("\n")
        fin = next((i for i, l in enumerate(lignes) if i > 0 and l.strip() == "---"), None)
        if not lignes or lignes[0].strip() != "---" or fin is None:
            print("  annexes/%s : en-tête manquant" % f)
            return None
        a = {"id": f[:-3], "titre": "", "categorie": "", "ordre": 0, "sections": [], "motifs": [], "references": [], "oeuvres": [],
             "lignes": lignes[fin + 1:]}
        for l in lignes[1:fin]:
            m = re.match(r"^([a-z]+):\s*(.*)$", l)
            if not m:
                continue
            k, v = m.group(1), m.group(2).strip()
            if k in CHAMPS_LISTE:
                a[k] = [x.strip() for x in v.split(" ; ") if x.strip()]
            elif k == "ordre":
                a[k] = int(v) if v.isdigit() else 0
            elif k in ("titre", "categorie"):
                a[k] = v
        if verifier:
            for k in ("titre", "categorie"):
                if not a[k]:
                    print("  annexes/%s : champ « %s » manquant" % (f, k))
            if a["categorie"] not in dict(CATEGORIES):
                print("  annexes/%s : catégorie inconnue « %s »" % (f, a["categorie"]))
            n = len(" ".join(a["lignes"]).split())
            if not 400 <= n <= 700:
                print("  annexes/%s : %d mots (attendu : 400 à 700)" % (f, n))
        return a


def cibles_liaison(annexes=(), lexique=True):
    """Cibles de la liaison automatique : (slug, page, motifs, classe), le lexique d'abord, puis les annexes."""
    c = []
    if lexique:
        for e in lexique_courant():
            c.append((e.get("slug", slug_terme(e["terme"])), "lexique.html", e.get("motifs", []), "lex"))
    for a in annexes:
        c.append((a["id"], "annexes.html", a["motifs"], "ann"))
    return c


SCOPE_RX = re.compile(r'<details class="(?:section|partie)[^"]*" id="([^"]+)"')
BLOQUANTES = ("a", "summary", "figcaption", "h1", "h2", "h3", "h4", "th", "button", "aside")
TITRES_LIENS = {"lexique.html": "Voir le lexique", "annexes.html": "Voir les annexes"}


_MOTIFS_COMPILES = {}


def motifs_compiles(cibles):
    """Compile une fois les motifs d'une liste de cibles (la compilation dominait le temps de build)."""
    cle = tuple((sl, page, tuple(ms), classe) for sl, page, ms, classe in cibles)
    if cle not in _MOTIFS_COMPILES:
        motifs = []
        for sl, page, ms, classe in cibles:
            for m in ms:
                fl = 0 if m[:1].isupper() and not m.isupper() and m not in ("Logos",) else re.I
                lit = html.escape(m, quote=False)
                # (cible, classe, regex, littéral de préfiltrage, insensible à la casse)
                motifs.append(((page, sl), classe, re.compile(r"(?<![\w-])(%s)(?![\w-])" % re.escape(lit), fl), lit.lower() if fl else lit, bool(fl)))
        _MOTIFS_COMPILES[cle] = motifs
    return _MOTIFS_COMPILES[cle]


def lier(h, cibles, scope_self=None):
    """Relie la premiere occurrence de chaque cible dans chaque section (ou partie), hors liens, titres et legendes.

    Le scope change a chaque balise <details class="section"> ou <details class="partie"> rencontree ; un texte
    sans ces balises (definition du lexique, article d'annexe) forme un seul scope. scope_self = (page, slug)
    exclut la cible qu'on est en train de rendre.
    """
    motifs = motifs_compiles(cibles)
    faits = set()
    scope = ""
    morceaux = re.split(r"(<[^>]+>)", h)
    bloque = 0
    for i, m in enumerate(morceaux):
        if m.startswith("<"):
            s = SCOPE_RX.match(m)
            if s:
                scope = s.group(1)
            nom = re.match(r"</?\s*([a-zA-Z0-9]+)", m)
            if nom and nom.group(1).lower() in BLOQUANTES:
                bloque += -1 if m.startswith("</") else (0 if m.endswith("/>") else 1)
            continue
        if bloque > 0 or not m.strip():
            continue
        m_bas = m.lower()
        # pour chaque cible, sa première occurrence dans ce morceau (ordre des motifs en cas d'égalité)
        cands = {}
        for rang, (cle, classe, rx, lit, ci) in enumerate(motifs):
            if cle == scope_self or (scope, cle) in faits:
                continue
            if lit not in (m_bas if ci else m):  # préfiltrage : évite la regex quand le motif est absent
                continue
            r = rx.search(m)
            if r and (cle not in cands or r.start() < cands[cle][0]):
                cands[cle] = (r.start(), r.end(), cle, classe, rang)
        # chevauchements : le lexique d'abord, puis le motif le plus long (« Évangile de Jean » plutôt
        # que « Évangile »), puis l'ordre des motifs ; une cible écartée reste libre pour la suite de la section
        poses = []
        for a0, b0, cle, classe, rang in sorted(cands.values(), key=lambda c: (c[3] != "lex", -(c[1] - c[0]), c[4])):
            if not any(a < b0 and a0 < b for a, b, _, _ in poses):
                poses.append((a0, b0, cle, classe))
                faits.add((scope, cle))
        for a, b, (page, sl), classe in sorted(poses, reverse=True):
            m = m[:a] + '<a class="%s" href="%s#%s" title="%s">%s</a>' % (classe, page, sl, TITRES_LIENS[page], m[a:b]) + m[b:]
        morceaux[i] = m
    return "".join(morceaux)


def ligne_annexes(annexes):
    """Ligne « Pour comprendre » placee en tete d'une section ou d'une partie."""
    if not annexes:
        return ""
    return '<p class="annexes-ligne">Pour comprendre : %s</p>\n' % " · ".join(
        '<a href="annexes.html#%s">%s</a>' % (a["id"], en_ligne(a["titre"].split(" : ")[0])) for a in annexes)


def rendre_annexe(a, libelles, cibles, vignette=None):
    """Rend un article d'annexe en <details> replie ; les sous-titres « #### » deviennent des <h3>."""
    morceaux, cur, sous = [], [], None
    for l in a["lignes"]:
        if l.startswith("#### "):
            morceaux.append((sous, cur))
            cur, sous = [], l[5:].strip()
        else:
            cur.append(l)
    morceaux.append((sous, cur))
    corps = []
    for t, ls in morceaux:
        if t:
            corps.append("<h3>%s</h3>" % en_ligne(t))
        corps += rendre_blocs(ls)
    corps_html = lier("\n".join(corps), cibles, scope_self=("annexes.html", a["id"]))
    essai = " · ".join('<a href="index.html#%s">%s</a>' % (s, html.escape(libelles[s])) for s in a["sections"] if s in libelles)
    refs = " ; ".join(en_ligne(r) for r in a["references"])
    galerie = "".join(vignette(f) for f in a.get("oeuvres", [])) if vignette else ""
    return ('<details class="annexe" data-item data-type="%s" id="%s"><summary><span class="annexe-titre">%s</span>'
            '<span class="annexe-cat">%s</span></summary><div class="annexe-corps">%s%s%s%s</div></details>') % (
        a["categorie"], a["id"], en_ligne(a["titre"]), dict(CATEGORIES).get(a["categorie"], a["categorie"]), corps_html,
        '<div class="annexe-oeuvres"><span>%s</span>%s</div>' % (T("Dans la Galerie :"), galerie) if galerie else "",
        '<p class="annexe-essai">%s %s</p>' % (T("Dans l'essai :"), essai) if essai else "",
        '<p class="annexe-refs">%s %s</p>' % (T("Pour aller plus loin :"), refs) if refs else "")


ROMAINS = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV",
           "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI"]


def siecle(y):
    n = (-y - 1) // 100 + 1 if y < 0 else (y - 1) // 100 + 1
    if LANG == "en":
        suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return "%d%s century%s" % (n, suf, " BCE" if y < 0 else "")
    if LANG == "ru":
        return "%s век%s" % (ROMAINS[n], " до н. э." if y < 0 else "")
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


PAGES_SITE = (("index.html", "L'essai"), ("auteurs.html", "Les auteurs"), ("lexique.html", "Lexique"),
              ("annexes.html", "Annexes"), ("bibliotheque.html", "Bibliothèque"), ("galerie.html", "Galerie"), ("sources.html", "Sources"))


def onglets(actif):
    """Onglets de navigation entre les pages du site, places dans le bandeau fixe de chaque page, puis le menu des langues."""
    return '<nav class="onglets" aria-label="Pages du site">%s</nav>%s' % ("".join(
        '<a class="onglet" href="%s"%s>%s</a>' % (f, ' aria-current="page"' if f == actif else "", l) for f, l in PAGES_SITE),
        selecteur_langues(actif))


def page_outil(nom, titre_page, intro, description, contenu, titre, og_image, version):
    tpl = open(os.path.join(ICI, "page.template.html"), encoding="utf-8").read()
    rempl = {"TITRE_PAGE": T(titre_page), "TITRE_BRUT": html.escape(titre), "DESCRIPTION": T(description),
             "OG_IMAGE": og_image, "ONGLETS": onglets(nom), "INTRO": intro, "CONTENU": contenu,
             "HREFLANG": hreflangs(nom), "UI": ui_js()}
    for k, v in rempl.items():
        tpl = tpl.replace("{{%s}}" % k, v)
    tpl = tpl.replace('href="css/style.css"', 'href="css/style.css?v=%s"' % version).replace(
        'src="js/pages.js"', 'src="js/pages.js?v=%s"' % version).replace('src="js/sauts.js"', 'src="js/sauts.js?v=%s"' % version).replace(
        'src="js/portrait.js"', 'src="js/portrait.js?v=%s"' % version)
    ecrire_page(nom, tpl)


PARTICULES = ("La", "Le", "Les", "Du", "Des", "De", "Saint", "Sainte", "Van", "Von", "Di", "Da", "Del", "Della", "Mac", "Mc")
CLES_AUTEURS = {"Jean de la Croix": "jean de la croix", "Dante": "dante", "Jean Paul": "jean paul", "Angelus Silesius": "silesius",
                "Al-Maʿarrī": "maarri", "Abû l-ʿAlâʾ al-Maʿarrî": "maarri", "Lucien de Samosate": "lucien", "Rûmî": "rumi",
                "Omar Khayyâm": "khayyam", "Mme de Staël": "stael"}


MOTS_VIDES = ("le", "la", "les", "de", "d", "du", "et")


def avatar_html(img, nom, petit=True):
    """Avatar rond : le portrait s'il existe, avec sa légende pour la fenêtre au survol, sinon les initiales."""
    cls = "avatar avatar-sm" if petit else "avatar"
    if img:
        return '<img class="%s" src="%s" alt="%s"%s data-legende="%s" loading="lazy">' % (
            cls, src_img(img["file"]), html.escape(img.get("alt", nom)), attr_dims(img["file"]), html.escape(img.get("caption", "")))
    return '<span class="%s avatar-init" aria-hidden="true">%s</span>' % (cls, html.escape(initiales(nom)))


def mots_nom(nom):
    return [w for w in slug(nom.split(" et ")[0]).split("-") if w and w not in MOTS_VIDES]


def meme_personne(a, b):
    """Deux noms désignent la même personne : même dernier mot (nom de famille) et les mots de l'un sont dans l'autre."""
    return bool(a) and bool(b) and a[-1] == b[-1] and (all(w in b for w in a) or all(w in a for w in b))


def redirection(nom, cible):
    """Page minimale qui renvoie vers une autre : garde vivants les anciens liens vers frise.html et reponses.html."""
    ecrire_page(nom,
        '<!doctype html>\n<html lang="fr"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=%s">'
        '<link rel="canonical" href="%s%s"><title>Redirection</title></head>'
        '<body><p>Cette page a été réunie à <a href="%s">Les auteurs</a>.</p></body></html>\n' % (cible, BASE_URL, cible, cible))


def portrait_de(nom, candidats):
    """Le portrait dont l'alt porte le nom : tous les mots du nom s'y retrouvent, de préférence avec le nom de famille en dernier."""
    mots = mots_nom(nom)
    if not mots:
        return None
    trouves = []
    for p in candidats:
        alt = [w for w in slug(p.get("alt_fr", p.get("alt", ""))).split("-") if w and w not in MOTS_VIDES + ("portrait",)]
        if alt and (all(w in alt for w in mots) or all(w in mots for w in alt)):
            trouves.append((0 if alt[-1] == mots[-1] else 1, p))
    return min(trouves, key=lambda x: x[0])[1] if trouves else None


def alias_de(a):
    """Noms d'un artiste qui peuvent ouvrir une légende : ses alias français et leur forme dans la langue courante."""
    al = list(a.get("alias", []))
    return al + [N(x) for x in al + [a["nom"]] if N(x) not in al]


def titre_oeuvre(legende, alias):
    """Titre d'une œuvre tiré de sa légende : avant le premier « : », sans le nom de l'artiste en tête."""
    t = legende.split(" : ")[0].rstrip(".")
    for a in sorted(alias, key=len, reverse=True):
        if t.startswith(a + ", "):
            return t[len(a) + 2:]
    return t


LIVRES_BIBLE = ("Gn", "Ex", "Lv", "Nb", "Dt", "Jos", "Jg", "Rt", "1 S", "2 S", "1 R", "2 R", "1 Ch", "2 Ch", "Esd", "Ne", "Est",
                "Tb", "Jdt", "1 M", "2 M", "Jb", "Ps", "Pr", "Qo", "Ct", "Sg", "Si", "Is", "Jr", "Lm", "Ba", "Ez", "Dn", "Os",
                "Jl", "Am", "Jon", "Mi", "Za", "Ml", "Mt", "Mc", "Lc", "Jn", "Ac", "Rm", "1 Co", "2 Co", "Ga", "Ep", "Ph", "Col",
                "1 Th", "2 Th", "1 Tm", "2 Tm", "Tt", "Phm", "He", "Jc", "1 P", "2 P", "1 Jn", "Jude", "Ap")
REF_BIBLE = re.compile(r"(?<![\w])(%s) (\d+)(?:, (\d+)(?:-\d+)?)?(?![\w-])" % "|".join(
    re.escape(l) for l in sorted(LIVRES_BIBLE, key=len, reverse=True)))


def annexe_du_passage(livre, ch):
    """L'annexe biblique qui explique un passage : par livre, et pour la Genèse et 1 Co 15 par chapitre."""
    if livre == "Gn":
        return "genese-creation-et-chute" if ch <= 3 else ("cain-deluge-et-babel" if ch <= 11 else "abraham-isaac-jacob")
    if livre == "1 Co" and ch == 15:
        return "passion-et-resurrection"
    table = {"Ex": "exode-moise-et-la-loi", "Lv": "sacrifice-dans-la-bible", "Nb": "exode-moise-et-la-loi", "Dt": "exode-moise-et-la-loi",
             "Jos": "juges-rois-david-salomon", "Jg": "juges-rois-david-salomon", "1 S": "juges-rois-david-salomon",
             "2 S": "juges-rois-david-salomon", "1 R": "juges-rois-david-salomon", "2 R": "juges-rois-david-salomon",
             "Rt": "livres-brefs-de-l-ancien-testament", "Est": "livres-brefs-de-l-ancien-testament", "Jon": "livres-brefs-de-l-ancien-testament",
             "Esd": "livres-brefs-de-l-ancien-testament", "Ne": "livres-brefs-de-l-ancien-testament", "Lm": "livres-brefs-de-l-ancien-testament",
             "Tb": "livres-brefs-de-l-ancien-testament", "Jdt": "livres-brefs-de-l-ancien-testament",
             "Jb": "psaumes-job-et-sagesse", "Ps": "psaumes-job-et-sagesse", "Pr": "psaumes-job-et-sagesse", "Qo": "psaumes-job-et-sagesse",
             "Ct": "psaumes-job-et-sagesse", "Sg": "intertestamentaire-et-qumran", "Si": "intertestamentaire-et-qumran",
             "1 M": "intertestamentaire-et-qumran", "2 M": "intertestamentaire-et-qumran", "Dn": "prophetes-et-daniel",
             "Mt": "evangiles-de-matthieu-et-de-luc", "Lc": "evangiles-de-matthieu-et-de-luc", "Mc": "evangile-de-marc", "Jn": "evangile-de-jean",
             "Ac": "actes-des-apotres", "He": "epitres-catholiques-et-hebreux", "Jc": "epitres-catholiques-et-hebreux",
             "1 P": "epitres-catholiques-et-hebreux", "2 P": "epitres-catholiques-et-hebreux", "1 Jn": "epitres-catholiques-et-hebreux",
             "Jude": "epitres-catholiques-et-hebreux", "Ap": "apocalypse-de-jean"}
    if livre in table:
        return table[livre]
    if livre in ("Rm", "1 Co", "2 Co", "Ga", "Ep", "Ph", "Col", "1 Th", "2 Th", "1 Tm", "2 Tm", "Tt", "Phm"):
        return "lettres-de-paul"
    return "prophetes-et-daniel"  # Is, Jr, Ez, Os, Am, Mi et les autres prophètes


def index_passages(textes, libelles, ids_annexes):
    """Tableau des passages bibliques cités par l'essai, dans l'ordre des livres : référence, section, annexe."""
    vus = {}
    for sid, texte in textes:
        for m in REF_BIBLE.finditer(texte):
            ref = m.group(0)
            cle = (LIVRES_BIBLE.index(m.group(1)), int(m.group(2)), int(m.group(3) or 0), ref)
            vus.setdefault(cle, [])
            if sid not in vus[cle]:
                vus[cle].append(sid)
    lignes = []
    for cle in sorted(vus):
        livre, ch = LIVRES_BIBLE[cle[0]], cle[1]
        aid = annexe_du_passage(livre, ch)
        if aid not in ids_annexes:
            print("  index des passages : pas d'annexe pour", cle[3])
            continue
        sections = " · ".join('<a href="index.html#%s">%s</a>' % (s, html.escape(libelles.get(s, s))) for s in vus[cle])
        lignes.append('<tr><td>%s</td><td>%s</td><td><a href="#%s">%s</a></td></tr>' % (
            html.escape(cle[3]), sections, aid, html.escape(ids_annexes[aid])))
    return lignes


def cle_auteur(nom):
    """Cle de tri d'un nom d'ecrivain : nom de famille (avec sa particule capitalisee), puis nom complet."""
    if nom in CLES_AUTEURS:
        return CLES_AUTEURS[nom]
    ws = nom.split()
    last = ws[-1]
    if len(ws) >= 2 and ws[-2] in PARTICULES:
        last = ws[-2] + " " + last
    return slug_terme(last) + " " + slug_terme(nom)


def pages_outils(titre, infos, version, og_image, ids, lettres=(), annexes=(), libelles=None, sources="", credits="",
                 tableau="", portraits=None, ecrivains=None, artistes=None, oeuvres=None, textes=(),
                 lettres_fr=None, tableau_fr=None):
    libelles = libelles or {}
    artistes = artistes or {}
    oeuvres = oeuvres or {}
    portraits = portraits or {}
    ecrivains = ecrivains or {}
    tous_portraits = [p for s in infos for p in portraits.get(s["id"], [])]
    # ---------------------------------------------------------------- les auteurs : annuaire chronologique
    # Une fiche par auteur, dans l'ordre de la frise ; chaque fiche réunit sa ligne du tableau du prologue (régime,
    # texte pivot, débat avec), le lien vers sa section et ses dialogues (reponses.json, sous les deux participants).
    dates_sup = charger("auteurs.json", {})
    infos_par_id = {s["id"]: s for s in infos}
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
    fiches, par_mots, vus = [], {}, set()

    def nouvelle_fiche(nom, dates="", y=None, sid=None, partie=None, partie_titre=""):
        f = {"nom": nom, "mots": tuple(mots_nom(nom)), "dates": dates, "annee": y, "sid": sid, "partie": partie or "",
             "partie_titre": partie_titre, "tableau": None, "sort": [], "entre": []}
        fiches.append(f)
        par_mots.setdefault(f["mots"], f)
        return f

    def fiche_pour(nom):
        """La fiche d'un nom : mêmes mots d'abord, sinon même personne (nom de famille commun, prénom compatible)."""
        mots = tuple(mots_nom(nom))
        if mots in par_mots:
            return par_mots[mots]
        return next((f for f in fiches if meme_personne(mots, f["mots"])), None)
    for y, nom, d, s in sorted(gens, key=lambda g: (g[0], g[1])):
        if nom in vus:
            continue
        vus.add(nom)
        nouvelle_fiche(nom, d, y, s["id"], s["partie"], s["partie_titre"])

    # le tableau du prologue : une ligne peut réunir plusieurs auteurs (« Celse (IIe s.) et Origène (…) »,
    # « Schweitzer, Drews, Couchoud, Ehrman ») ; une ligne sans fiche devient une fiche, datée si elle porte des dates
    def lignes_tableau(t):
        m = re.match(r"\s*<p>(.*?)</p>\s*", t, re.S)
        if m:
            t = t[m.end():]
        return ([re.sub(r"<[^>]+>", "", x) for x in re.findall(r"<th>(.*?)</th>", t, re.S)],
                [re.findall(r'<td data-label="[^"]*">(.*?)</td>', l, re.S) for l in re.findall(r"<tr>(.*?)</tr>", t, re.S)])
    entetes, rangs = lignes_tableau(tableau)
    rangs_fr = lignes_tableau(tableau_fr)[1] if tableau_fr else rangs
    if len(rangs_fr) != len(rangs):
        print("  traduction %s : le tableau des auteurs n'a pas le même nombre de lignes" % LANG)
        rangs_fr = rangs
    sans_fiche = []
    for cellules, cellules_fr in zip(rangs, rangs_fr):
        if len(cellules) < 2:
            continue
        texte_nu = html.unescape(re.sub(r"<[^>]+>", "", cellules_fr[0]))
        pers = personnes(texte_nu)
        noms = [n for n, d in pers] or [n.strip() for n in re.split(r",| et ", re.sub(r"\([^)]*\)", "", texte_nu)) if n.strip()]
        trouvees = [f for f in (fiche_pour(n) for n in noms) if f]
        if not trouvees:
            nom, d = (pers[0] if pers else (noms[0], ""))
            y = annee(d) if d else None
            sid = slug(texte_nu) if slug(texte_nu) in ids else None
            s = infos_par_id.get(sid)
            trouvees = [nouvelle_fiche(nom, d, y, sid, s["partie"] if s else None, s["partie_titre"] if s else "")]
            sans_fiche.append(texte_nu)
        for f in trouvees:
            if f["tableau"] is None:
                f["tableau"] = list(zip(entetes[1:], cellules[1:]))

    # les dialogues
    rel = charger("reponses.json", [])
    if LANG != "fr":
        notes = I18N.get("reponses", [])
        rel = [dict(r, note=notes[i]) if i < len(notes) else r for i, r in enumerate(rel)]
    for r in rel:
        if r["section"] not in ids:
            print("  reponses.json : section inconnue", r["section"])
        s = infos_par_id.get(r["section"])
        for cle, nom in (("sort", r["de"]), ("entre", r["a"])):
            f = fiche_pour(nom) or nouvelle_fiche(nom, partie=s["partie"] if s else None, partie_titre=s["partie_titre"] if s else "")
            f[cle].append(r)

    parties = []
    for s in infos:
        if s["partie"] not in [p[0] for p in parties]:
            parties.append((s["partie"], s["partie_titre"]))
    opts = '<option value="">Toutes les parties</option>' + "".join(
        '<option value="%s">%s</option>' % (pid, html.escape(pt)) for pid, pt in parties  # « Première partie : les Anciens… »
        if "partie" in pt.lower())

    datees = sorted([f for f in fiches if f["annee"] is not None], key=lambda f: (f["annee"], f["nom"]))
    autres = sorted([f for f in fiches if f["annee"] is None], key=lambda f: slug_terme(f["nom"]))
    ids_fiches = set()
    for f in datees + autres:  # identifiant de chaque fiche, ancre des liens entre fiches
        fid = slug_terme(f["nom"]) or "fiche"
        n = 2
        while fid in ids_fiches:
            fid = "%s-%d" % (slug_terme(f["nom"]), n)
            n += 1
        ids_fiches.add(fid)
        f["id"] = fid

    def li(r, autre):
        """Une ligne de dialogue : le nom renvoie à la fiche de l'interlocuteur, « Lire la section » à l'essai."""
        lab = "réponse attestée" if r["type"] == "attestee" else "confrontation construite"
        f = fiche_pour(autre)
        nom = '<a href="#%s">%s</a>' % (f["id"], html.escape(autre)) if f else html.escape(autre)
        return ('<li data-type="%s"><span class="r-type %s">%s</span> %s <a class="r-section" href="index.html#%s">Lire la section</a>'
                '<span class="r-note">%s</span></li>') % (r["type"], r["type"], lab, nom, r["section"], en_ligne(r["note"]))

    def rendre_fiche(f, siecle_id):
        fid = f["id"]
        img = portrait_de(f["nom"], portraits.get(f["sid"], [])) or portrait_de(f["nom"], tous_portraits)
        meta = []
        if f["partie_titre"]:
            meta.append(html.escape(f["partie_titre"]))
        if f["sid"]:
            meta.append('<a href="index.html#%s">Lire la section</a>' % f["sid"])
        h = ['<details class="rep-carte fiche" data-item data-partie="%s" data-siecle="%s" id="%s" open>'
             '<summary><h2>%s<span class="f-nom">%s</span>%s</h2></summary><div class="fiche-corps">' % (
                 f["partie"], siecle_id, fid, avatar_html(img, f["nom"]), html.escape(f["nom"]),
                 '<span class="f-dates">%s</span>' % html.escape(f["dates"]) if f["dates"] else "")]
        if meta:
            h.append('<p class="fiche-meta">%s</p>' % " · ".join(meta))
        if f["tableau"]:
            h.append('<dl class="fiche-tab">%s</dl>' % "".join("<dt>%s</dt><dd>%s</dd>" % (html.escape(k), v) for k, v in f["tableau"] if v.strip()))
        if f["sort"]:
            h.append("<h3>répond à</h3><ul>%s</ul>" % "".join(li(r, r["a"]) for r in f["sort"]))
        if f["entre"]:
            h.append("<h3>reçoit une réponse de</h3><ul>%s</ul>" % "".join(li(r, r["de"]) for r in f["entre"]))
        h.append("</div></details>")
        return "".join(h)
    h, cur, siecles = [], None, []
    for f in datees:
        sc = siecle(f["annee"])
        if sc != cur:
            if cur:
                h.append("</section>")
            siecles.append((slug(sc), sc))
            h.append('<section class="siecle" data-groupe><h2>%s</h2>' % sc)
            cur = sc
        h.append(rendre_fiche(f, slug(sc)))
    if cur:
        h.append("</section>")
    if autres:
        siecles.append(("autres", "Autres figures et interlocuteurs"))
        h.append('<section class="siecle" data-groupe><h2>Autres figures et interlocuteurs</h2>%s</section>' % "".join(
            rendre_fiche(f, "autres") for f in autres))
    att = sum(1 for r in rel if r["type"] == "attestee")
    opts_siecles = '<option value="">Toutes les périodes</option>' + "".join(
        '<option value="%s">%s</option>' % (sid, html.escape(lab)) for sid, lab in siecles)
    filtres = ('<div class="outil-filtres"><input type="search" data-filtre-texte placeholder="Chercher un auteur…" '
               'aria-label="Chercher un auteur"><select data-filtre-partie aria-label="Filtrer par partie">%s</select>'
               '<select data-filtre-siecle aria-label="Filtrer par période">%s</select>'
               '<button class="chip plier" type="button" id="plier-tout" aria-pressed="false">Tout replier</button></div>' % (opts, opts_siecles))
    page_outil("auteurs.html", "Les auteurs",
               "Les %d auteurs de l'essai, du plus ancien au plus récent : pour chacun, son régime de critique, son texte pivot, "
               "ses interlocuteurs, et les %d échanges que l'essai met en scène, %d réponses attestées, quand un auteur a réellement "
               "lu un autre et lui a répondu, et %d confrontations construites, quand l'essai fait se rencontrer deux pensées que "
               "l'histoire n'a pas mises face à face." % (len(datees), len(rel), att, len(rel) - att),
               "Les auteurs de l'essai : chronologie, régime de critique, texte pivot, dialogues.",
               filtres + "".join(h) + '<p id="aucun" hidden>Aucun auteur ne correspond.</p>', titre, og_image, version)
    redirection("frise.html", "auteurs.html")
    redirection("reponses.html", "auteurs.html")
    imprevues = [t for t in sans_fiche if t not in dates_sup.get("_tableau_seul", [])]
    if imprevues:
        print("  tableau des auteurs : lignes sans auteur de la frise, devenues fiches :", "; ".join(imprevues))

    # ---------------------------------------------------------------- lexique
    lex = sorted(lexique_courant(), key=lambda e: slug_terme(e["terme"]))
    cibles_ann = cibles_liaison(annexes, lexique=False)
    items = []
    for e in lex:
        if e["section"] not in ids:
            print("  lexique.json : section inconnue", e["section"])
        sl = e.get("slug", slug_terme(e["terme"]))
        items.append('<details class="lex-entree" data-item id="%s" open><summary><span class="lex-terme">%s</span>%s</summary>'
                     '<div class="lex-def">%s <a class="lex-voir" href="index.html#%s">Lire dans l\'essai</a></div></details>' % (
            sl, html.escape(e["terme"]),
            ' <span class="lex-langue">%s</span>' % en_ligne(e["langue"]) if e.get("langue") else "",
            lier(en_ligne(e["definition"]), cibles_ann, scope_self=("lexique.html", sl)), e["section"]))
    page_outil("lexique.html", "Lexique",
               "%d notions de l'essai." % len(lex),
               "Lexique des notions de l'essai.",
               '<div class="outil-filtres"><input type="search" data-filtre-texte placeholder="Chercher une notion…" aria-label="Chercher une notion">'
               '<button class="chip plier" type="button" id="plier-tout" aria-pressed="false">Tout replier</button></div>'
               '<div class="lexique">%s</div><p id="aucun" hidden>Aucune notion ne correspond.</p>' % "".join(items),
               titre, og_image, version)

    # ---------------------------------------------------------------- annexes
    cibles = cibles_liaison(annexes)
    liste_artistes = charger("artistes.json", [])
    images_par_fichier = {im["file"]: im for im in charger_images()}
    artiste_de = {f: a for a in liste_artistes for f in a["oeuvres"]}

    def vignette(f):
        """Une œuvre de la Galerie dans une annexe : vignette agrandie au survol, titre lié à la fiche de l'artiste."""
        im, a = images_par_fichier.get(f), artiste_de.get(f)
        if not im or not a:
            print("  annexes : œuvre inconnue de la galerie", f)
            return ""
        grand = oeuvres[f][2] if f in oeuvres and len(oeuvres[f]) > 2 else f
        return ('<a class="annexe-oeuvre" href="galerie.html#%s"><img class="vignette" src="%s" alt="%s"%s data-legende="%s"%s loading="lazy">'
                '<span>%s</span></a>') % (
                    slug_terme(a["nom"]), src_img(f), html.escape(im.get("alt", "")), attr_dims(f), html.escape(im.get("caption", "")),
                    ' data-grand="%s"' % src_img(grand) if grand != f else "",
                    html.escape(titre_oeuvre(im.get("caption", ""), alias_de(a))))
    titres_annexes = {a["id"]: a["titre"].split(" : ")[0] for a in annexes}
    lignes_passages = index_passages(textes, libelles, titres_annexes)
    passages = ('<details class="annexe" data-item data-type="bible" id="passages-cites"><summary>'
                '<span class="annexe-titre">Les passages bibliques cités par l\'essai</span><span class="annexe-cat">Index</span></summary>'
                '<div class="annexe-corps"><p>Les %d passages de la Bible que l\'essai cite ou désigne par leur référence, dans l\'ordre des livres, '
                'avec la section où ils apparaissent et l\'annexe qui les explique.</p><div class="table-wrap"><table class="passages">'
                '<thead><tr><th>Passage</th><th>Dans l\'essai</th><th>Annexe</th></tr></thead><tbody>%s</tbody></table></div></div></details>') % (
                    len(lignes_passages), "".join(lignes_passages)) if lignes_passages else ""
    groupes = []
    for cat, lab in CATEGORIES:
        arts = [a for a in annexes if a["categorie"] == cat]
        if arts:
            groupes.append('<section class="rep-carte annexes-groupe" data-groupe id="annexes-%s"><h2>%s</h2>%s%s</section>' % (
                cat, lab, passages if cat == "bible" else "", "".join(rendre_annexe(a, libelles, cibles, vignette) for a in arts)))
    chips = "".join('<button class="chip" data-filtre-type="%s" aria-pressed="%s">%s</button>' % (c, str(c == "tous").lower(), l)
                    for c, l in (("tous", "Tous"),) + tuple((c, l.split(" ")[0]) for c, l in CATEGORIES))
    filtres = ('<div class="outil-filtres"><input type="search" data-filtre-texte placeholder="Chercher un article…" aria-label="Chercher">'
               '<div class="chips">%s</div></div>' % chips)
    page_outil("annexes.html", "Annexes",
               "%d articles pour lire l'essai : les théories de ses auteurs, l'histoire du christianisme et de l'Europe, "
               "les disciplines qu'il convoque. Ce sont des synthèses de lecture, écrites sans citation ; elles ne remplacent pas "
               "les sources. Dans le texte, les termes soulignés en pointillé y renvoient." % len(annexes),
               "Repères pour lire l'essai.", filtres + "".join(groupes) + '<p id="aucun" hidden>Aucun article ne correspond.</p>',
               titre, og_image, version)

    # ---------------------------------------------------------------- bibliotheque : les écrivains, par siècle
    # Même forme que la page Les auteurs : une fiche repliable par écrivain, dates tirées de build/ecrivains.json
    # (Wikidata), filtres par texte, partie et période ; le corps de la fiche liste ses œuvres citées.
    dates_ecr = charger("ecrivains.json", {})
    auteurs, nom_aff = {}, {}
    fr_par_id = {l["id"]: l["oeuvres"] for l in (lettres_fr or [])}
    for l in lettres:
        oeuvres_fr = fr_par_id.get(l["id"]) if lettres_fr is not None else l["oeuvres"]
        if oeuvres_fr is None or len(oeuvres_fr) != len(l["oeuvres"]):
            print("  traduction %s, %s : encadré littéraire non aligné sur le français" % (LANG, l["id"]))
            oeuvres_fr = l["oeuvres"]
        for (aut, tit, reste, date), o_fr in zip(l["oeuvres"], oeuvres_fr):
            cle = o_fr[0]  # l'écrivain est identifié par son nom français (dates, portrait, ancre)
            nom_aff.setdefault(cle, aut)
            o = auteurs.setdefault(cle, {}).setdefault((tit, date), {"reste": reste, "sections": []})
            if (l["id"], l["nom"]) not in o["sections"]:
                o["sections"].append((l["id"], l["nom"]))
    for aut in auteurs:
        if aut not in dates_ecr:
            print("  ecrivains.json : écrivain sans dates", aut)
    ecr = [{"nom": nom_aff[aut], "fr": aut, "dates": dates_ecr.get(aut, {}).get("dates", ""), "annee": dates_ecr.get(aut, {}).get("annee"),
            "oeuvres": auteurs[aut]} for aut in auteurs]
    datees_ecr = sorted([f for f in ecr if f["annee"] is not None], key=lambda f: (f["annee"], cle_auteur(f["nom"])))
    sans_dates = sorted([f for f in ecr if f["annee"] is None], key=lambda f: cle_auteur(f["nom"]))

    def rendre_ecrivain(f, siecle_id):
        lis, parties_f = [], []
        for (tit, date), o in sorted(f["oeuvres"].items(), key=lambda kv: (kv[0][1], slug_terme(kv[0][0]))):
            liens = " · ".join('<a href="index.html#%s">%s</a>' % (sid, html.escape(nom)) for sid, nom in o["sections"])
            for sid, _ in o["sections"]:
                pid = infos_par_id.get(sid, {}).get("partie")
                if pid and pid not in parties_f:
                    parties_f.append(pid)
            lis.append('<li><em>%s</em>%s%s <span class="bib-liens">%s</span></li>' % (
                html.escape(tit), " " + html.escape(o["reste"]) if o["reste"] else "",
                " (%s)" % html.escape(date) if date else "", liens))
        return ('<details class="rep-carte fiche" data-item data-partie="%s" data-siecle="%s" id="%s" open>'
                '<summary><h2>%s<span class="f-nom">%s</span>%s</h2></summary>'
                '<div class="fiche-corps"><ul class="bib-oeuvres">%s</ul></div></details>') % (
                    " ".join(parties_f), siecle_id, slug_terme(f["fr"]),
                    avatar_html(ecrivains.get(slug_terme(f["fr"])), f["nom"]), html.escape(f["nom"]),
                    '<span class="f-dates">%s</span>' % html.escape(f["dates"]) if f["dates"] else "", "".join(lis))
    h, cur, siecles = [], None, []
    for f in datees_ecr:
        sc = siecle(f["annee"])
        if sc != cur:
            if cur:
                h.append("</section>")
            siecles.append((slug(sc), sc))
            h.append('<section class="siecle" data-groupe><h2>%s</h2>' % sc)
            cur = sc
        h.append(rendre_ecrivain(f, slug(sc)))
    if cur:
        h.append("</section>")
    if sans_dates:
        siecles.append(("sans-dates", "Sans dates"))
        h.append('<section class="siecle" data-groupe><h2>Sans dates</h2>%s</section>' % "".join(rendre_ecrivain(f, "sans-dates") for f in sans_dates))
    opts_siecles = '<option value="">Toutes les périodes</option>' + "".join(
        '<option value="%s">%s</option>' % (sid, html.escape(lab)) for sid, lab in siecles)
    filtres = ('<div class="outil-filtres"><input type="search" data-filtre-texte placeholder="Chercher un écrivain ou une œuvre…" '
               'aria-label="Chercher un écrivain ou une œuvre"><select data-filtre-partie aria-label="Filtrer par partie">%s</select>'
               '<select data-filtre-siecle aria-label="Filtrer par période">%s</select>'
               '<button class="chip plier" type="button" id="plier-tout" aria-pressed="false">Tout replier</button></div>' % (opts, opts_siecles))
    nb_oeuvres = sum(len(v) for v in auteurs.values())
    page_outil("bibliotheque.html", "Bibliothèque",
               "Les %d œuvres de %d écrivains convoquées dans les encadrés « En littérature » de l'essai, du plus ancien au plus récent. " % (nb_oeuvres, len(auteurs)),
               "Bibliothèque des œuvres littéraires citées dans l'essai, par écrivain et par siècle.",
               filtres + "".join(h) + '<p id="aucun" hidden>Aucune œuvre ne correspond.</p>', titre, og_image, version)

    # ---------------------------------------------------------------- galerie : les artistes et leurs œuvres
    # Même forme que la Bibliothèque : une fiche repliable par artiste (build/artistes.json : identifiant Wikidata,
    # dates, fichiers de ses œuvres), et dans la fiche chaque œuvre avec sa vignette, agrandie au survol, et le lien
    # vers l'endroit de l'essai où elle figure (section, partie ou couverture).
    listes = {f for a in liste_artistes for f in a["oeuvres"]}
    for f in sorted(oeuvres):
        if f.startswith("images/art/") and f not in listes:  # les pages de titre et les portraits ne sont pas des œuvres de la galerie
            print("  artistes.json : image d'art absente de la galerie", f)
    for a in liste_artistes:
        for f in a["oeuvres"]:
            if f not in oeuvres:
                print("  artistes.json : fichier inconnu ou non affiché dans l'essai", f)
    annexes_de = {}  # œuvre -> annexes qui la commentent (champ « oeuvres » des annexes)
    for an in annexes:
        for f in an.get("oeuvres", []):
            annexes_de.setdefault(f, []).append(an)

    def rendre_artiste(a, siecle_id):
        lis, parties_f = [], []
        for f in a["oeuvres"]:
            im = images_par_fichier.get(f)
            if not im or f not in oeuvres:
                continue
            ancre, lib = oeuvres[f][0], oeuvres[f][1]
            grand = oeuvres[f][2] if len(oeuvres[f]) > 2 else f
            pid = ancre if ancre in libelles and ancre not in infos_par_id else infos_par_id.get(ancre, {}).get("partie")
            if pid and pid not in parties_f:
                parties_f.append(pid)
            lien = "Voir la couverture" if ancre == "top" else ("Voir la partie" if ancre in libelles and ancre not in infos_par_id else "Lire la section")
            lis.append('<li><img class="vignette" src="%s" alt="%s"%s data-legende="%s"%s loading="lazy"><span class="gal-texte"><em>%s</em>'
                       ' <span class="bib-liens">%s · <a class="r-section" href="index.html#%s">%s</a>%s</span></span></li>' % (
                           src_img(f), html.escape(im.get("alt", "")), attr_dims(f), html.escape(im.get("caption", "")),
                           ' data-grand="%s"' % src_img(grand) if grand != f else "",
                           html.escape(titre_oeuvre(im.get("caption", ""), alias_de(a))), html.escape(lib), ancre, lien,
                           "".join(' · <a class="r-section" href="annexes.html#%s">Annexe : %s</a>' % (an["id"], html.escape(an["titre"].split(" : ")[0]))
                                   for an in annexes_de.get(f, []))))
        sl = slug_terme(a["nom"])
        return ('<details class="rep-carte fiche" data-item data-partie="%s" data-siecle="%s" id="%s" open>'
                '<summary><h2>%s<span class="f-nom">%s</span>%s</h2></summary>'
                '<div class="fiche-corps"><ul class="bib-oeuvres gal-oeuvres">%s</ul></div></details>') % (
                    " ".join(parties_f), siecle_id, sl, avatar_html(artistes.get(sl), a["nom"]), html.escape(a["nom"]),
                    '<span class="f-dates">%s</span>' % html.escape(a["dates"]) if a.get("dates") else "", "".join(lis))
    datees_art = sorted([a for a in liste_artistes if a.get("annee") is not None], key=lambda a: (a["annee"], slug_terme(a["nom"])))
    sans_art = [a for a in liste_artistes if a.get("annee") is None]
    h, cur, siecles = [], None, []
    for a in datees_art:
        sc = siecle(a["annee"])
        if sc != cur:
            if cur:
                h.append("</section>")
            siecles.append((slug(sc), sc))
            h.append('<section class="siecle" data-groupe><h2>%s</h2>' % sc)
            cur = sc
        h.append(rendre_artiste(a, slug(sc)))
    if cur:
        h.append("</section>")
    for a in sans_art:
        siecles.append((slug_terme(a["nom"]), a["nom"]))
        h.append('<section class="siecle" data-groupe><h2>%s</h2>%s</section>' % (html.escape(a["nom"]), rendre_artiste(a, slug_terme(a["nom"]))))
    opts_siecles = '<option value="">Toutes les périodes</option>' + "".join(
        '<option value="%s">%s</option>' % (sid, html.escape(lab)) for sid, lab in siecles)
    filtres = ('<div class="outil-filtres"><input type="search" data-filtre-texte placeholder="Chercher un artiste ou une œuvre…" '
               'aria-label="Chercher un artiste ou une œuvre"><select data-filtre-partie aria-label="Filtrer par partie">%s</select>'
               '<select data-filtre-siecle aria-label="Filtrer par période">%s</select>'
               '<button class="chip plier" type="button" id="plier-tout" aria-pressed="false">Tout replier</button></div>' % (opts, opts_siecles))
    nb_oeuvres_art = sum(1 for a in liste_artistes for f in a["oeuvres"] if f in oeuvres)
    page_outil("galerie.html", "Galerie",
               "Les %d œuvres de %d artistes reproduites dans l'essai, du plus ancien au plus récent : pour chacune, une vignette, "
               "son agrandissement au survol, et le lien vers l'endroit où elle figure." % (nb_oeuvres_art, len(datees_art)),
               "Galerie des œuvres d'art reproduites dans l'essai, par artiste et par siècle.",
               filtres + "".join(h) + '<p id="aucun" hidden>Aucune œuvre ne correspond.</p>', titre, og_image, version)

    # ---------------------------------------------------------------- sources et crédits
    page_outil("sources.html", "Sources et crédits",
               "Les éditions consultées, les sources secondaires, les réserves que l'auteur formule sur ses citations, "
               "et les crédits des images.",
               "Sources, éditions consultées et crédits des images de l'essai.",
               '<div class="sources">%s<h3>Crédits des images</h3>'
               '<p>Images issues de Wikimedia Commons, sous licence libre ou dans le domaine public.</p>%s</div>' % (sources, credits),
               titre, og_image, version)


def construire(chemin, version=None, fr_parties=None):
    """Rend l'essai (index.html). Pour une traduction, fr_parties est la structure française : ids, portraits,
    figures et dates de tri en viennent, alignés par position ; le texte affiché vient de la traduction."""
    titre, sous_titre, intro, parties = structurer(lire_article(chemin))
    parties = [p for p in parties if not p["titre"].startswith(RESUME)]
    if fr_parties is None:
        fr_parties = parties
    elif len(fr_parties) != len(parties):
        raise SystemExit("traduction %s : %d parties au lieu de %d" % (LANG, len(parties), len(fr_parties)))
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


    annexes = charger_annexes()
    par_cible = {}  # id de section ou de partie -> annexes qui l'eclairent (ordre du fichier)
    for a in annexes:
        for s in a["sections"]:
            par_cible.setdefault(s, []).append(a)
    libelles = {}  # id de section ou de partie -> libelle des liens « Dans l'essai »

    sources_html, tableau_html, toc, corps, cartes = "", "", [], [], []
    portraits_par_id = {}  # id de section -> portraits (pour les pages outils)
    textes = []  # (id, texte brut) des parties et sections, pour l'index des passages bibliques
    oeuvres = {}  # fichier d'une image d'art -> (ancre dans l'essai, libellé), pour la galerie
    nb_parties = 0
    infos = []  # sections, pour la frise
    lettres = []  # encadres litteraires, pour la bibliotheque
    for part, part_fr in zip(parties, fr_parties):
        pid = uid(slug(part_fr["titre"]), "p")
        ptitre = part["titre"]
        if len(part["sections"]) != len(part_fr["sections"]):
            raise SystemExit("traduction %s, %s : %d sections au lieu de %d" % (LANG, pid, len(part["sections"]), len(part_fr["sections"])))
        if pid == "sources":
            secs = []
            for sec in part["sections"]:
                secs.append("<h3>%s</h3>" % en_ligne(sec["titre"]))
                secs += rendre_blocs(sec["lignes"])
            sources_html = "\n".join(rendre_blocs(part["lignes"]) + secs)
            continue
        label, _, sous = partition_titre(ptitre)
        libelles[pid] = label
        if "partie" in partition_titre(part_fr["titre"])[0].lower():
            nb_parties += 1
        intro_p = rendre_blocs(part["lignes"])
        secs_html, toc_secs, nb_auteurs = [], [], 0
        for f in par_section.get((pid, "figure"), []):
            intro_p.insert(min(1, len(intro_p)), figure(f))
            oeuvres[f["file"]] = (pid, label)
        textes.append((pid, html.unescape(re.sub(r"<[^>]+>", " ", "\n".join(intro_p)))))
        for sec, sec_fr in zip(part["sections"], part_fr["sections"]):
            base = slug(sec_fr["titre"])
            sid = uid(base, pid)
            nom, dates, formule = analyser_titre(sec["titre"])
            dates_fr = analyser_titre(sec_fr["titre"])[1]
            if base == "tableau-des-auteurs":
                tableau_html = "\n".join(rendre_blocs(sec["lignes"]))  # publié à part, dans la page auteurs.html
                continue
            infos.append({"id": sid, "titre": sec_fr["titre"], "partie": pid, "partie_titre": ptitre})
            del LETTRES_BUF[:]
            corps_sec = rendre_blocs(sec["lignes"])
            buf = list(LETTRES_BUF)
            if fr_parties is not parties and len(corps_sec) != len(rendre_blocs(sec_fr["lignes"])):
                print("  traduction %s, %s : nombre de blocs différent du français" % (LANG, sid))
            if buf:
                lettres.append({"id": sid, "nom": nom if dates else sec["titre"], "oeuvres": buf})
            del LETTRES_BUF[:]
            portraits = par_section.get((base, "portrait"), [])
            portraits_par_id[sid] = portraits
            est_auteur = bool(dates_fr) or bool(portraits)
            nb_auteurs += 1 if est_auteur else 0
            corps_sec = inserer_figures(corps_sec, par_section.get((base, "figure"), []))
            for f in par_section.get((base, "figure"), []):
                oeuvres[f["file"]] = (sid, nom if dates else sec["titre"])
            textes.append((sid, html.unescape(re.sub(r"<[^>]+>", " ", "\n".join(corps_sec)))))
            if est_auteur:
                if portraits:
                    av = "".join('<img class="avatar" src="%s" alt="%s"%s data-legende="%s" loading="lazy">' % (
                        src_img(p["file"]), html.escape(p.get("alt", nom)), attr_dims(p["file"]),
                        html.escape(p.get("caption", ""))) for p in portraits)
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
            lib = nom if est_auteur else partition_titre(sec["titre"])[0]
            libelles[sid] = "%s (%s)" % (lib, label.lower()) if partition_titre(sec_fr["titre"])[0] == "Passage" else lib
            secs_html.append(
                '<details class="section%s" id="%s" data-partie="%s" open><summary>%s'
                '<span class="sec-side">%s</span></summary>'
                '<div class="sec-body">%s%s%s</div></details>' % (
                    " auteur" if est_auteur else "", sid, pid, head,
                    lien_btn(sid), ligne_annexes(par_cible.get(sid)), "\n".join(corps_sec), credits))
            toc_secs.append('<li><a href="#%s" data-target="%s">%s%s</a></li>' % (
                sid, sid, en_ligne(nom if est_auteur else sec["titre"]),
                ' <small>%s</small>' % html.escape(dates) if dates else ""))
        meta = T("{n} auteurs").replace("{n}", str(nb_auteurs)) if nb_auteurs else ""
        card_img = par_section.get((pid, "partcard"), [])
        part_img = par_section.get((pid, "partimage"), []) or card_img  # grande version si elle existe
        if card_img:
            oeuvres[card_img[0]["file"]] = (pid, label, part_img[0]["file"])
        corps.append(
            '<details class="partie" id="%s"><summary><span class="part-label">%s</span>'
            '<span class="part-sub">%s</span>%s%s</summary>'
            '<div class="part-body">%s%s%s%s<p class="part-end"><a href="#%s" data-target="%s">Haut de la partie</a></p></div></details>' % (
                pid, en_ligne(label), en_ligne(sous), '<span class="part-meta">%s</span>' % meta if meta else "", lien_btn(pid),
                figure(part_img[0], "part-image") if part_img else "",
                ligne_annexes(par_cible.get(pid)), "\n".join(intro_p), "\n".join(secs_html), pid, pid))
        toc.append('<li class="toc-part"><a href="#%s" data-target="%s">%s%s</a>%s</li>' % (
            pid, pid, en_ligne(ptitre),
            '<span class="toc-count" data-count="%s"></span>' % pid if toc_secs else "",
            "<ul>%s</ul>" % "".join(toc_secs) if toc_secs else ""))
        cartes.append(
            '<a class="card" href="#%s" data-target="%s">%s<span class="card-text">'
            '<span class="card-label">%s</span><span class="card-sub">%s</span>'
            '%s</span></a>' % (
                pid, pid,
                '<img src="%s" alt=""%s loading="lazy">' % (src_img(card_img[0]["file"]), attr_dims(card_img[0]["file"])) if card_img else "",
                en_ligne(label), en_ligne(sous), '<span class="card-meta">%s</span>' % meta if meta else ""))

    credits_imgs = "".join(
        '<li><a href="%s" rel="noopener">%s</a> : %s</li>' % (
            html.escape(i.get("source", "")), html.escape(i.get("alt", "") or i["file"]),
            html.escape(i.get("credit", "")))
        for i in images if i.get("role") != "partimage")  # même source que la carte : un seul crédit
    cover = par_section.get(("cover", "cover"), [])
    if cover:
        oeuvres[cover[0]["file"]] = ("top", "Couverture")
    for a in annexes:
        for s in a["sections"]:
            if s not in ids_vus:
                print("  annexes/%s.md : section inconnue %s" % (a["id"], s))
    corps_html = lier("\n".join(corps), cibles_liaison(annexes))
    tpl = open(os.path.join(ICI, "template.html"), encoding="utf-8").read()
    version = version or str(int(time.time()))
    rempl = {
        "TITRE": en_ligne(titre),
        "TITRE_BRUT": html.escape(titre),
        "SOUS_TITRE": en_ligne(sous_titre),
        "COUVERTURE": figure(cover[0], "cover") if cover else "",
        "STORE": "sdr-",
        "TITRE_ONGLET": html.escape(titre),
        "ONGLETS": onglets("index.html"),
        "HREFLANG": hreflangs("index.html"),
        "UI": ui_js(),
        "PAGE": "index.html",
        "CARTES": "\n".join(cartes),
        "TOC": "\n".join(toc),
        "CORPS": corps_html,
        "NB_PARTIES": NOMBRES.get(nb_parties, str(nb_parties)),
        "BASE_URL": BASE_URL,
        "OG_IMAGE": BASE_URL + (cover[0]["file"] if cover else ""),
        "OG_W": str(dimensions(cover[0]["file"])[0]) if cover else "",
        "OG_H": str(dimensions(cover[0]["file"])[1]) if cover else "",
    }
    tpl = tpl.replace('href="css/style.css"', 'href="css/style.css?v=%s"' % version).replace('src="js/app.js"', 'src="js/app.js?v=%s"' % version).replace('src="js/sauts.js"', 'src="js/sauts.js?v=%s"' % version).replace('src="js/portrait.js"', 'src="js/portrait.js?v=%s"' % version)
    for k, v in rempl.items():
        tpl = tpl.replace("{{%s}}" % k, v)
    ecrire_page("index.html", tpl)
    print("%sindex.html : %d parties" % ("" if LANG == "fr" else LANG + "/", len(corps)))
    return {"titre": titre, "infos": infos, "ids": ids_vus, "version": version, "og": rempl["OG_IMAGE"],
            "lettres": lettres, "annexes": annexes, "libelles": libelles, "sources": sources_html,
            "credits": "<ul>%s</ul>" % credits_imgs if credits_imgs else "<p>Aucune image.</p>",
            "tableau": tableau_html, "portraits": portraits_par_id,
            "ecrivains": {im["section"]: im for im in images if im["role"] == "ecrivain"},
            "artistes": {im["section"]: im for im in images if im["role"] == "artiste"}, "oeuvres": oeuvres, "textes": textes,
            "parties": parties}


def tout_construire(article=ARTICLE):
    global LANGUES_CONSTRUITES
    version = str(int(time.time()))
    LANGUES_CONSTRUITES = [c for c, _, _ in LANGUES if langue_disponible(c)]
    r_fr = None
    for code in LANGUES_CONSTRUITES:
        charger_langue(code)
        chemin = article if code == "fr" else os.path.join(dossier_langue(code), "article.md")
        r = construire(chemin, version=version, fr_parties=r_fr["parties"] if r_fr else None)
        pages_outils(r["titre"], r["infos"], version, r["og"], r["ids"], r["lettres"], r["annexes"], r["libelles"], r["sources"], r["credits"],
                     r["tableau"], r["portraits"], r["ecrivains"], r["artistes"], r["oeuvres"], r["textes"],
                     lettres_fr=r_fr["lettres"] if r_fr else None, tableau_fr=r_fr["tableau"] if r_fr else None)
        if code == "fr":
            r_fr = r
    charger_langue("fr")
    autres = "".join('  "%s/%s",\n' % (c, p) for c in LANGUES_CONSTRUITES if c != "fr"
                     for p in [f for f, _ in PAGES_SITE])
    sw = open(os.path.join(ICI, "sw.template.js"), encoding="utf-8").read()
    open(os.path.join(RACINE, "sw.js"), "w", encoding="utf-8").write(
        sw.replace("{{VERSION}}", version).replace("  /* {{AUTRES_LANGUES}} */\n", autres))


if __name__ == "__main__":
    tout_construire(sys.argv[1] if len(sys.argv) > 1 else ARTICLE)
