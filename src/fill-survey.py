from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import argparse
import time
import sys


parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", action="store", dest="url", required=True, type=str,
                    help="URL of the Daily Health Check survey from UTD")
parser.add_argument("-n", "--no", action="store_true", dest="on_campus_no", default=False,
                    help="Indicate that you are not on campus.")
args = vars(parser.parse_args())

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

driver.get(args["url"])

if args["on_campus_no"]:
    radio_button_ids = ["label-on_campus-0"]
else:
    radio_button_ids = ["label-on_campus-1", "label-q_1-0", "label-q_2-0", "label-q_3-0",
                        "label-q_4-0", "label-q_5-0", "label-healthy_cert-1"]

exit_code = 0
try:
    for element_id in radio_button_ids:
        try:
            radio_element = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, element_id)))
            radio_element.click()
        except:
            print(f"Expected option not found for id: {element_id}.")
            exit_code = -1

    try:
        submit_button = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.NAME, "submit-btn-saverecord")))
        submit_button.click()
    except:
        print(f"Submission button not found.")
        exit_code = -1
finally:
    time.sleep(2)
    driver.quit()
    sys.exit(exit_code)
