import PySimpleGUI as sg

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


scaling = 1.5
"""
Valeur de zoom des fenêtres. Recommandé: 1.5
"""

class SimpleInputWindow():
    """
    SimpleInputWindow - Fenêtre préconfigurée pour demander une entrée à l'utilisateur
    """
    def __init__(self, title, text):
        """
        :param title: Le titre de la fenêtre
        :param text: Le texte a afficher devant la case de saisie
        """
        self.layout = [
            [sg.Text(text)],
            [sg.InputText(key='input', size=(20, 1))],
            [sg.Button('Annuler', key='btn_annuler'), sg.Push(), sg.Button('Valider', key='btn_valider')]
        ]
        self.window = sg.Window(title, self.layout, finalize=True, scaling=scaling)

        # Bind de la touche Entrée
        self.window.bind('<Return>', 'btn_valider')

    def show(self):
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
            [sg.Text('Erreur : '+ text, text_color='red')],
            [sg.Button('Ok', key='btn_ok')]
        ]
        self.window = sg.Window('Erreur', self.layout, finalize=True, scaling=scaling)

        # Bind de la touche entrée au bouton ok
        self.window.bind('<Return>', 'btn_ok')

    def show(self):
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

        # Bind la touche entrée à la validation
        self.window.bind('<Return>', 'btn_connecter')

    def show(self):
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


class InfoWindow():
    """
    InfoWindow - Fenêtre préconfigurée pour simplement afficher un message
    """
    def __init__(self, title, text):
        self.layout = [
            [sg.Text(text)],
            [sg.Button('Ok', key='btn_ok')]
        ]
        self.window = sg.Window(title, self.layout, finalize=True, scaling=scaling)

    def show(self):
        event, values = self.window.read()
        self.window.close()
        return event, values


class Menu:
    """
    Menu - Fenêtre principale de l'application
    """

    def __init__(self, msg_info=''):
        """
        :param msg_info: Message d'information à afficher
        """
        msg_info = msg_info.strip()

        self.layout = []
        if msg_info != '':
            self.layout.append([
                sg.Push(), sg.Text(('INFO : ' + msg_info), text_color='green'), sg.Push()
            ])

        self.layout += [  # += --> Append toute la liste à self.layout
            [sg.Button('Créer votre clé', key='btn_createKey', size=(15,1)), sg.Button('Modifier votre clé', key='btn_editKey',size=(15,1))],
            [sg.Button('Supprimer votre clé', key='btn_delKey', size=(15,1)), sg.Button('Communiquer', key='btn_communiquer', size=(15,1))],
            [sg.Button('Quitter', key='btn_quit', size=(32,1))]
        ]
        self.window = sg.Window('Menu', self.layout, finalize=True, scaling=scaling)

    def show(self):
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

        self.window.close()
        return action
