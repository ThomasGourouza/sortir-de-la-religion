# Plan : encadrés « En littérature » dans l'essai *Sortir de la religion sans en fonder une autre ?*

## Contexte

L'essai (154 000 mots, douze parties, environ 85 philosophes) illustre déjà ses idées par des tableaux insérés dans la version web. L'auteur veut faire de même avec la littérature classique : pour chaque section d'auteur, chaque débat construit et chaque section de la conclusion, un encadré distinct du texte de fond, que le lecteur peut ignorer, qui cite une à trois œuvres littéraires (extrait court ou résumé de scène, explication du lien avec la thèse de la section, auteur et œuvre en fin d'encadré). But : convoquer le plus d'auteurs classiques possible (dont Céline, Hesse, Proust, Hugo, Saint-Exupéry, Goethe, Byron, Shelley, et des fables et contes) en restant pertinent, sans ajouter de contenu théorique.

Un plan avait été écrit le 14 octobre 2026 sur une autre machine (`~/Documents/sortir-de-la-religion/PLAN-encadres-litteraires.md`, commit f497104) et jamais exécuté : ni `litterature.json`, ni `.lettres` dans le CSS, ni `<aside>` dans `index.html`. Il prévoyait un JSON injecté dans le HTML parce que la source Markdown n'était pas sur cette machine-là. Ici elle est présente : `~/Documents/litterature/articles/2026-10-11-sortir-de-la-religion.md` (v6, maj 2026-10-13), et `python3 build/build.py` la reconstruit (vérifié dans le scratchpad : pages identiques au dépôt, sauf trois retouches faites à la main sur `index.html` le 14 octobre : compteur de mots `hero-meta` mis en commentaire, indentation, et deux liens de lexique qui pointaient vers l'abrégé supprimé).

**Décisions prises avec l'utilisateur** (14 et 15 octobre 2026) :
- Encadré **replié par défaut**, ligne de titre visible (« En littérature : Victor Hugo, *Quatrevingt-treize* (1874) »).
- Périmètre : toutes les sections d'auteurs, les cinq débats construits, les trois sections de la conclusion (environ 90 encadrés). Pas le prologue, pas les passages ni les bilans.
- Les encadrés sont écrits **dans le Markdown de l'essai**, dans leur section, comme blocs de citation ; `build.py` les rend en encadrés repliables (décision du 15 octobre, remplace le JSON).
- Règle de citation de l'essai conservée telle quelle : aucune citation de mémoire. On ne cite entre guillemets que ce qui a été retrouvé dans `textes/` (statut `[vérifiée, ...]`) ou sur une page lue dans la session (`[citée d'après ...]`) ; sinon on résume la scène sans guillemets. Œuvres sous droits (Céline, Hesse, Saint-Exupéry en France, Camus, Malraux, Koestler, Grossman, Levi, O'Connor, Waugh, Greene, Mahfouz, Beckett, Kerouac, Lampedusa, Kazantzakis, Boulgakov, Steinbeck, Hemingway, Jackson, Celan, Char, Giono, Borges, Eco, Singer, Murdoch, Brecht, Silone, T. S. Eliot, Yourcenar, Musil) : résumé seulement.
- Page outil « Bibliothèque » listant les œuvres citées, faite en dernier.
- Jamais de tiret cadratin ni demi-cadratin ; pas de commit sans demande (dans les deux dépôts).

## Principe technique

Un bloc Markdown par encadré, une fonction de rendu, un style, une page outil. Aucun JSON nouveau.

### 1. Syntaxe dans le Markdown (fichier `articles/2026-10-11-sortir-de-la-religion.md`)

Placé en fin de section (après le paragraphe de verdict, avant le `###` suivant), ou après un paragraphe précis quand une scène répond à une phrase donnée :

```markdown
> **En littérature.** Victor Hugo, *Quatrevingt-treize* (1874) ; Anatole France, *Les dieux ont soif* (1912)
>
> Cimourdain, prêtre devenu délégué du Comité de salut public, ... (une phrase qui situe, puis l'extrait de quatre lignes au plus, ou le résumé explicite : « je résume »).
>
> « ... » [vérifiée, `textes/hugo-quatrevingt-treize`, III, VII, 5]
>
> Pourquoi ici : Cimourdain est la religion civile de Rousseau faite homme ... (renvoie aux termes de la section : critère du sacrifice, refondation stricte ou douce, exception, régime de l'erreur).
>
> Sources : Victor Hugo, *Quatrevingt-treize*, troisième partie, livre VII (1874) ; Anatole France, *Les dieux ont soif*, ch. XXVIII (1912).
```

- Première ligne : `**En littérature.**` puis la liste des œuvres au format strict `Auteur, *Titre* (date)` ou `Auteur, « Titre » (date)`, séparées par ` ; ` (c'est ce que la page Bibliothèque analyse).
- Paragraphes séparés par une ligne `>` seule. Les statuts entre crochets suivent la convention de l'essai et sont masqués par `masquer_statuts` comme partout.
- Dernier paragraphe commençant par `Source :` ou `Sources :`.
- Tout lecteur du Markdown (GitHub, éditeur) voit un bloc de citation en retrait : lisible et distinct sans outil.

### 2. `build/build.py` (dépôt `sortir-de-la-religion`)

- `rendre_blocs` (ligne 114) : pour un bloc `quote` dont la première ligne correspond à `^>\s*\*\*En littérature\.\*\*`, appeler une nouvelle fonction `encadre_lettres(lignes)` au lieu du rendu `<blockquote>`. Elle découpe sur les lignes `>` vides, rend chaque paragraphe par `en_ligne(masquer_statuts(...))`, et produit :
  `<aside class="lettres"><details><summary><span class="lettres-label">En littérature</span> <span class="lettres-titre">Victor Hugo, <em>Quatrevingt-treize</em> (1874) ; …</span></summary><div class="lettres-corps"><p>…</p><p class="lettres-source">Sources : …</p></div></details></aside>` (un seul bloc, sur une ligne, comme tous les blocs d'`index.html`).
- `mots` (ligne 69) : retirer d'abord les `<aside class="lettres">…</aside>` (`re.S`) pour que les encadrés n'entrent ni dans les temps de lecture des sections ni dans le total.
- `inserer_figures` (ligne 245) : calculer `n` sur les blocs qui ne commencent pas par `<aside` pour ne pas déplacer les tableaux.
- `lier_lexique` (ligne 281) : ajouter `"aside"` à la liste des balises bloquantes, pour que la première occurrence d'un terme du lexique reste dans le texte de fond.
- Collecte pour la Bibliothèque : `encadre_lettres` renvoie aussi la liste `(auteur, titre, date)` analysée dans la ligne de titre (motif `^(.+?), (?:\*(.+?)\*|« (.+?) »)(?: \((.+?)\))?$` sur chaque élément séparé par ` ; `) ; `construire` accumule `(sid, titre de section, œuvres)` dans `r["lettres"]` et avertit sur toute ligne de titre qui ne s'analyse pas.
- Page `bibliotheque.html` dans `pages_outils` (ligne 340), sur le modèle du lexique (`page_outil`, ligne 327) : entrées triées par nom d'auteur (clé = dernier mot du nom, en gardant la particule capitalisée qui précède : « La Fontaine », « Saint-Exupéry » reste un mot), chaque auteur avec ses œuvres (titre, date) et un lien « Lire dans l'essai » par section (`index.html#id`), filtre texte `data-filtre-texte` comme les autres pages. Ajouter `("bibliotheque.html", "Bibliothèque")` à la navigation de `page_outil`, au `drawer-outils` (`build/template.html:82`) et au `hero-outils` (`:103`), à `SHELL` dans `build/sw.template.js`, et à la phrase « Une frise, une carte des réponses et un lexique complètent la lecture » (`build.py:567`).
- Reporter dans `build/template.html:99` la retouche manuelle du 14 octobre (ligne `hero-meta` mise en commentaire) pour qu'un vrai build reproduise `index.html` tel qu'il est publié.

### 3. `css/style.css`

Près des styles de `blockquote` et `figure` ; vérifier d'abord qu'aucune règle générale sur `summary` ou `details` (section repliable) ne déborde sur l'encadré, et scoper si besoin.

```css
.lettres { margin: 1.2em 0; font-size: .94em; }
.lettres > details { border: 1px solid var(--line); border-left: 4px solid var(--accent); border-radius: 12px; background: var(--bg-soft); }
.lettres summary { padding: 8px 12px; cursor: pointer; font: 600 14px/1.4 var(--sans); list-style: none; }
.lettres-label { color: var(--accent); text-transform: uppercase; letter-spacing: .04em; font-size: 11.5px; margin-right: 6px; }
.lettres-corps { padding: 4px 14px 8px; }
.lettres-source { font: 12.5px var(--sans); color: var(--ink-soft); margin: .2em 0 .6em; }
```

Pas de JavaScript : `details` natif ; `reveal()` (`js/app.js:39`) ouvre déjà tous les `details` ancêtres d'une cible, donc la recherche plein texte qui tombe dans un encadré l'ouvre. Les variables existent dans les quatre thèmes (lignes 6-39).

### 4. Fichiers touchés dans le dépôt `litterature`

- `articles/2026-10-11-sortir-de-la-religion.md` : les encadrés ; en-tête `version: 7`, `maj: 2026-10-15`, `version-precedente: articles/2026-10-11-sortir-de-la-religion-v6.md` (copier le fichier actuel sous ce nom avant toute modification, comme pour v1 à v5) ; section « Sources » : ajouter les textes littéraires récupérés à « Textes sources vérifiés » et les résumés d'œuvres sous droits à « Restent à contrôler ».
- `textes/` et `textes/INDEX.md` : textes du domaine public récupérés par `tools/fetch_text.py` (Gutenberg, Wikisource) ; pour zeno.org, projekt-gutenberg.org ou archive.org, récupération par WebFetch et ligne d'index écrite à la main, comme pour les textes Nietzsche et Schleiermacher déjà présents.
- `knowledge/connexions/litterature-et-critique-de-la-religion.md` (nouveau) et sa ligne dans `knowledge/INDEX.md` : la table des correspondances œuvre / section / thèse, pour réemploi (skill `sauver-note`).

### 5. Fichiers touchés dans le dépôt `sortir-de-la-religion`

`build/build.py`, `build/template.html`, `build/sw.template.js`, `css/style.css`, les pages générées (`index.html`, `frise.html`, `reponses.html`, `lexique.html`, `bibliotheque.html`, `sw.js`), `README.md` et `CLAUDE.md` (une phrase chacun : syntaxe des encadrés, page Bibliothèque), et `PLAN-encadres-litteraires.md` remplacé par ce plan mis à jour (il est versionné, l'autre machine le lit).

## Règles d'écriture des encadrés

- 120 à 220 mots, une à trois œuvres. Jamais de théorie nouvelle : le « pourquoi ici » renvoie aux termes de la section.
- Par œuvre : une phrase qui situe la scène ; l'extrait (quatre lignes au plus) ou le résumé annoncé comme tel ; une ou deux phrases « pourquoi ici » ; la source en fin d'encadré (auteur, œuvre, lieu, date).
- Citations seulement vérifiées (`grep` dans `textes/`, fichier nommé) ; vers très célèbres aussi en langue originale ; traductions sans traducteur = « je traduis ».
- Titres étrangers en langue originale à la première mention, puis titre français reçu ; dates d'auteur non répétées (les sections les donnent pour les philosophes ; pour les écrivains, la date de l'œuvre suffit, la Bibliothèque les classe).
- Pas de doublon d'œuvre entre sections, sauf scène différente et deux fois au plus (*Les Misérables*, *Madame Bovary*, *Moby-Dick*, *Der Zauberberg*, *Du côté de chez Swann*). Un même auteur peut revenir avec d'autres œuvres (Hugo, Goethe, Kafka, Flaubert, Tolstoï, Mann, Proust, Byron, Saint-Exupéry).
- Pas de psychologisation de l'auteur, pas de résumé d'éditeur : la scène n'est racontée que pour ce qu'elle illustre.
- Lire la section dans le Markdown (`sed -n` sur les lignes données par `grep -n '^### '`) avant d'écrire son encadré, pour choisir l'ancre et reprendre ses mots.

## Déroulement

1. **Préparation** : archiver `-v6.md`, mettre à jour l'en-tête ; reporter `hero-meta` dans le gabarit ; rebuild et diff avec `index.html` publié (seuls l'indentation et les deux liens de lexique de l'abrégé doivent différer).
2. **Technique** avec deux encadrés d'essai (Rousseau, Malinowski) écrits dans le Markdown : `build.py`, CSS, build, contrôle visuel sur `python3 -m http.server 8000` avec les outils Chrome (1440 px et 390 px, thème sombre, encadré replié puis ouvert, recherche d'un mot propre à l'encadré).
3. **Rédaction par lots**, dans l'ordre de l'essai, selon l'annexe : (a) première à quatrième partie ; (b) cinquième à septième ; (c) huitième et neuvième ; (d) dixième et onzième ; (e) douzième et conclusion. Pour chaque lot : récupérer les textes libres nécessaires, vérifier chaque citation par `grep`, écrire les encadrés, rebuild, relire le rendu d'une section du lot. Toute scène dont le détail n'est pas sûr est vérifiée dans le texte ou marquée « à contrôler » dans la section Sources.
4. **Bibliothèque**, navigation, service worker, README, CLAUDE.md, note `knowledge/`, remplacement du plan versionné.
5. **Bilan** remis à l'auteur : nombre d'encadrés, d'auteurs et d'œuvres ; liste des citations et résumés à contrôler ; rappel qu'aucun commit n'a été fait.

## Vérification

- `python3 -m py_compile build/build.py` ; `python3 build/build.py` deux fois : `index.html` identique hors horodatage `?v=` ; aucun avertissement (ligne de titre inanalysable, section inconnue).
- Temps de lecture : les `part-meta` et `sec-time` d'`index.html` sont identiques avant et après l'ajout des encadrés.
- Lexique : la liste des ancres `class="lex"` (terme et paragraphe d'accueil) est identique avant et après.
- Navigateur (Chrome, 1440 px et 390 px, thèmes clair et sombre) : encadré replié lisible, ouverture au toucher, pas de débordement, sources en bas ; la recherche plein texte d'un mot propre à un encadré ouvre la section et l'encadré ; `bibliotheque.html` liste tous les auteurs avec des liens qui résolvent.
- `grep -nP '[\x{2013}\x{2014}]'` sur le Markdown modifié, le CSS, `build.py`, README, CLAUDE.md : aucun résultat.
- `verificateur-citations` (agent) sur le texte des encadrés d'un lot sur deux, au minimum sur les lots (b) et (e).

## Annexe : correspondances retenues, section par section

Format : id : œuvre(s) ; scène ; lien avec la section ; [DP] texte libre à récupérer pour citer, [R] résumé seulement (droits), [?] détail à vérifier dans le texte avant d'écrire. La relecture de chaque section au moment de l'écriture peut remplacer un candidat.

### Première partie
- `platon` : Aristophane, *Les Nuées* [DP] (Strepsiade brûle le pensoir de Socrate accusé de nier Zeus : la cité qui punit l'impie, réflexe que *Lois* X transforme en loi) ; Saint-Exupéry, *Citadelle* [R] (le chef berbère fonde le sens par la contrainte et la cérémonie : le législateur).
- `aristote` : Dante, *Paradiso* XXXIII, 145 [DP] (« l'amor che move il sole e l'altre stelle » : le moteur qui meut comme ce qui est aimé, devenu Dieu des chrétiens) ; *Inferno* IV, 131 [DP] (« il maestro di color che sanno » : le philosophe honoré et exclu, dieu qui ignore le monde).
- `epicure-et-lucrece` : Leopardi, *La ginestra* [DP] (la nature indifférente, la consolation refusée, l'ironie des « magnifiche sorti e progressive ») ; Horace, *Odes* I, 34 [DP] (« parcus deorum cultor et infrequens » ramené aux dieux par un tonnerre en ciel clair : la crainte, cause de la superstition, chez un épicurien) ; Yourcenar, *Mémoires d'Hadrien* [R] en une phrase.
- `plotin` : Jean de la Croix, *Noche oscura* [DP] (« amada en el Amado transformada » : la fuite du seul vers le seul, mais avec révélation) ; Rûmî, *Mathnawî*, prologue de la flûte de roseau [DP, trad. à récupérer] (la séparation d'avec l'Un et le retour : spiritualité sans Église).
- `averroes` : Borges, « La busca de Averroes » (*El Aleph*, 1949) [R] (Averroès cherchant « tragédie » et « comédie » sans avoir vu de théâtre : la limite du commentaire) ; Eco, *Il nome della rosa* [R] (Jorge et le second livre de la *Poétique* : le savoir interdit au vulgaire, les trois classes).
- `maimonide` : Kafka, « Vor dem Gesetz » [DP] (la porte faite pour un seul : la Loi à deux publics, la septième cause de contradiction) ; I. B. Singer, *Le Magicien de Lublin* [R] (Yasha devant un Dieu dont on ne sait rien).
- `maitre-eckhart` : Angelus Silesius, *Cherubinischer Wandersmann* I, 8 et I, 289 [DP, ?numéros] (« Ich weiß, daß ohne mich Gott nicht ein Nu kann leben » ; « Die Ros ist ohn Warum ») ; Rilke, *Das Stunden-Buch* [DP] (« Was wirst du tun, Gott, wenn ich sterbe? ») ; Musil, « l'autre état » [R] en une phrase.

### Deuxième partie
- `philon-d-alexandrie` : Thomas Mann, *Joseph und seine Brüder* [R] (la Genèse relue en roman, « le mythe en des mains humanistes » : l'allégorie comme traduction).
- `paul-de-tarse` : Kazantzakis, *La Dernière Tentation* [R] (Paul annonce au Jésus vieilli qu'il prêchera le Christ crucifié qu'il lui faut : la thèse de Nietzsche en scène) ; Anatole France, *Sur la pierre blanche* [DP] (Gallion à Corinthe ne remarque pas Paul : « folie pour les Grecs », la philosophie qui ne voit pas passer ce qui va la remplacer).
- `justin-martyr` : Corneille, *Polyeucte* [DP] (le martyr brise les idoles et cherche la mort : l'offrande de soi, et c'est Rome qui exige) ; Sienkiewicz, *Quo vadis* [DP] (Pétrone devant les chrétiens et les torches de Néron).
- `celse-et-origene` : Lucien, *Sur la mort de Pérégrinus* [DP, trad. Talbot] (le regard d'un lettré païen vers 165 sur des chrétiens crédules : le public d'ignorants de Celse) ; Flaubert, *La Tentation de saint Antoine* [DP] (le défilé des hérésies, Hilarion comme la Science).
- `porphyre-et-augustin` : Ibsen, *Kejser og Galilæer* [DP, trad.] (Julien et le « troisième empire » : la refondation païenne) ; Proust, *Le Temps retrouvé* [DP, déjà dans `textes/`] (« la vraie vie... c'est la littérature » : l'intériorité augustinienne devenue mémoire) ; Pétrarque, *Secretum* [DP] en une phrase (le dialogue avec Augustinus).
- `jesus-a-t-il-existe-le-jesus-de-l-histoire-et-la-these-mythiste` : Boulgakov, *Le Maître et Marguerite*, ch. 1 [R] (Berlioz explique que Jésus n'a pas existé, Woland soutient le contraire) ; Anatole France, « Le Procurateur de Judée » [DP] (Pilate ne se souvient pas de Jésus : l'insignifiance historique et la transformation en Logos).

### Troisième partie
- `montaigne` : Shakespeare, *The Tempest* II, 1 [DP] (Gonzalo recopie « Des Cannibales » par Florio) et *Hamlet* II, 2 [DP] (« there is nothing either good or bad, but thinking makes it so » : la coutume, le doute).
- `descartes` : Valéry, *Monsieur Teste* [DP] (l'intellect pur en personnage, « la bêtise n'est pas mon fort » : le moment cartésien de Foucault, la spiritualité devenue méthode).
- `pascal` : Baudelaire, « Le Gouffre » [DP] (« Pascal avait son gouffre, avec lui se mouvant ») ; Racine, *Phèdre* [DP] (la grâce absente, lecture de Goldmann, *Le Dieu caché*, signalée comme interprétation).
- `spinoza` : Goethe, *Dichtung und Wahrheit* XIV [DP] (Spinoza lu comme apaisement ; « Wer Gott recht liebt, muß nicht verlangen, daß Gott ihn wiederliebe », écho d'*Éthique* V, 19) ; I. B. Singer, « Le Spinoza de la rue du Marché » [R] (Fischelson, l'*Éthique* et Dobbe : la béatitude et la vie) ; Borges, « Spinoza » [R] en une phrase.
- `bayle` : Montesquieu, *Lettres persanes* XI-XIV [DP] (les Troglodytes : vertu sans Église, société possible) ; Swift, *Gulliver* I, 4 [DP] (Gros-Boutiens et Petits-Boutiens : les guerres de religion ramenées à un œuf).
- `leibniz` : Voltaire, *Zadig*, « L'Ermite » [DP] (Jesrad : « il n'y a point de mal dont il ne naisse un bien » ; « Mais, dit Zadig... » : la théodicée et la plainte qu'on lui demande de taire) ; Pope, *Essay on Man* I [DP] (« Whatever is, is right », cible de Voltaire) ; Byron, *Cain* [DP] (Caïn et Lucifer devant la justice du Créateur, le refus du sacrifice : Ivan avant Ivan).

### Quatrième partie
- `hume` : Diderot, *Lettre sur les aveugles* [DP] (Saunderson : « si vous voulez que je croie en Dieu, il faut que vous me le fassiez toucher » [?mot à mot] : la preuve par le dessein refusée, comme Philon des *Dialogues*) ; Sterne, *Tristram Shandy* [DP] (la digression comme suspension, le sermon de Yorick lu par Trim).
- `voltaire` : Unamuno, *San Manuel Bueno, mártir* [DP, ?texte libre] (le curé sans foi qui la garde pour son village : « il faudrait l'inventer » vécu, le Grand Inquisiteur bienveillant) ; Stendhal, *Le Rouge et le Noir* [DP] (le séminaire de Besançon : la religion comme carrière et instrument).
- `rousseau` : Hugo, *Quatrevingt-treize* III, VII [DP, ?titre du chapitre « Le cachot » / « Les deux pôles du vrai »] (Cimourdain, « la république de l'absolu », condamne Gauvain et se tue : la religion civile faite homme) ; Anatole France, *Les dieux ont soif* [DP] (Gamelin et la fête de l'Être suprême).
- `d-holbach` : Shelley, *Queen Mab* VII et notes [DP] (« There is no God », l'Esprit de la Nature : l'athée qui prie la Nature) ; Sade, *Dialogue entre un prêtre et un moribond* [DP] (le mourant convertit le prêtre à la nature).
- `kant` : Kleist, *Michael Kohlhaas* [DP] (la justice érigée en absolu qui exige tout) et lettre de mars 1801 [DP] (la « crise kantienne ») ; Hugo, « La Conscience » (*La Légende des siècles*) [DP] (« L'œil était dans la tombe et regardait Caïn » : la loi morale en nous, le tribunal intérieur).
- `un-debat-construit` : Diderot, *Entretien d'un philosophe avec la maréchale de \*\*\** [DP] (l'athée honnête, le pari renversé) ; Hugo, *Les Misérables* I, 1, 10 [DP] (Myriel et le conventionnel G. : l'évêque demande la bénédiction de l'athée mourant : deux morales sans le même absolu).

### Cinquième partie
- `friedrich-schleiermacher` : Goethe, *Faust* I, « Marthens Garten » [DP] (la Gretchenfrage ; « Gefühl ist alles; / Name ist Schall und Rauch », 1808) ; Hölderlin, *Hyperion* [DP] (« Eines zu sein mit Allem, was lebt », 1797) ; Wordsworth, « Tintern Abbey » [DP] (« a sense sublime / Of something far more deeply interfused », 1798) : trois contemporains des *Discours* de 1799.
- `georg-wilhelm-friedrich-hegel` : Jean Paul, *Siebenkäs*, « Rede des toten Christus vom Weltgebäude herab, daß kein Gott sei » [DP] (la mort de Dieu avant Hegel) ; Mme de Staël, *De l'Allemagne* [DP] (sa traduction libre du « Songe », qui retire la fin consolante : deux auteurs, deux conclusions).
- `david-friedrich-strauss-et-bruno-bauer` : George Eliot, *Middlemarch* [DP] (Casaubon et la « Clé de toutes les mythologies » ; Eliot traductrice de Strauss en 1846) ; Tennyson, *In Memoriam* XCVI [DP, ?numéro] (« There lives more faith in honest doubt... » : la crise victorienne).
- `ernest-renan` : Proust, *Pastiches et mélanges*, « L'Affaire Lemoine » [DP] (le pastiche de Renan : le prêtre « par les entrailles » saisi par le style) ; Barrès, *Huit jours chez M. Renan* [DP] (le dilettante devant le culte du grand homme).

### Sixième partie
- `ludwig-feuerbach` : Steinbeck, *The Grapes of Wrath*, ch. 4 [R] (Jim Casy, l'ex-prédicateur : peut-être que le Saint-Esprit, c'est tous les hommes et toutes les femmes qu'on aime : la religion de l'amour humain, « Homo homini Deus ») ; Goethe, « Das Göttliche » [DP] (« Edel sei der Mensch » : les prédicats divins transportés sur l'homme) ; George Eliot, *Adam Bede* (Dinah Morris) en une phrase, la traductrice de 1854.
- `max-stirner` : Byron, *Manfred* [DP] (Manfred refuse l'abbé et les esprits : « The mind which is immortal makes itself / Requital » : l'Unique romantique) ; Flannery O'Connor, *Wise Blood* [R] (Hazel Motes et l'Église sans Christ : l'athée pieux) ; Tourgueniev, *Pères et fils* [DP] (Bazarov ne s'incline devant rien).
- `karl-marx-et-friedrich-engels` : Zola, *Germinal* [DP] (le rêve d'Étienne, la grève comme religion nouvelle, Souvarine) ; Heine, *Deutschland. Ein Wintermärchen* I [DP] (« Wir wollen hier auf Erden schon / Das Himmelreich errichten », 1844, l'ami de Marx à Paris) ; Brecht, *Die heilige Johanna der Schlachthöfe* [R] (Jeanne découvre que la charité est l'opium).
- `soren-kierkegaard` : Ibsen, *Brand* [DP, trad.] (« tout ou rien » ; le pasteur sacrifie femme et enfant à l'absolu : le critère vu de l'intérieur de la foi) ; Kafka, lettre à Klopstock de juin 1921 sur Abraham [DP, ?texte libre] (« un autre Abraham »).
- `auguste-comte` : Flaubert, *Bouvard et Pécuchet* [DP, ?mention de Comte dans le roman] (ils essaient la religion puis la quittent ; le catéchisme) ; George Eliot, « O may I join the choir invisible » [DP] (la religion de l'Humanité en vers).
- `arthur-schopenhauer` : Thomas Mann, *Buddenbrooks* X, 5 [DP depuis 2026] (Thomas lit « Über den Tod » : l'ivresse métaphysique d'un soir, puis l'oubli) ; Maupassant, « Auprès d'un mort » [DP] (la veillée du philosophe).

### Septième partie
- `dostoievski` : Melville, *Billy Budd* [DP] (Vere condamne l'innocent pour l'ordre du navire : la logique de l'Inquisiteur) ; Hugo, *Les Misérables* V, 4, « Javert déraillé » [DP] (la loi comme absolu qui ne survit pas à la grâce).
- `nietzsche` : Nerval, « Le Christ aux Oliviers » [DP] (« Dieu n'est pas ! Dieu n'est plus ! », 1844) ; Swinburne, « Hymn to Proserpine » [DP] (« Thou hast conquered, O pale Galilean » : Dionysos contre le Crucifié) ; Thomas Mann, *Doktor Faustus* [DP depuis 2026] (Leverkühn, Nietzsche en musicien).

### Huitième partie
- `durkheim` : Zola, *Lourdes* [DP] (la foule, l'effervescence, le miracle collectif) ; Céline, *Voyage au bout de la nuit* [R] (Bardamu, août 1914, la Patrie sacrée qui exige : le dissident de l'effervescence).
- `weber` : Kafka, *Das Schloss* [DP] (la bureaucratie comme destin sans visage : l'habitacle d'acier) ; Defoe, *Robinson Crusoe* [DP] (le livre de comptes « Evil / Good » : l'ascèse intramondaine) ; Schiller, « Die Götter Griechenlands » [DP] (« die entgötterte Natur » : l'Entzauberung en vers, 1788).
- `william-james` : Tolstoï, *Confession* [DP] (le twice-born que James cite) ; Whitman, *Song of Myself* [DP] (« I find letters from God dropt in the street » : le once-born) ; Bunyan en une phrase.
- `rudolf-otto` : Rilke, *Duineser Elegien* I [DP] (« Ein jeder Engel ist schrecklich » : tremendum) ; Blake, « The Tyger » [DP] (« Did he who made the Lamb make thee? ») ; Melville, *Moby-Dick* 42 [DP] (la blancheur de la baleine).
- `freud` : Kafka, *Brief an den Vater* [DP] (le père comme Dieu) ; Andersen, « La Petite Fille aux allumettes » [DP] (la grand-mère dans la flamme : l'illusion commandée par le désir, « religion sans père mais non sans mère »).
- `bergson` : Proust, *Du côté de chez Swann* [DP, déjà dans `textes/`] (la madeleine, la durée retrouvée) ; Péguy, *Le Porche du mystère de la deuxième vertu* [DP] (la petite espérance, l'élan).
- `ricoeur` : Saint-Exupéry, *Le Petit Prince* XXI [R] (le renard, les rites : le symbole qui donne à penser, la seconde naïveté) ; Baudelaire, « Correspondances » [DP] (« forêts de symboles »).

### Neuvième partie
- `tylor-et-frazer` : Hugo, « Ce que dit la bouche d'ombre » [DP] (« Tout est plein d'âmes » : l'animisme en vers) ; Conrad, *Heart of Darkness* [DP] (Kurtz adoré, « unspeakable rites ») ; T. S. Eliot, *The Waste Land* [R] (bâti sur *Le Rameau d'or*, selon ses notes).
- `malinowski` : Hemingway, *The Old Man and the Sea* [R] (Santiago : pas religieux, mais dix Notre Père pour attraper le poisson : la magie là où règne l'incertitude) ; La Fontaine, « Le Chartier embourbé » VI, 18 [DP] (« Aide-toi, le Ciel t'aidera » : lagon et haute mer).
- `jung` : Hesse, *Demian* [R] (Abraxas, l'oiseau qui sort de l'œuf ; Hesse analysé par un jungien) ; Melville, *Moby-Dick* (Achab et Job) [DP] pour *Réponse à Job*.
- `girard` : Euripide, *Les Bacchantes* [DP] (Penthée dépecé par la foule : Dionysos contre le Crucifié) ; La Fontaine, « Les Animaux malades de la peste » VII, 1 [DP] (« Haro sur le baudet » : le bouc émissaire désigné) ; Shirley Jackson, « The Lottery » [R] ; Golding en une phrase.
- `becker` : Tolstoï, *La Mort d'Ivan Ilitch* [DP] (« Caïus est mortel » : le déni) ; Grimm, « Der Gevatter Tod » [DP] (le médecin qui trompe la Mort).
- `berger-et-luckmann` : Cervantès, *Don Quichotte* II, 74 [DP] (« Yo fui loco, y ya soy cuerdo » : la canopée qui s'effondre) ; Pirandello, *Così è (se vi pare)* [DP] ; Andersen, « Les Habits neufs de l'empereur » [DP] (la structure de plausibilité et le mot de l'enfant).
- `hervieu-leger` : Lampedusa, *Il Gattopardo* [R] (la fin d'une lignée, le père Pirrone) ; Proust, *Du côté de chez Swann* [DP] (l'église de Combray, mémoire d'une lignée).
- `boyer` : Flaubert, « Un cœur simple » [DP] (Loulou devenu Saint-Esprit : l'inférence qui fabrique un dieu) ; Ovide, *Métamorphoses* [DP] (un monde plein d'agents) ; Carroll en une phrase (six choses impossibles).
- `norris-et-inglehart` : Hamsun, *Sult* [DP, trad.] (l'affamé qui crie vers Dieu) ; Dickens, *Hard Times* I, 5 [DP, ?chapitre] (Coketown, dix-huit confessions et des ouvriers qui n'y vont pas : l'insécurité et la croyance).
- `pourquoi-croit-on-un-debat-construit` : Flaubert, *Madame Bovary* II, 14 [DP] (la dévotion d'Emma après Rodolphe : la religion comme réponse au manque) ; Lamartine, « Le Désespoir » et « La Providence à l'homme » [DP] (la plainte et la réponse, 1820).
- `a-t-on-le-droit-de-croire-clifford-james-et-la-philosophie-analytique` : Ibsen, *Samfundets støtter* [DP, trad.] (Bernick laisse partir l'« Indian Girl » : l'armateur de Clifford) ; Conrad, *Lord Jim* [DP] (le Patna et ses pèlerins).

### Dixième partie
- `heidegger` : Hölderlin, « Patmos » [DP] (« Wo aber Gefahr ist, wächst / Das Rettende auch ») ; Kafka, « Eine kaiserliche Botschaft » [DP] (le message qui n'arrive jamais : le dieu attendu) ; Celan, « Todtnauberg » [R] (1967, la parole attendue).
- `wittgenstein` : Tolstoï, « Les Trois Vieillards » [DP] (« Trois vous êtes, trois nous sommes » : la prière que l'évêque ne peut améliorer ; le rite exprime) ; Tagore, *Le Roi de la chambre obscure* [DP] (lu au Cercle de Vienne) ; Trakl en une phrase.
- `barth` : Bernanos, *Journal d'un curé de campagne* [DP depuis 2019] (« Tout est grâce » : la religion affaire de l'homme, la foi reçue) ; Kafka, *Der Prozess*, la cathédrale [DP] (« Das Gericht will nichts von dir » : la différence qualitative infinie).
- `bonhoeffer` : Camus, *La Peste* [R] (les deux sermons de Paneloux, la mort de l'enfant) ; Greene, *The Power and the Glory* [R] (le prêtre faible, Dieu impuissant dans le monde).
- `simone-weil` : Homère, *Iliade* XXIV [DP] (Priam aux pieds d'Achille : le poème de la force) ; Sophocle, *Antigone* [DP] (Weil l'expliquait aux ouvriers).
- `bataille` : Baudelaire, « Les Litanies de Satan » [DP] ; Huysmans, *Là-bas* [DP] (la transgression comme sacré) ; Sade en une phrase.
- `sartre` : Sartre, *Les Mouches* [R] (Oreste : les hommes d'Argos sont mes hommes) et *Le Diable et le bon Dieu* [R] (Goetz : il n'y a que les hommes) : la position athée cohérente mise en scène par elle-même.
- `camus` : Camus, *L'Étranger* [R] (Meursault et l'aumônier, « la tendre indifférence du monde ») ; Malraux, *La Condition humaine* [R] (Katow donne son cyanure : l'offrande de soi, le « nous ») ; Char en une phrase.
- `levinas` : Grossman, *Vie et destin* [R] (le cahier d'Ikonnikov, « la petite bonté » que Levinas commentait) ; Tolstoï, « Maître et serviteur » [DP] (Brekhounov couvre Nikita de son corps : la substitution).
- `marion` : Dostoïevski, *L'Idiot* [DP] (le Christ mort de Holbein : idole ou icône) ; Gogol, « Le Portrait » [DP] (le tableau qui capte : l'idole comme miroir).

### Onzième partie
- `carl-schmitt` : Thomas Mann, *Der Zauberberg* [DP depuis 2026] (Naphta : la terreur au service de l'absolu) ; Shakespeare, *Richard II* III, 2 [DP] (« Not all the water in the rough rude sea / Can wash the balm off from an anointed king ») ; Büchner, *Dantons Tod* en une phrase.
- `karl-lowith` : Tolstoï, *Guerre et Paix*, épilogue II [DP] (l'histoire sans providence) ; Flaubert, *L'Éducation sentimentale* [DP] (1848 comme farce).
- `hans-blumenberg` : Goethe, « Prometheus » [DP] (« Hier sitz ich, forme Menschen / Nach meinem Bilde » : l'affirmation de soi) ; Mary Shelley, *Frankenstein; or, The Modern Prometheus* [DP] ; Kafka, « Prometheus » [DP] (quatre légendes ; « la légende tente d'expliquer l'inexplicable » : fin d'*Arbeit am Mythos*).
- `voegelin-et-aron` : Koestler, *Darkness at Noon* [R] (Roubachof, le Parti comme Église) ; Orwell, *1984* [DP en Europe depuis 2021, ?source libre] (O'Brien : « God is power ») ; Silone, *Pane e vino* en une phrase.
- `leo-strauss` : Lessing, *Nathan der Weise* III, 7 [DP] (les trois anneaux) ; Boccace, *Decameron* I, 3 [DP] (Melchisédech) ; Xénophon en une phrase.
- `marcel-gauchet` : Arnold, « Dover Beach » [DP] (« The Sea of Faith ») ; Flaubert, *Madame Bovary* III, 9 [DP] (Homais et Bournisien veillant Emma) ; Hugo, *Religions et religion* [DP] (les religions quittées, la religion gardée : « sortie de la religion ne signifie pas sortie de la croyance »).
- `charles-taylor` : Waugh, *Brideshead Revisited* [R] (« a twitch upon the thread » : la foi comme option) ; Chateaubriand, *René* [DP] (le vague des passions dans un monde qui se vide).
- `jurgen-habermas` : Goethe, *Faust* I, « Studierzimmer » [DP] (« Im Anfang war die Tat » : la sécularisation comme traduction) ; Lessing, *Die Erziehung des Menschengeschlechts* § 4 [DP] (la révélation comme éducation : la traduction avant Habermas).

### Douzième partie
- `pierre-hadot` : Rilke, « Archaïscher Torso Apollos » [DP] (« Du mußt dein Leben ändern ») ; Horace, *Odes* I, 11 [DP] (carpe diem) ; Thoreau, *Walden* [DP] (« live deliberately »).
- `michel-foucault` : Wilde, *The Picture of Dorian Gray* et *De Profundis* [DP] (l'esthétique de l'existence et son revers) ; Gide, *L'Immoraliste* [DP] (Michel, la liberté qui ne sait qu'en faire : l'objection « dandysme » de Hadot).
- `jaspers` : Shakespeare, *King Lear* [DP] (la tempête : situation-limite, échec, « As flies to wanton boys... » ; Jaspers sur le tragique) ; Hölderlin, « Hälfte des Lebens » [DP] (le chiffre, l'hiver).
- `pourquoi-y-a-t-il-quelque-chose-plutot-que-rien-un-debat-construit` : Leopardi, « Canto notturno di un pastore errante dell'Asia » [DP] (« Che fai tu, luna, in ciel? ») ; Whitman, « Miracles » [DP] (« every hour of the light and dark is a miracle » : l'étonnement sans dette) ; Beckett, *En attendant Godot* [R] (« Rien à faire » : la question dissoute).
- `iris-murdoch` : Proust, *La Prisonnière*, la mort de Bergotte [DP, déjà dans `textes/`] (les obligations « contractées dans une vie antérieure », le petit pan de mur jaune : un Bien sans Dieu, nécessairement réel) ; George Eliot, *Middlemarch*, finale [DP] (« the growing good of the world ») ; Murdoch, *The Sea, the Sea* [R] (l'ego qui échoue à se dessaisir).
- `le-bouddhisme-des-philosophes` : Hesse, *Siddhartha* [R] (le refus de la doctrine du Bouddha, l'expérience : la projection européenne) ; Kipling, *Kim* [DP] (le lama et la Roue) ; Kerouac, *The Dharma Bums* [R] (le bouddhisme réinventé).
- `andre-comte-sponville` : Rimbaud, « L'Éternité » [DP] (« C'est la mer allée / Avec le soleil ») ; Camus, *Noces à Tipasa* [R] (le Royaume ici) ; Giono en une phrase.
- `luc-ferry` : Hugo, « Le Satyre » (*La Légende des siècles*) [DP] (« Place à Tout ! Je suis Pan » : la divinisation de l'humain) ; Zola, *Travail* [DP] (la cité de l'Humanité).
- `comte-sponville-et-ferry` : facultatif ; Goethe, « Grenzen der Menschheit » [DP] (« Denn mit Göttern / Soll sich nicht messen / Irgendein Mensch » : le pôle de l'acceptation, face au « Satyre » qui précède).
- `l-islam-devant-la-sortie-de-la-religion` : Al-Maʿarrī, *Luzūmiyyāt* [DP, trad. Nicholson, ?vers exact] (le sceptique de Maʿarra) ; Khayyâm, *Rubáiyát* (FitzGerald) [DP] ; Mahfouz, *Awlād ḥāratinā* [R] (Arafa et la mort de Gabalawi, interdit au Caire).
- `les-athees-militants-contemporains` : Thomas Mann, *Der Zauberberg* [DP depuis 2026] (Settembrini, l'humaniste militant) ; Anatole France, *La Révolte des anges* [DP] (l'ange qui lit la bibliothèque et refait un dieu : la loi de Stirner).

### Conclusion
- `le-bilan-des-refondations` : Saint-Exupéry, *Vol de nuit* [R] (Rivière exige le sacrifice des pilotes au courrier : l'absolu qui exige, dit par qui l'admire) ; Kafka, « In der Strafkolonie » [DP] (l'officier, prêtre d'une loi morte, finit par s'exécuter lui-même).
- `ce-que-les-exceptions-ont-en-commun` : Hesse, *Das Glasperlenspiel* [R] (Castalie, Knecht quitte l'ordre : spiritualité d'exercice sans Église) ; Pessoa, *O Guardador de Rebanhos* (Alberto Caeiro) [DP] (« Há metafísica bastante em não pensar em nada » : la position de l'immanence, sans doctrine).
- `le-soupir-sans-ciel` : Primo Levi, *Se questo è un uomo* [R] (la prière de Kuhn que Levi cracherait : la consolation refusée, le bouc émissaire) ; Steinbeck, *The Grapes of Wrath* [R] (Tom Joad, « je serai là » : le nous horizontal) ; Vigny, « Le Mont des Oliviers » [DP] (« au silence éternel de la Divinité » : la plainte sans ciel).

### Textes libres à récupérer (`tools/fetch_text.py`, puis `grep`)

Par lot, seulement ceux qu'on cite : (a) Aristophane, Dante, Leopardi, Horace, Jean de la Croix, Kafka (*Ein Landarzt*, *Der Prozess*), Silesius, Rilke, Anatole France (quatre titres), Corneille, Sienkiewicz, Lucien, Flaubert (*Tentation*), Ibsen (trad. anglaises Gutenberg), Shakespeare, Valéry, Baudelaire, Racine, Goethe (*Faust*, *Gedichte*, *Dichtung und Wahrheit*), Montesquieu, Swift, Voltaire (*Zadig*), Pope, Byron, Diderot, Sterne, Stendhal, Hugo (*Quatrevingt-treize*, *Les Misérables*, *La Légende des siècles*, *Les Contemplations*, *Religions et religion*), Shelley, Sade, Kleist ; (b) Hölderlin, Wordsworth, Jean Paul, Staël, Eliot (*Middlemarch*, poèmes), Tennyson, Proust (*Pastiches*), Barrès, Tourgueniev, Zola (*Germinal*), Heine, Maupassant, Mann (*Buddenbrooks*, *Doktor Faustus*), Melville (*Billy Budd*, *Moby-Dick*), Nerval, Swinburne ; (c) Zola (*Lourdes*, *Travail*), Kafka (*Das Schloss*, *Brief an den Vater*), Defoe, Schiller, Tolstoï (*Confession*, *Ivan Ilitch*, contes, *Guerre et Paix*), Whitman, Blake, Andersen, Péguy, Conrad, La Fontaine, Euripide, Grimm, Cervantès, Pirandello, Ovide, Hamsun, Dickens, Flaubert (*Bovary*, *Trois contes*, *Bouvard*, *Éducation*), Lamartine ; (d) Tagore, Bernanos, Homère, Sophocle, Huysmans, Dostoïevski (*L'Idiot*), Gogol, Mann (*Zauberberg*), Mary Shelley, Lessing, Boccace, Arnold, Chateaubriand ; (e) Thoreau, Wilde, Gide, Rimbaud, Khayyâm, Al-Maʿarrī, Pessoa, Vigny. Environ 125 auteurs convoqués.
