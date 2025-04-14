import sys
import random
import threading
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QMessageBox, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QPixmap

# 原始字典
def load_words():
    main_word_dict = {
        0: '情绪价值', 1: '社交能耗', 2: '信息茧房', 3: '被动学习',
        4: '思维惰性', 5: '唯成绩论', 6: '专注力流失', 7: '时间碎片化',
        8: 'AI过度依赖', 9: '无纸化学习', 10: '产学研联合', 11: '“内卷式”竞争',
        12: '自媒体创业', 13: '天坑专业', 14: '适应与改变', 15: '教室沉默',
        16: '35岁危机', 17: '创新驱动力', 18: '智能教育', 19: '未来产业'
    }
    supplement_word_dict = {
        0: '唯成绩论', 1: '电影哪吒', 2: '人际关系', 3: '水课',
        4: '选择大于努力', 5: 'AI焦虑', 6: '多学科融合', 7: '学历贬值',
        8: '理论与实践', 9: '中国智造'
    }
    return main_word_dict, supplement_word_dict

class Worker(QObject):
    update_keyword = pyqtSignal(str)

    def __init__(self, word_list):
        super().__init__()
        self.word_list = word_list
        self.running = False

    def start_shuffling(self):
        self.running = True
        while self.running:
            random.shuffle(self.word_list)
            keyword = self.word_list[0]
            self.update_keyword.emit(keyword)
            time.sleep(0.05)

    def stop(self):
        self.running = False

class KeywordApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("关键词抽取器")
        self.init_ui()
        self.main_word_dict, self.supplement_word_dict = load_words()
        self.main_worker = None
        self.supplement_worker = None
        self.main_thread = None
        self.supplement_thread = None

    def init_ui(self):
        font = QFont("微软雅黑", 16)
        self.setFont(font)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("请输入你的姓名")

        self.background_label = QLabel(self)
        pixmap = QPixmap("background.png")
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.background_opacity = QGraphicsOpacityEffect()
        self.background_opacity.setOpacity(0.25)
        self.background_label.setGraphicsEffect(self.background_opacity)
        self.background_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.keyword_display = QLabel("等待抽取...", self)
        self.keyword_display.setAlignment(Qt.AlignCenter)
        self.keyword_display.setStyleSheet("""
            font-size: 56px;
            font-weight: bold;
            font-family: 微软雅黑;
            color: black;
            background-color: transparent;
        """)
        self.keyword_display.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.draw_button = QPushButton("抽取", self)
        self.redraw_button = QPushButton("我不懂，需要重新抽取", self)
        self.stop_button = QPushButton("停止", self)
        self.clear_button = QPushButton("清空信息", self)
        self.close_button = QPushButton("关闭", self)

        self.draw_button.clicked.connect(self.start_drawing)
        self.redraw_button.clicked.connect(self.start_redrawing)
        self.stop_button.clicked.connect(self.stop_drawing)
        self.clear_button.clicked.connect(self.clear_info)
        self.close_button.clicked.connect(self.close)

        vbox = QVBoxLayout()
        vbox.addWidget(self.name_input)
        vbox.addWidget(self.background_label)

        hbox = QHBoxLayout()
        hbox.addWidget(self.draw_button)
        hbox.addWidget(self.redraw_button)
        hbox.addWidget(self.stop_button)
        hbox.addWidget(self.clear_button)
        hbox.addWidget(self.close_button)

        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.background_label.resize(self.size())
        self.keyword_display.resize(self.size())
        self.keyword_display.raise_()

    def start_drawing(self):
        name = self.name_input.text()
        if not name:
            QMessageBox.warning(self, "警告", "请输入你的姓名！")
            return

        if self.main_worker and self.main_worker.running:
            self.main_worker.stop()
            if self.main_thread and self.main_thread.is_alive():
                self.main_thread.join()

        word_list = list(self.main_word_dict.values())
        self.main_worker = Worker(word_list)
        self.main_worker.update_keyword.connect(self.update_display)
        self.main_thread = threading.Thread(target=self.main_worker.start_shuffling)
        self.main_thread.start()

        self.draw_button.setEnabled(False)
        self.redraw_button.setEnabled(False)

    def start_redrawing(self):
        if self.keyword_display.text() in ["等待抽取...", ""]:
            QMessageBox.warning(self, "警告", "请先抽取你的关键词！")
            return

        if self.supplement_worker and self.supplement_worker.running:
            self.supplement_worker.stop()
            if self.supplement_thread and self.supplement_thread.is_alive():
                self.supplement_thread.join()

        word_list = list(self.supplement_word_dict.values())
        self.supplement_worker = Worker(word_list)
        self.supplement_worker.update_keyword.connect(self.update_display)
        self.supplement_thread = threading.Thread(target=self.supplement_worker.start_shuffling)
        self.supplement_thread.start()

        self.draw_button.setEnabled(False)
        self.redraw_button.setEnabled(False)

    def stop_drawing(self):
        if self.main_worker and self.main_worker.running:
            self.main_worker.stop()
            if self.main_thread and self.main_thread.is_alive():
                self.main_thread.join()
        if self.supplement_worker and self.supplement_worker.running:
            self.supplement_worker.stop()
            if self.supplement_thread and self.supplement_thread.is_alive():
                self.supplement_thread.join()

        self.draw_button.setEnabled(True)
        self.redraw_button.setEnabled(True)

    def clear_info(self):
        self.name_input.clear()
        self.keyword_display.setText("等待抽取...")
        self.stop_drawing()

    def update_display(self, keyword):
        self.keyword_display.setText(keyword)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = KeywordApp()
    window.resize(700, 400)
    window.show()
    sys.exit(app.exec_())
