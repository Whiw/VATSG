import locale
import tkinter
import tkinter.ttk
import uuid
from tkinter import *
from tkinter import filedialog
import tkinter.ttk as ttk

import threading
import os
import re
import tqdm

from tkinterdnd2 import DND_FILES, TkinterDnD

from PIL import ImageTk
import qrcode
import whisper
import stable_whisper

import UIwrapper
import localization
import sys

import queue

from extractaudio import get_media_length_in_time
from utility import get_file_size_in_mb, treeview_sort_column, sort_by_path, shorten_path
from settings import load_settings, load_apikey, settingjson, save_apikey, get_settings_path

update_queue = queue.Queue()
multifile_queue = queue.Queue()
lock = threading.Lock()

multi_processing = False

__version__ = '1.0.4'

defaultdir = "C:/Users"

window = TkinterDnD.Tk()
window.title(localization.getstr('appname') + __version__ + " by whiw")
window.geometry('760x400')

translateoption_var = tkinter.StringVar()
translateoption_var.set("small")
trnanslateoptions = ["tiny", "base", "small", "medium", "large-v1", "large-v2"]

cuda_var = tkinter.BooleanVar()

original_var = tkinter.BooleanVar()

fast_var = tkinter.BooleanVar()

file_list= []
multifile_status_indicator = 0
class _CustomProgressBar(tqdm.tqdm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current = self.n  # Set the initial value

    def update(self, n):
        super().update(n)
        self._current += n

        # Handle progress here

        multifile_progressbar['maximum'] = self.total
        multifile_progressbar['value'] = self._current

        multifile_status_label['text'] = "{:.2f}".format(round((self._current / self.total) * 100, 2)) + "%"

        progressbar['maximum'] = self.total
        progressbar['value'] = self._current
        percentagelabel['text'] = "{:.2f}".format(round((self._current / self.total) * 100, 2)) + "%"


transcribe_module = sys.modules['whisper.transcribe']
transcribe_module.tqdm.tqdm = _CustomProgressBar

#stable_transcribe_module = sys.modules['stable_whisper.whisper_word_level']
#stable_transcribe_module.tqdm = _CustomProgressBar

def open_donation_link():
    # Replace with your actual donation link
    donation_link = "https://paypal.me/whiw215"
    import webbrowser
    webbrowser.open(donation_link)
def open_patreon_link():
    patreonlink = "https://www.patreon.com/Whiw/membership"
    import webbrowser
    webbrowser.open(patreonlink)


def on_delete_key_press(event):
    selected_items = file_treeview.selection()
    for item in selected_items:
        item_values = file_treeview.item(item, 'values')
        for path, spath in file_list:
            if spath == item_values[0]:
                file_list.remove((path, spath))
        file_treeview.delete(item)
    multifile_list_label['text'] = "0/" + str(len(file_list))

def check_multifile_status():
    all_items = file_treeview.get_children()
    for item in all_items:
        item_value = list(file_treeview.item(item, 'values'))  # 튜플을 리스트로 변환
        item_spath = item_value[0]
        for path, spath in file_list:
            if spath == item_spath:
                file_name_without_extension, _ = os.path.splitext(path)
                if os.path.exists(file_name_without_extension + ".srt"):
                    item_value[3] = "Done"
                else:
                    item_value[3] = "Undone"
                file_treeview.item(item, values=tuple(item_value))

def list_label_indicate( number = 0):
    multifile_queue.put(('list', str(number) + "/" + str(len(file_list))))

def on_filetap_drop(event):
    file_path = event.data.strip('{}')
    targetfileEntry.delete(0, len(targetfileEntry.get()))
    targetfileEntry.insert(0, file_path)




def on_drop(event):
    file_path = event.data.strip().split()
    files = event.data.strip()
    extensions = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm", ".m4v", ".ogg", ".ogv", ".ts", ".f4v", ".mwa", ".asf", ".mpg", ".mpeg", ".mp3"}
    pattern = "(" + "|".join(re.escape(ext) for ext in extensions) + ")"

    split_data = re.split(pattern, files)
    file_paths = ["".join(split_data[i:i + 2]).strip("{}").strip() for i in range(0, len(split_data) - 1, 2)]

    if files[0] =="{":
        matches = re.finditer(r'\{([A-Za-z]:.*?\..\w{1,4})}', files)
        if len(file_list) != 0:
            count = len(file_list)
            for i, match in enumerate(matches):
                file_treeview.insert(parent='', index=tkinter.END, iid=uuid.uuid4(),
                                     values=[shorten_path(match.group(1)),
                                             str(get_file_size_in_mb(match.group(1))) + "MB",
                                             get_media_length_in_time(match.group(1)), "Undone"])
                file_list.append((match.group(1), shorten_path(match.group(1))))
        else:
            for i, match in enumerate(matches):
                file_treeview.insert(parent='', index=tkinter.END, iid=uuid.uuid4(),
                                     values=[shorten_path(match.group(1)),
                                             str(get_file_size_in_mb(match.group(1))) + "MB",
                                             get_media_length_in_time(match.group(1)), "Undone"])
                file_list.append((match.group(1), shorten_path(match.group(1))))

    else:
        for i, file in enumerate(file_paths):
            file_treeview.insert(parent='', index=tkinter.END, iid=uuid.uuid4(),
                                 values=[shorten_path(file),
                                         str(get_file_size_in_mb(file)) + "MB",
                                         get_media_length_in_time(file), "Undone"])
            file_list.append((file, shorten_path(file)))



    multifile_list_label['text'] = "0/" + str(len(file_list))




def open_dialog():
    file = filedialog.askopenfilename(initialdir= defaultdir)
    targetfileEntry.delete(0, len(targetfileEntry.get()))
    targetfileEntry.insert(0, file)


def proceedfastwhisperthread():
    from mywhisper import transcribe_from_mp3_fast_whisper, transcribe_from_mp3_whisper
    targetfile = targetfileEntry.get()
    file_name_without_extension, _ = os.path.splitext(targetfile)
    targetfile_audio = file_name_without_extension + ".mp3"
    transferuiwrapper = UIwrapper.UIwrapper(update_queue, lock, apikeyinput.get(), cuda_var.get(), translateoption_var.get(), sourcelanguagecodeinput.get(), targetlanguagecodeinput.get(), original_var.get(), fast_var.get())
    save_apikey(apikeyinput.get())
    settingjson(transferuiwrapper)
    if fast_var.get():
        transcribe_from_mp3_fast_whisper(targetfile, targetfile_audio, transferuiwrapper)
    else:
        transcribe_from_mp3_whisper(targetfile, targetfile_audio, transferuiwrapper)

def proceed_multifile_whisperthread():
    from mywhisper import transcribe_from_mp3_fast_whisper, transcribe_from_mp3_whisper
    transferuiwrapper = UIwrapper.UIwrapper(multifile_queue, lock, apikeyinput.get(), cuda_var.get(),
                                            translateoption_var.get(), sourcelanguagecodeinput.get(),
                                            targetlanguagecodeinput.get(), original_var.get(), fast_var.get())
    save_apikey(apikeyinput.get())
    settingjson(transferuiwrapper)
    for i, (file, spath) in enumerate(file_list):
        list_label_indicate(i+1)
        file_name_without_extension, _ = os.path.splitext(file)
        file_audio = file_name_without_extension + ".mp3"
        if fast_var.get():
            transcribe_from_mp3_fast_whisper(file, file_audio, transferuiwrapper)
        else:
            transcribe_from_mp3_whisper(file, file_audio, transferuiwrapper)


def multifile_update_from_queue():
    if not multifile_queue.empty():
        msg = multifile_queue.get()
        if msg[0] == "maximum":
            with lock:
                multifile_progressbar['maximum'] = msg[1]
        elif msg[0] == "value":
            with lock:
                multifile_progressbar['value'] = msg[1]
        elif msg[0] == "list":
            with lock:
                multifile_list_label['text'] = msg[1]
                check_multifile_status()
        elif msg[0] == "text" and msg[1] != "Finished":
            with lock:
                multifile_status_label['text'] = msg[1]
        elif msg[1] == "Finished" and multifile_list_label['text'].split("/")[0] == str(len(file_list)):
            with lock:
                multifile_status_label['text'] = msg[1]
                multifile_generation_button.config(state=NORMAL)
                multifile_progressbar['value'] = 0
                check_multifile_status()
                file_treeview.bind('<Delete>', on_delete_key_press)
                return
    window.after(100, multifile_update_from_queue)



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
    if not os.path.exists(get_settings_path()):
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

def proceedmultifile():
    multifile_generation_button.config(state=DISABLED)
    file_treeview.unbind('<Delete>')
    multifile_update_from_queue()
    thread = threading.Thread(target=proceed_multifile_whisperthread)
    thread.start()

#window.drop_target_register(DND_FILES)
#window.dnd_bind('<<Drop>>', on_drop)

notebook = ttk.Notebook(window)
notebook.pack()

frame1 = Frame(window)
frame1.drop_target_register(DND_FILES)
frame1.dnd_bind('<<Drop>>', on_filetap_drop)

multifileframe = Frame(window)
multifileframe.drop_target_register(DND_FILES)
multifileframe.dnd_bind('<<Drop>>', on_drop)



notebook.add(frame1, text="File")
notebook.add(multifileframe, text="Multifile")

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

tree_frame = Frame(multifileframe, width=400, height=20)
tree_frame.grid(column=0, row=0, sticky='nsew')
tree_frame.grid_rowconfigure(1, weight=0)

file_treeview_instruction = Label(tree_frame, text=localization.getstr("multifile_instruction"))
file_treeview_instruction.grid(column=0, row=0)

file_treeview =ttk.Treeview(tree_frame, columns=( localization.getstr("path"), localization.getstr("size"), localization.getstr("length"),localization.getstr("status")), height=5)
file_treeview.grid(column=0, row=1, sticky='nsew')

# 각 열의 설정
file_treeview.heading(localization.getstr("path"), text=localization.getstr("path"), command=lambda: sort_by_path(file_treeview, 0, False))
file_treeview.heading(localization.getstr("size"), text=localization.getstr("size") + "(MB)", command=lambda: treeview_sort_column(file_treeview, localization.getstr("size"), False))
file_treeview.heading(localization.getstr("length"), text=localization.getstr("length") + "(hh:mm:ss)", command=lambda: treeview_sort_column(file_treeview, localization.getstr("length"), False))
file_treeview.heading(localization.getstr("status"), text=localization.getstr("status"))

file_treeview.column("#0", width=0, stretch=tkinter.NO)
file_treeview.column(localization.getstr("path"), anchor=tkinter.W, width=400)
file_treeview.column(localization.getstr("size"), anchor=tkinter.W, width=70)
file_treeview.column(localization.getstr("length"), anchor=tkinter.W, width=90)
file_treeview.column(localization.getstr("status"), anchor=tkinter.W, width=70)



# 임시 데이터 삽입
generationframe = Frame(tree_frame, width=460)
generationframe.grid(column=0, row=2)
generationframe.grid_columnconfigure(1, weight=0)

file_treeview.bind('<Delete>', on_delete_key_press)

multifile_progressbar = ttk.Progressbar(generationframe, length=400, maximum=20)
multifile_progressbar.grid(column=0, row=0, padx=(60, 90), pady=10, sticky='e')

multifile_generation_button = Button(generationframe, text=localization.getstr('generate'), command=proceedmultifile)
multifile_generation_button.grid(column=1, row=0,padx=(0, 80), sticky='w')

multifile_indicator_frame = Frame(generationframe)
multifile_indicator_frame.grid(column=0, row=1)

multifile_list_label = Label(multifile_indicator_frame, text="0/0", anchor='w')
multifile_list_label.grid(column=1, row=0, sticky='w')

multifile_status_label = Label(multifile_indicator_frame, text = "0%")
multifile_status_label.grid(column=0, row=0)


donationlabel_multi = Label(multifile_indicator_frame, text=localization.getstr('donation_paypal'), fg="blue", cursor="hand2")
donationlabel_multi.grid(column=0, row=3)
donationlabel_multi.bind("<Button-1>", lambda e: open_donation_link())

kakao_label_multi = Label(multifile_indicator_frame, text=localization.getstr('donation_kakao'),padx=60, anchor='e')
kakao_label_multi.grid(column=1, row=4, sticky='e')
kakao_label_multi.grid_columnconfigure(0, weight=0)

patreonlabel_multi = Label(multifile_indicator_frame, text=localization.getstr('donation_patreon'), fg="red", cursor="hand2")
patreonlabel_multi.grid(column=0, row=4)
patreonlabel_multi.bind("<Button-1>", lambda e: open_patreon_link())

email_entry_multi = Entry(multifile_indicator_frame, width=50)
email_entry_multi.insert(0, localization.getstr("contact") + "hamwhiw330@gmail.com")
email_entry_multi.config(state="readonly")  # 읽기 전용으로 설정
email_entry_multi.grid(column = 0, row=5)

if locale.getlocale()[0] == 'ko_KR' or locale.getlocale()[0] == 'Korean_Korea':
    account_entry = Entry(multifile_indicator_frame, width=50)
    account_entry.insert(0, localization.getstr("donation_account"))
    account_entry.config(state="readonly")  # 읽기 전용으로 설정
    account_entry.grid(column=0, row=6)


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


qr_labelframe = Frame(multifile_indicator_frame)
qr_labelframe.grid(column=1, row=5)
qr_label_multi = Label(qr_labelframe, image=img_tk)
qr_label_multi.grid(column=0, row=0, sticky='e')
qr_label_multi.grid_rowconfigure(0, weight=0)

if __name__ == '__main__':
    window.mainloop()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
