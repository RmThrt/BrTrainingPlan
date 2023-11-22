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
        self.headless = headless
        
        self.setup_browser()
        
            
    def setup_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.firefox.launch(headless=self.headless)
        self.context = self.browser.new_context()
        self.page = self.context .new_page()
        self.login()
        self.go_to_workout_page()

    def read_json_file(self, file_path):
        with open(file_path, 'r') as json_file:
            
            data = json.load(json_file)
        return data
    
    def getPage(self): 
        return self.page 

    def login(self):
        print("Login...")
        self.page.goto(brytonActiveWorkoutUrl)
        config_data = self.read_json_file('config.json')
        self.page.get_by_placeholder("Email Address").fill(config_data['mail'])
        self.page.get_by_placeholder("Password").fill(config_data['pwd'])
        self.page.get_by_role("button", name="Log In", exact=True).click()
        
    def go_to_workout_page(self):
        self.page.get_by_text("Workout").click()    
        self.page.wait_for_timeout(3000)


    def close_browser(self, browser, context):
        context.close()
        browser.close()
        
    def dispose(self):
        self.close_browser(self.browser, self.context)


class WorkoutCreator:
    sectionCount = -1   
    
    def __init__(self,  title, workout_df, page):
        self.page = page
        self.title = title
        self.workout_df = workout_df
        self.create_workout()


    def create_workout(self):
        self.page.get_by_role("button", name="Add").click()
        
        self.page.wait_for_timeout(200)

        self.page.get_by_role("paragraph").filter(has_text=re.compile(r"bsWO.*", re.IGNORECASE)).click()
        self.page.get_by_placeholder(re.compile(r"bsWO.*", re.IGNORECASE)).fill(self.title)
        
        for index, row in tqdm(self.workout_df.iterrows(), total=self.workout_df.shape[0]):
            self.add_new_section(str(row[col_type]))
            self.set_duration(str(row[col_duration]))   
            
            #self.page.wait_for_timeout(3000)
        
        self.save_workout()

        
    def save_workout(self):
        self.page.get_by_text("Save").click()
        # self.page.locator("#dlg-body").get_by_text("Don't show this again.").click()
        self.page.get_by_role("button", name="OK").click()

    def add_new_section(self, regex):
        self.page.locator("div").filter(has_text=re.compile(regex)).locator("div").click()
        self.sectionCount += 1 
        #self.page.wait_for_timeout(500)

    def set_duration(self, duration):
        self.page.get_by_role("paragraph").filter(has_text="Distance").click()
        self.page.get_by_role("listitem").filter(has_text="Time").click()
        duration_locator = self.page.locator("div > .wo-itv-content-frame > .wo-itv-content > .wo-itv-duration-frame")
        
        self.locate(self.page.get_by_role("paragraph").filter(has_text=re.compile(r"^0:50:0$", re.IGNORECASE)), self.page.get_by_placeholder(re.compile(r"^0:50:0$", re.IGNORECASE)), duration)

    def change_ftp(self, ftp, isLowRange):
        base_selector = ".wo-itv-content-frame > .wo-itv-content > .wo-itv-range-frame > .wo-range-low"
        value_selector = " > .wo-range-low-val " if isLowRange else " > .wo-range-high-val "
        ftp_locator = self.page.locator(base_selector + value_selector)
        self.locate(ftp_locator, None, ftp)

    def locate(self, locator, locator_placeholder_param, value):
        self.page.wait_for_timeout(20)
        locator_placeholder = locator_placeholder_param
        if( locator_placeholder == None):
            locator_placeholder = locator.get_by_placeholder(re.compile(r".*", re.IGNORECASE))
        
        if self.sectionCount >= 1 and locator_placeholder_param == None:
            locator.nth(self.sectionCount).click()
            locator_placeholder.nth(self.sectionCount).click(timeout=5000)
            locator_placeholder.nth(self.sectionCount).fill(value)
            locator_placeholder.nth(self.sectionCount).press("Enter")
        else:
            locator.click()
            locator_placeholder.click(timeout=5000)
            locator_placeholder.fill(value)
            locator_placeholder.press("Enter")

    def change_ftp_range(self, min, max):
        self.change_ftp(min, True)
        self.change_ftp(max, False)
        #print("FTP range changed")