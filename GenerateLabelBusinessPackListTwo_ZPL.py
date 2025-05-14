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
    "PWR0000006": "GenerateLabelBusinessPackListTwo__standard__ZPL.zpl",
    "TEST000859": "GenerateLabelBusinessPackListTwo__Meest__ZPL.zpl",
    "TEST003483": "GenerateLabelBusinessPackListTwo__Vinted__ZPL.zpl",
}


# Funkcja generująca XML dla danego PartnerID i PartnerKey
def generate_soap_body(partner_id, partner_key):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
   <GenerateLabelBusinessPackListTwo xmlns="https://91.242.220.103/WebServicePwR">
      <PartnerID>{partner_id}</PartnerID>
      <PartnerKey>{partner_key}</PartnerKey>
      <AutoDestinationChange>T</AutoDestinationChange>
        
      <Format>ZPL</Format>
      <BusinessPackList>
        <BusinessPack>
          <ConfirmTermsOfUse>T</ConfirmTermsOfUse>
          <ConfirmMarketing>T</ConfirmMarketing>
          <CofirmMailing>T</CofirmMailing>
          <DestinationCode>WS-100001</DestinationCode>
          <AlternativeDestinationCode></AlternativeDestinationCode>
          <BoxSize>S</BoxSize>
          <PackValue>12345</PackValue>
          <CashOnDelivery>F</CashOnDelivery>
          <AmountCashOnDelivery>12345</AmountCashOnDelivery>
          <Insurance>F</Insurance>
          <EMail>kasiatester@wp.pl</EMail>
          <FirstName>Katarzyna</FirstName>
          <LastName>Nowakowska</LastName>
          <CompanyName>RUCH S.A.</CompanyName>
          <StreetName>Kwiatowa</StreetName>
          <BuildingNumber>44</BuildingNumber>
          <FlatNumber>33</FlatNumber>
          <City>Kalisz</City>
          <PostCode>87-999</PostCode>
          <PhoneNumber>885779607</PhoneNumber>
          <SenderEMail>sender@wp.pl</SenderEMail>
          <SenderFirstName>Jan</SenderFirstName>
          <SenderLastName>Nadawczyk</SenderLastName>
          <SenderCompanyName>Firma Jana</SenderCompanyName>
          <SenderStreetName>Drewnowska</SenderStreetName>
          <SenderBuildingNumber>66</SenderBuildingNumber>
          <SenderFlatNumber>777</SenderFlatNumber>
          <SenderCity>Grudziadz</SenderCity>
          <SenderPostCode>09-777</SenderPostCode>
          <SenderPhoneNumber>885779607</SenderPhoneNumber>
          <SenderOrders>Komentarz Do Zamówienia</SenderOrders>
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
          <ReturnPack></ReturnPack>
          <TransferDescription>TytulPrzelewu</TransferDescription>
          <PrintAdress>1</PrintAdress>
          <ReturnAvailable>N</ReturnAvailable>
          <ReturnQuantity></ReturnQuantity>
          <PrintType>1</PrintType>
        </BusinessPack>
        <BusinessPack>
          <ConfirmTermsOfUse>T</ConfirmTermsOfUse>
          <ConfirmMarketing>T</ConfirmMarketing>
          <CofirmMailing>T</CofirmMailing>
          <DestinationCode>WS-100001-27-26</DestinationCode>
          <AlternativeDestinationCode></AlternativeDestinationCode>
          <BoxSize>M</BoxSize>
          <PackValue>5554</PackValue>
          <CashOnDelivery>F</CashOnDelivery>
          <AmountCashOnDelivery>5554</AmountCashOnDelivery>
          <Insurance>F</Insurance>
          <EMail>kasiatester@wp.pl</EMail>
          <FirstName>Alicja</FirstName>
          <LastName>Grzelakowska</LastName>
          <CompanyName>RUCH S.A.</CompanyName>
          <StreetName>Rozana</StreetName>
          <BuildingNumber>44</BuildingNumber>
          <FlatNumber>10</FlatNumber>
          <City>Grudziadz</City>
          <PostCode>87-999</PostCode>
          <PhoneNumber>885779607</PhoneNumber>
          <SenderEMail>sender@wp.pl</SenderEMail>
          <SenderFirstName>Jan</SenderFirstName>
          <SenderLastName>Nadawczyk</SenderLastName>
          <SenderCompanyName>Firma Jana</SenderCompanyName>
          <SenderStreetName>Drewnowska</SenderStreetName>
          <SenderBuildingNumber>66</SenderBuildingNumber>
          <SenderFlatNumber>777</SenderFlatNumber>
          <SenderCity>Grudziadz</SenderCity>
          <SenderPostCode>09-777</SenderPostCode>
          <SenderPhoneNumber>885779607</SenderPhoneNumber>
          <SenderOrders>Komentarz Do Zamówienia</SenderOrders>
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
          <ReturnPack></ReturnPack>
          <TransferDescription>TytulPrzelewu</TransferDescription>
          <PrintAdress>1</PrintAdress>
          <ReturnAvailable>N</ReturnAvailable>
          <ReturnQuantity></ReturnQuantity>
          <PrintType>1</PrintType>
        </BusinessPack>
      </BusinessPackList>
    </GenerateLabelBusinessPackListTwo>
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

    # Sprawdzanie, czy <LabelData> znajduje się w odpowiedzi
    label_data = root.find(".//LabelData", namespaces=namespaces)

    pack_codes = root.findall(".//PackCode_RUCH", namespaces=None)
    result_pack_code = '__'.join(el.text for el in pack_codes)

    return label_data.text if label_data is not None else None, result_pack_code


# Funkcja dekodująca Base64 i zapisująca ZPL
def decode_and_save_zpl(base64_data, pack_code, main_folder, method_folder_name, output_filename, url_name):
    """Dekoduje dane Base64 i zapisuje je jako plik ZPL w określonym folderze z datą i godziną w nazwie pliku."""
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
        print(f"Błąd podczas zapisywania pliku: {e}")


# Główna część programu
if __name__ == "__main__":

    # Nazwa folderu metody (np. nazwa skryptu lub funkcji)
    method_folder_name = "GenerateLabelBusinessPackListTwo_ZPL"

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
                decode_and_save_zpl(response_data[0], response_data[1], OUTPUT_FOLDER,
                                    method_folder_name, PARTNER_FILE_NAMES[partner_id], url_name)

    except Exception as e:
        print(f"Wystąpił błąd: {e}")