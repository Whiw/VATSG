
import tkinter
from tkinter import *
from tkinter import filedialog
import tkinter.ttk as ttk

import threading
import os
import tqdm

from tkinterdnd2 import DND_FILES, TkinterDnD

from PIL import ImageTk
import qrcode
import whisper

import UIwrapper
import localization
import sys

import queue

from settings import load_settings, load_apikey, settingjson, save_apikey

update_queue = queue.Queue()
lock = threading.Lock()


__version__ = '1.0.1'

defaultdir = "C:/Users"

window = TkinterDnD.Tk()
window.title(localization.getstr('appname') + __version__ + " by whiw")
window.geometry('720x360')

translateoption_var = tkinter.StringVar()
translateoption_var.set("small")
trnanslateoptions = ["tiny", "base", "small", "medium", "large-v1", "large-v2"]

cuda_var = tkinter.BooleanVar()

original_var = tkinter.BooleanVar()

fast_var = tkinter.BooleanVar()
class _CustomProgressBar(tqdm.tqdm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current = self.n  # Set the initial value

    def update(self, n):
        super().update(n)
        self._current += n

        # Handle progress here
        print("Progress: " + str(self._current) + "/" + str(self.total))
        progressbar['maximum'] = self.total
        progressbar['value'] = self._current
        percentagelabel['text'] = str((self._current / self.total) * 100) + "%"


transcribe_module = sys.modules['whisper.transcribe']
transcribe_module.tqdm.tqdm = _CustomProgressBar


def open_donation_link():
    # Replace with your actual donation link
    donation_link = "https://paypal.me/whiw215"
    import webbrowser
    webbrowser.open(donation_link)
def open_patreon_link():
    patreonlink = "https://www.patreon.com/Whiw/membership"
    import webbrowser
    webbrowser.open(patreonlink)

def on_drop(event):
    file_path = event.data.strip('{}')
    targetfileEntry.delete(0, len(targetfileEntry.get()))
    targetfileEntry.insert(0, file_path)

def open_dialog():
    file = filedialog.askopenfilename(initialdir= defaultdir)
    targetfileEntry.delete(0, len(targetfileEntry.get()))
    targetfileEntry.insert(0, file)


def proceedfastwhisperthread():
    from mywhisper import transcribe_from_mp3_fast_whisper, transcribe_from_mp3_whisper
    targetfile = targetfileEntry.get()
    targetfile_audio = os.path.splitext(targetfile)[0] + ".mp3"
    transferuiwrapper = UIwrapper.UIwrapper(update_queue, lock, apikeyinput.get(), cuda_var.get(), translateoption_var.get(), sourcelanguagecodeinput.get(), targetlanguagecodeinput.get(), original_var.get(), fast_var.get())
    save_apikey(apikeyinput.get())
    settingjson(transferuiwrapper)
    if fast_var.get():
        transcribe_from_mp3_fast_whisper(targetfile, targetfile_audio, transferuiwrapper)
    else:
        transcribe_from_mp3_whisper(targetfile, targetfile_audio, transferuiwrapper)




def update_ui_from_queue():
    if not update_queue.empty():
        msg = update_queue.get()
        if msg[0] == "maximum":
            with lock:
                progressbar['maximum'] = msg[1]
        elif msg[0] == "value":
            with lock:
                progressbar['value'] = msg[1]
        elif msg[0] == "text" and msg[1] != "Finished":
            with lock:
                percentagelabel['text'] = msg[1]
        elif msg[1] == "Finished":
            with lock:
                percentagelabel['text'] = msg[1]
                proceedbutton.config(state=NORMAL)
                progressbar['value'] = 0
                return
    window.after(100, update_ui_from_queue)


def initialize():
    if not os.path.exists("settings.json"):
        return
    else:
        settings = load_settings()
        if load_apikey() is not None:
            apikeyinput.insert(0, load_apikey().decode('utf-16-le'))
        cuda_var.set(settings["cuda_var"])
        translateoption_var.set(settings["translateoption_var"])
        sourcelanguagecodeinput.insert(0, settings["sourcelanguagecodeinput"])
        targetlanguagecodeinput.insert(0, settings["targetlanguagecodeinput"])
        original_var.set(settings["original"])
        fast_var.set(settings["fast"])


def proceed():
    proceedbutton.config(state=DISABLED)
    update_ui_from_queue()
    thread = threading.Thread(target=proceedfastwhisperthread)
    thread.start()


window.drop_target_register(DND_FILES)
window.dnd_bind('<<Drop>>', on_drop)

notebook = ttk.Notebook(window)
notebook.pack()

frame1 = Frame(window)
notebook.add(frame1, text="File")

apikeyinput = Entry(frame1, width=30)
apikeyinput.grid(column=1, row=0)

label = Label(frame1, text=localization.getstr('apikey'))
label.grid(column=0, row=0)

targetfileEntry = Entry(frame1, width=30)
targetfileEntry.insert(0, localization.getstr('selectinstruction'))
targetfileEntry.grid(column=1, row=1)

button = Button(frame1, text=localization.getstr('selectfile'), command=open_dialog)
button.grid(column=0, row=1)

frame4 = Frame(frame1)
frame4.grid(column=0, row=2)

label = Label(frame4, text=localization.getstr('choosemodel'))
label.grid(column=0, row=0)

fastoption = Checkbutton(frame4, text="Fast", variable=fast_var)
fastoption.grid(column=1, row=0)

frame2 = Frame(frame1)
frame2.grid(column=1, row=2)

modeldropdown = ttk.Combobox(frame2, textvariable=translateoption_var, values=trnanslateoptions)
modeldropdown.grid(column=0, row=0)

checkbox = ttk.Checkbutton(frame2, text="Cuda", variable=cuda_var)
checkbox.grid(column=1, row=0)



sourcelanguagecodeinput = Entry(frame1, width=30)
sourcelanguagecodeinput.grid(column=1, row=3)


label = Label(frame1, text=localization.getstr('targetlangcode'))
label.grid(column=0, row=4)



targetlanguagecodeinput = Entry(frame1, width=30)
targetlanguagecodeinput.grid(column=1, row=4)

label = Label(frame1, text=localization.getstr('sourcelangcode'))
label.grid(column=0, row=3)


frame3 = Frame(frame1)
frame3.grid(column=0, row=5)

proceedbutton = Button(frame3, text=localization.getstr('generate'), command=proceed)
proceedbutton.grid(column=0, row=0)

originalcheckbox = Checkbutton(frame3, text=localization.getstr('original'), variable=original_var)
originalcheckbox.grid(column=1, row=0)

progressbar = ttk.Progressbar(frame1, length=100, maximum=20)
progressbar.grid(column=1, row=5)

percentagelabel = Label(frame1, text="0%")
percentagelabel.grid(column=1, row=6)

donationlabel = Label(frame1, text=localization.getstr('donation_paypal'), fg="blue", cursor="hand2")
donationlabel.grid(column=0, row=7)
donationlabel.bind("<Button-1>", lambda e: open_donation_link())

kakao_label = Label(frame1, text=localization.getstr('donation_kakao'))
kakao_label.grid(column=1, row=7)

patreonlabel = Label(frame1, text=localization.getstr('donation_patreon'), fg="red", cursor="hand2")
patreonlabel.grid(column=0, row=8)
patreonlabel.bind("<Button-1>", lambda e: open_patreon_link())

email_entry = Entry(frame1, width=50)
email_entry.insert(0, localization.getstr("contact") + "hamwhiw330@gmail.com")
email_entry.config(state="readonly")  # 읽기 전용으로 설정
email_entry.grid(column = 0, row=9)


initialize()


qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=2,
    border=4,
)
qr.add_data("https://qr.kakaopay.com/Ej7lvuIWi5dc02427")  # Replace with your URL
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img_tk = ImageTk.PhotoImage(img)

qr_label = Label(frame1, image=img_tk)
qr_label.grid(column=1, row=8,  padx=10, pady=10)


if __name__ == '__main__':
    window.mainloop()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
