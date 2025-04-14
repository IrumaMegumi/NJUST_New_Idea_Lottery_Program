import sys
import os
import random
import threading
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QMessageBox, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QPixmap

# 设置缓存目录到 AppData\Local\KeywordSelector
appdata_path = os.getenv('LOCALAPPDATA')
program_folder = os.path.join(appdata_path, 'KeywordSelector')
os.makedirs(program_folder, exist_ok=True)
USED_WORDS_FILE = os.path.join(program_folder, 'used_words.txt')

# 原始字典
def load_words():
    main_word_dict = {
        0: '情绪价值', 1: '社交能耗', 2: '信息茧房', 3: '被动学习',
        4: '思维惰性', 5: '新质生产力', 6: '专注力流失', 7: '时间碎片化',
        8: 'AI过度依赖', 9: '无纸化学习', 10: '产学研联合', 11: '“内卷式”竞争',
        12: '自媒体创业', 13: '科技成果转化', 14: '适应与改变', 15: '教室沉默',
        16: '35岁危机', 17: '创新驱动力', 18: '智能教育', 19: '未来产业',
        20: '人工智能+', 21: '电影哪吒', 22: '人际关系', 23: '创新与创业',
        24: '选择大于努力', 25: 'AI焦虑', 26: '多学科融合', 27: '学历贬值',
        28: '理论与实践', 29: '中国智造'
    }
    return main_word_dict

# 读取已使用关键词
def load_used_words():
    if not os.path.exists(USED_WORDS_FILE):
        return set()
    with open(USED_WORDS_FILE, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

# 保存已使用关键词
def save_used_word(word):
    with open(USED_WORDS_FILE, 'a', encoding='utf-8') as f:
        f.write(word + '\n')

# 清空缓存文件
def clear_used_words():
    if os.path.exists(USED_WORDS_FILE):
        os.remove(USED_WORDS_FILE)

class Worker(QObject):
    update_keyword = pyqtSignal(str)

    def __init__(self, word_list):
        super().__init__()
        self.word_list = word_list
        self.running = False

    def start_shuffling(self):
        self.running = True
        while self.running and self.word_list:
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
        self.main_word_dict = load_words()
        self.used_words = load_used_words()
        self.available_words = [word for word in self.main_word_dict.values() if word not in self.used_words]
        self.main_worker = None
        self.main_thread = None

    def init_ui(self):
        font = QFont("微软雅黑", 16)
        self.setFont(font)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("请输入你的姓名")

        self.background_label = QLabel(self)

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        background_path = os.path.join(base_path, "background.png")

        pixmap = QPixmap(background_path)
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
        self.stop_button = QPushButton("停止", self)
        self.clear_button = QPushButton("清空信息", self)
        self.clear_record_button = QPushButton("清空抽取记录", self)
        self.close_button = QPushButton("关闭", self)

        self.draw_button.clicked.connect(self.start_drawing)
        self.stop_button.clicked.connect(self.stop_drawing)
        self.clear_button.clicked.connect(self.clear_info)
        self.clear_record_button.clicked.connect(self.clear_record)
        self.close_button.clicked.connect(self.close)

        vbox = QVBoxLayout()
        vbox.addWidget(self.name_input)
        vbox.addWidget(self.background_label)

        hbox = QHBoxLayout()
        hbox.addWidget(self.draw_button)
        hbox.addWidget(self.stop_button)
        hbox.addWidget(self.clear_button)
        hbox.addWidget(self.clear_record_button)
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

        if not self.available_words:
            QMessageBox.information(self, "提示", "所有关键词都已经抽取完毕！")
            return

        if self.main_worker and self.main_worker.running:
            self.main_worker.stop()
            if self.main_thread and self.main_thread.is_alive():
                self.main_thread.join()

        self.main_worker = Worker(self.available_words)
        self.main_worker.update_keyword.connect(self.update_display)
        self.main_thread = threading.Thread(target=self.main_worker.start_shuffling)
        self.main_thread.start()

        self.draw_button.setEnabled(False)

    def stop_drawing(self):
        if self.main_worker and self.main_worker.running:
            self.main_worker.stop()
            if self.main_thread and self.main_thread.is_alive():
                self.main_thread.join()
            selected_word = self.keyword_display.text()
            if selected_word and selected_word != "等待抽取...":
                if selected_word in self.available_words:
                    self.available_words.remove(selected_word)
                    save_used_word(selected_word)

        self.draw_button.setEnabled(True)

    def clear_info(self):
        self.name_input.clear()
        self.keyword_display.setText("等待抽取...")
        self.stop_drawing()

    def clear_record(self):
        clear_used_words()
        self.used_words = set()
        self.available_words = list(self.main_word_dict.values())
        QMessageBox.information(self, "提示", "抽取记录已清空！")

    def update_display(self, keyword):
        self.keyword_display.setText(keyword)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = KeywordApp()
    window.resize(800, 450)
    window.show()
    sys.exit(app.exec_())
