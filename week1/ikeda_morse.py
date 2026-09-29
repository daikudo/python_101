MORSE_CODE_DICT = {
    'A': '.-',     'B': '-...',   'C': '-.-.',   'D': '-..',
    'E': '.',      'F': '..-.',   'G': '--.',    'H': '....',
    'I': '..',     'J': '.---',   'K': '-.-',    'L': '.-..',
    'M': '--',     'N': '-.',     'O': '---',    'P': '.--.',
    'Q': '--.-',   'R': '.-.',    'S': '...',    'T': '-',
    'U': '..-',    'V': '...-',   'W': '.--',    'X': '-..-',
    'Y': '-.--',   'Z': '--..',

    '0': '-----',  '1': '.----',  '2': '..---',  '3': '...--',
    '4': '....-',  '5': '.....',  '6': '-....',  '7': '--...',
    '8': '---..',  '9': '----.', ' ': '/He'
}

our_text = "ALFA"

morse_text = []
for letter in our_text:
    print (f"Наша буква: {letter}, Морзе: {MORSE_CODE_DICT [letter]}")
    morse_text.append(MORSE_CODE_DICT[letter])

final_text = " ".join(morse_text)

print (final_text)


def text_to_morse ():
    our_input = input("Введите текст на английском языке: \n")
    our_input = our_input.upper()
    morse_text = []
    for letter in our_input:
        morse_letter = MORSE_CODE_DICT[letter]
        morse_text.append(morse_letter)
    final_text = " ".join(morse_text)
    print(f"Зашифрованный результат: {final_text}") 
    return

text_to_morse()