# Consignes communes : script du podcast vidéo

Podcast vidéo d'une heure au plus, en français, un seul narrateur (voix de synthèse ElevenLabs « Nicolas », modèle eleven_multilingual_v2), tiré de l'essai `texte/sortir-de-la-religion.md` (Thomas Gourouza). Ce n'est pas une lecture mais une réécriture condensée pour l'oreille. Lire d'abord `CLAUDE.md` (carte de l'essai, termes, verdicts, réserves), puis les parties à traiter dans le Markdown source (lire le texte réel, ne pas se contenter de la carte).

## Format du fichier

```
## <titre de partie, recopié À L'IDENTIQUE depuis texte/sortir-de-la-religion.md>

<narration d'ouverture de la partie : 2 à 4 phrases qui annoncent l'enjeu>

### <titre de section, recopié À L'IDENTIQUE, dates et formule comprises>

<narration de la section>
```

- Les titres `##` et `###` doivent être des copies exactes des titres du Markdown (ils servent d'identifiants pour la vidéo). Ne jamais inventer de titre.
- On n'est pas obligé de narrer toutes les sections : regrouper ou omettre les moins importantes (elles restent visibles dans la table des matières de la vidéo). Les sections « Passage » et « Bilan » peuvent être fondues dans la dernière section narrée ou omises. Chaque section narrée : 60 à 250 mots.
- Respecter le budget de mots indiqué pour chaque partie (à 10 % près). Compter avec `wc -w`.

## Écrire pour l'oreille, avec émotion

- Phrases courtes ou moyennes, rythme varié, ton vivant de conteur passionné, pas de ton de manuel : questions rhétoriques, contrastes, moments de tension (Ivan qui rend son billet, Rousseau qui condamne à mort, l'insensé de Nietzsche), moments de calme (Spinoza, Plotin). Un récit qui avance : relier chaque section à la question directrice et à la loi des refondations.
- Pas de parenthèses, pas de références (pas de « § 344 », « V, 23 », numéros de pages), pas de notes. Dire les dates en toutes lettres seulement si utile (« en 1841 » est bien).
- Citations : en français seulement (la traduction donnée par l'essai), annoncées clairement (« Stirner écrit : ... »). Exceptions permises, très rares, pour une formule célèbre courte suivie de sa traduction (« Unsere Atheisten sind fromme Leute », Deus sive Natura, amor fati).
- Pauses : insérer `<break time="1.2s" />` (entre 0.8s et 2s) juste après une idée importante, une citation forte ou un verdict, pour laisser le temps de digérer. Environ une pause tous les 80 à 120 mots, pas plus. Jamais deux pauses d'affilée.
- Jamais de tiret cadratin (—) ni demi-cadratin (–), ni de liste à puces, ni de Markdown dans la narration (pas d'italique, pas de gras). Guillemets français « ».

## Fidélité à l'essai

- Distinguer ce que dit un auteur, et le verdict de l'essai (dit comme celui de l'auteur de l'essai : « l'essai tranche », « verdict : », ou à la première personne en citant l'auteur : « je ne connais pas de texte qui illustre plus exactement mon critère », dit l'essai). Ne rien ajouter que l'essai ne dit pas.
- Employer les termes de l'essai : loi des refondations, critère du sacrifice, refondation stricte et douce, exception, allié, spiritualité d'exercice, régimes de la critique, pierre de touche, Grand Inquisiteur.
- Pour les débats, dire quand c'est une réponse réelle (« Marx lui répond ») et quand c'est l'essai qui les confronte (« l'essai les met face à face »).
- Respecter les réserves (Heidegger cité de seconde main, Arkoun et Bidar non lus, etc.) quand on cite ces auteurs : une demi-phrase suffit.
