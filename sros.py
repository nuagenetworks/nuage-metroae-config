# pip install --upgrade textfsm==0.4.1
# ./levistate.py create -s 10.31.180.18 -u admin -p admin -tp wbx-templates/ -dp sros_user_data.yml
import netmiko

nokia_sr = {
    'device_type': 'alcatel_sros',
    'ssh_config_file': "/etc/ssh/ssh_config",
    'ip': "10.31.180.18",
    'username': "admin",
    'password': "admin",
    'port': 22,
    'secret': '',
    'verbose': False,
    'global_delay_factor': 10
}
sros = netmiko.ConnectHandler(**nokia_sr)

# output = sros.send_command("show version")
# print(output)

# print(sros.find_prompt())

# output = sros.send_command("admin display-config")
# print(output)

# output = sros.send_command("admin display-config")
# print(output)

sros.send_config_set(["port 999/1/3", "no shutdown"])
