import socket
import telnetlib
import time


class EricssonTelnet:
    __ip = ''
    __login = ''
    __password = ''
    __telnet = None
    __is_busy = True
    __alarms = []
    __is_alive = False
    __retries_counter = 0

    def __init__(self, ip, login, password):
        self.auth_with(ip, login, password)

    def get_auth_data(self) -> dict:
        return {'host': self.__ip, 'login': self.__login, 'pwd': self.__password}

    def auth_with(self, ip, login, pwd):
        self.__ip = ip
        self.__login = login
        self.__password = pwd
        self.__connect()

    def is_alive(self):
        return self.__is_alive

    def __connect(self):
        print(f'Подключение к {self.__ip}')
        try:
            self.__telnet = telnetlib.Telnet(self.__ip)
        except (ConnectionError, OSError, ConnectionResetError):
            self.__telnet = None
            print("Не удалось подключиться к " + self.__ip)
            self.__is_alive = False
            return False
        self.__auth()
        self.__is_alive = True
        self.__listen_mode()
        print("\nСоединение с " + self.__ip + ' установлено')
        return True

    def __heartbeat(self):
        self.__is_busy = True
        self.__telnet.write(b'\r\n')
        time.sleep(0.2)
        self.__telnet.write(b'\x04')
        self.__is_busy = False

    def __parse(self, alarm_text):
        for alarm in alarm_text.split('END'):
            self.__alarms.append(alarm.strip())

    @staticmethod
    def __clean_special_symbols(text):
        return text.replace('\x04', '').replace('<', '').replace('\x03', '').strip()

    def get_alarms(self):
        self.__listen()
        result = []
        for alarm in self.__alarms:
            if len(alarm) and alarm not in ['\x04', '<']:
                alarm_text = self.__clean_special_symbols(alarm)
                result.append(alarm_text)
        self.__alarms.clear()
        return result

    def __try_to_reconnect(self):
        while not self.__connect():
            time.sleep(30)

    def __listen(self):
        try:
            self.__retries_counter += 1
            channel_output = self.__telnet.read_very_eager().decode('ascii')
            print(channel_output)
            if 'Timeout' in channel_output or self.__retries_counter >= 10:
                self.__retries_counter = 0
                self.__heartbeat()
            self.__parse(channel_output)
        except (ConnectionError, OSError, ConnectionResetError):
            self.__try_to_reconnect()

    def __listen_mode(self):
        self.__telnet.write(b'\x04')
        self.__is_busy = False

    def __check_connection(self):
        try:
            self.__telnet.write(b'\r\n')
            for i in range(10):
                time.sleep(0.1)
                check_state = self.__telnet.read_very_eager().decode('ascii').lower()
                if 'timeout' in check_state:
                    self.__telnet.write(b'\r\n')
                    if 'WO' not in check_state:
                        self.__auth()
                    self.__listen_mode()
                if 'login' in check_state:
                    self.__connect()
                    self.__telnet.write(b'\r\n')
                if 'WO' in check_state:
                    break
        except (ConnectionError, OSError, ConnectionResetError):
            print(f'Переподключение к хосту {self.__ip}')
            self.__try_to_reconnect()

    def get(self, message) -> str:
        while self.__is_busy:
            time.sleep(0.2)
        self.__is_busy = True
        self.__check_connection()
        self.__telnet.write(message.encode('ascii') + b'\r\n')
        result = ''
        for count in range(30):
            result += self.__telnet.read_very_eager().decode('ascii')
            time.sleep(0.2)
            if 'END' in result or 'CELL NOT DEFINED' in result or 'EXTERNAL' in result:
                break

        self.__listen_mode()
        return result

    def send(self, message, accepting=True):
        while self.__is_busy:
            time.sleep(0.2)
        self.__is_busy = True
        self.__check_connection()
        self.__telnet.write(message.encode('ascii') + b'\r\n')
        time.sleep(0.5)
        if accepting:
            self.__telnet.write(b';\r\n\r\n')
        result = self.__telnet.read_very_eager().decode('ascii').lower()
        self.__listen_mode()
        if 'ordered' in result or 'executed' in result or 'preop' in result:
            return True
        return False

    def __auth(self):
        for i in range(50):
            time.sleep(0.1)
            answer = self.__telnet.read_very_eager()
            if b'login' in answer:
                self.__telnet.write(self.__login.encode('ascii') + b'\r\n')
            elif b'assword' in answer:
                self.__telnet.write(self.__password.encode('ascii') + b'\r\n')
            elif b'terminal' in answer:
                if b'Will assume' in answer:
                    break
                self.__telnet.write(b'xterm\r\n')
            elif b'Domain' in answer:
                self.__telnet.write(b'\r\n')
                time.sleep(1)
            elif b'WO' in answer:
                return
            elif b'Login ok' in answer:
                break
            elif b'Logon failure' in answer:
                self.__is_alive = False
                return

        self.__telnet.write(b'\r\n')
        self.__telnet.write(b'mml -a\r\n')

    def __del__(self):
        self.__telnet.write(b'exit;')
        self.__telnet.get_socket().shutdown(socket.SHUT_WR)
        self.__telnet.read_all()
        self.__telnet.close()
        self.__telnet = None
