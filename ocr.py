
import easyocr

reader = easyocr.Reader(['en'])

output = reader.readtext('plate.jpg')
# print(output)
for box, text, confidence in output:
    print(text)
    print(confidence)
