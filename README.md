# Sortir de la religion sans en fonder une autre ?

Version web de lecture de l'essai, pensée pour le téléphone : sommaire, parties et sections repliables, portraits, pages de titre et tableaux, thème clair, sépia ou sombre, taille de texte réglable, reprise de la lecture là où on l'avait laissée.

Le sommaire coche les sections lues (une section n'est marquée que si l'on a vu sa fin passer à l'écran), et compte les sections lues par partie ; un bouton dans l'en-tête de chaque section permet aussi de la marquer lue ou non lue à la main. Chaque section et chaque partie a un bouton qui copie son lien direct, ou ouvre le partage du téléphone. Un service worker (`sw.js`, généré par `build/build.py`) garde la page en cache ; le bouton « Lire hors connexion » du sommaire enregistre aussi toutes les images. Les balises Open Graph donnent un aperçu (titre, description, couverture) quand on partage le lien.

La loupe de la barre supérieure (raccourci « / ») cherche dans tout le texte de la page, hors connexion compris.

Quatre pages complètent l'essai, générées par `build/build.py` : `frise.html` (frise chronologique des auteurs, d'après les titres de sections et `build/auteurs.json`), `reponses.html` (qui répond à qui, d'après `build/reponses.json`, avec la distinction entre réponses attestées et confrontations construites), `lexique.html` (d'après `build/lexique.json` ; la première occurrence de chaque notion dans l'essai renvoie au lexique) et `bibliotheque.html` (les œuvres littéraires citées dans les encadrés « En littérature », classées par auteur, avec un lien vers la section qui les cite).

En ligne : https://thomasgourouza.github.io/sortir-de-la-religion/

Site statique : HTML, CSS et JavaScript sans dépendance, à part la police Literata chargée depuis Google Fonts.

## Contenu

| Chemin | Rôle |
|---|---|
| `index.html` | la page, générée ; ne pas l'éditer à la main |
| `css/style.css` | mise en page et thèmes |
| `js/app.js` | sommaire, sections repliables, thème, taille du texte, mémoire de lecture, sections lues, copie de lien, hors connexion |
| `sw.js` | service worker, généré depuis `build/sw.template.js` |
| `favicon.svg`, `apple-touch-icon.png` | icônes |
| `images/` | portraits (`auteurs/`), pages de titre (`oeuvres/`), tableaux et photographies (`art/`) |
| `build/build.py` | convertit l'essai Markdown en `index.html` |
| `build/template.html` | gabarit de la page |
| `build/images.py`, `build/images.json` | récupération des images libres sur Wikimedia Commons et leur description (légende, auteur, licence, source) |

## Reconstruire la page

L'essai source est dans le dépôt `litterature` :

```sh
python3 build/build.py ~/Documents/litterature/articles/2026-10-11-sortir-de-la-religion.md
```

Sans argument, le script prend ce chemin par défaut. Les statuts de vérification des citations sont retirés de la version web ; ils restent dans le Markdown source. Les encadrés « En littérature » sont écrits dans le Markdown comme des blocs de citation dont la première ligne est `> **En littérature.** Auteur, *Titre* (date) ; …` et le dernier paragraphe commence par `Source :` ; le script les rend en encadrés repliables (`<aside class="lettres">`), ne les compte pas dans les temps de lecture et en tire la page Bibliothèque.

Pour récupérer à nouveau les images :

```sh
python3 build/images.py
```

## Prévisualiser

```sh
python3 -m http.server 8000
```

puis ouvrir http://localhost:8000.

## Publier sur GitHub Pages

```sh
git init
git add .
git commit -m "Version web de l'essai"
git branch -M main
git remote add origin git@github.com:<utilisateur>/sortir-de-la-religion.git
git push -u origin main
```

Puis, sur GitHub : Settings, Pages, Source « Deploy from a branch », branche `main`, dossier `/ (root)`. Le fichier `.nojekyll` évite tout traitement Jekyll.

## Crédits

Les images viennent de Wikimedia Commons et sont dans le domaine public ou sous licence libre (CC0, CC BY, CC BY-SA). Auteur, licence et lien de chaque image figurent dans `build/images.json` et en fin de page, section « Sources et crédits ».
