# from playwright.sync_api import sync_playwright


# brytonActiveWorkoutUrl="https://active.brytonsport.com/workout" 

# with sync_playwright() as p:
#     # Make sure to run headed.
#     browser = p.chromium.launch(headless=False)

#     # Setup context however you like.
#     context = browser.new_context() # Pass any options
#     context.route('**/*', lambda route: route.continue_())

#     # Pause the page, and start recording manually.
#     page = context.new_page()
#     context = browser.new_context()
#     page = context.new_page()
#     page.goto(brytonActiveWorkoutUrl)
#     page.goto("https://active.brytonsport.com/")
#     # page.get_by_placeholder("Email Address").click()
#     page.get_by_placeholder("Email Address").fill("remi10_7@hotmail.fr")
#     # page.get_by_placeholder("Email Address").press("Tab")
#     # page.get_by_role("button", name="Log In", exact=True).click()
#     # page.get_by_role("button", name="OK", exact=True).click()
#     # page.get_by_placeholder("Password").click()
#     page.get_by_placeholder("Password").fill("remithrt")
#     page.get_by_role("button", name="Log In", exact=True).click()
#     page.get_by_text("Workout").click()
#     page.get_by_role("button", name="Add").click()
#     page.pause()