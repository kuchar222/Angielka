import json
import tkinter as tk

with open("slownik.json", encoding="utf-8") as json_file:
    slownik = json.load(json_file)

def rate():
    rate = []
    for slowo in slownik:
        rate.append(slowo["rate"])
    return min(rate)

liczba_pozycji = len(slownik)
dodane_pozycje = 0
usuniete_pozycje = 0

def zerowanie(slownik):
    for slowo in slownik:
        slowo["rate"] = 0
    print("zresetowano słownik")
    zeruj_button.config(bg="red")

def dodawanie_wyrazow(slownik, ang_wyraz, pol_wyraz):
    global dodane_pozycje
    zapis = True
    for slowo in slownik:
        if ang_wyraz == slowo["ang"] or pol_wyraz == slowo["pol"]:
            print("pozycja już istnieje")
            zapis = False
            break

    if zapis == True:
        slownik.append({"ang": ang_wyraz, "pol": pol_wyraz, "rate": 0})
        print(f"dodano pozycję: {ang_wyraz} > {pol_wyraz}")
        dodane_pozycje += 1
        entry1.set("")
        entry2.set("")
        wielkosc_label.config(text=(f"Ilość pozycji słownika: {liczba_pozycji} + {dodane_pozycje}"))

def usuwanie_wyrazow(slownik, wyraz):
    global liczba_pozycji
    global usuniete_pozycje
    usuwanie = False

    for slowo in slownik:
        if wyraz == slowo["ang"] or wyraz == slowo["pol"]:
            print("usunięto pozycję: " + slowo["ang"] + " > " + slowo["pol"])
            slownik.remove(slowo)
            usuwanie = True
            usuniete_pozycje += 1
            wielkosc_label.config(
                text=(
                    "Ilość pozycji słownika: {} - {}".format(
                        liczba_pozycji, usuniete_pozycje
                    )
                )
            )
            entry1.set("")
            entry2.set("")
            break
    if usuwanie == False:
        print(f"nie znaleziono wyrazu {wyraz}")

def zapisz(slownik):
    global dodane_pozycje
    global liczba_pozycji
    global usuniete_pozycje

    with open("slownik.json", "w") as json_file:
        json.dump(slownik, json_file)
    print("zapisano słownik")

    liczba_pozycji = liczba_pozycji + dodane_pozycje - usuniete_pozycje
    dodane_pozycje = 0
    usuniete_pozycje = 0
    wielkosc_label.config(text=("Ilość pozycji słownika: {}".format(liczba_pozycji)))
    rate_label.config(text=f"Minimalny rate: {rate()}")
    zeruj_button.config(bg="yellow")

slownik_window = tk.Tk()
slownik_window.title("Anglik-Słownik")
slownik_window.geometry("260x220+500+200")
wielkosc_frame = tk.LabelFrame(slownik_window, text="Wielkość słownika")
wielkosc_frame.pack(fill="both", padx=10, pady=10)
wielkosc_label = tk.Label(
    wielkosc_frame, text=("Ilość pozycji słownika: {}".format(liczba_pozycji))
)
wielkosc_label.pack(padx=5, pady=2)
rate_label = tk.Label(wielkosc_frame, text=f"Minimalny rate: {rate()}")
rate_label.pack(padx=5, pady=2)
pole_danych = tk.LabelFrame(slownik_window, text="Podaj wyrazy")
pole_danych.pack(fill="both", padx=10, pady=3)
ang_wyraz_label = tk.Label(pole_danych, text="Word: ")
pol_wyraz_label = tk.Label(pole_danych, text="Wyraz:")
entry1 = tk.StringVar()
entry2 = tk.StringVar()
ang_wyraz_entry = tk.Entry(pole_danych, textvariable=entry1)
pol_wyraz_entry = tk.Entry(pole_danych, textvariable=entry2)
ang_wyraz_label.grid(row=0, column=0, padx=5, pady=5)
ang_wyraz_entry.grid(row=0, column=1, padx=5, pady=5)
pol_wyraz_label.grid(row=1, column=0, padx=5, pady=5)
pol_wyraz_entry.grid(row=1, column=1, padx=5, pady=5)

button_frame = tk.Frame(slownik_window)
button_frame.pack(padx=10, pady=2)
dodaj_button = tk.Button(
    button_frame,
    text="DODAJ",
    command=lambda: dodawanie_wyrazow(slownik, entry1.get(), entry2.get()),
)
usuń_button = tk.Button(
    button_frame,
    text="USUŃ",
    command=lambda: usuwanie_wyrazow(slownik, entry1.get() or entry2.get()),
)
zeruj_button = tk.Button(
    button_frame, text="ZERUJ", command=lambda: zerowanie(slownik), bg="yellow"
)
zapisz_button = tk.Button(button_frame, text="ZAPISZ", command=lambda: zapisz(slownik))
dodaj_button.grid(row=0, column=0, padx=5, pady=5)
usuń_button.grid(row=0, column=1, padx=5, pady=5)
zeruj_button.grid(row=0, column=2, padx=5, pady=5)
zapisz_button.grid(row=0, column=3, padx=5, pady=5)

slownik_window.mainloop()