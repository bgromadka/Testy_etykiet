import subprocess


URL_DICT = {
    "public-api-url": "https://api-test.orlenpaczka.pl/WebServicePwR/WebServicePwR.asmx",
    "iis-api-url": "http://bruchorpact03/WebServicePwR/WebServicePwR.asmx",
    "kub-api-url": "http://bruchorpact03/WebServicePwRKube/WebServicePwR.asmx",
}

OUTPUT_FOLDER = r"C:\Users\bgromadka\Desktop\projekty\etykiety"


SCRIPT_LIST = [
    "GenerateLabelBusinessPack.py",
    "GenerateLabelBusinessPackAllegro.py",
    "GenerateLabelBusinessPackList_EPL.py", # ToDo lack of conversion from epl to png
    "GenerateLabelBusinessPackList_PDF.py",
    "GenerateLabelBusinessPackList_PDF10.py",
    # "GenerateLabelBusinessPackListAllegro_EPL.py", # ToDo lack of conversion from epl to png. An error occurred: Label data not found in SOAP response.
    "GenerateLabelBusinessPackListAllegro_PDF.py",
    "GenerateLabelBusinessPackListAllegro_PDF10.py"
    "GenerateLabelBusinessPackListAllegro_ZPL.py", # Zamiast zpl zwraca pdf
    "GenerateLabelBusinessPackListTwo_EPL.py", # ToDo lack of conversion from epl to png
    "GenerateLabelBusinessPackListTwo_PDF.py",
    "GenerateLabelBusinessPackListTwo_PDF10.py",
    "GenerateLabelBusinessPackListTwo_ZPL.py",
    "GenerateLabelBusinessPackTwo.py",
    "GenerateOrlenPaczkaLabel_PDF.py", # ToDo wywala się przy próbie pobrania allegro!
    "GenerateOrlenPaczkaLabel_PDF.py"
    "GenerateOrlenPaczkaLabel_ZPL.py",
    "GenerateOrlenPaczkaReturn2home_EPL.py"
    "GenerateOrlenPaczkaReturn2home_PDF.py" #brak etykiety dla kub
    "GenerateOrlenPaczkaReturn2home_PDF10.py" #brak etykiety dla kub
    "GenerateOrlenPaczkaReturn2home_ZPL.py" #brak etykiety dla kub
    "GenerateStandardCustomerReturn_PDF.py"
    "GenerateStandardCustomerReturn_PDF10.py"
    "GenerateStandardCustomerReturn_ZPL.py" #nie zwraca zakodowanej etykiety
    "GenerateStnadardCustomerReturn_EPL.py" #brak etykiety dla kub
    "LabelPrintDuplicate.py"
    "LabelPrintDuplicateList.py"
    "LabelPrintDuplicateListTwo_EPL.py"
    "LabelPrintDuplicateListTwo_PDF.py"
    "LabelPrintDuplicateListTwo_PDF10.py"
    "LabelPrintDuplicateListTwo_ZPL.py"
    "LabelPrintDuplicateTwo_EPL.py"
    "LabelPrintDuplicateTwo_PDF.py"
    "LabelPrintDuplicateTwo_PDF10.py"
    "LabelPrintDuplicateTwo_ZPL.py"
]


def main():
    for script in SCRIPT_LIST:
        subprocess.run(["python", script])


if __name__ == "__main__":
    main()