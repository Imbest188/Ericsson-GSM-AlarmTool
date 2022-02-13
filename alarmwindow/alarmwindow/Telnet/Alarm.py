import re
from datetime import datetime as dt


class Alarm:
    def mark_as_ceased(self):
        self.is_active = False

    def __parse_id(self, header_line, header_parts) -> None:
        try:
            if header_line.startswith('*'):
                id_index = 3 if 'CEASING' in header_line else 2
                self.id = int(header_parts[id_index])
            else:
                self.id = int(header_parts[-3])
        except ValueError:
            self.id = -1

    def __parse_header(self, header_parts) -> bool:
        type_identity = re.findall(r'[A|O][1-3]\/?\w{3}', header_parts[0])
        if not len(type_identity):
            return False
        self.type = type_identity[0]
        info_line = [x for x in header_parts[0].split(' ') if x != '']
        self.__parse_id(header_parts[0], info_line)

        time_line, date_line = info_line[-1], info_line[-2]
        if len(time_line) == 4:
            time_line = time_line + '00'
        if self.is_active:
            self.raising_time = dt.strptime(f'{date_line} {time_line}', "%y%m%d %H%M%S")
        else:
            self.ceasing_time = dt.strptime(f'{date_line} {time_line}', "%y%m%d %H%M%S")
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

    def __set_values(self, content_info) -> None:
        keys = content_info.keys()

        if 'RSITE' in keys:
            self.object_name = content_info['RSITE']
        elif 'TG' in keys:
            self.object_name = content_info['TG']
        elif 'SAID' in keys:
            self.object_name = content_info['SAID']
        elif 'SPID' in keys:
            self.object_name = content_info['SPID']

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
        elif 'DEST' in keys:
            self.managed_object = content_info['DEST']
        elif 'UNIT' in keys:
            self.managed_object = content_info['UNIT']
        elif 'FILENAME' in keys:
            self.managed_object = content_info['FILENAME']
        elif 'SNT' in keys:
            self.managed_object = content_info['SNT']

        if 'ALARM_SLOGAN' in keys:
            self.slogan = content_info['ALARM_SLOGAN']
        elif 'FAULT' in keys:
            self.slogan = content_info['FAULT']
        elif 'FAULT_TYPE' in keys:
            self.slogan = content_info['FAULT_TYPE']
        elif 'REASON' in keys:
            self.slogan = content_info['REASON']
        elif 'STATE' in keys:
            self.slogan = content_info['STATE']

    def __parse_content(self, alarm_data) -> None:
        alarm_data = alarm_data.replace('RADIO X-CEIVER ADMINISTRATION', '')
        if 'CEASING' in alarm_data:
            self.is_active = False
        lines_repr = [x for x in alarm_data.split('\n') if x != ''
                      and not x.startswith('WO')
                      and not x.startswith('EX')
                      and x != '\x03<']
        if not len(lines_repr) or not self.__parse_header(lines_repr[0:2]):
            return

        self.text = '\n'.join(lines_repr)
        if len(lines_repr) > 3:
            if 'DIGITAL PATH QUALITY SUPERVISION' in alarm_data:
                self.slogan = lines_repr[2]
                lines_repr.remove(lines_repr[2])
            if len(lines_repr) == 3:
                content_info = self.__get_values(lines_repr[1], lines_repr[2])
            else:
                content_info = self.__get_values(lines_repr[2], lines_repr[3])
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
