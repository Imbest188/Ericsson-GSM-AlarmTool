import re

from .Alarm import Alarm
from .EricssonTelnet import EricssonTelnet


ALARM_TYPE_REGEXP = r"[A|O][1-3]\/?\w{3}"


class EricssonNode(EricssonTelnet):
    def __init__(self, ip, login, password):
        super().__init__(ip, login, password)
        self.id = -1

    def __pack(self, alarms) -> dict:
        return {'alarms': alarms, 'node_id': self.id}

    def read_alarms(self) -> dict:
        return self.__pack(self.parse_node_output(self.get('allip;')))

    def get_new_alarms(self) -> dict:
        alarms = []
        for alarm_text in self.get_alarms():
            alarms += self.parse_node_output(alarm_text)
        return self.__pack([alarm for alarm in alarms if alarm.is_valid])

    @staticmethod
    def __replace_tokens(data):
        head = 'allip;\nALARM LIST\n\n'
        return data.replace('\r', '') \
            .replace(head, '') \
            .replace('ALARM SLOGAN', 'ALARM_SLOGAN') \
            .replace('FAULT TYPE', 'FAULT_TYPE')

    def parse_node_output(self, output_data) -> list:
        alarms = []

        for block in self.__replace_tokens(output_data).split('\n\n\n'):
            if re.findall(ALARM_TYPE_REGEXP, block):
                alarms.append(Alarm(block.strip(), self.id))
        return alarms


class EricssonBsc(EricssonNode):
    class BaseStation:
        def __init__(self, tg, name):
            self.tg = tg
            self.name = name
            self.rbl = []

        def __eq__(self, other):
            if other.name == self.name:
                return True
            if other.tg == self.tg:
                return True
            return False

        def __str__(self):
            return f'{self.tg} {self.name} {self.rbl}'

    def __init__(self, ip, login, password):
        super().__init__(ip, login, password)
        self.bs_list = []
        self.__init_tg()
        self.__init_rbl()

    def get_rbl_owner(self, rbl_text):
        rbl = int(rbl_text.split('R')[0])
        for bs in self.bs_list:
            if rbl in bs.rbl:
                return bs.name
        return ''

    def parse_node_output(self, output_data) -> list:
        result = super().parse_node_output(output_data)
        for alarm in result:
            if 'RBL' in alarm.managed_object:
                alarm.object_name = self.get_rbl_owner(alarm.managed_object)
        return result

    def __init_tg(self):
        tg_print = self.get('rxtcp:moty=rxotg;')
        for line in tg_print.split('\r\n'):
            if 'RXOTG' in line:
                tg, cell, *_ = [x for x in line.split(' ') if x != '']
                self.bs_list.append(self.BaseStation(tg, cell[:-1]))

    def __set_rbl(self, tg, rbl):
        for bs in self.bs_list:
            if bs.tg == tg:
                bs.rbl.append(rbl)

    def __init_rbl(self):
        rxapp_print = self.get('rxapp:moty=rxotg;')
        current_tg = ''
        last_rbl = -1
        for line in rxapp_print.split('\r\n'):
            if 'RXOTG' in line:
                current_tg = line.strip()
            if 'RBLT2-' in line:
                dev = line.split(' ')[0].replace('RBLT2-', '')
                rbl_no = int(int(dev) / 32)
                if rbl_no != last_rbl:
                    last_rbl = rbl_no
                    self.__set_rbl(current_tg, last_rbl)
        self.__set_rbl(current_tg, last_rbl)
