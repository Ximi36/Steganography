from PIL import Image
import random
import hashlib

min_size = 65534 # 65536 - 2 kontrolne bity do hasła (256x256)

# Funkcja zamieniająca tekst na binarną reprezentację ASCII
def txt_to_binary(txt_data):
    binary_data = [format(ord(i), '08b') for i in txt_data]  # Konwersja każdego znaku na 8-bitową reprezentację binarną
    return binary_data

# Funkcja wybierająca piksele do modyfikacji na podstawie klucza i danych tekstowych
def choose_pixels(key, txt_data):
    # Obliczenie liczby pikseli potrzebnych do zakodowania danych tekstowych
    if txt_data != '\'':
        how_much_pixels = len(txt_to_binary(txt_data)) * 3  # Każdy znak tekstowy wymaga 3 pikseli do zakodowania (każdy piksel zawiera 3 wartości: R, G, B)
    else:
        how_much_pixels = min_size  # Minimalny rozmiar obrazu 256x256

    # Pętla wybierająca unikalne piksele na podstawie zahashowanego klucza
    while True:
        hashed_key = hashlib.sha256(key.encode()).digest()  # Utworzenie skrótu SHA-256 z klucza

        hashed_integers = int.from_bytes(hashed_key, byteorder='big')  # Konwersja skrótu na liczbę całkowitą

        random.seed(hashed_integers)  # Ustawienie ziarna generatora liczb losowych na podstawie zahashowanego klucza
        all_pixels = list(range(min_size))  # Utworzenie listy zawierającej indeksy wszystkich pikseli obrazu (minimalny rozmiar obrazu 256x256)
        random.shuffle(all_pixels)  # Wymieszanie indeksów pikseli

        chosen_pixels = all_pixels[:how_much_pixels]  # Wybór określonej liczby pikseli

        # Sprawdzenie, czy wybrane piksele są unikalne
        if len(set(chosen_pixels)) == how_much_pixels:
            break
        else:
            key = key + "_retry"  # Jeśli wybrane piksele nie są unikalne, dodaj sufiks do klucza i spróbuj ponownie

    return chosen_pixels

# Funkcja modyfikująca piksele obrazu na podstawie danych tekstowych i klucza
def modify_pixels(img_pixels, chosen_pixels, txt_data):
    binary_data = txt_to_binary(txt_data)  # Konwersja danych tekstowych na binarną reprezentację ASCII
    byte_index = 0

    for byte in binary_data:
        # Uzyskanie wartości pikseli, które będą modyfikowane
        pixels_to_change = [value for value in img_pixels[chosen_pixels[0]] +
                            img_pixels[chosen_pixels[1]] +
                            img_pixels[chosen_pixels[2]]]

        chosen_pixels = chosen_pixels[3:]  # Usunięcie wykorzystanych pikseli z listy

        # Modyfikacja pikseli na podstawie danych binarnych
        for bit in range(0, 8):
            if byte[bit] == '1':
                if pixels_to_change[bit] % 2 == 0:  # Jeśli bit jest 1 i wartość piksela jest parzysta, zwiększ wartość o 1
                    pixels_to_change[bit] += 1

            if byte[bit] == '0':
                if pixels_to_change[bit] % 2 != 0:  # Jeśli bit jest 0 i wartość piksela jest nieparzysta, zmniejsz wartość o 1
                    if pixels_to_change[bit] == 255:
                        pixels_to_change[bit] -= 1
                    else:
                        pixels_to_change[bit] += 1

        # Dodanie bitu kontrolnego na końcu ostatniego bajtu danych
        if byte_index == len(binary_data) - 1:
            if pixels_to_change[-1] % 2 == 0:
                pixels_to_change[-1] += 1

        pixels_to_change = tuple(pixels_to_change)
        yield pixels_to_change[0:3]  # Zwrócenie krotek zawierających wartości kolorów (R, G, B) zmodyfikowanych pikseli
        yield pixels_to_change[3:6]
        yield pixels_to_change[6:9]

        byte_index += 1

# Funkcja szyfrująca dane tekstowe w obrazie
def encrypt():
    # Wczytanie obrazu
    while True:
        img = input("Podaj nazwe obrazka(PNG): ")
        try:
            image = Image.open(img + '.png', 'r')
            image = image.convert("RGB")
        except:
            print("No i gdzie ten obrazek?")
        else:
            break

    # Wczytanie danych tekstowych do zakodowania
    while True:
        txt_data = input("Wprowadz wiadomosc, ktora chcesz zaszyfrowac: ")
        if txt_data:
            break
        else:
            continue

    # Wczytanie klucza
    while True:
        key = input("Wprowadz klucz, za pomoca ktorego zostanie zakodowana wiadomosc: ")
        if key:
            break
        else:
            continue

    # Wybór pikseli do modyfikacji na podstawie klucza i danych tekstowych
    chosen_pixels = choose_pixels(key, txt_data)
    img_pixels = image.getdata()

    # Modyfikacja pikseli obrazu
    for pixel in modify_pixels(img_pixels, chosen_pixels, txt_data):

        x = chosen_pixels[0] % image.width
        y = chosen_pixels[0] // image.width

        image.putpixel((x, y), pixel)  # Aktualizacja piksela w obrazie
        chosen_pixels = chosen_pixels[1:]  # Przejście do następnych wybranych pikseli

    control_pixel(img, image)

    # Zapisanie zakodowanego obrazu
    encoded_img = input("Podaj nazwe dla zakodowanego obrazu: ")
    image.save(fp=encoded_img + ".png")

    return "\n===POMYSLNIE ZASZYFROWANO WIADOMOSC!==="

# Funkcja deszyfrująca dane tekstowe z obrazu
def decrypt():
    # Wczytanie obrazu
    while True:
        img = input("Podaj nazwe obrazka(PNG): ")
        try:
            image = Image.open(img + ".png", 'r')
            image = image.convert("RGB")
        except:
            print("No i gdzie ten obrazek?")
        else:
            break

    # Wczytanie klucza
    while True:
        key = input("Wprowadz klucz, za pomoca ktorego zostanie odkodowana wiadomosc: ")
        if key:
            break
        else:
            continue

    # Wczytanie pikseli z obrazu do odkodowania
    img_pixels = image.getdata()
    chosen_pixels = choose_pixels(key, txt_data='\'')  # Użyj pustego tekstu jako dane, aby odczytać wybrane piksele
    encoded_data = ''

    # Odkodowanie danych tekstowych z obrazu
    while True:
        pixels_to_decode = [value for value in img_pixels[chosen_pixels[0]] +
                            img_pixels[chosen_pixels[1]] +
                            img_pixels[chosen_pixels[2]]]

        chosen_pixels = chosen_pixels[3:]  # Usunięcie wykorzystanych pikseli z listy

        decoded_binary_data = ''
        for bit in pixels_to_decode[:8]:
            if (bit % 2 == 0):
                decoded_binary_data += '0'
            else:
                decoded_binary_data += '1'

        encoded_data += chr(int(decoded_binary_data, 2))

        # Sprawdzenie, czy odkodowany znak mieści się w zakresie ASCII
        if not 32 <= ord(encoded_data[-1]) <= 126:
            return penalty(img, image)

        if (pixels_to_decode[-1] % 2 != 0):
            break

    control_pixel(img, image)
    return "ZASZYFROWANA WIADOMOSC: " + encoded_data + "\n"

# Funkcja mieszająca pixele przy podaniu złego hasła
def penalty(img, image):
    wrong_key = 0
    secure_pixels = list(image.getdata())
    last_pixel = list(secure_pixels[-1])

    for color in range(3):
        if last_pixel[color] % 2 == 0:
            wrong_key += 1

    if wrong_key < 2:
        last_pixel[wrong_key] -= 1
        secure_pixels[-1] = tuple(last_pixel)
        image.putdata(secure_pixels)
        image.save(fp=img + ".png")
        return "\nWprowadzono bledny klucz! Pozostalo prob: " + str(2 - wrong_key) + "\n"

    else:
        random.shuffle(secure_pixels)
        image.putdata(secure_pixels)
        image.save(fp=img + ".png")
        return "\n===ZBYT DUZA LICZBA NIEPOWODZEN! OBRAZ ZOSTAL ZNISZCZONY!===\n"


# Ustawianie ostatniego pixela obrazu na domyslnie wartości (nieparzyste) do odczytu ilości prób dekodowania
# Każda parzysta liczba w osatatnim pixelu oznacza jedną próbę dekodowania obrazu
def control_pixel(img, image):
    secure_pixels = list(image.getdata())
    last_pixel = list(secure_pixels[-1])
    for color in range(3):
        if last_pixel[color] % 2 == 0:
            last_pixel[color] += 1
    secure_pixels[-1] = tuple(last_pixel)
    image.putdata(secure_pixels)
    image.save(fp=img + ".png")

# Główna funkcja programu
def main():

    while True:
        choose = input("---MENU---\n"
                       "1. Encode\n"
                       "2. Decode\n"
                       "3. Wyjscie\n"
                       "Wybor: ")

        match choose.lower():
            case '1' | "encode":
                print('\033[2J\033[0;0H')  # Czyszczenie konsoli
                print(encrypt()+'\n')

            case '2' | "decode":
                print('\033[2J\033[0;0H')
                print(decrypt())

            case '3' | "wyjscie":
                exit()

            case _:
                print("Nie ma takiej opcji!\n")


if __name__ == '__main__':
    main()
