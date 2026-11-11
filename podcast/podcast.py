"""Podcast vidéo de l'essai.

    python3 podcast/podcast.py audio   # synthèse ElevenLabs, une piste par segment du script (cache par contenu)
    python3 podcast/podcast.py video   # images 1920x1080 + montage ffmpeg -> podcast/out/sortir-de-la-religion.mp4

Le script est dans podcast/script/*.md : titres ## et ### recopiés de l'essai, narration dessous.
"""
import hashlib, json, os, re, subprocess, sys, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageOps

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(RACINE, "build"))
from build import lire_article, structurer, slug, analyser_titre  # noqa: E402

OUT = os.path.join(ICI, "out")
AUDIO, CADRES = os.path.join(OUT, "audio"), os.path.join(OUT, "cadres")
VOIX = "aQROLel5sQbj1vuIVi6B"  # Nicolas, narrateur (bibliothèque partagée ElevenLabs)
REGLAGES = {"stability": 0.35, "similarity_boost": 0.8, "style": 0.45, "use_speaker_boost": True, "speed": 0.95}
PAUSE_SECTION, PAUSE_PARTIE = 1.2, 2.5  # silences ajoutés après un segment, en secondes
IGNOREES = ("L'essai en dix minutes", "Sources")


def essai():
    """Parties de l'essai, avec ids (même règle que build.py) et sections."""
    _, _, _, parties = structurer(lire_article(os.path.join(RACINE, "texte", "sortir-de-la-religion.md")))
    vus, out = set(), []

    def uid(base, prefixe):
        i = base if base not in vus else "%s-%s" % (prefixe, base)
        vus.add(i)
        return i
    for p in parties:
        pid = uid(slug(p["titre"]), "")
        if p["titre"] in IGNOREES:
            continue
        secs = [{"titre": s["titre"], "id": uid(slug(s["titre"]), pid)} for s in p["sections"]
                if not s["titre"].startswith("Tableau des auteurs")]
        out.append({"titre": p["titre"], "id": pid, "sections": secs})
    return out


def script(parties):
    """Segments narrés : (index partie, index section ou None, texte)."""
    idx_p = {p["titre"]: i for i, p in enumerate(parties)}
    segs, ip, isec, buf = [], None, None, []

    def vider():
        t = "\n".join(buf).strip()
        if t and ip is not None:
            segs.append((ip, isec, t))
        buf.clear()
    for f in sorted(os.listdir(os.path.join(ICI, "script"))):
        for l in open(os.path.join(ICI, "script", f), encoding="utf-8"):
            l = l.rstrip("\n")
            if l.startswith("## "):
                vider()
                ip, isec = idx_p[l[3:].strip()], None
            elif l.startswith("### "):
                vider()
                titres = [s["titre"] for s in parties[ip]["sections"]]
                isec = titres.index(l[4:].strip())
            else:
                buf.append(l)
        vider()
    return segs


def cle_audio(texte):
    return hashlib.sha1(json.dumps([VOIX, REGLAGES, texte]).encode()).hexdigest()[:16]


def audio(segs):
    cle = dict(l.strip().split("=", 1) for l in open(os.path.join(RACINE, ".env.local")) if "=" in l)["ELEVENLABS_API_KEY"]
    os.makedirs(AUDIO, exist_ok=True)
    textes = [re.sub(r"\n\s*\n", "\n\n", t) for _, _, t in segs]
    for n, t in enumerate(textes):
        mp3 = os.path.join(AUDIO, cle_audio(t) + ".mp3")
        if os.path.exists(mp3):
            continue
        corps = {"text": t, "model_id": "eleven_multilingual_v2", "language_code": "fr", "voice_settings": REGLAGES,
                 "previous_text": textes[n - 1][-500:] if n else None,
                 "next_text": textes[n + 1][:500] if n + 1 < len(textes) else None}
        req = urllib.request.Request(
            "https://api.elevenlabs.io/v1/text-to-speech/%s?output_format=mp3_44100_128" % VOIX,
            data=json.dumps(corps).encode(), headers={"xi-api-key": cle, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as r, open(mp3 + ".tmp", "wb") as f:
            f.write(r.read())
        os.replace(mp3 + ".tmp", mp3)
        print("%d/%d  %d car." % (n + 1, len(textes), len(t)))


# --- vidéo -----------------------------------------------------------------

W, H, BARRE = 1920, 1080, 640
FOND, CARTE, ENCRE, DOUX, ACCENT, ACCENT_DOUX, LIGNE = "#f4ead5", "#eadcc0", "#3a2e1f", "#6d5c45", "#8a3b12", "#f2dccb", "#d8c7a5"
POL = "/System/Library/Fonts/Supplemental/Georgia%s.ttf"


def police(taille, style=""):
    return ImageFont.truetype(POL % style, taille)


def couper(d, texte, fnt, larg):
    """Lignes d'au plus larg pixels."""
    lignes, cur = [], ""
    for mot in texte.split():
        essai_ = (cur + " " + mot).strip()
        if d.textlength(essai_, font=fnt) <= larg:
            cur = essai_
        else:
            lignes.append(cur)
            cur = mot
    return lignes + [cur] if cur else lignes


def tronquer(d, texte, fnt, larg):
    if d.textlength(texte, font=fnt) <= larg:
        return texte
    while d.textlength(texte + "…", font=fnt) > larg:
        texte = texte[:-1]
    return texte.rstrip(" ,:") + "…"


ROMAINS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]


def libelle_partie(titre, i):
    nom, _, formule = titre.partition(" : ")
    if nom.endswith("partie"):
        return "%s. %s" % (ROMAINS[i - 1], formule[:1].upper() + formule[1:])
    return titre


def images_par_section():
    par = {}
    for im in json.load(open(os.path.join(RACINE, "build", "images.json"), encoding="utf-8")):
        if os.path.exists(os.path.join(RACINE, im["file"])):
            par.setdefault((im["section"], im["role"]), []).append(im)
    return par


def coller_image(fond, im, boite, position=None):
    """Image entière dans la boite (x, y, l, h), centrée ; renvoie le rectangle occupé."""
    x, y, l, h = boite
    img = Image.open(os.path.join(RACINE, im["file"])).convert("RGB")
    r = min(l / img.width, h / img.height, 2.0)
    img = img.resize((int(img.width * r), int(img.height * r)), Image.LANCZOS)
    px, py = x + (l - img.width) // 2, y + (h - img.height) // 2
    ImageDraw.Draw(fond).rectangle((px - 1, py - 1, px + img.width, py + img.height), outline=LIGNE)
    fond.paste(img, (px, py))
    return px, py, img.width, img.height


def avatar(fond, im, x, y, t):
    img = ImageOps.fit(Image.open(os.path.join(RACINE, im["file"])).convert("RGB"), (t, t), Image.LANCZOS, centering=(0.5, 0.3))
    masque = Image.new("L", (t, t), 0)
    ImageDraw.Draw(masque).ellipse((0, 0, t - 1, t - 1), fill=255)
    fond.paste(img, (x, y), masque)
    ImageDraw.Draw(fond).ellipse((x, y, x + t - 1, y + t - 1), outline=ACCENT, width=3)


def cadre(parties, ip, isec, imgs, chemin):
    fond = Image.new("RGB", (W, H), FOND)
    d = ImageDraw.Draw(fond)
    # table des matières
    d.rectangle((0, 0, BARRE, H), fill=CARTE)
    d.line((BARRE, 0, BARRE, H), fill=LIGNE, width=2)
    f_t, f_p, f_pb, f_s, f_sb = police(22, " Italic"), police(21), police(21, " Bold"), police(19), police(19, " Bold")
    y = 38
    for l in couper(d, "Sortir de la religion sans en fonder une autre ?", f_t, BARRE - 80):
        d.text((40, y), l, font=f_t, fill=ACCENT)
        y += 28
    y += 18
    for i, p in enumerate(parties):
        courant = i == ip
        lib = tronquer(d, libelle_partie(p["titre"], i), f_pb if courant else f_p, BARRE - 90)
        if courant and isec is None:
            d.rounded_rectangle((26, y - 5, BARRE - 22, y + 30), 8, fill=ACCENT)
            d.text((44, y), lib, font=f_pb, fill="#fff")
        else:
            d.text((44, y), lib, font=f_pb if courant else f_p, fill=ACCENT if courant else DOUX)
        y += 37
        if courant:
            for j, s in enumerate(p["sections"]):
                nom = analyser_titre(s["titre"])[0] or s["titre"]
                lib = tronquer(d, nom, f_sb if j == isec else f_s, BARRE - 130)
                if j == isec:
                    d.rounded_rectangle((60, y - 4, BARRE - 22, y + 27), 7, fill=ACCENT)
                    d.text((78, y), lib, font=f_sb, fill="#fff")
                else:
                    d.text((78, y), lib, font=f_s, fill=ENCRE)
                y += 31
            y += 8
    # zone principale
    p = parties[ip]
    x0, larg = BARRE + 70, W - BARRE - 140
    d.text((x0, 50), libelle_partie(p["titre"], ip).upper() if isec is not None else "", font=police(22), fill=ACCENT)
    y = 92
    portrait = None
    if isec is None:
        titre, sous = (p["titre"].partition(" : ")[0], p["titre"].partition(" : ")[2]) if ip else ("Sortir de la religion sans en fonder une autre ?", "Thomas Gourouza")
        lignes_t = couper(d, titre, police(58, " Bold"), larg)
    else:
        s = p["sections"][isec]
        nom, dates, formule = analyser_titre(s["titre"])
        titre, sous = (nom + (" (%s)" % dates.replace("; ", ", ") if dates else "")), formule
        portrait = (imgs.get((s["id"], "portrait")) or [None])[0]
        lignes_t = couper(d, titre, police(58, " Bold"), larg - (190 if portrait else 0))
    if portrait:
        avatar(fond, portrait, x0, y, 160)
    xt = x0 + (190 if portrait else 0)
    for l in lignes_t[:2]:
        d.text((xt, y), l, font=police(58, " Bold"), fill=ENCRE)
        y += 70
    for l in couper(d, sous, police(34, " Italic"), larg - (xt - x0))[:2]:
        d.text((xt, y + 4), l, font=police(34, " Italic"), fill=DOUX)
        y += 44
    y = max(y, 92 + (175 if portrait else 0)) + 30
    # image : figure de la section, sinon image de la partie, couverture pour l'ouverture
    im = None
    if isec is not None:
        im = (imgs.get((p["sections"][isec]["id"], "figure")) or [None])[0]
    if im is None and ip == 0 and isec is None:
        im = imgs[("cover", "cover")][0]
    im = im or imgs[(p["id"], "partimage")][0]
    leg = re.sub(r"<[^>]+>", "", im.get("caption", ""))
    f_leg = police(20, " Italic")
    lignes_leg = couper(d, leg, f_leg, larg)[:2]
    h_img = H - y - 50 - 28 * len(lignes_leg)
    px, py, pl, ph = coller_image(fond, im, (x0, y, larg, h_img))
    yl = py + ph + 14
    for l in lignes_leg:
        d.text((x0 + (larg - d.textlength(l, font=f_leg)) // 2, yl), l, font=f_leg, fill=DOUX)
        yl += 28
    fond.save(chemin)


def duree(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))


def hms(t):
    return "%d:%02d:%02d" % (t // 3600, t % 3600 // 60, t % 60)


def video(parties, segs):
    os.makedirs(CADRES, exist_ok=True)
    imgs = images_par_section()
    liste_img, liste_son, chap, t = [], [], [], 0.0
    for n, (ip, isec, texte) in enumerate(segs):
        mp3 = os.path.join(AUDIO, cle_audio(re.sub(r"\n\s*\n", "\n\n", texte)) + ".mp3")
        if not os.path.exists(mp3):
            raise SystemExit("audio manquant pour le segment %d : lancer d'abord « audio »" % (n + 1))
        png = os.path.join(CADRES, "%03d.png" % n)
        cadre(parties, ip, isec, imgs, png)
        fin_partie = n + 1 == len(segs) or segs[n + 1][0] != ip
        wav = os.path.join(CADRES, "%03d.wav" % n)
        pause = PAUSE_PARTIE if fin_partie else PAUSE_SECTION
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp3, "-af", "apad=pad_dur=%s" % pause,
                        "-ar", "44100", "-ac", "2", wav], check=True)
        dt = duree(wav)
        liste_img.append("file '%s'\nduration %.3f\n" % (png, dt))
        liste_son.append("file '%s'\n" % wav)
        titre = parties[ip]["titre"] if isec is None else parties[ip]["sections"][isec]["titre"]
        chap.append((t, t + dt, titre, ip))
        t += dt
    liste_img.append("file '%s'\n" % png)  # le démultiplexeur concat ignore la durée de la dernière entrée
    open(os.path.join(CADRES, "images.txt"), "w").write("".join(liste_img))
    open(os.path.join(CADRES, "sons.txt"), "w").write("".join(liste_son))
    meta = [";FFMETADATA1", "title=Sortir de la religion sans en fonder une autre ?", "artist=Thomas Gourouza"]
    for a, b, titre, _ in chap:
        meta += ["[CHAPTER]", "TIMEBASE=1/1000", "START=%d" % (a * 1000), "END=%d" % (b * 1000),
                 "title=" + titre.replace("=", "\\=").replace(";", "\\;")]
    open(os.path.join(CADRES, "chapitres.ffmeta"), "w").write("\n".join(meta) + "\n")
    # chapitres YouTube : un par partie
    vus, lignes = set(), []
    for a, _, _, ip in chap:
        if ip not in vus:
            vus.add(ip)
            lignes.append("%s %s" % (hms(a) if a >= 3600 else hms(a)[2:], parties[ip]["titre"]))
    open(os.path.join(OUT, "chapitres.txt"), "w").write("\n".join(lignes) + "\n")
    sortie = os.path.join(OUT, "sortir-de-la-religion.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stats",
                    "-f", "concat", "-safe", "0", "-i", os.path.join(CADRES, "images.txt"),
                    "-f", "concat", "-safe", "0", "-i", os.path.join(CADRES, "sons.txt"),
                    "-i", os.path.join(CADRES, "chapitres.ffmeta"), "-map", "0:v", "-map", "1:a", "-map_metadata", "2",
                    "-vf", "fps=5,format=yuv420p", "-c:v", "libx264", "-tune", "stillimage", "-crf", "20",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", sortie], check=True)
    print("%s  durée %s" % (sortie, hms(t)))


if __name__ == "__main__":
    P = essai()
    S = script(P)
    print("%d segments, %d mots, %d caractères" % (len(S), sum(len(x[2].split()) for x in S), sum(len(x[2]) for x in S)))
    {"audio": lambda: audio(S), "video": lambda: video(P, S)}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: None)()
