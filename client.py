from pygame import *
import socket, json
from threading import Thread

# розміри екрана
W, H = 800, 600
init()
mixer.init()
scr = display.set_mode((W, H))
clock = time.Clock()
display.set_caption("Пінг-Понг")

# картинки
ball = image.load("png-transparent-tennis-balls-tennis-game-grass-cartoon.png")
ball = transform.scale(ball, (40, 40)) # м'яч трошки менший

p1_img = image.load("jj.png.png")  # синя
p1_img = transform.scale(p1_img, (20, 100))

p2_img = image.load("gg2.png") # біла
p2_img = transform.scale(p2_img, (20, 100))

# конект до сервака
def connect():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', 8080))
            buf = ""
            gs = {}
            my_id = int(s.recv(24).decode())
            return my_id, gs, buf, s
        except:
            pass

def recv():
    global buf, gs, game_over
    while not game_over:
        try:
            d = client.recv(1024).decode()
            buf += d
            while "\n" in buf:
                pkt, buf = buf.split("\n", 1)
                if pkt.strip():
                    gs = json.loads(pkt)
        except:
            gs["winner"] = -1
            break

# шрифт
f_win = font.Font("Edu_NSW_ACT_Cursive\\EduNSWACTCursive-VariableFont_wght.ttf", 72)
f_main = font.Font("Edu_NSW_ACT_Cursive\\EduNSWACTCursive-VariableFont_wght.ttf", 36)

# фон і звуки
bg = image.load("reg.png")
bg = transform.scale(bg, (W, H))
snd_wall = mixer.Sound("power-punch-192118.mp3")

# змінні
game_over = False
you_win = None
my_id, gs, buf, client = connect()
Thread(target=recv, daemon=True).start()

while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

    # відлік перед стартом
    if "countdown" in gs and gs["countdown"] > 0:
        scr.fill((0, 0, 0))
        t = font.Font(None, 72).render(str(gs["countdown"]), True, (255, 255, 255))
        scr.blit(t, (W // 2 - 20, H // 2 - 30))
        display.update()
        continue

    # якщо хтось виграв
    if "winner" in gs and gs["winner"] is not None:
        scr.fill((20, 20, 20))
        if you_win is None:
            you_win = (gs["winner"] == my_id)

        msg = "You win!" if you_win else "Better luck next time!"
        t = f_win.render(msg, True, (255, 215, 0))
        scr.blit(t, t.get_rect(center=(W // 2, H // 2)))
        display.update()
        continue

    # сама гра
    if gs:
        scr.blit(bg, (0, 0))

        # малюю ракетки
        scr.blit(p1_img, (20, gs['paddles']['0']))
        scr.blit(p2_img, (W - 40, gs['paddles']['1']))

        # м'яч
        scr.blit(ball, (gs['ball']['x'], gs['ball']['y']))

        # верхня панель
        draw.rect(scr, (40, 40, 40), (0, 0, W, 40))
        st = f_main.render(f"Player: {my_id + 1}", True, (255, 255, 255))
        scr.blit(st, (10, 10))

        # надпис YOU
        if my_id == 0:
            lbl = f_main.render("YOU", True, (0, 180, 255))
            scr.blit(lbl, (20, gs['paddles']['0'] + 40))
        else:
            lbl = f_main.render("YOU", True, (255, 100, 0))
            scr.blit(lbl, (W - 70, gs['paddles']['1'] + 40))

        
        draw.rect(scr, (180, 180, 180), (0, 40, W, H - 40), 4)

        # рахунок
        score_t = f_main.render(f"{gs['scores'][0]} : {gs['scores'][1]}", True, (255, 255, 255))
        scr.blit(score_t, (W // 2 - 25, 10))

        
        if gs['sound_event']:
            if gs['sound_event'] == 'wall_hit':
                snd_wall.play()

    else:
        wait_t = f_main.render(f"Waiting players", True, (255, 255, 255))
        scr.blit(wait_t, (W // 2 - 100, 20))

    display.update()
    clock.tick(60)

    # керування
    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")

