#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2025/10/16
@author: Irony
@site: https://pyqt.site | https://github.com/PyQt5
@email: 892768447@qq.com
@file: test.py
@description:
"""

import json
import os
import sys
from pathlib import Path

from PySide2.QtCore import QFile, QIODevice, QResource, QTimer, Signal
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWebSockets import QWebSocket, QWebSocketProtocol
from PySide2.QtWidgets import QApplication, QWidget

CDIR = os.path.dirname(sys.argv[0])
UI_DIR = os.path.join(CDIR, "ui")
STYLE_FILE = os.path.join(os.path.dirname(CDIR), "dist", "default.qrcdat")

Widgets = []
Url = "ws://localhost:61052"


class QssClient(QWebSocket):
    styleChanged = Signal(str)

    def __init__(self, parent=None):
        super(QssClient, self).__init__(
            "QssClient",
            QWebSocketProtocol.VersionLatest,
            parent,
        )
        self._rcTimer = QTimer(self)
        self.connected.connect(self.handleConnected)
        self.disconnected.connect(self.handleDisconnected)
        self.textMessageReceived.connect(self.handleTextMessage)
        self._rcTimer.timeout.connect(self.start)

    def __del__(self):
        try:
            self.stop()
            self.close()
        except Exception as e:
            print(f"Exception: {e}")

    def start(self):
        self._rcTimer.stop()
        self.open(Url)

    def stop(self):
        self.blockSignals(True)
        self._rcTimer.stop()

    def handleConnected(self):
        print("QssClient connected")

    def handleDisconnected(self):
        print("QssClient disconnected")
        if not self._rcTimer.isActive():
            self._rcTimer.start(5000)

    def handleTextMessage(self, message):
        if not message or message.find("setStyleSheet") == -1:
            return
        try:
            info = json.loads(message)
            style = "\n".join(info.get("params", []))
            if style:
                self.styleChanged.emit(style)
        except Exception as e:
            print(f"Error parsing message: {e}")


def test():
    loader = QUiLoader()
    for path in Path(UI_DIR).rglob("*.ui"):
        w: QWidget = loader.load(str(path))
        Widgets.append(w)
        w.show()


def loadStyle(app):
    if os.path.exists(STYLE_FILE):
        if not QResource.registerResource(STYLE_FILE):
            print("Error loading style resource")
            return
        file = QFile(":/shadcn/default.qss")
        if file.open(QIODevice.ReadOnly):
            app.setStyleSheet(file.readAll().data().decode())
            file.close()
        else:
            print("Error loading style file")


if __name__ == "__main__":
    import cgitb
    import sys

    cgitb.enable(format="text")
    app = QApplication(sys.argv)
    loadStyle(app)

    client = QssClient(app)
    client.styleChanged.connect(app.setStyleSheet)
    client.start()

    test()
    ret = app.exec_()

    QResource.unregisterResource(STYLE_FILE)
    sys.exit(ret)
