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


class ZwitBrowserManager:
    def __init__(self, headless, workouts_url):
        self.headless = headless
        self.workouts_url = workouts_url
        
        self.setup_browser()
        self.page.goto(workouts_url)
        self.reject_all_cookies()
        
            
    def setup_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.firefox.launch(headless=self.headless)
        self.context = self.browser.new_context()
        self.page = self.context .new_page()
        
    def reject_all_cookies(self):
        self.page.frame_locator("#gdpr-consent-notice").get_by_role("button", name="Reject All").click()
        self.page.frame_locator("#gdpr-consent-notice").get_by_role("button", name="Reject").click()

    def getPage(self): 
        return self.page 

    def close_browser(self, browser, context):
        context.close()
        
        browser.close()
        
    def dispose(self):
        self.close_browser(self.browser, self.context)
        
class ZwiftWorkoutsBrower:
    def __init__(self, page):
        self.page = page
        
    def get_workouts_locators(self):
        locators = self.page.get_by_role("article")
        element = self.page.locator("div > main > section > section:nth-child(2) > article").nth(1).locator(".one-third").evaluate("el => el.innerHTML") 
        print(element)
        locator = locators.first()
        locator.textContent()
        print(locator.get_by_role("h4").text_content())
        
    def get_workouts(self, index):
        workout = self.page.locator("div > main > section > section:nth-child(2) > article").nth(index).locator(".one-third")
        div_list = workout.locator("div")
        count = div_list.count()
        array_html = []
        array_text = []
        for i in range(count):
            div= div_list.nth(i)
            array_html.append(div.evaluate("el => el.innerHTML"))
            array_text.append(div.text_content())
        print(array_text)

    
class ZwiftWorkoutExtractor:
    sectionCount = -1   
    
    def __init__(self,  index, workout_df, page):
        self.page = page
        self.index = index
        self.workout_df = workout_df
        self.extract_workout()


    def extract_workout(self):
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
        # page.locator(".wo-itv-repeat-div > .wo-itv-content-frame > .wo-itv-content > .wo-itv-duration-frame > div:nth-child(2)")
        duration_locator = self.page.locator("#work-" + str(self.sectionCount + 1) + " > .wo-itv-repeat-div > .wo-itv-content-frame > .wo-itv-content > .wo-itv-duration-frame > div:nth-child(2)")
        self.locate(self.page.get_by_role("paragraph").filter(has_text=re.compile(r"^0:50:0$", re.IGNORECASE)), self.page.get_by_placeholder(re.compile(r"^0:50:0$", re.IGNORECASE)), duration)
        self.locate(duration_locator,duration_locator, duration)

    def change_ftp(self, ftp, isLowRange):
        base_selector = ".wo-itv-content-frame > .wo-itv-content > .wo-itv-range-frame > .wo-range-low"
        value_selector = " > .wo-range-low-val " if isLowRange else " > .wo-range-high-val "
        ftp_locator = self.page.locator(base_selector + value_selector)
        self.locate(ftp_locator, None, ftp)

    def locate(self, locator, locator_placeholder_param, value):
        # Wait for 20 milliseconds to ensure all elements on the page are fully loaded
        self.page.wait_for_timeout(20)

        # If locator_placeholder_param is not provided, find a placeholder using a regular expression
        locator_placeholder = locator_placeholder_param
        if locator_placeholder is None:
            locator_placeholder = locator.get_by_placeholder(re.compile(r".*", re.IGNORECASE))

        # If sectionCount is greater than or equal to 1 and locator_placeholder_param is None
        # perform a series of actions on the nth element of locator and locator_placeholder
        if self.sectionCount >= 1 and locator_placeholder_param is None:
            locator.nth(self.sectionCount).click()
            locator_placeholder.nth(self.sectionCount).click(timeout=5000)
            locator_placeholder.nth(self.sectionCount).fill(value)
            locator_placeholder.nth(self.sectionCount).press("Enter")
        else:
            # If the conditions are not met, simply click the locator and locator_placeholder
            # fill it with the value, and press "Enter"
            locator.click()
            locator_placeholder.click(timeout=5000)
            locator_placeholder.fill(value)
            locator_placeholder.press("Enter")

    def change_ftp_range(self, min, max):
        self.change_ftp(min, True)
        self.change_ftp(max, False)
        #print("FTP range changed")