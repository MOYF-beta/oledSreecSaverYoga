import tkinter as tk
import threading
import time
import random
import queue
from datetime import datetime
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image, ImageDraw
import screeninfo
import cnlunar

class OLEDProtector:
    def __init__(self):
        # 获取所有显示器的信息
        self.monitors = screeninfo.get_monitors()

        # 创建两个窗口
        self.root1 = tk.Tk()
        self.root2 = tk.Tk()

        # 配置窗口
        self.configure_window(self.root1, self.monitors[0])
        self.configure_window(self.root2, self.monitors[1])

        # 初始时隐藏窗口
        self.root1.withdraw()
        self.root2.withdraw()

        # 更新窗口内容
        self.update_date_info()
        self.update_term_info()
        self.update_clock()

        # 创建系统托盘图标
        self.create_tray_icon()

        # 处理窗口关闭事件
        self.root1.protocol('WM_DELETE_WINDOW', self.hide_window)
        self.root2.protocol('WM_DELETE_WINDOW', self.hide_window)

        # 绑定双击事件关闭窗口
        self.root1.bind('<Double-1>', self.close_window)
        self.root2.bind('<Double-1>', self.close_window)

        # 创建队列来处理主线程的事件
        self.queue = queue.Queue()
        self.root1.after(100, self.process_queue)  # 启动队列处理

    def configure_window(self, window, monitor):
        # 去除窗口装饰
        window.overrideredirect(True)
        # 设置窗口大小和位置
        window.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
        window.configure(background='black')

        # 设置标签
        window.label_time = tk.Label(window, font=('Helvetica', 48), fg='gray', bg='black')
        window.label_date = tk.Label(window, font=('KaiTi', 18), fg='gray', bg='black') # 公元纪年
        window.label_term = tk.Label(window, font=('KaiTi', 18), fg='gray', bg='black') # 当前或下一个节气

        window.label_time.pack(pady=10)
        window.label_date.pack(pady=10)
        window.label_term.pack(pady=10)

    def update_clock(self):
        now = time.strftime("%H:%M")
        for window in [self.root1, self.root2]:
            window.label_time.config(text=now)
        self.move_labels()
        self.root1.after(60000, self.update_clock)  # 每分钟更新一次

    def move_labels(self):
        for window in [self.root1, self.root2]:
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            
            labels = [window.label_date, window.label_time, window.label_term]
            base_x = random.randint(0, screen_width) 
            base_y = random.randint(0, screen_height - int(0.2 * screen_height))  # 基准 y 位置
            
            max_width = 0
            for label in labels:
                max_width = max(max_width, label.winfo_width())

            for label in labels:
                label.place(x=0, y=0)
            for label in labels:
                label.update_idletasks()
                label_height = label.winfo_height()
                label_width = label.winfo_width()
                x = base_x + (max_width - label_width) // 2
                label.place(x=x, y=base_y)
                base_y = int(base_y + label_height + 0.01 * screen_height)

    def update_date_info(self):
        today = datetime.today()
        date_text = f"{today.strftime('%Y年%m月%d日')}"
        for window in [self.root1, self.root2]:
            window.label_date.config(text=date_text)
        self.root1.after(86400000, self.update_date_info)  # 每天更新一次

    def update_term_info(self):
        today = datetime.today().date()
        lunar = cnlunar.Lunar(datetime.today(), godType='8char')
        current_solar_terms = lunar.thisYearSolarTermsDic
        sorted_terms = sorted(current_solar_terms.items(), key=lambda x: (x[1][0], x[1][1]))
        
        next_term = None
        days_remaining = None
        for term, date in sorted_terms:
            term_date = datetime(today.year, date[0], date[1]).date()
            if term_date > today:
                next_term = term
                days_remaining = (term_date - today).days
                break
        if next_term is None:
            next_term = "来年立春"
            days_remaining_str = ""
        else:
            days_remaining_str = "" if days_remaining == 0 else f" {days_remaining}天后"
        
        term_text = f"{next_term}" + days_remaining_str
        for window in [self.root1, self.root2]:
            window.label_term.config(text=term_text)
        
        self.root1.after(86400000, self.update_term_info)  # 每天更新一次

    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), 'black')
        dc = ImageDraw.Draw(image)
        dc.rectangle((0, 0, 64, 64), fill="white")
        self.tray_icon = icon("OLED Protector", image, "OLED Protector", menu=menu(
            item('主屏黑屏', self.show_main_screen),
            item('副屏黑屏', self.show_secondary_screen),
            item('退出程序', self.quit)
        ))
        threading.Thread(target=self.tray_icon.run).start()

    def show_main_screen(self, icon=None, item=None):
        self.queue.put(('show_main',))

    def show_secondary_screen(self, icon=None, item=None):
        self.queue.put(('show_secondary',))

    def hide_window(self, icon=None, item=None):
        self.queue.put(('hide',))

    def close_window(self, event):
        if event.widget == self.root1:
            self.queue.put(('hide', 'root1'))
        elif event.widget == self.root2:
            self.queue.put(('hide', 'root2'))

    def quit(self, icon=None, item=None):
        self.tray_icon.stop()
        self.root1.quit()
        self.root2.quit()

    def process_queue(self):
        while not self.queue.empty():
            command = self.queue.get()
            if command[0] == 'show_main':
                self.root1.deiconify()
                self.root1.lift()  # 确保窗口置顶
            elif command[0] == 'show_secondary':
                self.root2.deiconify()
                self.root2.lift()  # 确保窗口置顶
            elif command[0] == 'hide':
                self.root1.withdraw()
                self.root2.withdraw()
            elif command[0] == 'hide' and command[1] == 'root1':
                self.root1.withdraw()
            elif command[0] == 'hide' and command[1] == 'root2':
                self.root2.withdraw()
        self.root1.after(100, self.process_queue)  # 继续处理队列

if __name__ == '__main__':
    app = OLEDProtector()
    app.root1.mainloop()
