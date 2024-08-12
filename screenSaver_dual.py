import tkinter as tk
import threading
import time
import random
import queue
import psutil
from datetime import datetime
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image, ImageDraw
import screeninfo
import cnlunar

class OLEDProtector:
    def __init__(self):
        self.monitors = screeninfo.get_monitors()

        self.root1 = tk.Tk()
        self.root2 = tk.Tk()

        self.configure_window(self.root1, self.monitors[0])
        self.configure_window(self.root2, self.monitors[1])

        self.root1.withdraw()
        self.root2.withdraw()

        self.last_bytes_sent = psutil.net_io_counters().bytes_sent
        self.last_bytes_recv = psutil.net_io_counters().bytes_recv

        self.update_date_info()
        self.update_term_info()
        self.update_clock()
        self.update_system_info()

        self.create_tray_icon()

        self.root1.protocol('WM_DELETE_WINDOW', self.hide_window)
        self.root2.protocol('WM_DELETE_WINDOW', self.hide_window)

        self.root1.bind('<Double-1>', self.close_window)
        self.root2.bind('<Double-1>', self.close_window)
        self.root1.bind('<Button-1>', self.move_labels)
        self.root2.bind('<Button-1>', self.move_labels)

        self.queue = queue.Queue()
        self.root1.after(100, self.process_queue)
        self.move_labels()

    def configure_window(self, window, monitor):
        window.overrideredirect(True)
        window.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
        window.configure(background='black')

        window.label_time = tk.Label(window, font=('Helvetica', 48), fg='gray', bg='black')
        window.label_date = tk.Label(window, font=('KaiTi', 18), fg='gray', bg='black')
        window.label_term = tk.Label(window, font=('KaiTi', 18), fg='gray', bg='black')
        window.label_battery = tk.Label(window, font=('Helvetica', 12), fg='gray', bg='black')
        window.label_network = tk.Label(window, font=('Helvetica', 12), fg='gray', bg='black')
        window.label_cpu = tk.Label(window, font=('Helvetica', 12), fg='gray', bg='black')

        window.label_time.pack(pady=10)
        window.label_date.pack(pady=10)
        window.label_term.pack(pady=10)
        window.label_battery.pack(pady=10)
        window.label_network.pack(pady=10)
        window.label_cpu.pack(pady=10)

    def update_clock(self):
        now = time.strftime("%H:%M")
        for window in [self.root1, self.root2]:
            window.label_time.config(text=now)
        self.move_labels()
        self.root1.after(60000, self.update_clock)

    def move_labels(self,*args):
        for window in [self.root1, self.root2]:
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()

            # 获取上60%和下40%的分界线
            top_area_height = int(screen_height * 0.6)
            bottom_area_start = top_area_height
            bottom_area_height = screen_height - bottom_area_start

            # 顶部60%区域内随机移动的标签
            top_labels = [window.label_date, window.label_time, window.label_term]
            top_base_x = random.randint(0, screen_width)
            top_base_y = random.randint(0, top_area_height - max([label.winfo_height() for label in top_labels]))
            max_top_width = max(label.winfo_width() for label in top_labels)

            for label in top_labels:
                label.place(x=0, y=0)
            for label in top_labels:
                label.update_idletasks()
                label_height = label.winfo_height()
                label_width = label.winfo_width()
                x = top_base_x + (max_top_width - label_width) // 2
                x = max(0, min(screen_width - label_width, x))  # 防止标签溢出屏幕
                y = top_base_y
                y = max(0, min(top_area_height - label_height, y))
                label.place(x=x, y=y)
                top_base_y += label_height + 0.01 * screen_height

            # 底部40%区域内随机移动的标签
            bottom_labels = [window.label_battery, window.label_network, window.label_cpu]
            bottom_base_y = random.randint(bottom_area_start, screen_height - max([label.winfo_height() for label in bottom_labels]))

            for label in bottom_labels:
                label.place(x=0, y=0)
            bottom_base_x = screen_width//2 + random.randint(-screen_width//5,screen_width//5)
            for label in bottom_labels:
                label.update_idletasks()
                label_height = label.winfo_height()
                label.place(x=bottom_base_x, y=bottom_base_y)
                bottom_base_y += label_height + 0.01 * screen_height

    def update_date_info(self):
        today = datetime.today()
        date_text = f"{today.strftime('%Y年%m月%d日')}"
        for window in [self.root1, self.root2]:
            window.label_date.config(text=date_text)
        self.root1.after(86400000, self.update_date_info)

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

        self.root1.after(86400000, self.update_term_info)

    def update_system_info(self):
        def format_speed(speed):
            if speed < 1024:
                return f"{speed:.2f} B/s"
            elif speed < 1024**2:
                return f"{speed / 1024:.2f} KB/s"
            else:
                return f"{speed / 1024**2:.2f} MB/s"

        net = psutil.net_io_counters()
        current_bytes_sent = net.bytes_sent
        current_bytes_recv = net.bytes_recv

        upload_speed = (current_bytes_sent - self.last_bytes_sent) / 5
        download_speed = (current_bytes_recv - self.last_bytes_recv) / 5

        upload_speed_text = format_speed(upload_speed)
        download_speed_text = format_speed(download_speed)
        net_text = f"net\t▲ {upload_speed_text}\t▼ {download_speed_text}"

        battery = psutil.sensors_battery()
        battery_text = f"batt\t{battery.percent}%" if battery else "batt\t--"
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_text = f"cpu\t{cpu_percent}%"

        for window in [self.root1, self.root2]:
            window.label_battery.config(text=battery_text)
            window.label_network.config(text=net_text)
            window.label_cpu.config(text=cpu_text)

        self.last_bytes_sent = current_bytes_sent
        self.last_bytes_recv = current_bytes_recv

        self.root1.after(5000, self.update_system_info)

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
                self.root1.lift()
            elif command[0] == 'show_secondary':
                self.root2.deiconify()
                self.root2.lift()
            elif command[0] == 'hide':
                self.root1.withdraw()
                self.root2.withdraw()
            elif command[0] == 'hide' and command[1] == 'root1':
                self.root1.withdraw()
            elif command[0] == 'hide' and command[1] == 'root2':
                self.root2.withdraw()
        self.root1.after(100, self.process_queue)

if __name__ == '__main__':
    app = OLEDProtector()
    app.root1.mainloop()