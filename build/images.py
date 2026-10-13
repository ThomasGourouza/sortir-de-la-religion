#!/usr/bin/env python3
"""Constitue les images du site depuis Wikimedia Commons et Wikidata.

Usage : python3 build/images.py   (depuis la racine du site)

Pour chaque cible : resolution du fichier Commons (directement, ou via la
propriete P18 de Wikidata pour les portraits), lecture de la licence et des
credits (extmetadata), refus de toute licence non libre, telechargement de la
vignette, puis ecriture de build/images.json.

Si une erreur SSL survient : export SSL_CERT_FILE=/etc/ssl/cert.pem
"""

import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "build", "images.json")
UA = "SortirDeLaReligionSite/1.0 (site personnel de lecture)"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
PAUSE = 1.0
MIN_BYTES = 5 * 1024

# ---------------------------------------------------------------------------
# Cibles
#   qid      : element Wikidata dont on prend la P18 (p18 = indice, defaut 0)
#   commons  : nom exact du fichier Commons (sans "File:")
#   page     : page a rendre pour un PDF ou un DjVu
#   width    : largeur de vignette demandee (480 par defaut)
#   artist   : remplace l'auteur lu dans les metadonnees quand il est confus
# ---------------------------------------------------------------------------

def P(section, slug, qid, name, caption=None, p18=0, artist=None, commons=None):
    t = {"section": section, "role": "portrait", "file": f"images/auteurs/{slug}",
         "alt": f"Portrait de {name}", "caption": caption or name, "p18": p18}
    if commons:
        t["commons"] = commons
    else:
        t["qid"] = qid
    if artist:
        t["artist"] = artist
    return t


def F(section, folder, slug, commons, alt, caption, width=480, page=None, artist=None, role="figure"):
    t = {"section": section, "role": role, "file": f"images/{folder}/{slug}",
         "commons": commons, "alt": alt, "caption": caption, "width": width}
    if page:
        t["page"] = page
    if artist:
        t["artist"] = artist
    return t


TARGETS = [
    # ----------------------------------------------------------- couverture
    F("cover", "art", "couverture", "Rembrandt - The Philosopher in Meditation.jpg",
      "Un vieillard assis près d'une fenêtre, à côté d'un escalier en colimaçon plongé dans l'ombre",
      "Rembrandt, Philosophe en méditation (1632, Paris, musée du Louvre).",
      width=800, role="cover"),

    # ----------------------------------------------------------- portraits
    P("epicure-et-lucrece", "epicure", "Q43216", "Épicure",
      "Épicure, portrait en marbre, copie romaine d'un original grec (Rome, Museo Nazionale Romano, Palazzo Massimo).",
      artist="Sculpteur inconnu, photo Marie-Lan Nguyen"),
    P("epicure-et-lucrece", "lucrece", "Q47154", "Lucrèce",
      "Lucrèce : aucun portrait authentique n'est connu, cette effigie est conventionnelle.",
      artist="Auteur inconnu"),
    P("maitre-eckhart", "eckhart", "Q76548", "Maître Eckhart",
      "Figure traditionnellement identifiée comme Maître Eckhart, détail de la fresque d'Andrea di Bonaiuto, chapelle des Espagnols, Santa Maria Novella, Florence (v. 1365-1367) ; aucun portrait authentique n'existe."),
    P("pascal", "pascal", "Q1290", "Blaise Pascal", "Blaise Pascal, gravure de Gérard Edelinck."),
    P("spinoza", "spinoza", "Q35802", "Baruch Spinoza", artist="Anonyme"),
    P("bayle", "bayle", "Q214816", "Pierre Bayle", artist="Attribué à Louis Ferdinand Elle le Jeune"),
    P("hume", "hume", "Q37160", "David Hume", "David Hume, portrait par Allan Ramsay."),
    P("voltaire", "voltaire", "Q9068", "Voltaire",
      "Voltaire, portrait par Nicolas de Largillière (Paris, musée Carnavalet)."),
    P("d-holbach", "holbach", "Q7104", "le baron d'Holbach",
      "Paul Henri Thiry d'Holbach, portrait par Alexander Roslin."),
    P("kant", "kant", "Q9312", "Immanuel Kant"),
    P("friedrich-schleiermacher", "schleiermacher", "Q76576", "Friedrich Schleiermacher"),
    P("georg-wilhelm-friedrich-hegel", "hegel", "Q9235", "Hegel",
      "Hegel, portrait par Jakob Schlesinger (1831)."),
    P("david-friedrich-strauss-et-bruno-bauer", "strauss", "Q57219", "David Friedrich Strauss"),
    P("david-friedrich-strauss-et-bruno-bauer", "bauer", "Q76878", "Bruno Bauer", artist="Auteur inconnu"),
    P("ernest-renan", "renan", "Q157155", "Ernest Renan"),
    P("ludwig-feuerbach", "feuerbach", "Q76422", "Ludwig Feuerbach"),
    P("max-stirner", "stirner", "Q76725", "Max Stirner",
      "Max Stirner, détail du dessin d'Engels représentant les Freien (1842) ; on ne connaît de lui que des croquis d'Engels."),
    P("karl-marx-et-friedrich-engels", "marx", "Q9061", "Karl Marx"),
    P("karl-marx-et-friedrich-engels", "engels", "Q34787", "Friedrich Engels", artist="William Hall"),
    P("soren-kierkegaard", "kierkegaard", "Q6512", "Søren Kierkegaard", artist="Bibliothèque royale du Danemark"),
    P("auguste-comte", "comte", "Q12718", "Auguste Comte", "Auguste Comte, portrait conservé à la Maison d'Auguste Comte, Paris.", artist="photo Jean-Pierre Dalbéra"),
    P("arthur-schopenhauer", "schopenhauer", "Q38193", "Arthur Schopenhauer",
      "Arthur Schopenhauer, photographie de J. Schäfer (1859)."),
    P("dostoievski", "dostoievski", "Q991", "Fiodor Dostoïevski",
      "Dostoïevski, portrait par Vassili Perov (1872, Moscou, galerie Tretiakov)."),
    P("nietzsche", "nietzsche", "Q9358", "Friedrich Nietzsche"),
    P("durkheim", "durkheim", "Q15948", "Émile Durkheim"),
    P("weber", "weber", "Q9387", "Max Weber", "Max Weber en 1918."),
    P("william-james", "william-james", "Q125249", "William James",
      "William James, photographie d'Alice Boughton (v. 1907)."),
    P("rudolf-otto", "otto", "Q76748", "Rudolf Otto", artist="Photographe inconnu"),
    P("freud", "freud", "Q9215", "Sigmund Freud", "Sigmund Freud, photographie de Max Halberstadt."),
    P("bergson", "bergson", "Q42156", "Henri Bergson"),
    P("heidegger", "heidegger", "Q48301", "Martin Heidegger", "Martin Heidegger en 1960."),
    P("barth", "barth", "Q107473", "Karl Barth"),
    P("bonhoeffer", "bonhoeffer", "Q76326", "Dietrich Bonhoeffer"),
    P("simone-weil", "simone-weil", "Q157309", "Simone Weil"),
    P("bataille", "bataille", "Q207359", "Georges Bataille", "Georges Bataille vers 1943."),
    P("sartre", "sartre", "Q9364", "Jean-Paul Sartre", "Jean-Paul Sartre en 1967.", artist="T1980"),
    P("camus", "camus", "Q34670", "Albert Camus", artist="United Press International"),
    P("marion", "marion", "Q460824", "Jean-Luc Marion"),
    P("carl-schmitt", "schmitt", "Q77148", "Carl Schmitt",
      "Carl Schmitt en 1904, détail d'une photographie de classe."),
    P("marcel-gauchet", "gauchet", "Q1027750", "Marcel Gauchet", "Marcel Gauchet en 2017."),
    P("charles-taylor", "taylor", "Q311757", "Charles Taylor", "Charles Taylor en 2019."),
    P("jurgen-habermas", "habermas", "Q76357", "Jürgen Habermas", artist="Wolfram Huke"),
    # Pierre Hadot : la P18 (PierreHadot.jpg) porte CC0 mais "tous droits reserves" en auteur, sans permission : ecartee.
    P("michel-foucault", "foucault", "Q44272", "Michel Foucault", "Michel Foucault en 1974."),
    P("andre-comte-sponville", "comte-sponville", "Q247016", "André Comte-Sponville",
      "André Comte-Sponville au Salon du livre de Paris, 2014."),
    P("luc-ferry", "ferry", "Q740110", "Luc Ferry", "Luc Ferry au Salon du livre de Paris, 2017."),
    P("comte-sponville-et-ferry", "comte-sponville", "Q247016", "André Comte-Sponville",
      "André Comte-Sponville au Salon du livre de Paris, 2014."),
    P("comte-sponville-et-ferry", "ferry", "Q740110", "Luc Ferry", "Luc Ferry au Salon du livre de Paris, 2017."),
    P("abdennour-bidar", "bidar", "Q2821215", "Abdennour Bidar"),
    P("michel-onfray", "onfray", "Q7060", "Michel Onfray", "Michel Onfray en 2012."),

    # ----------------------------------------------------------- figures : pascal (3)
    F("pascal", "oeuvres", "pascal-memorial", "Mémorial de Pascal autographe (Brunschwicg).jpg",
      "Feuillet manuscrit couvert d'une écriture serrée, avec une croix en tête",
      "Le Mémorial de Pascal (nuit du 23 novembre 1654), fac-similé de l'autographe dans l'édition Brunschvicg : le feuillet du « Dieu d'Abraham, Dieu d'Isaac, Dieu de Jacob, non des philosophes et des savants ».",
      artist="Blaise Pascal, fac-similé de l'édition Brunschvicg"),
    F("pascal", "art", "rembrandt-sacrifice-isaac", "Rembrandt Abraham's Sacrifice (Hermitage).jpg",
      "Un ange retient le bras d'Abraham au moment où il va égorger Isaac ; le couteau tombe",
      "Rembrandt, Le Sacrifice d'Abraham (1635, Saint-Pétersbourg, Ermitage) : le Dieu d'Abraham et d'Isaac, que le Mémorial oppose au Dieu des philosophes.",
      width=800),
    F("pascal", "art", "michel-ange-isaie", "Jesaja (Michelangelo).jpg",
      "Le prophète Isaïe assis, un livre fermé sous la main, se détournant vers un enfant",
      "Michel-Ange, le prophète Isaïe, voûte de la chapelle Sixtine (1508-1512) : Isaïe est le prophète du Dieu caché, Deus absconditus (Is 45, 15), au centre des Pensées.",
      width=800),

    # ----------------------------------------------------------- figures : pages de titre
    F("spinoza", "oeuvres", "spinoza-tractatus-1670",
      "Benedictus de Spinoza - Tractatus theologico-politicus continens dissertationes aliquot, Hamburg, Henricus Künrath, 1670.jpg",
      "Page de titre imprimée en latin du Tractatus theologico-politicus",
      "Page de titre du Tractatus theologico-politicus (1670), paru sans nom d'auteur et sous une fausse adresse d'imprimeur à Hambourg : le livre où Spinoza soumet l'Écriture à la critique historique."),
    F("bayle", "oeuvres", "bayle-pensees-comete",
      "Bayle - Pensées diverses sur la comète, édition 1749, tome 1.djvu",
      "Page de titre des Pensées diverses sur la comète, édition de 1749",
      "Page de titre des Pensées diverses écrites à un docteur de Sorbonne à l'occasion de la comète (sixième édition, 1749) : le livre de l'hypothèse d'une société d'athées, né de la comète de décembre 1680.",
      page=9),
    F("hume", "oeuvres", "hume-dialogues-1779", "Hume titlepage1779.jpg",
      "Page de titre des Dialogues concerning Natural Religion, 1779",
      "Page de titre des Dialogues concerning Natural Religion (1779), publiés trois ans après la mort de Hume, qui les avait gardés inédits de son vivant."),
    F("d-holbach", "oeuvres", "holbach-systeme-nature-1770",
      "Holbach - Système de la nature, 1770, tome 1.djvu",
      "Page de titre du Système de la nature, attribué à M. Mirabaud, Londres, 1770",
      "Page de titre du Système de la nature (1770), paru sous le nom de Mirabaud, mort dix ans plus tôt, et sous l'adresse fictive de Londres.",
      page=5, artist="Paul Henri Thiry d'Holbach"),
    F("kant", "oeuvres", "kant-religion-1793", "Religion within the bounds of bare reason (German edition).jpg",
      "Page de titre de Die Religion innerhalb der Grenzen der bloßen Vernunft, 1793",
      "Page de titre de Die Religion innerhalb der Grenzen der bloßen Vernunft (1793), le livre qui valut à Kant la réprimande royale de 1794."),
    F("friedrich-schleiermacher", "oeuvres", "schleiermacher-uber-die-religion-1799",
      "Cover of 1799 edition of Über die Religion.jpg",
      "Page de titre de Über die Religion, 1799",
      "Page de titre de Über die Religion. Reden an die Gebildeten unter ihren Verächtern (1799), paru sans nom d'auteur."),
    F("david-friedrich-strauss-et-bruno-bauer", "oeuvres", "strauss-leben-jesu-1835",
      "David Friedrich Strauss - Das Leben Jesu (1) - Titelseite.jpg",
      "Page de titre du premier volume de Das Leben Jesu de Strauss",
      "Page de titre du premier volume de Das Leben Jesu, kritisch bearbeitet (1835), qui fait du mythe la catégorie centrale de la critique des Évangiles."),
    F("ernest-renan", "oeuvres", "renan-vie-de-jesus-1863", "Vie de Jésus (Ernest Renan).jpg",
      "Page de titre de la Vie de Jésus d'Ernest Renan, 1863",
      "Page de titre de la Vie de Jésus (1863), premier volume de l'Histoire des origines du christianisme.", artist="Ernest Renan, numérisation Gallica"),
    F("ludwig-feuerbach", "oeuvres", "feuerbach-wesen-des-christenthums-1841",
      "Das Wesen des Christentums (1841).pdf",
      "Page de titre en caractères gothiques de Das Wesen des Christenthums, Leipzig, 1841",
      "Page de titre de Das Wesen des Christenthums (Leipzig, Otto Wigand, 1841).",
      page=5, artist="Ludwig Feuerbach"),
    F("max-stirner", "oeuvres", "stirner-der-einzige", "Ein1844v2.png",
      "Page de titre de Der Einzige und sein Eigenthum",
      "Page de titre de Der Einzige und sein Eigenthum (Leipzig, Otto Wigand), paru en octobre 1844 avec le millésime 1845."),
    F("karl-marx-et-friedrich-engels", "oeuvres", "marx-kapital-1867", "Kapital titel bd1.png",
      "Page de titre du premier livre de Das Kapital, Hambourg, 1867",
      "Page de titre du premier livre de Das Kapital (Hambourg, Otto Meissner, 1867), en fac-similé."),
    F("auguste-comte", "oeuvres", "comte-catechisme-positiviste-1852",
      "Catéchisme positiviste, ou, Sommaire exposition de la religion universelle - en onze entretiens systématiques entre une femme et un Prêtre de l'humanité (IA catchismeposit00comt).pdf",
      "Page de titre du Catéchisme positiviste, Paris, 1852",
      "Page de titre du Catéchisme positiviste (1852), « sommaire exposition de la religion universelle » en entretiens entre une femme et un prêtre de l'Humanité.",
      page=9, artist="Auguste Comte"),
    F("arthur-schopenhauer", "oeuvres", "schopenhauer-welt-1819",
      "Schopenhauer Die Welt als Wille und Vorstellung 1819.jpg",
      "Exemplaire ouvert de l'édition originale de Die Welt als Wille und Vorstellung",
      "Édition originale de Die Welt als Wille und Vorstellung (Leipzig, Brockhaus, millésime 1819, parue à la fin de 1818).", artist="photo H.-P. Haack"),
    F("dostoievski", "oeuvres", "dostoievski-karamazov", "Dostoevsky-Brothers Karamazov.jpg",
      "Page imprimée en russe portant le titre Les Frères Karamazov",
      "Les Frères Karamazov dans le Rousski Vestnik, où le roman parut en feuilleton (1879-1880)."),
    F("nietzsche", "oeuvres", "nietzsche-frohliche-wissenschaft-1882", "FW82.jpg",
      "Page de titre de la première édition de Die fröhliche Wissenschaft, 1882",
      "Page de titre de la première édition de Die fröhliche Wissenschaft (1882), où paraît au § 125 l'insensé qui annonce la mort de Dieu.",
      artist="Friedrich Nietzsche, Chemnitz, Ernst Schmeitzner"),
    F("durkheim", "oeuvres", "durkheim-formes-elementaires-1912", "E.Durkheim Form-Elem-Vie-Relig 1912.jpg",
      "Page de titre des Formes élémentaires de la vie religieuse, 1912",
      "Les Formes élémentaires de la vie religieuse (1912), où Durkheim fait du sacré la matrice de la société."),
    F("william-james", "oeuvres", "james-varieties-1902",
      "The varieties of religious experience, a study in human nature - frontcover.jpg",
      "Couverture de The Varieties of Religious Experience, 1902",
      "Couverture de The Varieties of Religious Experience (1902), issu des Gifford Lectures données à Édimbourg en 1901-1902."),
    F("freud", "oeuvres", "freud-zukunft-einer-illusion-1927", "Freud 1927 Die Zukunft einer Illusion.jpg",
      "Couverture de la première édition de Die Zukunft einer Illusion, 1927",
      "Couverture de la première édition de Die Zukunft einer Illusion (1927).", artist="Graphiste inconnu"),

    # ----------------------------------------------------------- figures : personnes
    F("ludwig-feuerbach", "auteurs", "george-eliot", "George Eliot, por François D'Albert Durade.jpg",
      "Portrait de George Eliot jeune, assise",
      "George Eliot, portrait par François D'Albert Durade : traductrice de Feuerbach, elle publie The Essence of Christianity en 1854 sous son nom de Marian Evans.", artist="François D'Albert Durade (réplique)"),
    F("freud", "auteurs", "romain-rolland", "Romain Rolland 1915.jpg",
      "Photographie de Romain Rolland en 1915",
      "Romain Rolland en 1915 : c'est à sa lettre sur le « sentiment océanique » que Freud répond au début de Das Unbehagen in der Kultur (1930)."),

    # ----------------------------------------------------------- figures : art et lieux
    F("georg-wilhelm-friedrich-hegel", "art", "velazquez-christ-crucifie", "Cristo crucificado.jpg",
      "Le Christ en croix sur fond noir, la tête inclinée",
      "Velázquez, Christ crucifié (v. 1632, Madrid, Prado) : le Vendredi saint spéculatif, où Hegel reprend le « Gott selbst ist tot » du cantique luthérien.",
      width=800),
    F("dostoievski", "art", "duccio-tentation", "Duccio - The Temptation on the Mount.jpg",
      "Le Christ sur une montagne repousse le diable ; à ses pieds, des villes miniatures",
      "Duccio, La Tentation du Christ sur la montagne (1308-1311, New York, Frick Collection), panneau de la Maestà de Sienne : les tentations que reprend le Grand Inquisiteur.",
      width=800),
    F("dostoievski", "art", "berruguete-autodafe",
      "Pedro Berruguete Saint Dominic Presiding over an Auto-da-fe 1495.jpg",
      "Saint Dominique sur une estrade préside un autodafé ; en bas, des condamnés au bûcher",
      "Pedro Berruguete, Saint Dominique présidant un autodafé (v. 1493-1499, Madrid, Prado) : l'Inquisition, que le Grand Inquisiteur transporte à Séville.",
      width=800),
    F("nietzsche", "art", "caravage-conversion-saint-paul",
      "Conversion on the Way to Damascus-Caravaggio (c.1600-1).jpg",
      "Saul renversé de son cheval, les bras ouverts vers la lumière",
      "Caravage, La Conversion de saint Paul (1600-1601, Rome, Santa Maria del Popolo, chapelle Cerasi) : Paul, le « Dysangelist » de Der Antichrist.",
      width=800),
    F("nietzsche", "art", "gerome-diogene", "Jean-Léon Gérôme - Diogenes - Walters 37131.jpg",
      "Diogène assis dans sa jarre allume une lanterne, entouré de chiens",
      "Jean-Léon Gérôme, Diogène (1860, Baltimore, Walters Art Museum) : la lanterne en plein jour, modèle de l'insensé qui cherche Dieu au § 125 du Gai Savoir.",
      width=800),
    F("camus", "art", "titien-sisyphe", "Titian - Sisyphus - Madrid - Prado.jpg",
      "Sisyphe portant un énorme rocher sur ses épaules",
      "Titien, Sisyphe (1548-1549, Madrid, Prado) : la figure dont Camus fait le héros de l'absurde.",
      width=800),
    F("jurgen-habermas", "art", "michel-ange-creation-adam", "Michelangelo - Creation of Adam (cropped).jpg",
      "Dieu tend le doigt vers celui d'Adam allongé",
      "Michel-Ange, La Création d'Adam, voûte de la Sixtine (v. 1511) : l'homme créé à l'image de Dieu (Gn 1, 27), que Habermas veut traduire dans le langage séculier de la dignité.",
      width=800),
    F("auguste-comte", "art", "temple-humanite-paris", "Paris, Rue Payenne, Temple de l'Humanité, Façade.jpg",
      "Façade du temple de l'Humanité, rue Payenne, avec un buste et une inscription",
      "Façade du temple de l'Humanité, 5 rue Payenne à Paris : la religion positiviste a eu ses lieux de culte.",
      width=800),
    F("auguste-comte", "art", "temple-positiviste-porto-alegre", "Templo Positivista em Porto Alegre.JPG",
      "Façade à colonnes du temple positiviste de Porto Alegre",
      "Le temple positiviste de Porto Alegre (Brésil) : le culte de l'Humanité a pris racine au Brésil, dont le drapeau porte la devise comtienne Ordem e Progresso.",
      width=800),

    # ----------------------------------------------------------- les Anciens, les monothéismes, l'âge classique
    F("premiere-partie", "art", "raphael-ecole-athenes",
      "\"The School of Athens\" by Raffaello Sanzio da Urbino.jpg",
      "Philosophes grecs réunis sous des voûtes antiques autour de Platon et d'Aristote",
      "Raphaël, L'École d'Athènes (1509-1511, Vatican, chambre de la Signature) : au centre, Platon montrant le ciel et Aristote tendant la main vers la terre ; à gauche, la figure au turban traditionnellement identifiée comme Averroès.",
      width=800),
    P("platon", "platon", "Q859", "Platon",
      "Platon, copie romaine du portrait réalisé par Silanion vers 370 av. J.-C. pour l'Académie (Rome, Musei Capitolini).",
      artist="D'après Silanion, photo Marie-Lan Nguyen"),
    P("aristote", "aristote", "Q868", "Aristote",
      "Aristote, copie romaine en marbre d'un bronze de Lysippe (v. 330 av. J.-C.), le manteau d'albâtre est moderne (Rome, Museo Nazionale Romano, Palazzo Altemps).",
      artist="D'après Lysippe, photo Jastrow"),
    P("plotin", "plotin", "Q134189", "Plotin",
      "Tête en marbre trouvée à Ostie (IIIe siècle ap. J.-C., Ostie, Museo Ostiense), l'une des quatre répliques d'un même portrait ; l'identification avec Plotin est traditionnelle et discutée.",
      artist="Sculpteur inconnu, photo Sailko",
      commons="Ritratto di plotino, da ostia, terme del filosofo, 250-300 ca. (museo arch. ostia).JPG"),
    P("averroes", "averroes", "Q39837", "Averroès",
      "Averroès, détail du Triomphe de saint Thomas d'Aquin d'Andrea di Bonaiuto, chapelle des Espagnols, Santa Maria Novella, Florence (v. 1365-1367) ; aucun portrait authentique n'existe, l'effigie est conventionnelle.",
      artist="Andrea di Bonaiuto, photo Sailko",
      commons="Andrea di bonaiuto, apoteosi di san tommaso d'aquino, 11 averroè.jpg"),
    P("maimonide", "maimonide", "Q127398", "Maïmonide",
      "Maïmonide, portrait imaginaire paru dans le Thesaurus antiquitatum sacrarum de Blasio Ugolini (1744), dont dérivent les effigies modernes ; aucun portrait authentique n'existe.",
      artist="Graveur inconnu", commons="Rambam-portrait.jpg"),
    F("maimonide", "oeuvres", "maimonide-moreh-nevukhim-copenhague", "Maimonides teaching.jpeg",
      "Page enluminée d'un manuscrit hébreu : un maître assis sous un ciel étoilé enseigne à un groupe d'hommes debout",
      "Moreh Nevukhim (Guide des égarés) dans la traduction hébraïque, manuscrit enluminé daté de 1347-1348 (Copenhague, Bibliothèque royale, Cod. Heb. 37) : un maître enseigne devant la voûte céleste.",
      artist="Copiste et enlumineur anonymes"),
    P("montaigne", "montaigne", "Q41568", "Michel de Montaigne",
      "Michel de Montaigne, portrait anonyme parfois attribué à Daniel Dumonstier (Chantilly, musée Condé).",
      artist="Anonyme"),
    F("montaigne", "oeuvres", "montaigne-exemplaire-bordeaux", "B330636101 S1238ResC EB 0001.jpg",
      "Frontispice gravé des Essais, édition de 1588, avec des corrections manuscrites dans le cartouche central",
      "Page de titre gravée des Essais (Paris, Abel L'Angelier, 1588), dans l'Exemplaire de Bordeaux, que Montaigne a couvert de corrections et d'additions jusqu'à sa mort (Bordeaux, bibliothèque municipale).",
      artist="Michel de Montaigne, Bibliothèque municipale de Bordeaux"),
    P("descartes", "descartes", "Q9191", "René Descartes",
      "René Descartes, d'après Frans Hals (Paris, musée du Louvre).", artist="D'après Frans Hals"),
    F("descartes", "oeuvres", "descartes-meditationes-1641", "Meditationes de prima philosophia 1641.jpg",
      "Page de titre en latin des Meditationes de prima philosophia, Paris, 1641",
      "Page de titre de la première édition des Meditationes de prima philosophia (Paris, Michel Soly, 1641), « in qua Dei existentia et animae immortalitas demonstratur ».",
      artist="René Descartes, Bibliothèque nationale de France"),
    P("leibniz", "leibniz", "Q9047", "Gottfried Wilhelm Leibniz",
      "Leibniz, portrait par Christoph Bernhard Francke (v. 1695, Brunswick, Herzog Anton Ulrich-Museum)."),
    F("leibniz", "oeuvres", "leibniz-theodicee-1734", "Théodicée title page.jpeg",
      "Page de titre des Essais de théodicée, Amsterdam, 1734",
      "Page de titre des Essais de théodicée sur la bonté de Dieu, la liberté de l'homme et l'origine du mal, dans la nouvelle édition d'Amsterdam (1734) ; la première édition parut en 1710.",
      artist="Gottfried Wilhelm Leibniz"),
    P("rousseau", "rousseau", "Q6527", "Jean-Jacques Rousseau",
      "Jean-Jacques Rousseau, pastel de Maurice Quentin de La Tour, réplique du portrait exposé au Salon de 1753 (Saint-Quentin, musée Antoine-Lécuyer)."),
    F("rousseau", "oeuvres", "rousseau-emile-1762", "EmileTitle.jpeg",
      "Page de titre d'Émile, ou De l'éducation, 1762",
      "Page de titre de la première édition d'Émile, ou De l'éducation (1762), dont le livre IV contient la Profession de foi du vicaire savoyard ; le livre fut condamné à Paris et à Genève.",
      artist="Jean-Jacques Rousseau"),
    P("ricoeur", "ricoeur", "Q192066", "Paul Ricœur",
      "Paul Ricœur (à droite) avec Maarten van Buuren au colloque de Cerisy-la-Salle, août 1988.",
      artist="Jmendrik", commons="Maarten van Buuren and Paul Ricoeur 1988.jpg"),
    P("levinas", "levinas", "Q153034", "Emmanuel Levinas", "Emmanuel Levinas en 1991."),
    P("wittgenstein", "wittgenstein", "Q9391", "Ludwig Wittgenstein",
      "Ludwig Wittgenstein, photographie de Moritz Nähr (1930)."),
    F("wittgenstein", "oeuvres", "wittgenstein-tractatus-1922", "Tractatus title page 1922 Harcourt.png",
      "Page de titre du Tractatus Logico-Philosophicus, 1922",
      "Page de titre de la première édition anglaise du Tractatus Logico-Philosophicus (1922), parue simultanément à Londres chez Kegan Paul et à New York chez Harcourt, Brace, avec l'introduction de Bertrand Russell.",
      artist="Ludwig Wittgenstein"),
    P("jaspers", "jaspers", "Q76509", "Karl Jaspers", "Karl Jaspers en 1946.",
      artist="Photographe inconnu (Mondadori)"),
    F("pourquoi-y-a-t-il-quelque-chose-plutot-que-rien", "art", "friedrich-moine-bord-de-mer",
      "Friedrich, Caspar David - Mönch am Meer - Alte Nationalgalerie in Berlin.jpg",
      "Une minuscule silhouette de moine sur une grève, face à une mer sombre sous un ciel immense",
      "Caspar David Friedrich, Le Moine au bord de la mer (1808-1810, Berlin, Alte Nationalgalerie) : l'homme seul devant l'immensité, figure de l'étonnement qu'il y ait un monde plutôt que rien.",
      width=800),

    # ----------------------------------------------------------- cartes des parties
    F("prologue", "art", "partie-prologue", "\"The School of Athens\" by Raffaello Sanzio da Urbino.jpg",
      "Philosophes grecs réunis sous des voûtes antiques autour de Platon et d'Aristote",
      "Raphaël, L'École d'Athènes (1509-1511, Vatican, chambre de la Signature).", role="partcard"),
    F("troisieme-partie", "art", "partie-deuxieme",
      "Joseph Wright of Derby - Philosopher giving a lecture on the orrery - Google Art Project.jpg",
      "Des visages éclairés par la lampe centrale d'un planétaire mécanique",
      "Joseph Wright of Derby, Un philosophe faisant une conférence sur le planétaire (v. 1766, Derby Museum).",
      role="partcard"),
    F("quatrieme-partie", "art", "partie-troisieme", "Caspar David Friedrich - Wanderer above the sea of fog.jpg",
      "Un homme de dos sur un rocher contemple une mer de nuages",
      "Caspar David Friedrich, Le Voyageur contemplant une mer de nuages (v. 1818, Hambourg, Kunsthalle).",
      role="partcard"),
    F("cinquieme-partie", "art", "partie-quatrieme", "Die Freien by Friedrich Engels.jpg",
      "Caricature à la plume d'un groupe d'hommes attablés qui se disputent",
      "Friedrich Engels, les Freien (dessin, v. 1842) : le cercle berlinois de Bruno Bauer et de Max Stirner.",
      role="partcard"),
    F("sixieme-partie", "art", "partie-cinquieme",
      "The Body of the Dead Christ in the Tomb, and a detail, by Hans Holbein the Younger.jpg",
      "Le corps du Christ mort allongé dans un tombeau étroit, et un détail du visage",
      "Hans Holbein le Jeune, Le Christ mort au tombeau (1521-1522, Bâle, Kunstmuseum) : tableau qui bouleversa Dostoïevski à Bâle en 1867, et qu'il met en scène dans L'Idiot.",
      role="partcard"),
    F("septieme-partie", "art", "partie-sixieme", "Jules Breton - La Bénédiction des blés en Artois.jpg",
      "Procession villageoise avec dais et bannières traversant un champ de blé",
      "Jules Breton, La Bénédiction des blés en Artois (1857) : la religion vécue, objet des sciences de la religion.",
      role="partcard"),
    F("huitieme-partie", "art", "partie-septieme", "Caspar David Friedrich - Abtei im Eichwald - Google Art Project.jpg",
      "Ruine d'abbaye gothique entourée de chênes nus dans la brume",
      "Caspar David Friedrich, L'Abbaye dans une forêt de chênes (1809-1810, Berlin, Alte Nationalgalerie).",
      role="partcard"),
    F("neuvieme-partie", "art", "partie-huitieme", "Notre Dame, Paris, France, ca. 1890-1900.jpg",
      "Façade de Notre-Dame de Paris en photochromie",
      "Notre-Dame de Paris vers 1890-1900 (Library of Congress).", artist="Photographe inconnu",
      role="partcard"),
    F("dixieme-partie", "art", "partie-neuvieme", "Marcus Aurelius Capitoline Hill September 2015-1.jpg",
      "Statue équestre en bronze de Marc Aurèle, le bras tendu",
      "Statue équestre de Marc Aurèle sur la place du Capitole à Rome (réplique ; l'original en bronze est aux musées du Capitole).",
      role="partcard"),
    F("conclusion", "art", "partie-conclusion",
      "Caspar David Friedrich - Woman before the Rising Sun (Woman before the Setting Sun) - WGA08253.jpg",
      "Une femme de dos, les bras ouverts, face au soleil bas",
      "Caspar David Friedrich, Femme devant le soleil couchant (v. 1818, Essen, Museum Folkwang).",
      role="partcard"),
    F("premiere-partie", "art", "partie-anciens-monotheismes",
      "\"The School of Athens\" by Raffaello Sanzio da Urbino.jpg",
      "Philosophes grecs réunis sous des voûtes antiques autour de Platon et d'Aristote",
      "Raphaël, L'École d'Athènes (1509-1511, Vatican, chambre de la Signature) : Platon et Aristote au centre ; à gauche, la figure au turban traditionnellement identifiée comme Averroès.",
      role="partcard"),
    F("deuxieme-partie", "art", "partie-age-classique",
      "Frans Hals - Portret van René Descartes.jpg",
      "Portrait de Descartes en habit noir et col blanc",
      "René Descartes, d'après Frans Hals (Paris, musée du Louvre).",
      artist="D'après Frans Hals", role="partcard"),
]

# ---------------------------------------------------------------------------

FREE = re.compile(r"^(public domain|pd\b|pdm|cc0|cc[ -]by(-sa)?[ -]\d|cc[ -]by(-sa)?$|no restrictions)", re.I)
NONFREE = re.compile(r"\bnc\b|\bnd\b|fair use|non-free|nonfree|noncommercial|non-commercial", re.I)


def is_free(lic):
    return bool(lic) and bool(FREE.match(lic.strip())) and not NONFREE.search(lic)


def http_get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
            time.sleep(PAUSE)
            return data if binary else json.loads(data.decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                wait = int(e.headers.get("Retry-After") or 0) or 15 * (attempt + 1)
                print(f"   {e.code}, pause {wait} s", flush=True)
                time.sleep(wait)
                continue
            raise
    raise RuntimeError("trop de refus : " + url)


def api(base, **params):
    params.setdefault("format", "json")
    return http_get(base + "?" + urllib.parse.urlencode(params))


def strip_html(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = html.unescape(s)
    s = re.sub(r"date QS:\S+", "", s)
    return re.sub(r"\s+", " ", s).strip()


def no_dashes(s):
    s = s.replace("\u2014", ",").replace("\u2013", "-")
    return re.sub(r"\s+,", ",", s)


def clean_artist(s):
    s = strip_html(s)
    s = re.sub(r"\b(Unknown (author|artist))\s*\1", r"\1", s, flags=re.I)
    s = re.sub(r"^(Unknown author|Unknown artist|Unknown)$", "Auteur inconnu", s, flags=re.I)
    s = re.sub(r"^[\s\-]+|[\s\-]+$", "", s)
    if len(s) > 120:
        s = s[:117].rsplit(" ", 1)[0] + "..."
    return no_dashes(s)


def wikidata_p18(qid, index):
    d = api(WIKIDATA_API, action="wbgetentities", ids=qid, props="claims")
    claims = d["entities"][qid].get("claims", {}).get("P18", [])
    if not claims:
        return None
    claim = claims[min(index, len(claims) - 1)]
    return claim["mainsnak"]["datavalue"]["value"]


def commons_info(name, width, page=None):
    params = dict(action="query", titles="File:" + name, prop="imageinfo",
                  iiprop="url|extmetadata|mime", iiurlwidth=width)
    if page:
        params["iiurlparam"] = f"page{page}-{width}px"
    d = api(COMMONS_API, **params)
    pg = next(iter(d["query"]["pages"].values()))
    if "imageinfo" not in pg:
        return None
    return pg["title"], pg["imageinfo"][0]


def main():
    out, skipped = [], []
    for t in TARGETS:
        label = f"{t['section']} / {t['role']} / {t['file']}"
        print("->", label, flush=True)
        try:
            name = t.get("commons") or wikidata_p18(t["qid"], t.get("p18", 0))
            if not name:
                skipped.append((label, "pas d'image P18 sur Wikidata"))
                continue
            width = t.get("width", 480)
            res = commons_info(name, width, t.get("page"))
            if not res:
                skipped.append((label, "fichier introuvable sur Commons : " + name))
                continue
            title, ii = res
            meta = ii.get("extmetadata", {})
            lic = strip_html(meta.get("LicenseShortName", {}).get("value", ""))
            if not is_free(lic):
                skipped.append((label, f"licence non libre ou inconnue ({lic or 'vide'})"))
                continue
            thumb = ii.get("thumburl") or ii["url"]
            path_part = urllib.parse.urlparse(thumb).path.lower()
            ext = ".png" if path_part.endswith(".png") else ".jpg"
            rel = t["file"] + ext
            dest = os.path.join(ROOT, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            if not (os.path.exists(dest) and os.path.getsize(dest) > MIN_BYTES):
                data = http_get(thumb, binary=True)
                if len(data) <= MIN_BYTES:
                    skipped.append((label, f"image telechargee trop petite ({len(data)} octets)"))
                    continue
                with open(dest, "wb") as f:
                    f.write(data)
            artist = t.get("artist") or clean_artist(meta.get("Artist", {}).get("value", "")) \
                or clean_artist(meta.get("Credit", {}).get("value", "")) or "Auteur inconnu"
            source = ii.get("descriptionurl") or \
                "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
            entry = {
                "section": t["section"],
                "role": t["role"],
                "file": rel,
                "alt": no_dashes(t["alt"]),
                "caption": no_dashes(t["caption"]),
                "credit": no_dashes(f"{artist}, {lic}"),
                "license": lic,
                "source": source,
            }
            out.append(entry)
            print("   ok", rel, "|", entry["credit"], flush=True)
        except Exception as e:  # noqa: BLE001
            skipped.append((label, f"erreur : {e}"))
            print("   ERREUR", e, flush=True)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\n{len(out)} images ecrites dans {os.path.relpath(OUT_JSON, ROOT)}")
    if skipped:
        print("Cibles sautees :")
        for label, why in skipped:
            print("  -", label, ":", why)
    return 0


if __name__ == "__main__":
    sys.exit(main())
