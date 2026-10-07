"""Move the student character with the arrow keys (Drill #9)."""

from pico2d import *


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024
SCREEN_CENTER_X = SCREEN_WIDTH / 2
SCREEN_CENTER_Y = SCREEN_HEIGHT / 2
FRAME_SIZE = 100
FRAME_COUNT = 8
PLAYER_SPEED = 300.0  # pixels per second
ANIMATION_FPS = 12.0
ANIMATION_FRAME_DURATION = 1.0 / ANIMATION_FPS
MAX_DELTA_TIME = 0.05
FRAME_DELAY = 0.01
BACKGROUND_FILE = "TUK_GROUND.png"
SPRITE_SHEET_FILE = "animation_sheet.png"
PLAYER_HALF_SIZE = FRAME_SIZE // 2
PLAYER_BOTTOM_MARGIN = FRAME_SIZE * 2
PLAYER_TOP_MARGIN = FRAME_SIZE + FRAME_SIZE // 4

# Sprite-sheet rows are counted from the bottom, as required by clip_draw.
IDLE_RIGHT_ROW = 3
IDLE_LEFT_ROW = 2
RUN_RIGHT_ROW = 1
RUN_LEFT_ROW = 0
ANIMATION_ROWS = {
    ("right", False): IDLE_RIGHT_ROW,
    ("left", False): IDLE_LEFT_ROW,
    ("right", True): RUN_RIGHT_ROW,
    ("left", True): RUN_LEFT_ROW,
}

KEY_DIRECTIONS = {
    SDLK_UP: (0, 1),
    SDLK_DOWN: (0, -1),
    SDLK_LEFT: (-1, 0),
    SDLK_RIGHT: (1, 0),
}
MOVEMENT_KEYS = frozenset(KEY_DIRECTIONS)


def handle_events(pressed_keys):
    """Update held movement keys and report whether the game should continue."""
    for event in get_events():
        if event.type == SDL_QUIT:
            return False

        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                return False
            if event.key in MOVEMENT_KEYS:
                pressed_keys.add(event.key)

        elif event.type == SDL_KEYUP and event.key in MOVEMENT_KEYS:
            pressed_keys.discard(event.key)

    return True


def movement_vector(pressed_keys):
    """Return normalized movement for the currently held arrow keys."""
    dx = sum(KEY_DIRECTIONS[key][0] for key in pressed_keys)
    dy = sum(KEY_DIRECTIONS[key][1] for key in pressed_keys)

    if dx and dy:
        diagonal_scale = 2 ** -0.5
        dx *= diagonal_scale
        dy *= diagonal_scale

    return dx, dy


def clamp(value, minimum, maximum):
    """Restrict a value to an inclusive range."""
    return max(minimum, min(maximum, value))


def keep_player_on_screen(player):
    """Clamp the player's center so its sprite stays inside the canvas."""
    player["x"] = clamp(player["x"], PLAYER_HALF_SIZE, SCREEN_WIDTH - PLAYER_HALF_SIZE)
    player["y"] = clamp(
        player["y"],
        PLAYER_BOTTOM_MARGIN,
        SCREEN_HEIGHT - PLAYER_TOP_MARGIN,
    )


def create_player():
    """Create the initial player state at the center of the screen."""
    return {
        "x": SCREEN_CENTER_X,
        "y": SCREEN_CENTER_Y,
        "facing": "right",
        "moving": False,
        "frame": 0,
        "animation_time": 0.0,
    }


def update_facing(player, horizontal_direction):
    """Change facing only when there is horizontal movement."""
    if horizontal_direction < 0:
        player["facing"] = "left"
    elif horizontal_direction > 0:
        player["facing"] = "right"


def move_player(player, dx, dy, delta_time):
    """Apply the normalized movement vector to the player's position."""
    player["x"] += dx * PLAYER_SPEED * delta_time
    player["y"] += dy * PLAYER_SPEED * delta_time
    keep_player_on_screen(player)


def advance_animation(player, delta_time):
    """Advance the sprite animation without depending on render speed."""
    player["animation_time"] += delta_time
    while player["animation_time"] >= ANIMATION_FRAME_DURATION:
        player["frame"] = (player["frame"] + 1) % FRAME_COUNT
        player["animation_time"] -= ANIMATION_FRAME_DURATION


def update_player(pressed_keys, player, delta_time):
    """Move the player, preserve horizontal facing, and keep the sprite visible."""
    was_moving = player["moving"]
    dx, dy = movement_vector(pressed_keys)

    move_player(player, dx, dy, delta_time)
    update_facing(player, dx)

    player["moving"] = bool(dx or dy)
    if player["moving"] != was_moving:
        player["frame"] = 0
        player["animation_time"] = 0.0

    advance_animation(player, delta_time)


def animation_row(player):
    """Select the sprite-sheet row for the current facing and movement state."""
    return ANIMATION_ROWS[(player["facing"], player["moving"])]


def draw_player(sprite_sheet, player):
    """Draw an idle or running animation that matches the current facing."""
    row = animation_row(player)

    sprite_sheet.clip_draw(
        player["frame"] * FRAME_SIZE,
        row * FRAME_SIZE,
        FRAME_SIZE,
        FRAME_SIZE,
        int(player["x"]),
        int(player["y"]),
    )


def draw_scene(background, sprite_sheet, player):
    """Render the background first and the player on top of it."""
    clear_canvas()
    background.draw(SCREEN_CENTER_X, SCREEN_CENTER_Y)
    draw_player(sprite_sheet, player)
    update_canvas()


def main():
    open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
    try:
        background = load_image(BACKGROUND_FILE)
        sprite_sheet = load_image(SPRITE_SHEET_FILE)

        pressed_keys = set()
        player = create_player()

        running = True
        previous_time = get_time()
        while running:
            current_time = get_time()
            elapsed_time = max(0.0, current_time - previous_time)
            delta_time = min(elapsed_time, MAX_DELTA_TIME)
            previous_time = current_time

            running = handle_events(pressed_keys)
            if not running:
                break

            update_player(pressed_keys, player, delta_time)

            draw_scene(background, sprite_sheet, player)
            delay(FRAME_DELAY)
    finally:
        close_canvas()


if __name__ == "__main__":
    main()
