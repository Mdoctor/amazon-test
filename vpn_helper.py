import subprocess
import time


class VPNConnector:
    def __init__(self, vpn_name, username, password):
        self.vpn_name = vpn_name
        self.username = username
        self.password = password

    def connect(self):
        """连接到VPN"""
        try:
            result = subprocess.run(
                ["rasdial", self.vpn_name, self.username, self.password],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"成功连接到 VPN: {self.vpn_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"连接失败: {e.stderr.strip()}")
            return False

    def disconnect(self):
        """断开VPN连接"""
        try:
            subprocess.run(
                ["rasdial", self.vpn_name, "/DISCONNECT"],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"已断开 VPN: {self.vpn_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"断开失败: {e.stderr.strip()}")
            return False

    def is_connected(self):
        """检测当前VPN是否已连接"""
        try:
            # 通过 rasdial 命令获取当前连接列表
            result = subprocess.run(
                ["rasdial"], capture_output=True, text=True, check=True
            )
            # 检查当前VPN名称是否在输出中
            return self.vpn_name in result.stdout
        except subprocess.CalledProcessError:
            return False

    def get_connection_details(self):
        """获取当前连接的详细信息"""
        try:
            result = subprocess.run(
                ["rasdial", self.vpn_name], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"无法获取连接状态: {e.stderr.strip()}"


# 使用示例
if __name__ == "__main__":
    # 替换为你的VPN配置
    vpn = VPNConnector(
        vpn_name="YourVPNName",  # 在Windows中预先配置的VPN名称
        username="your_username",
        password="your_password",
    )

    # 连接VPN
    if vpn.connect():
        print("正在检查连接状态...")
        time.sleep(3)
        if vpn.is_connected():
            print("当前状态: 已连接")
            print("连接详情:\n", vpn.get_connection_details())
        else:
            print("当前状态: 未连接")

    # 断开VPN
    time.sleep(10)
    vpn.disconnect()
