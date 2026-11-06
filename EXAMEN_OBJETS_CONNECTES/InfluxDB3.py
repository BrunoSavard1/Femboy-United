
import os
import json
import subprocess


# ============================================================
# CONFIGURATION
# ============================================================

# Serveur local
HOST_DB = "http://127.0.0.1:8181"

# Serveur du cégep
# HOST_DB = "http://10.240.2.201:8181"

# Autre serveur de test
# HOST_DB = "http://10.240.2.125:8181"

# Le programme essaie les deux noms de variables
TOKEN = (
    os.environ.get("INFLUXDB3_AUTH_TOKEN")
    or os.environ.get("SERVEUR_INFLUXDB3_AUTH_TOKEN")
)

NOM_DB = ""


# ============================================================
# FONCTIONS GÉNÉRALES
# ============================================================

def executer_commande(commande):

    try:
        resultat = subprocess.run(
            commande,
            capture_output=True,
            text=True
        )

    except FileNotFoundError:
        print("\nErreur : la commande influxdb3 est introuvable.")
        print("Vérifie que le CLI InfluxDB est installé.")
        return None

    if resultat.returncode != 0:
        print("\nErreur InfluxDB :")
        print(resultat.stderr.strip())
        return None

    return resultat.stdout.strip()


def lire_json(sortie):

    if not sortie:
        return []

    try:
        donnees = json.loads(sortie)

        if isinstance(donnees, list):
            return donnees

        if isinstance(donnees, dict):
            return [donnees]

    except json.JSONDecodeError:
        pass

    # Certains formats peuvent retourner un objet JSON par ligne
    donnees = []

    for ligne in sortie.splitlines():
        ligne = ligne.strip()

        if ligne.startswith("{") and ligne.endswith("}"):
            try:
                donnees.append(json.loads(ligne))
            except json.JSONDecodeError:
                pass

    return donnees


def proteger_nom(nom):

    # Protège un nom de table ou de colonne SQL
    return '"' + nom.replace('"', '""') + '"'


def afficher_resultats(donnees):

    if not donnees:
        print("\nAucune donnée trouvée.")
        return

    colonnes = list(donnees[0].keys())

    # Calcul de la largeur de chaque colonne
    largeurs = {}

    for colonne in colonnes:
        largeur = len(str(colonne))

        for ligne in donnees:
            largeur = max(
                largeur,
                len(str(ligne.get(colonne, "")))
            )

        largeurs[colonne] = min(largeur, 30)

    # En-tête
    print()

    for colonne in colonnes:
        print(
            str(colonne).ljust(largeurs[colonne] + 2),
            end=""
        )

    print()

    print("-" * (sum(largeurs.values()) + len(colonnes) * 2))

    # Données
    for ligne in donnees:

        for colonne in colonnes:
            valeur = str(ligne.get(colonne, ""))

            if len(valeur) > 30:
                valeur = valeur[:27] + "..."

            print(
                valeur.ljust(largeurs[colonne] + 2),
                end=""
            )

        print()

    print("\nNombre de résultats :", len(donnees))


# ============================================================
# CONNEXION ET SÉLECTION DE LA BASE
# ============================================================

def choisir_base():

    global NOM_DB

    if not TOKEN:
        print("\nErreur : aucun token InfluxDB trouvé.")
        print("Vérifie ta variable d'environnement.")
        return False

    commande = [
        "influxdb3", "show", "databases",
        "--host", HOST_DB,
        "--token", TOKEN,
        "--format", "json"
    ]

    sortie = executer_commande(commande)

    if sortie is None:
        return False

    bases_json = lire_json(sortie)

    bases = []

    for ligne in bases_json:

        nom = ligne.get("iox::database")

        if nom is None:
            nom = ligne.get("database_name")

        if nom is None:
            nom = ligne.get("name")

        if nom:
            bases.append(str(nom))

    if not bases:
        print("\nAucune base de données trouvée.")
        print(sortie)
        return False

    print("\n===== CONNEXION INFLUXDB =====")
    print("\nBases de données disponibles :")

    for i, base in enumerate(bases, 1):
        print(f"{i}. {base}")

    choix = input(
        "\nEntrer le numéro ou le nom de la base : "
    ).strip()

    base_selectionnee = None

    if choix.isdigit():

        numero = int(choix)

        if 1 <= numero <= len(bases):
            base_selectionnee = bases[numero - 1]

    else:

        for base in bases:

            if base.casefold() == choix.casefold():
                base_selectionnee = base
                break

    if base_selectionnee is None:
        print("\nBase de données introuvable.")
        return False

    NOM_DB = base_selectionnee

    print("\nConnexion configurée avec succès !")
    print("Base sélectionnée :", NOM_DB)

    return True


# ============================================================
# TABLES DISPONIBLES
# ============================================================

def obtenir_tables():

    commande = [
        "influxdb3", "query",
        "--host", HOST_DB,
        "--database", NOM_DB,
        "--token", TOKEN,
        "--format", "json",
        "SHOW TABLES"
    ]

    sortie = executer_commande(commande)

    if sortie is None:
        return []

    donnees = lire_json(sortie)

    tables = []

    for ligne in donnees:

        schema = str(ligne.get("table_schema", "")).strip()
        type_table = str(ligne.get("table_type", "")).strip()
        nom_table = ligne.get("table_name")

        if (
            schema == "iox"
            and type_table.upper() == "BASE TABLE"
            and nom_table
        ):
            tables.append(str(nom_table))

    # Évite les doublons sans modifier les majuscules
    tables_sans_doublons = []

    for table in tables:
        if table not in tables_sans_doublons:
            tables_sans_doublons.append(table)

    if not tables_sans_doublons:
        print("\nAucune table utilisateur trouvée.")
        return []

    print("\n===== TABLES DISPONIBLES =====")

    for i, table in enumerate(tables_sans_doublons, 1):
        print(f"{i}. {table}")

    return tables_sans_doublons


def choisir_table():

    tables = obtenir_tables()

    if not tables:
        return None

    choix = input(
        "\nEntrer le numéro ou le nom de la table : "
    ).strip()

    table_selectionnee = None

    if choix.isdigit():

        numero = int(choix)

        if 1 <= numero <= len(tables):
            table_selectionnee = tables[numero - 1]

    else:

        for table in tables:

            if table.casefold() == choix.casefold():
                table_selectionnee = table
                break

    if table_selectionnee is None:
        print("\nTable introuvable.")
        return None

    print("\nTable sélectionnée :", table_selectionnee)

    return table_selectionnee


# ============================================================
# STRUCTURE D'UNE TABLE
# ============================================================

def obtenir_structure(table):

    commande = [
        "influxdb3", "query",
        "--host", HOST_DB,
        "--database", NOM_DB,
        "--token", TOKEN,
        "--format", "json",
        "SHOW COLUMNS FROM " + proteger_nom(table)
    ]

    sortie = executer_commande(commande)

    if sortie is None:
        return []

    return lire_json(sortie)


def afficher_structure(table):

    print("\n===== STRUCTURE DE LA TABLE =====")
    print("Table :", table)

    colonnes = obtenir_structure(table)

    if not colonnes:
        print("\nImpossible de récupérer la structure.")
        return

    print("\nColonnes disponibles :")

    for i, colonne in enumerate(colonnes, 1):

        nom = colonne.get("column_name", "?")
        type_donnee = colonne.get("data_type", "?")

        print(f"{i}. {nom} ({type_donnee})")


# ============================================================
# CONSULTATION DES DONNÉES
# ============================================================

def valeur_sql(valeur, type_donnee):

    type_donnee = type_donnee.lower()

    if "bool" in type_donnee:

        valeur = valeur.lower()

        if valeur not in ("true", "false"):
            raise ValueError("Entre true ou false.")

        return valeur

    if any(
        type_num in type_donnee
        for type_num in ("int", "float", "double", "decimal")
    ):

        # Vérifie que la valeur est numérique
        float(valeur)
        return valeur

    # Pour les chaînes de caractères et les dates
    return "'" + valeur.replace("'", "''") + "'"


def consulter_donnees(table):

    print("\n===== CONSULTATION DES DONNÉES =====")
    print("Table :", table)

    colonnes = obtenir_structure(table)

    if not colonnes:
        print("\nImpossible de récupérer les colonnes.")
        return

    conditions = []

    # Filtres facultatifs
    while True:

        reponse = input(
            "\nAjouter un filtre ? (oui/non) : "
        ).strip().lower()

        if reponse not in ("oui", "o", "yes", "y"):
            break

        print("\nColonnes disponibles :")

        for i, colonne in enumerate(colonnes, 1):
            print(f"{i}. {colonne.get('column_name')}")

        choix_colonne = input(
            "\nChoisir une colonne (numéro ou nom) : "
        ).strip()

        colonne_selectionnee = None

        if choix_colonne.isdigit():

            numero = int(choix_colonne)

            if 1 <= numero <= len(colonnes):
                colonne_selectionnee = colonnes[numero - 1]

        else:

            for colonne in colonnes:

                nom = str(colonne.get("column_name", ""))

                if nom.casefold() == choix_colonne.casefold():
                    colonne_selectionnee = colonne
                    break

        if colonne_selectionnee is None:
            print("\nColonne introuvable.")
            continue

        nom_colonne = colonne_selectionnee["column_name"]
        type_donnee = colonne_selectionnee.get("data_type", "")

        print("\nOpérateurs disponibles :")
        print("1. =")
        print("2. !=")
        print("3. >")
        print("4. <")
        print("5. >=")
        print("6. <=")
        print("7. LIKE")
        print("8. IS NULL")
        print("9. IS NOT NULL")

        choix_operateur = input(
            "\nChoisir un opérateur : "
        ).strip()

        operateurs = {
            "1": "=",
            "2": "!=",
            "3": ">",
            "4": "<",
            "5": ">=",
            "6": "<=",
            "7": "LIKE",
            "8": "IS NULL",
            "9": "IS NOT NULL"
        }

        operateur = operateurs.get(choix_operateur)

        if operateur is None:
            print("\nOpérateur invalide.")
            continue

        nom_sql = proteger_nom(nom_colonne)

        if operateur in ("IS NULL", "IS NOT NULL"):

            condition = nom_sql + " " + operateur

        else:

            valeur = input("\nValeur à rechercher : ")

            try:

                if operateur == "LIKE":
                    valeur_sql_filtre = (
                        "'" + valeur.replace("'", "''") + "'"
                    )
                else:
                    valeur_sql_filtre = valeur_sql(
                        valeur,
                        type_donnee
                    )

                condition = (
                    nom_sql + " " + operateur + " " + valeur_sql_filtre
                )

            except ValueError:
                print("\nValeur invalide pour ce type de colonne.")
                continue

        if conditions:

            liaison = input(
                "Relier avec AND ou OR ? "
            ).strip().upper()

            if liaison not in ("AND", "OR"):
                print("Choix invalide. AND sera utilisé.")
                liaison = "AND"

            conditions.append(liaison)

        conditions.append(condition)

        print("\nFiltre ajouté :", condition)

    # Nombre de résultats
    choix_limite = input(
        "\nNombre maximal de résultats (50 par défaut) : "
    ).strip()

    if choix_limite == "":
        limite = 50
    elif choix_limite.isdigit() and int(choix_limite) > 0:
        limite = int(choix_limite)
    else:
        print("\nLimite invalide. 50 sera utilisé.")
        limite = 50

    # Construction de la requête SQL
    requete = (
        "SELECT * FROM " + proteger_nom(table)
    )

    if conditions:
        requete += " WHERE " + " ".join(conditions)

    requete += " ORDER BY time DESC LIMIT " + str(limite)

    print("\nRequête exécutée :")
    print(requete)

    commande = [
        "influxdb3", "query",
        "--host", HOST_DB,
        "--database", NOM_DB,
        "--token", TOKEN,
        "--format", "json",
        requete
    ]

    sortie = executer_commande(commande)

    if sortie is None:
        return

    donnees = lire_json(sortie)

    print("\n===== RÉSULTATS =====")
    afficher_resultats(donnees)


# ============================================================
# ÉCRITURE DE DONNÉES
# ============================================================

def echapper_cle(valeur):

    return (
        valeur.replace("\\", "\\\\")
        .replace(" ", "\\ ")
        .replace(",", "\\,")
        .replace("=", "\\=")
    )


def echapper_valeur_tag(valeur):

    return (
        valeur.replace("\\", "\\\\")
        .replace(" ", "\\ ")
        .replace(",", "\\,")
        .replace("=", "\\=")
    )


def echapper_texte(valeur):

    return (
        valeur.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", " ")
    )


def demander_type():

    print("\nType de donnée :")
    print("1. Texte")
    print("2. Entier")
    print("3. Nombre décimal")
    print("4. Booléen")

    choix = input("Choisir le type : ").strip()

    types = {
        "1": "texte",
        "2": "entier",
        "3": "decimal",
        "4": "booleen"
    }

    return types.get(choix)


def convertir_valeur_line_protocol(valeur, type_donnee):

    if type_donnee == "texte":

        return '"' + echapper_texte(valeur) + '"'

    elif type_donnee == "entier":

        int(valeur)
        return str(int(valeur)) + "i"

    elif type_donnee == "decimal":

        nombre = float(valeur)

        return repr(nombre)

    elif type_donnee == "booleen":

        valeur = valeur.lower()

        if valeur not in ("true", "false"):
            raise ValueError("Entre true ou false.")

        return valeur

    raise ValueError("Type de donnée invalide.")


def construire_ligne(table):

    # Les tags permettent de décrire le contexte de la mesure
    tags = []

    nombre_tags = input(
        "\nNombre de tags à ajouter (0 si aucun) : "
    ).strip()

    if not nombre_tags.isdigit():
        print("\nNombre invalide.")
        return None

    for i in range(int(nombre_tags)):

        print(f"\n--- TAG {i + 1} ---")

        nom = input("Nom du tag : ").strip()
        valeur = input("Valeur du tag : ").strip()

        if not nom:
            print("Nom de tag invalide.")
            return None

        tags.append(
            echapper_cle(nom)
            + "="
            + echapper_valeur_tag(valeur)
        )

    # Les champs contiennent les valeurs mesurées
    champs = []

    while True:

        print("\n--- NOUVEAU CHAMP ---")

        nom = input("Nom du champ (vide pour terminer) : ").strip()

        if nom == "":
            break

        type_donnee = demander_type()

        if type_donnee is None:
            print("\nType invalide.")
            continue

        valeur = input("Valeur : ")

        try:

            valeur_convertie = convertir_valeur_line_protocol(
                valeur,
                type_donnee
            )

        except ValueError:
            print("\nValeur invalide pour ce type.")
            continue

        champs.append(
            echapper_cle(nom) + "=" + valeur_convertie
        )

    if not champs:
        print("\nIl faut au moins un champ pour écrire des données.")
        return None

    # Construction de la ligne Line Protocol
    ligne = echapper_cle(table)

    if tags:
        ligne += "," + ",".join(tags)

    ligne += " " + ",".join(champs)

    return ligne


def ecrire_donnees(table):

    print("\n===== ÉCRITURE DE DONNÉES =====")
    print("Base :", NOM_DB)
    print("Table :", table)

    while True:

        ligne = construire_ligne(table)

        if ligne is None:
            return

        print("\nLigne qui sera envoyée :")
        print(ligne)

        confirmation = input(
            "\nConfirmer l'écriture ? (oui/non) : "
        ).strip().lower()

        if confirmation not in ("oui", "o", "yes", "y"):
            print("\nÉcriture annulée.")
            return

        commande = [
            "influxdb3", "write",
            "--host", HOST_DB,
            "--database", NOM_DB,
            "--token", TOKEN,
            ligne
        ]

        resultat = executer_commande(commande)

        if resultat is not None:
            print("\nDonnées envoyées à InfluxDB.")

        autre = input(
            "\nAjouter un autre enregistrement ? (oui/non) : "
        ).strip().lower()

        if autre not in ("oui", "o", "yes", "y"):
            break


# ============================================================
# AJOUTER UN CHAMP
# ============================================================

def ajouter_champ(table):

    print("\n===== AJOUTER UN CHAMP =====")
    print("Un champ sera ajouté en écrivant une nouvelle donnée.")
    print("Table :", table)

    nom = input("\nNom du nouveau champ : ").strip()

    if not nom:
        print("\nNom invalide.")
        return

    type_donnee = demander_type()

    if type_donnee is None:
        print("\nType invalide.")
        return

    valeur = input("Valeur du champ : ")

    try:

        valeur_convertie = convertir_valeur_line_protocol(
            valeur,
            type_donnee
        )

    except ValueError:
        print("\nValeur invalide.")
        return

    ligne = (
        echapper_cle(table)
        + " "
        + echapper_cle(nom)
        + "="
        + valeur_convertie
    )

    print("\nLigne qui sera envoyée :")
    print(ligne)

    confirmation = input(
        "\nConfirmer l'écriture ? (oui/non) : "
    ).strip().lower()

    if confirmation not in ("oui", "o", "yes", "y"):
        print("\nOpération annulée.")
        return

    commande = [
        "influxdb3", "write",
        "--host", HOST_DB,
        "--database", NOM_DB,
        "--token", TOKEN,
        ligne
    ]

    resultat = executer_commande(commande)

    if resultat is not None:
        print("\nChamp envoyé à InfluxDB.")
        print("Vérifie la structure de la table pour le voir.")


# ============================================================
# CRÉER UNE TABLE
# ============================================================

def creer_table():

    print("\n===== CRÉER UNE TABLE =====")

    nom_table = input("\nNom de la nouvelle table : ").strip()

    if not nom_table:
        print("\nNom invalide.")
        return

    tables = obtenir_tables()

    for table in tables:

        if table.casefold() == nom_table.casefold():
            print("\nUne table avec ce nom existe déjà.")
            return

    print("\nUne table InfluxDB doit avoir au moins un tag.")

    tags = input(
        "Nom(s) des tags séparés par des virgules : "
    ).strip()

    if not tags:
        print("\nIl faut au moins un tag.")
        return

    # Vérification simple des noms de tags
    liste_tags = [
        tag.strip()
        for tag in tags.split(",")
        if tag.strip()
    ]

    if not liste_tags:
        print("\nAucun tag valide.")
        return

    champs = []

    print("\nAjouter des champs à la structure ?")

    while True:

        nom = input(
            "\nNom du champ (vide pour terminer) : "
        ).strip()

        if nom == "":
            break

        print("\nType du champ :")
        print("1. Entier (int64)")
        print("2. Décimal (float64)")
        print("3. Texte (utf8)")
        print("4. Booléen (bool)")

        choix = input("Choisir le type : ").strip()

        types = {
            "1": "int64",
            "2": "float64",
            "3": "utf8",
            "4": "bool"
        }

        type_champ = types.get(choix)

        if type_champ is None:
            print("\nType invalide.")
            continue

        champs.append(nom + ":" + type_champ)

    commande = [
        "influxdb3", "create", "table",
        "--host", HOST_DB,
        "--database", NOM_DB,
        "--token", TOKEN,
        "--tags", ",".join(liste_tags)
    ]

    if champs:
        commande.extend([
            "--fields",
            ",".join(champs)
        ])

    commande.append(nom_table)

    confirmation = input(
        "\nConfirmer la création de la table ? (oui/non) : "
    ).strip().lower()

    if confirmation not in ("oui", "o", "yes", "y"):
        print("\nCréation annulée.")
        return

    resultat = executer_commande(commande)

    if resultat is not None:
        print("\nTable créée avec succès !")
        print("Nom :", nom_table)


# ============================================================
# MENU PRINCIPAL
# ============================================================

def menu_influxdb():

    table = choisir_table()

    if table is None:
        return

    while True:

        print("\n================================")
        print("         OUTIL INFLUXDB")
        print("================================")
        print("Base de données :", NOM_DB)
        print("Table actuelle :", table)
        print("--------------------------------")
        print("1. Afficher les tables")
        print("2. Changer de table")
        print("3. Consulter les données")
        print("4. Ajouter des données")
        print("5. Ajouter un champ")
        print("6. Voir la structure de la table")
        print("7. Créer une nouvelle table")
        print("8. Changer de base de données")
        print("0. Quitter")
        print("================================")

        choix = input("\nVotre choix : ").strip()

        if choix == "1":

            obtenir_tables()

        elif choix == "2":

            nouvelle_table = choisir_table()

            if nouvelle_table is not None:
                table = nouvelle_table

        elif choix == "3":

            consulter_donnees(table)

        elif choix == "4":

            ecrire_donnees(table)

        elif choix == "5":

            ajouter_champ(table)

        elif choix == "6":

            afficher_structure(table)

        elif choix == "7":

            creer_table()

        elif choix == "8":

            if choisir_base():

                nouvelle_table = choisir_table()

                if nouvelle_table is None:
                    return

                table = nouvelle_table

        elif choix == "0":

            print("\nFermeture du programme.")
            break

        else:

            print("\nChoix invalide.")


# ============================================================
# DÉMARRAGE DU PROGRAMME
# ============================================================

if __name__ == "__main__":

    if choisir_base():
        menu_influxdb()
