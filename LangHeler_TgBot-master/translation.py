from translate import Translator

def trns(word = None, lang = 'en-ru', file = None):
    if lang == '.':
        lang = 'en-ru'
    fromlang, tolang = lang.split('-')
    translator = Translator(to_lang=tolang, from_lang=fromlang)
    if file:
        with open("data/trans.txt", encoding='utf-8') as f, open('data/translated.txt', 'w+') as f1:
            data = list(map(str.strip, f.readlines()))
            for i in data:
                translation = translator.translate(i)
                f1.write(translation + '\n')
        return 'data/translated.txt'
    translation = translator.translate(word)
    return translation
