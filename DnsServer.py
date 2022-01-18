import socket
import string
import configparser
import os
import pathlib



class DNS:
    def __init__(self):
        # self.suffix = socket.getfqdn().replace(f"{socket.gethostname()}", "")[1:]
        self.path = pathlib.Path().resolve()
        self.config_name = f'{self.path}\\config.conf'
        self.config = configparser.ConfigParser()
        self.config.read(self.config_name)
        if not os.path.exists(self.config_name):
            self.createConfig()
        self.external_ip = self.config.get("DEFAULT", "external_dns_ip")

        self.blacklist = [i.replace("\n", "") for i in
                          open(self.config.get("DEFAULT", "blacklist_file"), 'r').readlines()]

    def createConfig(self):
        """
        Create a config file
        """
        config = configparser.ConfigParser()
        config.set("DEFAULT", "external_dns_ip", '1.1.1.1')
        config.set("DEFAULT", "blacklist_file", 'blacklist.conf')
        with open(self.config_name, "w") as config_file:
            config.write(config_file)
        open(config.get("DEFAULT", "blacklist_file"), 'w').close()

    def external_work(self, data):
        external_serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        external_serv.sendto(data, (self.external_ip, 53))
        answer, addr = external_serv.recvfrom(512)
        return answer

    def get_domain_name(self, data):
        lst = []
        domain_name = ''
        for bit in data:
            if chr(bit) in string.ascii_lowercase:
                domain_name += (chr(bit))
            else:
                lst.append(domain_name)
                domain_name = ''
        lst = [i for i in lst if len(i) > 0]
        domain = '.'.join(lst)
        # if self.suffix in domain:
        #     domain = domain.replace(f".{self.suffix}", "")
        #     print(domain)
        return domain

    def work(self):
        local_serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        local_serv.bind(('127.0.0.1', 53))
        local_data, addr = local_serv.recvfrom(512)
        domain_name = self.get_domain_name(local_data)
        state = any([url in domain_name for url in self.blacklist])
        answer = self.external_work(local_data)
        print(f"Host is in blacklist: {domain_name} - {state}")
        local_serv.sendto(answer if not state else answer[:-4] + socket.inet_aton('127.0.0.1'), addr)




d1 = DNS()

while True:
    d1.work()
