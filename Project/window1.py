import tkinter
from tkinter import *
from PIL import ImageTk, Image

main_ok = True

BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR1 = "tomato"
TEXT_COLOR = "turquoise1"
FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"


def _on_enter_pressed(event):
    global main_ok
    # msg = msg_entry.get()
    # insert_user_msg(msg)
    main_ok = False

# def edit_general_message(self, genMsg):
# chatBot.general_message = genMsg





def insert_robot_msg(msg):

    if not msg:
        return

    msg2 = f"{msg} \n\n"
    text_widget.configure(state=NORMAL)
    text_widget.insert(END, msg2)
    text_widget.configure(state=DISABLED)
    text_widget.see(END)

def insertImage():
    # img = Image.open("download.jpg")
    # filename = ImageTk.PhotoImage(img)
    #
    # window1 = Tk()
    # window1.title("Chat")
    # window1.resizable(width=False, height=False)
    # window1.configure(width=1000, height=650, bg="#17202A")
    #
    # print()
    # canvas = Canvas(window1, height=600, width=600)
    # canvas.image = filename  # <--- keep reference of your image
    # canvas.create_image(20, 20, anchor='nw', image=filename)
    # canvas.pack()
    load = Image.open("download.jpg")
    render = ImageTk.PhotoImage(load)

    # labels can be text or images
    global img
    img = Label(image=render)
    img.image = render
    img.place(x=600, y=60)

def delImage():
    img.place(x=700, y=850)

def insert_user_msg(msg):
    if not msg:
        return

    msg_entry.delete(0, END)
    msg_entry.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011,x=0.5)
    msg2 = f"You: {msg} \n\n"
    text_widget.configure(state=NORMAL)
    try:
        text_widget.tag_add("start", "sel.first", "sel.last")
    except tkinter.TclError:
        pass
    text_widget.insert(END, msg2)

    text_widget.configure(state=DISABLED)
    text_widget.see(END)

window = Tk()
window.title("Chat")
window.resizable(width=False, height=False)
window.configure(width=1000, height=650, bg="#17202A")
#
# window1 = Tk()
# window1.title("Chat")
# window1.resizable(width=False, height=False)
# window1.configure(width=1000, height=650, bg="#17202A")
#

window.title("Chat")
window.resizable(width=False, height=False)
window.configure(width=1000, height=650, bg="#17202A")

# head label
head_label = Label(window, bg=BG_COLOR, fg="purple1",
                   text="Welcome", font=FONT_BOLD, pady=10)
head_label.place(relwidth=1)

# tiny divider
line = Label(window, width=900, bg=BG_GRAY)
line.place(relwidth=1, rely=0.07, relheight=0.012)

# text widget
text_widget = Text(window, width=5, height=2, bg=BG_COLOR, fg=TEXT_COLOR,
                   font=FONT, padx=40, pady=5)
text_widget.place(relheight=0.745, relwidth=1, rely=0.08)
text_widget.configure(cursor="arrow", state=DISABLED)

# scroll bar
scrollbar = Scrollbar(text_widget)
scrollbar.place(relheight=1, relx=1)
scrollbar.configure(command=text_widget.yview)

# bottom label
bottom_label = Label(window, bg=BG_GRAY, height=80)
bottom_label.place(relwidth=1, rely=0.825)

# message entry box
msg_entry = Entry(bottom_label, bg="#2C3E50", fg=TEXT_COLOR, font=FONT)
msg_entry.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
msg_entry.focus()
msg_entry.bind("<Return>", _on_enter_pressed)
# send button
send_button = Button(bottom_label, text="Send", font=FONT_BOLD, width=20, bg=BG_GRAY,
                     command=lambda: _on_enter_pressed(None))
send_button.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)

window.update()