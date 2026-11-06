
import subprocess
import sys
import os


def lancer_outil(nom_fichier):

    chemin = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        nom_fichier
    )

    if not os.path.isfile(chemin):

        print("\nErreur : fichier introuvable.")
        print("Fichier :", nom_fichier)

        input("\nAppuie sur Entrée pour continuer...")
        return

    print("\nLancement de", nom_fichier)

    try:

        subprocess.run(
            [sys.executable, chemin],
            check=False
        )

    except Exception as erreur:

        print("\nErreur lors du lancement :", erreur)

    input("\nAppuie sur Entrée pour revenir au menu principal...")


def menu_principal():

    while True:

        print("\n================================")
        print("       OUTILS OBJETS CONNECTÉS")
        print("================================")
        print("1. SQLite / SQL")
        print("2. InfluxDB3")
        print("3. Mosquitto")
        print("0. Quitter")
        print("================================")

        choix = input("\nVotre choix : ").strip()

        # SQLITE
        if choix == "1":

            print("\n===== AVERTISSEMENT SQLITE =====")
            print("La base de données est hébergée sur le serveur.")
            print("Il faut lancer ce programme directement")
            print("sur le serveur pour accéder à cette base.")
            print("\nNe pas lancer depuis votre ordinateur.")

            input("\nAppuie sur Entrée pour continuer...")

            # Remplacer par le nom exact de ton fichier
            lancer_outil("sqlite.py")

        # INFLUXDB
        elif choix == "2":

            print("\n===== AVANT DE LANCER INFLUXDB =====")
            print("Assure-toi d'avoir démarré l'exécutable")
            print("InfluxDB 3 avant de lancer ce programme.")
            print("\nVérifie également que le serveur est accessible.")

            input("\nAppuie sur Entrée pour continuer...")

            lancer_outil("InfluxDB3.py")

        # MOSQUITTO
        elif choix == "3":

            lancer_outil("Mosquitto.py")

        # QUITTER
        elif choix == "0":

            print("\nFermeture du programme.")
            break

        else:

            print("\nChoix invalide.")


if __name__ == "__main__":

    menu_principal()
