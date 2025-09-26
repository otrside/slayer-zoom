import pymem
from enum import IntEnum
import platform
import os
import psutil

PREFIX = '/'
CURRENT_VERSION = '1.0.5'

if platform.system() != 'Windows':
    input('[INFO] -> Esse programa está disponível apenas para Windows.')
    os._exit(1)

print('Bem-vindo ao Slayer Zoom')
print(f'Versão: {CURRENT_VERSION}')

class Client:

    def __init__(self, pid: int) -> None:
        self.pid = pid
        self.process = pymem.Pymem(self.pid)

    def __get_module(self, module: str) -> int|None:
        return pymem.pymem.process.module_from_name(self.process.process_handle, module).lpBaseOfDll
    
    def read_string(self, address: int, module: int) -> any:
        return self.process.read_string(address + module, encoding='UTF-8')

    def read_int32(self, address: int, module: int) -> int:
        return self.process.read_int(address + module)

    def read_float32(self, address: int, module: int) -> float:
        return self.process.read_float(address + module)

    def write_float32(self, address: int, value: float) -> None:
        self.process.write_float(address, value)

    def write_string(self, address: int, value: float) -> None:
        self.process.write_string(address, value)

    def main_module(self) -> int:
        return self.__get_module('main.exe')

    def igcn_module(self) -> int:
        return self.__get_module('IGC.dll')

class PlayerAddress(IntEnum):
    CAMERA_ZOOM: float = 0x1858620              # FLOAT32
    CAMERA_CRYWOLF: float = 0x1588FC            # FLOAT32
    MESSAGE: str = 0x6A599B8                    # STRING
    NAME: str = 0x1589F1                        # STRING
    MAP_ID: int = 0x18585EC                     # INT32

class Slayer(Client):

    CAMERA_DEFAULT: float = 39.0

    # 93 SelectServer / 94 SelectCharacter
    __MAPSDISABLED: list[int] = [73, 74, 75, 76, 78, 93, 94]

    def __init__(self, pid: int):
        super().__init__(pid)

    def camera_address(self) -> int:
        return PlayerAddress.CAMERA_ZOOM + self.main_module()

    def camera_zoom(self) -> float:
        return self.read_float32(PlayerAddress.CAMERA_ZOOM, self.main_module())

    def set_camera_zoom(self, value: float) -> None:
        self.__zoom(value)
        self.__zoom_crywolf(value)
        self.clear_message()

    def __zoom(self, value: float) -> None:
        self.write_float32(PlayerAddress.CAMERA_ZOOM + self.main_module(), value)

    def __zoom_crywolf(self, value: float) -> None:
        self.write_float32(PlayerAddress.CAMERA_CRYWOLF + self.igcn_module(), value)
    
    def __set_message(self, value: str = '.') -> None:
        self.write_string(PlayerAddress.MESSAGE + self.main_module(), value)
    
    def clear_message(self) -> None:
        self.__set_message()

    def message(self) -> str:
        return self.read_string(PlayerAddress.MESSAGE, self.main_module())

    def name(self) -> str:
        return self.read_string(PlayerAddress.NAME, self.igcn_module())

    def is_logged(self) -> bool:
        try:
            if self.map_id() in self.__MAPSDISABLED:
                return False

            return True
        except:
            return False

    def map_id(self) -> int:
        return self.read_int32(PlayerAddress.MAP_ID, self.main_module())

class SlayerError:
    def __init__(self, error: any):
        self.message = str(error)

        if 'Could not open process' in self.message:
            input(self.process_permission_error())
            os._exit(1)

    def process_permission_error(self) -> str:
        return 'Abra o .exe como Administrador.'
    
while True:
    try:
        for process in psutil.process_iter(['pid', 'name']):

            if process.info['name'] != 'main.exe':
                continue

            slayer = Slayer(process.info['pid'])

            if not slayer.is_logged():
                continue

            playerName = slayer.name()
            message = slayer.message().lower().strip()

            if not message.startswith(PREFIX):
                continue

            content = message[1:].split(' ')

            commandName = content[0]
            args = content[1:]

            if commandName == 'zoom':

                if len(args) == 0:
                    print(f'[INFO] -> Use o comando dessa maneira: {PREFIX}zoom <número>')
                    slayer.clear_message()
                    continue

                try:
                    arg = float(args[0])

                    slayer.set_camera_zoom(arg)

                    print(
                        f'[INFO] -> Camera de {playerName} foi setada para', arg)                    
                except ValueError:
                    print(f'[INFO] -> {args[0]} não é um número. O comando {PREFIX}zoom aceita apenas número.')
                    slayer.clear_message()
                finally:
                    continue

            if commandName == 'default':
                slayer.set_camera_zoom(slayer.CAMERA_DEFAULT)
                print(f'[INFO] -> Camera de {playerName} foi resetada.')
                continue

            if commandName == 'stop':
                input('[INFO] -> Programa finalizado.')
                slayer.clear_message()
                os._exit(1)

    except Exception as Error:
        SlayerError(Error)
