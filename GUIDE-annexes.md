# Annexes : format et règles d'écriture

Les annexes de `annexes.html` sont des synthèses de lecture neutres, un article par fichier dans `build/annexes/`, traduites dans `i18n/<langue>/annexes/<id>.md` (titre, motifs, références et corps ; catégorie, ordre, sections et œuvres sont repris du français). `python3 build/build.py` signale les en-têtes incomplets, les catégories ou sections inconnues et les articles hors de 400 à 700 mots ; `python3 build/i18n_verif.py <langue>` contrôle les traductions. Le plan d'origine (mécanique du build, lots de rédaction) est dans l'historique git de ce fichier, sous son ancien nom `PLAN-annexes.md`.

## Format : `build/annexes/<id>.md`

Un fichier par article, nommé par son id (ASCII, minuscules, tirets ; c'est aussi l'ancre dans `annexes.html`). En-tête entre deux lignes `---`, puis le corps en Markdown.

```markdown
---
titre: De Constantin à Théodose : le christianisme religion de l'Empire
categorie: histoire
ordre: 20
sections: porphyre-et-augustin ; deuxieme-partie ; le-bilan-des-refondations
motifs: Constantin ; Théodose ; empereurs chrétiens ; édit de Milan
references: Peter Brown, *The Rise of Western Christendom* (1996) ; Paul Veyne, *Quand notre monde est devenu chrétien* (2007)
---
En 312, Constantin ... (400 à 700 mots : chapeau de deux phrases, contexte, trois à cinq idées, ce que l'essai suppose connu).

#### Les dates
- 313 : ...
```

- `titre` (obligatoire), `categorie` (obligatoire : `theories`, `bible`, `histoire`, `disciplines`, `courants`), `ordre` (facultatif, entier ; tri dans la catégorie, puis par titre), `sections` (ids de sections **ou de parties** d'`index.html`, séparés par ` ; ` ; c'est ce qui produit la ligne « Pour comprendre » et la ligne « Dans l'essai »), `motifs` (chaînes exactes à relier dans le texte, séparées par ` ; `, mêmes règles que le lexique : correspondance exacte, accents inclus, casse sensible si le motif commence par une majuscule ; un pluriel est un motif de plus), `references` (facultatif, séparées par ` ; `, rendues par `en_ligne`, donc `*italique*` accepté).
- Corps : paragraphes, listes `- `, tableaux `|`, citations `>`, `**gras**`, `*italique*`, et des sous-titres `#### `. Pas de backticks ni de crochets longs : `masquer_statuts` les retire.
- Liens vers l'essai, le lexique ou une autre annexe : inutiles à la main, le build les pose (lexique d'abord, puis motif le plus long) ; `[texte](#id)` reste possible pour une ancre interne à la page.

- Champ facultatif `oeuvres` : images de `images/art/`, rendues en vignettes « Dans la Galerie » et en lien « Annexe » sous l'œuvre dans `galerie.html`.
- Catégories : `bible` (ordre = rang × 10), `histoire`, `disciplines`, `courants`, `theories` (un article par auteur, deux pour les sections doubles).

## Règles d'écriture des annexes

- **Voix** : troisième personne, neutre, au présent. Aucun « je ». Aucun verdict sur la thèse de l'essai ; on peut écrire « l'essai mobilise cette notion dans… » (factuel), pas « l'essai a raison de… ».
- **Plan d'un article** (400 à 700 mots) : chapeau de deux phrases (qui, quand, quoi) ; contexte (d'où cela vient, contre quoi) ; la théorie ou la période en trois à cinq idées, avec des sous-titres `#### ` si l'article dépasse 500 mots ; un dernier paragraphe « Ce que l'essai suppose » qui nomme les faits et les termes que l'essai emploie sans les expliquer ; pour l'histoire, une liste de dates clés.
- **Sans citation** : aucun guillemet, sauf une formule déjà citée par l'essai, recopiée d'`index.html` (`grep`), jamais de mémoire. Les références de fin d'article donnent des titres et des dates, pas des pages.
- **Prudence factuelle** : dates et faits de culture générale établie ; en cas de doute, « vers », ou omettre. Les théories d'auteur sont présentées comme l'auteur les présente, pas comme l'essai les juge (c'est le sens de « de manière neutre » demandé pour Girard : la théorie mimétique dans son ensemble, du roman à l'économie, pas seulement son usage religieux).
- **Champ `sections`** : la section de l'auteur, plus les sections et parties où l'article aide vraiment (pas plus de quatre ou cinq cibles par article, sinon la ligne « Pour comprendre » devient un sommaire).
- **Champ `motifs`** : deux à six motifs précis, propres au sujet (`théorie mimétique`, `édit de Milan`, `concile de Nicée`), jamais le seul nom d'un auteur qui a sa section (il apparaît des centaines de fois ; la ligne « Pour comprendre » de sa section suffit).
- Pas de tiret cadratin ; pas de backticks ni de crochets longs ; titres d'œuvres en italique, en langue originale à la première mention puis titre français reçu.

## Inventaire d'origine

Format : `id` : titre ; sections cibles principales. Les ids sont les noms de fichiers. Environ 130 articles prévus ; les fichiers de `build/annexes/` font foi (156 au 17 octobre 2026, dont `revelations-recues` et `mystique-quantique`, ajoutées ce jour-là).

### Bible (catégorie `bible`, ajoutée le 17 octobre 2026, `ordre` = rang × 10)

Vingt-deux synthèses qui racontent et expliquent les textes bibliques que l'essai suppose connus, sans citation (pas même de verset) : `bible-canons-et-langues`, `genese-creation-et-chute`, `cain-deluge-et-babel`, `abraham-isaac-jacob`, `exode-moise-et-la-loi`, `juges-rois-david-salomon`, `prophetes-et-daniel`, `psaumes-job-et-sagesse`, `intertestamentaire-et-qumran`, `nouveau-testament-vue-d-ensemble`, `evangile-de-marc`, `evangiles-de-matthieu-et-de-luc`, `evangile-de-jean`, `passion-et-resurrection`, `royaume-paraboles-et-miracles`, `actes-des-apotres`, `lettres-de-paul`, `epitres-catholiques-et-hebreux`, `apocalypse-de-jean`, `evangiles-apocryphes`, `formation-du-canon`, `lectures-de-la-bible`. Chaque article distingue ce que le texte raconte de ce que l'histoire établit, et se termine par « Ce que l'essai suppose ». Motifs choisis pour exister dans l'essai (Genèse, Abraham, Isaïe, livre de Daniel, Job, Psaumes, Passion, Pilate, Évangile de Jean, lettre aux Romains…) ou pour pouvoir y apparaître ; les prénoms seuls (Jean, Marc, Luc, David, Thomas, Daniel, Salomon, Moïse) sont exclus parce qu'ils désignent aussi des auteurs modernes.

### Histoire (catégorie `histoire`, `ordre` croissant)

Lot 1 (dix articles) :
- `empire-romain-et-premiers-chretiens` (10) : Le christianisme dans l'Empire, de Néron à Dioclétien (statut, persécutions, Pline et Trajan, diffusion sociale et géographique) ; `deuxieme-partie`, `justin-martyr`, `celse-et-origene`.
- `constantin-et-theodose` (20) : De Constantin à Théodose (312, 313, 325, 380, 391-392 ; Julien) ; `porphyre-et-augustin`, `deuxieme-partie`, `le-bilan-des-refondations`.
- `pourquoi-le-christianisme-s-est-impose` (30) : Les explications des historiens (Gibbon, Harnack, Nock, Peter Brown, Veyne, Stark : réseaux urbains, charité, martyrs, universalisme, femmes, épidémies, conversion impériale) ; `deuxieme-partie`, `paul-de-tarse`, `norris-et-inglehart`.
- `conciles-et-formation-du-dogme` (40) : Nicée, Constantinople, Éphèse, Chalcédoine ; arianisme ; Trinité ; canon ; Pères de l'Église ; `celse-et-origene`, `porphyre-et-augustin`, `philon-d-alexandrie`.
- `chretiente-medievale` (50) : De la chute de Rome à la chrétienté (Clovis, monachisme, Charlemagne, réforme grégorienne, investitures, hérésies, Inquisition, croisades) ; `maitre-eckhart`, `dostoievski`, `premiere-partie`.
- `byzance-et-orthodoxie` (60) : Byzance, le schisme de 1054, Cyrille et Méthode, Russie de 988, Moscou troisième Rome, Raskol, synode de Pierre le Grand, startsy (Dostoïevski) ; `dostoievski`, `deuxieme-partie`.
- `scolastique-et-condamnations` (70) : Universités, Thomas d'Aquin, foi et raison, averroïsme latin, Tempier 1277, nominalisme et Ockham ; `averroes`, `maimonide`, `hans-blumenberg`, `passage`.
- `reforme-protestante` (80) : Luther 1517, Calvin, sola scriptura, imprimerie, Église d'Angleterre, anabaptistes, Contre-Réforme ; `weber`, `soren-kierkegaard`, `barth`, `bonhoeffer`.
- `guerres-de-religion-et-tolerance` (90) : Saint-Barthélemy, édit de Nantes et révocation (Bayle), Westphalie, Locke, libertins, Amsterdam de Spinoza ; `bayle`, `spinoza`, `troisieme-partie`.
- `lumieres-et-revolution` (100) : Absolutisme et droit divin, gallicanisme, jansénisme (Pascal), déchristianisation, Constitution civile du clergé, culte de l'Être suprême, Concordat ; `rousseau`, `voltaire`, `durkheim`, `quatrieme-partie`.

Lot 2 :
- `islam-naissance-et-pensee` (15) : Naissance et expansion, falsafa, mu'tazilites et clôture d'al-Qâdir, Ghazâlî, al-Andalus ; `averroes`, `l-islam-devant-la-sortie-de-la-religion`.
- `judaisme-du-second-temple-a-nos-jours` (12) : Pharisiens, Temple de 70, Talmud, Maïmonide, herem de Spinoza, Haskalah, hassidisme ; `philon-d-alexandrie`, `paul-de-tarse`, `maimonide`, `levinas`.
- `renaissance-humanisme-imprimerie` (75) : Gutenberg, Érasme, retour aux sources, Montaigne ; `montaigne`, `troisieme-partie`.
- `xixe-siecle-eglise-et-modernite` (110) : Syllabus, Vatican I, Kulturkampf, Tübingen et critique biblique, scandale Renan, Kulturprotestantismus ; `cinquieme-partie`, `ernest-renan`, `sixieme-partie`.
- `laicite-francaise` (120) : 1882, affaire Dreyfus, 1905, modèles européen et américain ; `marcel-gauchet`, `onzieme-partie`.
- `eglises-et-totalitarismes` (130) : Barmen, Église confessante, concordat de 1933, athéisme d'État soviétique, religions politiques ; `barth`, `bonhoeffer`, `voegelin-et-aron`, `carl-schmitt`.
- `vatican-ii-et-secularisation-europeenne` (140) : Vatican II, déclin de la pratique, 1979, retour du religieux, nouveaux athées 2004-2007 ; `onzieme-partie`, `douzieme-partie`, `les-athees-militants-contemporains`.

### Disciplines et méthodes (`disciplines`, lot 2)

`sociologie-de-la-religion` (Comte, Durkheim, Weber, Berger, Luckmann, Hervieu-Léger, théorie de la sécularisation, marché religieux) ; `psychologie-et-psychanalyse-de-la-religion` (James, Freud, Jung, Becker, TMT) ; `anthropologie-de-la-religion` (Tylor, Frazer, Malinowski, Durkheim, Girard) ; `sciences-cognitives-de-la-religion` (Boyer, Barrett, Guthrie, Dennett) ; `exegese-historico-critique-et-quetes-du-jesus-historique` (Reimarus, Strauss, Formgeschichte, Bultmann, trois quêtes, critères) ; `philosophie-analytique-de-la-religion` (Russell, Mackie, Plantinga, épistémologie réformée, problème du mal) ; `phenomenologie` (Husserl, Heidegger, Levinas, Marion) ; `hermeneutique` (Schleiermacher, Dilthey, Gadamer, Ricœur) ; `vocabulaire-de-la-theologie-chretienne` (révélation, grâce, incarnation, Trinité, péché originel, salut, théologie naturelle et révélée, apophatique) ; `metaphysique-et-preuves-de-l-existence-de-dieu` (être et étant, substance, causa sui, preuves ontologique, cosmologique, physico-théologique, critique de Kant) ; `philosophie-de-l-histoire` (Augustin, Bossuet, Vico, Hegel, Marx, progrès, Löwith).

### Courants et doctrines (`courants`, lot 8)

`platonisme-et-neoplatonisme` ; `ecoles-hellenistiques` (stoïcisme, épicurisme, scepticisme, la sagesse comme manière de vivre) ; `gnose-et-gnosticisme` (Jonas, Voegelin, Blumenberg) ; `mystique-chretienne` (Denys, Eckhart, Jean de la Croix, quiétisme) ; `pietisme-et-romantisme-allemand` ; `idealisme-allemand` (Kant, Fichte, Schelling, Hegel) ; `jeunes-hegeliens` ; `positivisme-et-scientisme` ; `existentialisme` ; `marxisme-et-religion` (Lénine, Bloch, Gramsci, théologie de la libération) ; `theologie-du-xxe-siecle` (dialectique, Bultmann, Tillich, Ratzinger) ; `bouddhisme-reperes` (Quatre nobles vérités, karma, écoles, réception européenne) ; `nouveaux-athees` ; `spiritualites-contemporaines` (New Age, méditation, « spirituel mais pas religieux »).

### Théories des auteurs (`theories`, lots 3 à 7 ; un article par auteur, deux pour les sections doubles)

Première à troisième partie (lot 3) : `platon-theorie` (Idées, âme, cité, Bien), `aristote-theorie` (acte et puissance, causes, moteur immobile, vertu, contemplation), `epicure-theorie` (atomisme, canonique, tétrapharmakos), `lucrece-theorie`, `plotin-theorie` (hypostases, procession, conversion), `averroes-theorie` (commentateur, intellect, Tahâfut, averroïsme), `maimonide-theorie` (Guide, Mishné Torah, prophétie), `eckhart-theorie` (détachement, naissance de Dieu dans l'âme, procès), `philon-theorie`, `paul-theorie` (lettres, justification, Loi, nouvelle perspective), `justin-et-apologistes`, `celse-theorie`, `origene-theorie` (allégorie, apocatastase), `porphyre-theorie`, `augustin-theorie` (Confessions, Cité de Dieu, grâce, péché originel, donatisme, pélagianisme), `montaigne-theorie`, `descartes-theorie`, `pascal-theorie` (trois ordres, pari, jansénisme), `spinoza-theorie` (substance, attributs, modes, conatus, genres de connaissance, TTP), `bayle-theorie`, `leibniz-theorie` (monades, harmonie, raison suffisante).

Quatrième à sixième partie (lot 4) : `hume-theorie` (empirisme, causalité, miracles), `voltaire-theorie`, `rousseau-theorie` (état de nature, contrat, volonté générale, Émile), `holbach-theorie`, `kant-theorie` (trois Critiques, impératif, postulats, Religion), `schleiermacher-theorie`, `hegel-theorie` (dialectique, Phénoménologie, Esprit absolu), `strauss-theorie`, `bauer-theorie`, `renan-theorie`, `feuerbach-theorie`, `stirner-theorie`, `marx-theorie` (matérialisme historique, aliénation, idéologie, fétichisme), `engels-theorie`, `kierkegaard-theorie` (stades, angoisse, désespoir, Abraham), `comte-theorie` (trois états, sociologie, religion de l'Humanité), `schopenhauer-theorie`.

Septième et huitième partie (lot 5) : `dostoievski-oeuvre` (Karamazov : structure, personnages ; Démons ; polyphonie), `nietzsche-theorie` (tragédie, généalogie, maître et esclave, volonté de puissance, éternel retour, surhomme), `durkheim-theorie`, `weber-theorie` (types idéaux, rationalisation, charisme, neutralité axiologique), `james-theorie` (pragmatisme), `otto-theorie`, `freud-theorie` (inconscient, Œdipe, Totem et tabou, Moïse), `bergson-theorie` (durée, intuition, élan vital), `ricoeur-theorie`.

Neuvième et dixième partie (lot 6) : `tylor-et-frazer-theorie`, `malinowski-theorie` (fonctionnalisme), `jung-theorie` (archétypes, inconscient collectif, individuation), `theorie-mimetique` (lot 1, pilote : désir, rivalité, crise, bouc émissaire, sacrifice, révélation ; applications au roman, à l'économie, à la politique), `becker-theorie`, `berger-et-luckmann-theorie` (construction sociale de la réalité), `hervieu-leger-theorie`, `boyer-theorie`, `norris-et-inglehart-theorie` (World Values Survey), `heidegger-theorie` (Dasein, Être et temps, tournant, technique, 1933), `wittgenstein-theorie` (Tractatus, Investigations, jeux de langage), `barth-theorie`, `bonhoeffer-theorie`, `weil-theorie` (attention, malheur, Enracinement), `bataille-theorie` (dépense, part maudite, souveraineté, Collège de sociologie), `sartre-theorie` (en-soi, pour-soi, liberté, mauvaise foi, engagement), `camus-theorie` (absurde, révolte, cycles), `levinas-theorie` (autrui, visage, éthique première, Talmud), `marion-theorie` (donation, phénomène saturé).

Onzième et douzième partie (lot 7) : `schmitt-theorie` (décisionnisme, ami et ennemi), `lowith-theorie`, `blumenberg-theorie` (métaphorologie, Arbeit am Mythos), `voegelin-theorie`, `aron-theorie`, `strauss-leo-theorie` (droit naturel, ésotérisme), `gauchet-theorie`, `taylor-theorie` (Sources of the Self), `habermas-theorie` (agir communicationnel, sphère publique), `hadot-theorie`, `foucault-theorie` (archéologie, pouvoir, souci de soi, parrêsia), `jaspers-theorie` (psychopathologie, existence, période axiale), `murdoch-theorie` (romans, Bien, attention), `comte-sponville-theorie`, `ferry-theorie`, `arkoun-theorie`, `bidar-theorie`, `onfray-theorie` (Contre-histoire, Traité, Décadence, Théorie de Jésus).
