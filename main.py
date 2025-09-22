import pymem
from pymem import exception
from enum import IntEnum
from time import sleep
import platform
import os
import psutil

if platform.system() != 'Windows':
    input('[INFO] -> Esse programa está disponível apenas para Windows.')
    os._exit(1)


class Client:

    def __init__(self, pid: int) -> None:
        self.process = pymem.Pymem(pid)

    def __get_module(self, module: str) -> int:
        return pymem.pymem.process.module_from_name(self.process.process_handle, module).lpBaseOfDll

    def read_string(self, address: int, module: int) -> str:
        return self.process.read_string(address + module, encoding='UTF-8')

    def read_int32(self, address: int, module: int) -> int:
        return self.process.read_int(address + module)

    def read_float32(self, address: int, module: int) -> float:
        return self.process.read_float(address + module)

    def write_float32(self, address: int, value: float) -> float:
        return self.process.write_float(address, value)

    def main_module(self) -> int:
        return self.__get_module('main.exe')

    def igcn_module(self) -> int:
        return self.__get_module('IGC.dll')


class PlayerAddress(IntEnum):
    CAMERA_ZOOM: float = 0x1858620              # FLOAT32
    CAMERA_CRYWOLF: float = 0x1588FC            # FLOAT32
    MESSAGE: str = 0x6A599B8                    # STRING

class Slayer(Client):

    CAMERA_DEFAULT: float = 39.0

    def __init__(self, pid: int):
        super().__init__(pid)

    def camera_address(self) -> int:
        return PlayerAddress.CAMERA_ZOOM + self.main_module()

    def camera_zoom(self) -> float:
        return self.read_float32(PlayerAddress.CAMERA_ZOOM, self.main_module())

    def set_camera_zoom(self, value: float) -> None:
        self.__zoom_maps(value)
        self.__zoom_crywolf(value)

    def __zoom_maps(self, value: float) -> float:
        return self.write_float32(PlayerAddress.CAMERA_ZOOM + self.main_module(), value)

    def __zoom_crywolf(self, value: float) -> float:
        return self.write_float32(PlayerAddress.CAMERA_CRYWOLF + self.igcn_module(), value)

    def message(self) -> str:
        return self.read_string(PlayerAddress.MESSAGE, self.main_module())


class SlayerError(Exception):
    def __init__(self, error: any):

        error = str(error)
        self.message = None

        if 'Could not open process' in error:
            self.message = 'Abra o .exe como Administrador.'

        if 'Could not find process' in error:
            self.message = 'Seu Jogo está fechado. Abra o MU e execute o programa novamente.'

        if not self.message:
            self.message = 'Ocorreum um erro indesejado.'
            print(f'[ERROR] -> ', error)

        super().__init__(self.message)


while True:
    try:
        for process in psutil.process_iter(['pid', 'name']):

            if process.info['name'] != 'main.exe':
                continue

            slayer = Slayer(process.info['pid'])

            command = slayer.message().lower()

            if not command.startswith('/'):
                continue

            args = ''

            if command.startswith('/zoom'):
                args = command.split('/zoom')

            if len(args) == 0:
                continue

            try:
                arg = float(args[1].strip())
                slayer.set_camera_zoom(arg)
            except:
                pass

            if command == '/default':
                slayer.set_camera_zoom(slayer.CAMERA_DEFAULT)

            if command.startswith('/stop'):
                input('[INFO] -> Programa finalizado.')
                break

        sleep(0.3)

    except (exception.ProcessNotFound, exception.CouldNotOpenProcess) as Error:
        input(SlayerError(Error))
        break