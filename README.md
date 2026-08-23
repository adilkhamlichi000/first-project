# first-project

Ceci est mon premier projet GitHub. J’apprends à utiliser GitHub et à construire des outils avec l’IA.

## Mon premier mini-agent IA

Le fichier `agent.py` contient un mini-agent d’analyse d’actions.

Il reçoit le nom d’une entreprise, décide quelles informations rechercher sur le web, analyse les informations trouvées et rend un verdict de screening.

### 1. Ouvrir le Terminal sur Mac

Place-toi dans le dossier du projet.

### 2. Créer un environnement Python

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer le SDK Agents d’OpenAI

```bash
pip install -r requirements.txt
```

### 4. Ajouter temporairement ta clé API OpenAI

Crée une clé API dans ton compte OpenAI, puis dans le Terminal :

```bash
export OPENAI_API_KEY="TA_CLE_ICI"
```

Ne mets jamais ta vraie clé API dans un fichier GitHub ou dans le code.

### 5. Lancer l’agent

Par exemple :

```bash
python agent.py "Societe Generale"
```

Tu peux ensuite remplacer Société Générale par une autre entreprise :

```bash
python agent.py "Nvidia"
python agent.py "BNP Paribas"
```

## Ce qu’on apprend ici

Un agent est composé de :

- un modèle : `gpt-5.6-sol`
- des instructions : la mission de l’analyste
- un outil : `WebSearchTool`
- une boucle agentique : le `Runner` laisse le modèle utiliser l’outil autant que nécessaire avant de produire sa réponse finale

Le SDK Agents gère cette boucle pour nous.
