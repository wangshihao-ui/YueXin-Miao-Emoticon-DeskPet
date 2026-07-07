# -*- coding: utf-8 -*-
"""
月薪喵虚拟桌面宠物
使用 Windows UpdateLayeredWindow 实现真正逐像素透明
"""
import tkinter as tk
from PIL import Image, ImageSequence, ImageDraw, ImageFont
import os, sys, random, ctypes
from collections import OrderedDict


WS_EX_LAYERED = 0x00080000
ULW_ALPHA = 0x00000002
AC_SRC_OVER = 0x00
AC_SRC_ALPHA = 0x01
ERROR_ALREADY_EXISTS = 183
GW = ctypes.windll.user32
GD = ctypes.windll.gdi32

MUTEX_NAME = "Global\\YuxuemaoPetSingleInstanceMutex"

MOOD_CATEGORIES = {
    "idle":       ["03", "05", "13", "14", "16", "26", "28", "30", "38", "41", "42", "43"],
    "happy":      ["08", "18", "25", "27"],
    "sad":        ["07", "17", "34", "35"],
    "angry":      ["15", "23", "32"],
    "sleepy":     ["10", "20", "33", "36"],
    "excited":    ["21", "39"],
    "shy":        ["45"],
    "eating":     ["06"],
    "working":    ["01", "02", "12", "19", "22", "24", "31", "37", "40"],
    "love":       ["44"],
    "confused":   ["04", "29"],
    "celebrate":  ["11"],
}

GIF_ACTIONS = {
    "01": "熬夜冠军", "02": "喵喵思考中...", "03": "做个裤衩穿上",
    "04": "多变的表情", "05": "放飞气球", "06": "挤点奶油",
    "07": "玩困了...", "08": "优哉游哉", "10": "咪要睡了",
    "12": "电影好好看", "14": "跳跳糖", "15": "谁在来电？",
    "16": "马桶上也想玩手机", "17": "被绑架学习", "20": "晚上手机好好玩",
    "21": "看咪的大雪糕", "22": "换个地方玩手机", "23": "给作者大大发红包",
    "24": "工作so easy", "26": "何事唤咪", "28": "一切都是浮云",
    "29": "咪要抢个新表情", "30": "Dancing", "31": "好像有点不会了",
    "32": "气死咪了！", "33": "不睡了不睡了", "37": "难得咪想上吊","38": "Dancing",
    "40": "快给咪上号！", "41": "闭嘴！咪要看手机", "44": "咪的外卖要到了",
    "45": "哈哈哈哈哈哈",
}

GIF_MESSAGES = {
    "01": ["熬夜冠军在此", "今晚不睡了喵", "越夜越精神~"],
    "02": ["喵喵思考中...", "这个问题有点难", "让我想想喵"],
    "03": ["做个裤衩穿上~", "新衣服真好看", "帅不帅喵~"],
    "04": ["表情变变变", "今天的脸好多变", "看我七十二变"],
    "05": ["放飞气球咯", "飞吧飞吧~", "气球带走烦恼"],
    "06": ["挤点奶油~", "甜甜的最好吃", "再来一点喵"],
    "07": ["玩困了...", "眼皮打架了", "不想动了喵"],
    "08": ["优哉游哉~", "慢慢晃真惬意", "好舒服喵~"],
    "10": ["咪要睡了...", "晚安喵~", "眼皮好重..."],
    "12": ["电影好好看", "这部剧真不错", "再看一集喵"],
    "14": ["跳跳糖！", "噼里啪啦~", "嘴里在跳舞"],
    "15": ["谁在来电？", "不接不接", "烦死了喵"],
    "16": ["马桶上也要玩手机", "再刷五分钟", "蹲麻了喵"],
    "17": ["被绑架学习", "学不动了喵", "知识不进脑子"],
    "20": ["晚上手机好好玩", "睡前刷一刷", "越刷越精神"],
    "21": ["看咪的大雪糕！", "好凉爽~", "一口吃掉喵"],
    "22": ["换个地方玩手机", "这里信号好", "躺平继续刷"],
    "23": ["红包拿来~", "谢谢老板", "给作者发红包喵"],
    "24": ["工作so easy", "小菜一碟", "轻松搞定喵"],
    "26": ["何事唤咪？", "叫我干嘛", "有事快说喵"],
    "28": ["一切都是浮云", "看淡点~", "莫生气喵"],
    "29": ["咪要抢个新表情", "这个表情我要了", "收藏收藏"],
    "30": ["Dancing~", "一起跳舞吧", "摇摆起来喵"],
    "31": ["好像有点不会了", "再教教我嘛", "脑子转不动了"],
    "32": ["气死咪了！", "哼！", "本喵不开心"],
    "33": ["不睡了不睡了", "再玩一会", " sleep 是什么"],
    "37": ["难得咪想上吊", "累瘫了喵", "生活不易"],
    "38": ["Dancing~", "害羞地摇摆", "轻轻跳起来"],
    "40": ["快给咪上号！", "游戏启动", "上线上线喵"],
    "41": ["闭嘴！咪要看手机", "别打扰我", "正忙呢喵"],
    "44": ["咪的外卖要到了", "好期待~", "肚子咕咕叫"],
    "45": ["哈哈哈哈哈哈", "太好笑了", "笑死咪了"],
}


class FrameCache:
    def __init__(self, max_size=20):
        self.max_size = max_size
        self.cache = OrderedDict()

    def get(self, filepath, size):
        key = (filepath, size)
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, filepath, size, frames):
        key = (filepath, size)
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
        self.cache[key] = frames

    def clear(self):
        self.cache.clear()


class _BLENDFUNCTION(ctypes.Structure):
    _fields_ = [("BlendOp", ctypes.c_byte), ("BlendFlags", ctypes.c_byte),
                ("SourceConstantAlpha", ctypes.c_byte), ("AlphaFormat", ctypes.c_byte)]

class _BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32),
                ("biHeight", ctypes.c_int32), ("biPlanes", ctypes.c_uint16),
                ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
                ("biSizeImage", ctypes.c_uint32), ("biXPelsPerMeter", ctypes.c_int32),
                ("biYPelsPerMeter", ctypes.c_int32), ("biClrUsed", ctypes.c_uint32),
                ("biClrImportant", ctypes.c_uint32)]

class _POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class _SIZE(ctypes.Structure):
    _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]


def _resource_path(relative):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative)


class YuxuemaoPet:
    def __init__(self, root, gif_folder):
        self.root = root
        self.gif_folder = gif_folder
        self.root.title("yuxuemao")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        self.pet_size = 143
        self.extra_h = 38
        self.pet_display_size = 128
        self.win_w = self.pet_size
        self.win_h = self.pet_size + self.extra_h

        self.root.geometry(f"{self.win_w}x{self.win_h}")
        self._center_on_screen()
        self.root.update_idletasks()

        hwnd = GW.GetParent(self.root.winfo_id())
        self.hwnd = hwnd if hwnd else self.root.winfo_id()
        ex = GW.GetWindowLongW(self.hwnd, -20)
        GW.SetWindowLongW(self.hwnd, -20, ex | WS_EX_LAYERED)

        self.mood = "idle"
        self.is_dragging = False
        self._click_start = (0, 0)
        self._window_start = (0, 0)
        self.gif_map = {}
        self.all_gif_paths = []
        self.frame_cache = FrameCache()
        self.current_frames = []
        self.frame_index = 0
        self.current_gif_num = "01"
        self.action_text = None
        self.action_timer = None
        self.speech_text = None
        self.speech_timer = None
        self._font_cache = {}
        self._bmi = _BITMAPINFOHEADER()
        self._bmi.biSize = ctypes.sizeof(_BITMAPINFOHEADER)
        self._bmi.biPlanes = 1
        self._bmi.biBitCount = 32
        self._bmi.biCompression = 0

        self._load_gif_list()

        self.root.bind("<Button-1>", self._on_click)
        self.root.bind("<B1-Motion>", self._on_drag)
        self.root.bind("<ButtonRelease-1>", self._on_release)
        self.root.bind("<Button-3>", self._on_right_click)

        self._switch_mood("idle")
        self._animate()
        self._idle_tick()

    def _center_on_screen(self):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{sw - self.win_w - 40}+{sh - self.win_h - 80}")

    def _get_font(self, size):
        if size not in self._font_cache:
            for name in ("msyh.ttc", "simhei.ttf", "arial.ttf"):
                try:
                    self._font_cache[size] = ImageFont.truetype(name, size)
                    break
                except Exception:
                    continue
            else:
                self._font_cache[size] = ImageFont.load_default()
        return self._font_cache[size]

    def _load_gif_list(self):
        files = os.listdir(self.gif_folder)
        num_map = {}
        for f in files:
            if not f.lower().endswith(".gif"):
                continue
            base = os.path.splitext(f)[0]
            parts = base.split("_")
            if len(parts) >= 2:
                num_map[parts[-1]] = os.path.join(self.gif_folder, f)
        self.all_gif_paths = list(num_map.values())
        for mood, nums in MOOD_CATEGORIES.items():
            paths = [num_map[n] for n in nums if n in num_map]
            if paths:
                self.gif_map[mood] = paths
        total = sum(len(v) for v in self.gif_map.values())
        print(f"月薪喵: 发现 {total} 个表情, 覆盖 {len(self.gif_map)} 种心情")

    def _load_frames(self, filepath):
        cached = self.frame_cache.get(filepath, self.pet_display_size)
        if cached is not None:
            return cached
        try:
            gif = Image.open(filepath)
            frames = []
            size = (self.pet_display_size, self.pet_display_size)
            for frame in ImageSequence.Iterator(gif):
                frame = frame.convert("RGBA")
                r, g, b, a = frame.split()
                a = a.point(lambda x: 255 if x > 127 else 0)
                frame = Image.merge("RGBA", (r, g, b, a))
                frame = frame.resize(size, Image.Resampling.NEAREST)
                frames.append(frame)
            self.frame_cache.put(filepath, self.pet_display_size, frames)
            return frames
        except Exception as e:
            print(f"加载失败 {filepath}: {e}")
            return []

    def _render_frame(self, pet_frame):
        w, h = self.win_w, self.win_h
        composite = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        px = (w - self.pet_display_size) // 2
        py = 6
        composite.alpha_composite(pet_frame, (px, py))

        if self.speech_text:
            draw = ImageDraw.Draw(composite)
            font = self._get_font(12)
            bbox = draw.textbbox((0, 0), self.speech_text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            bw, bh = tw + 24, th + 18
            bx = (w - bw) // 2
            by = 0
            draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=10,
                                   fill=(255, 255, 255, 230), outline=(255, 140, 0, 255), width=2)
            cx = w // 2
            draw.polygon([(cx - 8, by + bh - 2), (cx + 8, by + bh - 2), (cx, by + bh + 10)],
                         fill=(255, 255, 255, 230), outline=(255, 140, 0, 255))
            draw.text((bx + bw // 2, by + bh // 2), self.speech_text,
                      font=font, fill=(26, 26, 26, 255), anchor="mm")

        if self.action_text:
            draw = ImageDraw.Draw(composite)
            font = self._get_font(12)
            tx, ty = w // 2, py + self.pet_display_size + 3
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx or dy:
                        draw.text((tx + dx, ty + dy), self.action_text,
                                  font=font, fill=(0, 0, 0, 140), anchor="mt")
            draw.text((tx, ty), self.action_text,
                      font=font, fill=(255, 255, 255, 255), anchor="mt")

        return composite

    def _update_layered_window(self, image):
        w, h = image.size
        r, g, b, a = image.split()
        pixel_data = Image.merge("RGBA", (b, g, r, a)).tobytes()

        screen_dc = GW.GetDC(0)
        mem_dc = GD.CreateCompatibleDC(screen_dc)
        bmi = self._bmi
        bmi.biWidth = w
        bmi.biHeight = -h
        bits = ctypes.c_void_p()
        bitmap = GD.CreateDIBSection(screen_dc, ctypes.byref(bmi), 0, ctypes.byref(bits), None, 0)
        old_bmp = GD.SelectObject(mem_dc, bitmap)
        ctypes.memmove(bits, pixel_data, len(pixel_data))

        blend = _BLENDFUNCTION(AC_SRC_OVER, 0, 255, AC_SRC_ALPHA)
        pt_dst = _POINT(self.root.winfo_x(), self.root.winfo_y())
        sz = _SIZE(w, h)
        pt_src = _POINT(0, 0)
        GW.UpdateLayeredWindow(self.hwnd, screen_dc, ctypes.byref(pt_dst),
                               ctypes.byref(sz), mem_dc, ctypes.byref(pt_src),
                               0, ctypes.byref(blend), ULW_ALPHA)
        GD.SelectObject(mem_dc, old_bmp)
        GD.DeleteObject(bitmap)
        GD.DeleteDC(mem_dc)
        GW.ReleaseDC(0, screen_dc)

    def _set_current_gif(self, filepath):
        import re
        m = re.search(r'_(\d+)\.gif', filepath)
        self.current_gif_num = m.group(1) if m else "01"
        self.current_frames = self._load_frames(filepath)
        self.frame_index = 0
        self._clear_action()

    def _switch_mood(self, mood):
        if mood not in self.gif_map:
            mood = "idle"
        self.mood = mood
        paths = self.gif_map.get(mood, [])
        if not paths:
            return
        self._set_current_gif(random.choice(paths))

    def _show_action(self, text):
        if self.action_timer:
            self.root.after_cancel(self.action_timer)
        self.action_text = text
        self.action_timer = self.root.after(2500, self._clear_action)

    def _show_current_action(self):
        if self.current_gif_num in GIF_ACTIONS:
            self._show_action(GIF_ACTIONS[self.current_gif_num])
        else:
            self._clear_action()

    def _clear_action(self):
        if self.action_timer:
            self.root.after_cancel(self.action_timer)
        self.action_text = None
        self.action_timer = None

    def _show_bubble(self, text, duration=3000):
        if self.speech_timer:
            self.root.after_cancel(self.speech_timer)
        self.speech_text = text
        self.speech_timer = self.root.after(duration, self._clear_bubble)

    def _show_current_bubble(self, duration=3000):
        if self.current_gif_num in GIF_MESSAGES:
            self._show_bubble(random.choice(GIF_MESSAGES[self.current_gif_num]), duration)
        else:
            self._clear_bubble()

    def _clear_bubble(self):
        if self.speech_timer:
            self.root.after_cancel(self.speech_timer)
        self.speech_text = None
        self.speech_timer = None

    def _animate(self):
        if self.current_frames:
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            frame = self.current_frames[self.frame_index]
            composite = self._render_frame(frame)
            self._update_layered_window(composite)
        self.root.after(120, self._animate)

    def _on_click(self, event):
        self.is_dragging = False
        self._click_start = (event.x_root, event.y_root)
        self._window_start = (self.root.winfo_x(), self.root.winfo_y())

    def _on_drag(self, event):
        dx = event.x_root - self._click_start[0]
        dy = event.y_root - self._click_start[1]
        self.root.geometry(f"+{self._window_start[0] + dx}+{self._window_start[1] + dy}")
        self.is_dragging = True

    def _on_release(self, event):
        if not self.is_dragging:
            self._pet_pat()
        self.is_dragging = False

    def _pet_pat(self):
        if not self.all_gif_paths:
            return
        self._set_current_gif(random.choice(self.all_gif_paths))
        self._show_current_bubble()

    def _on_right_click(self, event):
        menu = tk.Menu(self.root, tearoff=0, font=("Microsoft YaHei", 9),
                       bg="#2C2C2C", fg="white", activebackground="#FF8C00",
                       activeforeground="white")
        menu.add_command(label="摸一摸", command=self._pet_pat)
        menu.add_command(label="喂食", command=self._feed)
        menu.add_command(label="哄睡觉", command=self._sleep)
        menu.add_command(label="玩耍", command=self._play)
        menu.add_command(label="去搬砖", command=self._work)
        menu.add_command(label="庆祝", command=self._celebrate)
        menu.add_separator()
        menu.add_command(label="放大", command=lambda: self._resize_pet(1.2))
        menu.add_command(label="缩小", command=lambda: self._resize_pet(0.8))
        menu.add_command(label="退出", command=self._quit)
        menu.tk_popup(event.x_root, event.y_root)

    def _feed(self):
        self._switch_mood("eating")
        self._show_current_bubble()
        self.root.after(3000, lambda: self._switch_mood("idle"))

    def _sleep(self):
        self._switch_mood("sleepy")
        self._show_current_bubble()
        self.root.after(4000, lambda: self._switch_mood("idle"))

    def _play(self):
        mood = random.choice(["excited", "happy", "confused"])
        self._switch_mood(mood)
        self._show_current_bubble()
        self.root.after(3000, lambda: self._switch_mood("idle"))

    def _work(self):
        self._switch_mood("working")
        self._show_current_bubble()
        self.root.after(3000, lambda: self._switch_mood("idle"))

    def _celebrate(self):
        self._switch_mood("celebrate")
        self._show_current_bubble(duration=4000)
        self._bounce()
        self.root.after(3000, lambda: self._switch_mood("idle"))

    def _bounce(self):
        orig_y = self.root.winfo_y()
        x = self.root.winfo_x()
        def _up(i):
            if i <= 8:
                self.root.geometry(f"+{x}+{orig_y - i * 4}")
                self.root.after(30, lambda: _up(i + 1))
            else:
                _down(0)
        def _down(i):
            if i <= 8:
                self.root.geometry(f"+{x}+{orig_y - 32 + i * 4}")
                self.root.after(30, lambda: _down(i + 1))
            else:
                self.root.geometry(f"+{x}+{orig_y}")
        _up(0)

    def _resize_pet(self, factor):
        self.pet_display_size = max(50, min(250, int(self.pet_display_size * factor)))
        self.pet_size = self.pet_display_size + 15
        self.win_w = self.pet_size
        self.win_h = self.pet_size + self.extra_h
        self.root.geometry(f"{self.win_w}x{self.win_h}")
        self.frame_cache.clear()
        self._switch_mood(self.mood)

    def _quit(self):
        self.root.destroy()
        sys.exit(0)

    def _idle_tick(self):
        if random.random() < 0.25:
            weights = {"idle": 12, "happy": 10, "excited": 8, "shy": 8, "confused": 8,
                       "love": 8, "sad": 8, "angry": 8, "celebrate": 6,
                       "sleepy": 6, "eating": 5, "working": 5}
            moods, wts = list(weights.keys()), list(weights.values())
            mood = random.choices(moods, weights=wts, k=1)[0]
            self._switch_mood(mood)
            self._show_current_bubble()
            self.root.after(2500, lambda: self._switch_mood("idle"))
        elif random.random() < 0.15:
            x = self.root.winfo_x() + random.randint(-30, 30)
            y = self.root.winfo_y() + random.randint(-20, 20)
            sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            x = max(0, min(x, sw - self.pet_size))
            y = max(0, min(y, sh - self.pet_size - 60))
            self.root.geometry(f"+{x}+{y}")
        self.root.after(random.randint(8000, 15000), self._idle_tick)


def _acquire_mutex():
    handle = ctypes.windll.kernel32.CreateMutexW(None, True, MUTEX_NAME)
    if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        return None
    return handle


def main():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    mutex = _acquire_mutex()
    if mutex is None:
        root = tk.Tk()
        root.withdraw()
        import tkinter.messagebox as mb
        mb.showinfo("月薪喵", "月薪喵已经在运行了哦~")
        root.destroy()
        sys.exit(0)

    gif_folder = _resource_path("\u8868\u60c5\u5305")
    if not os.path.isdir(gif_folder):
        print("\u8868\u60c5\u5305\u6587\u4ef6\u5939\u4e0d\u5b58\u5728: " + gif_folder)
        sys.exit(1)
    print("\u6708\u85aa\u55b5\u684c\u5ba0\u542f\u52a8\u4e2d...")
    root = tk.Tk()
    YuxuemaoPet(root, gif_folder)
    print("\u542f\u52a8\u6210\u529f! \u5de6\u952e\u62d6\u62fd, \u53f3\u952e\u83dc\u5355")
    root.mainloop()


if __name__ == "__main__":
    main()
