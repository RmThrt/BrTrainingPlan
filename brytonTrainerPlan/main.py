import os
import threading
from WorkoutInjector import WorkoutCreator
from prepareWorkout import prepare_workout_dict

threaded = False
headless = True
    
def process_file(filename):
    filename_without_ext = os.path.splitext(filename)[0]
    os.system("python ./brytonTrainerPlan/zwoparse.py " + directory + filename + " -f 266 -k 71 -t csv")

    workout_df = prepare_workout_dict(filename_without_ext + ".csv")
    WorkoutCreator(filename_without_ext, workout_df, headless)
    print(filename_without_ext + ' workout injected')

directory = "C:/dev/Perso/BrTrainingPlan/KoM_Builder/"
zwo_filenames = [f for f in os.listdir(directory) if f.endswith('.zwo')]

threads = []

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
        process_file(filename)
        print( filename + ' workout injected')
    