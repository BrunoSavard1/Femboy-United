
import paho.mqtt.client as mqtt
import time
import getpass


# ============================================================
# CONFIGURATION
# ============================================================

IP_BROKER = ""
PORT = 1883

topics = set()


# ============================================================
# CHOISIR LE SERVEUR
# ============================================================

def choisir_serveur():

    global IP_BROKER, PORT

    print("\n===== CONFIGURATION MOSQUITTO =====")
    print("1. Ordinateur local")
    print("2. Serveur distant")

    while True:

        choix = input("\nVotre choix : ").strip()

        if choix == "1":
            IP_BROKER = "127.0.0.1"
            break

        elif choix == "2":

            IP_BROKER = input(
                "\nAdresse IP du broker : "
            ).strip()

            if IP_BROKER:
                break

            print("Adresse invalide.")

        else:
            print("Choix invalide.")

    port = input("Port MQTT (Entrée pour 1883) : ").strip()

    if port:
        try:
            PORT = int(port)

            if PORT < 1 or PORT > 65535:
                raise ValueError

        except ValueError:
            print("Port invalide.")
            return False

    print("\n===== AUTHENTIFICATION =====")
    print("Nom d'utilisateur : Bruno")
    print("Mot de passe : 12345")

    utilisateur = input(
        "Nom d'utilisateur (vide si aucun) : "
    ).strip()

    mot_de_passe = ""

    if utilisateur:

        mot_de_passe = getpass.getpass(
            "Mot de passe : "
        )

    print("\nConfiguration sélectionnée :")
    print("IP :", IP_BROKER)
    print("Port :", PORT)

    return utilisateur, mot_de_passe


# ============================================================
# RECEVOIR LES MESSAGES
# ============================================================

def recevoir_message(client, userdata, message):

    topic = message.topic

    contenu = message.payload.decode(
        "utf-8",
        errors="replace"
    )

    topics.add(topic)

    print("\n===== MESSAGE REÇU =====")
    print("Topic :", topic)
    print("Message :", contenu)


# ============================================================
# CONNEXION AU BROKER
# ============================================================

def connecter(utilisateur, mot_de_passe):

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )

    client.on_message = recevoir_message

    # Ajouter les identifiants si nécessaire
    if utilisateur:
        client.username_pw_set(
            utilisateur,
            mot_de_passe
        )

    try:

        client.connect(IP_BROKER, PORT, 60)

        client.loop_start()

        print("\nConnexion au broker réussie.")

        return client

    except Exception as erreur:

        print("\nErreur de connexion :", erreur)

        return None


# ============================================================
# DÉCOUVRIR LES TOPICS
# ============================================================

def decouvrir_topics(client):

    print("\n===== DÉCOUVERTE DES TOPICS =====")
    print("Recherche pendant 5 secondes...")

    client.subscribe("#")

    time.sleep(5)

    client.unsubscribe("#")

    if not topics:

        print("\nAucun topic découvert.")

    else:

        print("\n===== TOPICS DISPONIBLES =====")

        for i, topic in enumerate(sorted(topics), 1):
            print(f"{i}. {topic}")


# ============================================================
# CHOISIR UN TOPIC
# ============================================================

def choisir_topic():

    liste_topics = sorted(topics)

    print("\n===== CHOISIR UN TOPIC =====")

    if liste_topics:

        for i, topic in enumerate(liste_topics, 1):
            print(f"{i}. {topic}")

        print("N. Nouveau topic")

        choix = input("\nVotre choix : ").strip()

        if choix.lower() == "n":

            topic = input(
                "Nom du nouveau topic : "
            ).strip()

            if topic:
                return topic

            print("Topic invalide.")
            return None

        try:

            numero = int(choix)

            if 1 <= numero <= len(liste_topics):
                return liste_topics[numero - 1]

        except ValueError:
            pass

        print("Choix invalide.")
        return None

    else:

        print("Aucun topic découvert.")

        topic = input(
            "Entrer un nouveau topic : "
        ).strip()

        if topic:
            return topic

        print("Topic invalide.")
        return None


# ============================================================
# PUBLIER UN MESSAGE
# ============================================================

def publier_message(client):

    print("\n===== PUBLIER UN MESSAGE =====")

    topic = choisir_topic()

    if topic is None:
        return

    message = input("\nMessage à publier : ")

    resultat = client.publish(topic, message)

    if resultat.rc == mqtt.MQTT_ERR_SUCCESS:

        resultat.wait_for_publish(timeout=5)

        if resultat.is_published():

            topics.add(topic)

            print("\nMessage publié avec succès !")

        else:

            print("\nPublication non confirmée.")

    else:

        print("\nErreur lors de la publication.")


# ============================================================
# LIRE LES MESSAGES D'UN TOPIC
# ============================================================

def lire_topic(client):

    print("\n===== LIRE UN TOPIC =====")

    topic = choisir_topic()

    if topic is None:
        return

    client.subscribe(topic)

    print("\nÉcoute du topic :", topic)
    print("En attente de messages...")

    input("\nAppuie sur Entrée pour arrêter l'écoute.")

    client.unsubscribe(topic)


# ============================================================
# ÉCOUTER TOUS LES TOPICS
# ============================================================

def ecouter_tout(client):

    print("\n===== ÉCOUTER TOUS LES TOPICS =====")

    client.subscribe("#")

    print("\nÉcoute de tous les topics...")

    input("\nAppuie sur Entrée pour arrêter l'écoute.")

    client.unsubscribe("#")


# ============================================================
# MENU PRINCIPAL
# ============================================================

def menu(client):

    while True:

        print("\n================================")
        print("         OUTIL MOSQUITTO")
        print("================================")

        print("Broker :", IP_BROKER)
        print("Port :", PORT)

        print("--------------------------------")
        print("1. Afficher les topics disponibles")
        print("2. Publier un message")
        print("3. Lire les messages d'un topic")
        print("4. Écouter tous les topics")
        print("0. Quitter")
        print("================================")

        choix = input("\nVotre choix : ").strip()

        if choix == "1":
            decouvrir_topics(client)

        elif choix == "2":
            publier_message(client)

        elif choix == "3":
            lire_topic(client)

        elif choix == "4":
            ecouter_tout(client)

        elif choix == "0":
            print("\nFermeture de Mosquitto.")
            break

        else:
            print("\nChoix invalide.")


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

if __name__ == "__main__":

    configuration = choisir_serveur()

    if configuration:

        utilisateur, mot_de_passe = configuration

        client = connecter(
            utilisateur,
            mot_de_passe
        )

        if client:

            try:
                menu(client)

            finally:
                client.loop_stop()
                client.disconnect()
