# Outils – Objets connectés

## Description

Ce projet regroupe plusieurs outils Python permettant de travailler avec différentes technologies vues dans le cours Objets connectés :

- **SQLite / SQL** : consulter, ajouter et modifier des données dans une base de données SQLite.
- **InfluxDB 3** : consulter et écrire des données dans une base de données InfluxDB.
- **Mosquitto (MQTT)** : se connecter à un broker MQTT, publier des messages et écouter les topics.

Le programme principal `core_runner.py` permet de lancer les différents outils à partir d'un seul menu.

## Installation

### 1. Télécharger le projet

Télécharger ou cloner le dépôt GitHub sur votre ordinateur.

### 2. Installer les dépendances

Créer un environnement virtuel :

```bash
python -m venv .venv
```

Activer l'environnement virtuel sous Windows :

```powershell
.venv\Scripts\activate
```

Installer les bibliothèques nécessaires :

```bash
pip install paho-mqtt influxdb3-python
```

### 3. Configuration des fichiers

**IMPORTANT :** Les fichiers ont été configurés initialement pour fonctionner avec mes propres chemins, serveurs et identifiants. Il faut donc modifier certains paramètres avant de les utiliser.

---

## Configuration SQLite / SQL

Dans le fichier `sqlite.py`, il faut modifier la variable `DOSSIER_BD` pour indiquer le répertoire où se trouvent vos bases de données `.db`.

Exemple :

```python
DOSSIER_BD = r"C:\Users\Utilisateur\Documents\MesBasesDeDonnees"

**Important :**
- Vérifier que le chemin du fichier est valide.
- Si la base de données est hébergée sur un serveur, lancer le programme directement sur ce serveur ou utiliser un accès réseau approprié.
- Le fichier `.db` doit être accessible par le programme.

## Configuration InfluxDB 3

Dans le fichier `influxdb.py`, il faut vérifier les paramètres de connexion à InfluxDB 3.

Modifier les éléments suivants selon votre installation :

- **Adresse IP** : adresse du serveur InfluxDB.
- **Port** : généralement `8181`.
- **Token** : jeton d'authentification InfluxDB.
- **Nom de la base de données** : nom de votre propre base.

Exemple :

```python
HOST = "http://127.0.0.1:8181"
TOKEN = "VOTRE_TOKEN"
DATABASE = "VOTRE_DATABASE"
```

Si InfluxDB 3 fonctionne sur votre ordinateur :

```python
HOST = "http://127.0.0.1:8181"
```

Si InfluxDB 3 fonctionne sur un serveur distant :

```python
HOST = "http://ADRESSE_IP_DU_SERVEUR:8181"
```

**Important :**
- Démarrer l'exécutable InfluxDB 3 avant de lancer le programme Python.
- Utiliser le bon token pour le serveur sélectionné.
- Vérifier que le serveur est accessible.
- Ne jamais publier son token personnel sur GitHub.

## Configuration Mosquitto (MQTT)

Dans le fichier `Mosquitto.py`, la configuration du broker se fait au lancement du programme.

Il est possible de choisir :
- Une connexion locale (`127.0.0.1`).
- Une connexion à un serveur distant avec son adresse IP.

Le programme demande également les informations d'authentification :

- Adresse IP du broker.
- Port MQTT (généralement `1883`).
- Nom d'utilisateur.
- Mot de passe.

Exemple de configuration :

```text
Adresse IP : ADRESSE_IP_DU_BROKER
Port : 1883
Nom d'utilisateur : VOTRE_UTILISATEUR
Mot de passe : VOTRE_MOT_DE_PASSE
```

Si le broker ne nécessite pas d'authentification, laisser le nom d'utilisateur vide.

**Important :**
- Il faut que le broker MQTT soit démarré et accessible.
- Les identifiants doivent être ceux fournis par l'administrateur du broker.
- Les topics accessibles dépendent des permissions accordées à votre compte.

## Lancement du programme

Une fois les configurations terminées, lancer le programme principal :

```bash
python core_runner.py
```

Le menu permet ensuite de choisir l'outil souhaité :

1. SQLite / SQL
2. InfluxDB 3
3. Mosquitto
0. Quitter

## Sécurité

Ne pas publier sur GitHub :

- Les tokens InfluxDB.
- Les mots de passe MQTT.
- Les identifiants personnels.
- Les informations confidentielles des serveurs.

Utiliser vos propres identifiants et vos propres paramètres de connexion.

## Auteur

Projet réalisé dans le cadre du cours Objets connectés – Cégep de Sherbrooke.
