from tkinter import *
from functools import partial


def afficherMenuAccueil():

    MAIN_WIN_H = 751
    MAIN_WIN_W = 600
    GAME_WIN_H = 700
    GAME_WIN_W = 1000

    fenetre = Tk()
    fenetre.title('Schotten Totten')

    main_frame = Frame(fenetre, height=MAIN_WIN_H,
                       width=MAIN_WIN_W, borderwidth=3, relief=GROOVE,)
    main_frame.pack(side=TOP)

    C = Canvas(fenetre, height=MAIN_WIN_H, width=MAIN_WIN_W)

    main_image = PhotoImage(file='resources/schotten_totten_main_menu.png')
    background_label = Label(main_frame, image=main_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    checkbutton = Checkbutton(
        fenetre, text="Expert Mode", height=3, width=20, onvalue=True, offvalue=False)
    checkbutton.place(relx=0.5, rely=0.9, anchor=CENTER)

    bouton1 = Button(main_frame, text="Player 1 VS Player 2",
                     height=3, width=20)
    bouton1.place(relx=0.5, rely=0.7, anchor=CENTER)

    bouton2 = Button(main_frame, text="Player 1 VS A.I.",
                     height=3, width=20, command=fenetre.quit)
    bouton2.place(relx=0.5, rely=0.8, anchor=CENTER)

    fenetre.mainloop()

    while 1:
        print(checkbutton.get())


def isExpert(var):
    print(var)


def changeValue(cb):
    cb.var = not(cb.var)
    print(cb.var)


afficherMenuAccueil()
