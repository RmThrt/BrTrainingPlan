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

class BrowserManager:
    brytonActiveWorkoutUrl = "https://active.brytonsport.com/"
    
    def __init__(self, headless):
        self.headless = headless
        
    def setup_browser(self, playwright):
        browser = playwright.firefox.launch(headless=self.headless)
        context = browser.new_context()
        page = context.new_page()
        self.login(page)
        return browser, context, page
    
    
    def read_json_file(self, file_path):
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        return data
    
    def login(self, page):
        page.goto(self.brytonActiveWorkoutUrl)
        config_data = self.read_json_file('config.json')
        page.get_by_placeholder("Email Address").fill(config_data['mail'])
        page.get_by_placeholder("Password").fill(config_data['pwd'])
        page.get_by_role("button", name="Log In", exact=True).click()



    def close_browser(self, browser, context):
        context.close()
        browser.close()

class WorkoutCreator:
    sectionCount = -1
    
    def __init__(self, title, workout_df, headless):
        self.title = title
        self.workout_df = workout_df
        with sync_playwright() as playwright:
            manager = BrowserManager(headless)
            browser, context, self.page = manager.setup_browser(playwright)
            self.create_workout()
            manager.close_browser(browser, context)

    def create_workout(self):
        self.page.get_by_text("Workout").click()    
        self.page.wait_for_timeout(3000)
        self.page.get_by_role("button", name="Add").click()
        self.page.wait_for_timeout(1000)
        self.page.get_by_role("paragraph").filter(has_text=re.compile(r"bsWO.*", re.IGNORECASE)).click()
        self.page.get_by_placeholder(re.compile(r"bsWO.*", re.IGNORECASE)).fill(self.title)
        
        for index, row in tqdm(self.workout_df.iterrows(), total=self.workout_df.shape[0]):
            self.add_new_section(str(row["type"]))
            self.set_duration(str(row["duration"]))   
            self.change_ftp_range(str(row["min_power"]), str(row["max_power"]))
        
        self.page.get_by_text("Save").click()
        self.page.locator("#dlg-body").get_by_text("Don't show this again.").click()
        self.page.get_by_role("button", name="OK").click()

    def add_new_section(self, regex):
        self.page.locator("div").filter(has_text=re.compile(regex)).locator("div").click()
        self.sectionCount += 1 
        self.page.wait_for_timeout(500)

    def set_duration(self, duration):
        self.page.get_by_role("paragraph").filter(has_text="Distance").click()
        self.page.get_by_role("listitem").filter(has_text="Time").click()
        duration_locator = self.page.locator("div > .wo-itv-content-frame > .wo-itv-content > .wo-itv-duration-frame")
        self.locate(duration_locator, duration)

    def change_ftp(self, ftp, isLowRange):
        base_selector = ".wo-itv-content-frame > .wo-itv-content > .wo-itv-range-frame > .wo-range-low"
        value_selector = " > .wo-range-low-val " if isLowRange else " > .wo-range-high-val "
        ftp_locator = self.page.locator(base_selector + value_selector)
        self.locate(ftp_locator, ftp)
            
    def locate(self, locator, value):
        locator_placeholder = locator.get_by_placeholder(re.compile(r".*", re.IGNORECASE))
        if self.sectionCount >= 1:
            locator.nth(self.sectionCount).click()
            locator_placeholder.nth(self.sectionCount).fill(value)
            locator_placeholder.nth(self.sectionCount).press("Enter")
        else:
            locator.click()
            locator_placeholder.fill(value)
            locator_placeholder.press("Enter")

    def change_ftp_range(self, min, max):
        self.change_ftp(min, True)
        self.change_ftp(max, False)



        