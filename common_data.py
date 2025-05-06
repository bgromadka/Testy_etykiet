import subprocess


URL_DICT = {
    "public-api-url": "https://api-test.orlenpaczka.pl/WebServicePwR/WebServicePwR.asmx",
    "kub-api-url": "http://bruchorpact03/WebServicePwRKube/WebServicePwR.asmx",
    "iis-api-url": "http://bruchorpact03/WebServicePwR/WebServicePwR.asmx"
}

OUTPUT_FOLDER = r"C:\Users\kdabek\Desktop\generowanie etykiet- dokumentacja\Etykiety"


SCRIPT_LIST = [
    "GenerateLabelBusinessPack.py",
    "GenerateLabelBusinessPackAllegro.py",
    # "GenerateLabelBusinessPackList_EPL.py", # ToDO
    "GenerateLabelBusinessPackList_PDF.py",
    "GenerateLabelBusinessPackList_PDF10.py",
    # "GenerateLabelBusinessPackListAllegro_EPL.py", # ToDO
    # "GenerateLabelBusinessPackListAllegro_PDF.py", # ToDO
    # "GenerateLabelBusinessPackListAllegro_PDF10.py", # ToDO
    "GenerateLabelBusinessPackListAllegro_ZPL.py", # Zamiast zpl zwraca pdf
    # "GenerateLabelBusinessPackListTwo_EPL.py", # ToDO
    # "GenerateLabelBusinessPackListTwo_PDF.py", # ToDO
    "GenerateLabelBusinessPackListTwo_PDF10.py",
    "GenerateLabelBusinessPackListTwo_ZPL.py",


]


def main():
    for script in SCRIPT_LIST:
        subprocess.run(["python", script])


if __name__ == "__main__":
    main()