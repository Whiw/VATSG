import os

from mutagen.mp3 import MP3

import deeplwrapper



def srt_to_txt(srt_file, txt_file):
    with open(srt_file, 'r', encoding='utf-8', errors='ignore') as orig_srt:
        orig_srt_text = orig_srt.read().splitlines()

    # Calculate duration of each subtitle based on the original SRT file
    timestamps = []
    for i in range(0, len(orig_srt_text), 4):
        timestamps.append(orig_srt_text[i + 1])

    for i in range(0, len(orig_srt_text), 4):
        with open(txt_file, 'a', encoding='utf-8') as f:
            f.write(orig_srt_text[i+2] + '\n')

    return timestamps

def srt_get_timestamps(srt_file):
    with open(srt_file, 'r', encoding='utf-8', errors='ignore') as orig_srt:
        orig_srt_text = orig_srt.read().splitlines()

    # Calculate duration of each subtitle based on the original SRT file
    timestamps = []
    for i in range(0, len(orig_srt_text), 4):
        timestamps.append(orig_srt_text[i + 1])

    return timestamps


def split_string_by_line_by_me(string, length):
    lines = string.splitlines(True)
    result = []
    current_line = ""
    count = 0
    for index, line in enumerate(lines):
        count +=len(line)
        if count < length:
            current_line+=line
        else:
            result.append(current_line)
            current_line = line
            count = len(current_line)
    result.append(current_line)

    return result


def is_whitespace_or_newline(string):
    if string.strip() == '':
        return True
    return False
def makeoutput(tar, str):
    with open(tar, "a", encoding='UTF8') as f:
        f.write(str + '\n')


def get_mp3_duration(file_path):
    audio = MP3(file_path)
    duration_in_seconds = audio.info.length
    return duration_in_seconds

def format_seconds(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{seconds:06.3f}".replace(".", ",")


def get_max_line_number(text):
    lines = text.splitlines()
    return len(lines)
def split_string_by_length(string, length):
    parts = []
    for i in range(0, len(string), length):
        part = string[i:i+length]
        parts.append(part)
    return parts

def split_string_by_line(string, length):
    lines = string.splitlines()
    result = []
    current_line = ""
    for index, line in enumerate(lines):
        words = line.split(" ")
        if words:
            for word in words:
                if word == "":
                    current_line+="...."
                else:
                    if len(current_line) + len(word) + 1 <= length:
                        current_line += word + " "
                    else:
                        result.append(current_line)
                        current_line = word + " "
            current_line = current_line + "\n"
    result.append(current_line)
    print(result)
    return result



def srt_to_txt_with_timestamp(srt_file, txt_file):
    with open(srt_file, 'r', encoding='utf-8') as srt:
        srt_lines = srt.readlines()
        with open(txt_file, 'w', encoding='utf-8') as txt:
            txt.writelines(srt_lines)

def returntosrt(txt, srt):
    with open(txt, 'r', encoding='utf-8') as txtt:
        srt_lines = txtt.readlines()
        with open(srt, 'w', encoding='utf-8') as srtt:
            srtt.writelines(srt_lines)


    # Join the reduced lines back into a single string with newlines


def makesrt(result, filename):
    count = 1
    with open(os.path.splitext(filename)[0] + ".txt", 'r', encoding='utf-8') as f:
        for item1 in result:
            r = f.readline()
            with open(os.path.splitext(filename)[0] + ".srt", 'a', encoding='utf-8') as s:
                s.write(str(count) + '\n')
                s.write(item1 + '\n')
                s.write(r + '\n\n')
                count+=1

def txttest(file1, file2):
    with open(file1, 'r', encoding='utf-8') as f1:
        r = f1.read()
        lst = split_string_by_line_by_me(r, 1400)
        for var in lst:
            with open(file2, 'a', encoding='utf-8') as f2:
                f2.write(var)


def translateusingapitofile(src, tar, uiwrapper):
    srcfile = open(src, "r", encoding='UTF8')
    raw = srcfile.read()
    result = deeplwrapper.translateusingapi(raw, uiwrapper)
    with open(tar, "w", encoding="utf8") as f:
        f.write(result)
