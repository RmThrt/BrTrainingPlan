import os
import sys
import time
import getopt
from pathlib import Path
from brytonTrainerPlan.zwoBuilder import ZwoBuilder
from brytonTrainerPlan.workoutInjector import BrowserManager, WorkoutCreator
from brytonTrainerPlan.utils import count_files, prepare_output_folder, search_in_google, slugify, zwo_to_csv
from brytonTrainerPlan.workoutExtractor.workoutExtractor import ZwitBrowserManager,  ZwiftWorkoutsBrowser
from tqdm import tqdm

from brytonTrainerPlan.prepareWorkout import prepare_workout_dict


def main(argv):

    inputfolder = ''
    outputfolder = ''
    headless = True
    csvToZwo = False
    injectInBryton = False
    parseZwift = False
    training_plans = []
    websiteUrlToGetTrainingPlans = ''
    # training_plans = ["active-offseason", "back-to-fitness", "build-me-up", "build-me-up-lite", "crit-crusher", "dirt-destroyer", "fast-track-fitness",
    #                 "fondo", "ftp-builder", "gran-fondo", "gravel-grinder", "pebble-pounder", "singletrack-slayer", "tt-tuneup", "zwift-101-cycling", "zwift-racing-plan"]
    opts, args = getopt.getopt(argv, "hi:o:", ["ifolder=", "ofolder=", "csv-to-zwo", "headless=",
                               "inject-in-bryton", "parse-zwift", "training-plan=", "website-url-to-get-training-plans="])
    for opt, arg in opts:
        if opt == '-h':
            print(
                'main.py --parse-zwift --training-plans active-offseason --headless false -o <outputfolder>')
            print('main.py --parse-zwift --website-url-to-get-training-plans https://whatsonzwift.com/workouts --headless true -o <outputfolder>')
            print('main.py --csv-to-zwo -i <inputfolder> -o <outputfolder>')
            print('main.py --inject-in-bryton --headless false -i <inputfolder>')
            sys.exit()
        elif opt in ("-i", "--ifolder"):
            inputfolder = arg
            print('Input folder is ', inputfolder)
        elif opt in ("-o", "--ofolder"):
            outputfolder = arg
            print('Output folder is ', outputfolder)
        elif opt == '--csv-to-zwo':
            csvToZwo = True
        elif opt == '--headless':
            headless = arg == 'true' or arg == 'True' or arg == 'TRUE' or arg == '1'
        elif opt == '--inject-in-bryton':
            injectInBryton = True
        elif opt == '--parse-zwift':
            parseZwift = True
        elif opt == '--website-url-to-get-training-plans':
            websiteUrlToGetTrainingPlans = arg
        elif opt == '--training-plans':
            training_plans = [arg]

    assert csvToZwo ^ injectInBryton ^ parseZwift, "please choose between csv-to-zwo, --inject-in-bryton, or --parse-zwift, it cannot be used in the same time"
    assert (websiteUrlToGetTrainingPlans != '') ^ (len(training_plans) >
                                                   0), "please choose between website-url-to-get-training-plans and training-plans, cannot be used in the same time"

    if csvToZwo:
        csv_filenames = [f for f in Path(inputfolder).rglob('*.csv')]
        outputs_zwo = outputfolder
        zwift_link_file = 'zwift_links.txt'
        zwift_link_file_path = os.path.join(outputs_zwo, zwift_link_file)
        if not os.path.exists(outputs_zwo):
            os.mkdir(outputs_zwo)
        open(zwift_link_file_path, 'w')
        for filename in tqdm(csv_filenames):
            csv_file_path = str(filename.absolute())
            zwoBuildertest = ZwoBuilder(
                csv_file_path, training_plan=filename.parent.name)
            zwoBuildertest.build_zwo_workout()
            zwo_file_path = zwoBuildertest.write_zwo_file(
                outputs_zwo)

            link = search_in_google('zwift_' + zwoBuildertest.get_title())
            with open(zwift_link_file_path, 'a') as f:
                f.write(link + '; file:///' + csv_file_path +
                        '; file:///' + zwo_file_path + '\n')

    elif parseZwift:
        zwiftBrowserManager = ZwitBrowserManager(
            headless)
        if websiteUrlToGetTrainingPlans != '':

            zwiftBrowserManager.goto(websiteUrlToGetTrainingPlans)
            training_plans = zwiftBrowserManager.get_training_plans()

        
        for training_plan in training_plans:
            zwift_url = "https://whatsonzwift.com/workouts/" + training_plan
            print("training_plan:", zwift_url)
            training_plan_folder = outputfolder + '/' + training_plan

            zwiftBrowserManager.goto(zwift_url)
            try:
                prepare_output_folder(training_plan_folder,
                                  training_plan, zwift_url)
            

                zwiftWorkoutsBrowser = ZwiftWorkoutsBrowser(
                    zwiftBrowserManager.getPage(), training_plan_folder)
                workout_count = zwiftWorkoutsBrowser.get_workouts_count()

                if os.path.exists(training_plan_folder):
                    training_plan_files_count = count_files(training_plan_folder)
                    if training_plan_files_count > workout_count:
                        print('training plan already scrapped')
                        continue

                print("workout_count:", workout_count)
                for i in tqdm(range(workout_count), total=workout_count):
                    zwiftWorkoutsBrowser.extract_workouts(i)
            except Exception as e:
                print('ERROR : ' + str(e))
                continue


        zwiftBrowserManager.dispose()
        del zwiftBrowserManager

    elif injectInBryton:
        if not os.path.exists('tmp'):
            os.mkdir('tmp')

        zwo_filenames = [f for f in os.listdir(
            inputfolder) if f.endswith('.zwo')]

        browserManager = BrowserManager(headless)

        index = 0
        for filename in zwo_filenames:
            index += 1
            print(filename + ' - file ' + str(index) + '/' +
                  str(len(zwo_filenames)) + ' injecting...')

            filename_without_ext = slugify(os.path.splitext(filename)[0])
            csvName = os.path.join('tmp', filename_without_ext + ".csv")
            zwo_to_csv(inputfolder, filename, csvName)

            workout_df = prepare_workout_dict(csvName)
            WorkoutCreator(filename_without_ext, workout_df,
                           browserManager.getPage())

            print(filename + ' - file ' + str(index) + '/' +
                  str(len(zwo_filenames)) + ' injected')

        browserManager.dispose()


class Logger(object):
    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stdout = sys.stdout
        sys.stdout = self

    def __del__(self):
        sys.stdout = self.stdout
        self.file.close()

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    def flush(self):
        self.file.flush()


if __name__ == "__main__":
    sys.stdout = Logger("message.log", "a")
    sys.stderr = Logger("message.log", "a")

    main(sys.argv[1:])
