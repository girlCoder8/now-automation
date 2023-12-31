import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import os
from getpass import getpass


###This class is used to perform all actions common to all ServiceNow applications
class ServiceNow():
    log_id = "ServiceNow"
    auth_page = "shib.idm.umd.edu"
    side_door = "https://umddev.service-now.com/side_door.do"
    home_page = "https://umddev.service-now.com"

    impl_wait = 30
    expl_wait = 5

    def __init__(self, driver, logs=True):
        driver.implicitly_wait(self.impl_wait)
        self.driver = driver
        self.logs = logs
        if logs:
            print("Created ServiceNow Object")
            print("Implicit Wait Time Set To", self.impl_wait)
            print("Explicit Wait Time Set To", self.expl_wait)
        else:
            print("Logs Disabled")

    def log(self, s):
        if self.logs: print("%s:" % log_id, s)

    def navigate_to_agent_view(self, tol=10):
        self.driver.get(self.home_page)

        while "itsupport" in self.driver.current_url and tol > 0:
            self.driver.get(self.home_page)
            tol -= 1

    def leave_form(self):
        self.driver.get(self.home_page)
        try:
            self.driver.switchTo().alert().accept();
        except:
            self.log("No Block Found")

    def side_door_login(self):
        self.log("Logging in through side door")
        self.driver.get(self.side_door)

        with open("secret.txt", "r") as f:
            creds = [line.split("\n")[0] for line in f]
            self.driver.switch_to.frame(self.driver.find_element(By.ID, "gsft_main"))
            self.driver.find_element(By.ID, "user_name").send_keys(creds[0])
            self.driver.find_element(By.ID, "user_password").send_keys(creds[1])
            self.driver.find_element(By.ID, "sysverb_login").click()
            self.driver.switch_to.default_content()
            f.close()
        time.sleep(self.expl_wait)
        self.log("Logged in through side door")

    def login(self, directory_id=None, password=None):
        self.log("Checking that user is logged in")
        self.driver.get(self.home_page)
        if self.auth_page not in self.driver.current_url: return

        self.log("Requesting user credentials for login")
        if not directory_id: directory_id = input("Directory ID: ")
        if not password: password = getpass()  # input("Password")

        self.log("Logging in as " + directory_id)
        self.driver.find_element(By.ID, "username").send_keys(directory_id)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR,
                                 "body > div.wrapper > div > div.content > div.column.one > form > div:nth-child(4) > button").click()

        self.log("Sending Push To Duo")
        self.driver.switch_to.frame(self.driver.find_element(By.ID, "duo_iframe"))
        self.driver.find_element(By.CSS_SELECTOR,
                                 "#auth_methods > fieldset > div.row-label.push-label > button").click()
        self.driver.switch_to.default_content()
        WebDriverWait(self.driver, self.impl_wait * 1000).until(
            expected_conditions.visibility_of_element_located((By.ID, "user_info_dropdown")))

        self.log("Logged in as " + directory_id)
        self.user = directory_id
        return True

    # EXPLICIT WAIT SHOULD BE REPLACED
    def impersonate(self, user):
        self.log("Impersonating " + user)
        self.navigate_to_agent_view()

        self.log("Finding " + user)
        self.driver.find_element(By.ID, "user_info_dropdown").click()
        self.driver.find_element(By.CSS_SELECTOR, "#glide_ui_impersonator").click()
        element = self.driver.find_element(By.ID, "select2-chosen-2")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "select2-drop-mask")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()

        # WebDriverWait(self.driver, self.impl_wait*1000).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "#select2-results-2 > li")))
        time.sleep(self.expl_wait)
        self.driver.find_element(By.ID, "s2id_autogen2_search").send_keys(user)
        time.sleep(self.expl_wait)
        self.driver.find_element(By.CSS_SELECTOR, "#select2-results-2 > li").click()  # send_keys(Keys.ENTER)
        self.log("Impersonated " + user)
        self.user = user
        time.sleep(self.expl_wait)
        self.driver.get(self.home_page)

    def check_submit(self):
        self.log("Checking That Form Was Submitted")
        elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "RITM")
        if len(elements) <= 0: return None, None

        ticket = self.driver.find_element(By.PARTIAL_LINK_TEXT, "RITM").text
        self.log("Ticket: " + ticket)
        self.driver.find_element(By.PARTIAL_LINK_TEXT, "RITM").click()

        fields = self.driver.find_elements(By.CLASS_NAME, "select2-chosen")
        for f in fields:
            if "REQ" in f.text:
                self.log("Request: " + f.text)
                return ticket, f.text

        return ticket, None

    def navigate_to_ticket(self, req, form, tic=None):
        self.log("Navigating To Ticket With Request: " + req)
        self.driver.get(self.req_url)
        elements = self.driver.find_elements(By.CLASS_NAME, "main-column")
        for e in elements:
            if req in e.text:
                self.log("Found Request " + req)
                e.find_element(By.PARTIAL_LINK_TEXT, form).click()

                ritm = self.driver.find_element(By.PARTIAL_LINK_TEXT, "RITM")
                if ritm.text == tic: self.log("Ticket Verified " + ritm.text)
                ritm.click()

                return True
        return False

    def get_approvers(self):
        self.log("Finding Approvers")
        els = self.driver.find_elements(By.CLASS_NAME, "col-xs-6")
        alt = self.driver.find_elements(By.CSS_SELECTOR, ".col-xs-1 > span")
        app = []
        for i, e in enumerate(els):
            try:
                app.append((e.text.split("\n")[0], alt[i].get_attribute("alt")))
            except:
                continue
        for a in app:
            self.log("Found Approver %s with status %s" % a)
        return app

    def approve_ticket(self, approver, ticket, request, reject=False, res="This is a reason to reject"):
        user = self.user
        self.log("%s Ticket for %s" % (("Approving", "Rejecting")[reject], self.user))
        self.impersonate(approver)

        self.log("Navigating to Ticket " + ticket)
        self.driver.get(self.temp_app_url)
        els = self.driver.find_elements(By.CSS_SELECTOR, "li:nth-child(9) > a > span:nth-child(1)")
        for el in els:
            if "my approval needed" in el.text.lower():
                break
        el.click()
        # self.driver.get(self.app_url)
        self.driver.find_element(By.PARTIAL_LINK_TEXT, ticket).click()
        time.sleep(self.expl_wait)

        self.log("%s Ticket %s" % (("Approving", "Rejecting")[reject], ticket))
        self.driver.find_element(By.NAME, ("approve", "reject")[reject]).click()

        if reject:
            self.driver.find_element(By.ID, "rejetreason").send_keys(res)
            self.driver.find_elements(By.CSS_SELECTOR,
                                      "body > div.modal.fade.ng-isolate-scope.in > div > div > div > div.panel-footer.text-right > button.btn.btn-danger")[
                0].click()

        # self.driver.find_elements(By.CSS_SELECTOR, "#sp-nav-bar-global > div > ul > li.dropdown.hidden-xs.ng-scope > a > span.navbar-avatar > div > div > div")[0].click()
        # self.driver.find_elements(By.CSS_SELECTOR, "#sp-nav-bar-global > div > ul > li.dropdown.hidden-xs.ng-scope.open > ul > li:nth-child(4) > a")[0].click()
        self.impersonate(user)

    def chain_approval(self, ticket, request, actions=[]):
        chain = []
        i = 0
        while True:
            appr = True
            if i < len(actions): appr = actions[i]

            self.navigate_to_ticket(request, ticket)
            apps = self.get_approvers()
            apps = [a[0] for a in apps if a[1] == "Requested"]
            if len(apps) <= 0: break

            self.approve_ticket(apps[0], ticket, request, reject=(not appr))
            self.log("CHAIN " + str(len(chain)) + ": " + apps[0])

            chain.append(apps[0])
            self.log("Waiting One Minute For Approval Process")
            time.sleep(60)

            i += 1
        return chain


if __name__ == "__main__":
    chrome_driver_path = os.path.join(".", "chromedriver.exe")
    driver = webdriver.Chrome()  # executable_path=chrome_driver_path)
    sn = ServiceNow(driver)
    sn.login()
    sn.impersonate("Jess Jacobson")
    input("Hit Enter To Close Page")
    driver.quit()