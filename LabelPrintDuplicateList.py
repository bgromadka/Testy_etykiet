import requests
import base64
import os
import xml.etree.ElementTree as ET
import webbrowser
import datetime
import threading
import shutil
# Konfiguracja
from common_data import URL_DICT, OUTPUT_FOLDER, MISSING_LABEL_FILE
HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# Mapowanie partnerów na nazwy plików
PARTNER_FILE_NAMES = {
    "PWR0000006": "LabelPrintDuplicateList_standard_PDF.pdf",
    "TEST000859": "LabelPrintDuplicateList_meest_PDF.pdf",
    "TEST003483": "LabelPrintDuplicateList_Vinted_PDF.pdf",
}


# Funkcja generująca XML dla GenerateLabelBusinessPack
def generate_label_business_pack_body(partner_id, partner_key, url):
    """Generuje XML dla żądania GenerateLabelBusinessPack"""
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


def generate_soap_body(partner_id, partner_key, pack_codes):
    """Generuje XML dla żądania LabelPrintDuplicateList z listą kodów paczek"""
    pack_code_list = "\n".join([f"<string>{code}</string>" for code in pack_codes])

    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
     <LabelPrintDuplicateList xmlns="https://91.242.220.103/WebServicePwR">
      <PartnerID>{partner_id}</PartnerID>
      <PartnerKey>{partner_key}</PartnerKey>
      <Format>PDF</Format>
      <PackCodeList>
        {pack_code_list}
      </PackCodeList>
    </LabelPrintDuplicateList>
  </soap:Body>
</soap:Envelope>"""


def get_single_pack_code(partner_id, partner_key, url):
    """Wywołuje GenerateLabelBusinessPack i zwraca PackCode_RUCH"""
    soap_body = generate_label_business_pack_body(partner_id, partner_key, url)
    response = requests.post(url, data=soap_body, headers=HEADERS, verify=True)

    if response.status_code != 200:
        print(f"Treść odpowiedzi: {response.text}")
        raise Exception(f"Błąd żądania: {response.status_code}")

    # Debug: zapisz odpowiedź do pliku
    with open("last_response.xml", "w", encoding="utf-8") as f:
        f.write(response.text)

    # Uproszczone parsowanie - usuwamy problem z namespace
    try:
        # Metoda 1: Usuń namespace dla prostszego parsowania
        clean_xml = response.text.replace('xmlns="https://91.242.220.103/WebServicePwR"', '')
        root = ET.fromstring(clean_xml)

        # Metoda 2: Wyszukaj bezpośrednio w tekście
        start_tag = "<PackCode_RUCH>"
        end_tag = "</PackCode_RUCH>"
        if start_tag in response.text:
            start = response.text.index(start_tag) + len(start_tag)
            end = response.text.index(end_tag)
            return response.text[start:end]

        # Metoda 3: Przeszukaj całe drzewo
        for elem in root.iter():
            if "PackCode_RUCH" in elem.tag:
                return elem.text

    except Exception as e:
        print(f"Błąd parsowania: {e}")

    print("\nNie znaleziono PackCode_RUCH. Pełna odpowiedź:")
    print(response.text)
    raise Exception("PackCode_RUCH nie znaleziony w odpowiedzi. Zobacz last_response.xml")


def get_two_pack_codes(partner_id, partner_key, url):
    """Pobiera dwa różne kody paczek poprzez dwukrotne wywołanie GenerateLabelBusinessPack"""
    print("Pobieranie pierwszego kodu paczki...")
    pack_code1 = get_single_pack_code(partner_id, partner_key, url)

    print("Pobieranie drugiego kodu paczki...")
    pack_code2 = get_single_pack_code(partner_id, partner_key, url)



    # Upewniamy się, że kody są różne
    while pack_code2 == pack_code1:
        print("Kody paczek są identyczne, ponawiam próbę...")
        pack_code2 = get_single_pack_code(partner_id, partner_key, url)

    return [pack_code1, pack_code2]


def get_label(partner_id, partner_key, url):
    """Wysyła zapytanie SOAP i pobiera etykietę w formacie Base64."""
    try:
        # 1. Pobierz dwa różne kody paczek
        pack_codes = get_two_pack_codes(partner_id, partner_key, url)
        print(f"Pobrano kody paczek: {pack_codes}")

        # 2. Wygeneruj żądanie LabelPrintDuplicateList
        soap_body = generate_soap_body(partner_id, partner_key, pack_codes)

        print("\nŻądanie SOAP do LabelPrintDuplicateList:")
        print(soap_body)

        response = requests.post(url, data=soap_body, headers=HEADERS, verify=True)

        print("\nOdpowiedź z LabelPrintDuplicateList:")
        print(response.text)

        if response.status_code != 200:
            raise Exception(f"Błąd HTTP: {response.status_code}")
        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            '': 'https://91.242.220.103/WebServicePwR'  # Default namespace, musimy go uwzględnić
        }
        # 3. Parsowanie odpowiedzi
        root = ET.fromstring(response.text)
        label_data = root.find(".//LabelData", namespaces=namespaces)



        # pack_codes = root.findall(".//PackCode_RUCH", namespaces=None)
        result_pack_code = '__'.join(pack_codes)

        return label_data.text if label_data is not None else None, result_pack_code
    except Exception as e:

        raise Exception(f"Błąd podczas pobierania label lub pack_Code: {e}")

# Funkcja dekodująca Base64 i zapisująca PDF
def decode_and_save_pdf(base64_data, pack_code, main_folder, method_folder_name, output_filename, url_name):
    """Dekoduje dane Base64 i zapisuje je jako plik PDF."""
    try:


        # Ścieżka do folderu metody wewnątrz "wygenerowane etykiety"
        method_folder = os.path.join(main_folder, method_folder_name)
        os.makedirs(method_folder, exist_ok=True)
        print(f"Folder metody '{method_folder_name}' został utworzony: {method_folder}")
        os.makedirs(method_folder, exist_ok=True)
        print(f"Folder docelowy: {method_folder}")
        # Pobranie aktualnej daty i godziny
        current_time = datetime.datetime.now().strftime("%Y-%m-%d")

        # Tworzenie nowej nazwy pliku z datą i godziną
        filename, file_extension = os.path.splitext(output_filename)
        new_output_filename = f"{filename}__{url_name}__{pack_code}__{current_time}{file_extension}"
        print(f"Nowa nazwa pliku: {new_output_filename}")
        output_path = os.path.join(method_folder, new_output_filename)
        print(f"Pełna ścieżka do pliku: {output_path}")
        print(f"Plik PDF zapisany: {output_path}")

        pdf_data = base64.b64decode(base64_data)
        print(f"Długość danych PDF: {len(pdf_data)} bajtów")
        if base64_data is None:
            shutil.copy(MISSING_LABEL_FILE, output_path)

        else:
            pdf_data = base64.b64decode(base64_data)
            print(f"Długość danych PDF: {len(pdf_data)} bajtów")

            with open(output_path, "wb") as pdf_file:
                pdf_file.write(pdf_data)
                print(f"Plik PDF zapisany: {output_path}")

        #webbrowser.open(f'file://{os.path.abspath(output_path)}')
        #print(f"Etykieta zapisana: {output_path} i otwarta w przeglądarce.")
    except Exception as e:
        print(f"Błąd podczas zapisywania pliku PDF: {e}")
        raise Exception(f"Błąd podczas zapisywania pliku PDF: {e}")

if __name__ == "__main__":


    # Nazwa folderu metody
    method_folder_name = "LabelPrintDuplicateList_PDF"



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
                decode_and_save_pdf(response_data[0], response_data[1], OUTPUT_FOLDER, method_folder_name,
                                    PARTNER_FILE_NAMES[partner_id], url_name)
    except Exception as e:
        print(f"Wystąpił ogólny błąd: {e}")