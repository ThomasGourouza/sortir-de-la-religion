# Plan : encadrés littéraires (« En littérature ») dans l'essai

## Contexte

L'essai *Sortir de la religion sans en fonder une autre ?* illustre déjà ses idées par des tableaux (figures insérées par `build/build.py` à partir de `build/images.json`). L'auteur veut faire de même avec la littérature classique : pour chaque section d'auteur, chaque débat construit et chaque section de conclusion, un encadré distinct du texte de fond, que le lecteur peut ignorer, qui cite une ou plusieurs œuvres littéraires (extrait court ou résumé de scène, explication du lien avec la thèse de la section, auteur et œuvre en fin d'encadré). But affiché : convoquer le plus d'auteurs classiques possible en restant pertinent, sans ajouter de contenu théorique.

Décisions prises avec l'utilisateur (14 octobre 2026) :
- Forme : encadré **replié par défaut**, dont la ligne de titre reste visible (« En littérature : Victor Hugo, *Quatrevingt-treize* (1874) »).
- Périmètre : sections d'auteurs de toutes les parties + les cinq débats construits + les trois sections de la conclusion (environ 90 encadrés). Pas le prologue, pas les passages, pas les bilans.
- Contenu : extraits courts quand le texte est sûr (domaine public surtout), résumés de scène sinon ; un statut « à vérifier » dans le JSON pour les citations non contrôlées, jamais affiché.
- Une page outil « Bibliothèque » listant toutes les œuvres citées, faite après les encadrés.

Contraintes permanentes : jamais de tiret cadratin ni de demi-cadratin ; pas de commit sans demande ; la source Markdown de l'essai (`~/Documents/litterature`) n'est pas sur cette machine, donc `index.html` ne peut pas être régénéré ici : il faut un mode d'injection directe dans le HTML existant, idempotent, que le prochain vrai build rendra inutile.

## Principe technique

Un fichier de données, une fonction d'injection, un style. Le texte de l'essai (Markdown) n'est pas touché.

### 1. `build/litterature.json` (nouveau)

Liste d'objets, un par encadré :

```json
{
  "section": "rousseau",
  "auteur": "Victor Hugo",
  "oeuvre": "Quatrevingt-treize",
  "date": "1874",
  "lieu": "troisième partie, livre VII, « Les deux pôles du vrai »",
  "apres": "je ne connais pas de texte qui illustre plus exactement mon critère",
  "corps": [
    "Cimourdain, l'ancien prêtre devenu délégué du Comité de salut public, ...",
    "« ... » (citation courte)",
    "Pourquoi ici : Cimourdain est la religion civile de Rousseau faite homme ..."
  ],
  "statut": "résumé"
}
```

- `section` : id de la section (mêmes ids que `reponses.json`, `lexique.json`). Plusieurs objets peuvent viser la même section (une œuvre par objet, ou deux œuvres dans un même objet : préférer un encadré par section regroupant une à trois œuvres, chaque œuvre avec son propre paragraphe et sa source en fin de paragraphe).
- `apres` (facultatif) : fragment de texte brut (sans balises) du paragraphe après lequel insérer ; absent = fin de section (avant les crédits de portrait).
- `corps` : paragraphes en Markdown léger (gras, italique), rendus par `en_ligne()` (`build/build.py:60`). Dernier paragraphe = explication du lien ; la source est rendue à part à partir de `auteur`, `oeuvre`, `date`, `lieu`.
- `statut` : `citation` (texte contrôlé), `résumé` (pas de citation littérale), `à vérifier` (citation de mémoire à collationner). Non affiché.

### 2. `build/build.py`

- `charger("litterature.json", [])` (fonction existante `charger`, ligne 258) ; indexer par section ; avertir sur les ids inconnus comme pour `reponses.json` / `lexique.json`.
- Nouvelle fonction `encadre_lettres(e)` qui rend :
  `<aside class="lettres"><details><summary><span class="lettres-label">En littérature</span> <span class="lettres-titre">Victor Hugo, <em>Quatrevingt-treize</em> (1874)</span></summary><div class="lettres-corps"><p>…</p><p class="lettres-source">Victor Hugo, <em>Quatrevingt-treize</em>, troisième partie, livre VII (1874).</p></div></details></aside>`
- Nouvelle fonction `inserer_lettres(corps_sec, encadres)` sur le modèle de `inserer_figures` (ligne 245) : après le bloc dont le texte brut contient `apres`, sinon en fin de liste. Appelée dans la boucle des sections juste après `inserer_figures` (ligne ~509), donc **après** le comptage des mots (`smots`) : les encadrés n'entrent pas dans les temps de lecture.
- `lier_lexique` (ligne 267) : ajouter `"aside"` à la liste des balises bloquantes pour que les encadrés ne volent pas la première occurrence d'un terme du lexique.
- Mode d'injection directe : `python3 build/build.py --lettres` lit `index.html`, retire les lignes commençant par `<aside class="lettres">`, puis pour chaque section (ligne `<details class="section… id="X"`) insère chaque encadré sur sa propre ligne après la ligne contenant `apres`, sinon avant la première ligne suivante contenant `</div></details>` (fermeture de la section ; les paragraphes n'en contiennent pas). Idempotent. C'est ce mode qui sera utilisé sur cette machine ; le vrai build sur la machine de l'auteur produira le même résultat.
- Page « Bibliothèque » (`bibliotheque.html`) : dans `pages_outils`, sur le modèle de la page lexique (`page_outil`, ligne ~329) : liste triée par auteur puis œuvre, avec date et lien(s) vers les sections ; ajouter l'entrée à la navigation des pages outils, au `drawer-outils` de `build/template.html`, au `hero-outils`, et au `SHELL` de `build/sw.template.js`. Faite en dernier.

### 3. `css/style.css`

```css
.lettres { margin: 1.2em 0; font-size: .94em; }
.lettres > details { border: 1px solid var(--line); border-left: 4px solid var(--accent); border-radius: 12px; background: var(--bg-soft); }
.lettres summary { padding: 8px 12px; cursor: pointer; font: 600 14px var(--sans); }
.lettres-label { color: var(--accent); text-transform: uppercase; letter-spacing: .04em; font-size: 11.5px; margin-right: 6px; }
.lettres-corps { padding: 4px 14px 8px; }
.lettres-source { font: 12.5px var(--sans); color: var(--ink-soft); text-align: right !important; margin: .2em 0 .6em; }
```

Pas de JS : `details` natif ; `reveal()` (`js/app.js:39`) ouvre déjà tous les `details` ancêtres d'une cible, donc une recherche plein texte qui tombe dans un encadré l'ouvre.

### 4. Fichiers générés sur cette machine

`index.html` (injection directe), puis `sw.js` et les pages : relever l'horodatage `?v=` dans `index.html`, `frise.html`, `reponses.html`, `lexique.html`, `sw.js` (et `bibliotheque.html` quand elle existe) pour que CSS et pages se rechargent. `CLAUDE.md` (mécanique du site, fichiers éditables) et `README.md` : une phrase chacun.

## Règles d'écriture des encadrés

- Longueur : 120 à 220 mots par encadré, une à trois œuvres. Jamais de théorie nouvelle : l'explication renvoie aux termes de la section (critère du sacrifice, refondation stricte ou douce, exception, régime de l'erreur, etc.).
- Structure de chaque œuvre : une phrase qui situe la scène ; l'extrait (quatre lignes au plus) ou le résumé ; une ou deux phrases « pourquoi ici » ; la source (auteur, œuvre, lieu, date).
- Citations : seulement des passages dont je suis sûr mot à mot ; sinon résumé explicite (« je résume »). Les œuvres sous droits (Céline, Hesse, Saint-Exupéry en France, Camus romans, Malraux, Koestler, Orwell, Grossman, Levi, O'Connor, Waugh, Mahfouz, Beckett, Kerouac, Lampedusa, Kazantzakis, Bulgakov, Steinbeck, Hemingway, Golding, Jackson, Celan, Char, Giono, Bernanos, Greene, Unamuno, Pirandello, Musil, Mann, Kafka selon éditions) : résumé de scène et au plus une phrase citée.
- Œuvres étrangères : titre original entre parenthèses à la première mention ; extrait en français (traduction courante ou la mienne, signalée « je traduis »), vers très célèbres aussi en langue originale.
- Pas de doublon d'œuvre entre sections sauf si la scène diffère (Les Misérables, La Peste, Zauberberg peuvent revenir avec des scènes différentes, deux fois au plus).
- Chaque encadré nomme explicitement l'auteur et l'œuvre dans sa ligne de titre : c'est ce que voit le lecteur qui n'ouvre pas.
- Ne pas employer de tiret cadratin ni de demi-cadratin.

## Déroulement (par lots, pour tenir dans les limites de sortie)

1. Technique d'abord, avec deux encadrés d'essai (Rousseau, Malinowski) : JSON, `build.py` (rendu, insertion, mode `--lettres`, `aside` dans `lier_lexique`), CSS, injection dans `index.html`, contrôle visuel desktop et mobile (serveur local + Playwright comme pour les changements précédents).
2. Rédaction par partie, dans l'ordre de l'essai, en relisant chaque section dans le texte extrait (`scratchpad/essai/NN-*.txt`, toujours présent ; sinon la recette grep/sed de CLAUDE.md sur `index.html`) avant d'écrire son encadré : première à quatrième partie ; cinquième à septième ; huitième et neuvième ; dixième et onzième ; douzième et conclusion. Après chaque lot : `python3 build/build.py --lettres`, vérification des ids inconnus, relecture du rendu d'une section du lot.
3. Page « Bibliothèque », navigation, service worker, horodatage, README, CLAUDE.md.
4. Bilan final : nombre d'encadrés, d'auteurs et d'œuvres ; liste des citations marquées « à vérifier » remise à l'auteur.

## Vérification

- `python3 -m py_compile build/build.py` ; build d'essai sur un article synthétique dans le scratchpad (comme fait pour la suppression de l'abrégé) pour vérifier que le vrai build insère les encadrés et génère `bibliotheque.html`.
- `python3 build/build.py --lettres` deux fois de suite : `index.html` identique (idempotence), aucun id inconnu signalé.
- Dans le navigateur (1440 px et 390 px) : encadré replié lisible, ouverture au toucher, pas de débordement, thème sombre correct ; la recherche plein texte d'un mot propre à un encadré ouvre la section et l'encadré ; les temps de lecture inchangés ; le lexique garde ses premières occurrences dans le texte de fond.
- Contrôle de l'absence des tirets typographiques interdits (U+2014 et U+2013) sur le JSON, le CSS, le script, README et CLAUDE.md.

## Annexe : correspondances envisagées, section par section

Candidats retenus après lecture de l'essai ; la relecture de chaque section au moment de l'écriture peut en remplacer un. Format : id de section : œuvre(s) ; scène ; lien avec la section.

### Première partie
- `platon` : Aristophane, *Les Nuées* (Socrate accusé d'impiété par la comédie, l'incendie du pensoir : la cité qui punit l'impie, ancêtre du sôphronistêrion) ; Saint-Exupéry, *Citadelle* (le chef qui fonde le sens par la contrainte et la cérémonie : le législateur) ; en second plan Orwell, *1984* (O'Brien et la police de la pensée, pour la version moderne de Lois X).
- `aristote` : Dante, *Paradiso* XXXIII, « l'amor che move il sole e l'altre stelle » (le moteur qui meut comme ce qui est aimé, devenu Dieu des chrétiens) ; Dante, *Inferno* IV (les limbes, Aristote « maestro di color che sanno » : le philosophe honoré et exclu).
- `epicure-et-lucrece` : Leopardi, *La Ginestra* et *A se stesso* (la nature indifférente, la consolation refusée) ; Yourcenar, *Mémoires d'Hadrien* (l'empereur épicurien devant les dieux, « animula vagula blandula »).
- `plotin` : Jean de la Croix, *Noche oscura* (l'union, « amada en el amado transformada ») ; Hesse, *Siddhartha* (l'écoute du fleuve, l'unité : la mystique sans Église) ; Novalis, *Hymnes à la nuit* en appoint.
- `averroes` : Borges, « La busca de Averroes » (*El Aleph*, 1949 : Averroès cherchant le sens de « tragédie » et « comédie » sans avoir vu de théâtre : la limite de la traduction) ; Umberto Eco, *Le Nom de la rose* (Jorge et le second livre de la *Poétique* : le savoir interdit au vulgaire).
- `maimonide` : Kafka, « Devant la loi » (*Le Procès* : la porte faite pour un seul, la Loi à deux publics) ; Isaac Bashevis Singer, « Le Spinoza de la rue du Marché » gardé pour Spinoza ; pour Maïmonide, Singer, *Le Magicien de Lublin* (Yasha et le Dieu dont on ne sait rien) en option.
- `maitre-eckhart` : Angelus Silesius, *Le Pèlerin chérubinique* (« Die Ros' ist ohn' Warum » ; « Ich weiß, dass ohne mich Gott nicht ein Nu kann leben ») ; Rilke, *Le Livre d'heures* (« Was wirst du tun, Gott, wenn ich sterbe? ») ; Musil, *L'Homme sans qualités* (« l'autre état », mystique sans Dieu) en appoint.

### Deuxième partie
- `philon-d-alexandrie` : Thomas Mann, *Joseph et ses frères* (« Tief ist der Brunnen der Vergangenheit » ; la Genèse relue en roman, l'allégorie comme traduction du mythe).
- `paul-de-tarse` : Kazantzakis, *La Dernière Tentation* (Paul annonçant au Jésus vieilli qu'il prêchera le Christ crucifié qu'il faut : la thèse de Nietzsche en scène) ; Racine, *Athalie* ou Claudel en réserve.
- `justin-martyr` : Corneille, *Polyeucte* (le martyr qui brise les idoles et cherche la mort : l'offrande de soi, et la question de qui exige le sacrifice) ; Sienkiewicz, *Quo vadis* (Pétrone devant les chrétiens).
- `celse-et-origene` : Yourcenar, *Mémoires d'Hadrien* (le regard romain sur la secte), ou Flaubert, *La Tentation de saint Antoine* (le défilé des hérésies, Hilarion comme science) ; Anatole France, *Sur la pierre blanche* (Gallion devant Paul : la philosophie qui ne voit pas passer le christianisme).
- `porphyre-et-augustin` : Ibsen, *Empereur et Galiléen* (Julien, la refondation païenne) ; Proust, *Le Temps retrouvé* (la vraie vie au-dedans : l'intériorité augustinienne devenue mémoire involontaire, « interior intimo meo ») ; Pétrarque, *Secretum* en appoint.
- `jesus-a-t-il-existe-le-jesus-de-l-histoire-et-la-these-mythiste` : Boulgakov, *Le Maître et Marguerite* (Berlioz et Woland sur l'existence de Jésus, chapitre 1 ; Pilate) ; Anatole France, « Le Procurateur de Judée » (Pilate qui ne se souvient pas de Jésus).

### Troisième partie
- `montaigne` : Shakespeare, *Hamlet* (« there is nothing either good or bad but thinking makes it so » ; le doute) et *La Tempête* (Gonzalo recopie « Des Cannibales ») ; Cervantès, *Don Quichotte* (la coutume et la fable qu'on prend pour vraie).
- `descartes` : Valéry, *Monsieur Teste* (l'intellect pur, « la bêtise n'est pas mon fort ») ; Poe, « Eurêka » en option.
- `pascal` : Baudelaire, « Le Gouffre » (« Pascal avait son gouffre, avec lui se mouvant ») ; Racine, *Phèdre* (la grâce absente, le Dieu caché de Port-Royal) ; Bernanos, *Journal d'un curé de campagne* en réserve pour Barth.
- `spinoza` : Singer, « Le Spinoza de la rue du Marché » (le docteur Fischelson, l'*Éthique* et le mariage avec Dobbe : la béatitude et la vie) ; Goethe, *Poésie et vérité*, livre XIV (Spinoza lu comme libération) ; Borges, « Spinoza » (sonnet, « alguien construye a Dios en la penumbra »).
- `bayle` : Montesquieu, *Lettres persanes* (les Troglodytes, lettres XI-XIV : vertu sans religion ; « Comment peut-on être Persan ? ») ; Swift, *Gulliver* (la guerre des Gros-Boutiens et Petits-Boutiens : les guerres de religion ramenées à un œuf).
- `leibniz` : Pope, *Essay on Man* (« Whatever is, is right », cible du *Poème sur le désastre de Lisbonne*) ; Melville, *Moby-Dick* (Achab contre le mal du monde ; le sermon du père Mapple sur Jonas) ; Kleist, *Michael Kohlhaas* en option.

### Quatrième partie
- `hume` : Sterne, *Tristram Shandy* (le scepticisme joueur, la digression comme suspension) ; Diderot, *Jacques le fataliste* (« tout ce qui nous arrive de bien et de mal ici-bas était écrit là-haut » : le destin sans Dieu).
- `voltaire` : Unamuno, *San Manuel Bueno, mártir* (le curé qui a perdu la foi et la garde pour son village : « Si Dieu n'existait pas, il faudrait l'inventer » vécu) ; Stendhal, *Le Rouge et le Noir* (le séminaire, la religion comme carrière).
- `rousseau` : Hugo, *Quatrevingt-treize* (Cimourdain, « la république de l'absolu », qui condamne Gauvain et se tue : la religion civile faite homme) ; Anatole France, *Les dieux ont soif* (Évariste Gamelin, la fête de l'Être suprême).
- `d-holbach` : Shelley, *Queen Mab* et « Hymn to Intellectual Beauty » (l'athéisme qui prie la Nature) ; Diderot, *Le Rêve de d'Alembert* (la matière sensible) en appoint.
- `kant` : Kleist, *Michael Kohlhaas* (la justice érigée en absolu qui exige tout) et la lettre de la « crise kantienne » (mars 1801) ; Schiller, « Die Götter Griechenlands » en appoint.
- `un-debat-construit` (la morale sans Dieu) : Diderot, *Entretien d'un philosophe avec la maréchale de \*\*\** (la morale de l'athée, le pari renversé) ; Lessing, *Nathan le Sage* (la parabole des trois anneaux, d'après Boccace, *Décaméron* I, 3).

### Cinquième partie
- `friedrich-schleiermacher` : Hölderlin, *Hyperion* (« Eins zu sein mit allem, was lebt ») ; Wordsworth, « Tintern Abbey » (« a sense sublime / Of something far more deeply interfused ») ; Lamartine, *Méditations* en appoint.
- `georg-wilhelm-friedrich-hegel` : Jean Paul, *Siebenkäs*, « Discours du Christ mort » (le Christ annonçant qu'il n'y a pas de Dieu : la mort de Dieu avant Hegel, traduit par Mme de Staël) ; Nerval, « Le Christ aux Oliviers » (« Dieu n'est pas ! Dieu n'est plus ! ») partagé avec Nietzsche selon la place.
- `david-friedrich-strauss-et-bruno-bauer` : George Eliot, *Middlemarch* (Casaubon et sa « Clé de toutes les mythologies » ; la traductrice de Strauss) ; Flaubert, *Bouvard et Pécuchet* gardé pour Comte.
- `ernest-renan` : Proust, *Pastiches et mélanges* (le pastiche de Renan, « L'Affaire Lemoine ») ; Anatole France, *Le Jardin d'Épicure* ou Loti en appoint ; Dostoïevski déjà présent.

### Sixième partie
- `ludwig-feuerbach` : Steinbeck, *Les Raisins de la colère* (Jim Casy, l'ex-prédicateur : « peut-être que c'est tous les hommes et toutes les femmes qu'on aime ; peut-être que c'est ça, le Saint-Esprit » : la religion de l'amour humain) ; George Eliot, *Adam Bede* (Dinah Morris, la traductrice de Feuerbach) ; Rilke, *Le Livre d'heures* si non pris par Eckhart.
- `max-stirner` : Flannery O'Connor, *La Sagesse dans le sang* (Hazel Motes et l'« Église sans Christ » : l'athée pieux qui refonde) ; Ibsen, *Peer Gynt* (le « moi gyntien ») ; Tourgueniev, *Pères et fils* (Bazarov).
- `karl-marx-et-friedrich-engels` : Zola, *Germinal* (la grève comme religion nouvelle, Souvarine, le « rêve » d'Étienne) ; Brecht, *Sainte Jeanne des abattoirs* (Jeanne Dark découvre que la charité est l'opium) ; Silone, *Le Pain et le vin* (Pietro Spina déguisé en prêtre : le socialisme comme religion) ou pour Aron.
- `soren-kierkegaard` : Ibsen, *Brand* (« tout ou rien » ; le pasteur qui sacrifie femme et enfant à l'absolu : le critère vu de l'intérieur de la foi) ; Kafka, *Journal* et *Lettre au père* sur Abraham en appoint.
- `auguste-comte` : Flaubert, *Bouvard et Pécuchet* (ils essaient la religion, puis la quittent ; le catéchisme) ; George Eliot, « O may I join the choir invisible » (la religion de l'Humanité en vers).
- `arthur-schopenhauer` : Thomas Mann, *Les Buddenbrook* (Thomas lisant « De la mort » : l'ivresse métaphysique d'un soir, puis l'oubli) ; Maupassant, « Auprès d'un mort » (la veillée du philosophe) ; Tolstoï, *Confession* gardé pour James.

### Septième partie
- `dostoievski` : Melville, *Billy Budd* (le capitaine Vere condamne l'innocent pour l'ordre du navire : la logique de l'Inquisiteur) ; Unamuno gardé pour Voltaire ; Hugo, *Les Misérables* (l'évêque et le conventionnel G. : deux absolus qui se saluent) en option.
- `nietzsche` : Nerval, « Le Christ aux Oliviers » (1844, la mort de Dieu en sonnets) ; Gide, *L'Immoraliste* (Michel, la liberté qui ne sait qu'en faire) ; Thomas Mann, *Le Docteur Faustus* (Leverkühn, Nietzsche en musicien) ; Hesse, *Demian* gardé pour Jung.

### Huitième partie
- `durkheim` : Zola, *Lourdes* (la foule, l'effervescence, le miracle collectif) ; Anatole France, *Les dieux ont soif* si non pris par Rousseau (la fête révolutionnaire comme culte).
- `weber` : Kafka, *Le Château* et *Le Procès* (l'habitacle d'acier, la bureaucratie comme destin sans visage) ; Defoe, *Robinson Crusoé* (l'ascèse intramondaine du puritain qui tient ses comptes).
- `william-james` : Tolstoï, *Confession* (le « twice-born » que James cite) ; Whitman, *Song of Myself* (le « once-born », la religion de la santé) ; Bunyan, *Le Voyage du pèlerin* en appoint.
- `rudolf-otto` : Rilke, *Élégies de Duino*, I (« Ein jeder Engel ist schrecklich » : le tremendum) ; Blake, « The Tyger » (« Did he who made the Lamb make thee? ») ; Melville, *Moby-Dick*, « La blancheur de la baleine » si non pris.
- `freud` : Kafka, *Lettre au père* (le père comme Dieu, « ta vision du monde… ») ; Zweig ou Schnitzler en appoint.
- `bergson` : Proust, *À la recherche du temps perdu* (la madeleine, la durée retrouvée) ; Péguy, *Le Porche du mystère de la deuxième vertu* (l'espérance, l'élan).
- `ricoeur` : Saint-Exupéry, *Le Petit Prince* (le renard : les rites, « l'essentiel est invisible pour les yeux » : la seconde naïveté, le symbole qui donne à penser) ; Claudel, *Cinq grandes odes* en appoint.

### Neuvième partie
- `tylor-et-frazer` : T. S. Eliot, *La Terre vaine* (bâtie sur *Le Rameau d'or*) ; Conrad, *Au cœur des ténèbres* (Kurtz adoré comme un dieu, « rites innommables »).
- `malinowski` : Hemingway, *Le Vieil Homme et la Mer* (Santiago : « je ne suis pas religieux, mais je dirai dix Notre Père… pour attraper ce poisson » : la magie là où règne l'incertitude) ; Conrad, *Lord Jim* (le Patna) gardé pour Clifford.
- `jung` : Hesse, *Demian* (Abraxas, « l'oiseau se bat pour sortir de l'œuf » ; Hesse analysé par un jungien) ; Melville, *Moby-Dick* (Achab et Job, pour *Réponse à Job*).
- `girard` : Euripide, *Les Bacchantes* (Penthée dépecé par la foule : Dionysos contre le Crucifié) ; Golding, *Sa Majesté des Mouches* (Simon tué par la ronde) ; Shirley Jackson, « La Loterie » (1948) ; Flaubert, *Salammbô* (Moloch) en appoint.
- `becker` : Tolstoï, *La Mort d'Ivan Ilitch* (le déni de la mort, « Caïus est mortel ») ; Ibsen, *Le Canard sauvage* (le « mensonge vital », Relling).
- `berger-et-luckmann` : Cervantès, *Don Quichotte* (la mort de Quichotte quand la canopée chevaleresque s'effondre : « Je fus fou, et je suis sage ») ; Pirandello, *Chacun sa vérité* (la réalité comme construction).
- `hervieu-leger` : Lampedusa, *Le Guépard* (la fin d'une lignée, le père Pirrone) ; Proust, *Du côté de chez Swann* (l'église de Combray, la mémoire d'une lignée).
- `boyer` : Flaubert, « Un cœur simple » (Félicité et le perroquet devenu Saint-Esprit : l'inférence qui fabrique un dieu) ; Ovide, *Métamorphoses* (un monde plein d'agents) ; Lewis Carroll (la Reine blanche et ses six choses impossibles) en appoint.
- `norris-et-inglehart` : Hamsun, *La Faim* (l'affamé qui crie vers Dieu) ; Hugo, *Les Misérables* (Fantine : la misère qui fait et défait la croyance) ; Dickens en appoint.
- `pourquoi-croit-on-un-debat-construit` : Flaubert, *Madame Bovary* (la dévotion d'Emma après Rodolphe : la religion comme réponse au manque, II, 14).
- `a-t-on-le-droit-de-croire-clifford-james-et-la-philosophie-analytique` : Ibsen, *Les Soutiens de la société* (Bernick laisse partir l'« Indian Girl » pourri : l'armateur de Clifford au théâtre) ; Conrad, *Lord Jim* (le Patna et ses pèlerins).

### Dixième partie
- `heidegger` : Hölderlin, « Patmos » (« Wo aber Gefahr ist, wächst / Das Rettende auch ») ; Celan, « Todtnauberg » (1967, la parole attendue qui ne vint pas : 1933 et le silence).
- `wittgenstein` : Tolstoï, « Ce qui fait vivre les hommes » et l'*Évangile abrégé* ; Tagore, *Le Roi de la chambre sombre* (lu au Cercle de Vienne) ; Trakl (le ton qu'on ne comprend pas et qui rend heureux).
- `barth` : Bernanos, *Journal d'un curé de campagne* (« Tout est grâce » ; la religion comme affaire de l'homme, la foi reçue) ; Kafka, *Le Procès* (le jugement sans accès) en appoint.
- `bonhoeffer` : Camus, *La Peste* (les deux sermons de Paneloux, la mort de l'enfant : « tout croire ou tout nier ») ; Graham Greene, *La Puissance et la Gloire* (le prêtre faible, Dieu impuissant dans le monde).
- `simone-weil` : Homère, *Iliade*, XXIV (Priam aux pieds d'Achille, « L'Iliade ou le poème de la force ») ; Sophocle, *Antigone* (Weil l'expliquait aux ouvriers) ; Primo Levi, *Si c'est un homme* (la prière de Kuhn que Levi cracherait : la consolation refusée) ou pour la conclusion.
- `bataille` : Baudelaire, « Les Litanies de Satan » ; Huysmans, *Là-bas* (la transgression comme sacré) ; Sade en appoint.
- `sartre` : Sartre, *Les Mouches* (Oreste : « les hommes d'Argos sont mes hommes ») et *Le Diable et le bon Dieu* (Goetz : « Dieu n'existe pas… il n'y a que les hommes ») ; Malraux gardé pour Camus.
- `camus` : Camus, *L'Étranger* (Meursault et l'aumônier, « la tendre indifférence du monde ») ; Malraux, *La Condition humaine* (Katow donne son cyanure : l'offrande de soi, le « nous ») ; Saint-Exupéry, *Terre des hommes* (Guillaumet : « ce que j'ai fait, aucune bête ne l'aurait fait ») ; René Char, *Feuillets d'Hypnos* en appoint.
- `levinas` : Vassili Grossman, *Vie et destin* (le cahier d'Ikonnikov, « la petite bonté » sans Dieu ni doctrine, que Levinas commentait) ; Dostoïevski, Markel déjà cité.
- `marion` : Dostoïevski, *L'Idiot* (le Christ mort de Holbein, l'image qui fait perdre la foi : idole ou icône) ; Dante, *Paradiso* XXXIII (voir sans dire) en appoint.

### Onzième partie
- `carl-schmitt` : Thomas Mann, *La Montagne magique* (Naphta : la terreur au service de l'absolu, contre Settembrini) ; Shakespeare, *Richard II* (« Not all the water in the rough rude sea / Can wash the balm off from an anointed king » : la théologie du souverain) ; Büchner, *La Mort de Danton* en appoint.
- `karl-lowith` : Tolstoï, *Guerre et Paix*, épilogue (l'histoire sans providence ni grands hommes) ; Flaubert, *L'Éducation sentimentale* (1848 comme farce, la fin des espérances).
- `hans-blumenberg` : Goethe, « Prometheus » (« Hier sitz ich, forme Menschen / Nach meinem Bilde » : l'affirmation de soi) ; Mary Shelley, *Frankenstein, ou le Prométhée moderne*.
- `voegelin-et-aron` : Koestler, *Le Zéro et l'Infini* (Roubachof, le Parti comme Église, Gletkin) ; Orwell, *1984* (O'Brien : « Dieu, c'est le pouvoir ») ; Silone, *Le Pain et le vin* si non pris par Marx.
- `leo-strauss` : Lessing, *Nathan le Sage* (les trois anneaux : ni la révélation ni la raison n'ont réfuté l'autre) ; Boccace, *Décaméron* I, 3 ; Xénophon en appoint.
- `marcel-gauchet` : Matthew Arnold, « Dover Beach » (« The Sea of Faith / Was once, too, at the full… ») ; Flaubert, *Madame Bovary* (Homais et Bournisien veillant Emma : la sortie de la religion en province).
- `charles-taylor` : Evelyn Waugh, *Retour à Brideshead* (la foi comme option, « a twitch upon the thread ») ; Chateaubriand, *René* (le vague des passions dans un monde qui se vide).
- `jurgen-habermas` : Goethe, *Faust* I (Faust traduisant « Im Anfang war das Wort » en « die Tat » : la sécularisation comme traduction) ; Thomas Mann, *Joseph et ses frères* (« le mythe en des mains humanistes ») si non pris par Philon.

### Douzième partie
- `pierre-hadot` : Rilke, « Torse archaïque d'Apollon » (« Du mußt dein Leben ändern » : l'exercice spirituel en un vers) ; Horace, *Odes* (carpe diem, la vue d'en haut) ; Thoreau, *Walden* (vivre délibérément).
- `michel-foucault` : Oscar Wilde, *Le Portrait de Dorian Gray* et *De Profundis* (l'esthétique de l'existence, l'objection « dandysme » de Hadot en scène) ; Baudelaire, « Le Peintre de la vie moderne » (le dandy).
- `jaspers` : Kafka, *Le Château* (K. devant un sens qui se refuse : le chiffre et l'échec) ; Hölderlin, « Hälfte des Lebens » en appoint.
- `pourquoi-y-a-t-il-quelque-chose-plutot-que-rien-un-debat-construit` : Leopardi, « Canto notturno di un pastore errante dell'Asia » (« Che fai tu, luna, in ciel? ») ; Beckett, *En attendant Godot* (« Rien à faire » : la question dissoute) ; Hugo, « Ce que dit la bouche d'ombre » en appoint.
- `iris-murdoch` : George Eliot, *Middlemarch*, finale (Dorothea, « the growing good of the world », l'attention aux autres) ; Murdoch, *La Mer, la mer* (Charles Arrowby, l'ego qui échoue à se désaisir).
- `le-bouddhisme-des-philosophes` : Hesse, *Siddhartha* si non pris par Plotin (le refus de la doctrine, l'expérience) ; Kipling, *Kim* (le lama et la Roue) ; Kerouac, *Les Clochards célestes* (le bouddhisme réinventé en Occident).
- `andre-comte-sponville` : Rimbaud, « L'Éternité » (« C'est la mer allée / Avec le soleil » : l'éternité, c'est maintenant) ; Camus, *Noces* (« Noces à Tipasa », le Royaume ici) ; Giono, *Colline* ou Whitman en appoint.
- `luc-ferry` : Hugo, *La Légende des siècles* (« Le Satyre », « Plein ciel » : la divinisation de l'humain, le progrès comme salut) ; Zola, *Travail* (la cité de l'Humanité).
- `comte-sponville-et-ferry` : pas d'encadré propre (section de synthèse), sauf si une œuvre tient les deux pôles : Montaigne déjà philosophe ; option Hugo, *Les Contemplations* (« acceptation » et « protestation » dans un même recueil).
- `l-islam-devant-la-sortie-de-la-religion` : Al-Ma'arrî, *Luzûmiyyât* (le sceptique de Ma'arra) ; Omar Khayyâm, *Robaiyat* ; Naguib Mahfouz, *Les Fils de la médina* (Arafa et la mort de Gabalawi : la mort de Dieu en roman arabe, interdit au Caire).
- `les-athees-militants-contemporains` : Thomas Mann, *La Montagne magique* (Settembrini, l'humaniste militant) ; Anatole France, *La Révolte des anges* (l'ange qui lit la bibliothèque et refait un dieu) ; Flannery O'Connor si non prise par Stirner.

### Conclusion
- `le-bilan-des-refondations` : Saint-Exupéry, *Vol de nuit* (Rivière exige le sacrifice des pilotes au courrier : l'absolu qui exige, dit par un auteur qui l'admire) ; Hugo, *Quatrevingt-treize* si non pris.
- `ce-que-les-exceptions-ont-en-commun` : Hesse, *Le Jeu des perles de verre* (Castalie, la spiritualité d'exercice sans Église ; Joseph Valet quittant l'ordre) ; Rilke, « Torse archaïque » si non pris par Hadot.
- `le-soupir-sans-ciel` : Primo Levi, *Si c'est un homme* (la prière de Kuhn, le bouc émissaire : « Si j'étais Dieu, je cracherais à terre la prière de Kuhn ») ; Steinbeck, *Les Raisins de la colère* (Tom Joad : « je serai là », le nous horizontal) ; Hugo, *Les Misérables* (la plainte qui change d'adresse) ; Char en appoint.

Auteurs convoqués (environ 90) : Aristophane, Euripide, Sophocle, Homère, Ovide, Horace, Dante, Boccace, Pétrarque, Jean de la Croix, Angelus Silesius, Cervantès, Shakespeare, Corneille, Racine, Montesquieu, Swift, Pope, Sterne, Diderot, Lessing, Goethe, Schiller, Jean Paul, Hölderlin, Novalis, Kleist, Wordsworth, Blake, Shelley, Mary Shelley, Leopardi, Chateaubriand, Lamartine, Hugo, Nerval, Baudelaire, Rimbaud, Flaubert, Maupassant, Zola, Huysmans, Anatole France, Proust, Péguy, Claudel, Valéry, Gide, Bernanos, Giono, Malraux, Saint-Exupéry, Camus, Sartre, Char, Céline (à placer : *Voyage au bout de la nuit*, Bardamu et la religion de la guerre ou de l'argent, pour Marx ou Weber), Dickens, George Eliot, Hardy, Arnold, Carroll, Wilde, Conrad, Kipling, T. S. Eliot, Waugh, Greene, Golding, Orwell, Koestler, Tolstoï, Dostoïevski, Tourgueniev, Boulgakov, Grossman, Ibsen, Hamsun, Strindberg (option), Thomas Mann, Hesse, Kafka, Rilke, Musil, Brecht, Celan, Zweig, Melville, Hawthorne (option), Whitman, Thoreau, Hemingway, Steinbeck, O'Connor, Jackson, Poe, Pirandello, Lampedusa, Silone, Levi, Unamuno, Borges, Kazantzakis, Tagore, Al-Ma'arrî, Khayyâm, Mahfouz, Singer, Defoe, Bunyan, Trakl, Beckett, Kerouac, Yourcenar, Eco.
