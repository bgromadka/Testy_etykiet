import os
import subprocess


URL_DICT = {
    "public-api-url": "https://api-test.orlenpaczka.pl/WebServicePwR/WebServicePwR.asmx",
    "iis-api-url": "http://bruchorpact03/WebServicePwR/WebServicePwR.asmx",
    "kub-api-url": "http://bruchorpact03/WebServicePwRKube/WebServicePwR.asmx",
}

script_directory = os.path.dirname(os.path.abspath(__file__))

OUTPUT_FOLDER = os.path.join(script_directory, 'label_report_generator\input_labels_folder')

MISSING_LABEL_FILE = os.path.join(script_directory, 'missing_label.pdf')

SCRIPT_LIST = [
    "GenerateLabelBusinessPack.py",
    "GenerateLabelBusinessPackAllegro.py",
    "GenerateLabelBusinessPackList_EPL.py",
    "GenerateLabelBusinessPackList_PDF.py",
    "GenerateLabelBusinessPackList_PDF10.py",
    # "GenerateLabelBusinessPackListAllegro_EPL.py", # incorrect PartnerID or PartnerKey
    "GenerateLabelBusinessPackListAllegro_PDF.py",
    "GenerateLabelBusinessPackListAllegro_PDF10.py",
    "GenerateLabelBusinessPackListAllegro_ZPL.py", # pdf zamiast zpl
    "GenerateLabelBusinessPackListTwo_EPL.py",
    "GenerateLabelBusinessPackListTwo_PDF.py",
    "GenerateLabelBusinessPackListTwo_PDF10.py",
    "GenerateLabelBusinessPackListTwo_ZPL.py",
    "GenerateLabelBusinessPackTwo.py",
    "GenerateOrlenPaczkaLabel_PDF.py",
    "GenerateOrlenPaczkaLabel_PDF10.py",
    "GenerateOrlenPaczkaLabel_ZPL.py",
    "GenerateOrlenPaczkaReturn2home_EPL.py",
    "GenerateOrlenPaczkaReturn2home_PDF.py",
    "GenerateOrlenPaczkaReturn2home_PDF10.py",
    "GenerateOrlenPaczkaReturn2home_ZPL.py",
    "GenerateStandardCustomerReturn_PDF.py",
    "GenerateStandardCustomerReturn_PDF10.py",
    "GenerateStandardCustomerReturn_ZPL.py",
    "GenerateStnadardCustomerReturn_EPL.py",
    "LabelPrintDuplicate.py",
    "LabelPrintDuplicateList.py",
    # "LabelPrintDuplicateListTwo_EPL.py",
    # "LabelPrintDuplicateListTwo_PDF.py",
    # "LabelPrintDuplicateListTwo_PDF10.py",
    # "LabelPrintDuplicateListTwo_ZPL.py",
    # "LabelPrintDuplicateTwo_EPL.py",
    # "LabelPrintDuplicateTwo_PDF.py",
    # "LabelPrintDuplicateTwo_PDF10.py",
    # "LabelPrintDuplicateTwo_ZPL.py",
]


def main():
    for script in SCRIPT_LIST:
        subprocess.run(["python", script])


if __name__ == "__main__":
    main()