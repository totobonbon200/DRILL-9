import os
from pico2d import *

# 자원 경로는 셸 작업 디렉터리와 무관하게 스크립트 폴더 기준
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 상수
FRAME_SIZE = 100
FRAME_COUNT = 8
SPEED = 5
HALF = FRAME_SIZE // 2
CANVAS_W, CANVAS_H = 800, 600
MIN_X, MAX_X = HALF, CANVAS_W - HALF   # 50 ~ 750
MIN_Y, MAX_Y = HALF, CANVAS_H - HALF   # 50 ~ 550

# 시트 행 (clip_draw의 sy: 이미지 아래쪽이 0)
SY_WALK_RIGHT = 100
SY_WALK_LEFT = 0
SY_IDLE_RIGHT = 200
SY_IDLE_LEFT = 300

open_canvas(CANVAS_W, CANVAS_H)
background = load_image(os.path.join(BASE_DIR, 'TUK_GROUND.png'))
character = load_image(os.path.join(BASE_DIR, 'animation_sheet.png'))


def clamp(value, low, high):
    return max(low, min(high, value))


def handle_events():
    global running, dir_x, dir_y, facing

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                running = False
            elif event.key == SDLK_RIGHT:
                dir_x += 1
                facing = 1
            elif event.key == SDLK_LEFT:
                dir_x -= 1
                facing = -1
            elif event.key == SDLK_UP:
                dir_y += 1
            elif event.key == SDLK_DOWN:
                dir_y -= 1
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_RIGHT:
                dir_x -= 1
            elif event.key == SDLK_LEFT:
                dir_x += 1
            elif event.key == SDLK_UP:
                dir_y -= 1
            elif event.key == SDLK_DOWN:
                dir_y += 1


running = True
x, y = 400, 300
frame = 0
dir_x, dir_y = 0, 0
facing = 1  # +1 오른쪽, -1 왼쪽

while running:
    clear_canvas()
    background.draw(400, 300)

    moving = (dir_x != 0 or dir_y != 0)
    if moving:
        sy = SY_WALK_RIGHT if facing > 0 else SY_WALK_LEFT
    else:
        sy = SY_IDLE_RIGHT if facing > 0 else SY_IDLE_LEFT

    character.clip_draw(frame * FRAME_SIZE, sy, FRAME_SIZE, FRAME_SIZE, x, y)
    update_canvas()

    handle_events()

    x = clamp(x + dir_x * SPEED, MIN_X, MAX_X)
    y = clamp(y + dir_y * SPEED, MIN_Y, MAX_Y)
    frame = (frame + 1) % FRAME_COUNT
    delay(0.05)

close_canvas()
