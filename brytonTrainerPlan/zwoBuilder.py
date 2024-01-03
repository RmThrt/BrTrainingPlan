# -*- coding: utf-8 -*-
import csv
import os

class ZwoBuilder :

    def __init__(self, csv_path) -> None:
        self.title, _ = os.path.splitext(os.path.basename(csv_path))
        with open(csv_path) as csv_file:
            self.csv_content = csv.reader(csv_file, delimiter=',')
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
        return  "</workout>\n\
    </workout_file>"

    def build_zwo_workout(self):
        title = self.title
        description = "Workout generated from csv file"
        self.zwo_content += self.start_zwo_file(title, description)

        self.zwo_content+= self.end_zwo_file()
        return self.zwo_content


