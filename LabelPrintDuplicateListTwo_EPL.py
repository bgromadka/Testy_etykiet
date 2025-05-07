import requests
import base64
import os
import xml.etree.ElementTree as ET
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime

# Konfiguracja
from common_data import OUTPUT_FOLDER, URL_DICT
HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# Mapowanie partnerów na nazwy plików
PARTNER_FILE_NAMES = {
    "PWR0000006": "LabelPrintDuplicateListTwo_standard_EPL.pdf",
    "TEST000859": "LabelPrintDuplicateListTwo_meest_EPL.pdf",
    "TEST003483": "LabelPrintDuplicateListTwo_Vinted_EPL.pdf",

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
      <DestinationCode>WS-100001</DestinationCode>
      <SenderOrders>referencja-/</SenderOrders>
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
      <CashOnDelivery>F</CashOnDelivery>
      <AmountCashOnDelivery>1234</AmountCashOnDelivery>
      <TransferDescription>opis transakcji</TransferDescription>
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
    </GenerateLabelBusinessPack>
  </soap:Body>
</soap:Envelope>"""


def generate_soap_body(partner_id, partner_key, pack_codes):
    """Generuje XML dla żądania LabelPrintDuplicateListTwo z listą kodów paczek"""
    pack_code_list = "\n".join([f"<string>{code}</string>" for code in pack_codes])

    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
     <LabelPrintDuplicateListTwo xmlns="https://91.242.220.103/WebServicePwR">
      <PartnerID>{partner_id}</PartnerID>
      <PartnerKey>{partner_key}</PartnerKey>
      <Format>EPL</Format>
      <PackCodeList>
        {pack_code_list}
      </PackCodeList>
   </LabelPrintDuplicateListTwo>
  </soap:Body>
</soap:Envelope>"""


def get_single_pack_code(partner_id, partner_key, url):
    """Wywołuje GenerateLabelBusinessPack i zwraca PackCode_RUCH"""
    soap_body = generate_label_business_pack_body(partner_id, partner_key)
    response = requests.post(url, data=soap_body, headers=HEADERS, verify=True)

    if response.status_code != 200:
        print(f"Treść odpowiedzi: {response.text}")
        raise Exception(f"Błąd żądania: {response.status_code}")

    # Uproszczone parsowanie
    try:
        start_tag = "<PackCode_RUCH>"
        end_tag = "</PackCode_RUCH>"
        if start_tag in response.text:
            start = response.text.index(start_tag) + len(start_tag)
            end = response.text.index(end_tag)
            return response.text[start:end]
    except Exception as e:
        print(f"Błąd parsowania: {e}")

    raise Exception("PackCode_RUCH nie znaleziony w odpowiedzi")


def get_label(partner_id, partner_key, url):
    """Wysyła zapytanie SOAP i pobiera etykietę w formacie Base64."""
    try:
        # 1. Pobierz trzy kody paczek
        pack_codes = [get_single_pack_code(partner_id, partner_key, url) for _ in range(3)]
        print(f"Użyte kody paczek: {pack_codes}")

        # 2. Generuj żądanie
        soap_body = generate_soap_body(partner_id, partner_key, pack_codes)

        # Debug: Wyświetl żądanie SOAP
        print("\nŻądanie SOAP do LabelPrintDuplicateListTwo:")
        print(soap_body)

        response = requests.post(url, data=soap_body, headers=HEADERS, verify=True)

        # Debug: Wyświetl odpowiedź
        print("\nOdpowiedź z LabelPrintDuplicateListTwo:")
        print(response.text)

        if response.status_code != 200:
            raise Exception(f"Błąd HTTP: {response.status_code}")

        # 3. Uproszczone parsowanie odpowiedzi - bez XPath
        root = ET.fromstring(response.text)

        # Przeszukaj całe drzewo XML w poszukiwaniu etykiety
        label_data = None
        for elem in root.iter():
            if 'Label' in elem.tag or 'LabelData' in elem.tag:
                if elem.text and elem.text.strip():
                    label_data = elem.text
                    break

        # Alternatywnie: próba znalezienia tekstu base64
        if not label_data:
            import re
            base64_pattern = r'([A-Za-z0-9+/]{30,}={0,2})'
            matches = re.findall(base64_pattern, response.text)
            if matches:
                label_data = max(matches, key=len)  # Zwróć najdłuższy ciąg Base64

        if not label_data:
            print("\nNie znaleziono LabelData. Dostępne elementy w odpowiedzi:")
            for elem in root.iter():
                print(f"Element: {elem.tag}, Wartość: {elem.text}")
            raise Exception("Nie znaleziono danych etykiety w odpowiedzi")

        return label_data

    except ET.ParseError as e:
        print(f"\nBłąd parsowania XML: {e}")
        print("Odpowiedź serwera:")
        print(response.text)
        raise Exception("Nie można sparsować odpowiedzi XML")
    except Exception as e:
        print(f"\nBłąd w get_label: {str(e)}")
        raise


def decode_and_save_EPL(base64_data, main_folder, method_folder_name, output_filename, url_name):
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

        #webbrowser.open(f'file://{os.path.abspath(output_path)}')
        #print(f"Etykieta zapisana: {output_path} i otwarta w przeglądarce.")
    except Exception as e:
        print(f"Błąd podczas zapisywania pliku PDF: {e}")



#def open_epl_printer_website(driver, file_path):
 #   """Otwiera stronę eplprinter i ładuje plik"""
  #  try:
   #     driver.execute_script("window.open('');")
    #    driver.switch_to.window(driver.window_handles[-1])
     #   driver.get("https://eplprinter.azurewebsites.net/")

        # Zaznacz UTF-8
      #  WebDriverWait(driver, 10).until(
       #     EC.presence_of_element_located((By.ID, "chkUTF8"))).click()

        # Wczytaj zawartość pliku
        #with open(file_path, "r") as f:
         #   content = f.read()

        # Wklej do formularza
        #textarea = WebDriverWait(driver, 10).until(
         #   EC.presence_of_element_located((By.ID, "eplCommands")))
        #textarea.clear()
        #textarea.send_keys(content)

        # Kliknij przycisk
        #WebDriverWait(driver, 10).until(
         #   EC.element_to_be_clickable((By.CLASS_NAME, "btn-danger"))).click()

    #except Exception as e:
     #   print(f"Błąd przeglądarki: {e}")


if __name__ == "__main__":

    method_folder_name = "LabelPrintDuplicateListTwo_EPL"
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
            # output_filename = PARTNER_FILE_NAMES[partner_id]
                decode_and_save_EPL(label_base64, OUTPUT_FOLDER, method_folder_name, PARTNER_FILE_NAMES[partner_id],
                                    url_name)
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
