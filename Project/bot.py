# Import necessary modules:
import json
import pickle
import random
import time
from threading import Thread
from tkinter import *

import deep_translator.exceptions
import nltk
# Uncomment this line to install all important packages for nltk
# nltk.download("all")
import numpy
import requests
import tensorflow
import tflearn
from deep_translator import GoogleTranslator
# added WordNetLemmatizer to lemmatize ingredients
from nltk.stem import WordNetLemmatizer
from nltk.stem.lancaster import LancasterStemmer

import window1
from window1 import *

stemmer = LancasterStemmer()


class ChatBot(Thread):
    lemmatizer = WordNetLemmatizer()
    trans = GoogleTranslator()

    words = []
    labels = []
    docs_x = []
    docs_y = []

    with open("intents.json") as file:
        data = json.load(file)

    try:
        with open("data.pickle", "rb") as f:
            words, labels, training, output = pickle.load(f)

    except:

        for intent in data["intents"]:
            for pattern in intent["patterns"]:
                wrds = nltk.word_tokenize(pattern)
                words.extend(wrds)
                docs_x.append(wrds)
                docs_y.append(intent["tag"])

            if intent["tag"] not in labels:
                labels.append(intent["tag"])

        words = [stemmer.stem(w.lower()) for w in words if w != "?"]
        words = sorted(list(set(words)))
        labels = sorted(labels)

        training = []
        output = []

        out_empty = [0 for _ in range(len(labels))]

        for x, doc in enumerate(docs_x):
            bag = []
            wrds = [stemmer.stem(w.lower()) for w in doc]
            for w in words:
                if w in wrds:
                    bag.append(1)
                else:
                    bag.append(0)
            output_row = out_empty[:]
            output_row[labels.index(docs_y[x])] = 1
            training.append(bag)
            output.append(output_row)

        training = numpy.array(training)
        output = numpy.array(output)

        with open("data.pickle", "wb") as f:
            pickle.dump((words, labels, training, output), f)

    tensorflow.compat.v1.reset_default_graph()

    net = tflearn.input_data(shape=[None, len(training[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
    net = tflearn.regression(net)

    model = tflearn.DNN(net)

    try:
        f = open("model.tflearn.data-00000-of-00001")
        model.load("model.tflearn")
    except IOError:
        model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
        model.save("model.tflearn")
    finally:
        f.close()

    def bag_of_words(self, s, words):
        bag = [0 for _ in range(len(words))]

        s_words = nltk.word_tokenize(s)
        s_words = [stemmer.stem(word.lower()) for word in s_words]

        for se in s_words:
            for i, w in enumerate(words):
                if w == se:
                    bag[i] = 1

        return numpy.array(bag)

    # -------------------------------------------------------------------------------------------- pana aici a fost ml
    # pentru apelari la spooncular API
    key = "bb238c76bf8e4034829176f6fbd152ca"
    baseUrl = "https://api.spoonacular.com/recipes/"

    # Vectori pentru a tine minte retetele
    RETETE = []
    IDRETETE = []
    TITLURETETE = []
    IMAGINIRETETE = []

    # functie pentru request la data de baze spooncular
    def req(self, type, data):
        window.update()
        request = self.baseUrl + type + self.key
        r = requests.get(request, params=data)
        result = r.json()
        return result

    # handle pentru raspunsuri si stergerea imaginii
    def raspuns(self, rsp):
        delImage()
        if rsp == "Acestea sunt ingredientele necesare:" or rsp == "Acestea sunt ingredientele de care ai nevoie:" or rsp == "Ingredientele pentru cumparaturi:":
            return 1
        elif rsp == "Acestea sunt instructiunile:" or rsp == "Acestia sunt pasii:" or rsp == "Acestia sunt pasii:":
            return 2
        elif rsp == "Nutritia retetei:" or rsp == "Valorile nutritionale sunt:":
            return 3
        elif rsp == "Vei avea nevoie de:" or rsp == "Echipamentul necesar este:" or rsp == "Iti va trebui":
            return 4
        elif rsp == "Cu placere! Sper sa-ti placa reteta!" or rsp == "Cu drag, sper ca ti-am fost de ajutor!":
            return 5
        elif rsp == "Bine ai venit(revenit) la meniu! Aici sunt retetele:":
            return 6
        elif rsp == "Aici poti incepe o sesiune  noua:":
            return 7

    # curatam vectorii la o noua cautare
    def curata(self):
        self.RETETE.clear()
        self.IDRETETE.clear()
        self.TITLURETETE.clear()
        self.IMAGINIRETETE.clear()

    # flow de dialog dupa ce userul a ales o reteta
    def dialog(self):

        window.update()
        insert_robot_msg("ChefBot: Pune-mi intrebari despre reteta aleasa! Daca vrei sa iesi imi poti scrie 'gata'.")
        window.update()
        insert_robot_msg(
            "ChefBot: Ma poti intreba despre ingrediente, echipamentul care iti trebuie, instructiunile de preparare sau valorile nutritionale!")
        window.update()
        insert_robot_msg("ChefBot: De asemenea, imi poti spune si daca vrei o cautare noua!")
        window.update()

        ok = 1
        while ok:
            window1.main_ok = True
            while window1.main_ok:
                window.update()
                msg = msg_entry.get()
                window.update()

            insert_user_msg(msg)
            window.update()

            if msg.lower() == "gata":
                break

            results = self.model.predict([self.bag_of_words(msg, self.words)])[0]
            results_index = numpy.argmax(results)
            tag = self.labels[results_index]

            # If confidence level is higher 70%, open up the json file, find specific tag and spit out response
            if results[results_index] > 0.70:
                for tg in self.data["intents"]:
                    if tg['tag'] == tag:
                        responses = tg['responses']
                response = random.choice(responses)

                insert_robot_msg("ChefBot: " + str(response))
                window.update()

                optiunea = self.raspuns(response)
                id = str(self.RETETE[0])
                pd = {
                    'id': id,
                    'stepBreakdown': False
                }

                if optiunea == 1:

                    nume = []
                    greutate = []
                    unitate = []
                    n = 0

                    url = str(id) + "/ingredientWidget.json?apiKey="
                    rez = self.req(url, pd)

                    try:
                        for ingr in rez["ingredients"]:
                            val = rez["ingredients"][n]["name"]
                            nume.append(val)
                            val = rez["ingredients"][n]["amount"]["metric"]["value"]
                            greutate.append(val)
                            val = rez["ingredients"][n]["amount"]["metric"]["unit"]
                            unitate.append(val)
                            n = n + 1

                    except KeyError:
                        insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                        window.update()
                        self.reteta()

                    n = 0

                    for i in range(len(nume)):
                        mesaj = str(str(greutate[n]) + " " + str(unitate[n]) + "," + str(nume[n]))
                        try:
                            translated = GoogleTranslator(source='en', target='ro').translate(mesaj)
                        except deep_translator.exceptions.NotValidPayload:
                            insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                            window.update()
                            self.reteta()
                        except deep_translator.exceptions.NotValidLength:
                            insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                            window.update()
                            self.reteta()
                        insert_robot_msg(translated)
                        window.update()

                        n = n + 1
                    self.dialog()

                elif optiunea == 4:

                    url = str(id) + "/equipmentWidget.json?apiKey="

                    rez = self.req(url, pd)

                    eqp = ""
                    for equipment in rez["equipment"]:
                        dict = equipment
                        eqp = eqp + dict.get('name') + ","

                    mesaj = str(eqp[:-1])
                    try:
                        translated = GoogleTranslator(source='en', target='ro').translate(mesaj)
                    except deep_translator.exceptions.NotValidPayload:
                        insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                        window.update()
                        self.reteta()
                    except deep_translator.exceptions.NotValidLength:
                        insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                        window.update()
                        self.reteta()
                    insert_robot_msg(translated)
                    window.update()
                    self.dialog()




                elif optiunea == 2:

                    url = str(id) + "/analyzedInstructions?apiKey="
                    rez = self.req(url, pd)

                    n = 0

                    for st in rez:
                        mesaj = str("\nSteps " + ":" + rez[n]["name"])
                        try:
                            translated = GoogleTranslator(source='en', target='ro').translate(mesaj)
                        except deep_translator.exceptions.NotValidPayload:
                            insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                            window.update()
                            self.reteta()
                        except deep_translator.exceptions.NotValidLength:
                            insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                            window.update()
                            self.reteta()
                        insert_robot_msg(translated)
                        window.update()

                        for sub_st in rez[n]['steps']:
                            stt = sub_st['step']
                            prop = stt.split(".")

                            for i in prop:
                                if not i:
                                    continue
                                if i[0] == " ":
                                    j = i.replace(" ", "", 1)
                                    if j[0] == " ":
                                        k = j.replace(" ", "", 1)
                                        mesaj = str(" – " + str(k) + ".")
                                        try:
                                            translated = GoogleTranslator(source='en', target='ro').translate(mesaj)
                                        except deep_translator.exceptions.NotValidPayload:
                                            insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                                            window.update()
                                            self.reteta()
                                        except deep_translator.exceptions.NotValidLength:
                                            insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                                            window.update()
                                            self.reteta()
                                        insert_robot_msg(translated)
                                        window.update()
                                    else:
                                        mesaj = str(" – " + str(j) + ".")
                                        try:
                                            translated = GoogleTranslator(source='en', target='ro').translate(mesaj)
                                        except deep_translator.exceptions.NotValidPayload:
                                            insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                                            window.update()
                                            self.reteta()
                                        except deep_translator.exceptions.NotValidLength:
                                            insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                                            window.update()
                                            self.reteta()
                                        insert_robot_msg(translated)
                                        window.update()
                                else:
                                    mesaj = str(" – " + str(i) + ".")
                                    try:
                                        translated = GoogleTranslator(source='en', target='ro').translate(mesaj)
                                    except deep_translator.exceptions.NotValidPayload:
                                        insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                                        window.update()
                                        self.reteta()
                                    except deep_translator.exceptions.NotValidLength:
                                        insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                                        window.update()
                                        self.reteta()
                                    insert_robot_msg(translated)
                                    window.update()
                        n += 1
                    self.dialog()

                elif optiunea == 3:

                    url = str(id) + "/nutritionWidget.json?apiKey="

                    rez = self.req(url, pd)

                    insert_robot_msg(" - calorii: " + str(rez["calories"]) + "cal")
                    window.update()
                    insert_robot_msg(" - carbohidrati: " + str(rez["carbs"]))
                    window.update()
                    insert_robot_msg(" - grasimi: " + str(rez["fat"]))
                    window.update()
                    insert_robot_msg(" - proteine: " + str(rez["protein"]))
                    window.update()

                    self.dialog()









                # multumiri
                elif optiunea == 5:
                    time.sleep(2)
                    exit()

                # inapoi la celelalte retete
                elif optiunea == 6:
                    self.alegereteta()

                # cautare noua
                elif optiunea == 7:
                    self.curata()
                    self.reteta()
            else:
                insert_robot_msg("ChefBot: Nu sunt sigur de ce trebuie sa fac, poti reformula te rog intrebarea?")
                window.update()
                self.dialog()
        exit()

    # O functie pentru a alege din retete si pentru a le afisa
    def alegereteta(self):
        window.update()
        n = 0
        # afisam retetele
        for i in self.TITLURETETE:
            mesaj = str(self.TITLURETETE[n])
            try:
                translated = GoogleTranslator(source='en', target='ro').translate(mesaj)
            except deep_translator.exceptions.NotValidPayload:
                insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                window.update()
                self.reteta()
            except deep_translator.exceptions.NotValidLength:
                insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                window.update()
                self.reteta()

            mesaj = str(n + 1) + "." + translated + "..."
            insert_robot_msg(mesaj)
            window.update()
            n += 1

        insert_robot_msg("ChefBot: Te rog sa alegi o reteta spunandu-mi numarul acesteia!")
        window.update()

        window1.main_ok = True
        while window1.main_ok:
            window.update()
            mesaj = msg_entry.get()
            window.update()

        insert_user_msg(mesaj)
        window.update()

        numere = [int(s) for s in mesaj.split() if s.isdigit()]

        # Verificam daca ales o reteta daca nu restartam functia
        try:
            numarreteta = int(sum(numere) / len(numere))
        except ValueError:
            insert_robot_msg("ChefBot: Nu ai ales niciun numar! Reluam...")
            window.update()
            self.alegereteta()
        except ZeroDivisionError:
            insert_robot_msg("ChefBot: Nu ai ales niciun numar! Reluam...")
            window.update()
            self.alegereteta()

        if len(self.TITLURETETE) >= numarreteta and numarreteta >= 1:
            self.RETETE.clear()
            self.RETETE.append(self.IDRETETE[numarreteta - 1])
            mesaj = str(self.TITLURETETE[numarreteta - 1])
            try:
                translated = GoogleTranslator(source='en', target='ro').translate(mesaj)
            except deep_translator.exceptions.NotValidPayload:
                insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                window.update()
                self.reteta()
            except deep_translator.exceptions.NotValidLength:
                insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                window.update()
                self.reteta()
            insert_robot_msg("ChefBot: Ai ales ' " + translated + " '. Buna alegere!")

            response = requests.get(str(self.IMAGINIRETETE[numarreteta - 1]))
            file = open("download.jpg", "wb")
            file.write(response.content)
            file.close()
            insertImage()
            window.update()
            window.update()
            self.dialog()
        else:
            insert_robot_msg("ChefBot: Nu ai ales niciun numar! Reluam...")
            window.update()
            self.alegereteta()

    def retetaveg(self):
        pd = {
            'number': 20,
            'tags': "vegetarian",
            'limitLicense': False
        }

        rez = self.req("random?apiKey=", pd)

        try:
            for i in rez["recipes"]:
                self.TITLURETETE.append(i["title"])
                self.IDRETETE.append(i["id"])
                val = i["image"]
                self.IMAGINIRETETE.append(val)
        except KeyError:
            insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
            window.update()
            self.reteta()

        self.alegereteta()

    def preluamretete(self, numar, ingrediente):
        # daca avem un numar de retete pe care vrea sa le vada
        if 1 <= numar <= 20:

            pd = {
                'ingredients': ingrediente,
                'number': numar,
                'ranking': 1,
                'fillIngredients': False,
                'limitLicense': False
            }

            rez = self.req("findByIngredients?apiKey=", pd)

            n = 0
            try:
                for i in rez:
                    self.IMAGINIRETETE.append(rez[n]["image"])
                    self.TITLURETETE.append(rez[n]["title"])
                    self.IDRETETE.append(rez[n]["id"])
                    n += 1
            except KeyError:
                insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
                window.update()
                self.reteta()

            # daca avem un numar de retete valid, chem functia de alegere a unei retete, desi s-ar putea ca sa nu existe
            # retete pentru anumite ingrediente asa ca vom printa un mesaj corespunzator

            if len(self.TITLURETETE) == 0:
                insert_robot_msg(
                    "ChefBot: Imi pare rau dar nu am putut gasi retete pentru ingredientele tale... Reincepem de la inceput...")
                window.update()
                self.reteta()

            elif len(self.TITLURETETE) >= numar:
                self.alegereteta()

        else:
            insert_robot_msg(
                "ChefBot: Nu ai ales niciun numar... Te rog sa alegi cate retete doresti sa vezi...")
            window.update()
            self.reteta()

    def retetaingrediente(self, mesaj):
        try:
            translated = GoogleTranslator(source='ro', target='en').translate(mesaj)
        except deep_translator.exceptions.NotValidPayload:
            insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
            window.update()
            self.reteta()
        except deep_translator.exceptions.NotValidLength:
            insert_robot_msg("ChefBot: A aparut o problema! Reluam de la inceput!")
            window.update()
            self.reteta()

        mesaj = translated
        mesaj = re.findall(re.compile("\w+"), mesaj.lower())

        f = open("food.txt", encoding="utf8")
        content = f.read()
        content = re.findall(re.compile("\w+"), content.lower())

        ing = []
        for cuv in mesaj:
            # scoatem ingredientele
            if self.lemmatizer.lemmatize(cuv) in content:
                ing.append(self.lemmatizer.lemmatize(cuv))

        # verificam daca avem macar 10 ingrediente
        if 1 <= len(ing) <= 10:

            window.update()
            insert_robot_msg("ChefBot: Cate retete ai dori sa vezi ? Te rog sa-mi spui un numar (maxim 20).")
            window.update()

            mesaj = ""
            window1.main_ok = True
            while window1.main_ok:
                window.update()
                mesaj = msg_entry.get()
                window.update()

            insert_user_msg(mesaj)
            window.update()

            numere = [int(s) for s in mesaj.split() if s.isdigit()]

            try:
                numarRetete = int(sum(numere) / len(numere))
                self.preluamretete(numarRetete, ing)
            except ValueError:
                insert_robot_msg("ChefBot: Nu ai introdus niciun numar ...")
                window.update()
                self.reteta()
            except ZeroDivisionError:
                insert_robot_msg("ChefBot: Nu ai introdus niciun numar ...")
                window.update()
                self.reteta()


        else:
            insert_robot_msg(
                "ChefBot: Te rog sa faci o alegere... Spune-mi niste ingrediente sau daca esti vegetarian!")
            window.update()
            self.reteta()

    def reteta(self):
        window.update()
        insert_robot_msg(
            "ChefBot: Sa vedem ce reteta doresti! Te rog sa-mi spui ceva ingrediente pe care vrei sa le folosesti.")
        window.update()
        insert_robot_msg(
            "ChefBot: De asemenea, imi poti spune si daca esti vegetarian pentru a explora cele 20 de optiuni pentru vegetarieni!.")
        window.update()

        window1.main_ok = True
        while window1.main_ok:
            window.update()
            mesaj = msg_entry.get()
            window.update()

        insert_user_msg(mesaj)
        window.update()

        results = self.model.predict([self.bag_of_words(mesaj, self.words)])[0]
        results_index = numpy.argmax(results)
        tag = self.labels[results_index]

        if results[results_index] > 0.80:
            for tg in self.data["intents"]:
                if tg['tag'] == tag:
                    responses = tg['responses']
            rsp = random.choice(responses)

            insert_robot_msg("ChefBot:" + str(rsp))
            window.update()
            self.retetaveg()

        else:
            self.retetaingrediente(mesaj)

    def start(self):
        window.update()
        insert_robot_msg(
            "ChefBot: Buna! Sunt un asistent specializat in retete culinare si te voi ajuta sa gasesti o reteta delicioasa!")
        self.reteta()
        window.update()


BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"


def run(window1):
    window1.update()


if __name__ == '__main__':
    bot = ChatBot()
    bot.start()
