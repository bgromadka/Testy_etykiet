import requests
import base64
import os
import xml.etree.ElementTree as ET
import webbrowser
import datetime
import threading

# Konfiguracja
from common_data import URL_DICT, OUTPUT_FOLDER
HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# Mapowanie partnerów na nazwy plików
PARTNER_FILE_NAMES = {
    "PWR0000006": "LabelPrintDuplicateTwo_standard_PDF10.pdf",
    "TEST000859": "LabelPrintDuplicateTwo_meest_PDF10.pdf",
    "TEST003483": "LabelPrintDuplicateTwo_Vinted_PDF10.pdf",
}


# Funkcja generująca XML dla GenerateLabelBusinessPack
def generate_label_business_pack_body(partner_id, partner_key):
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
    """Generuje poprawne żądanie XML dla LabelPrintDuplicateListTwo"""
    pack_code_list = "\n".join([f"<string>{code}</string>" for code in pack_codes])

    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <LabelPrintDuplicateListTwo xmlns="https://91.242.220.103/WebServicePwR">
      <PartnerID>{partner_id}</PartnerID>
      <PartnerKey>{partner_key}</PartnerKey>
      <Format>PDF10</Format>
      <PackCodeList>
        {pack_code_list}
      </PackCodeList>
    </LabelPrintDuplicateListTwo>
  </soap:Body>
</soap:Envelope>"""


def get_label(partner_id, partner_key, url):
    """Wysyła poprawne żądanie SOAP i obsługuje odpowiedź"""
    try:
        # 1. Pobierz kody paczek (zmień na 1 jeśli API nie akceptuje wielu)
        pack_codes = [get_single_pack_code(partner_id, partner_key)]

        # 2. Generuj żądanie
        soap_body = generate_soap_body(partner_id, partner_key, pack_codes)

        # Debug: Zapisz żądanie do pliku
        with open("last_request.xml", "w", encoding="utf-8") as f:
            f.write(soap_body)

        # 3. Wyślij żądanie z poprawnymi nagłówkami
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": '"https://91.242.220.103/WebServicePwR/LabelPrintDuplicateListTwo"'
        }

        response = requests.post(url, data=soap_body, headers=HEADERS, verify=True)

        # Debug: Zapisz odpowiedź
        with open("last_response.xml", "w", encoding="utf-8") as f:
            f.write(response.text)

        # 4. Analiza odpowiedzi
        if response.status_code == 400:
            print("\nSzczegóły błędu 400:")
            print(response.text)
            raise Exception(f"Błąd 400 - Nieprawidłowe żądanie. Sprawdź last_request.xml")

        if response.status_code != 200:
            raise Exception(f"Błąd HTTP {response.status_code}")

        # Parsowanie odpowiedzi
        try:
            root = ET.fromstring(response.text)
            label = root.find(".//{https://91.242.220.103/WebServicePwR}Label") or \
                    root.find(".//Label")

            if label is not None and label.text:
                return label.text

            raise Exception("Odpowiedź nie zawiera danych etykiety")

        except ET.ParseError:
            # Jeśli parsowanie XML zawiedzie, spróbuj znaleźć base64 w tekście
            import re
            match = re.search(r'<Label>(.*?)</Label>', response.text)
            if match:
                return match.group(1)
            raise Exception("Nie można znaleźć danych etykiety w odpowiedzi")

    except Exception as e:
        print(f"\nBłąd podczas przetwarzania partnera {partner_id}:")
        print(f"Typ błędu: {type(e).__name__}")
        print(f"Komunikat: {str(e)}")
        if 'last_request.xml' in os.listdir():
            print("Sprawdź plik last_request.xml i last_response.xml")
        raise


def get_single_pack_code(partner_id, partner_key, url):
    """Wywołuje GenerateLabelBusinessPack i zwraca pojedynczy PackCode_RUCH"""
    try:
        # Generuj żądanie
        soap_body = generate_label_business_pack_body(partner_id, partner_key)

        # Wyślij żądanie
        response = requests.post(url, data=soap_body, headers=HEADERS, verify=True)

        if response.status_code != 200:
            print(f"Treść odpowiedzi: {response.text}")
            raise Exception(f"Błąd żądania: {response.status_code}")

        # Parsowanie odpowiedzi - prosta wersja bez XPath
        start_tag = "<PackCode_RUCH>"
        end_tag = "</PackCode_RUCH>"
        response_text = response.text

        if start_tag in response_text and end_tag in response_text:
            start = response_text.index(start_tag) + len(start_tag)
            end = response_text.index(end_tag)
            return response_text[start:end]

        raise Exception("Nie znaleziono PackCode_RUCH w odpowiedzi")

    except Exception as e:
        print(f"Błąd w get_single_pack_code: {str(e)}")
        raise
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

        print("\nŻądanie SOAP do LabelPrintDuplicateListTwo:")
        print(soap_body)

        response = requests.post(url, data=soap_body, headers=HEADERS, verify=True)

        print("\nOdpowiedź z LabelPrintDuplicateListTwo:")
        print(response.text)

        if response.status_code != 200:
            raise Exception(f"Błąd HTTP: {response.status_code}")

        # 3. Parsowanie odpowiedzi
        root = ET.fromstring(response.text)
        label_data = None

        # Szukamy LabelData w różnych możliwych lokalizacjach
        for elem in root.iter():
            if 'LabelData' in elem.tag and elem.text:
                label_data = elem.text
                break

        if not label_data:
            # Alternatywnie: próba znalezienia base64 w odpowiedzi
            import re
            base64_pattern = r'([A-Za-z0-9+/]{50,}={0,2})'
            matches = re.findall(base64_pattern, response.text)
            if matches:
                label_data = max(matches, key=len)

        if not label_data:
            raise Exception("Nie znaleziono danych etykiety w odpowiedzi")

        return label_data

    except Exception as e:
        print(f"\nBłąd w get_label: {str(e)}")
        raise

# Funkcja dekodująca Base64 i zapisująca PDF
def decode_and_save_pdf10(base64_data, main_folder, method_folder_name, output_filename, url_name):
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
        os.makedirs(method_folder, exist_ok=True)
        print(f"Folder docelowy: {method_folder}")
        # Pobranie aktualnej daty i godziny
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Tworzenie nowej nazwy pliku z datą i godziną
        filename, file_extension = os.path.splitext(output_filename)
        new_output_filename = f"{filename}__{url_name}__{current_time}{file_extension}"
        print(f"Nowa nazwa pliku: {new_output_filename}")
        output_path = os.path.join(method_folder, new_output_filename)
        print(f"Pełna ścieżka do pliku: {output_path}")
        print(f"Plik PDF zapisany: {output_path}")

        pdf_data = base64.b64decode(base64_data)
        print(f"Długość danych PDF: {len(pdf_data)} bajtów")
        with open(output_path, "wb") as pdf_file:
            pdf_file.write(pdf_data)
            print(f"Plik PDF zapisany: {output_path}")

        # webbrowser.open(f'file://{os.path.abspath(output_path)}')
        # print(f"Etykieta zapisana: {output_path} i otwarta w przeglądarce.")
    except Exception as e:
        print(f"Błąd podczas zapisywania pliku PDF: {e}")

if __name__ == "__main__":
    # Nazwa folderu metody
    method_folder_name = "LabelPrintDuplicateTwo_PDF10"

    # Lista partnerów (PartnerID, PartnerKey)
    partners = [
        ("PWR0000006", "1234"),
        ("TEST000859", "SMS8IKIF3A"),
        ("TEST003483", "F2E087C0B9"),

    ]
    try:
        for url_name, url_value in URL_DICT.items():
            for partner_id, partner_key in partners:
                print(f"Generowanie etykiety dla partnera {partner_id}...")
                label_base64 = get_label(partner_id, partner_key, url_value)
                decode_and_save_pdf10(label_base64, OUTPUT_FOLDER, method_folder_name, PARTNER_FILE_NAMES[partner_id],
                                      url_name)

    except Exception as e:
        print(f"Wystąpił ogólny błąd: {e}")