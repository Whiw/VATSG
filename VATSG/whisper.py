import os
import glob


from faster_whisper import WhisperModel
from deeplwrapper import translateusingapi
from extractaudio import extract_audio_from_video
from utility import get_mp3_duration, format_seconds



def transcribe_fast_whisper(file, option, uiwrapper):
    if uiwrapper.get_cuda_var() == "Cuda On":
        model = WhisperModel(option, device="cuda", compute_type="float16")
    else:
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

def transcribebypatterns(filepattern, options, uiwrapper):
    translateoptionvar = uiwrapper.get_translateoption_Var()
    matching_files = glob.glob(filepattern)
    print(matching_files)
    for gfile in matching_files:
        gfile2 = os.path.splitext(gfile)[0] + ".mp3"
        transcribe_from_mp3_fast_whisper(gfile2, translateoptionvar.get())


def transcribe_from_mp3_fast_whisper(file1, file2, uiwrapper):
    if os.path.splitext(file1)[1] != ".mp3":
        extract_audio_from_video(file1, file2)
        transcribe_fast_whisper(file2, uiwrapper.get_translateoption_Var(), uiwrapper)
    else:
        transcribe_fast_whisper(file2, uiwrapper.get_translateoption_Var(), uiwrapper)


