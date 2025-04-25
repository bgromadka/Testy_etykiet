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
SOAP_URL = "http://bruchorpact03/WebServicePwRKube/WebServicePwR.asmx"
HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# Mapowanie partnerów na nazwy plików
PARTNER_FILE_NAMES = {
    "PWRTR50301": "label_allegro_GenerateStandardCustomerReturn_ZPL.zpl",

    "TEST000129": "label_Packeta_GenerateStandardCustomerReturn_ZPL.zpl",




}


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
      <Format>ZPL</Format>

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

# Funkcja dekodująca Base64 i zapisująca ZPL
def decode_and_save_zpl(base64_data, main_folder, method_folder_name, output_filename):
    """Dekoduje dane Base64 i zapisuje je jako plik ZPL w określonym folderze z datą i godziną w nazwie pliku."""
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

        # Dekodowanie Base64
        ZPL_data = base64.b64decode(base64_data)

        # Pobranie aktualnej daty i godziny
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Tworzenie nowej nazwy pliku z datą i godziną
        filename, file_extension = os.path.splitext(output_filename)
        new_output_filename = f"{filename}_{current_time}{file_extension}"
        print(f"Nowa nazwa pliku: {new_output_filename}")

        # Pełna ścieżka do pliku ZPL
        output_path = os.path.join(method_folder, new_output_filename)
        print(f"Pełna ścieżka do pliku: {output_path}")

        # Zapisz dane ZPL do pliku
        with open(output_path, "wb") as ZPL_file:
            ZPL_file.write(ZPL_data)

        # Uruchomienie Notepad++ w tle
        notepad_plus_plus_path = r"C:\Program Files\Notepad++\notepad++.exe"  # Ścieżka do Notepad++
        if os.path.exists(notepad_plus_plus_path):
            subprocess.Popen([notepad_plus_plus_path, output_path])
        else:
            print("Nie znaleziono Notepad++ w domyślnej lokalizacji. Upewnij się, że jest zainstalowany.")

        print(f"Etykieta została zapisana jako ZPL w folderze {method_folder}: {new_output_filename} i otwarta w Notepad++.")

        # Zwróć nową nazwę pliku
        return new_output_filename
    except Exception as e:
        print(f"Błąd podczas zapisywania pliku ZPL: {e}")
        return None

# Funkcja do otwierania strony i przesyłania pliku
def open_zpl_printer_website_and_upload_file(driver, file_path):
    try:
        # Otwórz nową kartę
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])  # Przełącz się na nową kartę

        # Przejdź do strony ZPL Printer
        driver.get("https://labelary.com/viewer.html")
        print("Strona ZPL Printer została otwarta w nowej karcie.")

        # Wczytanie zawartości pliku ZPL
        with open(file_path, "r", encoding="utf-8") as file:
            zpl_data = file.read()
        print("Zawartość pliku ZPL została wczytana.")

        # Poczekaj, aż pole tekstowe będzie widoczne
        text_area = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "zpl")))

        # Wklejenie danych do pola tekstowego
        text_area.clear()
        text_area.send_keys(zpl_data)
        print("Dane ZPL zostały wklejone do pola tekstowego.")

        # Znalezienie przycisku "Redraw ZPL" i kliknięcie
        wait = WebDriverWait(driver, 5)
        submit_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn btn-default")))
        driver.execute_script("arguments[0].scrollIntoView();", submit_button)
        time.sleep(1)  # Czekamy chwilę po przewinięciu
        driver.execute_script("arguments[0].click();", submit_button)
        print("Przycisk 'Redraw ZPL' został kliknięty.")

    except Exception as e:
        print(f"Błąd: {e}")

# Główna część programu
if __name__ == "__main__":
    # Ścieżka do folderu głównego
    main_folder = r"C:\Users\bgromadka\Desktop\generowanie etykiet- dokumentacja\Etykiety"

    # Nazwa folderu metody (np. nazwa skryptu lub funkcji)
    method_folder_name = "label_GenerateStandardCustomerReturn_ZPL"

    # Lista partnerów (PartnerID, PartnerKey)
    partners = [
        ("PWRTR50301", "PWRTR50301"),


        ("TEST000129", "TTFWWSCSVO"),

    ]

    print("Pobieranie etykiet...")

    try:
        # Inicjalizacja przeglądarki Chrome
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option("detach", True)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        for partner_id, partner_key in partners:
            print(f"Generowanie etykiety dla {partner_id}...")
            label_base64 = get_label(partner_id, partner_key)
            output_filename = PARTNER_FILE_NAMES[partner_id]  # Pobierz nazwę pliku dla danego partnera
            new_output_filename = decode_and_save_zpl(label_base64, main_folder, method_folder_name, output_filename)

            if new_output_filename:  # Sprawdź, czy plik został poprawnie zapisany
                # Otwórz stronę ZPL Printer i prześlij plik w nowej karcie
                file_path = os.path.join(main_folder, "wygenerowane etykiety", method_folder_name, new_output_filename)
                if os.path.exists(file_path):  # Sprawdź, czy plik istnieje
                    open_zpl_printer_website_and_upload_file(driver, file_path)
                else:
                    print(f"Plik {file_path} nie istnieje.")

        print("Wszystkie etykiety zostały przetworzone. Przeglądarka pozostaje otwarta.")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")