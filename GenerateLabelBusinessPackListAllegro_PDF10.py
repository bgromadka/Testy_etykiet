import requests
import base64
import os
import xml.etree.ElementTree as ET
import webbrowser
import datetime

# Konfiguracja
SOAP_URL = "http://bruchorpact03/WebServicePwRKube/WebServicePwR.asmx"
HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# Mapowanie partnerów na nazwy plików
PARTNER_FILE_NAMES = {
    "PWRTR50301": "label_standard_GenerateLabelBusinessPackListAllegro_PDF10.pdf",
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

    # Sprawdzanie, czy <LabelData> znajduje się w odpowiedzi
    label_data = root.find(".//LabelData", namespaces=namespaces)

    if label_data is None or not label_data.text:
        raise Exception("Nie znaleziono danych etykiety w odpowiedzi SOAP.")

    # Zwracamy zakodowaną etykietę
    return label_data.text

# Funkcja dekodująca Base64 i zapisująca PDF10 w określonym folderze
def decode_and_save_pdf10(base64_data, folder_path, output_filename):
    """Dekoduje dane Base64 i zapisuje je jako plik PDF10 w określonym folderze z datą i godziną w nazwie pliku."""
    try:
        # Upewniamy się, że folder istnieje
        os.makedirs(folder_path, exist_ok=True)

        # Pobranie aktualnej daty i godziny
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Tworzenie nowej nazwy pliku z datą i godziną
        filename, file_extension = os.path.splitext(output_filename)
        new_output_filename = f"{filename}_{current_time}{file_extension}"

        # Pełna ścieżka do pliku PDF10
        output_path = os.path.join(folder_path, new_output_filename)

        # Dekodowanie Base64 i zapis do pliku PDF10
        with open(output_path, "wb") as pdf10_file:
            pdf10_file.write(base64.b64decode(base64_data))

        # Otwórz plik PDF10 w przeglądarce
        webbrowser.open(f'file://{os.path.abspath(output_path)}')
        print(f"Etykieta została zapisana jako PDF10 w folderze {folder_path}: {new_output_filename} i otwarta w przeglądarce.")
    except Exception as e:
        print(f"Błąd podczas zapisywania pliku PDF10: {e}")

if __name__ == "__main__":
    # Ścieżka do folderu, w którym będą zapisane etykiety
    folder_name = "label_GenerateLabelBusinessPackListAllegro_PDF10"

    # Lista partnerów (pary PartnerID, PartnerKey)
    partners = [
        ("PWRTR50301", "PWRTR50301"),
    ]

    print("Pobieranie etykiet...")

    try:
        for partner_id, partner_key in partners:
            print(f"Generowanie etykiety dla {partner_id}...")
            label_base64 = get_label(partner_id, partner_key)
            output_filename = PARTNER_FILE_NAMES[partner_id]  # Pobierz nazwę pliku dla danego partnera
            decode_and_save_pdf10(label_base64, folder_name, output_filename)

    except Exception as e:
        print(f"Wystąpił błąd: {e}")