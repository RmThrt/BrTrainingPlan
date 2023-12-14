import json
import re
import os
from openai import OpenAI

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

class WorkoutLine:
    def __init__(self, number_of_time,  time_in_seconds, low_power, high_power, power_unit, cadence):
        self.number_of_time = number_of_time
        self.time_in_seconds = time_in_seconds
        self.low_power = low_power
        self.high_power = high_power
        self.power_unit = power_unit
        self.cadence = cadence
        
        print("workout line : ", str(self.number_of_time), str(self.time_in_seconds), str(self.low_power), str(self.high_power), str(self.power_unit), str(self.cadence))
    
class Workout:
    def __init__(self, title, description, workout):
        self.title = title
        self.description = description
        self.workout = workout
        
    
    def build_workout(self):
        self.workoutLines = []
        for workoutLine in self.workout:
            print ("line: " , workoutLine)
            number_of_time = self.get_number_of_time(workoutLine)
            cadence = self.get_rpm(workoutLine)
            time_in_seconds =  self.get_time_in_seconds(workoutLine)
            low_power , high_power, power_unit  = self.get_power(workoutLine)
            self.workoutLines.append(WorkoutLine(number_of_time, time_in_seconds,low_power, high_power, power_unit, cadence))
                       
    def get_number_of_time(self, workoutLine):
        searches = re.search(r'^(\d+)x ', workoutLine)
        if searches is not None:
            return searches.group(1)
        else:
            return 1
        
    def get_rpm(self, workoutLine):
        searches = re.search(r'(\d+)rpm', workoutLine)
        if searches is not None:
            return searches.group(1)
        else:
            return 0

    def get_power(self, workoutLine):
        searches = re.findall(r'from (\d+) to (\d+)(%|W)|(\d+)(%|W)|(free ride)', workoutLine)
        if len(searches) > 0:
            for i, _ in enumerate(searches):
                if searches[i][0] != '':
                    searches[i] = (searches[i][0], searches[i][1], searches[i][2])
                    continue
                elif searches[i][3] != '':
                    searches[i] =  (searches[i][3], searches[i][3], searches[i][4])
                    continue
                elif searches[i][5] != '':
                    searches[i] =  (0, 0, 0)
                    continue

        return searches
        
    def get_time_in_seconds(self, workoutLine, isInterval=False):
        
        rslt_time_in_min = re.findall(r'(\d+)min', workoutLine)
        
        if  len(rslt_time_in_min) > 0 :
            return [int(numeric_string) *60 for numeric_string in rslt_time_in_min] 
        else:
            return  [int(numeric_string) for numeric_string in re.findall(r'(\d+)sec', workoutLine)]
        


    
def return_regex_int_value(regex, workoutLine):
    searches = re.findall(regex, workoutLine)
    if len(searches) > 0 :
        return int(searches[0]) if len(searches) < 2 else int(searches[0]), int(searches[1])
    else:
        return None
        
class OpenAIWorkoutExtractor:
    
    def __init__(self):
        config_data = self.read_json_file('config.json')
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=config_data['openai_key'],
        )
    
    def read_json_file(self, file_path):
        with open(file_path, 'r') as json_file:
            
            data = json.load(json_file)
        return data
    
    def ask_openai_convert_workout_to_zwo(self, workout):
        self.ask_to_openai("Convert the following workout to zwo format: " + "\n".join(workout))
        
    def ask_to_openai(self, question):
        response = self. client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
            model="gpt-3.5-turbo",
        )
        print(response)
        return response

        
        
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
        WorkoutLines = []
        for i in range(count):
            div= div_list.nth(i)
            array_html.append(div.evaluate("el => el.innerHTML"))
            array_text.append(div.text_content())
        wk = Workout('test','test', array_text)
        wk.build_workout()
        
        print(array_text)
        zwoFileContent = OpenAIWorkoutExtractor().ask_openai_convert_workout_to_zwo(array_text)
        print("zxoFileContent: " , zwoFileContent)

    
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