import requests
import base64
import os
import xml.etree.ElementTree as ET
import webbrowser
import datetime

# Konfiguracja
SOAP_URL = "https://api-test.orlenpaczka.pl/WebServicePwR/WebServicePwR.asmx"
HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# Funkcja generująca XML dla danego PartnerID i PartnerKey
def generate_soap_body(partner_id, partner_key):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
   <soap:Body>
   <GenerateStandardCustomerReturn xmlns="https://91.242.220.103/WebServicePwR">
----------------------------------------------------------Generowanie listu przewozowego z etykieta
       <PartnerID>{partner_id}</PartnerID>
      <PartnerKey>{partner_key}</PartnerKey>


     <PrintLabel>T</PrintLabel>
      <Format>PDF</Format>

      <BoxSize>S</BoxSize>
      <PrintType>1</PrintType>

      <Insurance>T</Insurance>
    <PackValue>500</PackValue>
      ----------------------------------------------------------Nadawca - odbiorca
      <SenderFirstName>SenderFirstName</SenderFirstName>
      <SenderLastName>SenderLastName</SenderLastName>
      <SenderCompanyName>SenderCompanyName</SenderCompanyName>
      <SenderStreetName>SenderStreetName</SenderStreetName>
      <SenderBuildingNumber>1</SenderBuildingNumber>
      <SenderFlatNumber>1</SenderFlatNumber>
      <SenderCity>SenderCity</SenderCity>
      <SenderPostCode>04347</SenderPostCode>
      <SenderEMail>SenderMailAdress@ruch.com.pl</SenderEMail>
      <SenderPhoneNumber>123456789</SenderPhoneNumber>
      <SenderOrders>SenderOrders</SenderOrders>

      <ExternalSenderPackageNumber></ExternalSenderPackageNumber>
      <ExternalPackageNumber></ExternalPackageNumber>
----------------------------------------------------------Nadawca - odbiorca
    </GenerateStandardCustomerReturn>
  </soap:Body>
</soap:Envelope>"""

# Funkcja wysyłająca zapytanie SOAP i pobierająca etykietę
def get_label(partner_id, partner_key):
    """Wysyła zapytanie SOAP i pobiera etykietę w formacie Base64."""
    soap_body = generate_soap_body(partner_id, partner_key)

    response = requests.post(SOAP_URL, data=soap_body, headers=HEADERS, verify=True)

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

    # Sprawdzanie, czy <Label> znajduje się w odpowiedzi
    label = root.find(".//Label", namespaces=namespaces)

    if label is None or not label.text:
        raise Exception("Nie znaleziono danych etykiety w odpowiedzi SOAP.")

    # Zwracamy zakodowaną etykietę
    return label.text

# Funkcja dekodująca Base64 i zapisująca PDF w określonym folderze
def decode_and_save_pdf(base64_data, main_folder, method_folder_name, output_filename):
    """Dekoduje dane Base64 i zapisuje je jako plik PDF w określonym folderze z datą i godziną w nazwie pliku."""
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
        new_output_filename = f"{filename}_{current_time}{file_extension}"
        print(f"Nowa nazwa pliku: {new_output_filename}")

        # Pełna ścieżka do pliku PDF
        output_path = os.path.join(method_folder, new_output_filename)
        print(f"Pełna ścieżka do pliku: {output_path}")

        # Dekodowanie Base64 i zapis do pliku PDF
        with open(output_path, "wb") as pdf_file:
            pdf_file.write(base64.b64decode(base64_data))
            print(f"Plik PDF zapisany: {output_path}")

        # Otwórz plik PDF w przeglądarce
        webbrowser.open(f'file://{os.path.abspath(output_path)}')
        print(f"Etykieta zapisana: {output_path} i otwarta w przeglądarce.")
    except Exception as e:
        raise Exception(f"Błąd podczas zapisywania pliku PDF: {e}")

if __name__ == "__main__":
    # Ścieżka do folderu głównego
    main_folder = r"C:\Users\bgromadka\Desktop\generowanie etykiet- dokumentacja\Etykiety"

    # Nazwa folderu metody (np. nazwa skryptu lub funkcji)
    method_folder_name = "label_GenerateStandardCustomerReturn_PDF_PDF"

    # Lista partnerów (PartnerID, PartnerKey)
    partners = [
        ("PWRTR50301", "PWRTR50301"),


        #("TEST000859", "SMS8IKIF3A"),
        #("TEST003483", "F2E087C0B9"),
        #("TEST002922", "57FE54AF8E"),
        #("TEST000129", "TTFWWSCSVO"),
        #("TEST000015", "GTTFM5HEOP")


       # ("TEST000129", "TTFWWSCSVO"),


    ]

    print("Pobieranie etykiet...")

    try:
        # Generowanie etykiety dla każdego partnera
        for partner_id, partner_key in partners:
            print(f"Generowanie etykiety dla partnera {partner_id}...")
            label_base64 = get_label(partner_id, partner_key)
            output_filename = f"label_{partner_id}.pdf"
            decode_and_save_pdf(label_base64, main_folder, method_folder_name, output_filename)

    except Exception as e:
        print(f"Wystąpił błąd: {e}")