"""Recale le découpage d'une traduction (i18n/<langue>/article/) sur celui de la source française, puis réassemble
i18n/<langue>/article.md.

python3 build/i18n_redecouper.py en

À lancer après python3 build/i18n_export.py, quand l'ajout ou le retrait d'une section a déplacé les frontières des
morceaux français (une partie passe par exemple de 4 à 5 morceaux). Pour chaque partie, le texte traduit est recousu
puis recoupé aux mêmes titres de section (### ) que la source : le premier morceau garde la tête de partie, chaque
morceau suivant reçoit autant de sections que son homologue français. Une partie dont le nombre de sections traduites
diffère du français n'est pas touchée : il faut d'abord traduire (ou retirer) la section en cause.
"""
import os, re, sys, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B

MORCEAU = re.compile(r"^(\d+-[a-z0-9-]+?)(?:-(\d+))?\.md$")


def groupes(dossier):
    """{partie: [noms de fichiers dans l'ordre]}, la partie étant le préfixe NN-<id> sans le numéro de morceau."""
    g = collections.OrderedDict()
    for chemin in sorted(glob.glob(os.path.join(dossier, "*.md"))):
        m = MORCEAU.match(os.path.basename(chemin))
        if m:
            g.setdefault(m.group(1), []).append((int(m.group(2) or 0), os.path.basename(chemin)))
    return collections.OrderedDict((k, [n for _, n in sorted(v)]) for k, v in g.items())


def unites(texte):
    """Découpe un texte en [tête, section, section…] ; chaque section commence par une ligne « ### »."""
    out, cur = [], []
    for ligne in texte.split("\n"):
        if ligne.startswith("### ") and (cur or out):
            out.append(cur)
            cur = []
        cur.append(ligne)
    out.append(cur)
    if out and out[0] and out[0][0].startswith("### "):
        out.insert(0, [])  # pas de tête : le premier morceau commence par une section
    return out


def lire(dossier, noms):
    return "".join(open(os.path.join(dossier, n), encoding="utf-8").read() for n in noms)


def main(langue):
    src_dir = os.path.join(B.RACINE, "i18n", "source", "article")
    tr_dir = os.path.join(B.RACINE, "i18n", langue, "article")
    src, tr = groupes(src_dir), groupes(tr_dir)
    changes, refus = 0, 0
    for partie, noms_src in src.items():
        noms_tr = tr.get(partie, [])
        if not noms_tr:
            print("  %s : aucune traduction" % partie); refus += 1; continue
        if noms_tr == noms_src and all(
                len(unites(open(os.path.join(src_dir, n), encoding="utf-8").read()))
                == len(unites(open(os.path.join(tr_dir, n), encoding="utf-8").read())) for n in noms_src):
            continue  # déjà aligné
        u_tr = unites(lire(tr_dir, noms_tr))
        u_src = unites(lire(src_dir, noms_src))
        if len(u_tr) != len(u_src):
            titres = [u[0][4:] for u in u_src[1:]]
            print("  %s : %d sections traduites pour %d en français, partie laissée telle quelle ; sections françaises : %s"
                  % (partie, len(u_tr) - 1, len(u_src) - 1, " | ".join(t[:50] for t in titres)))
            refus += 1
            continue
        tete, sections = u_tr[0], u_tr[1:]
        i = 0
        for k, nom in enumerate(noms_src):
            n = len(unites(open(os.path.join(src_dir, nom), encoding="utf-8").read())) - 1
            lignes = (tete if k == 0 else []) + [l for s in sections[i:i + n] for l in s]
            i += n
            open(os.path.join(tr_dir, nom), "w", encoding="utf-8").write("\n".join(lignes).rstrip() + "\n")
        for nom in set(noms_tr) - set(noms_src):
            os.remove(os.path.join(tr_dir, nom))
        print("  %s : %s -> %s" % (partie, ", ".join(noms_tr), ", ".join(noms_src)))
        changes += 1
    ordre = [n for noms in groupes(tr_dir).values() for n in noms]
    open(os.path.join(B.RACINE, "i18n", langue, "article.md"), "w", encoding="utf-8").write(lire(tr_dir, ordre))
    print("%s : %d partie(s) redécoupée(s), %d refusée(s) ; article.md réassemblé" % (langue, changes, refus))
    return 1 if refus else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
