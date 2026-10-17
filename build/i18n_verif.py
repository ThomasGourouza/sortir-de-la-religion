"""Vérifie une traduction (i18n/<langue>/) contre la source française : structure, citations, chiffres, résidus.

python3 build/i18n_verif.py en          rapport complet
Contrôles par morceau de l'essai (i18n/source/article/ contre i18n/<langue>/article/) : mêmes titres (niveaux et
nombre), même nombre de blocs (paragraphes, listes, tableaux, citations), mêmes encadrés « En littérature » ;
citations en langue originale (grec, cyrillique, hébreu, arabe, et segments sans mots français) retrouvées à
l'identique ; années et nombres conservés ; aucun tiret cadratin ou demi-cadratin ; peu de mots français hors
citations. Puis les annexes, le lexique et les données.
"""
import os, re, sys, json, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B

MOTS_FR = set("le la les des du une est et que qui dans pour pas sur avec ce cette sont mais aussi comme plus ne se il elle ils lui leur leurs on nous vous où".split())
NON_LATIN = re.compile(r"[Ͱ-Ͽἀ-῿Ѐ-ӿ֐-׿؀-ۿ]")
CITATION = re.compile(r"«\s*(.+?)\s*»", re.S)
# gloses françaises entre guillemets que l'heuristique prend pour des citations originales : elles se traduisent
GLOSES = {"Effondrement de l'Effondrement", "interprétation non religieuse"}


def blocs(texte):
    return [k for k, _ in B.blocs(texte.split("\n"))]


def titres(texte):
    return re.findall(r"(?m)^(#{1,4}) ", texte)


def citations_originales(texte):
    out = []
    for c in CITATION.findall(texte):
        mots = re.findall(r"[a-zàâçéèêëîïôûùüÿœ']+", c.lower())
        francais = sum(1 for m in mots if m in MOTS_FR)
        if c not in GLOSES and (NON_LATIN.search(c) or (len(c) > 25 and francais == 0)):
            out.append(re.sub(r"\s+", " ", c).strip())
    return out


def nombres(texte):
    return collections.Counter(re.findall(r"(?<![\d.,])\d{3,4}(?![\d])", texte))


def residus_fr(texte):
    sans = CITATION.sub(" ", texte)
    sans = re.sub(r"\*\*[^*]+\*\*", " ", sans)  # le gras d'abord, sinon il fausse l'appariement des italiques
    sans = re.sub(r"“[^”]*”|„[^“]*“|\*[^*]+\*", " ", sans)
    mots = re.findall(r"[a-zàâçéèêëîïôûùüÿœ']+", sans.lower())
    tous = re.findall(r"\w+", sans)  # tous les mots, tous alphabets : le rapport vaut pour le cyrillique aussi
    return sum(1 for m in mots if m in MOTS_FR and m not in ("on", "plus", "ne", "se", "il", "pas")), len(tous)


def verif_morceau(src, tr):
    s, t = open(src, encoding="utf-8").read(), open(tr, encoding="utf-8").read()
    pb = []
    if titres(s) != titres(t):
        pb.append("titres %s au lieu de %s" % (collections.Counter(titres(t)), collections.Counter(titres(s))))
    bs, bt = blocs(s), blocs(t)
    if len(bs) != len(bt):
        pb.append("%d blocs au lieu de %d" % (len(bt), len(bs)))
    ns, nt = s.count("> **En littérature.**"), t.count("> **En littérature.**")
    if ns != nt:
        pb.append("%d encadrés au lieu de %d" % (nt, ns))
    plat = re.sub(r"\s+", " ", t)
    manquantes = [c for c in citations_originales(s) if c not in plat]
    if manquantes:
        pb.append("%d citations originales absentes, dont : %s" % (len(manquantes), " | ".join(c[:70] for c in manquantes[:3])))
    perdus = nombres(s) - nombres(t)
    if sum(perdus.values()) > 2:
        pb.append("nombres perdus : %s" % ", ".join(sorted(perdus)[:12]))
    if re.search("[–—]", t):
        pb.append("tiret cadratin ou demi-cadratin")
    fr, tot = residus_fr(t)
    if tot and fr / tot > 0.02 and not os.path.basename(tr).startswith("15-sources"):  # la bibliographie garde ses titres français
        pb.append("mots français hors citations : %d sur %d" % (fr, tot))
    return pb, len(t.split()), len(s.split())


def main(langue="en"):
    racine = B.RACINE
    total = 0
    print("== essai")
    for src in sorted(glob.glob(os.path.join(racine, "i18n", "source", "article", "*.md"))):
        nom = os.path.basename(src)
        tr = os.path.join(racine, "i18n", langue, "article", nom)
        if not os.path.exists(tr):
            print("  MANQUANT", nom); total += 1; continue
        pb, mt, ms = verif_morceau(src, tr)
        ratio = mt / ms if ms else 0
        bornes = {"ru": (0.65, 1.2)}.get(langue, (0.8, 1.25))  # le russe, sans articles, compte moins de mots
        if not bornes[0] <= ratio <= bornes[1]:
            pb.append("longueur %.2f de l'original" % ratio)
        if pb:
            total += 1
            print("  %s : %s" % (nom, " ; ".join(pb)))
    print("== annexes")
    for src in sorted(glob.glob(os.path.join(racine, "build", "annexes", "*.md"))):
        nom = os.path.basename(src)
        tr = os.path.join(racine, "i18n", langue, "annexes", nom)
        if not os.path.exists(tr):
            print("  MANQUANT", nom); total += 1; continue
        a, b = B.lire_annexe(src, nom, verifier=False), B.lire_annexe(tr, nom, verifier=False)
        pb = []
        if not b or not b["titre"] or not b["motifs"]:
            pb.append("en-tête incomplet")
        else:
            if titres("\n".join(a["lignes"])) != titres("\n".join(b["lignes"])):
                pb.append("sous-titres différents")
            if len(blocs("\n".join(a["lignes"]))) != len(blocs("\n".join(b["lignes"]))):
                pb.append("blocs différents")
            interdits = "[\u2013\u2014«»]" if langue == "en" else "[\u2013\u2014]"
            if re.search(interdits, open(tr, encoding="utf-8").read()):
                pb.append("tiret interdit" + (" ou guillemets français" if langue == "en" else ""))
        if pb:
            total += 1
            print("  %s : %s" % (nom, " ; ".join(pb)))
    print("== lexique")
    lex = {e["terme"] for e in json.load(open(os.path.join(racine, "build", "lexique.json"), encoding="utf-8"))}
    trad = {}
    for f in glob.glob(os.path.join(racine, "i18n", langue, "lexique", "*.json")):
        for e in json.load(open(f, encoding="utf-8")):
            trad[e.get("fr")] = e
    manq = sorted(lex - set(trad))
    if manq:
        total += 1; print("  %d notions manquantes : %s" % (len(manq), ", ".join(manq[:8])))
    for k, e in trad.items():
        n = len(e.get("definition", "").split())
        if not e.get("motifs") or not 90 <= n <= 220:
            total += 1; print("  %s : %d mots, %d motifs" % (k, n, len(e.get("motifs", []))))
    print("== données")
    src = json.load(open(os.path.join(racine, "i18n", "source", "donnees.json"), encoding="utf-8"))
    for nom, cles in (("donnees-noms.json", ("noms", "dates")), ("donnees-images.json", None)):
        p = os.path.join(racine, "i18n", langue, nom)
        if not os.path.exists(p):
            total += 1; print("  MANQUANT", nom); continue
        d = json.load(open(p, encoding="utf-8"))
        if cles:
            for k in cles:
                m = set(src[k]) - set(d.get(k, {}))
                if m:
                    total += 1; print("  %s : %d %s manquants" % (nom, len(m), k))
            if len(d.get("reponses", [])) != len(src["reponses"]):
                total += 1; print("  %s : %d notes au lieu de %d" % (nom, len(d.get("reponses", [])), len(src["reponses"])))
        else:
            m = set(src["images"]) - set(d)
            if m:
                total += 1; print("  %s : %d images manquantes" % (nom, len(m)))
    print("problèmes :", total)
    return total


if __name__ == "__main__":
    sys.exit(1 if main(*(sys.argv[1:] or ["en"])) else 0)
