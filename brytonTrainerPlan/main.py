import json
import re
from playwright.sync_api import sync_playwright


brytonActiveWorkoutUrl="https://active.brytonsport.com/" 


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
    
    add_warmup(page)
   

    # page.get_by_text("Save").click()
    
def add_warmup(page):
    page.locator("div").filter(has_text=re.compile(r"^Warm Up$")).locator("div").click()
    page.wait_for_timeout(500)
    set_duration(page, "0:10:0")   
    change_ftp_range(page, "25", "55")

def set_duration(page, duration):
    
    default_duration = "0:50:0"
    page.get_by_text("Distance Distance Time").click()
    page.get_by_text("Time").click()
    page.get_by_role("paragraph").filter(has_text=re.compile(r"^"+default_duration+"$")).click()
    page.get_by_placeholder(default_duration).click()
    page.get_by_placeholder(default_duration).fill(duration)     
    page.get_by_placeholder(default_duration).press("Enter")     
    
def change_ftp(page, ftp_to_replace, ftp):
    page.get_by_text(ftp_to_replace, exact=True).click()
    page.get_by_placeholder(ftp_to_replace).fill(ftp)
    page.get_by_placeholder(ftp_to_replace).press("Enter")

def change_ftp_range(page, min, max):
    change_ftp(page, "20", min)
    change_ftp(page, "40", max)
    
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


