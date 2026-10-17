"""Exporte la source française publiée, à traduire : i18n/source/article/NN-<partie>[-k].md.

Le texte est celui que publie le site : statuts de citation masqués (masquer_statuts), partie « L'essai en
dix minutes » retirée. Chaque morceau fait au plus LIMITE mots environ ; une partie longue est découpée entre
ses sections. Concaténer les morceaux traduits dans l'ordre des noms de fichiers redonne l'article entier.
"""
import os, re, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B

LIMITE = 6000


def main(article=B.ARTICLE):
    lignes = B.lire_article(article)
    titre, sous_titre, intro, parties = B.structurer(lignes)
    out = os.path.join(B.RACINE, "i18n", "source", "article")
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    morceaux = [("00-titre", ["# " + titre, "", "*" + sous_titre + "*", ""] + intro)]
    n = 0
    for part in parties:
        if part["titre"].startswith(B.RESUME):
            continue
        n += 1
        pid = B.slug(part["titre"])
        tete = ["## " + part["titre"]] + part["lignes"]
        lots, cur = [], list(tete)
        for sec in part["sections"]:
            bloc = ["### " + sec["titre"]] + sec["lignes"]
            if len(" ".join(cur).split()) + len(" ".join(bloc).split()) > LIMITE and len(cur) > len(tete if not lots else []):
                lots.append(cur)
                cur = []
            cur += bloc
        lots.append(cur)
        for k, lot in enumerate(lots):
            nom = "%02d-%s%s" % (n, pid, "-%d" % (k + 1) if len(lots) > 1 else "")
            morceaux.append((nom, lot))
    total = 0
    for nom, ls in morceaux:
        texte = B.masquer_statuts("\n".join(ls)).rstrip() + "\n"
        open(os.path.join(out, nom + ".md"), "w", encoding="utf-8").write(texte)
        mots = len(texte.split())
        total += mots
        print("%-48s %6d mots" % (nom, mots))
    print(len(morceaux), "morceaux,", total, "mots")


if __name__ == "__main__":
    main(*sys.argv[1:])
