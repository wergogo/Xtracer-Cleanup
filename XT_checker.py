import subprocess
import os
import time
import XT_config

config_path = 'config/config.yml'
config = XT_config.config(config_path)
config_data = config.data['baseConf']


def deviceStart():
    devicePath = config_data.get('simulator_path', '')
    if devicePath:
        print('devicePath:', devicePath)
        os.popen(devicePath)
    else:
        printM('No simulator_path configured; start the AVD manually.')


def _adb(cmd):
    return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8').stdout


def checkDeviceConnect():
    serial = config_data.get('device_serial', '')
    lines = os.popen('adb devices').read().strip().splitlines()
    # lines[0] is header; others contain "<serial>\tstate"
    devices = [l.split('\t')[0] for l in lines[1:] if '\tdevice' in l]
    if serial and serial in devices:
        # Ensure frida ports forwarded to this device
        os.popen(f'adb -s {serial} forward tcp:27042 tcp:27042')
        os.popen(f'adb -s {serial} forward tcp:27043 tcp:27043')
        printM(f'Port forward set for {serial} (27042/27043)')
        return True
    return False


def checkBootCompleted():
    serial = config_data.get('device_serial', '')
    out = os.popen(f'adb -s {serial} shell getprop sys.boot_completed').read()
    return out.strip() == '1'


def checkFrida():
    adbReturn = _adb('frida-ps -U')
    if "Failed" in adbReturn:
        return False
    if "PID" in adbReturn:
        return True
    return False


def FridaConnect():
    serial = config_data.get('device_serial', '')
    host_path = config_data.get('frida_server_host_path', '')
    remote_path = config_data.get('frida_server_remote_path', '/data/local/tmp/frida-server')
    args = config_data.get('frida_server_args', '')
    if not host_path or not os.path.exists(host_path):
        printM('frida_server_host_path not set or file missing. Please configure in config.yml.')
        return
    printM(f'Pushing frida-server to {serial}: {remote_path}')
    _adb(f'adb -s {serial} push "{host_path}" "{remote_path}"')
    _adb(f'adb -s {serial} shell chmod 755 "{remote_path}"')
    # Start frida-server in background (no su required on many emulators)
    _adb(f'adb -s {serial} shell nohup "{remote_path}" {args} >/dev/null 2>&1 &')
    printM('frida-server start command sent.')


def printM(msg):
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), ':', msg)


def mainCheckProcess():
    deviceStart()
    print("---------------------------------------------")
    while True:
        if checkDeviceConnect():
            if not checkBootCompleted():
                printM('device loading')
                time.sleep(5)
                continue
            printM('device connected')
            if checkFrida():
                printM('frida connected')
            else:
                printM('frida disconnected | trying connect')
                FridaConnect()
        else:
            printM('device not found; ensure the emulator is running (see device_serial).')
        time.sleep(5)
        print("---------------------------------------------")


if __name__ == '__main__':
    mainCheckProcess()
