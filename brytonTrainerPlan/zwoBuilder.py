# -*- coding: utf-8 -*-
import csv
import os
from enum import Enum
from bs4 import BeautifulSoup as bs


class RowField(Enum):
    description = "description"
    number_of_time = "number_of_time"
    time_in_seconds = "time_in_seconds"
    low_power = "low_power"
    high_power = "high_power"
    power_unit = "power_unit"
    cadence = "cadence"
    time_in_seconds2 = "time_in_seconds2"
    low_power2 = "low_power2"
    high_power2 = "high_power2"
    power_unit2 = "power_unit2"
    cadence2 = "cadence2"


class WorkoutRowType(Enum):
    Cooldown = "Cooldown"
    FreeRide = "FreeRide"
    IntervalsT = "IntervalsT"
    MaxEffort = "MaxEffort"
    Ramp = "Ramp"
    RestDay = "RestDay"
    SolidState = "SolidState"
    SteadyState = "SteadyState"
    Warmup = "Warmup"


def keyval(key, val):
    return key + "=\"" + val + "\" "


class RowBuilder:
    def __init__(self, row, index, last_row_index):
        if len(row) == 1 and row[RowField.description.value] != None:
            self.row_parsed = row[RowField.description.value]
            return
        self.dict = row
        self.index = index
        self.last_row_index = last_row_index

        self.workoutDefineType = self.define_type_of_row()
        self.check_row_validity()
        self.row_parsed = self.build_Row()

    def get_row(self):
        return self.row_parsed

    def define_type_of_row(self):

        if (self.dict[RowField.low_power2.value] == ''):
            if self.index == 0:
                return WorkoutRowType.Warmup
            if self.index == self.last_row_index:
                return WorkoutRowType.Cooldown
            if self.dict[RowField.power_unit.value] == 'Max':
                return WorkoutRowType.MaxEffort
            if self.dict[RowField.low_power.value] != self.dict[RowField.high_power.value]:
                return WorkoutRowType.Ramp
            if self.dict[RowField.low_power.value] == '0' and self.dict[RowField.high_power.value] == '0':
                return WorkoutRowType.FreeRide
            return WorkoutRowType.SteadyState
        else:
            return WorkoutRowType.IntervalsT

    def check_row_validity(self):
        valid_units = ['', '%', 'Max', '0', 'W']
        if self.dict[RowField.power_unit.value] not in valid_units:
            raise ValueError("Power unit must be in percentage")
        if self.dict[RowField.power_unit2.value] not in valid_units:
            raise ValueError("Power unit 2 must be in percentage")

    def build_Row(self):
        if self.workoutDefineType == WorkoutRowType.Cooldown:
            return self.build_cooldown_row()
        if self.workoutDefineType == WorkoutRowType.IntervalsT:
            return self.build_intervals_t_row()
        if self.workoutDefineType == WorkoutRowType.MaxEffort:
            return self.build_maxEffort_row()
        if self.workoutDefineType == WorkoutRowType.Ramp:
            return self.build_ramp_row()
        if self.workoutDefineType == WorkoutRowType.SteadyState:
            return self.build_steady_state_row()
        if self.workoutDefineType == WorkoutRowType.FreeRide:
            return self.build_free_ride_row()
        if self.workoutDefineType == WorkoutRowType.Warmup:
            return self.build_warmup_row()
        else:
            raise ValueError('cannot handle this row')

    def power_convert(self, power) -> str:
        if power == '0':
            return '0'
        if float(power) < 2:
            raise ValueError(
                "Power must be greater than 2,as it has to be in percentage")
        if float(power) == 2000 and self.workoutDefineType == WorkoutRowType.IntervalsT:
            return str(300/100)
        if self.dict[RowField.power_unit.value] == 'W':
            return power
        return str(float(power)/100)

    def add_cadence(self):
        cadences = ''
        if self.dict[RowField.cadence.value] != '':
            cadences += keyval("Cadence", self.dict[RowField.cadence.value])
            cadences += keyval("CadenceLow", self.dict[RowField.cadence.value])
            cadences += keyval("CadenceHigh",
                               self.dict[RowField.cadence.value])
        if self.dict[RowField.cadence2.value] != '':
            cadences += keyval("CadenceResting",
                               self.dict[RowField.cadence2.value])

        return cadences

    def add_power(self, intervals=False):
        powers = ''
        suffix = ['']
        on_off_suffix = ['']

        if self.dict[RowField.power_unit.value] == '0':
            return powers

        if self.dict[RowField.power_unit.value] == 'Max':
            return powers

        if intervals:
            suffix = ['', '2']
            on_off_suffix = ['On', 'Off']

        for i in range(len(on_off_suffix)):

            if self.dict[RowField.low_power.value + suffix[i]] == self.dict[RowField.high_power.value + suffix[i]]:
                powers += keyval(on_off_suffix[i] + "Power",  self.power_convert(
                    self.dict[RowField.low_power.value + suffix[i]]))
            else:
                powers += keyval("Power" + on_off_suffix[i] + "Low", self.power_convert(
                    self.dict[RowField.low_power.value + suffix[i]]))
                powers += keyval("Power" + on_off_suffix[i] + "High", self.power_convert(
                    self.dict[RowField.high_power.value + suffix[i]]))

        return powers

    def build_simple_row(self, workout_type):
        str = "<" + workout_type + " "
        str += keyval("Duration", self.dict[RowField.time_in_seconds.value])
        str += self.add_power()
        str += self.add_cadence()
        str += "/>"
        return str

    def build_cooldown_row(self):
        # <Cooldown Cadence CadenceHigh CadenceLow CadenceResting Duration EndAtRoadTime Pace pace Power PowerHigh PowerLow replacement_prescription replacement_verb units Zone>
        #     <gameplayevent camera duration timeoffset type>
        #     <TextEvent Duration message TimeOffset timeoffset>
        #     <textevent distoffset duration message mssage textscale timeoffset y>
        #     <TextNotification duration font_size text timeOffset x y>

        return self.build_simple_row(WorkoutRowType.Cooldown.value)

    def build_intervals_t_row(self):
        # <IntervalsT Cadence CadenceHigh CadenceLow CadenceResting FlatRoad OffDuration OffPower OnDuration OnPower OverUnder pace PowerOffHigh PowerOffLow PowerOffZone PowerOnHigh PowerOnLow PowerOnZone Repeat units>
        #     <TextEvent Duration message TimeOffset timeoffset>
        #     <textevent distoffset duration message mssage textscale timeoffset y>
        #     <TextNotification duration font_size text timeOffset x y>

        str = "<IntervalsT "
        str += keyval("Repeat", self.dict[RowField.number_of_time.value])
        str += keyval("OnDuration", self.dict[RowField.time_in_seconds.value])
        str += keyval("OffDuration",
                      self.dict[RowField.time_in_seconds2.value])
        str += self.add_power(True)
        str += self.add_cadence()
        str += "/>"
        return str

    def build_maxEffort_row(self):
        # <MaxEffort Duration>

        return self.build_simple_row(WorkoutRowType.MaxEffort.value)

    def build_ramp_row(self):
        # <Ramp Cadence CadenceResting Duration pace Power PowerHigh PowerLow show_avg>
        #     <textevent distoffset duration message mssage textscale timeoffset y>

        return self.build_simple_row(WorkoutRowType.Ramp.value)

    def build_steady_state_row(self):
        # <SteadyState Cadence CadenceHigh CadenceLow CadenceResting Duration FailThresholdDuration Forced_Performance_Test forced_performance_test NeverFails OffPower pace Power PowerHigh PowerLow ramptest replacement_prescription replacement_verb show_avg Target Text units Zone>
        #     <TextEvent Duration message TimeOffset timeoffset>
        #     <textevent distoffset duration message mssage textscale timeoffset y>

        return self.build_simple_row(WorkoutRowType.SteadyState.value)

    def build_warmup_row(self):
        # <Warmup Cadence CadenceHigh CadenceLow CadenceResting Duration pace Power PowerHigh PowerLow Quantize replacement_prescription replacement_verb Text units Zone>
        #     <TextEvent Duration message TimeOffset timeoffset>
        #     <textevent distoffset duration message mssage textscale timeoffset y>

        return self.build_simple_row(WorkoutRowType.Warmup.value)

    def build_free_ride_row(self):
        # <FreeRide Cadence CadenceHigh CadenceLow Duration FailThresholdDuration FlatRoad ftptest Power ramptest show_avg>
        #     <TextEvent Duration message TimeOffset timeoffset>
        #     <textevent distoffset duration message mssage textscale timeoffset y>

        return self.build_simple_row(WorkoutRowType.FreeRide.value)


class ZwoBuilder:

    def __init__(self, csv_path=None, training_plan ='') -> None:
        self.csv_path = csv_path
        self.title = training_plan + '_' + os.path.splitext(os.path.basename(csv_path))[0]

        self.csv_content = csv.DictReader(open(csv_path, newline='\n'))
        self.zwo_content = ""

    def start_zwo_file(self, title, description):
        return "<workout_file>\n\
    <author></author>\n\
    <name>" + title + "</name>\n\
    <description>" + description + "</description>\n\
    <sportType>bike</sportType>\n\
    <tags>\n\
    </tags>\n\
    <workout>"

    def end_zwo_file(self):
        return "</workout>\n\
    </workout_file>"

    def build_zwo_workout(self, csv_content=None):
        if csv_content is None:
            csv_content = self.csv_content

        title = self.title

        rows = list(csv_content)
        totalrows = len(rows)
        for i, row in enumerate(rows):
            try:
                if i == 0:
                    description = row[RowField.description.value].replace('&','&amp;').replace("<", "&lt;").replace(">", "&gt;")
                    self.zwo_content += self.start_zwo_file(title, description)

                rowBuilder = RowBuilder(
                    row, i, totalrows - 1)
                self.zwo_content += rowBuilder.get_row() + '\n'
            except Exception as e:
                print('title : ' + self.csv_path)
                print('row number  : ' + str(i))
                print('row: ' + str(row))
                raise e

        self.zwo_content += self.end_zwo_file()
        # soup = bs(self.zwo_content)  # make BeautifulSoup
        # self.zwo_content = soup.prettify()  # prettify the html
        return self.zwo_content

    def get_title(self):
        return self.title

    def write_zwo_file(self, folder):
        if not os.path.exists(folder):
            os.mkdir(folder)
        file_path = os.path.join(folder,  self.title + '.zwo')
        with open(file_path, 'w') as f:
            f.write(self.zwo_content)
        self.zwo_content
        return os.path.abspath(file_path)
