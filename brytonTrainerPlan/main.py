from urllib.request import Request, urlopen
import os
import threading
from WorkoutInjector import WorkoutCreator, BrowserManager
from workoutExtractor.WorkoutExtractor import ZwitBrowserManager, ZwiftWorkoutExtractor, ZwiftWorkoutsBrowser
from prepareWorkout import prepare_workout_dict
from tqdm import tqdm

threaded = False
headless = True
csvFolder = "tmp/"
directory = "./inputs/KoM_Builder/"
Zwift = True
training_plan = "active-offseason"

def prepare_output_folder(output_folder, training_plan):
    os.makedirs(output_folder) if not os.path.exists(output_folder) else None

    req = Request(zwift_url)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    req.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')
    req.add_header('Accept-Encoding', 'none')
    req.add_header('Accept-Language', 'en-US,en;q=0.8')
    req.add_header('Connection', 'keep-alive')
    cnt = str(urlopen(req).read())
    f = open(output_folder + "/" + training_plan + ".html", 'w', encoding='utf-8')
    f.write(cnt)
    f.close

def process_file(filename, page):
    filename_without_ext = os.path.splitext(filename)[0]
    csvName = "tmp/" + filename_without_ext + ".csv"
    os.system("python ./brytonTrainerPlan/zwoparse.py " + directory + filename + " -f 266 -k 71 -t csv -o " + csvName)

    workout_df = prepare_workout_dict(csvName)
    WorkoutCreator(filename_without_ext, workout_df, page)
    
    
if Zwift:
    zwift_url =  "https://whatsonzwift.com/workouts/" + training_plan
    zwiftBrowserManager = ZwitBrowserManager(headless,zwift_url)
    output_folder = 'outputs/' + training_plan
    prepare_output_folder(output_folder, training_plan)

    ZwiftWorkoutsBrowser =  ZwiftWorkoutsBrowser(zwiftBrowserManager.getPage(), output_folder)
    for i in tqdm(range(100), total=100):
        zwwiftWorkoutsLocators = ZwiftWorkoutsBrowser.extract_workouts(i)
    
    zwiftBrowserManager.dispose()
    
else :    
    if not os.path.exists(csvFolder):
        os.mkdir(csvFolder)

    zwo_filenames = [f for f in os.listdir(directory) if f.endswith('.zwo')]

    threads = []

    browserManager = BrowserManager(headless)

    index = 0

    if threaded:
        for filename in zwo_filenames:
            index += 1
            print(filename + ' - file ' + str(index) + '/' + str(len(zwo_filenames)) + ' injecting...')
            
            thread = threading.Thread(target=process_file, args=(filename,))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()
    else:
        for filename in zwo_filenames:
            index += 1
            print(filename + ' - file ' + str(index) + '/' + str(len(zwo_filenames)) + ' injecting...')
            process_file(filename, browserManager.getPage())
            print( filename + ' - file ' + str(index) + '/' + str(len(zwo_filenames)) + ' injected')

    browserManager.dispose()


