import shutil

import requests
import base64
import os
import xml.etree.ElementTree as ET

import datetime

from common_data import OUTPUT_FOLDER, URL_DICT, MISSING_LABEL_FILE

# Konfiguracja
HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# Mapowanie partnerów na nazwy plików
PARTNER_FILE_NAMES = {
    "PWR0000006": "GenerateLabelBusinessPackList__standard__EPL.epl",
    "TEST000859": "GenerateLabelBusinessPackList__meest__EPL.epl",
    "TEST003483": "GenerateLabelBusinessPackList__Vinted__EPL.epl",
}

# Funkcja generująca XML dla danego PartnerID i PartnerKey
def generate_soap_body(partner_id, partner_key):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GenerateLabelBusinessPackList xmlns="https://91.242.220.103/WebServicePwR">
      <PartnerID>{partner_id}</PartnerID>
      <PartnerKey>{partner_key}</PartnerKey>
      <Format>EPL</Format>
      <BusinessPackList>
        <BusinessPack>
          <BoxSize>S</BoxSize>
          <DestinationCode>WS-100001</DestinationCode>
          <SenderOrders>referencja-1</SenderOrders>
          <SenderEMail>test@nadawca.pl</SenderEMail>
          <SenderCompanyName>Firmanadawcaźśźćżą</SenderCompanyName>
          <SenderFirstName>imienadawca1</SenderFirstName>
          <SenderLastName>nazwiskonadawca1</SenderLastName>
          <SenderStreetName>ulicanadawca1</SenderStreetName>
          <SenderFlatNumber>1</SenderFlatNumber>
          <SenderBuildingNumber>2</SenderBuildingNumber>
          <SenderCity>Warszawa</SenderCity>
          <SenderPostCode>99-999</SenderPostCode>
          <SenderPhoneNumber>885779607</SenderPhoneNumber>
          <PrintAdress>1</PrintAdress>
          <PrintType>1</PrintType>
          <CashOnDelivery>F</CashOnDelivery>
          <AmountCashOnDelivery>1234</AmountCashOnDelivery>
          <TransferDescription>opis transakcji 1</TransferDescription>
          <EMail>pz59fbsv0e+3d809d138@user.allegrogroup.pl</EMail>
          <FirstName>odbiorcaimie1</FirstName>
          <LastName>odbiorcanazwisko1</LastName>
          <PhoneNumber>885779607</PhoneNumber>
          <CompanyName>firmaodbiorca1</CompanyName>
          <StreetName>ulicaodbiorca1</StreetName>
          <BuildingNumber>1</BuildingNumber>
          <FlatNumber>1</FlatNumber>
          <City>miastoodbiorca1</City>
          <PostCode>99-999</PostCode>
        </BusinessPack>
        <BusinessPack>
          <BoxSize>S</BoxSize>
          <DestinationCode>WS-100001</DestinationCode>
          <SenderOrders>referencja-2</SenderOrders>
          <SenderEMail>test@nadawca.pl</SenderEMail>
          <SenderCompanyName>Firmanadawca</SenderCompanyName>
          <SenderFirstName>imienadawca2</SenderFirstName>
          <SenderLastName>nazwiskonadawca2</SenderLastName>
          <SenderStreetName>ulicanadawca2</SenderStreetName>
          <SenderFlatNumber>1</SenderFlatNumber>
          <SenderBuildingNumber>2</SenderBuildingNumber>
          <SenderCity>Warszawa</SenderCity>
          <SenderPostCode>99-999</SenderPostCode>
          <SenderPhoneNumber>885779607</SenderPhoneNumber>
          <PrintAdress>1</PrintAdress>
          <PrintType>1</PrintType>
          <CashOnDelivery>F</CashOnDelivery>
          <AmountCashOnDelivery>1234</AmountCashOnDelivery>
          <TransferDescription>opis transakcji 2</TransferDescription>
          <EMail>pz59fbsv0e+3d809d138@user.allegrogroup.pl</EMail>
          <FirstName>odbiorcaimie2</FirstName>
          <LastName>odbiorcanazwisko2</LastName>
          <PhoneNumber>885779607</PhoneNumber>
          <CompanyName>firmaodbiorca2</CompanyName>
          <StreetName>ulicaodbiorca2</StreetName>
          <BuildingNumber>1</BuildingNumber>
          <FlatNumber>1</FlatNumber>
          <City>miastoodbiorca2</City>
          <PostCode>99-999</PostCode>
        </BusinessPack>
      </BusinessPackList>
    </GenerateLabelBusinessPackList>
  </soap:Body>
</soap:Envelope>"""

def decode_and_save_EPL(base64_data, pack_code, main_folder, method_folder_name, output_filename, url_name):
    """Dekoduje dane Base64 i zapisuje je jako plik EPL w określonym folderze z datą i godziną w nazwie pliku."""
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

        # Pełna ścieżka do pliku EPL
        output_path = os.path.join(method_folder, new_output_filename)
        print(f"Pełna ścieżka do pliku: {output_path}")

        # Dekodowanie Base64
        if base64_data is None:
            shutil.copy(MISSING_LABEL_FILE, output_path)
        else:
            epl_data = base64.b64decode(base64_data)

            with open(output_path, "wb") as EPL_file:
                EPL_file.write(epl_data)
                print(f"Plik EPL zapisany: {output_path}")

    except Exception as e:
        print(f"Błąd podczas zapisywania pliku EPL: {e}")


def get_label(partner_id, partner_key,url):
    """Wysyła zapytanie SOAP i pobiera etykietę w formacie Base64."""
    soap_body = generate_soap_body(partner_id, partner_key)

    response = requests.post(url, data=soap_body, headers=HEADERS, verify=True)

    if response.status_code != 200:
        # Funkcja wysyłająca zapytanie SOAP i pobierająca etykietę
        print(f"Treść odpowiedzi: {response.text}")
        raise Exception(f"Błąd żądania: {response.status_code}\n{response.text}")

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


# Główna część programu
if __name__ == "__main__":

    # Nazwa folderu metody (np. nazwa skryptu lub funkcji)
    method_folder_name = "GenerateLabelBusinessPackList_EPL"

    # Lista partnerów (PartnerID, PartnerKey)
    partners = [
        ("PWR0000006", "1234"),
        ("TEST000859", "SMS8IKIF3A"),
        ("TEST003483", "F2E087C0B9"),
    ]

    print("Pobieranie etykiet...")

    try:
        for url_name, url_value in URL_DICT.items():
            for partner_id, partner_key in partners:
                print(f"Generowanie etykiety dla {partner_id}...")
                response_data = get_label(partner_id, partner_key, url_value)
                decode_and_save_EPL(response_data[0], response_data[1], OUTPUT_FOLDER, method_folder_name,
                                    PARTNER_FILE_NAMES[partner_id], url_name)

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

