import pytest 
import csv

from brytonTrainerPlan.zwoBuilder import ZwoBuilder

zwo_content_expected = []

zwoBuilder = ZwoBuilder('examples/zwo_workouts/zwo_parsed_to_csv_workouts/chain_breaker.csv')

with open('examples/zwo_workouts/Chain_Breaker.zwo') as f:
        zwo_content_expected = f.read().split('\n')


def test_start_zwo_file():
    title = "Chain Breaker"
    description = ""
    expected_result = "<workout_file>\n\
    <author></author>\n\
    <name>" + title + "</name>\n\
    <description>" + description + "</description>\n\
    <sportType>bike</sportType>\n\
    <tags>\n\
    </tags>\n\
    <workout>" 

    assert zwoBuilder.start_zwo_file(title, description) == expected_result  

def test_end_zwo_file():
    expected_result = "</workout>\n\
    </workout_file>"

    assert zwoBuilder.end_zwo_file() == expected_result 

def test_build_zwo_workout():
    title = "chain_breaker"
    description = "Workout generated from csv file"
    expected_result = "<workout_file>\n\
    <author></author>\n\
    <name>" + title + "</name>\n\
    <description>" + description + "</description>\n\
    <sportType>bike</sportType>\n\
    <tags>\n\
    </tags>\n\
    <workout></workout>\n\
    </workout_file>" 
    result = zwoBuilder.build_zwo_workout()
    assert result == expected_result
