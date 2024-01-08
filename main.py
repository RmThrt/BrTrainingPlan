import os
from pathlib import Path
import webbrowser
from brytonTrainerPlan.zwoBuilder import ZwoBuilder
from brytonTrainerPlan.workoutInjector import BrowserManager
from brytonTrainerPlan.utils import prepare_output_folder, search_in_google, slugify, zwo_to_csv
from brytonTrainerPlan.workoutExtractor.workoutExtractor import ZwitBrowserManager,  ZwiftWorkoutsBrowser
from tqdm import tqdm


headless = True
csvFolder = "outputs_examples/"
directory = "./examples/zwo_workouts/"
Zwift = False
csvToZwo = True
training_plans = ["active-offseason", "back-to-fitness", "build-me-up", "build-me-up-lite", "crit-crusher", "dirt-destroyer", "fast-track-fitness",
                  "fondo", "ftp-builder", "gran-fondo", "gravel-grinder", "pebble-pounder", "singletrack-slayer", "tt-tuneup", "zwift-101-cycling", "zwift-racing-plan"]

directory = 'csv_to_zwo_inputs'
csv_filenames = [f for f in Path(directory).rglob('*.csv')]


if csvToZwo:
    outputs_zwo = 'outputs_zwo'
    zwift_link_file = 'zwift_links.txt'
    zwift_link_file_path = os.path.join(outputs_zwo, zwift_link_file)
    if not os.path.exists(outputs_zwo):
        os.mkdir(outputs_zwo)
    open(zwift_link_file_path, 'w')
    for filename in tqdm(csv_filenames):
        csv_file_path = str(filename.absolute())
        zwoBuildertest = ZwoBuilder(csv_file_path, training_plan=filename.parent.name)
        workout = zwoBuildertest.build_zwo_workout()
        zwo_file_path = zwoBuildertest.write_zwo_file(
            outputs_zwo)

        link = search_in_google('zwift_' + zwoBuildertest.get_title())
        with open(zwift_link_file_path, 'a') as f:
            f.write(link + '; file:///' + csv_file_path +
                    '; file:///' + zwo_file_path + '\n')
        # webbrowser.open(link)


elif Zwift:
    for training_plan in training_plans:
        print("training_plan:", training_plan)
        zwift_url = "https://whatsonzwift.com/workouts/" + training_plan
        zwiftBrowserManager = ZwitBrowserManager(headless, zwift_url)
        output_folder = directory + '/' + training_plan
        prepare_output_folder(output_folder, training_plan, zwift_url)

        zwiftWorkoutsBrowser = ZwiftWorkoutsBrowser(
            zwiftBrowserManager.getPage(), output_folder)
        workout_count = zwiftWorkoutsBrowser.get_workouts_count()
        print("workout_count:", workout_count)
        for i in tqdm(range(workout_count), total=workout_count):
            zwwiftWorkoutsLocators = zwiftWorkoutsBrowser.extract_workouts(i)

        zwiftBrowserManager.dispose()
        del zwiftBrowserManager

else:
    if not os.path.exists(csvFolder):
        os.mkdir(csvFolder)

    zwo_filenames = [f for f in os.listdir(directory) if f.endswith('.zwo')]

    threads = []

    browserManager = BrowserManager(headless)

    index = 0

    for filename in zwo_filenames:
        index += 1
        print(filename + ' - file ' + str(index) + '/' +
              str(len(zwo_filenames)) + ' injecting...')

        filename_without_ext = slugify(os.path.splitext(filename)[0])
        csvName = "tmp/" + filename_without_ext + ".csv"
        zwo_to_csv(directory, filename, csvName)

        workout_df = prepare_workout_dict(csvName)
        WorkoutCreator(filename_without_ext, workout_df,
                       browserManager.getPage())

        print(filename + ' - file ' + str(index) + '/' +
              str(len(zwo_filenames)) + ' injected')

    browserManager.dispose()
