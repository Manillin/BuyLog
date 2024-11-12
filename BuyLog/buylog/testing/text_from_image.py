import pytesseract
from PIL import Image

image = Image.open('scontrino1.png')

text = pytesseract.image_to_string(image, lang='ita')
print("\n-----\n")
print(text)
