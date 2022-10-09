from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pickle, datetime, time, pandas as pd

hoursFile = open("hours.csv", "r")
line = hoursFile.readline()
loginHour, triggerHour = [int(i) for i in line.split(',')]

url = "https://nyuad.dserec.com/online/capacity"
PATH = "./chromedriver_win.exe"
dataFile = "data.csv"

df = pd.read_csv(dataFile)
netids, passwords, bookingTimes = list(df["netid"]), list(df["password"]), list(df["booking-time"])

driver = None
options = Options()
options.add_argument("--window-size=1920,1080")
options.add_argument("--start-maximized")

dateTriggered = None
dateLoggedIn = None
refreshed = None

class User():
    def __init__(self, netid, password, bookingTime) -> None:
        self.netid = netid
        self.password = password
        self.bookingTime = bookingTime

    def trigger(self, cookies=None):

        print("[START]")

        global driver, options
        driver = Chrome(executable_path=PATH, options=options)
        driver.get(url)

        if(cookies != None):
            for cookie in cookies:
                driver.add_cookie(cookie)

            print("COOKIES ADDED")

            driver.get(url)

        wait = WebDriverWait(driver, 60)
        driver.switch_to.frame(driver.find_element_by_id("dse-widget"))

        if cookies == None:
            login_link = driver.find_element_by_class_name("login-link")
            login_link.click()
            print("LOGIN CLICKED")

            sso = driver.find_element_by_class_name("btn")
            if(sso.text.lower() == "university sso"):
                sso.click()

                print("SSO CLICKED")

            this_url = driver.current_url

            wait.until(EC.presence_of_element_located((By.ID, "username")))
            username_txt = driver.find_element_by_id("username")
            password_txt = driver.find_element_by_id("password")
            username_txt.send_keys(self.netid)
            password_txt.send_keys(self.password)

            login_button = driver.find_element_by_name("_eventId_proceed")
            login_button.click()
            
            wait.until(lambda driver: driver.current_url != this_url)
            
            this_url = driver.current_url

            wait.until(lambda driver: driver.current_url != this_url)
            pickle.dump(driver.get_cookies(), open("cookies_{}.pkl".format(self.netid), "wb"))
            print("COOKIES SAVED")
            driver.quit()

        else:
            time.sleep(2)
            tabs = driver.find_elements_by_class_name("overflow-break-word")
            for tab in tabs:
                if tab.text.lower().strip() == "fitness center":
                    tab.click()

            time.sleep(2)
            for i in range(2):
                wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a.online-reserve-link")))
                next = driver.find_elements_by_css_selector("a.online-reserve-link")[1]
                next.click()
            
            time.sleep(2)

            slots = driver.find_elements_by_class_name("day-time-slot")
            print("[FINDING TIME SLOT]")

            available = False
            for slot in slots:
                if slot.text.lower().strip() == self.bookingTime:
                    slot.click()
                    available = True

            if not available:
                print("SLOT NOT AVAILABLE")
            else:
                time.sleep(2)
                confirm = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "btn-primary")))
                confirm.click()
                print("[SLOT CONFIRMED]")
                driver.save_screenshot("CONFIRMED.png")

            time.sleep(2)
            driver.quit()

    def refreshCookies(self, cookies):
        global driver, options
        driver = Chrome(executable_path=PATH, options=options)
        driver.get(url)

        if(cookies != None):
            for index, cookie in enumerate(cookies):
                driver.add_cookie(cookie)
                if index == 1: print(time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.localtime(cookie["expiry"])))

            print("COOKIES REFRESHED FOR", self.netid)

            driver.get(url)
            time.sleep(2)

        pickle.dump(driver.get_cookies(), open("cookies_{}.pkl".format(self.netid), "wb"))
        driver.quit()


USERS = []
for idx, id in enumerate(netids):
    USERS.append(User(id, passwords[idx], bookingTimes[idx]))

def setDates() -> None:
    pass

def main() -> None:
    global dateTriggered, dateLoggedIn, refreshed
    if datetime.datetime.now().hour == loginHour and dateLoggedIn != datetime.datetime.now().date():
        for user in USERS:
            try:
                user.trigger()
            except Exception as e:
                print(e)
        dateLoggedIn = datetime.datetime.now().date()
        refreshed = datetime.datetime.now()
    
    elif datetime.datetime.now().hour == triggerHour and dateTriggered != datetime.datetime.now().date():
        for user in USERS:
            cookies = pickle.load(open("cookies_{}.pkl".format(user.netid), "rb"))
            try:
                user.trigger(cookies=cookies)
            except Exception as e:
                print(e)
        dateTriggered = datetime.datetime.now().date()

    elif refreshed != None and (datetime.datetime.now() - refreshed).total_seconds() >= (60 * 60) and dateTriggered != datetime.datetime.now().date():
        for user in USERS:
            cookies = pickle.load(open("cookies_{}.pkl".format(user.netid), "rb"))
            user.refreshCookies(cookies)
            refreshed = datetime.datetime.now()

while True:
    main()
