# ===========================================
# @@@@@@@@@@@@@@@@@@@@%%%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@%%%%##%%%%%%%%%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@%%%%*--=%%%%%%%%%%%%%%%%%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@%%%%%*=-:+%%%%**##%%%%%%%%%%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@%%%#%%#*=-=%#%%######%%%%%%#=====+*%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@%#*+*#++#%*--=***+--+*#%%%+--------=*%@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@#*--+*=-===--:--------+++===-----=---+%@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@#-----==::-==------------====------=---*@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@=---++==-----=--:----:---=====--------:+@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@#----=**+====---=---====----=+====------:+@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@=----==-:-==-==-----=======--======---==-:+@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@*-----=-=-+*+++===----========--=====---===-+@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@===-=-+-=+#@+:::-=====--===============---===+%@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@+==+==*=:--+-:::::-=+===========++++++==---====*%@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@#-*@*=+-:::::::::::-=-=---===+++=+++++*++=------=*%@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@=#@@+-::::::::::::-=-==----==***++*+==++*+--------=**##%%@@@@@@@
# @@@@@@@@@@@@@@@@%*@@%=+=::--::::::-:====----==+*****=====++--------:::----=+#@@@
# @@@@@@@@@@@@@@@@@@@@@%*=--:::::::---=-==------=+*****++=======---=---------::=@@
# @@@@@@@@@@@@@@@@@@%#*+---=*=-:::----=:-====-----=##****++============--------:=@
# @@@@@@@@@@@@@@@@%**#%+::=%*+-=###+----=+*##+=----=*%%####**++==========--------=
# @@@@@@@@@@@@@@@@@@@@%-:------+####**==*#+###*==----=*%%%%%%%%###*++=====--------
# @@@@@@@@@@@@@@@@@@%%#-::::--:****++*+-=*++++++===--::=###%%%%%%%%%%###*===------
# @@@@@@@@@@@@@%%%%%%%#-::::--=%%%%%###+=+#*+++++++==----=++++********++++=-------
# @@@@@@@@@@@%%%%%%%%%#:-::::#%%%%%%####=+#%###**++*#*+===########%%##*####+-=----
# @@@@@@@@@@%%%%%%%%%%=:-:::+@%%%%%%#*##*=+###*=====*%%#*++%%%%%%%@@%%%%%%%%*===--
# @@@@@@@@@#%%%%%%#+==---::*@%%%%%%%++**#*=+##*======+#%%%*#%%%%%%%%%%%%%%%%%#+++=
# @@@@@@@@@#%%%%%*+=:--::=%@@@%%%%%%===++**=*#+=====++=+#%%%%%%%%%%%%%%%%%%%%%%%%#
# @@@@@@@@@%%%%#+==-:-:::*@%%%%%%%%#=+====++=++======+++=*%%%%%%%%%%%%%%%%%%%%%%%%
# @@@@@@@%%%%#+==++=:::::+#%%%%%%%%+++=====++=++======++++*%%%%%%%%%%%%%%%%%%%%%%%
# @@@@@%%%%*+==+++++=-::-=#%%%%%%%#++========+=++======++==*%%%%%%%%%%%%%%%%%%%%%%
# @@@@%%%#+==+++++===+=---#%%%%%%%+++=========+=++======+==+*%%%%%%%%%%%%%%%%%%%%%
# @@%#**+==+++++=====+===*%%%%%%%#++======+++++==+=++++++++++*%%%%%%%%%%%%%%%%%%%%
# @#*+==+++++++====++==+*%%%%%%%#++===+++++++++==+++++++++++++*%%%%%%%%%%%%%%%%%%%
# #*==++++++++======++#%%%%%%%%*+==+++++****+*+=+++++++++++++*%%%%%%%%%%%%%%%%%#*+
# *++++++++++======+#%%%%%%%%#*+++++++++******++++++++++++++*%%%%%%%%%%%%%##**++==
# ++++++++======+*#%%%%%%%%%#++*+++++++++++***++*******+++**%%%%%%%%%%##*+++++====
# ++++++=====+*#%%%%%%%%%%%%%#++********++++++=++++++++++++*%%%%%%%%%*==++++=====+
# *+====+++*#%%%%%%%%%%%%%%%%%#+++++++++=====+=+++++++===++*%%%%%%%%*=++++======++
# %#######%@%%%%%%%%%%%%%%%%%%%+============++==+++++++++++*%%%%%%%#++++======++++
# "自动检测&配置工具"
# Author: 金英杰·MoonSage
# (c) 2024-2025
# ===========================================

import serial
import time
import re
import sys
import csv
import os
from web_config import set_web_config
from serial_config import update_device_config_via_serial

# 串口配置
SERIAL_PORT = 'COM9'
#BAUDRATE = 115200
BAUDRATE = 1500000
TIMEOUT = 10

# 忽略列表，用于过滤串口输出中的无用信息
IGNORE_LIST = [
    "push end.",
    "push device event to topic:",
    "(0.0,",
    "Subprogram output",
]

# 要进行 ping 测试的 IP 列表
PING_IP_LIST = [
    "8.8.8.8",          # Google公共DNS
    "114.114.114.114",  # 中国公共DNS
    "123.57.54.1",      # FP数据服务
    "124.160.42.66",    # 开发平台
    "120.26.107.230",   # 山顶基地总IP
    "106.15.42.105",    # SH测试代理IP
    "139.196.51.40",    # SH测试代理IP 2
    "180.158.129.197",  # SH服务器
    "113.204.224.114",  # 重庆平台(测试环境)
    "113.250.83.149",   # 政务云(正式环境)
]

def get_device_info(index):
    """
    从 CSV 文件中获取指定索引的设备信息
    :param index: 设备索引
    :return: 设备信息字典，如果未找到则返回 None
    """
    csv_path = "data/deviceIdFile.csv"
    try:
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, 1):
                if i == index:
                    return row
    except FileNotFoundError:
        print(f"未找到 CSV 文件: {csv_path}")
    return None

def should_ignore(line):
    """
    判断一行输出是否应该被忽略
    :param line: 输出行
    :return: 如果应该忽略则返回 True，否则返回 False
    """
    return any(ignore in line for ignore in IGNORE_LIST)

def wait_for(ser, keyword, timeout=10, capture=False):
    """
    等待串口输出中出现指定的关键字
    :param ser: 串口对象
    :param keyword: 要等待的关键字
    :param timeout: 超时时间，默认为 10 秒
    :param capture: 是否捕获输出，默认为 False
    :return: 如果捕获模式开启，返回 (是否找到关键字, 捕获的输出)；否则返回是否找到关键字
    """
    ser.timeout = 0.5
    buf = ""
    output = ""
    start = time.time()
    while time.time() - start < timeout:
        data = ser.read(1024).decode(errors='ignore')
        if data:
            buf += data
            output += data
            for line in data.splitlines():
                if not should_ignore(line):
                    print(line)
            if keyword in buf:
                if capture:
                    return True, output
                return True
        time.sleep(0.1)
    if capture:
        return False, output
    return False

def send_ctrl_c(ser, times=3):
    """
    向串口发送 Ctrl+C 信号
    :param ser: 串口对象
    :param times: 发送次数，默认为 3 次
    """
    for _ in range(times):
        ser.write(b'\x03')
        time.sleep(0.5)

def send_cmd(ser, cmd):
    """
    向串口发送命令
    :param ser: 串口对象
    :param cmd: 要发送的命令
    """
    ser.write((cmd + '\n').encode())

def check_ifconfig(output):
    """
    检查 ifconfig 输出是否符合要求
    :param output: ifconfig 输出
    :return: 如果 eth0 和 usb0 都符合要求则返回 True，否则返回 False
    """
    eth0_ok = False
    usb0_ok = False

    # 检查 eth0
    eth0_match = re.search(r'eth0.*?inet addr:([\d\.]+)', output, re.S)
    if eth0_match and eth0_match.group(1) == "192.168.137.55":
        eth0_ok = True

    # 检查 usb0
    usb0_match = re.search(r'usb0.*?inet addr:([\d\.]+)', output, re.S)
    if usb0_match and usb0_match.group(1):
        usb0_ok = True

    return eth0_ok and usb0_ok

def check_ping(ser, ip):
    """
    对指定 IP 进行 ping 测试
    :param ser: 串口对象
    :param ip: 要测试的 IP 地址
    :return: 如果 ping 成功则返回 True，否则返回 False
    """
    send_cmd(ser, f"ping -c 1 -w 3 {ip}")
    ok, output = wait_for(ser, "#", timeout=10, capture=True)
    if "1 received" in output or "0% packet loss" in output:
        print(f"Ping {ip} 成功")
        return True
    else:
        print(f"Ping {ip} 失败")
        return False

def wait_for_any(ser, keywords, timeout=10):
    """
    等待串口输出中出现任意一个关键字
    :param ser: 串口对象
    :param keywords: 要等待的关键字列表
    :param timeout: 超时时间，默认为 10 秒
    :return: 如果找到关键字，返回 (关键字, 捕获的输出)；否则返回 (None, 捕获的输出)
    """
    ser.timeout = 0.5
    buf = ""
    output = ""
    start = time.time()
    while time.time() - start < timeout:
        data = ser.read(1024).decode(errors='ignore')
        if data:
            buf += data
            output += data
            for line in data.splitlines():
                if not should_ignore(line):
                    print(line)
            for kw in keywords:
                if kw in buf:
                    return kw, output
        time.sleep(0.1)
    return None, output

def login_to_shell(ser):
    """
    尝试登录到设备的 shell
    :param ser: 串口对象
    :return: 如果登录成功则返回 True，否则返回 False
    """
    max_login = 10  # 最多尝试 10 次，防止死循环
    for login_count in range(max_login):
        print(f"第{login_count + 1}次尝试登录...")
        kw, _ = wait_for_any(ser, ["login:", "Password:", "#"], timeout=10)
        if kw == "login:":
            print("检测到 login:，发送 root")
            send_cmd(ser, "root")
        elif kw == "Password:":
            print("检测到 Password:，发送 root")
            send_cmd(ser, "root")
        elif kw == "#":
            print("检测到 shell 提示符，已进入 shell，开始后续流程")
            return True
        else:
            print("未检测到任何已知提示，发送回车等待")
            send_cmd(ser, "")
            time.sleep(0.5)
    print("多次尝试仍未进入 shell，退出")
    return False

def perform_network_check(ser):
    """
    执行网络检查
    :param ser: 串口对象
    :return: 如果网络检查通过则返回 True，否则返回 False
    """
    # 先尝试中断前台进程
    send_ctrl_c(ser, times=3)

    # 登录到 shell
    if not login_to_shell(ser):
        return False

    print("登录成功，开始执行命令")
    send_cmd(ser, "ifconfig")
    ok, ifconfig_output = wait_for(ser, "#", capture=True)
    if not ok:
        print("未获取到 ifconfig 结果，退出")
        return False

    all_ok = check_ifconfig(ifconfig_output)
    if all_ok:
        print("网络检查通过，继续执行后续命令")
        # 依次 ping 每个 IP
        for ip in PING_IP_LIST:
            if not check_ping(ser, ip):
                print(f"网络不通：{ip}，硬件不可用！")
                all_ok = False
                break
        if all_ok:
            print("所有 IP 均可达，继续执行后续命令")
            send_cmd(ser, "python3 ./test_tool/app.py")
            wait_for(ser, "Serving Flask app", timeout=20)
    else:
        print("网络检查未通过，硬件不可用！")
    return all_ok

def main_check():
    """
    仅进行网络检测
    :return: 如果网络检测通过则返回 True，否则返回 False
    """
    with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=TIMEOUT) as ser:
        return perform_network_check(ser)

import os

def main_update_with_config(index):
    """
    仅配置第 index 个设备，并保存 config.json 到本地 htmls/Axx.config
    :param index: 设备索引
    """
    device_info = get_device_info(index)
    if not device_info:
        print(f"未找到第{index}个设备信息")
        return
    print(f"选中设备: {device_info['device_name']}")
    config_dict = {
        "mqtt_server_ip": device_info["mqtt_server_ip"],
        "device_name": device_info["device_name"],
        "device_secret": device_info["device_secret"],
        "product_key": device_info["product_key"]
    }
    with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=TIMEOUT) as ser:
        update_device_config_via_serial(ser, config_dict)
        # 获取 config.json 内容
        ser.write(b"cat /usr/dkkj/config.json\n")
        time.sleep(1)
        lines = []
        while ser.in_waiting:
            line = ser.readline().decode(errors="ignore")
            lines.append(line)
        config_content = ''.join(lines)
        # 保存到本地
        os.makedirs("htmls", exist_ok=True)
        local_path = f"htmls/A{index}.config"
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(config_content)
        print(f"已保存 config.json 到本地 {local_path}")

def main_update(index):
    """
    仅配置第 index 个设备
    :param index: 设备索引
    """
    device_info = get_device_info(index)
    if not device_info:
        print(f"未找到第{index}个设备信息")
        return
    print(f"选中设备: {device_info['device_name']}")
    url = "http://192.168.137.55:7000/"
    set_web_config(device_info, url, index)

def main_check_update(index):
    """
    检测网络后再配置设备
    :param index: 设备索引
    """
    ok = main_check()
    if not ok:
        print("网络检测未通过，终止后续操作。")
        return
    print("网络检测通过，开始执行更新流程。")
    main_update_with_config(index)

if __name__ == "__main__":
    print("========== 终端自动检测与配置工具 ==========")
    print("支持命令：")
    print("  python main.py check                # 仅检测网络")
    print("  python main.py update <index>       # 仅配置第 <index> 个设备")
    print("  python main.py check_update <index> # 检测网络后再配置设备")
    print("===========================================")
    if len(sys.argv) < 2:
        print("用法: python main.py check | update <index> | check_update <index>")
        sys.exit(1)
    cmd = sys.argv[1]
    print(f"收到命令：{cmd}")
    if cmd == "check":
        print("开始网络检测流程...")
        main_check()
    elif cmd == "update":
        if len(sys.argv) < 3:
            print("用法: python main.py update <index>")
            sys.exit(1)
        index = int(sys.argv[2])
        print(f"开始配置第 {index} 个设备...")
        main_update(index)
    elif cmd == "check_update":
        if len(sys.argv) < 3:
            print("用法: python main.py check_update <index>")
            sys.exit(1)
        index = int(sys.argv[2])
        print(f"开始网络检测并配置第 {index} 个设备...")
        main_check_update(index)
    else:
        print("未知命令")