
import sqlite3
from pathlib import Path
import os

# ==========================================
# CONFIGURATION SQLITE
# ==========================================

# Chemin du dossier contenant les bases de données
# À MODIFIER PENDANT L'EXAMEN SI NECESSAIRE

DOSSIER_BD = r"C:\Users\Bruno\Documents\objet_connect\EXAMEN_OBJETS_CONNECTES"

# Exemple de chemin sur le serveur :
# DOSSIER_BD = "/home/professeur/examen"

# Exemple de chemin sur ton ordinateur :
# DOSSIER_BD = r"C:\Users\Bruno\Documents\objet_connect\EXAMEN_OBJETS_CONNECTES"


# ==========================================
# FONCTIONS GENERALES
# ==========================================

# Comparer deux textes sans tenir compte des majuscules
def comparer_texte(texte1, texte2):
    return texte1.strip().casefold() == texte2.strip().casefold()


# Proteger les noms des tables et des colonnes
def proteger_nom(nom):
    return '"' + nom.replace('"', '""') + '"'


# Trouver le vrai nom d'une colonne
def trouver_colonne(connexion, table, nom_recherche):

    colonnes = obtenir_colonnes(connexion, table)

    for colonne in colonnes:
        if comparer_texte(colonne, nom_recherche):
            return colonne

    return None


def connexion_base():

    print("\n===== CONNEXION SQLITE =====")

    # Afficher les bases de données disponibles
    fichiers = [
        fichier for fichier in os.listdir(DOSSIER_BD)
        if fichier.lower().endswith(".db")
    ]

    if not fichiers:
        print("Aucune base de données trouvée.")
        return None

    print("\nBases de données disponibles :")

    for i, fichier in enumerate(fichiers, 1):
        print(f"{i}. {fichier}")

    choix = input("\nChoisir une base de données : ")

    if not choix.isdigit() or not 1 <= int(choix) <= len(fichiers):
        print("Choix invalide.")
        return None

    fichier = fichiers[int(choix) - 1]

    # Construire le chemin complet
    chemin = os.path.join(DOSSIER_BD, fichier)

    try:
        connexion = sqlite3.connect(chemin)

        print("\nConnexion réussie !")
        print("Base de données :", fichier)

        return connexion

    except sqlite3.Error as erreur:
        print("Erreur de connexion :", erreur)
        return None


# ==========================================
# OBTENIR LES TABLES
# ==========================================

def obtenir_tables(connexion):

    curseur = connexion.cursor()

    curseur.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
    """)

    return [ligne[0] for ligne in curseur.fetchall()]


# ==========================================
# CHOISIR UNE TABLE
# ==========================================

def choisir_table(connexion):

    tables = obtenir_tables(connexion)

    if not tables:
        print("Aucune table trouvée.")
        return None

    print("\n===== TABLES DISPONIBLES =====")

    for i, table in enumerate(tables, 1):
        print(f"{i}. {table}")

    choix = input("\nChoisir une table (numéro ou nom) : ").strip()

    if choix.isdigit():

        numero = int(choix)

        if 1 <= numero <= len(tables):
            return tables[numero - 1]

    for table in tables:

        if comparer_texte(table, choix):
            return table

    print("Table introuvable.")
    return None


# ==========================================
# OBTENIR LES COLONNES
# ==========================================

def obtenir_colonnes(connexion, table):

    curseur = connexion.cursor()

    curseur.execute(
        "PRAGMA table_info(" + proteger_nom(table) + ")"
    )

    return [ligne[1] for ligne in curseur.fetchall()]


# ==========================================
# AFFICHER LA STRUCTURE
# ==========================================

def afficher_structure(connexion, table):

    curseur = connexion.cursor()

    curseur.execute(
        "PRAGMA table_info(" + proteger_nom(table) + ")"
    )

    resultats = curseur.fetchall()

    print("\n===== STRUCTURE DE LA TABLE =====")

    for colonne in resultats:

        print(
            f"Nom : {colonne[1]} | "
            f"Type : {colonne[2]} | "
            f"Clé primaire : {colonne[5]}"
        )


# ==========================================
# CHOISIR DES COLONNES
# ==========================================

def choisir_colonnes(connexion, table):

    colonnes = obtenir_colonnes(connexion, table)

    print("\n===== COLONNES DISPONIBLES =====")

    for i, colonne in enumerate(colonnes, 1):
        print(f"{i}. {colonne}")

    print("\nÉcrire * pour toutes les colonnes.")
    print("Exemple : 1,2,3 ou Time_Stop, Inspecteur")

    choix = input("\nColonnes à sélectionner : ").strip()

    if choix == "*":
        return "*"

    selection = []

    elements = [element.strip() for element in choix.split(",")]

    for element in elements:

        if element.isdigit():

            numero = int(element)

            if 1 <= numero <= len(colonnes):
                colonne = colonnes[numero - 1]
            else:
                print("Numéro de colonne invalide.")
                return None

        else:

            colonne = trouver_colonne(connexion, table, element)

            if colonne is None:
                print("Colonne introuvable :", element)
                return None

        if colonne not in selection:
            selection.append(colonne)

    return ", ".join(proteger_nom(colonne) for colonne in selection)


# ==========================================
# CHOISIR UNE COLONNE POUR UN FILTRE
# ==========================================

def choisir_colonne_filtre(connexion, table):

    colonnes = obtenir_colonnes(connexion, table)

    print("\nColonnes disponibles :")

    for i, colonne in enumerate(colonnes, 1):
        print(f"{i}. {colonne}")

    choix = input("\nColonne à filtrer (numéro ou nom) : ").strip()

    if choix.isdigit():

        numero = int(choix)

        if 1 <= numero <= len(colonnes):
            return colonnes[numero - 1]

    else:

        colonne = trouver_colonne(connexion, table, choix)

        if colonne is not None:
            return colonne

    print("Colonne introuvable.")
    return None


# ==========================================
# CONSTRUIRE LES FILTRES
# ==========================================

# ==========================================
# CONSTRUIRE LES FILTRES
# ==========================================

def construire_filtres(connexion, table):

    filtres = []
    valeurs = []

    colonnes = obtenir_colonnes(connexion, table)

    print("\n===== FILTRES =====")
    print("Appuyer sur Entree pour terminer les filtres.")

    while True:

        print("\nColonnes disponibles :")

        for i, colonne in enumerate(colonnes, 1):
            print(f"{i}. {colonne}")

        choix = input("\nColonne à filtrer : ").strip()

        # Si vide, on termine les filtres
        if choix == "":
            break

        # Trouver la colonne choisie
        colonne = None

        if choix.isdigit():

            numero = int(choix)

            if 1 <= numero <= len(colonnes):
                colonne = colonnes[numero - 1]

        else:

            colonne = trouver_colonne(connexion, table, choix)

        if colonne is None:
            print("Colonne introuvable.")
            continue

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

        choix_op = input("Choisir un opérateur : ").strip()

        if choix_op not in operateurs:
            print("Opérateur invalide.")
            continue

        operateur = operateurs[choix_op]

        nom_colonne = proteger_nom(colonne)

        if operateur in ("IS NULL", "IS NOT NULL"):

            filtres.append(
                f"{nom_colonne} {operateur}"
            )

        else:

            valeur = input("Valeur recherchée : ")

            filtres.append(
                f"{nom_colonne} COLLATE NOCASE {operateur} ?"
            )

            valeurs.append(valeur)

        print("\nFiltre ajouté !")

    # Combiner plusieurs filtres
    if len(filtres) > 1:

        print("\n1. ET (AND) : toutes les conditions")
        print("2. OU (OR) : au moins une condition")

        choix = input("Combiner les filtres avec : ")

        liaison = " OR " if choix == "2" else " AND "

    else:

        liaison = " AND "

    condition = liaison.join(filtres)

    return condition, valeurs


# ==========================================
# AFFICHER LES RESULTATS
# ==========================================

def afficher_resultats(curseur):

    resultats = curseur.fetchall()

    if not resultats:
        print("\nAucun résultat trouvé.")
        return

    # Recuperer les noms des colonnes
    colonnes = [
        description[0]
        for description in curseur.description
    ]

    # Calculer la largeur necessaire pour chaque colonne
    largeurs = []

    for i, colonne in enumerate(colonnes):

        largeur = len(colonne)

        for ligne in resultats:
            valeur = "NULL" if ligne[i] is None else str(ligne[i])
            largeur = max(largeur, len(valeur))

        largeurs.append(largeur)

    # Afficher les titres
    print("\n===== RESULTATS =====")

    entete = " | ".join(
        colonnes[i].ljust(largeurs[i])
        for i in range(len(colonnes))
    )

    print(entete)
    print("-" * len(entete))

    # Afficher chaque ligne
    for ligne in resultats:

        valeurs = []

        for i, valeur in enumerate(ligne):

            texte = "NULL" if valeur is None else str(valeur)
            valeurs.append(texte.ljust(largeurs[i]))

        print(" | ".join(valeurs))

    print("\nNombre de résultats :", len(resultats))



def consulter(connexion, table):

    print("\n===== CONSULTATION =====")
    print("Table sélectionnée :", table)

    # Afficher automatiquement toute la table
    requete = (
        f"SELECT * FROM {proteger_nom(table)}"
    )

    try:

        curseur = connexion.cursor()
        curseur.execute(requete)

        afficher_resultats(curseur)

        # Proposer des filtres facultatifs
        filtre = input(
            "\nVoulez-vous ajouter un filtre ? (oui/non) : "
        ).strip().lower()

        condition = ""
        valeurs = []

        if filtre == "oui":

            condition, valeurs = construire_filtres(
                connexion, table
            )

        # Construire la nouvelle requete
        requete = (
            f"SELECT * FROM {proteger_nom(table)}"
        )

        if condition:
            requete += " WHERE " + condition

        # Proposer un tri
        tri = input(
            "\nTrier les résultats ? (oui/non) : "
        ).strip().lower()

        if tri == "oui":

            colonne = choisir_colonne_filtre(
                connexion, table
            )

            if colonne is not None:

                print("\n1. Croissant")
                print("2. Décroissant")

                ordre = input("Votre choix : ")

                direction = "DESC" if ordre == "2" else "ASC"

                requete += (
                    f" ORDER BY {proteger_nom(colonne)} {direction}"
                )

        # Proposer une limite
        limite = input(
            "\nLimiter le nombre de résultats ? "
            "(laisser vide pour tout afficher) : "
        ).strip()

        if limite:

            if limite.isdigit() and int(limite) > 0:

                requete += " LIMIT ?"
                valeurs.append(int(limite))

            else:

                print("Limite invalide. Aucun résultat limité.")

        # Afficher les résultats filtrés, triés ou limités
        if condition or tri == "oui" or limite:

            curseur = connexion.cursor()
            curseur.execute(requete, valeurs)

            afficher_resultats(curseur)

    except sqlite3.Error as erreur:

        print("Erreur SQL :", erreur)

# ==========================================
# AJOUTER DES DONNEES
# ==========================================

def ajouter(connexion, table):

    colonnes = obtenir_colonnes(connexion, table)

    print("\n===== AJOUTER DES DONNEES =====")

    for i, colonne in enumerate(colonnes, 1):
        print(f"{i}. {colonne}")

    choix = input("\nColonnes à remplir (ex : 1,2,3) : ")

    selection = []

    try:

        elements = [element.strip() for element in choix.split(",")]

        for element in elements:

            if element.isdigit():

                numero = int(element)

                if not 1 <= numero <= len(colonnes):
                    print("Numéro invalide.")
                    return

                colonne = colonnes[numero - 1]

            else:

                colonne = trouver_colonne(connexion, table, element)

                if colonne is None:
                    print("Colonne introuvable :", element)
                    return

            if colonne not in selection:
                selection.append(colonne)

        print("\n1. Ajouter une seule ligne")
        print("2. Ajouter plusieurs lignes")

        mode = input("\nVotre choix : ")

        if mode == "1":
            nombre_lignes = 1

        elif mode == "2":

            nombre = input("Combien de lignes voulez-vous ajouter ? ")

            if not nombre.isdigit() or int(nombre) < 1:
                print("Nombre invalide.")
                return

            nombre_lignes = int(nombre)

        else:
            print("Choix invalide.")
            return

        noms_sql = ", ".join(
            proteger_nom(colonne) for colonne in selection
        )

        marqueurs = ", ".join("?" for _ in selection)

        requete = (
            f"INSERT INTO {proteger_nom(table)} "
            f"({noms_sql}) VALUES ({marqueurs})"
        )

        toutes_les_lignes = []

        for i in range(nombre_lignes):

            print(f"\n===== LIGNE {i + 1} =====")

            valeurs = []

            for colonne in selection:

                valeur = input(f"{colonne} : ")
                valeurs.append(valeur)

            toutes_les_lignes.append(valeurs)

        curseur = connexion.cursor()

        curseur.executemany(requete, toutes_les_lignes)

        connexion.commit()

        print(
            f"\n{nombre_lignes} ligne(s) ajoutée(s) avec succès !"
        )

    except (ValueError, sqlite3.Error) as erreur:

        print("Erreur :", erreur)

# ==========================================
# AFFICHER LA TABLE POUR MODIFIER / SUPPRIMER
# ==========================================

def afficher_table_actions(connexion, table):

    curseur = connexion.cursor()

    # Le rowid permet d'identifier chaque ligne
    curseur.execute(
        f"SELECT _rowid_, * FROM {proteger_nom(table)} "
        "ORDER BY _rowid_"
    )

    resultats = curseur.fetchall()

    if not resultats:
        print("\nLa table est vide.")
        return None

    colonnes = [
        description[0]
        for description in curseur.description
    ]

    # Ajouter une colonne de numero visible
    entetes = ["Ligne"] + colonnes[1:]

    # Calculer la largeur des colonnes
    largeurs = []

    for i, entete in enumerate(entetes):

        largeur = len(entete)

        for numero, ligne in enumerate(resultats, 1):

            if i == 0:
                valeur = str(numero)
            else:
                valeur = "NULL" if ligne[i] is None else str(ligne[i])

            largeur = max(largeur, len(valeur))

        largeurs.append(largeur)

    # Afficher les entetes
    print("\n===== TABLE :", table, "=====")

    print(" | ".join(
        entetes[i].ljust(largeurs[i])
        for i in range(len(entetes))
    ))

    print("-" * (sum(largeurs) + 3 * (len(largeurs) - 1)))

    # Afficher les lignes
    for numero, ligne in enumerate(resultats, 1):

        valeurs = [str(numero)]

        for valeur in ligne[1:]:

            texte = "NULL" if valeur is None else str(valeur)
            valeurs.append(texte)

        print(" | ".join(
            valeurs[i].ljust(largeurs[i])
            for i in range(len(valeurs))
        ))

    return resultats



def modifier(connexion, table):

    print("\n===== MODIFIER DES DONNEES =====")

    # Afficher la table
    lignes = afficher_table_actions(connexion, table)

    if lignes is None:
        return

    # Obtenir les noms des colonnes
    colonnes = obtenir_colonnes(connexion, table)

    print("\n===== CHOISIR UNE LIGNE =====")

    choix = input("Numéro de la ligne à modifier : ")

    if not choix.isdigit() or not 1 <= int(choix) <= len(lignes):
        print("Ligne invalide.")
        return

    # Récupérer la ligne choisie
    ligne = lignes[int(choix) - 1]

    # Le premier élément est le rowid
    rowid = ligne[0]

    modifications = {}

    # Permettre de modifier plusieurs colonnes
    while True:

        print("\n===== COLONNES DISPONIBLES =====")

        for i, colonne in enumerate(colonnes, 1):
            print(f"{i}. {colonne}")

        print("0. Terminer les modifications")

        choix_colonne = input("\nColonne à modifier : ")

        if choix_colonne == "0":
            break

        if not choix_colonne.isdigit():
            print("Choix invalide.")
            continue

        numero = int(choix_colonne)

        if numero < 1 or numero > len(colonnes):
            print("Colonne invalide.")
            continue

        colonne = colonnes[numero - 1]

        nouvelle_valeur = input(
            f"Nouvelle valeur pour {colonne} : "
        )

        modifications[colonne] = nouvelle_valeur

        print("Modification ajoutée.")

    if not modifications:
        print("Aucune modification effectuée.")
        return

    # Afficher les changements avant confirmation
    print("\n===== RESUME =====")

    for colonne, valeur in modifications.items():
        print(f"{colonne} : {valeur}")

    confirmation = input("\nConfirmer ? (oui/non) : ")

    if confirmation.casefold() != "oui":
        print("Modifications annulées.")
        return

    # Appliquer les modifications
    curseur = connexion.cursor()

    for colonne, valeur in modifications.items():

        requete = (
            f"UPDATE {proteger_nom(table)} "
            f"SET {proteger_nom(colonne)} = ? "
            f"WHERE _rowid_ = ?"
        )

        curseur.execute(requete, (valeur, rowid))

    connexion.commit()

    print("\nModifications effectuées avec succès !")

    # Afficher la table mise à jour
    afficher_table_actions(connexion, table)

# ==========================================
# SUPPRIMER DES DONNEES
# ==========================================

def supprimer(connexion, table):

    print("\n===== SUPPRIMER DES DONNEES =====")

    # Afficher toute la table
    resultats = afficher_table_actions(connexion, table)

    if resultats is None:
        return

    # Choisir la ligne à supprimer
    numero = input("\nQuel numero de ligne voulez-vous supprimer ? ")

    if not numero.isdigit() or not 1 <= int(numero) <= len(resultats):
        print("Numero de ligne invalide.")
        return

    ligne = resultats[int(numero) - 1]

    rowid = ligne[0]

    print("\n===== LIGNE SELECTIONNEE =====")

    for i, colonne in enumerate(obtenir_colonnes(connexion, table)):
        print(f"{colonne} : {ligne[i + 1]}")

    confirmation = input(
        "\nVoulez-vous vraiment supprimer cette ligne ? (oui/non) : "
    )

    if confirmation.lower() != "oui":
        print("Suppression annulée.")
        return

    try:

        curseur = connexion.cursor()

        curseur.execute(
            f"DELETE FROM {proteger_nom(table)} "
            "WHERE _rowid_ = ?",
            (rowid,)
        )

        connexion.commit()

        print("\nLigne supprimée avec succès !")

        # Afficher la table mise à jour
        afficher_table_actions(connexion, table)

    except sqlite3.Error as erreur:

        print("Erreur SQL :", erreur)


# ==========================================
# CREER UNE NOUVELLE TABLE
# ==========================================

def creer_table(connexion):

    print("\n===== CREER UNE TABLE =====")

    nom_table = input("Nom de la table : ").strip()

    if not nom_table:
        print("Nom invalide.")
        return

    nombre = input("Nombre de colonnes : ")

    if not nombre.isdigit() or int(nombre) < 1:
        print("Nombre invalide.")
        return

    colonnes_sql = []
    types = {
        "1": "INTEGER",
        "2": "TEXT",
        "3": "REAL",
        "4": "BLOB"
    }

    nombre_cles = 0

    for i in range(int(nombre)):

        print(f"\n===== COLONNE {i + 1} =====")

        nom_colonne = input("Nom de la colonne : ").strip()

        if not nom_colonne:
            print("Nom invalide.")
            return

        print("\nTypes disponibles :")
        print("1. INTEGER")
        print("2. TEXT")
        print("3. REAL")
        print("4. BLOB")

        choix_type = input("Type : ")

        if choix_type not in types:
            print("Type invalide.")
            return

        type_donnee = types[choix_type]

        cle_primaire = input("Clé primaire ? (oui/non) : ")

        colonne_sql = (
            f"{proteger_nom(nom_colonne)} {type_donnee}"
        )

        if cle_primaire.lower() == "oui":

            nombre_cles += 1

            if nombre_cles > 1:
                print("Une seule clé primaire est permise ici.")
                return

            colonne_sql += " PRIMARY KEY"

            if type_donnee == "INTEGER":
                colonne_sql += " AUTOINCREMENT"

        colonnes_sql.append(colonne_sql)

    requete = (
        f"CREATE TABLE {proteger_nom(nom_table)} "
        f"({', '.join(colonnes_sql)})"
    )

    try:

        curseur = connexion.cursor()
        curseur.execute(requete)

        connexion.commit()

        print("\nTable créée avec succès !")

    except sqlite3.Error as erreur:

        print("Erreur :", erreur)
def ajouter_colonne(connexion, table):

    print("\n===== AJOUTER UNE COLONNE =====")

    # Afficher les colonnes déjà présentes
    curseur = connexion.cursor()
    curseur.execute(f"SELECT * FROM {proteger_nom(table)} LIMIT 0")

    colonnes_existantes = [colonne[0] for colonne in curseur.description]

    print(f"\nTable sélectionnée : {table}")
    print("\nColonnes actuelles :")

    for colonne in colonnes_existantes:
        print("-", colonne)

    # Demander le nom de la nouvelle colonne
    nom_colonne = input("\nNom de la nouvelle colonne : ").strip()

    if not nom_colonne:
        print("Le nom ne peut pas être vide.")
        return

    # Vérifier si la colonne existe déjà
    for colonne in colonnes_existantes:
        if colonne.casefold() == nom_colonne.casefold():
            print("Cette colonne existe déjà.")
            return

    # Choisir le type de données
    print("\nTypes disponibles :")
    print("1. TEXT")
    print("2. INTEGER")
    print("3. REAL")
    print("4. BLOB")

    types = {
        "1": "TEXT",
        "2": "INTEGER",
        "3": "REAL",
        "4": "BLOB"
    }

    choix = input("\nChoisir le type : ").strip()

    if choix not in types:
        print("Type invalide.")
        return

    type_donnee = types[choix]

    # Demander confirmation
    confirmation = input(
        f"\nAjouter la colonne '{nom_colonne}' de type {type_donnee} ? (oui/non) : "
    )

    if confirmation.casefold() != "oui":
        print("Opération annulée.")
        return

    # Ajouter la colonne dans la table
    requete = (
        f"ALTER TABLE {proteger_nom(table)} "
        f"ADD COLUMN {proteger_nom(nom_colonne)} {type_donnee}"
    )

    try:
        curseur.execute(requete)
        connexion.commit()

        print("\nColonne ajoutée avec succès !")

        # Afficher la nouvelle structure
        afficher_structure(connexion, table)

    except sqlite3.Error as erreur:
        print(f"Erreur : {erreur}")

# ==========================================
# MENU PRINCIPAL
# ==========================================

def menu_principal(connexion):

    table = choisir_table(connexion)

    while True:

        print("\n================================")
        print("          OUTIL SQLITE")
        print("================================")
        print("Table actuelle :", table)
        print("--------------------------------")
        print("1. Afficher les tables")
        print("2. Changer de table")
        print("3. Consulter les données")
        print("4. Ajouter des données")
        print("5. Modifier des données")
        print("6. Supprimer des données")
        print("7. Ajouter une colonne")
        print("8. Voir la structure de la table")
        print("9. Créer une nouvelle table")
        print("0. Quitter")
        print("================================")

        choix = input("Votre choix : ")

        if choix == "1":

            for nom in obtenir_tables(connexion):
                print("-", nom)

        elif choix == "2":

            nouvelle_table = choisir_table(connexion)

            if nouvelle_table is not None:
                table = nouvelle_table

        elif choix == "3":

            if table is not None:
                consulter(connexion, table)

        elif choix == "4":

            if table is not None:
                ajouter(connexion, table)

        elif choix == "5":

            if table is not None:
                modifier(connexion, table)

        elif choix == "6":

            if table is not None:
                supprimer(connexion, table)

        elif choix == "7":

            if table is not None:
                ajouter_colonne(connexion, table)

        elif choix == "8":

            if table is not None:
                afficher_structure(connexion, table)

        elif choix == "9":

            creer_table(connexion)

        elif choix == "0":
            break

        else:
            print("Choix invalide.")

# ==========================================
# PROGRAMME PRINCIPAL
# ==========================================

def main():

    connexion = connexion_base()

    if connexion is None:
        return

    try:

        menu_principal(connexion)

    finally:

        connexion.close()
        print("\nConnexion fermée.")


main()
