import shutil

import requests
import base64
import os
import xml.etree.ElementTree as ET
import datetime

from common_data import URL_DICT, OUTPUT_FOLDER, MISSING_LABEL_FILE

# Konfiguracja
HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# Mapowanie partnerów na nazwy plików
PARTNER_FILE_NAMES = {
    "PWR0000006": "GenerateLabelBusinessPackTwo__standard__PDF.pdf",
    "TEST000859": "GenerateLabelBusinessPackTwo__meest__PDF.pdf",
    "TEST003483": "GenerateLabelBusinessPackTwo__Vinted__PDF.pdf",
}

# Funkcja generująca XML dla danego PartnerID i PartnerKey
def generate_soap_body(partner_id, partner_key):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GenerateLabelBusinessPackTwo xmlns="https://91.242.220.103/WebServicePwR">
      <PartnerID>{partner_id}</PartnerID>
      <PartnerKey>{partner_key}</PartnerKey>
      <DestinationCode>WS-100001</DestinationCode>
            <AlternativeDestinationCode></AlternativeDestinationCode>
----------------------------------------------------------Punkt odbioru
----------------------------------------------------------serwisy
            <BoxSize>S</BoxSize>
            <Insurance></Insurance>
            <PackValue></PackValue>
            <CashOnDelivery></CashOnDelivery>
            <AmountCashOnDelivery></AmountCashOnDelivery>
                        <TransferDescription>TransferDescription</TransferDescription>
                        <PrintType>1</PrintType>
----------------------------------------------------------serwisy
----------------------------------------------------------pole referencji widoczne na etykiecie
<SenderOrders>SenderOrders</SenderOrders>
----------------------------------------------------------pole referencji widoczne na etykiecie
----------------------------------------------------------Odbiorca
            <PhoneNumber>885779607</PhoneNumber>
            <EMail>testypostman@ruch.com.pl</EMail>
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
            <SenderEMail>testypostman@ruch.com.pl</SenderEMail>
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
----------------------------------------------------------zwrot
            <ReturnDestinationCode></ReturnDestinationCode>
            <ReturnEMail></ReturnEMail>
            <ReturnFirstName></ReturnFirstName>
            <ReturnLastName></ReturnLastName>
            <ReturnCompanyName></ReturnCompanyName>
            <ReturnStreetName></ReturnStreetName>
            <ReturnBuildingNumber></ReturnBuildingNumber>
            <ReturnFlatNumber></ReturnFlatNumber>
            <ReturnCity></ReturnCity>
            <ReturnPostCode></ReturnPostCode>
            <ReturnPhoneNumber></ReturnPhoneNumber>
            <ReturnPack></ReturnPack>-------zwrot czy nie 
<PrintAdress>1</PrintAdress>-------wybór adresu do wydruku przy zwrocie  1- adres odbiorcy, 2 - adres zwrotu

            <ReturnAvailable></ReturnAvailable>
            <ReturnQuantity></ReturnQuantity>
            ----------------------------------------------------------zwrot
    </GenerateLabelBusinessPackTwo>
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

    # Parsowanie XML odpowiedzi
    root = ET.fromstring(response.text)

    # Namespace w odpowiedzi, który może być potrzebny przy wyszukiwaniu elementów XML
    namespaces = {
        'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
        '': 'https://91.242.220.103/WebServicePwR'  # Default namespace, musimy go uwzględnić
    }

    # Pobranie danych etykiety
    label_data = root.find(".//LabelData", namespaces=namespaces)

    pack_codes = root.findall(".//PackCode_RUCH", namespaces=None)
    result_pack_code = '__'.join(el.text for el in pack_codes)

    return label_data.text if label_data is not None else None, result_pack_code


# Funkcja dekodująca Base64 i zapisująca PDF w określonym folderze
def decode_and_save_pdf(base64_data, pack_code, main_folder, method_folder_name, output_filename, url_name):
    """Dekoduje dane Base64 i zapisuje je jako plik PDF w określonym folderze z datą i godziną w nazwie pliku."""
    try:
        # Ścieżka do folderu metody wewnątrz "wygenerowane etykiety"
        method_folder = os.path.join(main_folder, method_folder_name)
        os.makedirs(method_folder, exist_ok=True)
        print(f"Folder metody '{method_folder_name}' został utworzony: {method_folder}")

        # Upewniamy się, że folder istnieje
        os.makedirs(method_folder, exist_ok=True)
        print(f"Folder docelowy: {method_folder}")

        # Pobranie aktualnej daty i godziny
        current_time = datetime.datetime.now().strftime("%H-%M-%S")

        # Tworzenie nowej nazwy pliku z datą i godziną
        filename, file_extension = os.path.splitext(output_filename)
        new_output_filename = f"{filename}__{url_name}__{pack_code}__{current_time}{file_extension}"
        print(f"Nowa nazwa pliku: {new_output_filename}")

        # Pełna ścieżka do pliku PDF
        output_path = os.path.join(method_folder, new_output_filename)
        print(f"Pełna ścieżka do pliku: {output_path}")

        # Dekodowanie Base64 i zapis do pliku PDF
        if base64_data is None:
            shutil.copy(MISSING_LABEL_FILE, output_path)

        else:
            data = base64.b64decode(base64_data)
            print(f"Długość danych pliku: {len(data)} bajtów")

            with open(output_path, "wb") as file:
                file.write(data)
                print(f"Plik zapisany: {output_path}")

    except Exception as e:
        print(f"Błąd podczas zapisywania pliku PDF: {e}")


if __name__ == "__main__":

    # Nazwa metody (np. nazwa skryptu lub funkcji)
    method_folder_name = "GenerateLabelBusinessPackTwo_PDF"

    # Lista partnerów (PartnerID, PartnerKey)
    partners = [
        ("PWR0000006", "1234"),
        ("TEST000859", "SMS8IKIF3A"),
        ("TEST003483", "F2E087C0B9"),
    ]

    try:
        for url_name, url_value in URL_DICT.items():
            for partner_id, partner_key in partners:
                print(f"Generowanie etykiety dla {partner_id}...")
                response_data = get_label(partner_id, partner_key, url_value)
                decode_and_save_pdf(response_data[0], response_data[1], OUTPUT_FOLDER,
                                    method_folder_name, PARTNER_FILE_NAMES[partner_id], url_name)

    except Exception as e:
        print(f"Wystąpił błąd: {e}")