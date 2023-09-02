import os
import glob
import sys

import tqdm

from faster_whisper import WhisperModel
from whisper.utils import get_writer
import whisper

from deeplwrapper import translateusingapi
from extractaudio import extract_audio_from_video
from utility import get_mp3_duration, format_seconds, get_byte_size, split_string_by_max_byte

import torch
import localization






def transcribe_fast_whisper(file, option, uiwrapper):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Using device:', device)


    if uiwrapper.get_cuda_var() and device.type == 'cuda':
        print("Cuda On")
        model = WhisperModel(option, device="cuda", compute_type="float16")
    else:
        print("cpu")
        model = WhisperModel(option, device="cpu", compute_type="int8")
    srtfile = os.path.splitext(file)[0] + ".srt"
    if uiwrapper.get_srclanguagecodeinput() == "":
        print(file)
        segments, info = model.transcribe(file, beam_size=5, word_timestamps=True)
    else:
        print(file)
        segments, info = model.transcribe(file, beam_size=5, word_timestamps=True,
                                          language=uiwrapper.get_srclanguagecodeinput())
    allseconds = get_mp3_duration(file)
    uiwrapper.update_progressbar('maximum', allseconds)

    cnt = 1
    if os.path.exists(srtfile):
        os.remove(srtfile)

    with open(srtfile, "a", encoding="utf8") as f:
        for segment in segments:
            translated_string = translateusingapi(segment.text, uiwrapper)
            if translated_string:
                print(str(cnt) + "\n" + format_seconds(segment.start) + " --> " + format_seconds(segment.end) + "\n" + translated_string + "\n\n")
                f.write(str(cnt) + "\n" + format_seconds(segment.start) + " --> " + format_seconds(segment.end) + "\n" + translated_string + "\n\n")
            cnt+=1
            uiwrapper.update_progressbar("value", segment.end)
            uiwrapper.update_percentagelabel_post("text", str((segment.end / allseconds) * 100))


    uiwrapper.update_percentagelabel_post("text", "Finished")


def transcribe_fast_whisper_differently(file, option, uiwrapper):
    def makesrt(timestamp, strs):
        count = 1
        results = strs.splitlines()
        for time, result in zip(timestamp, results):
            with open(file_name_without_extension + ".srt", 'a', encoding='utf-8') as s:
                """
                print(str(count))
                print(str(time))
                print(result + '\n')
                """
                s.write(str(count) + '\n')
                s.write(time + '\n')
                s.write(result + '\n\n')
                count += 1
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Using device:', device)

    if uiwrapper.get_cuda_var() and device.type == 'cuda':
        print("Cuda On")
        model = WhisperModel(option, device="cuda", compute_type="float16")
    else:
        print("cpu")
        model = WhisperModel(option, device="cpu", compute_type="int8")

    file_name_with_extension = os.path.basename(file)
    file_name_without_extension, _ = os.path.splitext(file)

    translatedsrtfile = file_name_without_extension + ".srt"
    transcribedsrtfile = file_name_without_extension + localization.getstr("transcribed") + ".srt"

    if uiwrapper.get_srclanguagecodeinput() == "":
        print(file)
        segments, info = model.transcribe(file, beam_size=5, word_timestamps=True)
    else:
        print(file)
        segments, info = model.transcribe(file, beam_size=5, word_timestamps=True,
                                          language=uiwrapper.get_srclanguagecodeinput())
    allseconds = get_mp3_duration(file)
    uiwrapper.update_progressbar('maximum', allseconds)

    cnt = 1
    if os.path.exists(transcribedsrtfile):
        os.remove(transcribedsrtfile)

    with open(transcribedsrtfile, "a", encoding="utf8") as f:
        for segment in segments:

            print(str(cnt) + "\n" + format_seconds(segment.start) + " --> " + format_seconds(
                segment.end) + "\n" + segment.text + "\n\n")

            f.write(str(cnt) + "\n" + format_seconds(segment.start) + " --> " + format_seconds(
                segment.end) + "\n" + segment.text + "\n\n")
            cnt += 1
            uiwrapper.update_progressbar("value", segment.end)
            uiwrapper.update_percentagelabel_post("text", "{:.2f}".format(round((segment.end / allseconds) * 100, 2)) + "%")

    with open(transcribedsrtfile, 'r', encoding='utf-8', errors='ignore') as orig_srt:
        orig_srt_text = orig_srt.read().splitlines()

    # Calculate duration of each subtitle based on the original SRT file
    timestamps = []
    for i in range(0, len(orig_srt_text), 4):
        timestamps.append(orig_srt_text[i + 1])

    src_lang = []
    for i in range(0, len(orig_srt_text), 4):
        src_lang.append(orig_srt_text[i+2])

    src_lang_sentence = '\n'.join(src_lang)
    src_lang_sentences = []

    trg_lang_sentences = []

    if get_byte_size(src_lang_sentence) > 102400:
        src_lang_sentences = split_string_by_max_byte(src_lang_sentence)
        for sentence in src_lang_sentences:
            trg_lang_sentences.append(translateusingapi(sentence, uiwrapper))
            trg_lang = '\n'.join(trg_lang_sentences)
            makesrt(timestamps, trg_lang)
    else:
        tr = translateusingapi(src_lang_sentence, uiwrapper)
        makesrt(timestamps, tr)

    if not uiwrapper.get_original_var():
        os.remove(transcribedsrtfile)

    uiwrapper.update_percentagelabel_post("text", "Finished")

def transcribe_whisper(file, option, uiwrapper):
    def makesrt(timestamp, strs):
        count = 1
        results = strs.splitlines()
        for time, result in zip(timestamp, results):
            with open(os.path.splitext(file)[0] + localization.getstr("transcribed") + ".srt", 'a', encoding='utf-8') as s:
                """
                print(str(count))
                print(str(time))
                print(result + '\n')
                """
                s.write(str(count) + '\n')
                s.write(time + '\n')
                s.write(result + '\n\n')
                count += 1

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Using device:', device)

    if uiwrapper.get_cuda_var() and device.type == 'cuda':
        print("Cuda On")
        model = whisper.load_model(option, device="cuda")

    else:
        print("cpu")
        model = whisper.load_model(option, device="cpu")

    file_name_with_extension = os.path.basename(file)
    file_name_without_extension, _ = os.path.splitext(file)

    transcribedsrtfile = file_name_without_extension + ".srt"
    translatedsrtfile = file_name_without_extension + localization.getstr("transcribed") + ".srt"



    if uiwrapper.get_srclanguagecodeinput() == "":
        print(file)
        result = model.transcribe(file, verbose=True)
        writer = get_writer("srt", os.path.dirname(file))
        writer(result, transcribedsrtfile)
    else:
        print(file)
        result = model.transcribe(file, verbose=True, language=uiwrapper.get_srclanguagecodeinput())
        writer = get_writer("srt", os.path.dirname(file))
        writer(result, transcribedsrtfile)

    allseconds = get_mp3_duration(file)
    uiwrapper.update_progressbar('maximum', allseconds)

    cnt = 1

    with open(transcribedsrtfile, 'r', encoding='utf-8', errors='ignore') as orig_srt:
        orig_srt_text = orig_srt.read().splitlines()

    # Calculate duration of each subtitle based on the original SRT file
    timestamps = []
    for i in range(0, len(orig_srt_text), 4):
        timestamps.append(orig_srt_text[i + 1])

    src_lang = []
    for i in range(0, len(orig_srt_text), 4):
        src_lang.append(orig_srt_text[i+2])

    src_lang_sentence = '\n'.join(src_lang)
    src_lang_sentences = []

    trg_lang_sentences = []

    if get_byte_size(src_lang_sentence) > 102400:
        src_lang_sentences = split_string_by_max_byte(src_lang_sentence)
        for sentence in src_lang_sentences:
            trg_lang_sentences.append(translateusingapi(sentence, uiwrapper))
            trg_lang = '\n'.join(trg_lang_sentences)
            makesrt(timestamps, trg_lang)
    else:
        tr = translateusingapi(src_lang_sentence, uiwrapper)
        makesrt(timestamps, tr)

    os.rename(transcribedsrtfile, os.path.splitext(file)[0] + "temp" + ".srt" )
    os.rename(translatedsrtfile, os.path.splitext(file)[0] + ".srt")
    os.rename(os.path.splitext(file)[0] + "temp" + ".srt" , os.path.splitext(file)[0] + localization.getstr("transcribed") + ".srt")

    if not uiwrapper.get_original_var():
        os.remove(os.path.splitext(transcribedsrtfile)[0] + localization.getstr("transcribed") + ".srt")

    uiwrapper.update_percentagelabel_post("text", "Finished")

def transcribebypatterns(filepattern, options, uiwrapper):
    translateoptionvar = uiwrapper.get_translateoption_Var()
    matching_files = glob.glob(filepattern)
    print(matching_files)
    for gfile in matching_files:
        gfile2 = os.path.splitext(gfile)[0] + ".mp3"
        transcribe_from_mp3_fast_whisper(gfile2, translateoptionvar.get())


def transcribe_from_mp3_whisper(file1, file2, uiwrapper):
    if os.path.splitext(file1)[1] != ".mp3":
        extract_audio_from_video(file1, file2)
        transcribe_whisper(file2, uiwrapper.get_translateoption_Var(), uiwrapper)
    else:
        transcribe_whisper(file2, uiwrapper.get_translateoption_Var(), uiwrapper)


def transcribe_from_mp3_fast_whisper(file1, file2, uiwrapper):
    if os.path.splitext(file1)[1] != ".mp3":
        extract_audio_from_video(file1, file2)
        transcribe_fast_whisper_differently(file2, uiwrapper.get_translateoption_Var(), uiwrapper)
    else:
        transcribe_fast_whisper_differently(file2, uiwrapper.get_translateoption_Var(), uiwrapper)
