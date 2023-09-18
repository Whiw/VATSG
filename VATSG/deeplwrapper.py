from deepl import Translator
from deepl import exceptions
import time


def translateusingapi(text, uiwrapper):
    try:
        translator = Translator(uiwrapper.getkey().strip())
        result = translator.translate_text(text, target_lang=uiwrapper.get_trglanguagecodeinput())
        return result.text
    except Exception as e:
        if isinstance(e, exceptions.QuotaExceededException):
            uiwrapper.update_percentagelabel_post("text", "api Exceed Quota")
        elif isinstance(e, exceptions.AuthorizationException):
            uiwrapper.update_percentagelabel_post("text", "check your apikey again")
        elif isinstance(e, exceptions.TooManyRequestsException):
            uiwrapper.update_percentagelabel_post("text", "deepl request is busy")

def translateusingapifortest(text):
    try:
        translator = Translator("fortest")
        result = translator.translate_text(text, target_lang='KO', source_lang='ZH')
        return result.text
    except Exception as e:
        if isinstance(e, exceptions.QuotaExceededException):
            pass
        elif isinstance(e, exceptions.AuthorizationException):
            pass
        elif isinstance(e, exceptions.TooManyRequestsException):
            pass