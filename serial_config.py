import time

def update_config_json_on_device(ser, config_path, new_values):
    """
    通过串口在设备上直接用 sed 命令修改 config.json 的指定字段
    :param ser: 串口对象
    :param config_path: 设备上的 config.json 路径
    :param new_values: 包含4个字段的新配置
    """
    # 备份原文件
    backup_cmd = f"cp {config_path} {config_path}.bak\n"
    ser.write(backup_cmd.encode())
    time.sleep(0.2)

    # 构造 sed 命令
    cmds = [
        f"sed -i 's/\"ip\": *\"[^\"]*\"/\"ip\": \"{new_values['mqtt_server_ip']}\"/' {config_path}\n",
        f"sed -i 's/\"device_name\": *\"[^\"]*\"/\"device_name\": \"{new_values['device_name']}\"/' {config_path}\n",
        f"sed -i 's/\"device_secret\": *\"[^\"]*\"/\"device_secret\": \"{new_values['device_secret']}\"/' {config_path}\n",
        f"sed -i 's/\"product_key\": *\"[^\"]*\"/\"product_key\": \"{new_values['product_key']}\"/' {config_path}\n"
    ]
    for cmd in cmds:
        ser.write(cmd.encode())
        time.sleep(0.2)  # 适当延时，防止命令丢失

    print("配置已通过 sed 命令写回设备。")
    return True

def update_device_config_via_serial(serial_obj, config_dict, config_path="/usr/dkkj/config.json"):
    """
    外部调用接口
    :param serial_obj: 已打开的串口对象
    :param config_dict: 包含4个字段的新配置
    :param config_path: 配置文件路径
    """
    return update_config_json_on_device(serial_obj, config_path, config_dict)