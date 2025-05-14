import shutil

import requests
import base64
import os
import xml.etree.ElementTree as ET
import datetime

from common_data import URL_DICT, OUTPUT_FOLDER, MISSING_LABEL_FILE

# Konfiguracja
HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# Mapowanie partnerów na nazwy plików
PARTNER_FILE_NAMES = {
    "PWRTR50301": "GenerateLabelBusinessPackListAllegro__allegro__PDF.pdf",
}

# Funkcja generująca XML dla danego PartnerID i PartnerKey
def generate_soap_body(partner_id, partner_key):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
   <soap:Body>
        <GenerateLabelBusinessPackListAllegro xmlns="https://91.242.220.103/WebServicePwR">
      <PartnerID>{partner_id}</PartnerID>
      <PartnerKey>{partner_key}</PartnerKey>
       <AutoDestinationChange>T</AutoDestinationChange>
      ----------------------------------------------------------Punkt odbioru
      <BusinessPackList>
        <BusinessPackAllegro>
            <DestinationCode>WS-100001</DestinationCode>
            <AlternativeDestinationCode>100001</AlternativeDestinationCode>


      ----------------------------------------------------------Punkt odbioru
----------------------------------------------------------format wydruku
      <Format>PDF10</Format>

----------------------------------------------------------format wydruku
----------------------------------------------------------rozmiar paczki- gabaryt
            <BoxSize>L</BoxSize>
----------------------------------------------------------rozmiar paczki- gabaryt
----------------------------------------------------------pole referencji widoczne na etykiecie
            <SenderOrders>referencja</SenderOrders>
----------------------------------------------------------pole referencji widoczne na etykiecie
----------------------------------------------------------dodatkowe serwisy
            <Insurance></Insurance>--T-F
            <PackValue></PackValue>--kwota
            <CashOnDelivery></CashOnDelivery>--T-F
            <AmountCashOnDelivery></AmountCashOnDelivery>--kwota
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
            <PrintAdress>1</PrintAdress>-------wybór adresu do wydruku przy zwrocie  1- adres odbiorcy, 2 - adres zwrotu
            <PrintType>1</PrintType>
----------------------------------------------------------Nadawca
----------------------------------------------------------dane dla zwrotu
            <ReturnDestinationCode></ReturnDestinationCode>
            <ReturnEMail></ReturnEMail>
            <ReturnFirstName></ReturnFirstName>
            <ReturnLastName></ReturnLastName>
            <ReturnCompanyName></ReturnCompanyName>
            <ReturnStreetName></ReturnStreetName>
            <ReturnBuildingNumber></ReturnBuildingNumber>
            <ReturnFlatNumber></ReturnFlatNumber>
            <ReturnCity></ReturnCity>
            <ReturnPostCode></ReturnPostCode>
            <ReturnPhoneNumber></ReturnPhoneNumber>
            <ReturnPack>F</ReturnPack>-------zwrot czy nie T/N
----------------------------------------------------------dane dla zwrotu
----------------------------------------------------------marketning
            <ConfirmTermsOfUse></ConfirmTermsOfUse>
            <ConfirmMarketing></ConfirmMarketing>
            <CofirmMailing></CofirmMailing>
----------------------------------------------------------marketning
----------------------------------------------------------allegro
            <AllegroId></AllegroId>
            <AllegroOrderId></AllegroOrderId>
            <AllegroCustomerLogin></AllegroCustomerLogin>
            <AllegroTransactionId></AllegroTransactionId>
            <AllegroSellerId></AllegroSellerId>
            <AllegroDeliveryType></AllegroDeliveryType>
            <AllegroPaymentType></AllegroPaymentType>
            <AllegroDealId></AllegroDealId>
      ----------------------------------------------------------allegro
        </BusinessPackAllegro>

      </BusinessPackList>
    </GenerateLabelBusinessPackListAllegro>
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

    # Sprawdzanie, czy <LabelData> znajduje się w odpowiedzi
    label_data = root.find(".//LabelData", namespaces=namespaces)

    pack_codes = root.findall(".//PackCode_RUCH", namespaces=None)
    result_pack_code = '__'.join(el.text for el in pack_codes)

    return label_data.text if label_data is not None else None, result_pack_code


# Funkcja dekodująca Base64 i zapisująca PDF w określonym folderze
def decode_and_save_pdf(base64_data, pack_code, main_folder, method_folder_name, output_filename, url_name):
    """Dekoduje dane Base64 i zapisuje je jako plik PDF w określonym folderze z datą i godziną w nazwie pliku."""
    try:
        # Ścieżka do folderu metody wewnątrz "wygenerowane etykiety"
        method_folder = os.path.join(main_folder, method_folder_name)
        os.makedirs(method_folder, exist_ok=True)
        print(f"Folder metody '{method_folder_name}' został utworzony: {method_folder}")

        # Upewniamy się, że folder istnieje
        os.makedirs(method_folder, exist_ok=True)
        print(f"Folder docelowy: {method_folder}")

        # Pobranie aktualnej daty i godziny
        current_time = datetime.datetime.now().strftime("%H-%M-%S")

        # Tworzenie nowej nazwy pliku z datą i godziną
        filename, file_extension = os.path.splitext(output_filename)
        new_output_filename = f"{filename}__{url_name}__{pack_code}__{current_time}{file_extension}"
        print(f"Nowa nazwa pliku: {new_output_filename}")

        # Pełna ścieżka do pliku PDF
        output_path = os.path.join(method_folder, new_output_filename)
        print(f"Pełna ścieżka do pliku: {output_path}")

        # Dekodowanie Base64 i zapis do pliku PDF
        if base64_data is None:
            shutil.copy(MISSING_LABEL_FILE, output_path)

        else:
            pdf_data = base64.b64decode(base64_data)
            print(f"Długość danych PDF: {len(pdf_data)} bajtów")

            with open(output_path, "wb") as pdf_file:
                pdf_file.write(pdf_data)
                print(f"Plik PDF zapisany: {output_path}")

    except Exception as e:
        raise Exception(f"Błąd podczas zapisywania pliku PDF: {e}")

if __name__ == "__main__":

    # Nazwa folderu metody (np. nazwa skryptu lub funkcji)
    method_folder_name = "GenerateLabelBusinessPackListAllegro_PDF"

    # Lista partnerów (PartnerID, PartnerKey)
    partners = [
        ("PWRTR50301", "PWRTR50301"),

    ]

    print("Pobieranie etykiet...")

    try:
        # Generowanie etykiety dla każdego partnera
        for url_name, url_value in URL_DICT.items():
            for partner_id, partner_key in partners:
                print(f"Generowanie etykiety dla partnera {partner_id}...")
                response_data = get_label(partner_id, partner_key, url_value)
                decode_and_save_pdf(response_data[0], response_data[1], OUTPUT_FOLDER, method_folder_name,
                                    PARTNER_FILE_NAMES[partner_id], url_name)

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
