from zz import zApp, zWindow, zWidget


class MainWindow(zWindow):
    def __init__(self):
        super().__init__("main", "window1")

    def __build__(self):
        self.txt.on_changed.add(self.on_txt_changed)

    def btn_clicked(self, wid: zWidget):
        wid.label = self.lbl.text
        self.lbl.text = self.txt.text

    def on_txt_changed(self, wid: zWidget):
        print(wid.text)


if __name__ == '__main__':
    app = zApp()
    app.run(MainWindow())