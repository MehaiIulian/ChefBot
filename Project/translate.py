from deep_translator import GoogleTranslator

translated = GoogleTranslator(source='en', target='ro').translate("keep it up, you are awesome")
print(translated)
# output -> Weiter so, du bist großartig