import json
import re
from playwright.sync_api import sync_playwright


brytonActiveWorkoutUrl="https://active.brytonsport.com/" 

warmupFlag = r"^Warm Up$"
activityFlag = r"^Work$"
recoveryFlag = r"^Recovery$"
coolDownFlag = r"^Cool Down$"

sectionCount = -1


def run(playwright) -> None:
    browser = playwright.firefox.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    login(page)
    create_workout(page, "test")

    # # ---------------------
    # context.close()
    while True:  # Infinite loop to prevent the script from finishing
        pass
    

def create_workout(page, name):
    
    page.get_by_text("Workout").click()    
    page.wait_for_timeout(3000)
    page.get_by_role("button", name="Add").click()
    page.wait_for_timeout(1000)
    # try:
    #     page.locator("#WObutton-list").click()
    # except: 
    #     print("already in workout page")
    # page.locator("#WObutton-list").click()
    # page.get_by_role("button", name="Add").click()
    
    
    page.get_by_role("paragraph").filter(has_text=re.compile(r"bsWO.*", re.IGNORECASE)).click()
    page.get_by_placeholder(re.compile(r"bsWO.*", re.IGNORECASE)).fill(name)
    
    try:
        add_new_section(page, warmupFlag)
        set_duration(page, "0:10:0")   
        change_ftp_range(page, "25", "55")
        
        add_new_section(page, activityFlag)
        set_duration(page, "0:10:0")   
        change_ftp_range(page, "25", "55")
        
        add_new_section(page, activityFlag)
        set_duration(page, "0:11:0")   
        change_ftp_range(page, "26", "56")

        add_new_section(page, coolDownFlag)
        set_duration(page, "0:12:0")   
        change_ftp_range(page, "27", "57")
        
    except Exception as e: print(e)
    
    page.get_by_text("Save").click()
    
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
    
    

with sync_playwright() as playwright:
    run(playwright)


