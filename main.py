from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import pandas
import random
import os

BACKGROUND_COLOR = "#B1DDC6"
ORIGINAL_WORDS_FILE = "data/greek_words.csv"
current_card = {}
to_learn = []
is_flipped = False
front_lang = "English"   # γλώσσα που ρωτάει η κάρτα
back_lang = "Greek"      # γλώσσα της μετάφρασης
progress_file = ""       # αρχείο προόδου της γλώσσας που επιλέχθηκε
flip_timer = None

#____________Load / Reset Words____________


def save_progress():
    data = pandas.DataFrame(to_learn)
    data.to_csv(progress_file, index=False)


def reset_words():
    #Σβηνει το αρχειο με τις αγνωστες λεξεις(λιστα προοδου)
    global to_learn
    original_data = pandas.read_csv(ORIGINAL_WORDS_FILE)
    to_learn = original_data.to_dict(orient="records")
    random.shuffle(to_learn)
    if os.path.exists(progress_file):
        os.remove(progress_file)


def load_words():
    #Επιλογη λεξεων λωσσας
    global to_learn
    try:
        data = pandas.read_csv(progress_file)
    except (FileNotFoundError, pandas.errors.EmptyDataError):
        reset_words()
    else:
        to_learn = data.to_dict(orient="records")
        if not to_learn:
            reset_words()

#____________Next Card____________


def next_card():
    global current_card, flip_timer, is_flipped
    window.after_cancel(flip_timer)
    is_flipped = False
    current_card = to_learn[0]   # πάντα η πρώτη λέξη της ουράς
    canvas.itemconfig(card_title, text=front_lang, fill="black")
    canvas.itemconfig(card_word, text=current_card[front_lang], fill="black")
    canvas.coords(card_word, 400, 263)
    canvas.coords(word_flag_item, 120, 263)
    canvas.itemconfig(translate_label, text="")
    canvas.itemconfig(card_translation, text="")
    canvas.itemconfig(translation_flag_item, state=HIDDEN)
    canvas.itemconfig(card_background, image=front_card_img)
    next_button.config(state=DISABLED)
    flip_timer = window.after(3000, func=flip_card)

#____________Flip Card__________


def flip_card():
    global is_flipped
    is_flipped = True
    canvas.itemconfig(card_title, fill="white")
    canvas.itemconfig(card_word, fill="white")
    canvas.coords(card_word, 400, 215)
    canvas.coords(word_flag_item, 120, 215)
    canvas.itemconfig(translate_label, text="Μετάφραση / Translate", fill="white")
    canvas.itemconfig(card_translation, text=current_card[back_lang], fill="white")
    canvas.itemconfig(translation_flag_item, state=NORMAL)
    canvas.itemconfig(card_background, image=back_card_img)
    next_button.config(state=NORMAL)

#____________Unknown Word___________


def move_to_end():
    #Η αγνωστη λεξη μπαινει στο τελος της λισταας ωστε να ξανα εξεταστει
    to_learn.append(to_learn.pop(0))
    save_progress()
    next_card()


def is_unknown():
    window.after_cancel(str(flip_timer))
    if is_flipped:
        move_to_end()
    else:
        flip_card()

#____________Known Word___________


def is_known():
    to_learn.pop(0)
    print(len(to_learn))
    if len(to_learn) == 0:
        window.after_cancel(flip_timer)
        restart = messagebox.askyesno(
            title="Reset",
            message="Τις ξέρεις όλες τις λέξεις! Θες να ξεκινήσεις πάλι από την αρχή;"
        )
        if restart:
            reset_words()
        else:
            window.destroy()
            return
    else:
        save_progress()
    next_card()

#____________Start Game____________


def start_game(language):
    #Επιλογη γλωσσας
    global front_lang, back_lang, progress_file
    front_lang = language
    back_lang = "Greek" if language == "English" else "English"
    progress_file = f"data/words_to_learn_{language.lower()}.csv"
    load_words()
    menu_frame.destroy()
    build_card_ui()
    next_card()

#____________Card UI__________________


def build_card_ui():
    global canvas, front_card_img, back_card_img
    global card_background, card_title, card_word, card_translation, translate_label
    global word_flag_item, translation_flag_item
    global x_image, c_image, next_button, flip_timer

    canvas = Canvas(width=800, height=526)
    front_card_img = PhotoImage(file="images/card_front.png")
    back_card_img = PhotoImage(file="images/card_back.png")
    card_background = canvas.create_image(400, 263, image=front_card_img)
    card_title = canvas.create_text(400, 150, text="", font=("Arial", 40, "italic"))
    card_word = canvas.create_text(400, 263, text="", font=("Arial", 40, "bold"))
    translate_label = canvas.create_text(400, 275, text="", font=("Arial", 20, "italic"))
    card_translation = canvas.create_text(400, 340, text="", font=("Arial", 40, "bold"))

    word_flag_item = canvas.create_image(120, 263, image=small_flags[front_lang])
    translation_flag_item = canvas.create_image(120, 340, image=small_flags[back_lang],
                                                state=HIDDEN)

    canvas.config(bg=BACKGROUND_COLOR, highlightthickness=0)
    canvas.grid(row=0, column=0, columnspan=2)

    x_image = PhotoImage(file="images/wrong.png")
    x_button = Button(image=x_image,
                      highlightthickness=0,
                      command=is_unknown)
    x_button.grid(row=1, column=0)

    c_image = PhotoImage(file="images/right.png")
    c_button = Button(image=c_image,
                      highlightthickness=0,
                      command=is_known)
    c_button.grid(row=1, column=1)

    next_button = Button(text="Next",
                         font=("Arial", 20, "bold"),
                         width=10,
                         state=DISABLED,
                         command=move_to_end)
    next_button.grid(row=2, column=0, columnspan=2, pady=(20, 0))

    flip_timer = window.after(3000, func=flip_card)

#_____________ΥΙ__________________


window = Tk()
window.title("Flashy_dev")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)


def load_flag(path, size):
    img = Image.open(path).resize(size)
    return ImageTk.PhotoImage(img)


greek_flag_img = load_flag("images/greek_flag.png", (240, 160))
uk_flag_img = load_flag("images/uk_flag.png", (240, 160))
greek_small = load_flag("images/greek_flag.png", (60, 40))
uk_small = load_flag("images/uk_flag.png", (60, 40))
small_flags = {"Greek": greek_small, "English": uk_small}

menu_frame = Frame(window, bg=BACKGROUND_COLOR)
menu_frame.grid(row=0, column=0)

Label(menu_frame, text="Διάλεξε τη γλώσσα που θέλεις να μάθεις",
      font=("Arial", 28, "bold"), bg=BACKGROUND_COLOR).grid(
    row=0, column=0, columnspan=2, pady=(0, 10))
Label(menu_frame, text="Choose the language you want to learn",
      font=("Arial", 18, "italic"), bg=BACKGROUND_COLOR).grid(
    row=1, column=0, columnspan=2, pady=(0, 30))

greek_flag_label = Label(menu_frame, image=greek_flag_img, bd=2, relief="solid",
                         cursor="hand2")
greek_flag_label.grid(row=2, column=0, padx=30)
greek_flag_label.bind("<Button-1>", lambda event: start_game("Greek"))

greek_label = Label(menu_frame, text="Ελληνικά / Greek", font=("Arial", 20, "bold"),
                    bg=BACKGROUND_COLOR, cursor="hand2")
greek_label.grid(row=3, column=0, pady=(10, 0))
greek_label.bind("<Button-1>", lambda event: start_game("Greek"))

uk_flag_label = Label(menu_frame, image=uk_flag_img, bd=2, relief="solid",
                      cursor="hand2")
uk_flag_label.grid(row=2, column=1, padx=30)
uk_flag_label.bind("<Button-1>", lambda event: start_game("English"))

uk_label = Label(menu_frame, text="Αγγλικά / English", font=("Arial", 20, "bold"),
                 bg=BACKGROUND_COLOR, cursor="hand2")
uk_label.grid(row=3, column=1, pady=(10, 0))
uk_label.bind("<Button-1>", lambda event: start_game("English"))

window.mainloop()