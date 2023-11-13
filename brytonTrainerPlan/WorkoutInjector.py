import json
import re
from tqdm import tqdm
from playwright.sync_api import sync_playwright

        
        
brytonActiveWorkoutUrl="https://active.brytonsport.com/" 

warmupFlag = r"^Warm Up$"
activityFlag = r"^Work$"
recoveryFlag = r"^Recovery$"
coolDownFlag = r"^Cool Down$"

col_type="type"
col_duration="duration"
col_min_power="min_power"
col_max_power="max_power"
col_cadence="cadence"

sectionCount = -1  

def run(playwright,title, workout_df, headless) -> None:
    global sectionCount
    sectionCount = -1  
    browser = playwright.firefox.launch(headless=headless)
    context = browser.new_context()
    page = context.new_page()
    login(page)
    create_workout(page, title, workout_df)
    
    context.close()
    browser.close()

def create_workout(page, name, workout_df):
    
    page.get_by_text("Workout").click()    
    page.wait_for_timeout(3000)
    page.get_by_role("button", name="Add").click()
    page.wait_for_timeout(1000)
    
    page.get_by_role("paragraph").filter(has_text=re.compile(r"bsWO.*", re.IGNORECASE)).click()
    page.get_by_placeholder(re.compile(r"bsWO.*", re.IGNORECASE)).fill(name)
    
    count_rows = workout_df.shape[0]

    
    for index, row in tqdm(workout_df.iterrows(), total=count_rows):
        
        add_new_section(page, str(row[col_type]))
        set_duration(page, str(row[col_duration]))   
        change_ftp_range(page, str(row[col_min_power]), str(row[col_max_power]))
    
    
    page.get_by_text("Save").click()
    page.locator("#dlg-body").get_by_text("Don't show this again.").click()
    page.get_by_role("button", name="OK").click()
    

    
def add_new_section(page, regex):
    global sectionCount
    page.locator("div").filter(has_text=re.compile(regex)).locator("div").click()
    sectionCount += 1 
    page.wait_for_timeout(500)


def set_duration(page, duration):
    
    page.get_by_role("paragraph").filter(has_text="Distance").click()
    page.get_by_role("listitem").filter(has_text="Time").click()
    duration_locator = page.locator("div > .wo-itv-content-frame > .wo-itv-content > .wo-itv-duration-frame")
    
    if sectionCount >= 1:
        duration_locator.nth(sectionCount).click()
        duration_locator.get_by_placeholder(re.compile(r".*", re.IGNORECASE)).nth(sectionCount).fill(duration)     
        duration_locator.get_by_placeholder(re.compile(r".*", re.IGNORECASE)).nth(sectionCount).press("Enter")   
    else:
        duration_locator.click()
        duration_locator.get_by_placeholder(re.compile(r".*", re.IGNORECASE)).fill(duration)     
        duration_locator.get_by_placeholder(re.compile(r".*", re.IGNORECASE)).press("Enter")     
    
def change_ftp(page, ftp, isLowRange):
    range =".wo-itv-content-frame > .wo-itv-content > .wo-itv-range-frame > .wo-range-low"
    range +=  " > .wo-range-low-val " if isLowRange else " > .wo-range-high-val "
    
    ftp_locator = page.locator(range)
    
    if sectionCount >= 1:
        ftp_locator.nth(sectionCount).click()
        ftp_locator.get_by_placeholder(re.compile(r".*", re.IGNORECASE)).nth(sectionCount).fill(ftp)
        ftp_locator.get_by_placeholder(re.compile(r".*", re.IGNORECASE)).nth(sectionCount).press("Enter")
    else:
        ftp_locator.click()
        ftp_locator.get_by_placeholder(re.compile(r".*", re.IGNORECASE)).fill(ftp)
        ftp_locator.get_by_placeholder(re.compile(r".*", re.IGNORECASE)).press("Enter")

def change_ftp_range(page, min, max):
    change_ftp(page, min, True)
    change_ftp(page, max, False)
    
def login(page):
    
    page.goto(brytonActiveWorkoutUrl)
    
    def read_json_file(file_path):
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        return data

    config_data = read_json_file('config.json')

    page.get_by_placeholder("Email Address").fill(config_data['mail'])

    page.get_by_placeholder("Password").fill(config_data['pwd'])
    page.get_by_role("button", name="Log In", exact=True).click()
    

def inject_workout(title, workout_df, headless): 
    with sync_playwright() as playwright:
        run(playwright, title, workout_df, headless)



