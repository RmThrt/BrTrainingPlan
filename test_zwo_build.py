
import os
import subprocess
from brytonTrainerPlan.utils import search_in_google
from brytonTrainerPlan.zwoBuilder import RowBuilder, RowField, WorkoutRowType, ZwoBuilder
from pathlib import Path

zwo_content_expected = []

zwoBuilderChainBreaker = ZwoBuilder(
    'examples/zwo_workouts/zwo_parsed_to_csv_workouts/chain_breaker.csv')
zwoBuilderAmalgam = ZwoBuilder('examples/csv_files_scrapped/Amalgam.csv')

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

    assert zwoBuilderChainBreaker.start_zwo_file(
        title, description) == expected_result
        


def test_end_zwo_file():
    expected_result = "</workout>\n\
    </workout_file>"

    assert zwoBuilderChainBreaker.end_zwo_file() == expected_result


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
    result = zwoBuilderAmalgam.build_zwo_workout()
    # assert result == expected_result


def test_define_type_of_row():

    row = dict({'description': '', 'number_of_time': '1', 'time_in_seconds': '600', 'low_power': '40', 'high_power': '75',
                'power_unit':  '%', 'cadence': '', 'time_in_seconds2': '', 'low_power2': '', 'high_power2': '', 'power_unit2': '',
                'cadence2': ''})
    assert RowBuilder(row=row, index=0, last_row_index=0).define_type_of_row(
    ) == WorkoutRowType.Warmup
    assert RowBuilder(row=row, index=10, last_row_index=10).define_type_of_row(
    ) == WorkoutRowType.Cooldown
    assert RowBuilder(
        row=row, index=9, last_row_index=10).define_type_of_row() == WorkoutRowType.Ramp

    row['high_power'] = row['low_power']
    assert RowBuilder(row=row, index=9, last_row_index=10).define_type_of_row(
    ) == WorkoutRowType.SteadyState

    row['low_power2'] = '45'
    row['high_power2'] = '45'
    row['power_unit2'] = '%'
    assert RowBuilder(row=row, index=9, last_row_index=10).define_type_of_row(
    ) == WorkoutRowType.IntervalsT


def test_row_builder():
    row = dict({'description': '', 'time_in_seconds': '600', 'low_power': '40', 'high_power': '40',
                'power_unit':  '%', 'cadence': '', 'time_in_seconds2': '', 'low_power2': '', 'high_power2': '', 'power_unit2': '',
                'cadence2': ''})    

    time_in_seconds = "600"
    lowPower = "0.4"
    highPower = "0.4"

    # SteadyState
    row_calculated = RowBuilder(
        row=row, index=9, last_row_index=10).build_Row()
    assert row_calculated == "<SteadyState Duration=\"" + time_in_seconds +\
        "\" Power=\"" + lowPower + "\" />"

    highPower = "0.75"
    row[RowField.high_power.value] = str(float(highPower) * 100)

    # warmup
    assert RowBuilder(row=row, index=0, last_row_index=0).build_Row() == "<Warmup Duration=\"" + time_in_seconds +\
        "\" PowerLow=\"" + lowPower + \
        "\" PowerHigh=\"" + highPower + "\" />"
    # cooldown
    assert RowBuilder(row=row, index=10, last_row_index=10).build_Row() == "<Cooldown Duration=\"" + time_in_seconds +\
        "\" PowerLow=\"" + lowPower + \
        "\" PowerHigh=\"" + highPower + "\" />"

    # Ramp
    row_calculated = RowBuilder(
        row=row, index=9, last_row_index=10).build_Row()
    assert row_calculated == "<Ramp Duration=\"" + time_in_seconds +\
        "\" PowerLow=\"" + lowPower + \
        "\" PowerHigh=\"" + highPower + "\" />"

    # Max Effort
    row[RowField.power_unit.value] = 'Max'

    row_calculated = RowBuilder(
        row=row, index=9, last_row_index=10).build_Row()
    assert row_calculated == "<MaxEffort Duration=\"" + time_in_seconds + "\" />"

    row[RowField.power_unit.value] = '%'

    # IntervalT
    number_of_time = '5'
    time_in_seconds2 = "6001"
    lowPower2 = "0.5"
    highPower2 = "0.76"
    cadence = '100'

    row[RowField.number_of_time.value] = number_of_time
    row[RowField.time_in_seconds2.value] = time_in_seconds2
    row[RowField.low_power2.value] = str(float(lowPower2) * 100)
    row[RowField.high_power2.value] = str(float(highPower2) * 100)

    row_calculated = RowBuilder(
        row=row, index=9, last_row_index=10).build_Row()
    assert row_calculated == "<IntervalsT " + "Repeat=\"" + number_of_time + \
        "\" OnDuration=\"" + time_in_seconds + \
        "\" OffDuration=\"" + time_in_seconds2 + \
        "\" PowerOnLow=\"" + lowPower + \
        "\" PowerOnHigh=\"" + highPower + \
        "\" PowerOffLow=\"" + lowPower2 + \
        "\" PowerOffHigh=\"" + highPower2 + \
        "\" />"

    # with cadence
    row[RowField.cadence.value] = cadence

    row_calculated = RowBuilder(
        row=row, index=9, last_row_index=10).build_Row()
    assert row_calculated == "<IntervalsT " + "Repeat=\"" + number_of_time + \
        "\" OnDuration=\"" + time_in_seconds + \
        "\" OffDuration=\"" + time_in_seconds2 + \
        "\" PowerOnLow=\"" + lowPower + \
        "\" PowerOnHigh=\"" + highPower + \
        "\" PowerOffLow=\"" + lowPower2 + \
        "\" PowerOffHigh=\"" + highPower2 + \
        "\" Cadence=\"" + cadence + \
        "\" CadenceLow=\"" + cadence + \
        "\" CadenceHigh=\"" + cadence + \
        "\" />"
    

def test_build_zwo_workout():
    directory = 'csv_to_zwo_inputs'
    csv_filenames = [f for f in Path(directory).rglob('*.csv')]


    for filename in csv_filenames:
        zwoBuildertest = ZwoBuilder(filename)
        workout = zwoBuildertest.build_zwo_workout()
        zwoBuildertest.write_zwo_file('outputs_zwo')
        # search_in_google('zwift ' + zwoBuildertest.get_title())


    # assert workout == ''

