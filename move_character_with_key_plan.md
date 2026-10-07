# 키보드 캐릭터 이동 계획 (move_character_with_key 기준)

## 목표

`move_character_with_key.py`를 기반으로 상하좌우 방향키로 캐릭터를 이동시키는
스크립트 `move_character_with_key_full.py`를 같은 폴더에 새로 만든다.
(원본 `move_character_with_key.py`는 fill-in 연습문제 그대로 보존)

- 배경: `TUK_GROUND.png`
- 캐릭터: `animation_sheet.png`
- 정지 상태에서도 IDLE 애니메이션이 출력된다.
- 위/아래 이동 시에도 좌/우로 바라보던 기존 방향을 유지한다.
- 화면 경계에 도달하면 그 이상 진행하지 않는다.

## 자산 정보 (실측)

| 파일 | 크기 |
|---|---|
| `animation_sheet.png` | 802 x 402 (100 x 100 프레임 8개 x 4행, 여백 2px) |
| `TUK_GROUND.png` | 1280 x 1024 (불투명, 화면보다 큼) |
| canvas | 800 x 600 (기본 `open_canvas()`) |

### 스프라이트 시트 매핑

`clip_draw`의 `sy`는 이미지 아래쪽이 0 기준이므로 이미지 행과 다음과 같이 대응한다.
프레임 폭/높이는 모두 100px, 프레임 수는 8개(`sx = frame * 100`, `frame = 0..7`).

| 상태 | 바라보는 방향 | `sy` | 이미지 행 |
|---|---|---|---|
| IDLE | 오른쪽 | 200 | 2행 |
| IDLE | 왼쪽 | 300 | 1행 |
| WALK | 오른쪽 | 100 | 3행 |
| WALK | 왼쪽 | 0 | 4행 |

- 1/2행(IDLE): 몸통이 세로로 서 있고 프레임 간 변화가 작다 (미세한 호흡 동작).
- 3/4행(WALK): 다리가 벌어지는 달리기 자세로 프레임 간 변화가 크다.
- 오른쪽 바라보기 판정: 픽셀 무게중심이 오른쪽 치우침 (2, 3행),
  왼쪽 판정: 1, 4행 (좌우 반전 관계).

## 입력 처리

- `SDL_KEYDOWN` / `SDL_KEYUP` 이벤트로 축별 방향값을 누적한다. (키를 누르는 동안 계속 이동)
  - `dir_x`: 오른쪽 `+1`, 왼쪽 `-1` (`KEYDOWN` 증가 / `KEYUP` 감소 → 동시 입력 시 상쇄되어 정지)
  - `dir_y`: 위쪽 `+1`, 아래쪽 `-1` (동일 방식)
- `SDLK_ESCAPE` 또는 `SDL_QUIT` → `running = False`.
- 원본의 `dir += dir*5` 자리는 연습용 오류이므로 제거하고
  `x += dir_x * SPEED`, `y += dir_y * SPEED`로 대체한다.

## 상태 및 표시 규칙

- `facing`: `+1`(오른쪽) / `-1`(왼쪽).
  - 왼쪽/오른쪽 키를 누른 순간에만 갱신. 위/아래 키는 `facing`에 영향을 주지 않는다.
- `moving = (dir_x != 0 or dir_y != 0)`
  - `moving == True` → 현재 `facing`의 **WALK** 8프레임 순환
    (`sy = 100` if `facing > 0` else `sy = 0`)
  - `moving == False` → 현재 `facing`의 **IDLE** 8프레임 순환
    (`sy = 200` if `facing > 0` else `sy = 300`)
- 위/아래로만 이동해도 WALK 애니메이션을 재생하되, 시트의 좌/우 행 선택은
  `facing`만 사용한다 (방향 플립 없음, 기존 방향 유지).
- `frame = (frame + 1) % 8` 을 루프마다 증가시킨다 (정지 시에도 IDLE 애니 순환).

## 위치 및 경계

- 이동량: `SPEED = 5` 픽셀/프레임 (축별 독립, 대각선 이동 시 두 축 모두 5씩 이동).
- 캐릭터는 100 x 100으로 그려지고 중심 `(x, y)` 기준이므로 반지름은 50.
  - `x = clamp(x, 50, 750)`
  - `y = clamp(y, 50, 550)`
- clamp는 이동 계산 직후에 수행해서 경계 밖으로 나가지 않게 한다.

## 배경

- `TUK_GROUND.png`(1280 x 1024)를 중앙 `(400, 300)`에 원본 크기로 그린다.
  캔버스 800 x 600보다 크므로 항상 화면 전체를 덮는다.
- 레이어 순서: `clear_canvas()` → 배경 → 캐릭터 → `update_canvas()`.

## 구현 단계

1. 이 계획서를 커밋하고 자원 경로를 기록한다.
2. `from pico2d import *` 로 시작하고 캔버스를 연다.
3. `TUK_GROUND.png`, `animation_sheet.png`를 로드한다.
4. 상수 선언: `FRAME_SIZE = 100`, `FRAME_COUNT = 8`, `SPEED = 5`,
   `HALF = 50`, 화면 경계값.
5. 전역 상태 초기화: `x = 400`, `y = 300`, `frame = 0`,
   `dir_x = 0`, `dir_y = 0`, `facing = 1`, `running = True`.
6. `handle_events()` 작성: `SDL_QUIT`, `SDLK_ESCAPE` 처리.
7. `SDL_KEYDOWN`에서 `SDLK_RIGHT/LEFT/UP/DOWN` 별 `dir_x`, `dir_y` 증감,
   좌/우 키에서 `facing` 갱신.
8. `SDL_KEYUP`에서 반대로 감산해 키를 뗄 때 정지하도록 한다.
9. 메인 루프: `clear_canvas()`.
10. 배경을 `(400, 300)`에 그린다.
11. `moving` 여부에 따라 `sy`를 선택한다 (WALK/IDLE x 좌/우 4가지).
12. `character.clip_draw(frame * 100, sy, 100, 100, x, y)` 로 캐릭터를 그린다.
13. `update_canvas()` 후 `handle_events()` 호출.
14. `x`, `y`에 `dir_x * SPEED`, `dir_y * SPEED` 적용하고 경계 clamp.
15. `frame = (frame + 1) % 8` 증가.
16. `delay(0.05)` 로 프레임 속도를 조절한다.
17. 루프 종료 후 `close_canvas()`.

## 커밋 로그 계획

각 커밋은 한 줄짜리 짧은 메시지로, `git log --oneline`에서 한 화면에 들어오도록 한다.
기존 저장소 커밋 스타일(국문 한 줄)을 따른다. 총 24개.

```
 1 계획서 move_character_with_key_plan.md 추가
 2 키보드 이동 스크립트 골격과 캔버스 생성
 3 배경 TUK_GROUND.png 로드 후 중앙에 그리기
 4 애니메이션 시트 animation_sheet.png 로드
 5 이동 상수와 화면 경계값 정의
 6 위치와 방향, 프레임 상태 변수 초기화
 7 SDL_QUIT과 ESC 키로 종료 처리
 8 오른쪽 왼쪽 키 입력으로 dir_x 증감 처리
 9 위쪽 아래쪽 키 입력으로 dir_y 증감 처리
10 좌우 키 입력 시 facing 방향 갱신
11 KEYUP 이벤트로 키를 뗄 때 방향값 복구
12 좌우 동시 입력 상쇄 동작 확인 후 주석 정리
13 메인 루프에 clear_canvas와 update_canvas 추가
14 캐릭터 clip_draw로 프레임 위치 지정
15 WALK 시트 행을 facing 기준으로 선택
16 IDLE 시트 행을 facing 기준으로 선택
17 이동 여부에 따라 WALK과 IDLE 상태 전환
18 위아래 이동 중에도 facing 유지되도록 수정
19 프레임 번호 8프레임 순환 증가 추가
20 x와 y에 이동량을 적용하고 속도 상수 적용
21 화면 경계 clamp 로 좌표 범위 제한
22 프레임 속도 조절용 delay 추가
23 문법 검사와 Pylance 오류 확인 후 수정
24 검증 체크리스트 통과 확인 후 계획서 갱신
```

각 단계는 구현 단계 1~17번과 검증 항목에 대응하며,
커밋마다 정상 실행 가능한 상태를 유지한다.

## 검증

- `python -m py_compile move_character_with_key_full.py` 문법 통과.
- Pylance가 선택된 Python 환경에서 `pico2d`를 해석한다.
- 자원 로드가 셸 작업 디렉터리와 무관하게 스크립트 폴더 기준으로 이루어진다.
- 수동 체크리스트:
  - [ ] 좌/우 키: 이동 + 해당 방향의 WALK 애니메이션, 방향 전환 시 시트 행 전환
  - [ ] 상/하 키: 이동 + **이전 좌/우 방향 그대로** 유지 (행이 바뀌지 않음)
  - [ ] 모든 키를 뗀 상태: IDLE 8프레임이 계속 순환
  - [ ] 좌우 경계(`x = 50 / 750`), 상하 경계(`y = 50 / 550`)에서 정지, 화면 밖으로 나가지 않음
  - [ ] 좌우 동시 입력 시 상쇄되어 정지
  - [ ] ESC / 창 닫기로 종료 후 캔버스 정상 닫힘
