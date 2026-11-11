"""Échantillons de voix ElevenLabs pour le podcast : python3 podcast/voix.py, puis ouvrir podcast/out/voix/index.html."""
import html, json, os, urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ICI, "out", "voix")
CLE = dict(l.strip().split("=", 1) for l in open(os.path.join(ICI, "..", ".env.local")) if "=" in l)["ELEVENLABS_API_KEY"]

VOIX = [  # id, nom, profil (bibliothèque partagée ElevenLabs, langue fr, usage narration)
    ("aQROLel5sQbj1vuIVi6B", "Nicolas", "Homme, la quarantaine, accent parisien. Narrateur d'audioguides, la voix française la plus utilisée de la bibliothèque."),
    ("Qrl71rx6Yg8RvyPYRGCQ", "Guillaume", "Homme, 40 ans, voix chaude et grave. Narration et vulgarisation."),
    ("cTNP6ZM2mLTKj2BFhxEh", "Paul", "Homme, posé et assuré. Voix de podcast et de documentaire."),
    ("txtf1EDouKke753vN8SL", "Jeanne", "Femme, jeune, accent parisien. Narration éducative."),
    ("hFgOzpmS0CMtL2to8sAl", "Camille", "Femme, voix calme et grave. Livres audio, vidéos institutionnelles."),
]

TEXTE = ("On raconte volontiers l'histoire de la critique de la religion comme une course de relais. "
         "Lucrèce aurait passé le témoin à Spinoza, Spinoza aux Lumières, les Lumières à Feuerbach, Feuerbach à Marx, "
         "Marx à Nietzsche, Nietzsche à Freud. Cette histoire est fausse. Depuis deux siècles, chaque critique de la religion "
         "est accusée par la suivante d'être restée religieuse. Max Stirner l'a dit le premier : « Unsere Atheisten sind "
         "fromme Leute », nos athées sont des gens pieux. Peut-on sortir de la religion sans en fonder une autre ?")


def tts(voix_id, chemin):
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/text-to-speech/%s?output_format=mp3_44100_128" % voix_id,
        data=json.dumps({"text": TEXTE, "model_id": "eleven_multilingual_v2", "language_code": "fr"}).encode(),
        headers={"xi-api-key": CLE, "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r, open(chemin, "wb") as f:
        f.write(r.read())


os.makedirs(OUT, exist_ok=True)
cartes = []
for vid, nom, profil in VOIX:
    mp3 = os.path.join(OUT, nom.lower() + ".mp3")
    if not os.path.exists(mp3):
        tts(vid, mp3)
        print("ok", nom)
    cartes.append('<article><h2>%s</h2><p>%s</p><audio controls preload="none" src="%s.mp3"></audio><code>%s</code></article>'
                  % (nom, html.escape(profil), nom.lower(), vid))

open(os.path.join(OUT, "index.html"), "w").write("""<!doctype html><html lang="fr"><meta charset="utf-8">
<title>Voix du podcast</title><meta name="viewport" content="width=device-width">
<style>body{font:17px/1.5 Georgia,serif;background:#f4ecd8;color:#3b2f20;max-width:760px;margin:2em auto;padding:0 16px}
article{background:#fbf6ea;border:1px solid #d8c9a8;border-radius:8px;padding:1em 1.2em;margin:1em 0}
h2{margin:0}audio{width:100%%;margin:.5em 0}code{font-size:12px;color:#8a7a60}blockquote{font-style:italic}</style>
<h1>Cinq voix pour le podcast</h1><p>Même texte pour chaque voix (modèle eleven_multilingual_v2) :</p>
<blockquote>%s</blockquote>%s</html>""" % (html.escape(TEXTE), "\n".join(cartes)))
print(os.path.join(OUT, "index.html"))
