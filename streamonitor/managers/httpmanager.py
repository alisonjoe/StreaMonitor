from flask import Flask, request, render_template, jsonify
import os
import zmq
from collections import namedtuple
from streamonitor.bot import Bot
import streamonitor.log as log
from streamonitor.manager import Manager

app = Flask(__name__)

class HTTPManager(Manager):
    def __init__(self, streamers):
        super().__init__(streamers)
        self.logger = log.Logger("manager")

    def run(self):
        @app.route('/')
        def status():
            return render_template('status.html', streamers=self.streamers)

        def get_file_size(file_path):
            return os.path.getsize(file_path)

        def format_file_size(file_size):
            # 定义单位后缀
            suffixes = ['B', 'KB', 'MB', 'GB', 'TB']

            # 递归转换大小并选择合适的单位
            index = 0
            while file_size >= 1024 and index < len(suffixes) - 1:
                file_size /= 1024
                index += 1

            # 格式化输出文件大小
            return f"{file_size:.2f} {suffixes[index]}"

        @app.route('/recordings')
        def recordings():
            user = request.args.get("user")
            site = request.args.get("site")
            streamer = self.getStreamer(user, site)
            recordings_list = []
            real_recordings_list = []
            try:
                directory = f"./downloads/{user} [{site}]"
                recordings_list = os.listdir(directory)
                for recording in recordings_list:
                    file_path = os.path.join(directory, recording)
                    file_size = format_file_size(get_file_size(file_path))
                    file = f"{recording} ---- {file_size}"
                    real_recordings_list.append(file)
            except FileNotFoundError:
                pass

            return render_template('recordings.html', streamer=streamer, recordings=real_recordings_list)

        @app.route('/add_streamer', methods=['POST'])
        def add_streamer():
            # 在这里处理按钮点击触发的操作
            # 你可以调用 Bot 或执行其他逻辑

            # 构造消息
            message = [
                'add',
                request.json['username'],
                request.json['website']
            ]

            # 使用 ZeroMQ Socket 发送消息给服务器
            socket = zmq.Context.instance().socket(zmq.REQ)
            socket.connect('tcp://127.0.0.1:6969')

            # 发送消息
            socket.send_string(' '.join(message))

            # 接收服务器响应
            response = socket.recv_string()

            # 关闭 Socket
            socket.close()

            return jsonify({'message': response})

        @app.route('/toggle_streamer', methods=['POST'])
        def toggle_streamer():
            # 在这里处理按钮点击触发的操作
            # 你可以调用 Bot 或执行其他逻辑

            # 构造消息
            message = [
                request.json['operation'],
                request.json['username'],
            ]

            # 使用 ZeroMQ Socket 发送消息给服务器
            socket = zmq.Context.instance().socket(zmq.REQ)
            socket.connect('tcp://127.0.0.1:6969')

            # 发送消息
            socket.send_string(' '.join(message))

            # 接收服务器响应
            response = socket.recv_string()

            # 关闭 Socket
            socket.close()

            return jsonify({'message': response})

        @app.route('/remove_streamer', methods=['POST'])
        def remove_streamer():
            # 在这里处理按钮点击触发的操作
            # 你可以调用 Bot 或执行其他逻辑

            # 构造消息
            message = [
                'remove',
                request.json['username']
            ]

            # 使用 ZeroMQ Socket 发送消息给服务器
            socket = zmq.Context.instance().socket(zmq.REQ)
            socket.connect('tcp://127.0.0.1:6969')

            # 发送消息
            socket.send_string(' '.join(message))

            # 接收服务器响应
            response = socket.recv_string()

            # 关闭 Socket
            socket.close()

            return jsonify({'message': response})

        app.run(host='127.0.0.1', port=5000)
