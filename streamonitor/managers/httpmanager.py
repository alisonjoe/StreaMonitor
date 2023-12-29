from flask import Flask, request, render_template
import os
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

        @app.route('/recordings')
        def recordings():
            user = request.args.get("user")
            site = request.args.get("site")
            streamer = self.getStreamer(user, site)
            recordings_list = []
            try:
                recordings_list = os.listdir(f"./downloads/{user} [{site}]")
            except FileNotFoundError:
                pass

            return render_template('recordings.html', streamer=streamer, recordings=recordings_list)

        app.run(host='127.0.0.1', port=5000)
