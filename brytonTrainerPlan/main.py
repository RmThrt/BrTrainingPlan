import os
from workoutInjector import  BrowserManager
from utils import prepare_output_folder, slugify, zwo_to_csv
from workoutExtractor.workoutExtractor import ZwitBrowserManager,  ZwiftWorkoutsBrowser
from tqdm import tqdm


headless = False
csvFolder = "outputs_examples/"
directory = "./examples/zwo_workouts/"
Zwift = True
training_plans = ["active-offseason", "back-to-fitness", "build-me-up", "build-me-up-lite", "crit-crusher", "dirt-destroyer", "fast-track-fitness","fondo", "ftp-builder", "gran-fondo", "gravel-grinder", "pebble-pounder", "singletrack-slayer", "tt-tuneup", "zwift-101-cycling", "zwift-racing-plan"]


    
    
if Zwift:
    for training_plan in training_plans:
        print("training_plan:", training_plan)
        zwift_url =  "https://whatsonzwift.com/workouts/" + training_plan
        zwiftBrowserManager = ZwitBrowserManager(headless,zwift_url)
        output_folder = 'outputs/' + training_plan
        prepare_output_folder(output_folder, training_plan, zwift_url)

        zwiftWorkoutsBrowser =  ZwiftWorkoutsBrowser(zwiftBrowserManager.getPage(), output_folder)
        workout_count = zwiftWorkoutsBrowser.get_workouts_count()
        print("workout_count:", workout_count)
        for i in tqdm(range(workout_count), total=workout_count):
            zwwiftWorkoutsLocators = zwiftWorkoutsBrowser.extract_workouts(i)
        
        zwiftBrowserManager.dispose()
        del zwiftBrowserManager
    
else :    
    if not os.path.exists(csvFolder):
        os.mkdir(csvFolder)

    zwo_filenames = [f for f in os.listdir(directory) if f.endswith('.zwo')]

    threads = []

    browserManager = BrowserManager(headless)

    index = 0

    for filename in zwo_filenames:
        index += 1
        print(filename + ' - file ' + str(index) + '/' + str(len(zwo_filenames)) + ' injecting...')

        filename_without_ext = slugify(os.path.splitext(filename)[0])
        csvName = "tmp/" + filename_without_ext + ".csv"
        zwo_to_csv(directory, filename, csvName)
        
        workout_df = prepare_workout_dict(csvName)
        WorkoutCreator(filename_without_ext, workout_df, browserManager.getPage())

        print( filename + ' - file ' + str(index) + '/' + str(len(zwo_filenames)) + ' injected')

    browserManager.dispose()


