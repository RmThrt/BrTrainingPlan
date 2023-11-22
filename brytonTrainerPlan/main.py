import os
import threading
from WorkoutInjector import WorkoutCreator, BrowserManager
from prepareWorkout import prepare_workout_dict

threaded = False
headless = True
csvFolder = "tmp/"
directory = "./inputs/KoM_Builder/"


def process_file(filename, page):
    filename_without_ext = os.path.splitext(filename)[0]
    csvName = "tmp/" + filename_without_ext + ".csv"
    os.system("python ./brytonTrainerPlan/zwoparse.py " + directory + filename + " -f 266 -k 71 -t csv -o " + csvName)

    workout_df = prepare_workout_dict(csvName)
    WorkoutCreator(filename_without_ext, workout_df, page)
    print(filename_without_ext + ' workout injected')
    
    

if not os.path.exists(csvFolder):
    os.mkdir(csvFolder)

zwo_filenames = [f for f in os.listdir(directory) if f.endswith('.zwo')]

threads = []

browserManager = BrowserManager(headless)

if threaded:
    for filename in zwo_filenames:
        print('Injecting ' + filename + '...')
        
        thread = threading.Thread(target=process_file, args=(filename,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
else:
    for filename in zwo_filenames:
        print('Injecting ' + filename + '...')
        process_file(filename, browserManager.getPage())

browserManager.dispose()