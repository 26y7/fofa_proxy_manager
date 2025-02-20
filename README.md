# 代理管理器 (Proxy Manager)

## 概述

这个 Python 脚本是一个代理管理器，允许用户通过 FOFA API 查询代理服务器，并测试这些代理的可用性。脚本支持 HTTP、SOCKS4 和 SOCKS5 代理类型，并可以根据国家代码筛选代理。查询结果可以保存到文件中，并且可以进一步测试这些代理的可用性。

## 功能

1. **FOFA 查询**：通过 FOFA API 查询代理服务器，支持自定义查询语句和结果数量。
2. **代理类型选择**：支持 HTTP、SOCKS4 和 SOCKS5 代理类型。
3. **国家代码筛选**：可以根据国家代码筛选代理服务器。
4. **代理测试**：测试代理服务器的可用性，并将可用的代理保存到文件中。
5. **结果保存**：将查询结果和可用的代理保存到本地文件中。

## 依赖

- Python 3.x
- `requests` 库
- `socks` 库 (用于 SOCKS 代理支持)

你可以通过以下命令安装所需的库：

```bash
pip install requests pysocks
```

## 配置

在使用脚本之前，需要配置 FOFA API 的认证信息。将你的 FOFA 邮箱和 API 密钥设置为环境变量：

```bash
export FOFA_EMAIL='your_email@example.com'
export FOFA_API_KEY='your_fofa_api_key'
```

## 使用方法

1. **运行脚本**：

```bash
   python proxy_manager.py
```

2. **主菜单**：

   - **1. FOFA 检索代理**：通过 FOFA API 查询代理服务器。
   - **2. 获取国家代理**：根据国家代码和代理类型查询代理服务器。
   - **3. 退出**：退出程序。

3. **FOFA 检索代理**：
   - 输入 FOFA 查询语句（例如：`protocol="http"`）。
   - 输入查询结果数量（最大 10000）。
   - 查询结果将保存到 `fofa_results.txt` 文件中。
   - 可以选择是否进行代理可用性测试，测试结果将保存到 `fofa_working.txt` 文件中。

4. **获取国家代理**：
   - 选择代理类型（HTTP、SOCKS4、SOCKS5）。
   - 输入国家代码（例如：US、CN）。
   - 输入查询结果数量（最大 10000）。
   - 查询结果将保存到 `{proxy_type}_{country_code}_proxies.txt` 文件中。
   - 可以选择是否进行代理可用性测试，测试结果将保存到 `working_proxies.txt` 文件中。

## 文件说明

- `fofa_results.txt`：保存 FOFA 查询的原始结果。
- `fofa_working.txt`：保存通过可用性测试的代理。
- `{proxy_type}_{country_code}_proxies.txt`：保存根据国家代码和代理类型查询的代理。
- `working_proxies.txt`：保存通过可用性测试的代理。

## 注意事项

- 请确保你的 FOFA API 密钥有足够的权限进行查询。
- 代理测试可能需要一些时间，具体取决于代理的数量和网络状况。
- 脚本中的代理测试使用了 `httpbin.org` 作为测试目标，确保该网站可访问。
