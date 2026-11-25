from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.window import Window
from random import choice, sample, randrange
import time

CYAN = (0.20, 0.82, 0.89, 1)
PALE = (0.81, 0.87, 0.94, 1)
BLUE = (0.25, 0.53, 0.95, 1)
PURPLE = (0.39, 0.39, 0.83, 1)
ORANGE = (1.0, 0.61, 0.0, 1)
WHITE = (1, 1, 1, 1)
DARK = (0.25, 0.31, 0.40, 1)
GREEN = (0.40, 0.83, 0.65, 1)

WORDS = ["PYTHON", "KOMPUTER", "JARINGAN", "DATABASE",
         "INTERNET", "MONITOR", "SISTEM", "PROGRAM"]

def label(text, size, color=WHITE, **kwargs):
    return Label(text=text, font_size=size, color=color, **kwargs)

def button(text, bg, callback, height=48, size=17):
    b = Button(text=text, size_hint_y=None, height=height,
               background_normal="", background_color=bg,
               color=WHITE, font_size=size, bold=True)
    b.bind(on_release=lambda *_: callback())
    return b

class WordQuestApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.home_screen()
        return self.sm

    def background(self, widget, color):
        with widget.canvas.before:
            Color(*color)
            rect = Rectangle(pos=widget.pos, size=widget.size)
        widget.bind(pos=lambda *_: setattr(rect, "pos", widget.pos),
                    size=lambda *_: setattr(rect, "size", widget.size))

    def home_screen(self):
        s = Screen(name="home")
        self.background(s, CYAN)
        root = BoxLayout(orientation="vertical", padding=[22, 14, 22, 18], spacing=5)
        root.add_widget(label("👑", 62, ORANGE, size_hint_y=None, height=72))
        root.add_widget(label("word", 43, WHITE, size_hint_y=None, height=48, bold=True))
        root.add_widget(label("Quest", 58, WHITE, size_hint_y=None, height=65, bold=True))
        # Honeycomb-inspired decorative letter tiles.
        honey = GridLayout(cols=5, spacing=5, size_hint=(1, None), height=205)
        honey_rows = [["Q","U","R","N","T"], ["U","I","Z","R",""],
                      ["","K","N","E",""]]
        for row in honey_rows:
            for ch in row:
                if not ch:
                    honey.add_widget(Label())
                else:
                    active = ch in ("Q","U","I","Z","E")
                    honey.add_widget(Label(text=ch, bold=True, font_size=27,
                                           color=WHITE if active else (0.72,0.84,0.91,1),
                                           size_hint=(1,1)))
        root.add_widget(honey)
        root.add_widget(label("FIND THE HIDDEN WORDS", 17, WHITE,
                              size_hint_y=None, height=40, bold=True))
        root.add_widget(button("PLAY", ORANGE, self.start_game, 62, 26))
        root.add_widget(label("WORD SEARCH PUZZLE GAME", 12, WHITE,
                              size_hint_y=None, height=28))
        s.add_widget(root)
        self.sm.add_widget(s)

    def start_game(self):
        self.words = sample(WORDS, 6)
        self.found = set()
        self.n = 12
        self.board = [["" for _ in range(self.n)] for _ in range(self.n)]
        self.placements = {}
        self.selected = None
        self.make_board()
        self.seconds = 360
        self.sm.switch_to(Screen(name="game"))
        # Rebuild current game screen under the registered screen name.
        old = self.sm.get_screen("game")
        self.sm.remove_widget(old)
        self.game_screen()
        self.start_time = time.time()
        self.clock_event = Clock.schedule_interval(self.tick, 1)

    def make_board(self):
        dirs = [(0,1),(1,0),(1,1),(0,-1),(-1,0),(-1,-1),(1,-1),(-1,1)]
        for word in self.words:
            for _ in range(800):
                dr,dc = choice(dirs)
                r,c = randrange(self.n),randrange(self.n)
                er,ec = r+dr*(len(word)-1),c+dc*(len(word)-1)
                if not (0 <= er < self.n and 0 <= ec < self.n):
                    continue
                cells=[(r+i*dr,c+i*dc) for i in range(len(word))]
                if all(self.board[rr][cc] in ("",word[i]) for i,(rr,cc) in enumerate(cells)):
                    for i,(rr,cc) in enumerate(cells): self.board[rr][cc]=word[i]
                    self.placements[word]=cells
                    break
        for r in range(self.n):
            for c in range(self.n):
                if not self.board[r][c]: self.board[r][c]=choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    def game_screen(self):
        s=Screen(name="game")
        self.background(s, PALE)
        root=BoxLayout(orientation="vertical", padding=8, spacing=5)
        root.add_widget(label("🔎 WORD SEARCH PUZZLE GAME", 21, PURPLE,
                              size_hint_y=None, height=35, bold=True))
        root.add_widget(label("FIND HIDDEN WORDS", 15, (0.18,0.34,0.52,1),
                              size_hint_y=None, height=25, bold=True))
        controls=BoxLayout(size_hint_y=None,height=42,spacing=4)
        controls.add_widget(button("Random Words", self.start_game, BLUE, 42, 12))
        controls.add_widget(button("I give up", self.finish, (0.82,0.08,0.22,1), 42, 12))
        controls.add_widget(button("How to play?", self.help, (0.22,0.48,0.90,1), 42, 12))
        root.add_widget(controls)
        self.progress=ProgressBar(max=100,value=0,size_hint_y=None,height=18)
        root.add_widget(self.progress)
        self.timer_label=label("⏱ 06:00",22,(0.35,0.27,0.38,1),
                               size_hint_y=None,height=34,bold=True)
        root.add_widget(self.timer_label)

        grid=GridLayout(cols=self.n, spacing=1, size_hint=(1,1))
        self.tiles=[]
        for r in range(self.n):
            row=[]
            for c in range(self.n):
                b=Button(text=self.board[r][c], font_size="16sp", bold=True,
                         color=DARK, background_normal="", background_color=WHITE)
                b.bind(on_release=lambda inst, rr=r, cc=c:self.pick(rr,cc))
                grid.add_widget(b); row.append(b)
            self.tiles.append(row)
        root.add_widget(grid)
        self.words_label=label(self.words_text(),13,DARK,size_hint_y=None,height=54)
        root.add_widget(self.words_label)
        self.status=label("Tap the first letter, then the last letter.",12,DARK,
                          size_hint_y=None,height=28)
        root.add_widget(self.status)
        s.add_widget(root)
        self.sm.add_widget(s)
        self.sm.current="game"

    def words_text(self):
        return "   ".join(("✓ " if w in self.found else "")+w for w in self.words)

    def pick(self,r,c):
        if self.selected is None:
            self.selected=(r,c)
            self.tiles[r][c].background_color=(1,0.85,0.35,1)
            self.status.text="Now tap the last letter."
            return
        a=self.selected; self.selected=None
        path=self.get_path(a,(r,c))
        if not path:
            self.reset_tiles(); self.status.text="Choose two ends in a straight line."; return
        value="".join(self.board[rr][cc] for rr,cc in path)
        found=next((w for w in self.words if w not in self.found and w in (value,value[::-1])),None)
        self.reset_tiles()
        if found:
            self.found.add(found)
            for rr,cc in self.placements[found]:
                self.tiles[rr][cc].background_color=GREEN
            self.words_label.text=self.words_text()
            self.progress.value=100*len(self.found)/len(self.words)
            self.status.text=found+" found! +10 points"
            if len(self.found)==len(self.words):
                Clock.schedule_once(lambda *_:self.finish(),0.7)
        else:
            self.status.text="Not a matching word. Try again."

    def get_path(self,a,b):
        dr=b[0]-a[0]; dc=b[1]-a[1]
        if dr==0 and dc==0: return None
        if not (dr==0 or dc==0 or abs(dr)==abs(dc)): return None
        sr=0 if dr==0 else (1 if dr>0 else -1)
        sc=0 if dc==0 else (1 if dc>0 else -1)
        return [(a[0]+i*sr,a[1]+i*sc) for i in range(max(abs(dr),abs(dc))+1)]

    def reset_tiles(self):
        for r in range(self.n):
            for c in range(self.n):
                self.tiles[r][c].background_color = GREEN if any((r,c) in self.placements[w] for w in self.found) else WHITE

    def tick(self,dt):
        self.seconds-=1
        self.timer_label.text=f"⏱ {self.seconds//60:02d}:{self.seconds%60:02d}"
        if self.seconds<=0:
            self.finish()
            return False

    def help(self):
        messagebox_text="Find a word in the letter grid. Tap its first and last letters. Words can go horizontally, vertically, or diagonally, in either direction. Each word is worth 10 points."
        from kivy.uix.popup import Popup
        box=BoxLayout(orientation="vertical",padding=12)
        box.add_widget(label(messagebox_text,16,DARK))
        box.add_widget(button("OK",BLUE,lambda:popup.dismiss()))
        popup=Popup(title="How to play?",content=box,size_hint=(.85,.5))
        popup.open()

    def finish(self):
        if hasattr(self,"clock_event"):
            self.clock_event.cancel()
        if not self.sm.has_screen("result"):
            s=Screen(name="result"); self.sm.add_widget(s)
        s=self.sm.get_screen("result")
        s.clear_widgets()
        self.background(s,(0.25,0.55,0.96,1))
        root=BoxLayout(orientation="vertical",padding=20,spacing=9)
        root.add_widget(label("🏆",75,(1,0.8,0.15,1),size_hint_y=None,height=100))
        win=len(self.found)==len(self.words)
        root.add_widget(label("YOU WIN!" if win else "GAME OVER",32,(1,0.88,0.2,1),
                              size_hint_y=None,height=58,bold=True))
        card=BoxLayout(orientation="vertical",padding=15,spacing=8)
        with card.canvas.before:
            Color(*WHITE); rect=Rectangle(pos=card.pos,size=card.size)
        card.bind(pos=lambda *_:setattr(rect,"pos",card.pos),
                  size=lambda *_:setattr(rect,"size",card.size))
        card.add_widget(label("YOUR RESULT",23,DARK,size_hint_y=None,height=42,bold=True))
        card.add_widget(label(f"TOTAL SCORE     {len(self.found)*10}",25,(0.9,0.3,0.12,1),bold=True))
        card.add_widget(label(f"WORDS FOUND     {len(self.found)} / {len(self.words)}",20,(0.1,0.55,0.8,1),bold=True))
        card.add_widget(label("FOUND WORDS",14,DARK))
        card.add_widget(label(", ".join(sorted(self.found)) or "No words found",14,DARK))
        root.add_widget(card)
        root.add_widget(button("EXIT",ORANGE, self.stop,55,20))
        root.add_widget(button("RESTART", (0.25,0.78,0.08,1), self.start_game,55,20))
        root.add_widget(button("BACK TO MENU",WHITE,self.back_home,45,15))
        root.add_widget(label("HAVE FUN!",30,WHITE,size_hint_y=None,height=45,bold=True))
        s.add_widget(root)
        self.sm.current="result"

    def back_home(self):
        self.sm.current="home"

if __name__ == "__main__":
    WordQuestApp().run()
