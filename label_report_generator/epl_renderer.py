import base64
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class EPLRenderer:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

        self.driver.get("https://eplprinter.azurewebsites.net/")
        checkbox = self.driver.find_element(By.ID, "chkUTF8")
        checkbox.click()
        self.text_area = self.wait.until(EC.presence_of_element_located((By.ID, "eplCommands")))
        self.submit_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-danger")))

    def render(self, filepath: str):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                epl_code = file.read()

            self.text_area.clear()
            self.text_area.send_keys(epl_code)

            self.driver.execute_script("arguments[0].scrollIntoView();", self.submit_button)
            self.driver.execute_script("arguments[0].click();", self.submit_button)

            self.wait.until(
                lambda driver: driver.find_element(By.ID, "imgLabelPreview")
                .get_attribute("src").startswith("data:image"))
            img_element = self.driver.find_element(By.ID, "imgLabelPreview")
            src = img_element.get_attribute("src")

            if src.startswith("data:image"):
                _, encoded = src.split(",", 1)
                image_data = base64.b64decode(encoded)
                image_path = filepath + ".png"
                with open(image_path, "wb") as img_file:
                    img_file.write(image_data)
                return image_path

            else:
                return None

        except Exception as e:
            logging.error(f"Error during rendering EPL: {filepath} | {e}")
            return None

    def close(self):
        self.driver.quit()
