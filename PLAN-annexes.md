# Plan : page « Annexes » et lexique enrichi pour *Sortir de la religion sans en fonder une autre ?*

## Contexte

L'essai suppose chez le lecteur des connaissances qu'il ne développe pas : la théorie de chaque auteur au-delà de ce que la section en retient, l'histoire du christianisme et de l'Europe (Empire romain, Constantin, Byzance et l'orthodoxie russe, Moyen Âge, Réforme et imprimerie, monarchie, laïcité), les disciplines convoquées (sociologie, psychologie, anthropologie, exégèse, philosophie analytique). Exemple déclencheur (conversation du 15 octobre 2026) : la deuxième partie passe de Celse à l'Empire chrétien en une phrase (« de Constantin à Théodose »), sans rien dire du comment ni du pourquoi de l'expansion.

L'auteur veut, **sans modifier le texte de l'essai** :

1. **Enrichir le lexique** (`lexique.html`, 48 notions de 21 à 85 mots) : définitions plus longues, davantage de notions, et un lien à la première occurrence de chaque notion **dans chaque section** (aujourd'hui une seule fois dans tout l'essai, 48 liens).
2. **Créer une page « Annexes »** (`annexes.html`) sur le modèle du lexique : des articles neutres de 400 à 700 mots (théories des auteurs, histoire, disciplines, courants), reliés à l'essai par une ligne « Pour comprendre » générée sous le titre des sections concernées et par des liens discrets dans le texte, comme le lexique.

**Décisions prises avec l'auteur le 15 octobre 2026 :**
- Rigueur des annexes : exposé neutre **sans citation** (sauf celles déjà présentes dans l'essai, recopiées d'`index.html`) ; références en fin d'article (titres et dates) ; avertissement en tête de page : ce sont des synthèses de lecture, pas des sources.
- Longueur : 400 à 700 mots par article.
- Liaison : ligne « Pour comprendre » sous le titre de section **et** liens dans le texte.
- Lexique : un lien par section (première occurrence dans chaque section).
- Nom de la page : **Annexes** (`annexes.html` ; nom sans tiret ni chiffre, exigé par la regex `/([a-z]+\.html)$/` du service worker).
- Premier lot : la mécanique, l'allongement du lexique, une dizaine d'articles d'histoire du christianisme et l'article pilote sur Girard. Les théories des auteurs suivent, partie par partie, sur plusieurs sessions.
- **Le plan s'exécute sur la machine où se trouve la source Markdown** (`~/Documents/litterature/articles/2026-10-11-sortir-de-la-religion.md`), absente de celle-ci : `python3 build/build.py` y reconstruit tout. Aucun mode de build sans la source n'est à écrire.
- Pas de tiret cadratin ni demi-cadratin nulle part ; pas de commit sans demande.

**Étape 0 de l'exécution :** copier ce plan dans le dépôt sous `PLAN-annexes.md` (à la racine, à côté de `PLAN-encadres-litteraires.md`) : l'auteur relit et versionne les plans avec le projet.

## État d'avancement

**Lot 1 exécuté le 16 octobre 2026** (aucun commit) : mécanique complète (§§ 2 à 4), lexique allongé (48 définitions de 100 à 200 mots, motifs revus : pluriels et variantes, `Inquisiteur`, `numinosum`, `Entzauberung`, `école du soupçon`, etc.), dix articles d'histoire (ids 10 à 100 de l'annexe A) et l'article pilote `theorie-mimetique`. Résultat : 374 liens de lexique dans l'essai (48 auparavant), 69 liens d'annexes, 11 articles, aucun lien dans une zone bloquée, aucun doublon par section, deux builds successifs identiques hors `?v=`.

Écarts par rapport au plan, tous minimes :
- `js/pages.js` : le masquage des listes vides ne vise plus que les `ul` enfants directs d'une carte (`.rep-carte > ul`), sinon les listes de dates des articles étaient cachées ; l'arrivée par ancre ouvre le `details` visé (le `reveal()` de `sauts.js` ne joue qu'au retour par les boutons). `js/app.js` : la ligne « Pour comprendre » est exclue de l'index de recherche.
- La ligne « Pour comprendre » n'affiche que la partie du titre avant « : », comme les titres de sections ; la page Annexes montre le titre entier.
- Les libellés « Dans l'essai » viennent des titres de sections (nom seul pour les auteurs, tête de titre sinon, « Passage (deuxième partie) » pour les passages) et des labels de parties.
- `build.py` avertit aussi quand un article sort de 400 à 700 mots.
- Le contrôle à 390 px n'a pas pu être fait (la fenêtre Chrome ne descend pas sous 500 px) ; contrôle fait à 1440 px, thème sombre, pour `annexes.html`, `lexique.html` et l'essai (Girard, Porphyre et Augustin).

**Lot 2 exécuté le 16 octobre 2026** (aucun commit) : cent notions nouvelles dans `build/lexique.json` (148 au total ; l'annexe B en prévoyait 50 à 60, mais toutes les candidates validées par comptage dans `index.html` ont été gardées, plus quelques-unes rencontrées en chemin : absolu sacrificiel, panthéisme et acosmisme, religion de l'Humanité, surhomme, immanence et transcendance, christianisme non religieux qui regroupe les motifs de Bonhoeffer) ; les sept articles d'histoire restants (ids 12 à 140) et les onze articles de disciplines (ordre 10 à 110). Résultat : 688 liens de lexique dans l'essai, 185 liens d'annexes, 29 articles, toutes les notions reliées au moins une fois, aucun lien en zone bloquée, aucun doublon par section ou par article, deux builds identiques hors `?v=`.

Choix et écarts du lot 2 :
- Motifs volontairement écartés pour cause de faux positifs : `l'Un` (« l'un musulman »), `attention`, `malheur`, `visage` seul (remplacé par `visage d'autrui`), `absurde` seul (remplacé par `l'absurde`), `traduction` seul (remplacé par `mode de la traduction`), `état d'exception` (absent du texte), `grâce` (« grâce à »), `anthropologie` seul (le mot de Feuerbach) ; `religion de l'Humanité` garde un faux positif chez Hume (« la plus ancienne religion de l'humanité »), le motif étant insensible à la casse.
- Notions à une seule section admises quand le terme est étranger ou propre à l'essai (Ataraxie, Bildungsphilister, Fable du relais, Pierre de touche, etc.), conformément à la règle d'admission.
- `judaisme-du-second-temple-a-nos-jours` et `exegese-historico-critique-et-quetes-du-jesus-historique` ne ciblent plus `deuxieme-partie`, qui aurait reçu sept articles dans sa ligne « Pour comprendre » (cinq désormais).
- Le bloc d'ouverture du bilan de la conclusion reçoit neuf liens pour quatre cents mots ; le tableau des auteurs en reçoit cinquante et un (un par terme, cellules non bloquées).
- Contrôle navigateur limité à `annexes.html` (filtre Disciplines, un article ouvert) et à `lexique.html` ; pas de contrôle à 390 px ni hors connexion.

**Lot 3 exécuté le 16 octobre 2026** (aucun commit) : les vingt et un articles de théories des auteurs des première à troisième parties (`platon-theorie` à `leibniz-theorie`, ordre 11 à 36 : dizaine = partie, unité = rang dans la partie, schéma du pilote `theorie-mimetique`, 94). Chaque article présente la pensée entière de l'auteur, non son seul usage dans l'essai, et cible sa section plus deux à quatre sections où il est discuté, sans les intros de parties. Résultat : 292 liens d'annexes dans l'essai, 50 articles, aucun avertissement, aucune cible au-delà de cinq articles (les cibles `porphyre-et-augustin`, `celse-et-origene`, `deuxieme-partie` et `troisieme-partie` ont été allégées en retirant des articles d'auteurs qui ont leur propre section).

**Lot 4 exécuté le 16 octobre 2026** (aucun commit) : les dix-sept articles de théories des auteurs des quatrième à sixième parties (`hume-theorie` à `schopenhauer-theorie`, ordre 41 à 67), mêmes règles que le lot 3. Motifs écartés pour collision : `Vie de Jésus` (Strauss et Renan), `Confessions` (Rousseau, déjà motif d'Augustin), `Abraham` (« Dieu d'Abraham » chez Pascal), `miracles`, `angoisse`, `pitié` (trop généraux) ; Renan passe par `cinquième évangile` et ses autres titres, Strauss par `Das Leben Jesu`. Résultat : 67 articles, aucun avertissement, aucune cible au-delà de cinq articles, deux builds identiques hors `?v=`.

**Lot 5 exécuté le 16 octobre 2026** (aucun commit) : les neuf articles des septième et huitième parties (`dostoievski-oeuvre`, `nietzsche-theorie`, ordre 71 et 72 ; `durkheim-theorie` à `ricoeur-theorie`, ordre 81 à 87). Motifs écartés : `Ivan` (dix-neuf sections), `Gifford` (conférences d'autres auteurs), `Marbourg` (Strauss y a étudié), `a priori`, `Œdipe`, `Moïse`, `durée` ; `rationalisation` seul remplacé par `rationalisation des conduites`, `rationalisation religieuse` et `sociologie de la rationalisation` (le mot seul visait aussi Leibniz et Otto). Résultat : 76 articles, aucun avertissement, aucune cible au-delà de cinq articles, deux builds identiques hors `?v=`.

**Lot 6 exécuté le 16 octobre 2026** (aucun commit) : les dix-huit articles des neuvième et dixième parties (`tylor-et-frazer-theorie` à `norris-et-inglehart-theorie`, ordre 91 à 99 autour du pilote 94 ; `heidegger-theorie` à `marion-theorie`, ordre 101 à 110). Motifs écartés après lecture des liens produits : `héroïsme` (Weber), `forme de vie` (Philon, Dostoïevski), `Berger` et `Inglehart` (noms d'auteurs à section), `lignée`, `converti`, `souveraineté` (Schmitt), `substitution`, `idole`, `technique`, `Critique`, `Cahiers`, `Nein`, `Dasein` (citations allemandes de Nietzsche), `dépense` (la Verschwendung de Heidegger). Résultat : 94 articles, aucun avertissement, aucune cible au-delà de cinq articles, deux builds identiques hors `?v=`.

**Lot 7 exécuté le 16 octobre 2026** (aucun commit) : les dix-huit articles des onzième et douzième parties (`schmitt-theorie` à `habermas-theorie`, ordre 111 à 119 ; `hadot-theorie` à `onfray-theorie`, ordre 121 à 129). Motifs écartés : `Athènes et Jérusalem` (thème général), `Philosophie`, `Mémoires`, `existentielle`, `Sagesse des Modernes` (deux auteurs) ; `Glauben und Wissen` retiré aussi de `hegel-theorie`, le titre étant partagé avec Habermas. Résultat : 112 articles, aucun avertissement, aucune cible au-delà de cinq articles, deux builds identiques hors `?v=`.

**Lot 8 exécuté le 16 octobre 2026** (aucun commit) : les quatorze articles de courants et doctrines (`platonisme-et-neoplatonisme` à `spiritualites-contemporaines`, ordre 10 à 140). Motifs écartés : `mystique` et `mystiques` (vingt-sept sections), `méditation` (les Méditations de Descartes), `sceptique` et `scepticisme` (le scepticisme du vicaire, de Hume, des mythistes), `Académie`, `Marcel`, `marxiste`, `Hölderlin` (déjà motif de Heidegger). Résultat : 126 articles (17 d'histoire, 11 de disciplines, 84 de théories dont le pilote et les articles collectifs, 14 de courants), 589 liens d'annexes dans l'essai, 688 liens de lexique, aucun avertissement, aucune cible au-delà de cinq articles, deux builds identiques hors `?v=`.

**Revue du 16 octobre 2026** : dix relectures indépendantes de tous les articles et des cent nouvelles définitions, confrontées à CLAUDE.md et à index.html. Une trentaine d'erreurs de fait corrigées (dates, attributions, titres), une quarantaine de déformations de l'essai rétablies (statuts attesté ou construit, verdicts, mentions prêtées à l'essai qu'il ne fait pas), une soixantaine de motifs retirés ou précisés après constat de faux positifs dans l'essai construit (Tractatus vers Wittgenstein depuis Spinoza, Émile vers Rousseau depuis Durkheim, Encyclopédie vers Hegel depuis Voltaire, Confessions vers Augustin depuis Rousseau, etc.), première personne et citations déguisées retirées, longueurs ramenées dans les fourchettes. Après revue : 669 liens de lexique, 473 liens d'annexes, aucun avertissement. Restent à l'auteur : l'italique des titres dans le corps des articles (fait dans onze articles seulement), la relecture finale des dates non contestées, et reponses.json à compléter pour les échanges Otto et Schleiermacher, Otto et James, Barth et Schleiermacher que l'essai donne pour attestés.

**Finitions du 16 octobre 2026, après la revue** : titres d'œuvres mis en italique dans le corps des cent vingt-six articles (943 italiques, par sept passes vérifiées : seuls des astérisques ajoutés, en-têtes et sous-titres intacts) ; les titres d'articles courts restent en romain, faute de guillemets autorisés ; `reponses.json` complété des deux réponses d'Otto, à Schleiermacher et à James, que l'essai donne pour attestées (74 échanges, 60 attestés, 14 construits, compte mis à jour dans CLAUDE.md) ; `build.py` : la compilation des motifs est mise en cache entre les appels de `lier`, ce qui ramène le build de plus d'une minute à trois secondes sans changer la sortie.

**Correctif du 16 octobre 2026** : les liens d'un article vers un autre article de la même page (annexes.html#…) ne faisaient que changer l'ancre, sans ouvrir l'article cible ; `js/pages.js` écoute désormais `hashchange`, ouvre et met en évidence la cible, lève le filtre qui la masquerait et la fait défiler en vue. Vérifié dans le navigateur (Herméneutique vers Chrétienté médiévale), ainsi que l'arrivée sur l'essai depuis « Dans l'essai ».

**Le plan est exécuté en entier.** Restent, à la charge de l'auteur : la relecture des articles, le commit, et deux contrôles que la session n'a pas pu faire, l'affichage à 390 px et la page Annexes hors connexion après rechargement.

## Principe technique

Un fichier Markdown par article, rendu par les fonctions de `build.py` déjà écrites ; une page outil de plus produite par `page_outil` ; une seule passe de liaison généralisée (lexique et annexes, par section). Aucune dépendance nouvelle, aucun JavaScript nouveau.

### 1. Les articles : `build/annexes/<id>.md`

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
- Corps : paragraphes, listes `- `, tableaux `|`, citations `>`, `**gras**`, `*italique*`, et des sous-titres `#### ` (nouveau, voir § 2). Pas de backticks ni de crochets longs : `masquer_statuts` (build.py l. 41-56) les retire.
- Liens vers l'essai, le lexique ou une autre annexe : inutiles à la main, la passe de liaison du § 2 les pose ; `[texte](#id)` reste possible pour une ancre interne à la page.

### 2. `build/build.py`

Références de lignes : état du fichier au 15 octobre 2026 (commit 186ce46).

**a. Lecture des annexes** : nouvelle fonction `charger_annexes()` qui lit `build/annexes/*.md` triés, analyse l'en-tête (regex `^([a-z]+):\s*(.*)$` ligne à ligne entre les deux `---`), découpe les champs à ` ; `, et renvoie une liste de dicts `{id, titre, categorie, ordre, sections, motifs, references, lignes}`. Avertir (`print`, comme l. 479-480) si `categorie` est inconnue, si un id de `sections` n'est pas dans `ids`, ou si un en-tête manque.

**b. Rendu d'un article** : `rendre_annexe(a)` : découper `a["lignes"]` sur les lignes `#### ` (chaque morceau passe par `rendre_blocs`, l. 148-168 ; le sous-titre devient `<h3>`), puis produire :

```html
<details class="annexe" data-item data-type="histoire" id="constantin-et-theodose"><summary><span class="annexe-titre">…</span><span class="annexe-cat">Histoire</span></summary><div class="annexe-corps">…corps…<p class="annexe-essai">Dans l'essai : <a href="index.html#porphyre-et-augustin">Porphyre et Augustin</a> · <a href="index.html#deuxieme-partie">Deuxième partie</a></p><p class="annexe-refs">Pour aller plus loin : …</p></div></details>
```

Le libellé des liens « Dans l'essai » vient de `infos` (titre de section via `analyser_titre`, nom seul pour les auteurs) ou du titre de partie ; construire un dict `id → libellé` à partir de `infos` et des parties dans `construire`.

**c. Page `annexes.html`** : dans `pages_outils` (l. 394-516), après le lexique, sur le modèle de `reponses.html` (l. 439-473) : quatre blocs `<section class="rep-carte annexes-groupe" data-groupe id="annexes-<categorie>"><h2>Théories des auteurs</h2>…</section>` dans l'ordre `theories, histoire, disciplines, courants`, articles triés par `(ordre, slug_terme(titre))` ; filtres identiques à ceux de `reponses.html` : champ `data-filtre-texte` et chips `data-filtre-type` (`tous`, `theories`, `histoire`, `disciplines`, `courants`). `js/pages.js` (`apply`, l. 36-58) fait déjà tout : texte normalisé, `data-type`, groupes vides masqués, `#aucun`. Intro de la page : « N articles pour lire l'essai. » Appel : `page_outil("annexes.html", "Annexes", intro, "Repères pour lire l'essai.", contenu, titre, og_image, version)`.

**d. Liaison généralisée** : remplacer `lier_lexique(h)` (l. 303-333) par `lier(h, cibles, scope_self=None)` où `cibles` est une liste de `(slug, page, motifs, classe)` : les entrées du lexique (`page="lexique.html"`, classe `lex`) **puis** les annexes (`page="annexes.html"`, classe `ann`). Changements par rapport au code actuel :
  - `faits` devient un ensemble de couples `(scope, slug)`. Le scope courant est mis à jour quand une balise `<details class="section…" id="X"` ou `<details class="partie" id="X"` est rencontrée dans la boucle sur `morceaux` (regex `<details class="(?:section|partie)[^"]*" id="([^"]+)"`). Texte hors de toute `details` : scope `""`. Résultat : une occurrence par terme et par section (intro de partie comprise, qui a son propre scope).
  - La liste des balises bloquantes (l. 316) reste : `a, summary, figcaption, h1-h4, th, button, aside` ; les motifs d'annexes ne peuvent donc pas tomber dans un lien de lexique déjà posé.
  - `title` : « Voir le lexique » ou « Voir les annexes ».
  - `scope_self` : quand on relie le corps d'une annexe ou d'une définition de lexique, exclure la cible elle-même.
  - Appels : `corps_html = lier("\n".join(corps), cibles)` (l. 628, inchangé dans l'esprit) ; dans `pages_outils`, les définitions du lexique passent par `lier(en_ligne(definition), cibles_annexes_seulement, scope_self=slug)` et le corps de chaque annexe par `lier(corps, cibles, scope_self=id)`. Chaque entrée ou article est son propre scope.

**e. Ligne « Pour comprendre »** : dans `construire`, après avoir chargé les annexes, construire `par_cible = {id_section_ou_partie: [annexes]}`. Dans `secs_html.append(...)` (l. 598-604), insérer en tête de `<div class="sec-body">` : `<p class="annexes-ligne">Pour comprendre : <a href="annexes.html#id">Titre</a> · <a …>…</a></p>` suivi de `\n` quand la section a des annexes (ordre : celui du fichier, `ordre` puis titre). Même chose pour les parties en tête de `<div class="part-body">` (l. 610). Les recettes `grep -n 'id="…"'` de `CLAUDE.md` restent valables (la ligne commence toujours par `<details`).

**f. Navigation** : ajouter `("annexes.html", "Annexes")` au tuple de `page_outil` (l. 365-367), entre Lexique et Bibliothèque.

**g. `construire` renvoie aussi `annexes`** (liste chargée) pour `pages_outils`, et `pages_outils` reçoit `annexes` en paramètre. Le lexique passe à l'intro : « N notions de l'essai. »

### 3. Gabarits et service worker

- `build/template.html` l. 82 (`drawer-outils`) et l. 102 (`hero-outils`) : ajouter `<a class="chip" href="annexes.html">Annexes</a>` et `· <a href="annexes.html">Annexes</a>` entre Lexique et Bibliothèque.
- `build/sw.template.js` l. 6-18 (`SHELL`) : ajouter `"annexes.html"`.
- `README.md` l. 9 : « Cinq pages… » et `annexes.html` (d'après `build/annexes/*.md`) ; tableau « Contenu » : une ligne pour `build/annexes/`. `CLAUDE.md` : « Mécanique du site » (fichiers générés, éditables, format d'un article d'annexe, catégories, lien par section), « Autres index » (ajouter `build/annexes/`), et la phrase sur `lexique.json` (un lien par section).

### 4. `css/style.css`

Près de `a.lex` (l. 286-288) et des styles du lexique (l. 324-330) :

```css
a.lex, a.ann { color: inherit; text-decoration: underline dotted var(--accent); text-underline-offset: 3px; }
a.lex:hover, a.ann:hover { color: var(--accent); }
.annexes-ligne { font: 13px/1.5 var(--sans); color: var(--ink-soft); margin: 0 0 1em; }
.annexes-ligne a { color: var(--accent); text-decoration: none; }
.annexe { border-bottom: 1px solid var(--line); }
.annexe > summary { padding: 10px 0; cursor: pointer; display: flex; gap: 10px; align-items: baseline; }
.annexe-titre { font-weight: 600; }
.annexe-cat { font: 11.5px var(--sans); color: var(--accent); text-transform: uppercase; letter-spacing: .04em; margin-left: auto; }
.annexe-corps { padding: 0 0 12px; }
.annexe-corps h3 { font-size: 1.05em; margin: 1em 0 .3em; }
.annexe-essai, .annexe-refs { font: 13px/1.5 var(--sans); color: var(--ink-soft); }
.annexe.cible { background: var(--accent-soft); }
```

Vérifier que les variables (`--sans`, `--ink-soft`, `--line`, `--accent`, `--accent-soft`) existent dans les quatre thèmes (l. 6-39) et qu'aucune règle générale sur `details`/`summary` des sections de l'essai ne déborde sur `.annexe` (scoper si besoin, comme pour `.lettres`).

Arrivée par ancre (`annexes.html#id`) : `js/sauts.js` `reveal()` ouvre les `details` ancêtres ; `js/pages.js` l. 69-73 pose la classe `cible`. Rien à écrire.

### 5. `build/lexique.json`

- Schéma inchangé (`terme`, `langue?`, `motifs`, `section`, `definition`) ; les définitions acceptent déjà `*italique*`, `**gras**` et `[texte](#id)`.
- **Allonger les 48 définitions** à 100 à 200 mots : la définition ; l'origine (auteur, œuvre, date, mot original) ; ce que l'essai en fait (sans verdict nouveau : reprendre celui de la section) ; un renvoi « Voir aussi » aux notions voisines quand il y en a (la liaison automatique vers les annexes fait le reste).
- **Revoir les motifs** : ajouter les pluriels et variantes courantes (`religions séculières` existe déjà ainsi ; faire de même pour `Grand Inquisiteur` / `Inquisiteur`, `numineux` / `numinosum`, etc.), en vérifiant chaque motif par `grep -c` dans `index.html` pour éviter les faux positifs (un motif trop court comme « exception » ou « sacré » seul est à proscrire : garder « Sacré » seulement avec les motifs précis déjà en place).
- **Ajouter des notions** (liste en annexe B, à valider motif par motif contre `index.html`). Règle d'admission : un terme que l'essai emploie comme vocabulaire propre ou technique, qui apparaît dans au moins deux sections ou qui est en langue étrangère, et dont le motif peut être relié sans faux positif. Ce qui demande plus de 200 mots est une annexe, pas une notion.

## Règles d'écriture des annexes

- **Voix** : troisième personne, neutre, au présent. Aucun « je ». Aucun verdict sur la thèse de l'essai ; on peut écrire « l'essai mobilise cette notion dans… » (factuel), pas « l'essai a raison de… ».
- **Plan d'un article** (400 à 700 mots) : chapeau de deux phrases (qui, quand, quoi) ; contexte (d'où cela vient, contre quoi) ; la théorie ou la période en trois à cinq idées, avec des sous-titres `#### ` si l'article dépasse 500 mots ; un dernier paragraphe « Ce que l'essai suppose » qui nomme les faits et les termes que l'essai emploie sans les expliquer ; pour l'histoire, une liste de dates clés.
- **Sans citation** : aucun guillemet, sauf une formule déjà citée par l'essai, recopiée d'`index.html` (`grep`), jamais de mémoire. Les références de fin d'article donnent des titres et des dates, pas des pages.
- **Prudence factuelle** : dates et faits de culture générale établie ; en cas de doute, « vers », ou omettre. Les théories d'auteur sont présentées comme l'auteur les présente, pas comme l'essai les juge (c'est le sens de « de manière neutre » demandé pour Girard : la théorie mimétique dans son ensemble, du roman à l'économie, pas seulement son usage religieux).
- **Champ `sections`** : la section de l'auteur, plus les sections et parties où l'article aide vraiment (pas plus de quatre ou cinq cibles par article, sinon la ligne « Pour comprendre » devient un sommaire).
- **Champ `motifs`** : deux à six motifs précis, propres au sujet (`théorie mimétique`, `édit de Milan`, `concile de Nicée`), jamais le seul nom d'un auteur qui a sa section (il apparaît des centaines de fois ; la ligne « Pour comprendre » de sa section suffit).
- Pas de tiret cadratin ; pas de backticks ni de crochets longs ; titres d'œuvres en italique, en langue originale à la première mention puis titre français reçu.

## Déroulement

1. **Préparation** (machine avec la source) : copier le plan en `PLAN-annexes.md` ; `python3 build/build.py` ; `git diff --stat` doit être vide hors horodatage `?v=` (sinon, régler d'abord l'écart).
2. **Mécanique** : §§ 2 à 4 avec deux articles d'essai (`constantin-et-theodose`, `theorie-mimetique`) ; build ; contrôle visuel sur `python3 -m http.server 8000` (1440 px et 390 px, thème sombre) : ligne « Pour comprendre » sous Girard et sous Porphyre et Augustin, liens pointillés dans le texte, page Annexes repliée puis ouverte, filtres, arrivée par ancre depuis l'essai, retour « Dans l'essai ».
3. **Lexique** : allonger les 48 définitions, revoir les motifs ; build ; compter les `class="lex"` (attendu : plusieurs centaines) et lire une section au hasard pour vérifier qu'aucun paragraphe n'est saturé.
4. **Lot 1, histoire** (dix articles, annexe A, catégorie histoire, ids 10 à 100) et `theorie-mimetique` finalisé ; build ; relecture d'un article sur deux dans le navigateur.
5. **Lots suivants**, une session chacun : lot 2 (notions nouvelles du lexique, reste de l'histoire, disciplines) ; lots 3 à 7 (théories des auteurs, parties 1-3, 4-6, 7-8, 9-10, 11-12) ; lot 8 (courants et doctrines). Chaque lot : rédaction, build, relecture, bilan.
6. **Finition** : README, CLAUDE.md, remplacement de `PLAN-annexes.md` par la version à jour. Bilan à l'auteur : nombre d'articles, de notions, de liens ; rappel qu'aucun commit n'a été fait.

## Vérification

- `python3 -m py_compile build/build.py` ; `python3 build/build.py` deux fois de suite : sortie identique hors `?v=` ; aucun avertissement (section inconnue, catégorie inconnue, en-tête manquant).
- `grep -c '<a class="lex"' index.html` et `grep -c '<a class="ann"' index.html` : le premier passe de 48 à plusieurs centaines ; aucun lien dans un `<summary>`, un `<figcaption>`, un `<aside class="lettres">` ou un `<a>` (vérifier par un petit script Python qui rejoue le découpage de `lier` et compte les liens par zone).
- Pour chaque section, au plus un lien par terme : script qui, pour chaque `<details class="section">`, compte les `href` de lexique et d'annexes et signale tout doublon.
- `grep -o 'annexes.html#[^"]*' index.html | sort -u` : toutes les ancres existent dans `annexes.html` ; `grep -o 'index.html#[^"]*' annexes.html | sort -u` : tous les ids existent dans `index.html`.
- `grep -nP '[\x{2013}\x{2014}]' build/annexes/*.md build/lexique.json build/build.py css/style.css README.md CLAUDE.md` : aucun résultat.
- Longueur : script qui compte les mots de chaque `build/annexes/*.md` hors en-tête et signale ceux hors 400 à 700.
- Navigateur : `annexes.html` et `lexique.html` sur les trois thèmes et à 390 px ; recherche plein texte de l'essai (`/`) sur un mot d'une ligne « Pour comprendre » ; hors connexion après rechargement : `annexes.html` servie par le service worker.

## Annexe A : inventaire des annexes

Format : `id` : titre ; sections cibles principales. Les ids sont les noms de fichiers. Environ 130 articles.

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

## Annexe B : notions candidates pour le lexique (lot 2)

À valider une à une : le motif doit exister dans `index.html` (`grep -c`) et ne pas produire de faux positifs. Format : terme [section d'ancrage]. Environ 70 ; en retenir 50 à 60.

- Vocabulaire de l'essai : loi des refondations [these] ; refondation stricte et refondation douce [these] ; réponse attestée et confrontation construite [huit-regimes-de-la-critique] ; fable du relais [prologue] ; athées du marché [nietzsche] ; pierre de touche [le-bilan-des-refondations] ; spiritualité d'exercice [ce-que-les-exceptions-ont-en-commun] ; offrande de soi [le-bilan-des-refondations] ; soupir sans ciel [le-soupir-sans-ciel] ; besoin et disposition [neuvieme-partie] ; étonnement sans dette [pourquoi-y-a-t-il-quelque-chose-plutot-que-rien-un-debat-construit] ; Dieu des philosophes [pascal] ; platonisme pour le peuple [deuxieme-partie].
- Antiquité et Moyen Âge : periagôgê [platon] ; sôphronistêrion [platon] ; moteur immobile [aristote] ; noêsis noêseôs [aristote] ; ataraxie [epicure-et-lucrece] ; l'Un [plotin] ; taʾwīl [averroes] ; Gelassenheit [maitre-eckhart] ; allégorie [philon-d-alexandrie] ; Logos spermatikos [justin-martyr] ; critère d'embarras [jesus-a-t-il-existe-le-jesus-de-l-histoire-et-la-these-mythiste].
- Âge classique et Lumières : pari de Pascal [pascal] ; Dieu caché [pascal] ; Deus sive Natura [spinoza] ; amour intellectuel de Dieu [spinoza] ; béatitude [spinoza] ; asylum ignorantiae [spinoza] ; société d'athées [bayle] ; meilleur des mondes [leibniz] ; principe de raison suffisante [pourquoi-y-a-t-il-quelque-chose-plutot-que-rien-un-debat-construit] ; religion naturelle [hume] ; mal radical [kant] ; Afterdienst [kant] ; postulats de la raison pratique [kant].
- XIXe siècle : Anschauung und Gefühl [friedrich-schleiermacher] ; représentation et concept [georg-wilhelm-friedrich-hegel] ; Vendredi saint spéculatif [georg-wilhelm-friedrich-hegel] ; Bildungsphilister [david-friedrich-strauss-et-bruno-bauer] ; Gattung [ludwig-feuerbach] ; Homo homini Deus [ludwig-feuerbach] ; Spuk [max-stirner] ; athées pieux [max-stirner] ; fétichisme de la marchandise [karl-marx-et-friedrich-engels] ; Protestation [karl-marx-et-friedrich-engels] ; stades de l'existence [soren-kierkegaard] ; loi des trois états [auguste-comte] ; Grand-Être [auguste-comte] ; vouloir-vivre [arthur-schopenhauer] ; polyphonie [dostoievski] ; tout est permis [dostoievski] ; volonté de vérité [nietzsche] ; idéal ascétique [nietzsche] ; ressentiment [nietzsche].
- Sciences de la religion : effervescence collective [durkheim] ; représentation collective [durkheim] ; habitacle d'acier [weber] ; polythéisme des valeurs [weber] ; sacrifice de l'intellect [weber] ; once-born et twice-born [william-james] ; over-beliefs [william-james] ; mysterium tremendum [rudolf-otto] ; névrose obsessionnelle universelle [freud] ; dieu Logos [freud] ; fonction fabulatrice [bergson] ; âme close et âme ouverte [bergson] ; survivances [tylor-et-frazer] ; archétype [jung] ; individuation [jung] ; crise mimétique [girard] ; système héroïque [becker] ; terror management theory [becker] ; canopée sacrée [berger-et-luckmann] ; structures de plausibilité [berger-et-luckmann] ; religion invisible [berger-et-luckmann] ; lignée croyante [hervieu-leger] ; concept minimalement contre-intuitif [boyer] ; sécurité existentielle [norris-et-inglehart] ; option vivante, forcée, capitale [a-t-on-le-droit-de-croire-clifford-james-et-la-philosophie-analytique] ; épistémologie réformée [a-t-on-le-droit-de-croire-clifford-james-et-la-philosophie-analytique].
- XXe siècle : causa sui [heidegger] ; dire et montrer [wittgenstein] ; différence qualitative infinie [barth] ; positivisme de la révélation [bonhoeffer] ; Dieu bouche-trou [bonhoeffer] ; monde devenu majeur [bonhoeffer] ; décréation [simone-weil] ; attention [simone-weil] ; malheur [simone-weil] ; expérience intérieure [bataille] ; absurde [camus] ; révolte [camus] ; pensée de midi [camus] ; divinisation de l'histoire [camus] ; visage [levinas] ; état d'exception [carl-schmitt] ; gnose [voegelin-et-aron] ; immanentisation de l'eschaton [voegelin-et-aron] ; affirmation de soi [hans-blumenberg] ; absolutisme théologique [hans-blumenberg] ; art d'écrire [leo-strauss] ; hétéronomie [marcel-gauchet] ; religion de la sortie de la religion [marcel-gauchet] ; cadre immanent [charles-taylor] ; humanisme exclusif [charles-taylor] ; traduction [jurgen-habermas] ; souci de soi [michel-foucault] ; moment cartésien [michel-foucault] ; chiffres [jaspers] ; période axiale [jaspers] ; unselfing [iris-murdoch] ; nirvâna [le-bouddhisme-des-philosophes] ; athée fidèle [andre-comte-sponville] ; transcendance horizontale [luc-ferry] ; Homme-Dieu [luc-ferry] ; impensé [l-islam-devant-la-sortie-de-la-religion] ; chrétien athée [les-athees-militants-contemporains].

## Annexes bibliques (17 octobre 2026)

Vingt-deux articles de catégorie `bible` ajoutés (inventaire en annexe A), tous entre 400 et 700 mots, relus : faits, dates, neutralité, absence de citation, conformité de « Ce que l'essai suppose » au texte de l'essai. Les cibles `sections` ont été élaguées pour qu'aucune ligne « Pour comprendre » ne dépasse neuf renvois. La passe de liaison résout désormais les chevauchements en faveur du motif le plus long, et prend pour chaque cible sa vraie première occurrence. Liens vers les annexes dans l'essai : 408 avant, 463 après.
