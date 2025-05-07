from lxml import etree

import requests
import base64
import os
import xml.etree.ElementTree as ET
import datetime
from common_data import URL_DICT, OUTPUT_FOLDER

# Mapowanie partnerów na nazwy plików
PARTNER_FILE_NAMES = {
    "PWR0000006": "LabelPrintDuplicate_standard_PDF.pdf",
    "TEST000859": "LabelPrintDuplicate_meest_PDf.pdf",
    "TEST003483": "LabelPrintDuplicate_Vinted_PDF.pdf",

}
HEADERS = {"Content-Type": "text/xml; charset=utf-8"}


# Funkcja generująca XML dla GenerateLabelBusinessPack
def generate_label_business_pack_body(partner_id, partner_key):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GenerateLabelBusinessPack xmlns="https://91.242.220.103/WebServicePwR">
      <PartnerID>{partner_id}</PartnerID>
      <PartnerKey>{partner_key}</PartnerKey>
      <BoxSize>L</BoxSize>
----------------------------------------------------------rozmiar paczki- gabaryt
      ----------------------------------------------------------Punkt odbioru
      <DestinationCode>WS-100001</DestinationCode>
      <AlternativeDestinationCode></AlternativeDestinationCode>
      ----------------------------------------------------------Punkt odbioru
----------------------------------------------------------pole referencji widoczne na etykiecie
<SenderOrders>referencja-/</SenderOrders>
----------------------------------------------------------pole referencji widoczne na etykiecie
----------------------------------------------------------Nadawca
<SenderEMail>test@nadawca.pl</SenderEMail>
<SenderCompanyName>Firmanadawca</SenderCompanyName>
<SenderFirstName>imienadawca</SenderFirstName>
<SenderLastName>nazwiskonadawca</SenderLastName>
<SenderStreetName>ulicanadawca</SenderStreetName>
<SenderFlatNumber>1</SenderFlatNumber>
<SenderBuildingNumber>2</SenderBuildingNumber>
<SenderCity>Warszawa</SenderCity>
<SenderPostCode>99-999</SenderPostCode>
<SenderPhoneNumber>885779607</SenderPhoneNumber>
<PrintAdress>1</PrintAdress>
<PrintType>1</PrintType>

----------------------------------------------------------Nadawca


----------------------------------------------------------dodatkowe serwisy
      <Insurance></Insurance>--T-F
      <PackValue></PackValue>--kwota

      <CashOnDelivery>F</CashOnDelivery>--T-F
      <AmountCashOnDelivery>1234</AmountCashOnDelivery>--kwota
          <TransferDescription>opis transakcji</TransferDescription>
----------------------------------------------------------dodatkowe serwisy



----------------------------------------------------------Odbiorca
      <EMail>f8evljcyjw+7a6e0eca8@user.allegrogroup.pl</EMail>
      <FirstName>odbiorcaimie</FirstName>
      <LastName>odbiorcanazwisko</LastName>
      <PhoneNumber>885779607</PhoneNumber>
      <CompanyName>firmaodbiorca</CompanyName>
      <StreetName>ulicaodbiorca</StreetName>
      <BuildingNumber>1</BuildingNumber>
      <FlatNumber>1</FlatNumber>
      <City>miastoodbiorca</City>
      <PostCode>99-999</PostCode>
----------------------------------------------------------Odbiorca
    </GenerateLabelBusinessPack>
  </soap:Body>
</soap:Envelope>"""


# Funkcja generująca XML dla LabelPrintDuplicate
def generate_soap_body(partner_id, partner_key, pack_code):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <LabelPrintDuplicate xmlns="https://91.242.220.103/WebServicePwR">
      <PartnerID>{partner_id}</PartnerID>
      <PartnerKey>{partner_key}</PartnerKey>
      <PackCode>{pack_code}</PackCode>
    </LabelPrintDuplicate>
  </soap:Body>
</soap:Envelope>"""


# Funkcja do pobrania PackCode z GenerateLabelBusinessPack
# Zmodyfikowana funkcja do pobrania PackCode
def get_pack_code(partner_id, partner_key, url):
    """Pobiera PackCode_RUCH z odpowiedzi GenerateLabelBusinessPack"""
    soap_body = generate_label_business_pack_body(partner_id, partner_key)
    response = requests.post(url, data=soap_body, headers=HEADERS, verify=True)

    if response.status_code != 200:
        print(f"Treść odpowiedzi: {response.text}")
        raise Exception(f"Błąd żądania GenerateLabelBusinessPack: {response.status_code}\n{response.text}")

    print("Otrzymana odpowiedź SOAP:")  # Debug
    print(response.text)  # Debug

    # Parsowanie odpowiedzi
    try:
        root = ET.fromstring(response.text)

        # Rejestracja namespace - ważne!
        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'https://91.242.220.103/WebServicePwR'  # Główna przestrzeń nazw
        }

        # Szukamy w dwóch miejscach - raz z namespace, raz bez
        pack_code_element = root.find(".//PackCode_RUCH", namespaces=namespaces)
        if pack_code_element is None:
            pack_code_element = root.find(".//PackCode_RUCH")  # Próba bez namespace

        if pack_code_element is None:
            # Jeśli nadal nie znaleziono, sprawdź w Body/GenerateLabelBusinessPackResponse
            body = root.find(".//soap:Body", namespaces=namespaces)
            if body is not None:
                response_node = body.find(".//ns:GenerateLabelBusinessPackResponse", namespaces=namespaces)
                if response_node is not None:
                    pack_code_element = response_node.find(".//PackCode_RUCH")

        if pack_code_element is None or not pack_code_element.text:
            print("Pełna odpowiedź SOAP:")
            print(response.text)
            raise Exception("Nie znaleziono PackCode_RUCH w odpowiedzi. Struktura XML może być inna niż oczekiwano.")

        print(f"Znaleziono PackCode_RUCH: {pack_code_element.text}")
        return pack_code_element.text

    except ET.ParseError as e:
        print(f"Błąd parsowania XML: {e}")
        print("Odpowiedź serwera:")
        print(response.text)
        raise Exception("Nie można sparsować odpowiedzi XML")


# Funkcja get_label
def get_label(partner_id, partner_key, url):
    """Wysyła zapytanie SOAP i pobiera etykietę w formacie Base64."""
    try:
        # 1. Pobierz PackCode
        pack_code = get_pack_code(partner_id, partner_key, url)
        print(f"Pobrano PackCode: {pack_code}")

        # 2. Wygeneruj żądanie LabelPrintDuplicate
        soap_body = generate_soap_body(partner_id, partner_key, pack_code)

        # Debug: Wyświetl żądanie SOAP
        print("\nŻądanie SOAP do LabelPrintDuplicate:")
        print(soap_body)

        response = requests.post(url, data=soap_body, headers=HEADERS, verify=True)

        # Debug: Wyświetl odpowiedź
        print("\nOdpowiedź z LabelPrintDuplicate:")
        print(response.text)

        if response.status_code != 200:
            raise Exception(f"Błąd HTTP: {response.status_code}")

        xml_response = etree.fromstring(response.text.encode('utf-8'))
        get_element = xml_response.find(f'.//Label', {None: 'https://91.242.220.103/WebServicePwR'})
        return get_element.text if get_element is not None else None

    except Exception as e:
        print(f"\nBłąd w get_label: {str(e)}")
        raise


# Funkcja dekodująca Base64 i zapisująca PDF
def decode_and_save_pdf(base64_data, main_folder, method_folder_name, output_filename, url_name):
    """Dekoduje dane Base64 i zapisuje je jako plik PDF."""
    try:
        # Ścieżka do folderu "wygenerowane etykiety"
        generated_folder = os.path.join(main_folder, "wygenerowane etykiety")
        os.makedirs(generated_folder, exist_ok=True)
        print(f"Folder 'wygenerowane etykiety' został utworzony: {generated_folder}")

        # Ścieżka do folderu metody wewnątrz "wygenerowane etykiety"
        method_folder = os.path.join(generated_folder, method_folder_name)
        os.makedirs(method_folder, exist_ok=True)
        print(f"Folder metody '{method_folder_name}' został utworzony: {method_folder}")

        # Upewniamy się, że folder istnieje
        os.makedirs(method_folder, exist_ok=True)
        print(f"Folder docelowy: {method_folder}")

        # Pobranie aktualnej daty i godziny
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Tworzenie nowej nazwy pliku z datą i godziną
        filename, file_extension = os.path.splitext(output_filename)
        new_output_filename = f"{filename}__{url_name}__{current_time}{file_extension}"
        print(f"Nowa nazwa pliku: {new_output_filename}")

        # Pełna ścieżka do pliku PDF
        output_path = os.path.join(method_folder, new_output_filename)
        print(f"Pełna ścieżka do pliku: {output_path}")

        # Dekodowanie Base64 i zapis do pliku PDF
        pdf_data = base64.b64decode(base64_data)
        print(f"Długość danych PDF: {len(pdf_data)} bajtów")

        with open(output_path, "wb") as pdf_file:
            pdf_file.write(pdf_data)
            print(f"Plik PDF zapisany: {output_path}")

        # Otwórz plik PDF w przeglądarce
        # webbrowser.open(f'file://{os.path.abspath(output_path)}')
        # print(f"Etykieta zapisana: {output_path} i otwarta w przeglądarce.")
    except Exception as e:
        print(f"Błąd podczas zapisywania pliku PDF: {e}")
if __name__ == "__main__":

    method_folder_name = "LabelPrintDuplicate_PDF"
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
                label_base64 = get_label(partner_id, partner_key, url_value)
                # Zapisanie etykiety w folderze z nazwą metody
                decode_and_save_pdf(label_base64, OUTPUT_FOLDER, method_folder_name, PARTNER_FILE_NAMES[partner_id],
                                    url_name)
    except Exception as e:
        print(f"Wystąpił błąd: {e}")