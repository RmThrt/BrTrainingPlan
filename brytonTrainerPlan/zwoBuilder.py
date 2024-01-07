# -*- coding: utf-8 -*-
import csv
import os
from enum import Enum


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


class RowBuilder:
    def __init__(self, row, index, last_row_index) -> None:
        self.dict = row
        self.index = index
        self.last_row_index = last_row_index

        self.workoutDefineType = self.define_type_of_row()
        self.check_row_validity()
        self.build_Row()

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
            if self.dict[RowField.low_power.value] == 0 and self.dict[RowField.high_power.value] == 0:
                return WorkoutRowType.FreeRide
            return WorkoutRowType.SteadyState
        else:
            return WorkoutRowType.IntervalsT

    def check_row_validity(self):
        if self.dict[RowField.power_unit.value] != '%' and self.dict[RowField.power_unit.value] != 'Max' and self.dict[RowField.power_unit.value] != '':
            raise ValueError("Power unit must be in percentage")
        if self.dict[RowField.power_unit2.value] != '%' and self.dict[RowField.power_unit2.value] != 'Max' and self.dict[RowField.power_unit2.value] != '':
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
        if self.workoutDefineType == WorkoutRowType.Warmup:
            return self.build_warmup_row()

    def power_convert(self, power) -> str:
        if float(power) < 2:
            raise ValueError(
                "Power must be greater than 2,as it has to be in percentage")
        if float(power) == 2000 and self.workoutDefineType == WorkoutRowType.IntervalsT:
            return str(300/100)
        return str(float(power)/100)

    def add_cadence(self):
        if self.dict[RowField.cadence.value] != '':
            return " CadenceLow=" + self.dict[RowField.cadence.value] + " CadenceHigh=" + self.dict[RowField.cadence.value]
        return ''

    def build_common_parts(self):
        str = "Duration=" + self.dict[RowField.time_in_seconds.value]
        str += " PowerLow=" + \
            self.power_convert(self.dict[RowField.low_power.value])
        str += " PowerHigh=" + \
            self.power_convert(self.dict[RowField.high_power.value])
        str += self.add_cadence()
        str += "/>"
        return str

    def build_cooldown_row(self):
        # <Cooldown Cadence CadenceHigh CadenceLow CadenceResting Duration EndAtRoadTime Pace pace Power PowerHigh PowerLow replacement_prescription replacement_verb units Zone>
        #     <gameplayevent camera duration timeoffset type>
        #     <TextEvent Duration message TimeOffset timeoffset>
        #     <textevent distoffset duration message mssage textscale timeoffset y>
        #     <TextNotification duration font_size text timeOffset x y>

        return "<Cooldown " + self.build_common_parts()

    def build_intervals_t_row(self):
        # <IntervalsT Cadence CadenceHigh CadenceLow CadenceResting FlatRoad OffDuration OffPower OnDuration OnPower OverUnder pace PowerOffHigh PowerOffLow PowerOffZone PowerOnHigh PowerOnLow PowerOnZone Repeat units>
        #     <TextEvent Duration message TimeOffset timeoffset>
        #     <textevent distoffset duration message mssage textscale timeoffset y>
        #     <TextNotification duration font_size text timeOffset x y>

        if self.dict[RowField.cadence.value] != '' and self.dict[RowField.cadence2.value] != '' and self.dict[RowField.cadence.value] != self.dict[RowField.cadence2.value]:
            raise ValueError(
                'There is different cadences for 1st and 2nd part of interval, this is not handled')
        str = "<IntervalsT " + "Repeat=" + self.dict[RowField.number_of_time.value] + \
            " OnDuration=" + self.dict[RowField.time_in_seconds.value] + \
            " OffDuration=" + self.dict[RowField.time_in_seconds2.value] + \
            " PowerOnLow=" + self.power_convert(self.dict[RowField.low_power.value]) + \
            " PowerOnHigh=" + self.power_convert(self.dict[RowField.high_power.value]) + \
            " PowerOffLow=" + self.power_convert(self.dict[RowField.low_power2.value]) + \
            " PowerOffHigh=" + \
            self.power_convert(self.dict[RowField.high_power2.value])
        str += self.add_cadence()
        str += "/>"
        return str

    def build_maxEffort_row(self):
        # <MaxEffort Duration>
        
        return "<MaxEffort Duration=" + self.dict[RowField.time_in_seconds.value]

    def build_ramp_row(self):
        # <Ramp Cadence CadenceResting Duration pace Power PowerHigh PowerLow show_avg>
        #     <textevent distoffset duration message mssage textscale timeoffset y>

        return "<Ramp " + self.build_common_parts()

    def build_steady_state_row(self):
        # <SteadyState Cadence CadenceHigh CadenceLow CadenceResting Duration FailThresholdDuration Forced_Performance_Test forced_performance_test NeverFails OffPower pace Power PowerHigh PowerLow ramptest replacement_prescription replacement_verb show_avg Target Text units Zone>
        #     <TextEvent Duration message TimeOffset timeoffset>
        #     <textevent distoffset duration message mssage textscale timeoffset y>

        str =  "<SteadyState " + "Duration=" + self.dict[RowField.time_in_seconds.value] + \
            " Power=" + self.power_convert(self.dict[RowField.low_power.value])
        str += self.add_cadence()
        str += "/>"
        return str

    def build_warmup_row(self):
        # <Warmup Cadence CadenceHigh CadenceLow CadenceResting Duration pace Power PowerHigh PowerLow Quantize replacement_prescription replacement_verb Text units Zone>
        #     <TextEvent Duration message TimeOffset timeoffset>
        #     <textevent distoffset duration message mssage textscale timeoffset y>

        return "<Warmup " + self.build_common_parts()


class ZwoBuilder:

    def __init__(self, csv_path=None) -> None:
        self.title, _ = os.path.splitext(os.path.basename(csv_path))

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

        last_row_index = 0

        index = 0

        for row in csv_content:
            rowBuilder = RowBuilder(
                row, index, last_row_index)
            workoutRowType = rowBuilder.define_type_of_row()
            index += 1
            duration = row[' Duration']
            print('DURATION :' + row[' Duration'])

        title = self.title
        description = "Workout generated from csv file"
        self.zwo_content += self.start_zwo_file(title, description)

        self.zwo_content += self.end_zwo_file()
        return self.zwo_content
