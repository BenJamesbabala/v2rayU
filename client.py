#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json

from config import Config
from utils import get_ip
from group import Vmess, Socks, SS, Mtproto
from selector import ClientSelector


class ClientWriter:
    def __init__(self, group, client_index):
        self.config_factory = Config()
        with open(self.config_factory.get_path("config_path"), 'r') as json_file:
            self.config = json.load(json_file)
        
        self.write_path = self.config_factory.get_path("write_client_path")
        self.template_path = self.config_factory.get_path("template_path")
        self.group = group
        self.client_index = client_index
        self.node = group.node_list[client_index]

    def load_template(self, template_name):
        """
        load special template
        """
        with open(self.template_path + "/" + template_name, 'r') as stream_file:
            template = json.load(stream_file)
        return template

    def transform(self):
        user_json = None
        if type(self.node) == Vmess:
            self.client_config = self.load_template('client.json')
            user_json = self.client_config["outbounds"][0]["settings"]["vnext"][0]
            user_json["users"][0]["id"] = self.node.password
            user_json["users"][0]["alterId"] = self.node.alter_id

        elif type(self.node) == Socks:
            self.client_config = self.load_template('client_socks.json')
            user_json = self.client_config["outbounds"][0]["settings"]["servers"][0]
            user_json["users"][0]["user"] = self.node.user_info
            user_json["users"][0]["pass"] = self.node.password

        elif type(self.node) == SS:
            self.client_config = self.load_template('client_ss.json')
            user_json = self.client_config["outbounds"][0]["settings"]["servers"][0]
            user_json["method"] = self.node.method
            user_json["password"] = self.node.password

        elif type(self.node) == Mtproto:
            print("\nMTProto协议只支持Telegram通信, 所以无法生成配置文件!\n")
            exit(-1)

        user_json["port"] = int(self.group.port)

        if type(self.node) != SS:
            self.client_config["outbounds"][0]["streamSettings"] = self.config["inbounds"][group.index]["streamSettings"]

        if group.tls == 'tls':
            content = self.config_factory.get_data("domain")
            user_json["address"] = str(content)
            self.client_config["outbounds"][0]["streamSettings"]["tlsSettings"] = {}
        else:
            user_json["address"] = str(get_ip())

    def write(self):
        """
        写客户端配置文件函数
        """
        json_dump = json.dumps(self.client_config,indent=1)
        with open(self.write_path, 'w') as write_json_file:
            write_json_file.writelines(json_dump)

        print("保存成功！({})\n".format(self.write_path))
        

if __name__ == '__main__':
    cs = ClientSelector('生成客户端json')
    client_index = cs.client_index
    group = cs.group

    if group == None:
        exit(-1)
    else:
        cw = ClientWriter(group, client_index)
        cw.transform()
        cw.write()