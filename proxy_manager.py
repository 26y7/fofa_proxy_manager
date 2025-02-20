import base64
import requests
import socks
import socket
import sys
import re
import os

# FOFA API 配置
FOFA_EMAIL = os.getenv('FOFA_EMAIL')
FOFA_API_KEY = os.getenv('FOFA_API_KEY')
FOFA_API_URL = "https://fofa.info/api/v1/search/all"

class ProxyManager:
    def __init__(self):
        pass

    def test_proxy(self, proxy, output_file, proxy_type='http'):
        # 尝试测试代理是否可用
        try:
            # 根据代理类型选择不同的请求方式
            if proxy_type in ['http', 'https']:
                # 使用HTTP或HTTPS代理进行请求
                response = requests.get('http://httpbin.org/ip', proxies={"http": proxy, "https": proxy}, timeout=5)
            else:
                # 解析代理IP和端口
                ip, port = proxy.split(':')
                # 保存原始的socket对象
                original_socket = socket.socket
                # 根据代理类型设置SOCKS代理
                if proxy_type == 'socks5':
                    socks.set_default_proxy(socks.SOCKS5, ip, int(port))
                else:
                    socks.set_default_proxy(socks.SOCKS4, ip, int(port))
                # 使用SOCKS代理
                socket.socket = socks.socksocket
                response = requests.get('https://httpbin.org/ip', timeout=10)
                # 恢复原始的socket对象
                socket.socket = original_socket

            # 如果请求成功，将代理写入输出文件
            if response.status_code == 200:
                with open(output_file, 'a') as f:
                    f.write(f"{proxy}\n")
                return True
        except Exception as e:
            return False

    def fofa_query(self, query, size=100):
        # 对FOFA进行查询
        # 将查询字符串编码为base64格式
        encoded_query = base64.b64encode(query.encode("utf-8")).decode("utf-8")
        # 构造请求参数
        params = {
            "email": FOFA_EMAIL,  # FOFA账户邮箱
            "key": FOFA_API_KEY,  # FOFA API密钥
            "qbase64": encoded_query,  # 编码后的查询字符串
            "size": size,  # 查询结果数量
            "fields": "ip,port,protocol"  # 需要返回的字段：IP、端口、协议
        }
        # 发送GET请求到FOFA API
        response = requests.get(FOFA_API_URL, params=params)
        # 检查响应状态码，如果不是200则请求失败
        if response.status_code != 200:
            print(f"FOFA API请求失败，状态码：{response.status_code}")
            return []
        # 解析响应的JSON数据
        data = response.json()
        # 检查是否存在错误信息
        if data.get("error"):
            print(f"FOFA API返回错误：{data.get('errmsg')}")
            return []
        # 返回查询结果，如果没有结果则返回空列表
        return data.get("results", [])

    def validate_country_code(self, country_code):
        # 验证国家代码是否有效
        # 使用正则表达式匹配国家代码
        # 正则表达式 ^[A-Z]{2}$ 表示匹配两个大写字母
        # re.match 函数用于从字符串的开始位置匹配正则表达式
        # bool 函数将匹配结果转换为布尔值，匹配成功返回 True，否则返回 False
        return bool(re.match(r'^[A-Z]{2}$', country_code))

    def validate_proxy_type(self, proxy_type):
        # 验证代理类型是否有效
        # 检查传入的proxy_type是否在允许的类型列表中
        # 允许的类型有 'http', 'socks4', 'socks5'
        return proxy_type in ['http', 'socks4', 'socks5']

    def save_proxies(self, proxies, filename):
        # 将代理保存到文件
        # 使用with语句打开文件，确保文件在操作完成后自动关闭
        with open(filename, 'w') as f:
            # 遍历代理列表proxies
            for p in proxies:
                # 将每个代理的IP和端口以"IP:端口"的格式写入文件，并在每行末尾添加换行符
                f.write(f"{p[0]}:{p[1]}\n")
        # 打印保存成功的消息，包括文件名
        print(f"代理已保存到 {filename}")

    def test_and_save_working_proxies(self, proxies, proxy_type, output_file):
        # 测试并保存可用的代理
        working_proxies = []
        # 遍历所有代理
        for p in proxies:
            ip, port, protocol = p
            protocol = protocol.lower()
            # 根据代理类型和协议进行匹配
            # 如果匹配成功，则将代理添加到working_proxies列表中
            if (protocol in ['http', 'https'] and proxy_type == 'http') or \
                (protocol == 'socks4' and proxy_type == 'socks4') or \
                (protocol == 'socks5' and proxy_type == 'socks5'):
                proxy = f"{ip}:{port}"
                # 测试代理是否可用
                if self.test_proxy(proxy, output_file, proxy_type):
                    working_proxies.append(proxy)
        return working_proxies

    def fofa_menu(self):
        # FOFA查询菜单
        print("\n----- FOFA 检索 -----")
        # 提示用户输入FOFA查询语句
        query = input("请输入 FOFA 查询语句: ")
        # 提示用户输入查询结果数量，并转换为整数
        size = int(input("请输入查询结果数量（最大 10000）: "))
        # 调用fofa_query方法进行查询，并获取代理列表
        proxies = self.fofa_query(query, size)

        # 如果未找到代理，打印提示信息并返回
        if not proxies:
            print("未找到代理。")
            return

        # 调用save_proxies方法保存代理列表到文件'fofa_results.txt'
        self.save_proxies(proxies, 'fofa_results.txt')

        # 提示用户是否进行可用性测试，并去除输入的前后空格并转换为小写
        test_choice = input("是否进行可用性测试？(y/n): ").strip().lower()
        # 如果用户选择不进行测试，直接返回
        if test_choice != 'y':
            return

        # 调用test_and_save_working_proxies方法测试代理的可用性，并保存可用代理到文件'fofa_working.txt'
        working_proxies = self.test_and_save_working_proxies(proxies, 'all', 'fofa_working.txt')
        # 打印找到的可用代理数量，并提示已保存到文件
        print(f"找到 {len(working_proxies)} 个可用代理，已保存到 fofa_working.txt")

    def proxy_menu(self):
        # 代理IP获取菜单
        print("\n----- 代理 IP 获取 -----")
        # 获取用户输入的代理类型，并将其转换为小写
        proxy_type = input("请选择代理类型（http/socks4/socks5）: ").lower()
        # 验证代理类型是否有效
        if not self.validate_proxy_type(proxy_type):
            print("无效的代理类型，请输入 http、socks4 或 socks5。")
            return

        # 获取用户输入的国家代码，去除前后空格并转换为大写
        country_code = input("请输入国家代码（例如 US、CN）: ").strip().upper()
        # 验证国家代码是否有效
        if not self.validate_country_code(country_code):
            print("无效的国家代码，请输入两位大写字母。")
            return

        # 获取用户输入的代理数量
        size = int(input("请输入数量（最大 10000）: "))

        # 构造查询语句
        query = f'protocol="{proxy_type}" && country="{country_code}"'
        # 使用fofa_query方法查询代理
        proxies = self.fofa_query(query, size)

        # 如果未找到代理，则提示用户
        if not proxies:
            print("未找到代理。")
            return

        # 构造保存代理的文件名
        filename = f"{proxy_type}_{country_code}_proxies.txt"
        # 保存代理到文件
        self.save_proxies(proxies, filename)

        # 获取用户是否进行代理验证的选择
        test_choice = input("是否进行代理验证？(y/n): ").strip().lower()
        # 如果用户选择不进行验证，则直接返回
        if test_choice != 'y':
            return

        # 验证并保存可用的代理
        working_proxies = self.test_and_save_working_proxies(proxies, proxy_type, 'working_proxies.txt')
        # 输出验证结果
        print(f"验证完成，可用代理数：{len(working_proxies)}，已保存到 working_proxies.txt")

def main_menu():
    # 创建一个ProxyManager对象，用于管理代理
    proxy_manager = ProxyManager()
    # 无限循环，直到用户选择退出
    while True:
        # 打印主菜单
        print("\n----- 主菜单 -----")
        print("1. FOFA 检索代理")
        print("2. 获取国家代理")
        print("3. 退出")
        # 获取用户输入的选择，并去除前后空格
        choice = input("请选择操作（1/2/3）: ").strip()

        # 根据用户的选择执行相应的操作
        if choice == '1':
            # 如果选择1，调用ProxyManager的fofa_menu方法
            proxy_manager.fofa_menu()
        elif choice == '2':
            # 如果选择2，调用ProxyManager的proxy_menu方法
            proxy_manager.proxy_menu()
        elif choice == '3':
            # 如果选择3，退出程序
            sys.exit(0)
        else:
            # 如果输入无效，提示用户重新选择
            print("无效输入，请重新选择。")

if __name__ == '__main__':
    main_menu()