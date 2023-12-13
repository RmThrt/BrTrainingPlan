import os
import threading
from WorkoutInjector import WorkoutCreator, BrowserManager
from workoutExtractor.WorkoutExtractor import ZwitBrowserManager, ZwiftWorkoutExtractor, ZwiftWorkoutsBrower
from prepareWorkout import prepare_workout_dict

threaded = False
headless = False
csvFolder = "tmp/"
directory = "./inputs/KoM_Builder/"
Zwift = True

def process_file(filename, page):
    filename_without_ext = os.path.splitext(filename)[0]
    csvName = "tmp/" + filename_without_ext + ".csv"
    os.system("python ./brytonTrainerPlan/zwoparse.py " + directory + filename + " -f 266 -k 71 -t csv -o " + csvName)

    workout_df = prepare_workout_dict(csvName)
    WorkoutCreator(filename_without_ext, workout_df, page)
    
    
if Zwift:
    
    
    zwiftBrowserManager = ZwitBrowserManager(headless, "https://whatsonzwift.com/workouts/build-me-up")
    zwiftWorkoutsBrower =  ZwiftWorkoutsBrower(zwiftBrowserManager.getPage())
    zwwiftWorkoutsLocators = zwiftWorkoutsBrower.get_workouts(0)
    zwiftBrowserManager.getPage().pause()
    
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