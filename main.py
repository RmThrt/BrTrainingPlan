import os
import sys
import threading
import getopt
from pathlib import Path
from brytonTrainerPlan.zwoBuilder import ZwoBuilder
from brytonTrainerPlan.workoutInjector import BrowserManager, WorkoutCreator
from brytonTrainerPlan.utils import count_files, prepare_output_folder, search_in_google, slugify, zwo_to_csv
from brytonTrainerPlan.workoutExtractor.workoutExtractor import ZwitBrowserManager,  ZwiftWorkoutsBrowser
from tqdm import tqdm

from brytonTrainerPlan.prepareWorkout import prepare_workout_dict

from queue import Queue

jobs = Queue()

def build_job():
    while True:
        value = jobs.get()
        func = value[0]
        args = value[1:]
        func(*args)
        print(value)
        jobs.task_done()


def csv_to_zwo(filename,outputs_zwo, zwift_link_file_path ):
    parent_directory = filename.parent.name
    output_training_plan = outputs_zwo + '/' + parent_directory
    if not os.path.exists(output_training_plan):
        try:
            os.mkdir(output_training_plan)
        except Exception as e:
            if e.winerror == 183:
                pass
    csv_file_path = str(filename.absolute())
    zwoBuildertest = ZwoBuilder(
        csv_file_path, training_plan='')#filename.parent.name)
    zwoBuildertest.build_zwo_workout()
    zwo_file_path = zwoBuildertest.write_zwo_file(
        output_training_plan)

    link = search_in_google('zwift_' + zwoBuildertest.get_title())
    with open(zwift_link_file_path, 'a') as f:
        f.write(link + '; file:///' + csv_file_path +
                '; file:///' + zwo_file_path + '\n')
        

def extract_training_plan(training_plan,outputfolder, headless):
    zwift_url = "https://whatsonzwift.com/workouts/" + training_plan
    training_plan_folder = outputfolder + '/' + training_plan
    
    zwiftBrowserManager = ZwitBrowserManager(
    headless)

    zwiftBrowserManager.goto(zwift_url)
    try:
        prepare_output_folder(training_plan_folder,
                            training_plan, zwift_url)
    
        already_scrapped = False
        zwiftWorkoutsBrowser = ZwiftWorkoutsBrowser(
            zwiftBrowserManager.getPage(), training_plan_folder)
        workout_count = zwiftWorkoutsBrowser.get_workouts_count()

        if os.path.exists(training_plan_folder):
            training_plan_files_count = count_files(training_plan_folder)
            if training_plan_files_count > workout_count:
                print('training plan already scrapped')
                already_scrapped = True
        
        if not already_scrapped:
            for i in tqdm(range(workout_count), total=workout_count, desc='extraction of: ' + zwift_url):
                zwiftWorkoutsBrowser.extract_workouts(i)
    except Exception as e:
        print('ERROR : ' + str(e))

    finally:
        zwiftBrowserManager.dispose()
        del zwiftBrowserManager

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
    assert not ((websiteUrlToGetTrainingPlans != '') and  (len(training_plans) >
                                                   0)), "please choose between website-url-to-get-training-plans and training-plans, cannot be used in the same time"

    if csvToZwo:
        csv_filenames = [f for f in Path(inputfolder).rglob('*.csv')]
        outputs_zwo = outputfolder
        zwift_link_file = 'zwift_links.txt'
        zwift_link_file_path = os.path.join(outputs_zwo, zwift_link_file)
        if not os.path.exists(outputs_zwo):
            os.mkdir(outputs_zwo)
        open(zwift_link_file_path, 'w')
        for filename in tqdm(csv_filenames):
            x= threading.Thread(target=csv_to_zwo, args=(filename,outputs_zwo, zwift_link_file_path ))
            x.start()

    elif parseZwift:
        if websiteUrlToGetTrainingPlans != '':
            zwiftBrowserManager = ZwitBrowserManager(
            headless)

            zwiftBrowserManager.goto(websiteUrlToGetTrainingPlans)
            training_plans = zwiftBrowserManager.get_training_plans()

            zwiftBrowserManager.dispose()
            del zwiftBrowserManager
        
        
        for training_plan in training_plans:
            jobs.put((extract_training_plan, training_plan, outputfolder, headless))

        for i in range(5):
            worker = threading.Thread(target=build_job)
            worker.start()

        print("waiting for queue to complete", jobs.qsize(), "tasks")
        jobs.join()
        print("all done")

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
