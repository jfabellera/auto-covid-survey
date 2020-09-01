from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", action="store", dest="url", required=True, type=str,
                    help="URL of the Daily Health Check survey from UTD")
parser.add_argument("-d", "--driver", action="store", dest="driver_path", type=str,
                    help="Path to chrome driver version 85 if in different directory.",
                    default="C:/Program Files (x86)/chromedriver.exe")
parser.add_argument("-n", "--no", action="store_true", dest="on_campus_no", default=False,
                    help="Indicate that you are not on campus.")
args = vars(parser.parse_args())

driver = webdriver.Chrome(args["driver_path"])

driver.get(args["url"])

if args["on_campus_no"]:
    radio_button_ids = ["label-on_campus-0"]
else:
    radio_button_ids = ["label-on_campus-1", "label-q_1-0", "label-q_2-0", "label-q_3-0",
                        "label-q_4-0", "label-q_5-0", "label-healthy_cert-1"]

for element_id in radio_button_ids:
    try:
        radio_element = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, element_id)))
        radio_element.click()
    except:
        print(f"Expected option not found for id: {element_id}.")

try:
    submit_button = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.NAME, "submit-btn-saverecord")))
    # submit_button.click()
except:
    # TODO report to user status of submission
    print(f"Submission button not found.")
