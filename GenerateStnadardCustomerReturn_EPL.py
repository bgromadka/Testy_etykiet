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
from common_data import OUTPUT_FOLDER, URL_DICT
# Konfiguracja

HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# Mapowanie partnerów na nazwy plików
PARTNER_FILE_NAMES = {
    "PWRTR50301": "GenerateStandardCustomerReturn_Pokemon_EPL.epl",


}

# Konfiguracja

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
      <Format>EPL</Format>

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


def decode_and_save_EPL(base64_data, main_folder, method_folder_name, output_filename, url_name):
    """Dekoduje dane Base64 i zapisuje je jako plik EPL w określonym folderze z datą i godziną w nazwie pliku."""
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
        EPL_data = base64.b64decode(base64_data)

        # Pobranie aktualnej daty i godziny
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Tworzenie nowej nazwy pliku z datą i godziną
        filename, file_extension = os.path.splitext(output_filename)
        new_output_filename = f"{filename}__{url_name}__{current_time}{file_extension}"
        print(f"Nowa nazwa pliku: {new_output_filename}")

        # Pełna ścieżka do pliku EPL
        output_path = os.path.join(method_folder, new_output_filename)
        print(f"Pełna ścieżka do pliku: {output_path}")

        # Zapisz dane EPL do pliku
        with open(output_path, "wb") as EPL_file:
            EPL_file.write(EPL_data)

        # Uruchomienie Notepad++ w tle
        #notepad_plus_plus_path = r"C:\Program Files\Notepad++\notepad++.exe"  # Ścieżka do Notepad++
        #if os.path.exists(notepad_plus_plus_path):
         #   subprocess.Popen([notepad_plus_plus_path, output_path])
        #else:
         #   print("Nie znaleziono Notepad++ w domyślnej lokalizacji. Upewnij się, że jest zainstalowany.")

        #print(f"Etykieta została zapisana jako EPL w folderze {method_folder}: {new_output_filename} i otwarta w Notepad++.")
    except Exception as e:
        print(f"Błąd podczas zapisywania pliku EPL: {e}")

def get_label(partner_id, partner_key, url):
    """Wysyła zapytanie SOAP i pobiera etykietę w formacie Base64."""
    soap_body = generate_soap_body(partner_id, partner_key)

    response = requests.post(url, data=soap_body, headers=HEADERS, verify=True)

    if response.status_code != 200:
        # Funkcja wysyłająca zapytanie SOAP i pobierająca etykietę
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

# Funkcja do otwierania strony i przesyłania pliku
#def open_epl_printer_website_and_upload_file(driver, file_path):
 #   try:
        # Otwórz nową kartę
   #     driver.execute_script("window.open('');")
    #    driver.switch_to.window(driver.window_handles[-1])  # Przełącz się na nową kartę

        # Przejdź do strony EPL Printer
     #   driver.get("https://eplprinter.azurewebsites.net/")
      #  print("Strona EPL Printer została otwarta w nowej karcie.")

        # Zaznaczenie checkboxa zapewniającego polskie znaki
  #      checkbox = driver.find_element(By.ID, "chkUTF8")
   #     checkbox.click()

    #    # Sprawdzenie, czy checkbox jest zaznaczony
     #   assert checkbox.is_selected(), "Checkbox nie został zaznaczony!"

        # Wczytanie zawartości pliku EPL
      #  with open(file_path, "r", encoding="utf-8") as file:
       #     epl_data = file.read()

        # Poczekaj, aż pole tekstowe będzie widoczne
        #wait = WebDriverWait(driver, 10)
        #text_area = wait.until(EC.presence_of_element_located((By.ID, "eplCommands")))

        # Wklejenie danych do pola tekstowego
        #text_area.clear()
        #text_area.send_keys(epl_data)
        #print("Dane EPL zostały wklejone.")

        # Znalezienie przycisku "Print EPL" i kliknięcie
        #submit_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-danger")))
        #driver.execute_script("arguments[0].scrollIntoView();", submit_button)
       # time.sleep(1)  # Czekamy chwilę po przewinięciu
      #  driver.execute_script("arguments[0].click();", submit_button)
     #   print("Przycisk 'Print EPL' został kliknięty.")

    #except Exception as e:
       # print(f"Błąd: {e}")

# Główna część programu
if __name__ == "__main__":

    # Nazwa folderu metody (np. nazwa skryptu lub funkcji)
    method_folder_name = "GenerateStandardCustomerReturn_EPL"

    # Lista partnerów (PartnerID, PartnerKey)
    partners = [
        ("PWRTR50301", "PWRTR50301"),


    ]

    print("Pobieranie etykiet...")

    try:
        # Inicjalizacja przeglądarki Chrome
       # chrome_options = Options()
        #chrome_options.add_argument("--start-maximized")
        #chrome_options.add_experimental_option("detach", True)
        #service = Service(ChromeDriverManager().install())
        #driver = webdriver.Chrome(service=service, options=chrome_options)

        for url_name, url_value in URL_DICT.items():
            for partner_id, partner_key in partners:
                print(f"Generowanie etykiety dla {partner_id}...")
                label_base64 = get_label(partner_id, partner_key, url_value)
                decode_and_save_EPL(label_base64, OUTPUT_FOLDER, method_folder_name, PARTNER_FILE_NAMES[partner_id],
                                    url_name)
            # Otwórz stronę EPL Printer i prześlij plik w nowej karcie
           # file_path = os.path.join(main_folder, "wygenerowane etykiety", method_folder_name, f"{output_filename}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.epl")
            #open_epl_printer_website_and_upload_file(driver, file_path)

        #print("Wszystkie etykiety zostały przetworzone. Przeglądarka pozostaje otwarta.")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")