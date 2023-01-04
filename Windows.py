import tkinter

import PySimpleGUI as sg
import multiprocessing
import threading as th

# Création du thème custom pour les fenêtres
sg.LOOK_AND_FEEL_TABLE['CUSTOM_THEME'] = {"BACKGROUND": "#f0f0f0",
                                          "TEXT": sg.COLOR_SYSTEM_DEFAULT,
                                          "INPUT": "#E4E3E3",
                                          "TEXT_INPUT": sg.COLOR_SYSTEM_DEFAULT,
                                          "SCROLL": sg.COLOR_SYSTEM_DEFAULT,
                                          "BUTTON": ("#000000", "#BEBDBD"),
                                          "PROGRESS": sg.COLOR_SYSTEM_DEFAULT,
                                          "BORDER": 1,
                                          "SLIDER_DEPTH": 1,
                                          "PROGRESS_DEPTH": 0, }
sg.theme('CUSTOM_THEME')

scaling = 3
"""
Valeur de zoom des fenêtres. Recommandé: 1.5
"""

middle_win_pos = (None, None)
"""
Contient la position de la dernière fenêtre ouverte. Permet de déplacer les nouvelles fenêtres sur cette position
"""


def get_window_pos(evt: tkinter.Event) -> None:
    """
    Permet de récupérer les coordonnées de la fenêtre sur l'écran à partir d'un évènement de type <Configure>
    :param evt: L'évènement de type <Configure>
    """
    global middle_win_pos
    banned_coords = ()  # Coordonnées "magiques" utilisées lors de la construction de la fenetre par Tkinter
    if (evt.x, evt.y) not in banned_coords:
        widget: tkinter.Widget = evt.widget
        middle_win_pos = evt.x + widget.winfo_width() / 2, evt.y + widget.winfo_height() / 2
        print(middle_win_pos)


def set_location(window: sg.Window) -> None:
    """
    Permet de définir la position de la fenêtre en fonction de la position de la dernière fenêtre ouverte
    :param window: La fenêtre à déplacer
    """
    global middle_win_pos
    x, y = middle_win_pos
    if x is not None and y is not None:
        size_x, size_y = window.current_size_accurate()
        x = x - size_x / 2
        y = y - size_y / 2
        window.TKroot.geometry("+%d+%d" % (x, y))

        print("Window moved to", x, y)


def bind_get_pos(window: sg.Window) -> None:
    """
    Permet de lier la fonction get_window_pos à l'évènement <Configure> de la fenêtre passée en paramètre puis lance
    un évènement de ce type pour récupérer la position de la fenêtre (au cas où elle aurait été bougée alors que
    l'évènement n'était pas lié)
    (Fonction utilisée avec Tk::after() car des évènement de types <Configure> sont envoyés à la fenêtre lors de ses
    créations avec des fausses coordonnées)
    :param window: La fenêtre à lier
    """
    window.TKroot.bind("<Configure>", get_window_pos)
    window.TKroot.event_generate("<Configure>", x=window.TKroot.winfo_x(), y=window.TKroot.winfo_y())


class SimpleInputWindow():
    """
    SimpleInputWindow - Fenêtre préconfigurée pour demander une entrée à l'utilisateur
    """

    def __init__(self, title, text):
        """
        :param title: Le titre de la fenêtre
        :param text: Le texte à afficher devant la case de saisie
        """
        self.layout = [
            [sg.Text(text)],
            [sg.InputText(key='input', size=(20, 1))],
            [sg.Button('Annuler', key='btn_annuler'), sg.Push(), sg.Button('Valider', key='btn_valider')]
        ]
        self.window = sg.Window(title, self.layout, finalize=True, scaling=scaling)
        set_location(self.window)

        # Bind de la touche Entrée
        self.window.bind('<Return>', 'btn_valider')

    def show(self):
        self.window.TKroot.after(500, bind_get_pos, self.window)

        event, values = self.window.read()

        if event == 'btn_annuler' or event == sg.WIN_CLOSED:
            entree = None

        elif event == 'btn_valider':
            entree = self.window['input'].get().strip()

        self.window.close()
        return entree


class ErrorWindow:
    """
    ErrorWindow - Fenêtre préconfigurée pour simplement afficher une erreur
    """

    def __init__(self, text):
        """
        :param text: Le texte décrivant l'erreur
        """
        self.layout = [
            [sg.Text('Erreur : ' + text, text_color='red')],
            [sg.Button('Ok', key='btn_ok')]
        ]
        self.window = sg.Window('Erreur', self.layout, finalize=True, scaling=scaling)
        set_location(self.window)

        # Bind de la touche entrée au bouton ok
        self.window.bind('<Return>', 'btn_ok')

    def show(self):
        self.window.TKroot.after(500, bind_get_pos, self.window)

        event, values = self.window.read()
        self.window.close()
        return event, values


def validate(name):
    """
    Permet de valider un nom d'utilisateur. Contraintes :
        - Un nom pas vide
        - Ne doit pas contenir de virgules
    :param name: Le nom à valider
    :return: True si le nom est valide, False sinon
    """
    nom_ok = True
    if name == '':
        ErrorWindow('Vous devez entrer un nom').show()
        nom_ok = False
    if nom_ok and (name.find(',') != -1):
        nom_ok = False
        ErrorWindow('Le nom ne doit pas contenir de virgules').show()
    return nom_ok


class ConnectWindow:
    """
    ConnectWindow - Fenêtre permettant à l'utilisateur d'entrer son nom
    """

    def __init__(self):
        self.layout = [
            [sg.Text('Entrez votre nom :'), sg.InputText(key='input_name')],
            [sg.Push(), sg.Button('Valider', key='btn_connecter')]
        ]
        self.window = sg.Window('Connexion', self.layout, finalize=True, scaling=scaling)
        set_location(self.window)

        # Bind la touche entrée à la validation
        self.window.bind('<Return>', 'btn_connecter')

    def show(self):
        self.window.TKroot.after(500, bind_get_pos, self.window)

        end = False
        while not end:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED:
                end = True
                name = None

            if event == 'btn_connecter':
                name = self.window['input_name'].get().strip()
                if validate(name):
                    end = True

        self.window.close()
        return name


class InfoWindow:
    """
    InfoWindow - Fenêtre préconfigurée pour simplement afficher un message
    """

    def __init__(self, title, text):
        self.layout = [
            [sg.Text(text)],
            [sg.Button('Ok', key='btn_ok')]
        ]
        self.window = sg.Window(title, self.layout, finalize=True, scaling=scaling)
        set_location(self.window)

    def show(self):
        self.window.TKroot.after(500, bind_get_pos, self.window)

        event, values = self.window.read()
        self.window.close()
        return event, values


class DiscussWindow:
    def __init__(self, client):
        self.queue_recv = multiprocessing.Queue()
        self.queue_send = multiprocessing.Queue()

        self.client = client
        self.__expediteur = client.nom
        self.__destinataire = client.nom_destinataire

        self.__start_thread()

        self.__layout = [
            [sg.Multiline(key='output', size=(50, 10), autoscroll=True, disabled=True)],
            [sg.InputText(key='input', size=(52, 1), disabled=True)],
            [sg.Button('Sortir', key='btn_quit'), sg.Push(), sg.Button('Envoyer', key='btn_send', disabled=True)]
        ]
        self.__window = sg.Window('Discussion', self.__layout, finalize=True, scaling=scaling)
        set_location(self.__window)

        # Variables liés à l'affichage des messages
        self.__text_msg = self.__window['output']
        self.__last_person = None

    def show_waiting_text(self):
        """
        Permet d'afficher le texte par défaut dans la fenêtre de discussion
        :return None
        """
        self.__text_msg.print('Bienvenue dans le salon de discussion !\n')
        self.__text_msg.print('En attente de la confirmation de conversation avec ' + self.__destinataire + '...\n')

    def show_welcome_text(self):
        """
        Permet d'afficher le texte de bienvenue dans la fenêtre de discussion
        :return None
        """
        self.__text_msg.update(value='')  # Clear du texte
        self.__text_msg.print('Bienvenue dans le salon de discussion !\n')
        self.__text_msg.print('Vous êtes en conversation avec ' + self.__destinataire + '.\n')

    def process_recv(self):
        end = False
        while not end:
            msg = self.queue_recv.get()
            if msg is not None:
                self.__print_msg(self.__destinataire, msg)
            else:
                end = True

    def __start_thread(self):
        self.__rcv_process = th.Thread(target=self.process_recv)
        self.__rcv_process.start()

    def __print_msg(self, expediteur, msg):
        """
        Effectue la mise en forme des messages sur la fenêtre
        :param expediteur: Permet l'affchage de l'expéditeur du message à afficher
        :param msg: Permet l'affichage du message à afficher
        """
        if (self.__last_person != expediteur):
            self.__text_msg.print('-'*65, justification='center')
            self.__last_person = expediteur

        self.__text_msg.print(expediteur + ' :', font=(sg.DEFAULT_FONT[0], sg.DEFAULT_FONT[1], 'underline'), end='') # end changé pour retirer le \n
        self.__text_msg.print(' ' + msg)

    def enable_communication(self):
        """
        Permet d'activer le bouton et l'input de communication
        :return: None
        """
        self.__window['btn_send'].update(disabled=False)
        self.__window['input'].update(disabled=False)

    def show(self):
        """
        Affiche la fenêtre de discussion
        :return: True si l'utilisateur a éu une conversation avec son destinataire, False sinon
        """
        self.__window.TKroot.after(500, bind_get_pos, self.__window)

        from Communicate import envoyer_message
        end = False

        while not end:
            event, values = self.__window.read()
            if event == 'btn_quit':
                end = True
            elif event == 'btn_send':
                envoyer_message(self.client, values['input'])
                self.__print_msg(self.__expediteur, values['input'])
                self.__window['input'].update('')
            elif event == sg.WIN_CLOSED:
                end = True
        self.close()

    def close(self):
        self.queue_recv.put(None)  # Pour que le thread de réception se termine proprement (On débloque la fn bloquante)
        self.__window.close()


class YesNoWindow:
    """
    YesNoWindow - Fenêtre préconfigurée pour demander une confirmation à l'utilisateur
    """
    def __init__(self, title, text):
        self.layout = [
            [sg.Text(text)],
            [sg.Button('Oui', key='btn_yes'), sg.Push(), sg.Button('Non', key='btn_no')]
        ]
        self.window = sg.Window(title, self.layout, finalize=True, scaling=scaling)
        set_location(self.window)

    def show(self):
        """
        Affiche la fenêtre et retourne le résultat de l'utilisateur
        :return: True si l'utilisateur a cliqué sur Oui, False sinon
        """
        self.window.TKroot.after(500, bind_get_pos, self.window)

        event, values = self.window.read()
        self.window.close()
        if event == 'btn_yes':
            return True
        else:  # englobe 'btn_no' et sg.WIN_CLOSED
            return False


def disable_buttons(window, client):
    """
    Permet de désactiver les boutons de la fenêtre principale en fonctions du contexte de l'utilisateur
    :param window: La fenêtre principale
    :param client: Le client
    :return La fenêtre avec les boutons activés/désactivés
    """
    buttons_status = []
    if client.cle is None:
        buttons_status = [False, True, True, True, False]
    else:
        buttons_status = [True, False, False, False]

    # On complète la liste en desactivant les boutons si ils n'ont pas été définis au dessus
    while len(buttons_status) < 5:
        buttons_status.append(True)

    # On applique les états aux boutons
    window['btn_createKey'].update(disabled=buttons_status[0])
    window['btn_editKey'].update(disabled=buttons_status[1])
    window['btn_delKey'].update(disabled=buttons_status[2])
    window['btn_communiquer'].update(disabled=buttons_status[3])
    window['btn_quit'].update(disabled=buttons_status[4])

    return window


class Menu:
    """
    Menu - Fenêtre principale de l'application
    """

    def __init__(self, client, msg_info=''):
        """
        :param client: Le client, utilisé pour toggle les boutons
        :param msg_info: Message d'information à afficher
        """

        self.client = client
        msg_info = msg_info.strip()

        self.layout = []
        if msg_info != '':
            self.layout.append([
                sg.Push(), sg.Text(('INFO : ' + msg_info), text_color='green'), sg.Push()
            ])

        self.layout += [  # += --> Append toute la liste à self.layout
            [sg.Button('Créer votre clé', key='btn_createKey', size=(15, 1)), sg.Button('Modifier votre clé', key='btn_editKey', size=(15, 1))],
            [sg.Button('Supprimer votre clé', key='btn_delKey', size=(15, 1)), sg.Button('Communiquer', key='btn_communiquer', size=(15, 1))],
            [sg.Button('Quitter', key='btn_quit', size=(32, 1))]
        ]

        title = 'Menu - ' + client.nom
        self.window = sg.Window(title, self.layout, finalize=True, scaling=scaling)
        set_location(self.window)

        self.window = disable_buttons(self.window, client)
        self.update_conn_btn()  # On met à jour le statut du bouton communiquer si une demande est arrivée alors que la
                                # fenêtre était fermée

    def update_conn_btn(self):
        """
        Permet de mettre à jour le bouton de connexion en fonction du contexte de l'utilisateur pour le mettre en vert
        si une demande de connexion est en attente
        :return None
        """
        print("UPDATE CONN BTN")
        if self.client.demande_connexion:
            self.window['btn_communiquer'].update(button_color=(None, 'green'))
        else:
            self.window['btn_communiquer'].update(button_color=(None, sg.theme_button_color_background()))

    def show(self):
        self.window.TKroot.after(500, bind_get_pos, self.window)

        end = False
        while not end:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED or event == 'btn_quit':
                end = True
                action = 'quit'

            if event == 'btn_createKey':
                end = True
                action = 'createKey'

            if event == 'btn_editKey':
                end = True
                action = 'editKey'

            if event == 'btn_delKey':
                end = True
                action = 'delKey'

            if event == 'btn_communiquer':
                end = True
                action = 'communiquer'

        self.window.close()
        return action
