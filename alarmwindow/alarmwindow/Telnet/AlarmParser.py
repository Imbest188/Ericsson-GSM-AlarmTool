import re
from datetime import datetime as dt
import json


class Alarm:
    def __parse_header(self, header_parts):
        info_line = [x for x in header_parts[0].split(' ') if x != '']
        self.type = info_line[0]
        try:
            if len(info_line[-1]) == 4:
                info_line[-1] = info_line[-1] + '00'
            self.date_time = dt.strptime(f'{info_line[-2]} {info_line[-1]}', "%y%m%d %H%M%S")
        except:
            print(f'exc with {info_line[-2]} {info_line[-1]}\n{header_parts}')
        self.descr = header_parts[-1]

    def __dict__(self):
        return {
            'type': self.type,
            'date_time': self.date_time,
            'managed_object': self.managed_object,
            'object_name': self.object_name,
            'slogan': self.slogan,
            'descr': self.descr
        }

    def toDict(self):
        return self.__dict__()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    @staticmethod
    def __get_values(header='', value_line='') -> dict:
        result = {}
        tokens = [x for x in header.split(' ') if x != '']

        for it in range(len(tokens) - 1):
            start_position = header.find(tokens[it])
            end_position = header.find(tokens[it + 1])
            value = value_line[start_position:end_position].strip()
            result[tokens[it]] = value

        start_position = header.find(tokens[-1])
        value = value_line[start_position:].strip()
        result[tokens[-1]] = value

        return result

    def __parse_content(self, alarm_data=''):
        alarm_data = alarm_data.replace('RADIO X-CEIVER ADMINISTRATION', '')
        lines_repr = [x for x in alarm_data.split('\n') if x != '' and not x.startswith('WO')]
        self.__parse_header(lines_repr[0:2])
        if len(lines_repr) > 3:
            if 'DIGITAL PATH QUALITY SUPERVISION' in alarm_data:
                self.slogan = lines_repr[2].strip()
                lines_repr.remove(lines_repr[2])
            content_info = self.__get_values(lines_repr[2], lines_repr[3])
            keys = content_info.keys()

            if 'RSITE' in keys:
                self.object_name = content_info['RSITE']
            elif 'TG' in keys:
                self.object_name = content_info['TG']

            if 'MO' in keys:
                self.managed_object = content_info['MO']
            elif 'CELL' in keys:
                self.managed_object = content_info['CELL']
                self.object_name = content_info['CELL'][:-1]
            elif 'DIP' in keys:
                self.managed_object = content_info['DIP']
            elif 'SDIP' in keys:
                self.object_name = content_info['SDIP']
                self.managed_object = content_info['LAYER']

            if 'ALARM_SLOGAN' in keys:
                self.slogan = content_info['ALARM_SLOGAN']
            elif 'FAULT' in keys:
                self.slogan = content_info['FAULT']

    def __init__(self, alarm_text):
        self.type = ''
        self.date_time = ''
        self.managed_object = ''
        self.object_name = ''
        self.slogan = ''
        self.descr = ''
        self.text = alarm_text
        try:
            self.__parse_content(alarm_text)
        except:
            print(alarm_text)

    def __str__(self):
        return f'type:{self.type} dt:{self.date_time} mo:{self.managed_object} name:{self.object_name}' \
               f' slogan:{self.slogan} desc:{self.descr}'


class AlarmParser:

    @staticmethod
    def parse_node_output(output_data) -> list:
        alarms = []
        head = 'allip;\nALARM LIST\n\n'
        for block in output_data \
                .replace('\r', '') \
                .replace(head, '') \
                .replace('ALARM SLOGAN', 'ALARM_SLOGAN') \
                .split('\n\n\n'):
            if re.findall(r'^[A|O][1-3]', block):
                alarms.append(Alarm(block.strip()))
        return alarms
