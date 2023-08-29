# VATSG(Video Automatic Transcribed to translated Subtitle Generator)
![Untitled (1)](https://github.com/Whiw/VATSG/assets/9716884/bbd026ad-bf9b-41c5-b31f-4d454784f54a)
Above Demovideo's source language is Korean and target language is English. 

This is the subtitle generator(VATSG) which use [moviepy](https://github.com/Zulko/moviepy) to generate mp3 and then use [faster-whisper](https://github.com/guillaumekln/faster-whisper) to get text recognition and then use deepl-api to generate your target language subtitle file(srt format)

If you are a general user who want to view any video file and mp3 file to your language, It will provide way. 

## Setup

### Windows

You can download it in release tab. It is split compressed because of size limit policy. you just download and decompress and run VATGS.exe file. I only tested windows 10, It worked well.

## Usage
In file tab, 
1. Write your api key(deepl) and then press file open to choose video or drag&drop your video file(mp3 file is ok too)
2. Select model based on [faster-whisper](https://github.com/guillaumekln/faster-whisper), there are specific specs to select. choose CUDA enable or disable based on your environment.
3. Write source and target language code. If you don't write source language code, it will automatically detect, But If translation is weird, fill that.
4. Press generate button. I tested several window10 machine only. But it works fine.
5. It will generate *.srt file in your video file directory.
6. Enjoy it! At first generation, Model will be downloaded so it will take some time. 

About Language code, please check [deepl](https://www.deepl.com/docs-api/translate-text/?utm_source=github&utm_medium=github-python-readme)

Also for your convenience, I made language code text files 'sourcelangcode.txt', 'targetlangcode.txt'

## CUDA
Because [faster-whisper](https://github.com/guillaumekln/faster-whisper) can use CUDA, If you satisfy CUDA spec, then it will work on it. Just check CUDA and proceed it. 

## SUPPORT

Since there are much more to improve things, such as not just one file, multifile automatic generation and not generate subtitle but make add subtitle to original video file.

If AI language translation model which shows good quality comes to show, I want to combine it also. Also cli support and mac/linux build and test.

And I have future plan to make android app to connect local program in pc to generate srt file in mobile device. 

So, I want you to support me to encourage and motivate this project!

[Paypal](https://paypal.me/whiw215), 

Or you can be member to support me in [patreon](https://www.patreon.com/Whiw/membership)