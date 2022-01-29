import sys, json, time
from googletrans import Translator
from PySide6 import QtWidgets, QtGui
import speech_recognition as sr     #głos na tekst
import pyttsx3 as tts               #tekst na głos

# ścieżki do plików z frazamia do modułu mówienia
PATHS = 'frazy1.txt', 'frazy2.txt', 'frazy3.txt', 'frazy4.txt'

class MenuWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        temp = self._temp_load()
        self.main_points = temp['main_points']
        self.trial_number = temp['trial_number']
        self.mówienie = temp['mówienie']
        self.pisanie = temp['pisanie']
        main_layout = self._initialize_layout()
        self.setLayout(main_layout)
        self.setWindowTitle("Angielka")
        self.resize(240, 150)

    def _initialize_layout(self):    
        # blok informacji
        
        if self.trial_number > 0: efficiency = self.main_points/self.trial_number*100 
        else: efficiency = 0
        
        info_layout = QtWidgets.QVBoxLayout()
        self.points_label = QtWidgets.QLabel(f'Zdobyte punkty: {self.main_points}')
        self.points_label.setFont(QtGui.QFont('Sanserif', 14))
        self.trial_number_label = QtWidgets.QLabel(f'Liczba prób: {self.trial_number}, w tym:\n   mówienie: {self.mówienie}\n   pisanie: {self.pisanie}')
        self.trial_number_label.setFont(QtGui.QFont('Sanserif', 14))
        self.efficiency_label = QtWidgets.QLabel(f'Twoja sprawność: {int(efficiency)}%')
        self.efficiency_label.setFont(QtGui.QFont('Sanserif', 14))
        info_layout.addWidget(self.points_label)
        info_layout.addWidget(self.trial_number_label)
        info_layout.addWidget(self.efficiency_label)
        
        # blok przycisków do wyboru mówienie/pisanie
        head_layout = QtWidgets.QHBoxLayout()
        head_group_box = QtWidgets.QGroupBox()
        
        self.b5 = QtWidgets.QRadioButton("mówienie")
        self.b5.setChecked(True)
        head_layout.addWidget(self.b5)
            
        self.b6 = QtWidgets.QRadioButton("pisanie")
        head_layout.addWidget(self.b6)
        head_group_box.setLayout(head_layout)

        # blok przycisków wyboru trybu tłumaczenia
        top_layout = QtWidgets.QHBoxLayout()
        top_group_box = QtWidgets.QGroupBox() #klasa która grupuje radiobuttony, tzn. może być tylko jeden zaznaczony w danej grupie

        self.b1 = QtWidgets.QRadioButton("ang-->pol")
        self.b1.setChecked(True)
        top_layout.addWidget(self.b1)
            
        self.b2 = QtWidgets.QRadioButton("pol-->ang")
        top_layout.addWidget(self.b2)
        top_group_box.setLayout(top_layout)

        # blok przycisków wyboru ilości pytań
        down_layout = QtWidgets.QHBoxLayout()
        down_group_box = QtWidgets.QGroupBox()

        self.b3 = QtWidgets.QRadioButton("10 pytań")
        self.b3.setChecked(True)
        down_layout.addWidget(self.b3)
            
        self.b4 = QtWidgets.QRadioButton("20 pytań")
        down_layout.addWidget(self.b4)
        down_group_box.setLayout(down_layout)

        # klawisze
        button_translate = QtWidgets.QPushButton('TŁUMACZ')
        button_translate.setStyleSheet("background-color: yellow")
        button_translate.setFont(QtGui.QFont('Arial', 10,))
        button_translate.clicked.connect(self._translator)

        button = QtWidgets.QPushButton('ZACZYNAMY')
        button.setStyleSheet("background-color: green")
        button.setFont(QtGui.QFont('Arial', 10,))
        button.clicked.connect(self._start)

        # tworzenie okna MENU
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(info_layout)
        main_layout.addWidget(button_translate)
        main_layout.addWidget(top_group_box)
        main_layout.addWidget(head_group_box)
        main_layout.addWidget(down_group_box)
        main_layout.addWidget(button)
    
        return main_layout

    def _translator(self):
        if self.b1.isChecked():
            wybor = 'pl'
        else:
            wybor = 'en'

        self.translate = TranslateWidget(wybor)
        self.translate.resize(280, 100)
        self.translate.show()

    def _temp_load(self):
        try: 
            with open("temp.json", encoding="utf-8") as json_file:
                temp = json.load(json_file)
        except:
            temp = {"main_points": 0, "trial_number": 0, "mówienie": 0, "pisanie": 0}
            with open("temp.json", 'w') as json_file:
                json.dump(temp, json_file)
        return temp

    def temp_save(self, points, liczba_pytan, tryb):
        with open("temp.json", encoding="utf-8") as json_file:
            temp = json.load(json_file)
        
        temp['main_points'] += points
        temp['trial_number'] += liczba_pytan
        if tryb:
            temp['mówienie'] += liczba_pytan
        else:
            temp['pisanie'] += liczba_pytan
        
        a = temp['main_points']
        b = temp['trial_number']
        c = temp['mówienie']
        d = temp['pisanie']
        efficiency = a/b*100
        
        menu.points_label.setText(f'Zdobyte punkty: {a}')
        menu.points_label.repaint()
        menu.trial_number_label.setText(f'Liczba prób: {b}, w tym:\n   mówienie: {c}\n   pisanie: {d}')
        menu.trial_number_label.repaint()
        menu.efficiency_label.setText(f'Twoja sprawność: {int(efficiency)}%')
        menu.efficiency_label.repaint()
        
        with open("temp.json", 'w') as json_file:
            json.dump(temp, json_file)
        #print('zapisano temp')

    def tasowanie_pytan(self):    
        #uruchomienie json
        with open("slownik.json", encoding="utf-8") as json_file:
            words = json.load(json_file)
        #sortowanie słownika (bąbelkowe) od najniższej wartości "rate" czyli od najtrudniejszych wyrazów
        n=len(words)
        while n>1:
            zamien = False
            for i in range(0, n-1):
                if words[i]["rate"]>words[i+1]["rate"]:
                    words[i], words[i+1] = words[i+1], words[i]
                    zamien = True
            n -= 1
            if zamien == False:
                break
        return words

    def transform_list(self):
        #lista z wyrazami do przetłumaczenia
        self.quest = []  
        for i, word in enumerate(self.words):
            if i < self.liczba_pytan:
                self.quest.append(word['ang']) if self.wybor == 'pl' else self.quest.append(word['pol'])
            else: 
                break
        #lista z poprawnymi odpowiedziami
        self.correctAnswer = []
        for i, word in enumerate(self.words):
            if i < self.liczba_pytan:
                self.correctAnswer.append(word['pol']) if self.wybor == 'pl' else self.correctAnswer.append(word['ang'])
            else: 
                break
        return self.quest, self.correctAnswer

    def save_rate(self, words):  #zapisywanie danych "rate" do pliku słownika
        with open("slownik.json", 'w') as json_file:
            json.dump(words, json_file)  
        #print('zapisano słownik')

    def quit_msg(self, points, liczba_pytan, popr_odp):
        msg = QtWidgets.QMessageBox()
        msg.setText(f'Zdobywasz {points} pkt. \nOdpowiedziałaś poprawnie na {popr_odp/liczba_pytan*100} % pytań')
        msg.exec()

    def _start(self):
        self.words = self.tasowanie_pytan()
        if self.b1.isChecked():
            self.wybor = 'pl'
        else:
            self.wybor = ''

        if self.b3.isChecked():
            self.liczba_pytan = 10
        else:
            self.liczba_pytan = 20

        if self.b5.isChecked():
            self.talk = TalkWidget(self.words, self.liczba_pytan, self.wybor)
            self.talk.resize(450, 100)
            self.talk.show()
            self.talk.powitanie()
        else:
            self.write = WriteWidget(self.words, self.liczba_pytan, self.wybor)
            self.write.resize(280, 100)
            self.write.show()
        
class TalkWidget(QtWidgets.QWidget):
    def __init__(self, words, liczba_pytan, wybor):
        super().__init__()
        self.r = sr.Recognizer()
        self.engine = tts.init()
        self.pol_glos = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_PL-PL_PAULINA_11.0"
        self.ang_glos = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"

        self.words = words
        self.liczba_pytan = liczba_pytan
        self.wybor = wybor
        self.question_number = 0
        self.points = 0
        self.licznik_bledu = 0

        self.quest, self.correctAnswer = menu.transform_list()
        self.layout = self._initialize_layout()
        self.setLayout(self.layout)
        self.setWindowTitle("Angielka - Mówienie")

    def powitanie(self):
        self.engine.say(f'witaj w trybie mówienia, odpowiesz na {self.liczba_pytan} pytań')
        self.engine.say('wciśnij start gdy będziesz gotowa')
        self.engine.runAndWait()

    def _pobieranie_fraz(self, paths):
        frazy = []
        for path in paths:
            with open(path, "r", encoding="utf-8") as file: lines = file.readlines()
            fraza = []
            for line in lines: fraza.append(line.strip())
            frazy.append(fraza)
        return frazy

    def _initialize_layout(self):
        grid = QtWidgets.QGridLayout()
        self.pytanie_label = QtWidgets.QLabel(f'Pytanie nr: _/{self.liczba_pytan}')
        self.pytanie_label.setFont(QtGui.QFont('Sanserif', 13))
        self.punkty_label = QtWidgets.QLabel(f'     Punkty: {self.points}')
        self.punkty_label.setFont(QtGui.QFont('Sanserif', 13))
        self.word_label = QtWidgets.QLabel()
        self.word_label.setFont(QtGui.QFont('Sanserif', 16))
        arrows_label = QtWidgets.QLabel('         >>>')
        arrows_label.setFont(QtGui.QFont('Sanserif', 13))
        self.ans_label = QtWidgets.QLabel()
        self.ans_label.setFont(QtGui.QFont('Sanserif', 16))
        start_btn = QtWidgets.QPushButton('START')
        start_btn.setStyleSheet("background-color: green")
        start_btn.setFont(QtGui.QFont('Arial', 10,))
        start_btn.clicked.connect(self._asking)
        grid.addWidget(self.pytanie_label, 0, 1)
        grid.addWidget(self.punkty_label, 1, 1)
        grid.addWidget(self.word_label, 2, 0)
        grid.addWidget(arrows_label, 2, 1)
        grid.addWidget(self.ans_label, 2, 2)
        grid.addWidget(start_btn, 3, 1)

        return grid
        
    def _ask(self, i):
        self.word_label.setText('')
        self.ans_label.setText('')
        self.word_label.repaint()
        self.ans_label.repaint()

        if self.wybor == 'pl':
            self.engine.say("jak jest po polsku")
            self.engine.setProperty('voice', self.ang_glos)
            self.engine.say(self.quest[i])
            self.engine.setProperty('voice', self.pol_glos)
        else:
            self.engine.say("jak jest po angielsku")
            self.engine.say(self.quest[i])
        self.engine.runAndWait()

        self.word_label.setText(self.quest[i])
        self.word_label.repaint()

    def _asking(self):
        frazy = self._pobieranie_fraz(PATHS)
        popr_odp = 0
        for i, ans in enumerate(self.correctAnswer):
            self.question_number = i + 1
            self.pytanie_label.setText(f'Pytanie nr: {self.question_number}/{self.liczba_pytan}')
            self.punkty_label.setText(f'     Punkty: {self.points}')
            self.pytanie_label.repaint()
            self.punkty_label.repaint()
            self._ask(i)
            
            while True:
                odp = self._getText()
                if odp == "error":
                    break
                if odp is not None:
                    if odp in frazy[0]: #frazy1.txt zwroty wywłujące przejście do następnego pytania
                        self.engine.say("oj Luiza, tego nie wiesz, prawidłowa odpowiedź to")
                        if self.wybor == 'pl':
                            self.engine.say(ans)
                        else:
                            self.engine.setProperty('voice', self.ang_glos)
                            self.engine.say(ans)
                            self.engine.setProperty('voice',self.pol_glos)
                        self.engine.runAndWait()
                        self.words[i]["rate"] -= 0.5
                        self.ans_label.setText(ans)
                        self.ans_label.repaint()
                        time.sleep(2)
                        break 
                    elif odp in frazy[1]: # frazy2.txt zwroty zdenerwowania obrażające Angielkę :)
                        self.engine.say("chyba ty, czekam na odpowiedź")
                        self.engine.runAndWait()
                    elif odp in frazy[2]: # frazy3.txt zwroty zrezygnowania, niechęci do dalszego odpowiadania
                        self.engine.say(f"nie marudź, zostało ci już tylko {self.liczba_pytan - self.question_number} pytań, czekam na odpowiedź")
                        self.engine.runAndWait()
                    elif odp in frazy[3]: # frazy4.txt zwroty niezrozumienia pytania i prośby o powtórzenie          
                        self.engine.say("dobrze, to powtórzę")
                        self.engine.runAndWait()
                        self._ask(i)
                    elif odp == ans:
                        self.ans_label.setText(odp)
                        self.ans_label.repaint()
                        self.engine.say("bardzo dobrze")
                        self.engine.runAndWait()
                        popr_odp += 1
                        if self.wybor == 'pl':
                            self.words[i]["rate"] += 0.5
                            self.points += 1
                        else:
                            self.words[i]["rate"] += 1
                            self.points += 1.5
                        break
                    else:
                        self.engine.say("źle, zrozumiałam, że powiedziałaś")
                        self.words[i]["rate"] -= 0.5
                        if self.wybor == 'pl':
                            self.engine.say(odp)
                            self.ans_label.setText(odp)
                            self.ans_label.repaint()
                            self.engine.say('a powinno być')
                            self.engine.say(ans)
                        else:
                            self.engine.setProperty('voice', self.ang_glos)
                            self.engine.say(odp)
                            self.ans_label.setText(odp)
                            self.ans_label.repaint()
                            self.engine.setProperty('voice',self.pol_glos)
                            self.engine.say('a powinno być')
                            self.engine.setProperty('voice', self.ang_glos)
                            self.engine.say(ans)
                            self.engine.setProperty('voice',self.pol_glos)
                        self.engine.runAndWait()
                        self.ans_label.setText(ans)
                        self.ans_label.repaint()
                        time.sleep(2)
                        break            
        
        menu.save_rate(self.words)
        menu.temp_save(self.points, self.liczba_pytan, 1)
        self.close() #zamykanie okna instancji WriteWidget
        menu.quit_msg(self.points, self.liczba_pytan, popr_odp)     

    def _getText(self):
        try:
            with sr.Microphone() as source:
                audio = self.r.listen(source, timeout=3, phrase_time_limit=2)
                #wybór trybu pol>ang lub ang>pol
                if self.wybor == 'pl':
                    text = self.r.recognize_google(audio, language='pl-PL')
                else:
                    text = self.r.recognize_google(audio, language='en-GB')
                
                if text=="":
                    return None
                else:
                    self.licznik_bledu = 0
                    return text.lower()

        except sr.WaitTimeoutError:
            self.engine.say('czekam na odpowiedź')
            self.engine.runAndWait()
            return None
        except sr.UnknownValueError:
            if self.licznik_bledu > 1:
                self.engine.say('coś jest nie tak, nie mogę cię zrozumieć, spróbujmy z nowym wyrazem')
                self.engine.runAndWait()
                self.licznik_bledu = 0
                e="error"
                return e
            else:
                self.engine.say('nie rozumiem, powtórz')
                self.engine.runAndWait()
                self.licznik_bledu += 1
                return None
        except sr.RequestError:
            self.engine.say('czekaj, brak połączenia z internetem')
            self.engine.runAndWait()
            return None
        except:    
            return None

class TranslateWidget(QtWidgets.QWidget): # tłumaczenie słów przy pomocy google translator
    def __init__(self, wybor):
        super().__init__()
        self.wybor = wybor
        self.translator = Translator()
        self.layout = self._initialize_layout()
        self.setLayout(self.layout)
        self.setWindowTitle("Angielka - Tłumaczenie")

    def _initialize_layout(self):
                
        if self.wybor == 'en':
            src = 'j. polski'
            dest = 'j. angielski'
        else:
            dest = 'j. polski'
            src = 'j. angielski'

        grid = QtWidgets.QGridLayout()
        name_to_translate = QtWidgets.QLabel(src)
        name_to_translate.setFont(QtGui.QFont('Sanserif', 13))
        name_translated = QtWidgets.QLabel(dest)
        name_translated.setFont(QtGui.QFont('Sanserif', 13))
        self.entry_to_translate = QtWidgets.QLineEdit()
        self.label_translated = QtWidgets.QLabel()
        arrows = QtWidgets.QLabel("        >>>         ")
        
        button = QtWidgets.QPushButton('TŁUMACZ')
        button.setStyleSheet("background-color: green")
        button.setFont(QtGui.QFont('Arial', 10,))
        button.clicked.connect(self._translate_word)

        grid.addWidget(name_to_translate, 0, 0)
        grid.addWidget(name_translated, 0, 2)
        grid.addWidget(self.entry_to_translate, 1, 0)
        grid.addWidget(arrows, 1, 1)
        grid.addWidget(self.label_translated, 1, 2)
        grid.addWidget(button, 2, 1)
        return grid

    def _translate_word(self):
        word = self.entry_to_translate.text()
        if self.wybor == 'pl':
            translated_word = self.translator.translate(word, src='en', dest='pl').text
        else:
            translated_word = self.translator.translate(word, src='pl', dest='en').text
        self.label_translated.setText(translated_word)
        self.label_translated.repaint()

class WriteWidget(QtWidgets.QWidget): # pisanie
    def __init__(self, words, liczba_pytan, wybor):
        super().__init__()
        self.words = words
        self.liczba_pytan = liczba_pytan
        self.wybor = wybor
        
        self.quest, self.correctAnswer = menu.transform_list()
        self.layout = self._initialize_layout()
        self.setLayout(self.layout)
        self.setWindowTitle("Angielka - Pisanie")
                
    def _check_translation(self):
        self.points = 0
        popr_odp = 0
               
        # sprawdzanie czy odpowiedź jest prawidłowa i naliczanie punktów
        for i, answer in enumerate(self.answers):
            if answer.text().lower()==self.correctAnswer[i]:
                popr_odp += 1
                if self.wybor == 'pl':
                    self.words[i]["rate"] += 0.5
                    self.points += 1  
                else:
                    self.words[i]["rate"] += 1
                    self.points += 1.5
            else:
                self.words[i]["rate"] -= 1
      
        menu.save_rate(self.words)
        menu.temp_save(self.points, self.liczba_pytan, 0)
        self.close() #zamykanie okna instancji WriteWidget
        
        self.answerWindow = AnswerWindow(self.quest, self.answers, self.correctAnswer, self.points, self.liczba_pytan, popr_odp)
        self.answerWindow.show()
            
    def _initialize_layout(self):
        self.answers=[]

        grid = QtWidgets.QGridLayout()
        for row, word in enumerate(self.quest):
            label_number = QtWidgets.QLabel(str(row+1))
            label_number.setFont(QtGui.QFont('Sanserif', 13))
            label_word = QtWidgets.QLabel(word)
            label_word.setFont(QtGui.QFont('Sanserif', 13,))
            label_odp = QtWidgets.QLineEdit()
            self.answers.append(label_odp)
            grid.addWidget(label_number, row, 0)
            grid.addWidget(label_word, row, 1)
            grid.addWidget(label_odp, row, 2)
              
        button = QtWidgets.QPushButton('SPRAWDŹ')
        button.setStyleSheet("background-color: green")
        button.setFont(QtGui.QFont('Arial', 10,))
        button.clicked.connect(self._check_translation)
        grid.addWidget(button, len(self.quest), 2)
        
        return grid

# okno wyświetlające udzielone odpowiedzi i poprawne odpowiedzi
class AnswerWindow(QtWidgets.QWidget):
    def __init__(self, quest, answers, correctAnswer, points, liczba_pytan, popr_odp):
        super().__init__()
        self.quest = quest
        self.answers = answers
        self.correctAnswer = correctAnswer
        self.points = points
        self.liczba_pytan = liczba_pytan
        self.popr_odp = popr_odp
        self.layout = self._initialize_answer_window()
        self.setLayout(self.layout)
        self.setWindowTitle("Angielka - Pisanie - Odpowiedzi")

    def _initialize_answer_window(self):

        grid = QtWidgets.QGridLayout()
        for row, word in enumerate(self.quest):
            label_number = QtWidgets.QLabel(str(row+1))
            label_number.setFont(QtGui.QFont('Sanserif', 13))
            label_word = QtWidgets.QLabel(word)
            label_word.setFont(QtGui.QFont('Sanserif', 13))
            label_odp = QtWidgets.QLabel(self.answers[row].text())
            label_odp.setFont(QtGui.QFont('Sanserif', 13))
            label_correct_answer = QtWidgets.QLabel(self.correctAnswer[row])
            label_correct_answer.setStyleSheet("background-color: green") if self.answers[row].text().lower() == self.correctAnswer[row] else label_correct_answer.setStyleSheet("background-color: red")
            label_correct_answer.setFont(QtGui.QFont('Sanserif', 13))
            grid.addWidget(label_number, row, 0)
            grid.addWidget(label_word, row, 1)
            grid.addWidget(label_odp, row, 2)
            grid.addWidget(label_correct_answer, row, 3)

        button = QtWidgets.QPushButton('KONIEC')
        button.setStyleSheet("background-color: purple")
        button.setFont(QtGui.QFont('Arial', 10,))
        button.clicked.connect(self.quit)
        grid.addWidget(button, len(self.quest), 2)
        return grid  

    def quit(self):
        self.close()
        menu.quit_msg(self.points, self.liczba_pytan, self.popr_odp)

if __name__=='__main__':
    app=QtWidgets.QApplication([])
    menu = MenuWidget()
    menu.show()
    sys.exit(app.exec())
    