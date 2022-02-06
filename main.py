import sys, json, time
from datetime import timedelta, date
from googletrans import Translator
from PySide6.QtGui import QFont, QPixmap, QIcon
from PySide6 import QtWidgets
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Slot, QSize, Qt
import speech_recognition as sr     #głos na tekst
import pyttsx3 as tts               #tekst na głos

# ścieżki do plików z frazamia do modułu mówienia
PATHS = 'frazy1.txt', 'frazy2.txt', 'frazy3.txt', 'frazy4.txt'

class MenuWidget(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # ustawienia początkowe programu
        self.wybor = ''  # pol>ang 
          
        # ładowanie głównego okna aplikacji z GUI
        loader = QUiLoader()
        self.window = loader.load("GUI/menu.ui", self)

        # tworzenie obiektów grafiki
        self.pix_ang = QPixmap(r'img\united_kingdom_round_icon_64.png')
        self.pix_pol = QPixmap(r'img\poland_round_icon_64.png')
        pix_jezykBtn = QPixmap(r'img\transfer_green.png')

        # ładowanie pliku temp do okna aplikacji i aktualizacja okienka statystka
        self._aktualizacja_statystyki()
        self._wybierz_jezyk()
        
        # przypisanie akcji do przycisków
        self.window.jezykBtn.setIcon(QIcon(pix_jezykBtn))
        self.window.jezykBtn.setIconSize(QSize(30, 30))
        self.window.jezykBtn.clicked.connect(self._wybierz_jezyk)
        self.window.startBtn.clicked.connect(self._start)
        self.window.tlumaczBtn.clicked.connect(self._translator)
           
        # uruchomienie okna
        self.window.show()

    def _aktualizacja_statystyki(self):
        self.temp = self._temp_load()
        sprawnosc = self._wylicz_sprawnosc(self.temp)
        # w przypadku braku w plik temp danych o ostatniej wizycie wystawiam komunikat "nie pamiętam"
        try:
            wizyta = self._kiedy_ostatnia_wizyta(self.temp['ostatnia_wizyta'])
        except:
            wizyta = 'NIE PAMIĘTAM'
        self.window.mainPointsLCD.display(self.temp['main_points'])
        self.window.trialNumberLCD.display(self.temp['trial_number'])
        self.window.sprawnoscBar.setValue(sprawnosc)
        self.window.wizytaLabel.setText(wizyta)

    def _kiedy_ostatnia_wizyta(self, data):
        # funkcja zwraca termin ostatniego uruchomienia aplikacji
        timeStamp = date.fromisoformat(data)
        ileMinelo = date.today()-timeStamp
        if ileMinelo > timedelta(days=2):
            return f'{ileMinelo.days} DNI TEMU'
        elif ileMinelo == timedelta(days=1):
            return 'WCZORAJ'
        elif ileMinelo == timedelta(days=2):
            return 'PRZEDWCZORAJ'
        else:
            return 'DZISIAJ'

    def _wylicz_sprawnosc(self, temp):
        # funkcja zwraca sprawnosc oddawanych odpowiedzi
        if temp['trial_number'] > 0: 
            return temp['main_points']/temp['trial_number']*100 
        else:
            return 0

    @Slot()
    def _wybierz_jezyk(self):
        if self.wybor == 'pl':
            self.wybor = ''
            self.window.jezykZ.setPixmap(self.pix_pol)
            self.window.jezykNa.setPixmap(self.pix_ang)
        else:
            self.wybor = 'pl'
            self.window.jezykZ.setPixmap(self.pix_ang)
            self.window.jezykNa.setPixmap(self.pix_pol)

    # def _ustaw_flagi(self):
    #     if self.wybor == 'pl':
    
    @Slot()
    def _translator(self):
        if self.wybor == 'pl':
            wybor = 'pl'
        else:
            wybor = 'en'

        self.translate = TranslateWidget(wybor)
        self.translate.setWindowTitle('Angielka - Tłumaczenie')
        self.translate.show()

    def _temp_load(self):
        try: 
            with open("temp.json", encoding="utf-8") as json_file:
                temp = json.load(json_file)
        except:
            timeStamp = date.today().isoformat()
            temp = {"main_points": 0, "trial_number": 0, "mówienie": 0, "pisanie": 0, "ostatnia_wizyta": timeStamp}
            with open("temp.json", 'w') as json_file:
                json.dump(temp, json_file)
        return temp

    def temp_save(self, points, liczba_pytan):
        # funkcja zapisuje do pliku temp aktualne punkty, liczbę prób z podziałem na tryb mówienia i pisania
        
        with open("temp.json", encoding="utf-8") as json_file:
            temp = json.load(json_file)
        
        temp['main_points'] += points
        temp['trial_number'] += liczba_pytan
        if self.window.rBtnMowienie.isChecked():
            temp['mówienie'] += liczba_pytan
        else:
            temp['pisanie'] += liczba_pytan
        temp['ostatnia_wizyta'] = date.today().isoformat()
                
        with open("temp.json", 'w') as json_file:
            json.dump(temp, json_file)
        
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
        # funkcja przygotowuje liste wyrazów do przetłumaczenia zgodnie z wybraną liczbą pytań i językiem 
        
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

    def save_rate(self, words):  
        #zapisywanie danych "rate" do pliku słownika
        with open("slownik.json", 'w') as json_file:
            json.dump(words, json_file)  
        
    def quit_msg(self, points, liczba_pytan, popr_odp):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle('Podsumowanie')
        msg.setText(f'Zdobywasz {points} pkt. \nOdpowiedziałaś poprawnie na {int(popr_odp/liczba_pytan*100)} % pytań')
        msg.exec()
    
    def _zmien_tryb_na_msg(self, tryb):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setWindowTitle('Info')
        msg.setText(f'Za często korzystasz z tej opcji, spróbuj teraz zmienić tryb na {tryb}')
        msg.exec()

    @Slot()
    def _start(self):
        self.liczba_pytan = self.window.liczbaPytan.value()
        self.words = self.tasowanie_pytan()
        self.temp = self._temp_load()

        if self.window.rBtnMowienie.isChecked():    # wybrano mówienie
            # sprawdzenie warunku czy za żadko nie było pisania
            if self.temp['pisanie']/self.temp['trial_number'] <= 0.2:
                self._zmien_tryb_na_msg('PISANIE')    
            else:
                self.talk = TalkWidget(self.words, self.liczba_pytan, self.wybor)
                self.talk.setWindowTitle('Angielka - Mówienie')
                self.talk.show()
        else:   # wybrano pisanie
            # sprawdzenie warunku czy za żadko nie było mówienia
            if self.temp['mówienie']/self.temp['trial_number'] <= 0.2:
                self._zmien_tryb_na_msg('MÓWIENIE')
            else:
                self.write = WriteWidget(self.words, self.liczba_pytan, self.wybor)
                self.write.setWindowTitle('Angielka - Pisanie')
                self.write.resize(280, 100)
                self.write.show()
        
class TalkWidget(QtWidgets.QMainWindow):
    def __init__(self, words, liczba_pytan, wybor):
        super().__init__()
        self.r = sr.Recognizer()
        self.engine = tts.init()
        self.pol_glos = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_PL-PL_PAULINA_11.0"
        self.ang_glos = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
        
        # przypisanie zmiennych lokalnych
        self.words = words
        self.liczba_pytan = liczba_pytan
        self.wybor = wybor
        self.question_number = 0
        self.points = 0
        self.licznik_bledu = 0
        self.quest, self.correctAnswer = menu.transform_list()
       
        # ładowanie głównego okna aplikacji z GUI
        loader = QUiLoader()
        self.window = loader.load("GUI/mowienie.ui", self)
        self.window.start_btn.clicked.connect(self._asking)
        self.window.pytanie_label.setText(f' _ z {self.liczba_pytan}')
        
        self.powitanie()
        
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
        
    def _ask(self, i):
        self.window.word_label.setText('')
        self.window.ans_label.setText('')
        self.window.repaint()
        if self.wybor == 'pl':
            self.engine.say("jak jest po polsku")
            self.engine.setProperty('voice', self.ang_glos)
            self.engine.say(self.quest[i])
            self.engine.setProperty('voice', self.pol_glos)
        else:
            self.engine.say("jak jest po angielsku")
            self.engine.say(self.quest[i])
        self.engine.runAndWait()

        self.window.word_label.setText(self.quest[i])
        self.window.repaint()
        
    @Slot()
    def _asking(self):
        frazy = self._pobieranie_fraz(PATHS)
        popr_odp = 0
        for i, ans in enumerate(self.correctAnswer):
            self.question_number = i + 1
            self.window.pytanie_label.setText(f' {self.question_number} z {self.liczba_pytan}')
            self.window.repaint()
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
                        self.window.ans_label.setText(ans)
                        self.window.repaint()
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
                        self.window.ans_label.setStyleSheet("color : green")
                        self.window.ans_label.setText(odp)
                        self.window.repaint()
                        self.engine.say("bardzo dobrze")
                        self.engine.runAndWait()
                        popr_odp += 1
                        if self.wybor == 'pl':
                            self.words[i]["rate"] += 0.5
                            self.points += 1
                        else:
                            self.words[i]["rate"] += 1
                            self.points += 1.5
                        self.window.punkty_label.setValue(popr_odp/self.liczba_pytan*100)
                        self.window.repaint()
                        break
                    else:
                        self.engine.say("źle, zrozumiałam, że powiedziałaś")
                        self.words[i]["rate"] -= 0.5
                        if self.wybor == 'pl':
                            self.engine.say(odp)
                            self.window.ans_label.setStyleSheet("color : red")
                            self.window.ans_label.setText(odp)
                            self.window.repaint()
                            self.engine.say('a powinno być')
                            self.engine.say(ans)
                        else:
                            self.engine.setProperty('voice', self.ang_glos)
                            self.engine.say(odp)
                            self.window.ans_label.setStyleSheet("color : red")
                            self.window.ans_label.setText(odp)
                            self.window.repaint()
                            self.engine.setProperty('voice',self.pol_glos)
                            self.engine.say('a powinno być')
                            self.engine.setProperty('voice', self.ang_glos)
                            self.engine.say(ans)
                            self.engine.setProperty('voice',self.pol_glos)
                        self.engine.runAndWait()
                        self.window.ans_label.setStyleSheet("color : green")
                        self.window.ans_label.setText(ans)
                        self.window.repaint()
                        time.sleep(2)
                        break            
        
        menu.save_rate(self.words)
        menu.temp_save(self.points, self.liczba_pytan)
        menu._aktualizacja_statystyki()
        self.destroy() #zamykanie okna instancji WriteWidget
        menu.quit_msg(self.points, self.liczba_pytan, popr_odp)     

    def _getText(self):
        try:
            with sr.Microphone() as source:
                audio = self.r.listen(source, timeout=3, phrase_time_limit=3)
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
       
        # tworzenie obiektów grafiki
        self.pix_ang = QPixmap(r'img\united_kingdom_flag_background_64.png')
        self.pix_pol = QPixmap(r'img\poland_flag_background_64.png')
        pix_transfer = QPixmap(r'img\transfer_blue.png')

        loader = QUiLoader()
        self.window = loader.load("GUI/translator.ui", self)
        self.window.setWindowTitle("Angielka - Tłumaczenie")
        
        if self.wybor == 'en':
            self.window.name_to_translate.setPixmap(self.pix_pol)
            self.window.name_translated.setPixmap(self.pix_ang)
        else:
            self.window.name_to_translate.setPixmap(self.pix_ang)
            self.window.name_translated.setPixmap(self.pix_pol)
        
        self.window.pushButton.clicked.connect(self._translate_word)
        self.window.zmienBtn.setIcon(QIcon(pix_transfer))
        self.window.zmienBtn.setIconSize(QSize(48, 48))
        self.window.zmienBtn.clicked.connect(self._zmien_jezyk)        
        self.window.show()

    @Slot()
    def _zmien_jezyk(self):
        if self.wybor == 'pl':
            self.window.name_to_translate.setPixmap(self.pix_pol)
            self.window.name_translated.setPixmap(self.pix_ang) 
            self.wybor = 'en'
        else:
            self.window.name_to_translate.setPixmap(self.pix_ang)
            self.window.name_translated.setPixmap(self.pix_pol)   
            self.wybor = 'pl' 

    @Slot()
    def _translate_word(self):
        word = self.window.entry_to_translate.text()
        if self.wybor == 'pl':
            translated_word = self.translator.translate(word, src='en', dest='pl').text
        else:
            translated_word = self.translator.translate(word, src='pl', dest='en').text
        self.window.label_translated.setText(translated_word)

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
        menu.temp_save(self.points, self.liczba_pytan)
        menu._aktualizacja_statystyki()
        self.destroy() #zamykanie okna instancji WriteWidget
        
        self.answerWindow = AnswerWindow(self.quest, self.answers, self.correctAnswer, self.points, self.liczba_pytan, popr_odp)
        self.answerWindow.show()
            
    def _initialize_layout(self):
        self.answers=[]

        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(15)
        grid.setContentsMargins(5, 5, 5, 5)
        for row, word in enumerate(self.quest):
            label_number = QtWidgets.QLabel(str(row+1))
            label_number.setFont(QFont('Sanserif', 14))
            label_word = QtWidgets.QLabel(word)
            label_word.setFont(QFont('Sanserif', 14))
            label_odp = QtWidgets.QLineEdit()
            label_odp.setFont(QFont('Sanserif', 14))
            self.answers.append(label_odp)
            grid.addWidget(label_number, row, 0)
            grid.addWidget(label_word, row, 1)
            grid.addWidget(label_odp, row, 2)
              
        button = QtWidgets.QPushButton('SPRAWDŹ')
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        button.setStyleSheet(u"background-color: rgb(85, 170, 0);\n"
"color: rgb(255, 255, 127);\n"
"border-radius: 15px;")
        button.setFont(font)
        button.setMinimumSize(QSize(130, 35))
        button.setMaximumSize(QSize(130, 35))
        button.setDefault(True)
        button.clicked.connect(self._check_translation)
                
        h_frame = QtWidgets.QHBoxLayout()
        h_frame.setAlignment(Qt.AlignCenter)
        h_frame.addWidget(button)
        
        frame = QtWidgets.QVBoxLayout()
        frame.addLayout(grid)
        frame.addLayout(h_frame)

        return frame

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
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(10)
        grid.setContentsMargins(5, 5, 5, 5)
        for row, word in enumerate(self.quest):
            label_number = QtWidgets.QLabel(str(row+1))
            label_number.setFont(QFont('Sanserif', 14))
            label_word = QtWidgets.QLabel(word)
            label_word.setFont(QFont('Sanserif', 14))
            label_odp = QtWidgets.QLabel(self.answers[row].text())
            label_odp.setFont(QFont('Sanserif', 14))
            label_correct_answer = QtWidgets.QLabel(self.correctAnswer[row])
            label_correct_answer.setStyleSheet("color: green") if self.answers[row].text().lower() == self.correctAnswer[row] else label_correct_answer.setStyleSheet("color: red")
            label_correct_answer.setFont(QFont('Sanserif', 14))
            grid.addWidget(label_number, row, 0)
            grid.addWidget(label_word, row, 1)
            grid.addWidget(label_odp, row, 2)
            grid.addWidget(label_correct_answer, row, 3)

        button = QtWidgets.QPushButton('KONIEC')
        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(True)
        button.setStyleSheet(u"background-color: rgb(85, 170, 0);\n"
"color: rgb(255, 255, 127);\n"
"border-radius: 15px;")
        button.setFont(font2)
        button.setMinimumSize(QSize(130, 35))
        button.setMaximumSize(QSize(130, 35))
        button.setDefault(True)
        button.clicked.connect(self.quit)
        
        h_frame = QtWidgets.QHBoxLayout()
        h_frame.setAlignment(Qt.AlignCenter)
        h_frame.addWidget(button)
        
        frame = QtWidgets.QVBoxLayout()
        frame.addLayout(grid)
        frame.addLayout(h_frame)

        return frame  

    def quit(self):
        self.destroy()
        menu.quit_msg(self.points, self.liczba_pytan, self.popr_odp)

if __name__=='__main__':
    app=QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(False)
    menu = MenuWidget()
    sys.exit(app.exec()) 