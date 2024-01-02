import pytest 

from  brytonTrainerPlan.workoutExtractor.WorkoutExtractor import Workout, WorkoutLine

workout = ['5min free ride', '1min @ 85rpm, 100W', '1min @ 85rpm, 120W', '1min @ 85rpm, 140W', '1min @ 85rpm, 160W', '1min @ 85rpm, 180W', '1min @ 85rpm, 200W', '1min @ 85rpm, 220W', '1min @ 85rpm, 240W', '1min @ 85rpm, 260W', '1min @ 85rpm, 280W', '1min @ 85rpm, 300W', '1min @ 85rpm, 320W', '1min @ 85rpm, 340W', '1min @ 85rpm, 360W', '1min @ 85rpm, 380W', '1min @ 85rpm, 400W', '1min @ 85rpm, 420W', '1min @ 85rpm, 440W', '1min @ 85rpm, 460W', '1min @ 85rpm, 480W', '1min @ 85rpm, 500W', '1min @ 85rpm, 520W', '1min @ 85rpm, 540W', '1min @ 85rpm, 560W', '1min @ 85rpm, 580W', '1min @ 85rpm, 600W', '1min @ 85rpm, 620W', '1min @ 85rpm, 640W', '10min from 75 to 70W']
workout2 = ['10min from 25 to 75% FTP', '1x 30sec @ 95rpm, 95% FTP,30sec @ 85rpm, 50% FTP', '1x 30sec @ 105rpm, 105% FTP,30sec @ 85rpm, 50% FTP', '1x 30sec @ 115rpm, 115% FTP,30sec @ 85rpm, 50% FTP', '2min @ 85rpm, 50% FTP', '10min @ 90rpm, 90% FTP', '4min @ 85rpm, 55% FTP', '10min @ 80rpm, 90% FTP', '4min @ 85rpm, 55% FTP', '2min @ 90rpm, 90% FTP', '1min @ 70rpm, 90% FTP', '2min @ 90rpm, 90% FTP', '1min @ 70rpm, 90% FTP', '4min @ 100rpm, 90% FTP', '7min from 55 to 25% FTP']

wk = Workout('test','test', workout)

def test_time_extraction():
    assert wk.get_time_in_seconds('1min @ 85rpm, 100W') == [60]
    assert wk.get_time_in_seconds('5min free ride') == [300]
    assert wk.get_time_in_seconds('25sec @ 85rpm, 100W') == [25]
    assert wk.get_time_in_seconds('1hr 30min @ 95rpm, 73% FTP') == [ 3600+60*30]
    assert wk.get_time_in_seconds('1x 30sec @ 95rpm, 95% FTP,30sec @ 85rpm, 50% FTP') == [30, 30]
    assert wk.get_time_in_seconds('1x 30sec @ 95rpm, 95% FTP,40sec @ 85rpm, 50% FTP') == [30, 40]
    assert wk.get_time_in_seconds('1x 30sec @ 95rpm, 95% FTP,40sec @ 85rpm, 50% FTP') == [30, 40]
    assert wk.get_time_in_seconds('1x 30sec @ 95rpm, 95% FTP') == [30]
    assert wk.get_time_in_seconds('2hr @ 73% FTP') == [60*60*2]
    assert wk.get_time_in_seconds('8sec @ MAX') == [8]
    
    



def test_power_extraction():
    assert wk.get_power('1min @ 85rpm, 100W') == [( '100' , '100', 'W')]
    assert wk.get_power('1min @ 85rpm, from 0 to 15% FTP') == [('0', '15', '%')]
    assert wk.get_power('1x 1min @ 85rpm, from 0 to 15% FTP,1min @ 85rpm, from 0 to 15% FTP') == [('0', '15', '%'),('0', '15', '%')]
    assert wk.get_power('1x 1min @ 85rpm, from 0 to 15% FTP,1min @ 85rpm, from 7 to 18% FTP') == [('0', '15', '%', ),('7', '18', '%' )]
    assert wk.get_power('1min @ 85rpm, 100W') == [( '100' , '100', 'W')]
    assert wk.get_power('1min @ 85rpm, from 0 to 15% FTP') == [('0', '15', '%')]
    assert wk.get_power('1x 1min @ 85rpm, from 0 to 15% FTP,1min @ 85rpm, from 0 to 15% FTP') == [('0', '15', '%'),('0', '15', '%')]
    assert wk.get_power('1x 1min @ 85rpm, from 0 to 15% FTP,1min @ 85rpm, from 7 to 18% FTP') == [('0', '15', '%', ),('7', '18', '%' )]
    assert wk.get_power('5min free ride') ==  [(0, 0, 0)]
    assert wk.get_power('8sec @ MAX') == [(2000,2000,'Max')]


def test_rpm_extraction():
    assert wk.get_rpm('1min @ 85rpm, 100W') == [85]
    assert wk.get_rpm('1x 1min @ 85rpm, from 0 to 15% FTP,1min @ 85rpm, from 0 to 15% FTP') == [85, 85]
    assert wk.get_rpm('1hr 30min @ 95rpm, 73% FTP') == [95]
    assert wk.get_rpm('8sec @ MAX') == [None]


def test_workout_extraction():
    assert   wk.build_workout_line('1hr 30min @ 95rpm, 73% FTP') == WorkoutLine(1, 5400, '73', '73', '%', 95, None, None, None, None, None)
    assert   wk.build_workout_line('8sec @ MAX') == WorkoutLine(1, 8, 2000, 2000, 'Max', None, None, None, None, None, None)
    

 