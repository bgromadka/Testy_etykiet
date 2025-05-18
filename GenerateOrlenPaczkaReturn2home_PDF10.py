import requests
import base64
import os
import xml.etree.ElementTree as ET
import webbrowser
import datetime
from common_data import URL_DICT, OUTPUT_FOLDER, MISSING_LABEL_FILE
import shutil
# Konfiguracja
PARTNER_FILE_NAMES = {

    "TEST000129": "GenerateOrlenPaczkaReturn2Home_Packeta_PDF10.pdf",

}
HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# Funkcja generująca XML dla danego PartnerID i PartnerKey
def generate_soap_body(partner_id, partner_key):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
   <soap:Body>
   <GenerateOrlenPaczkaReturn2Home xmlns="https://91.242.220.103/WebServicePwR">
----------------------------------------------------------Generowanie listu przewozowego z etykieta
       <PartnerID>{partner_id}</PartnerID>
      <PartnerKey>{partner_key}</PartnerKey>


     <DestinationCode>WS-100001</DestinationCode>
            <AlternativeDestinationCode></AlternativeDestinationCode>
----------------------------------------------------------Punkt odbioru
----------------------------------------------------------serwisy
      <Format>PDF10</Format>
            <BoxSize>S</BoxSize>
            <Insurance></Insurance>
            <PackValue></PackValue>
----------------------------------------------------------serwisy
----------------------------------------------------------pole referencji widoczne na etykiecie
<SenderOrders>SenderOrders</SenderOrders>
----------------------------------------------------------pole referencji widoczne na etykiecie

      <OriginalPackageNumber></OriginalPackageNumber>
----------------------------------------------------------Odbiorca
            <PhoneNumber>885779607</PhoneNumber>
            <EMail>tmsec1p9ju+4f9d21f12@user.allegrogroup.pl</EMail>
            <FirstName>FirstName</FirstName>
            <LastName>LastName</LastName>
            <CompanyName>CompanyName</CompanyName>
            <StreetName>StreetName</StreetName>
            <BuildingNumber>1</BuildingNumber>
            <FlatNumber>1</FlatNumber>
            <City>City</City>
            <PostCode>04-347</PostCode>
----------------------------------------------------------Odbiorca
----------------------------------------------------------Nadawca
            <SenderEMail>tmsec1p9ju+4f9d21f12@user.allegrogroup.pl</SenderEMail>
            <SenderFirstName>SenderFirstName</SenderFirstName>
            <SenderLastName>SenderLastName</SenderLastName>
            <SenderCompanyName>SenderCompanyName</SenderCompanyName>
            <SenderStreetName>SenderStreetName</SenderStreetName>
            <SenderBuildingNumber>1</SenderBuildingNumber>
            <SenderFlatNumber>1</SenderFlatNumber>
            <SenderCity>SenderCity</SenderCity>
            <SenderPostCode>04-347</SenderPostCode>
            <SenderPhoneNumber>885779607</SenderPhoneNumber>
----------------------------------------------------------Nadawca
      <ExternalSenderPackageNumber>Ad111111111</ExternalSenderPackageNumber>
      <ExternalPackageNumber></ExternalPackageNumber>
      <Serwis></Serwis>
      <ItemsInPackage></ItemsInPackage>

    </GenerateOrlenPaczkaReturn2Home>
  </soap:Body>
</soap:Envelope>"""

# Funkcja wysyłająca zapytanie SOAP i pobierająca etykietę
def get_label(partner_id, partner_key, url):
    """Wysyła zapytanie SOAP i pobiera etykietę w formacie Base64."""
    soap_body = generate_soap_body(partner_id, partner_key)

    response = requests.post(url, data=soap_body, headers=HEADERS, verify=True)

    if response.status_code != 200:
        print(f"Treść odpowiedzi: {response.text}")
        raise Exception(f"Błąd żądania: {response.status_code}\n{response.text}")

    # Wydrukowanie odpowiedzi, aby sprawdzić, co zwraca serwer
    print("Odpowiedź SOAP z serwera:")
    print(response.text)

    # Parsowanie XML odpowiedzi
    root = ET.fromstring(response.text)

    # Namespace w odpowiedzi, który może być potrzebny przy wyszukiwaniu elementów XML
    namespaces = {
        'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
        '': 'https://91.242.220.103/WebServicePwR'  # Default namespace, musimy go uwzględnić
    }

    # Sprawdzanie, czy <LabelData> znajduje się w odpowiedzi
    label_data = root.find(".//LabelData", namespaces=namespaces)

    pack_codes = root.findall(".//PackCode_RUCH", namespaces=None)
    result_pack_code = '__'.join(el.text for el in pack_codes)

    return label_data.text if label_data is not None else None, result_pack_code

# Funkcja dekodująca Base64 i zapisująca PDF w określonym folderze
def decode_and_save_pdf(base64_data, pack_code, main_folder, method_folder_name, output_filename, url_name):
    """Dekoduje dane Base64 i zapisuje je jako plik PDF10 w określonym folderze z datą i godziną w nazwie pliku."""
    try:


        # Ścieżka do folderu metody wewnątrz "wygenerowane etykiety"
        method_folder = os.path.join(main_folder, method_folder_name)
        os.makedirs(method_folder, exist_ok=True)
        print(f"Folder metody '{method_folder_name}' został utworzony: {method_folder}")

        # Upewniamy się, że folder istnieje
        os.makedirs(method_folder, exist_ok=True)
        print(f"Folder docelowy: {method_folder}")

        # Pobranie aktualnej daty i godziny
        current_time = datetime.datetime.now().strftime("%Y-%m-%d")

        # Tworzenie nowej nazwy pliku z datą i godziną
        filename, file_extension = os.path.splitext(output_filename)
        new_output_filename = f"{filename}__{url_name}__{pack_code}__{current_time}{file_extension}"
        print(f"Nowa nazwa pliku: {new_output_filename}")

        # Pełna ścieżka do pliku PDF
        output_path = os.path.join(method_folder, new_output_filename)
        print(f"Pełna ścieżka do pliku: {output_path}")

        # Dekodowanie Base64 i zapis do pliku PDF10
        if base64_data is None:
            shutil.copy(MISSING_LABEL_FILE, output_path)

        else:
            pdf_data = base64.b64decode(base64_data)
            print(f"Długość danych PDF: {len(pdf_data)} bajtów")

            with open(output_path, "wb") as pdf_file:
                pdf_file.write(pdf_data)
                print(f"Plik PDF zapisany: {output_path}")
        # Otwórz plik PDF10 w przeglądarce
        #webbrowser.open(f'file://{os.path.abspath(output_path)}')
        #print(f"Etykieta zapisana: {output_path} i otwarta w przeglądarce.")
    except Exception as e:
        raise Exception(f"Błąd podczas zapisywania pliku PDF: {e}")

if __name__ == "__main__":

    # Nazwa folderu metody (np. nazwa skryptu lub funkcji)
    method_folder_name = "GenerateOrlenPaczkaReturn2home_PDF10"

    # Lista partnerów (PartnerID, PartnerKey)
    partners = [





        ("TEST000129", "TTFWWSCSVO"),


    ]

    print("Pobieranie etykiet...")

    try:
        # Generowanie etykiety dla każdego partnera
        for url_name, url_value in URL_DICT.items():
            for partner_id, partner_key in partners:
                print(f"Generowanie etykiety dla partnera {partner_id}...")
                response_data = get_label(partner_id, partner_key, url_value)
                decode_and_save_pdf(response_data[0], response_data[1], OUTPUT_FOLDER, method_folder_name,
                                    PARTNER_FILE_NAMES[partner_id], url_name)
    except Exception as e:
        print(f"Wystąpił błąd: {e}")