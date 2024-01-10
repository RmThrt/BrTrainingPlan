import csv
import os
import re
import numpy as np
import re

from playwright.sync_api import sync_playwright

from brytonTrainerPlan.utils import increment_filename_if_necessary, slugify

warmupFlag = r"^Warm Up$"
activityFlag = r"^Work$"
recoveryFlag = r"^Recovery$"
coolDownFlag = r"^Cool Down$"

col_type="type"
col_duration="duration"
col_min_power="min_power"
col_max_power="max_power"
col_cadence="cadence"

verbose = False



class ZwitBrowserManager:
    def __init__(self, headless, timeout = 5000):
        self.headless = headless
        self.setup_browser(timeout)
       
        
    def goto(self, url):
        if verbose: print("page loaded")
        self.page.goto(url, timeout=60000)
        try:
            self.reject_all_cookies()
        except:
            pass


    def setup_browser(self, timeout):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)  
        if verbose: print("browser launched")
        self.context = self.browser.new_context()
        if verbose: print("context created")
        self.page = self.context .new_page()
        self.context.set_default_timeout(timeout)
        if verbose: print("page created")
        
    def reject_all_cookies(self,timeout = 20):
        self.page.frame_locator("#gdpr-consent-notice").get_by_role("button", name="Reject All").click(timeout)
        self.page.frame_locator("#gdpr-consent-notice").get_by_role("button", name="Reject").click(timeout)

    def get_training_plans(self):
        training_plans = []
        for div in  self.page.locator('.card').all():
            sport_card = div.locator('.card-sports')
            training_plan_name = div.locator('.card-title').text_content(timeout = 5000)
            if sport_card.locator('.flaticon-bike').count() > 0:
                training_plans.append(training_plan_name)
            else: 
                print('warn - training plan : \"' + training_plan_name + '\" is a running training plan, not converted')
        training_plans = [x.replace("+", "plus").replace("L'Etape", 'l-etape')  for x in training_plans]
        training_plans = [slugify(x) for x in training_plans]
        training_plans = [x.replace("4wk-prudential-ride-london-prl-prep", "4wk-prl-prep")\
                        .replace('zwift-academy-2016','zwift-academy'\
                        .replace('ride-on-for-world-bicycle-relief-watopia-1-lap-tt-plan', 'ride-on-for-world-bicycle-relief-watopia-1lap-tt-plan')\
                        .replace('mattias-thyrs-unstructured-workouts', 'mattias-thyr-unstructured-workouts')\
                        .replace('leandro-messineos-poison-dart-frog-intervals', 'leandro-messineo-poison-dart-frog-intervals')\
                        .replace('dig-deep-coaching-3-week-grand-tour-2018', 'dig-deep-coaching-3-week-grand-tour')\
                        .replace('classics-and-climbing', 'classics-climbing')\
                        )  for x in training_plans]
        return training_plans

    def getPage(self): 
        return self.page 

    def dispose(self):
        self.context.close()    
        self.browser.close()
        self.playwright.stop()

class WorkoutLine:
    def __init__(self, number_of_time,  time_in_seconds,  low_power, high_power,power_unit, cadence, time_in_seconds2, low_power2, high_power2,  power_unit2, cadence2):
        self.number_of_time = number_of_time
        self.time_in_seconds = time_in_seconds
        self.low_power = low_power
        self.high_power = high_power
        self.power_unit = power_unit
        self.cadence = cadence
        self.time_in_seconds2 = time_in_seconds2
        self.low_power2 = low_power2
        self.high_power2 = high_power2
        self.power_unit2 = power_unit2
        self.cadence2 = cadence2
        
        if verbose: print("workout line : ", 
                str(self.number_of_time),
                str(self.time_in_seconds),
                str(self.low_power),
                str(self.high_power),
                str(self.cadence2),
                str(self.time_in_seconds2),
                str(self.low_power2),
                str(self.high_power2),
                str(self.power_unit),
                str(self.power_unit2),
                str(self.cadence)
            )
        
    def __eq__(self, other): 
        if not isinstance(other, WorkoutLine):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.number_of_time == other.number_of_time and \
            self.time_in_seconds == other.time_in_seconds and \
            self.low_power == other.low_power and \
            self.high_power == other.high_power and \
            self.power_unit == other.power_unit and \
            self.cadence == other.cadence and \
            self.time_in_seconds2 == other.time_in_seconds2 and \
            self.low_power2 == other.low_power2 and \
            self.high_power2 == other.high_power2 and \
            self.power_unit2 == other.power_unit2 and \
            self.cadence2 == other.cadence2

    
class Workout:
    def __init__(self, title, description, workout):
        self.title = title
        self.description = description
        self.workout = workout
        
        
    
    def build_workout(self):
        self.workoutLines = []
        for workoutLine in self.workout:
            t = self.build_workout_line(workoutLine)
            self.workoutLines.append(t)

    def build_workout_line(self, workoutLine):
        if verbose: print ("line: " , workoutLine)
        number_of_time = self.get_number_of_time(workoutLine)
        cadences = self.get_rpm(workoutLine)
        times =  self.get_time_in_seconds(workoutLine)
        powers = self.get_power(workoutLine)
        return WorkoutLine(number_of_time, times[0],powers[0][0], powers[0][1], powers[0][2], cadences[0] if len(cadences) > 0 else None,times[1] if len(times) >1 else None,  powers[1][0] if len(powers) >1 else None, powers[1][1]if len(powers) >1 else None, powers[1][2]if len(powers) >1 else None,  cadences[1]if len(cadences) >1 else None)


    def build_csv(self, output_folder):
        header : [str] = ["description"]
        if len(self.workoutLines) > 0:
            for key, value  in vars(self.workoutLines[0]).items():
                header.append(key)

        filename = increment_filename_if_necessary(output_folder + "/" + self.title + ".csv")


        with open(filename, mode='w', newline='') as csv_file:
            # Create a CSV writer object
            csv_writer = csv.writer(csv_file)

            # Write the header row
            csv_writer.writerow(header)

            first_row = True

            if len(self.workoutLines) == 0:
                csv_writer.writerow([self.description])

            # Write the data rows
            for obj in self.workoutLines:
                desc = ""
                if first_row :   
                    desc = self.description
                    first_row = False
                else :
                    desc= ""
                test = np.concatenate((np.array([desc]), np.array([getattr(obj, attr) for attr in header[1:]])), axis = None)
                csv_writer.writerow(test) # from 1 index because 0 is description
       

    def get_number_of_time(self, workoutLine):
        searches = re.search(r'^(\d+)x ', workoutLine)
        if searches is not None:
            return searches.group(1)
        else:
            return 1 
        
    def get_rpm(self, workoutLine):
        searches = re.findall(r'(\d+)rpm', workoutLine) 
        if  len(searches) > 0 :
            return [int(numeric_string) for numeric_string in searches] 

        return [None]

    def get_power(self, workoutLine):
        searches = re.findall(r'from (\d+) to (\d+)(%|W)|(\d+)(%|W)|(free ride)|(MAX)', workoutLine)
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
                elif searches[i][6] != '':
                    searches[i] =  (2000,2000,'Max')
                    continue

        return searches
        
    def get_time_in_seconds(self, workoutLine, isInterval=False):
        matches = re.findall(r'((\d+)hr )?((\d+)min )?((\d+)sec)?', workoutLine)
        matches =  [t for t in matches if any(t)]
        match1 = matches[0]
      

        hours_to_secs =  int(match1[1]) * 3600 if len(match1) > 3 and match1[1] != '' else 0 
        mins_to_secs = int(match1[3]) * 60 if len(match1) > 3 and match1[3] != ''  else 0 
        secs = int(match1[5]) if len(match1) > 5 and match1[5] != '' else 0

        duration1 = hours_to_secs + mins_to_secs + secs

        if len(matches) > 1:
            match2 = matches[1]

            hours_to_secs =  int(match2[1]) * 3600 if len(match2) > 3 and match2[1] != '' else 0 
            mins_to_secs = int(match2[3]) * 60 if len(match2) > 5 and match2[3] != '' else 0 
            secs = int(match2[5]) if len(match2) > 5 and match2[5] != '' else 0

            duration2 = hours_to_secs + mins_to_secs + secs
            return [duration1, duration2]
        
        return [duration1]


    
def return_regex_int_value(regex, workoutLine):
    searches = re.findall(regex, workoutLine)
    if len(searches) > 0 :
        return int(searches[0]) if len(searches) < 2 else int(searches[0]), int(searches[1])
    else:
        return None

        
        
class ZwiftWorkoutsBrowser:
    def __init__(self, page, output_folder):
        self.page = page
        self.output_folder = output_folder  


    def get_workouts_count(self):
        return self.page.locator("div > main > section > section:nth-child(2) > article > div > div > div > .flaticon-bike").count()
        
    def extract_workouts(self, index):  
        article_locator = self.page.locator("div > main > section > section:nth-child(2) > article").nth(index)
        workout = article_locator.locator(".one-third")
        try:
            workout_prefix_title = slugify(article_locator.locator(".breadcrumbs > a").nth(1).text_content(timeout=2000)) + "_" 
        except:
            workout_prefix_title = ''
        workout_title = workout_prefix_title + slugify(article_locator.locator("h4").text_content())
        if article_locator.locator('.flaticon-run').count() > 0: 
            print('warn - workout : \"' + workout_title + '\" is a running workout, not converted')
            return 
        workout_description = self.page.locator("div > main > section > section:nth-child(2) > article").nth(index).locator(".two-thirds > p").nth(0).text_content()
        div_list = workout.locator("div")
        count = div_list.count()
        array_html = []
        array_text = []
        for i in range(count):
            div= div_list.nth(i)
            array_html.append(div.evaluate("el => el.innerHTML"))
            array_text.append(div.text_content())
        
        wk = Workout(workout_title, workout_description, array_text)
        wk.build_workout()
        wk.build_csv(self.output_folder)
        if verbose: print(array_text)

