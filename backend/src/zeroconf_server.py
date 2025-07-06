from zeroconf import IPVersion, ServiceInfo, Zeroconf
import time

class Server:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.ip = self._get_ip()

    def _get_ip(self):
        # 获取本地IP地址
        # 这里可以使用其他方式获取IP地址，例如socket或者requests库
        return "192.168.0.100"

    def broadcast(self):
        # 广播设备信息
        info = ServiceInfo("_http._tcp.local.",
                           f"{self.name}._http._tcp.local.",
                           addresses=[self.ip],
                           port=self.port,
                           weight=0,
                           priority=0,
                           properties={},
                           server=f"{self.name}.local.")
        zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
        zeroconf.register_service(info)

    def stop_broadcast(self):
        # 停止广播设备信息
        zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
        zeroconf.unregister_all_services()
        zeroconf.close()

    def handle_connection(self, socket, data):
        # 处理其他设备的连接请求
        # 例如，可以通过socket进行通信，处理其他设备发送的数据
        pass

    def run(self):
        # 运行设备服务端
        # 在该方法中，我们可以使用socket库来接收其他设备的连接请求，并调用handle_connection方法来处理请求
        pass

class Client:
    def find_devices(self):
        # 发现其他设备
        devices = []
        zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
        service_infos = zeroconf.get_service_info("_http._tcp.local.","LabPlatformServer._http._tcp.local.")
        print(service_infos.addresses)
        # for info in service_infos.values():
        #     devices.append({
        #         "name": info.name.split("._")[0],
        #         "ip": info.addresses[0],
        #         "port": info.port
        #     })
        zeroconf.close()
        return devices

    def connect_to_device(self, device):
        # 连接其他设备
        # 例如，可以使用socket库来连接其他设备的IP地址和端口号，实现设备间的通信
        pass

    def run(self):
        # 运行设备客户端
        # 在该方法中，我们可以使用find_devices方法来发现其他设备，并调用connect_to_device方法来连接其他设备
        pass

if __name__ == "__main__":
    server = Server("LabPlatformServer", 8000)
    server.broadcast()
    client = Client()
    devices = client.find_devices()
    print(f"Devices found: {devices}")
    while True:
        time.sleep(0.1)

