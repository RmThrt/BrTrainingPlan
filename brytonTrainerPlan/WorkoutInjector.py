import json
import re
from tqdm import tqdm
from playwright.sync_api import sync_playwright

warmupFlag = r"^Warm Up$"
activityFlag = r"^Work$"
recoveryFlag = r"^Recovery$"
coolDownFlag = r"^Cool Down$"

col_type="type"
col_duration="duration"
col_min_power="min_power"
col_max_power="max_power"
col_cadence="cadence"

brytonActiveWorkoutUrl = "https://active.brytonsport.com/"

class BrowserManager:
    def __init__(self, headless):
        print("Initializing BrowserManager")
        self.headless = headless
        print("BrowserManager initialized")

    def setup_browser(self, playwright):
        print("Setting up browser")
        browser = playwright.firefox.launch(headless=self.headless)
        context = browser.new_context()
        page = context.new_page()
        self.login(page)
        print("Browser setup complete")
        return browser, context, page

    def read_json_file(self, file_path):
        print("Reading JSON file")
        with open(file_path, 'r') as json_file:
            
            data = json.load(json_file)
        print("JSON file read complete")
        return data

    def login(self, page):
        print("Logging in")
        page.goto(brytonActiveWorkoutUrl)
        config_data = self.read_json_file('config.json')
        page.get_by_placeholder("Email Address").fill(config_data['mail'])
        page.get_by_placeholder("Password").fill(config_data['pwd'])
        page.get_by_role("button", name="Log In", exact=True).click()
        print("Logged in")

    def close_browser(self, browser, context):
        print("Closing browser")
        context.close()
        browser.close()
        print("Browser closed")

class WorkoutCreator:
    sectionCount = -1

    def __init__(self, title, workout_df, headless):
        print("Initializing WorkoutCreator")
        self.title = title
        self.workout_df = workout_df
        with sync_playwright() as playwright:
            manager = BrowserManager(headless)
            browser, context, self.page = manager.setup_browser(playwright)
            self.create_workout()
            manager.close_browser(browser, context)
        print("WorkoutCreator initialized")

    def create_workout(self):
        print("Starting workout creation")
        self.page.get_by_text("Workout").click()    
        self.page.wait_for_timeout(3000)
        self.page.get_by_role("button", name="Add").click()
        self.page.wait_for_timeout(1000)
        self.page.get_by_role("paragraph").filter(has_text=re.compile(r"bsWO.*", re.IGNORECASE)).click()
        self.page.get_by_placeholder(re.compile(r"bsWO.*", re.IGNORECASE)).fill(self.title)
        
        for index, row in tqdm(self.workout_df.iterrows(), total=self.workout_df.shape[0]):
            self.add_new_section(str(row[col_type]))
            self.set_duration(str(row[col_duration]))   
            self.change_ftp_range(str(row[col_min_power]), str(row[col_max_power]))
            self.page.wait_for_timeout(3000)
        
        self.page.get_by_text("Save").click()
        self.page.locator("#dlg-body").get_by_text("Don't show this again.").click()
        self.page.get_by_role("button", name="OK").click()
        print("Workout creation complete")

    def add_new_section(self, regex):
        print("Adding new section")
        self.page.locator("div").filter(has_text=re.compile(regex)).locator("div").click()
        self.sectionCount += 1 
        self.page.wait_for_timeout(500)
        print("New section added")

    def set_duration(self, duration):
        print("Setting duration")
        self.page.get_by_role("paragraph").filter(has_text="Distance").click()
        self.page.get_by_role("listitem").filter(has_text="Time").click()
        duration_locator = self.page.locator("div > .wo-itv-content-frame > .wo-itv-content > .wo-itv-duration-frame")
        self.locate(duration_locator, duration)
        print("Duration set")

    def change_ftp(self, ftp, isLowRange):
        print("Changing FTP")
        base_selector = ".wo-itv-content-frame > .wo-itv-content > .wo-itv-range-frame > .wo-range-low"
        value_selector = " > .wo-range-low-val " if isLowRange else " > .wo-range-high-val "
        ftp_locator = self.page.locator(base_selector + value_selector)
        self.locate(ftp_locator, ftp)
        print("FTP changed")

    def locate(self, locator, value):
        print("Locating element")
        locator_placeholder = locator.get_by_placeholder(re.compile(r".*", re.IGNORECASE))
        if self.sectionCount >= 1:
            locator.nth(self.sectionCount).click()
            locator_placeholder.nth(self.sectionCount).fill(value)
            locator_placeholder.nth(self.sectionCount).press("Enter")
        else:
            locator.click()
            self.page.wait_for_timeout(3000)
            # locator_placeholder.wait_for()
            locator_placeholder.type(value)
            locator_placeholder.press("Enter")
        print("Element located")

    def change_ftp_range(self, min, max):
        print("Changing FTP range")
        self.change_ftp(min, True)
        self.change_ftp(max, False)
        print("FTP range changed")