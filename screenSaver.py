import tkinter as tk
import time
import random
import threading
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image, ImageDraw
from datetime import datetime
import cnlunar

class OLEDProtector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.configure(background='black')
        
        self.label_time = tk.Label(self.root, font=('Helvetica', 48), fg='gray', bg='black')
        self.label_date = tk.Label(self.root, font=('KaiTi', 18), fg='gray', bg='black') # 公元纪年
        self.label_term = tk.Label(self.root, font=('KaiTi', 18), fg='gray', bg='black') # 当前或下一个节气
        
        self.label_time.pack(pady=10)
        self.label_date.pack(pady=10)
        self.label_term.pack(pady=10)
        
        self.update_date_info()
        self.update_term_info()
        self.update_clock()

        self.create_tray_icon()
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)
        
    def update_clock(self):
        now = time.strftime("%H:%M")
        self.label_time.config(text=now)
        self.move_labels()
        self.root.after(60000, self.update_clock)
        
    def move_labels(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        labels = [self.label_date, self.label_time, self.label_term]# self.label_ganzhi
        base_x = random.randint(0, screen_width) 
        base_y = random.randint(0, screen_height - int(0.2 * screen_height))  # 基准 y 位置
        
        max_width = 0
        for label in labels:
            max_width = max(max_width,label.winfo_width())

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
        self.label_date.config(text=f"{today.strftime('%Y年%m月%d日')}")
        self.root.after(86400000, self.update_date_info)  # 每天更新一次

    def update_term_info(self):
        today = datetime.today().date()
        lunar = cnlunar.Lunar(datetime.today(), godType='8char')
        current_solar_terms = lunar.thisYearSolarTermsDic
        sorted_terms = sorted(current_solar_terms.items(), key=lambda x: (x[1][0], x[1][1]))
        
        # 查找下一个节气
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
        
        self.label_term.config(text=f"{next_term}" + days_remaining_str)
        
        # 每天更新一次
        self.root.after(86400000, self.update_term_info)  # 86400000毫秒 = 24小时
    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), 'black')
        dc = ImageDraw.Draw(image)
        dc.rectangle((0, 0, 64, 64), fill="white")
        self.tray_icon = icon("OLED Protector", image, "OLED Protector", menu=menu(
            item('黑屏', self.show_window),
            item('隐藏', self.hide_window),
            item('退出', self.quit)
        ))
        threading.Thread(target=self.tray_icon.run).start()
        
    def show_window(self, icon=None, item=None):
        self.root.deiconify()
        
    def hide_window(self, icon=None, item=None):
        self.root.withdraw()
        
    def quit(self, icon=None, item=None):
        self.tray_icon.stop()
        self.root.quit()

if __name__ == '__main__':
    app = OLEDProtector()
    app.root.mainloop()
