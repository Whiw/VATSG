import locale


localize_strings = {
    'ko_KR' : {
        'contact' : "버그 제보 및 기타연락 : ",
        'appname' : "영상자막자동생성및번역기",
        'apikey' : "api키(딥엘)",
        'generate' : "자막생성",
        'selectfile' : "파일 열기",
        'selectinstruction' : "파일 경로 입력(드래그 앤 드랍 가능)",
        'sourcelangcode' : "원본 언어코드(일단 자동인식이지만 번역이 이상하면 넣어보세요.\n 언어코드 예시 : ko, en, ja, fr, zh, etc...",
        'targetlangcode' : "타깃 언어코드(KO, EN-US, JA, FR, ZH, etc...)",
        'choosemodel'   : "언어모델 선택",
        'donation_paypal' : "페이팔로 후원하기",
        'donation_patreon' : "패트론으로 구독해서 프로젝트 후원하기",
        'donation_kakao' : "카카오페이로 커피한잔^^",
        'original' : "원본자막도 생성(*원문.srt로 생성)",
        'transcribed' : "원문"
    },
    'base' : {
        'contact': "contact : ",
        'appname' : "Subtitlegenerator",
        'apikey' : "api Key(deepl)",
        'generate' : "generate subtitle",
        'selectfile' : "file open",
        'selectinstruction' : "file path : (Drag & Drop enable)",
        'sourcelangcode' : "source language code(ko, en, ja, fr, zh, etc..\n optional, autodetect it but if translation is not good",
        'targetlangcode' : "target language code(KO, EN-US, JA, FR, ZH, etc...)",
        'choosemodel'   : "choose translationmodel",
        'donation_paypal' : "Support my project by Paypal",
        'donation_patreon' : "Or you can join membership in patreon to motivate this project",
        'donation_kakao' : "If you're Korean, Use kakaopay:)",
        'original' : "generate transcribed srt too(*transcribed.srt)",
        'transcribed' : "transcribed"
    }
}


def getstr(strcode):
    if locale.getlocale()[0] == 'ko_KR' or locale.getlocale()[0] == 'Korean_Korea':
        return localize_strings['ko_KR'][strcode]
    else:
        return localize_strings['base'][strcode]