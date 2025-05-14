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
    "PWR0000006": "GenerateLabelBusinessPackList__standard__PDF10.pdf",
    "TEST000859": "GenerateLabelBusinessPackList__meest__PDF10.pdf",
    "TEST003483": "GenerateLabelBusinessPackList__Vinted__PDF10.pdf",
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
      <Format>PDF10</Format>
      <BusinessPackList>
        <BusinessPack>
          <BoxSize>S</BoxSize>
          <DestinationCode>WS-100001</DestinationCode>
          <SenderOrders>referencja-1</SenderOrders>
          <SenderEMail>test@nadawca.pl</SenderEMail>
          <SenderCompanyName>Firmanadawca</SenderCompanyName>
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


# Funkcja dekodująca Base64 i zapisująca PDF10 w określonym folderze
def decode_and_save_pdf10(base64_data, pack_code, main_folder, method_folder_name, output_filename, url_name):
    """Dekoduje dane Base64 i zapisuje je jako plik PDF10 w określonym folderze z datą i godziną w nazwie pliku."""
    try:
        # Ścieżka do folderu metody wewnątrz "wygenerowane etykiety"
        method_folder = os.path.join(main_folder, method_folder_name)
        os.makedirs(method_folder, exist_ok=True)
        print(f"Folder metody '{method_folder_name}' został utworzony: {method_folder}")

        # Pobranie aktualnej daty i godziny
        current_time = datetime.datetime.now().strftime("%H-%M-%S")

        # Tworzenie nowej nazwy pliku z datą i godziną
        filename, file_extension = os.path.splitext(output_filename)
        new_output_filename = f"{filename}__{url_name}__{pack_code}__{current_time}{file_extension}"

        # Pełna ścieżka do pliku PDF10
        output_path = os.path.join(method_folder, new_output_filename)

        # Dekodowanie Base64 i zapis do pliku PDF10
        if base64_data is None:
            shutil.copy(MISSING_LABEL_FILE, output_path)

        else:
            pdf_data = base64.b64decode(base64_data)
            print(f"Długość danych PDF: {len(pdf_data)} bajtów")

            with open(output_path, "wb") as pdf_file:
                pdf_file.write(pdf_data)
                print(f"Plik PDF zapisany: {output_path}")

    except Exception as e:
        print(f"Błąd podczas zapisywania pliku PDF10: {e}")

if __name__ == "__main__":
    # Ścieżka do folderu, w którym będą zapisane etykiety
    folder_name = "GenerateLabelBusinessPackList_PDF10"

    # Lista partnerów (pary PartnerID, PartnerKey)
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
                decode_and_save_pdf10(response_data[0], response_data[1],  OUTPUT_FOLDER, folder_name,
                                      PARTNER_FILE_NAMES[partner_id], url_name)

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
