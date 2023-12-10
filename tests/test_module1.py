# from playwright.sync_api import sync_playwright


# url ="https://whatsonzwift.com/workouts/build-me-up#week-0-prep" 

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
#     page.goto(url)
#     page.frame_locator("#gdpr-consent-notice").get_by_role("button", name="Reject All").click()
#     page.frame_locator("#gdpr-consent-notice").get_by_role("button", name="Reject").click()
#     # page.get_by_role("article").nth(1).click()

#     page.pause()