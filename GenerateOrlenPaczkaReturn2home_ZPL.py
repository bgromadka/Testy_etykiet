import requests
import base64
import os
import xml.etree.ElementTree as ET
import datetime
from common_data import URL_DICT, OUTPUT_FOLDER, MISSING_LABEL_FILE
import shutil
# Konfiguracja

HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# Mapowanie partnerów na nazwy plików
PARTNER_FILE_NAMES = {

    "TEST000129": "GenerateOrlenPaczkaReturn2Home_Packeta_ZPL.zpl",




}


# Funkcja generująca XML dla danego PartnerID i PartnerKey
def generate_soap_body(partner_id, partner_key):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
   <soap:Body>
    <GenerateOrlenPaczkaReturn2Home xmlns="https://91.242.220.103/WebServicePwR">
----------------------------------------------------------Generowanie listu przewozowego z etykieta
       <PartnerID>{partner_id}</PartnerID>
      <PartnerKey>{partner_key}</PartnerKey>


         <DestinationCode>100001</DestinationCode>
            <AlternativeDestinationCode></AlternativeDestinationCode>
----------------------------------------------------------Punkt odbioru
----------------------------------------------------------serwisy
      <Format>zpl</Format>
            <BoxSize>S</BoxSize>
            <Insurance></Insurance>
            <PackValue></PackValue>
----------------------------------------------------------serwisy
----------------------------------------------------------pole referencji widoczne na etykiecie
<SenderOrders>SenderOrders</SenderOrders>
----------------------------------------------------------pole referencji widoczne na etykiecie

      <OriginalPackageNumber></OriginalPackageNumber>
----------------------------------------------------------Odbiorca
            <PhoneNumber>885779607</PhoneNumber>
            <EMail>testypostman@ruch.com.pl</EMail>
            <FirstName>FirstName</FirstName>
            <LastName>LastName</LastName>
            <CompanyName>CompanyName</CompanyName>
            <StreetName>StreetName</StreetName>
            <BuildingNumber>1</BuildingNumber>
            <FlatNumber>1</FlatNumber>
            <City>City</City>
            <PostCode>04-347</PostCode>
----------------------------------------------------------Odbiorca
----------------------------------------------------------Nadawca
            <SenderEMail>tmsec1p9ju+4f9d21f12@user.allegrogroup.pl</SenderEMail>
            <SenderFirstName>SenderFirstName</SenderFirstName>
            <SenderLastName>SenderLastName</SenderLastName>
            <SenderCompanyName>SenderCompanyName</SenderCompanyName>
            <SenderStreetName>SenderStreetName</SenderStreetName>
            <SenderBuildingNumber>1</SenderBuildingNumber>
            <SenderFlatNumber>1</SenderFlatNumber>
            <SenderCity>SenderCity</SenderCity>
            <SenderPostCode>04-347</SenderPostCode>
            <SenderPhoneNumber>885779607</SenderPhoneNumber>
----------------------------------------------------------Nadawca
      <ExternalSenderPackageNumber>Ad111111111</ExternalSenderPackageNumber>
      <ExternalPackageNumber></ExternalPackageNumber>
      <Serwis></Serwis>
      <ItemsInPackage></ItemsInPackage>

    </GenerateOrlenPaczkaReturn2Home>
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

    # Sprawdzanie, czy <LabelData> znajduje się w odpowiedzi
    label_data = root.find(".//LabelData", namespaces=namespaces)

    pack_codes = root.findall(".//PackCode_RUCH", namespaces=None)
    result_pack_code = '__'.join(el.text for el in pack_codes)

    return label_data.text if label_data is not None else None, result_pack_code

    # Zwracamy zakodowaną etykietę
    return label_data.text

# Funkcja dekodująca Base64 i zapisująca ZPL
def decode_and_save_zpl(base64_data, pack_code, main_folder, method_folder_name, output_filename, url_name):
    """Dekoduje dane Base64 i zapisuje je jako plik ZPL w określonym folderze z datą i godziną w nazwie pliku."""
    try:


        # Ścieżka do folderu metody wewnątrz "wygenerowane etykiety"
        method_folder = os.path.join(main_folder, method_folder_name)
        os.makedirs(method_folder, exist_ok=True)
        print(f"Folder metody '{method_folder_name}' został utworzony: {method_folder}")

        # Upewniamy się, że folder istnieje
        os.makedirs(method_folder, exist_ok=True)
        print(f"Folder docelowy: {method_folder}")

        # Dekodowanie Base64


        # Pobranie aktualnej daty i godziny
        current_time = datetime.datetime.now().strftime("%H-%M-%S")

        # Tworzenie nowej nazwy pliku z datą i godziną
        filename, file_extension = os.path.splitext(output_filename)
        new_output_filename = f"{filename}__{url_name}__{pack_code}__{current_time}{file_extension}"
        print(f"Nowa nazwa pliku: {new_output_filename}")

        # Pełna ścieżka do pliku ZPL
        output_path = os.path.join(method_folder, new_output_filename)
        print(f"Pełna ścieżka do pliku: {output_path}")

        # Zapisz dane ZPL do pliku
        # Dekodowanie Base64
        if base64_data is None:
            shutil.copy(MISSING_LABEL_FILE, output_path)
        else:
            data = base64.b64decode(base64_data)
            print(f"Długość danych pliku: {len(data)} bajtów")
        # Uruchomienie Notepad++ w tle
        # notepad_plus_plus_path = r"C:\Program Files\Notepad++\notepad++.exe"  # Ścieżka do Notepad++
        # if os.path.exists(notepad_plus_plus_path):
        #     subprocess.Popen([notepad_plus_plus_path, output_path])
        # else:
        #     print("Nie znaleziono Notepad++ w domyślnej lokalizacji. Upewnij się, że jest zainstalowany.")

        with open(output_path, "wb") as file:
            file.write(data)
            print(f"Plik zapisany: {output_path}")


    except Exception as e:
        print(f"Błąd podczas zapisywania pliku ZPL: {e}")


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
    method_folder_name = "GenerateOrlenPaczkaReturn2Home_ZPL"

    # Lista partnerów (PartnerID, PartnerKey)
    partners = [



        ("TEST000129", "TTFWWSCSVO"),

    ]

    print("Pobieranie etykiet...")

    try:
        try:
            for url_name, url_value in URL_DICT.items():
                for partner_id, partner_key in partners:
                    print(f"Generowanie etykiety dla partnera {partner_id}...")
                    response_data = get_label(partner_id, partner_key, url_value)
                    decode_and_save_zpl(response_data[0], response_data[1], OUTPUT_FOLDER,
                                        method_folder_name, PARTNER_FILE_NAMES[partner_id], url_name)
        except Exception as e:
            print(f"Wystąpił błąd: {e}")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")