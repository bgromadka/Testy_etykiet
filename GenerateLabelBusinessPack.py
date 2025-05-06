import requests
import base64
import os
import xml.etree.ElementTree as ET
import webbrowser
import datetime

from common_data import URL_DICT, OUTPUT_FOLDER

HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# Mapowanie partnerów na nazwy plików
PARTNER_FILE_NAMES = {
    "PWR0000006": "GenerateLabelBusinessPack__standard__PDF.pdf",
    "TEST000859": "GenerateLabelBusinessPack__meest__PDF.pdf",
    "TEST003483": "GenerateLabelBusinessPack__Vinted__PDF.pdf",
}

# Funkcja generująca XML dla danego PartnerID i PartnerKey
def generate_soap_body(partner_id, partner_key):
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

    if label_data is None or not label_data.text:
        print("Nie znaleziono danych etykiety w odpowiedzi SOAP.")
        print("Pełna odpowiedź SOAP:")
        print(response.text)
        raise Exception("Nie znaleziono danych etykiety w odpowiedzi SOAP.")

    print(f"Znaleziono dane etykiety dla partnera {partner_id}.")
    return label_data.text


# Funkcja dekodująca Base64 i zapisująca PDF w określonym folderze
def decode_and_save_pdf(base64_data, folder_path, output_filename, url_name):
    """Dekoduje dane Base64 i zapisuje je jako plik PDF w określonym folderze z datą i godziną w nazwie pliku."""
    try:
        # Upewniamy się, że folder istnieje
        os.makedirs(folder_path, exist_ok=True)
        print(f"Folder docelowy: {folder_path}")

        # Pobranie aktualnej daty i godziny
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Tworzenie nowej nazwy pliku z datą i godziną
        filename, file_extension = os.path.splitext(output_filename)
        new_output_filename = f"{filename}__{url_name}__{current_time}{file_extension}"
        print(f"Nowa nazwa pliku: {new_output_filename}")

        # Pełna ścieżka do pliku PDF
        output_path = os.path.join(folder_path, new_output_filename)
        print(f"Pełna ścieżka do pliku: {output_path}")

        # Dekodowanie Base64 i zapis do pliku PDF
        pdf_data = base64.b64decode(base64_data)
        print(f"Długość danych PDF: {len(pdf_data)} bajtów")

        with open(output_path, "wb") as pdf_file:
            pdf_file.write(pdf_data)
            print(f"Plik PDF zapisany: {output_path}")

        # # Otwórz plik PDF w przeglądarce
        # webbrowser.open(f'file://{os.path.abspath(output_path)}')
        # print(f"Etykieta zapisana: {output_path} i otwarta w przeglądarce.")
    except Exception as e:
        print(f"Błąd podczas zapisywania pliku PDF: {e}")


if __name__ == "__main__":
    # Ścieżka do folderu "wygenerowane etykiety"
    generated_folder = os.path.join(OUTPUT_FOLDER, "wygenerowane etykiety")
    os.makedirs(generated_folder, exist_ok=True)
    print(f"Folder 'wygenerowane etykiety' został utworzony: {generated_folder}")

    # Nazwa folderu metody (np. nazwa skryptu lub funkcji)
    method_folder_name = "GenerateLabelBusinessPack"

    # Ścieżka do folderu metody wewnątrz "wygenerowane etykiety"
    method_folder = os.path.join(generated_folder, method_folder_name)
    os.makedirs(method_folder, exist_ok=True)
    print(f"Folder metody '{method_folder_name}' został utworzony: {method_folder}")

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

                # Zapisanie etykiety w folderze metody wewnątrz "wygenerowane etykiety"
                decode_and_save_pdf(label_base64, method_folder, PARTNER_FILE_NAMES[partner_id], url_name)

    except Exception as e:
        print(f"Wystąpił błąd: {e}")