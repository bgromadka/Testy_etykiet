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
from common_data import URL_DICT, OUTPUT_FOLDER
HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# Mapowanie partnerów na nazwy plików
PARTNER_FILE_NAMES = {
    "PWR0000006": "LabelPrintDuplicateTwo_standard_ZPL.zpl",
    "TEST000859": "LabelPrintDuplicateTwo_meest_ZPL.zpl",
    "TEST003483": "LabelPrintDuplicateTwo_Vinted_ZPL.zpl",
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
    """Generuje XML dla żądania LabelPrintDuplicateListTwo"""
    pack_code_list = "\n".join([f"<string>{code}</string>" for code in pack_codes])

    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <LabelPrintDuplicateListTwo xmlns="https://91.242.220.103/WebServicePwR">
      <PartnerID>{partner_id}</PartnerID>
      <PartnerKey>{partner_key}</PartnerKey>
      <Format>ZPL</Format>
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


# Funkcja wysyłająca zapytanie SOAP i pobierająca etykietę
def get_label(partner_id, partner_key, url):
    """Wysyła zapytanie SOAP i pobiera etykietę w formacie Base64."""
    try:
        # 1. Pobierz dwa kody paczek (możesz zmienić na get_three_pack_codes jeśli potrzebujesz 3)
        pack_codes = get_two_pack_codes(partner_id, partner_key, url)
        print(f"Użyte kody paczek: {pack_codes}")

        # 2. Generuj żądanie z listą kodów
        soap_body = generate_soap_body(partner_id, partner_key, pack_codes)

        # 3. Wyślij żądanie
        response = requests.post(url, data=soap_body, headers=HEADERS, verify=True)

        if response.status_code != 200:
            print(f"Treść odpowiedzi: {response.text}")
            raise Exception(f"Błąd żądania: {response.status_code}\n{response.text}")

        # 4. Parsowanie odpowiedzi
        root = ET.fromstring(response.text)
        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            '': 'https://91.242.220.103/WebServicePwR'
        }

        # Szukamy etykiety (może być Label lub LabelData w zależności od API)
        label = root.find(".//Label", namespaces=namespaces) or root.find(".//LabelData", namespaces=namespaces)

        if label is None or not label.text:
            raise Exception("Nie znaleziono danych etykiety w odpowiedzi SOAP.")

        return label.text

    except Exception as e:
        print(f"Błąd w get_label: {str(e)}")
        raise

# Funkcja dekodująca Base64 i zapisująca ZPL
def decode_and_save_zpl(base64_data, main_folder, method_folder_name, output_filename, url_name):
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

# Funkcja do otwierania strony i przesyłania pliku
# def open_zpl_printer_website_and_upload_file(driver, file_path):
#     try:
#         # Otwórz nową kartę
#         driver.execute_script("window.open('');")
#         driver.switch_to.window(driver.window_handles[-1])  # Przełącz się na nową kartę
#
#         # Przejdź do strony ZPL Printer
#         driver.get("https://labelary.com/viewer.html")
#         print("Strona ZPL Printer została otwarta w nowej karcie.")
#
#         # Wczytanie zawartości pliku ZPL
#         with open(file_path, "r", encoding="utf-8") as file:
#             zpl_data = file.read()
#         print("Zawartość pliku ZPL została wczytana.")
#
#         # Poczekaj, aż pole tekstowe będzie widoczne
#         text_area = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "zpl")))
#
#         # Wklejenie danych do pola tekstowego
#         text_area.clear()
#         text_area.send_keys(zpl_data)
#         print("Dane ZPL zostały wklejone do pola tekstowego.")
#
#         # Znalezienie przycisku "Redraw ZPL" i kliknięcie
#         wait = WebDriverWait(driver, 5)
#         submit_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn btn-default")))
#         driver.execute_script("arguments[0].scrollIntoView();", submit_button)
#         time.sleep(1)  # Czekamy chwilę po przewinięciu
#         driver.execute_script("arguments[0].click();", submit_button)
#         print("Przycisk 'Redraw ZPL' został kliknięty.")
#
#     except Exception as e:
#         print(f"Błąd: {e}")

# Główna część programu
if __name__ == "__main__":


    # Nazwa folderu metody (np. nazwa skryptu lub funkcji)
    method_folder_name = "LabelPrintDuplicateTwo_ZPL"

    # Lista partnerów (PartnerID, PartnerKey)
    partners = [
        ("PWR0000006", "1234"),
        ("TEST000859", "SMS8IKIF3A"),
        ("TEST003483", "F2E087C0B9"),


    ]

    print("Pobieranie etykiet...")

    try:
        # Inicjalizacja przeglądarki Chrome
        # chrome_options = Options()
        # chrome_options.add_argument("--start-maximized")
        # chrome_options.add_experimental_option("detach", True)
        # service = Service(ChromeDriverManager().install())
        # driver = webdriver.Chrome(service=service, options=chrome_options)
        #
        # for partner_id, partner_key in partners:
        #     print(f"Generowanie etykiety dla {partner_id}...")
        #     label_base64 = get_label(partner_id, partner_key)
        #     output_filename = PARTNER_FILE_NAMES[partner_id]  # Pobierz nazwę pliku dla danego partnera
        #     new_output_filename = decode_and_save_zpl(label_base64, main_folder, method_folder_name, output_filename)
        #
        #     if new_output_filename:  # Sprawdź, czy plik został poprawnie zapisany
        #         # Otwórz stronę ZPL Printer i prześlij plik w nowej karcie
        #         file_path = os.path.join(main_folder, "wygenerowane etykiety", method_folder_name, new_output_filename)
        #         if os.path.exists(file_path):  # Sprawdź, czy plik istnieje
        #             open_zpl_printer_website_and_upload_file(driver, file_path)
        #         else:
        #             print(f"Plik {file_path} nie istnieje.")
        #
        # print("Wszystkie etykiety zostały przetworzone. Przeglądarka pozostaje otwarta.")
        for url_name, url_value in URL_DICT.items():
            for partner_id, partner_key in partners:
                print(f"Generowanie etykiety dla partnera {partner_id}...")
                label_base64 = get_label(partner_id, partner_key, url_value)
                decode_and_save_zpl(label_base64, OUTPUT_FOLDER, method_folder_name, PARTNER_FILE_NAMES[partner_id],
                                    url_name)

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
