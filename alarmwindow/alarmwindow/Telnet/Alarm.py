import re
from datetime import datetime as dt

object_name_keys = ['RSITE', 'TG', 'SAID', 'SPID']
managed_object_keys = ['MO', 'CELL', 'DIP', 'SDIP', 'LAYER', 'DEST', 'UNIT', 'FILENAME', 'SNT']
slogan_keys = ['ALARM_SLOGAN', 'FAULT', 'FAULT_TYPE', 'REASON', 'STATE']

ALARM_TYPE_REGEXP = r"[A|O][1-3]\/?\w{3}"


class Alarm:
    def mark_as_ceased(self):
        self.is_active = False

    def __parse_id(self, header_line: str, header_parts: list) -> None:
        try:
            if header_line.startswith('*'):
                id_index = 3 if 'CEASING' in header_line else 2
                self.id = int(header_parts[id_index])
            else:
                self.id = int(header_parts[-3])
        except ValueError:
            self.id = -1

    def __set_date_time(self, date_line, time_line):
        if len(time_line) == 4:
            time_line = time_line + '00'
        datetime_object = dt.strptime(f'{date_line} {time_line}', "%y%m%d %H%M%S")
        if self.is_active:
            self.raising_time = datetime_object
        else:
            self.ceasing_time = datetime_object

    def __parse_header(self, header_parts) -> bool:
        type_identity = re.findall(ALARM_TYPE_REGEXP, header_parts[0])
        if not len(type_identity):
            return False

        self.type = type_identity[0]
        info_line = [x for x in header_parts[0].split(' ') if x != '']
        self.__parse_id(header_parts[0], info_line)
        time_line, date_line = info_line[-1], info_line[-2]
        self.__set_date_time(date_line, time_line)

        self.descr = header_parts[-1]
        return len(self.type) > 0

    def __dict__(self):
        return {
            'id': self.id,
            'type': self.type,
            'raising_time': self.raising_time,
            'ceasing_time': self.ceasing_time,
            'managed_object': self.managed_object,
            'object_name': self.object_name,
            'slogan': self.slogan,
            'descr': self.descr
        }

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

    @staticmethod
    def __get_value_from_keys(container: dict, keys: list):
        for key in keys:
            if key in container.keys():
                return container[key]
        return ''

    def __set_values(self, content_info: dict) -> None:
        self.object_name = self.__get_value_from_keys(content_info, object_name_keys)
        self.managed_object = self.__get_value_from_keys(content_info, managed_object_keys)
        self.slogan = self.__get_value_from_keys(content_info, slogan_keys)
        if 'CELL' in content_info.keys():
            self.object_name = content_info['CELL'][:-1]

    @staticmethod
    def __is_service_line(line: str) -> bool:
        if line == '' or line.startswith('WO') \
                or line.startswith('EX') or line == '\x03<':
            return True
        return False

    def __prepare_data(self, alarm_data: str) -> list:
        alarm_data = alarm_data.replace('RADIO X-CEIVER ADMINISTRATION', '')
        if 'CEASING' in alarm_data:
            self.is_active = False
        lines_repr = [x for x in alarm_data.split('\n') if not self.__is_service_line(x)]
        if not len(lines_repr) or not self.__parse_header(lines_repr[0:2]):
            return []
        if 'DIGITAL PATH QUALITY SUPERVISION' in alarm_data:
            self.slogan = lines_repr[2]
            lines_repr.remove(lines_repr[2])
        return lines_repr

    def __parse_content(self, alarm_data: str) -> None:
        lines_repr = self.__prepare_data(alarm_data)
        if not len(lines_repr):
            return
        self.text = '\n'.join(lines_repr)
        if len(lines_repr) > 3:
            start_line = 1 if len(lines_repr) == 3 else 2
            content_info = self.__get_values(lines_repr[start_line], lines_repr[start_line + 1])
            self.__set_values(content_info)
        self.is_valid = True

    def __init__(self, alarm_text: str, node_id: int):
        self.type = ''
        self.raising_time = None
        self.ceasing_time = None
        self.managed_object = ''
        self.object_name = ''
        self.slogan = ''
        self.descr = ''
        self.text = ''
        self.id = 0
        self.is_active = True
        self.__parse_content(alarm_text)
        self.node_id = node_id
        self.is_valid = False

    def __str__(self):
        return f'type:{self.type} dt:{self.raising_time} mo:{self.managed_object} name:{self.object_name}' \
               f' slogan:{self.slogan} desc:{self.descr}'
