# =========================
# Snake Game Premium - Pygame
# Arquivo: snake_game.py
# =========================
#
# Requisitos:
#   pip install pygame
#
# Para rodar:
#   python snake_game.py
#
# =========================

import pygame
import random
import math
import sys

# -------------------------
# Inicialização
# -------------------------
pygame.init()
pygame.mixer.init()

# -------------------------
# Configurações
# -------------------------
WIDTH = 1024
HEIGHT = 768
FPS = 90

GRID_SIZE = 16
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

TITLE = "Snake Neon Edition"

# -------------------------
# Cores
# -------------------------
BG_TOP = (10, 12, 30)
BG_BOTTOM = (25, 20, 50)

NEON_GREEN = (57, 255, 20)
GREEN_2 = (0, 200, 120)
GREEN_DARK = (20, 80, 40)

APPLE_RED = (255, 60, 80)

WHITE = (240, 240, 240)
GRAY = (120, 120, 120)

GLOW = (120, 255, 120)

# -------------------------
# Tela
# -------------------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

clock = pygame.time.Clock()

# -------------------------
# Fontes
# -------------------------
title_font = pygame.font.SysFont("arialblack", 64)
menu_font = pygame.font.SysFont("arial", 30)
score_font = pygame.font.SysFont("consolas", 32)

# -------------------------
# Helpers
# -------------------------
def draw_gradient(surface, top_color, bottom_color):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (30, 30, 50), (x, 0), (x, HEIGHT))

    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (30, 30, 50), (0, y), (WIDTH, y))

def glow_circle(surface, color, pos, radius):
    for i in range(4, 0, -1):
        alpha_surface = pygame.Surface((radius * 8, radius * 8), pygame.SRCALPHA)
        pygame.draw.circle(
            alpha_surface,
            (*color, 20),
            (radius * 4, radius * 4),
            radius * i
        )
        surface.blit(alpha_surface, (pos[0] - radius * 4, pos[1] - radius * 4))

# -------------------------
# Snake
# -------------------------
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.new_block = False
        self.alive = True
        self.score = 0

    def move(self):
        if not self.alive:
            return

        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction

        new_head = (head_x + dir_x, head_y + dir_y)

        # colisão parede
        if (
            new_head[0] < 0
            or new_head[0] >= GRID_WIDTH
            or new_head[1] < 0
            or new_head[1] >= GRID_HEIGHT
        ):
            self.alive = False
            return

        # colisão corpo
        if new_head in self.body:
            self.alive = False
            return

        self.body.insert(0, new_head)

        if not self.new_block:
            self.body.pop()
        else:
            self.new_block = False

    def grow(self):
        self.new_block = True
        self.score += 1

    def draw(self):
        for index, block in enumerate(self.body):
            x = block[0] * GRID_SIZE
            y = block[1] * GRID_SIZE

            rect = pygame.Rect(x + 2, y + 2, GRID_SIZE - 4, GRID_SIZE - 4)

            # brilho
            glow_circle(
                screen,
                GLOW,
                (x + GRID_SIZE // 2, y + GRID_SIZE // 2),
                8
            )

            # cabeça
            if index == 0:
                pygame.draw.rect(screen, NEON_GREEN, rect, border_radius=10)

                eye_size = 4

                pygame.draw.circle(
                    screen,
                    WHITE,
                    (x + 8, y + 8),
                    eye_size
                )

                pygame.draw.circle(
                    screen,
                    WHITE,
                    (x + GRID_SIZE - 8, y + 8),
                    eye_size
                )

            else:
                pygame.draw.rect(screen, GREEN_2, rect, border_radius=8)

# -------------------------
# Food
# -------------------------
class Food:
    def __init__(self):
        self.randomize()

    def randomize(self):
        self.position = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1)
        )

    def draw(self):
        x = self.position[0] * GRID_SIZE
        y = self.position[1] * GRID_SIZE

        center = (x + GRID_SIZE // 2, y + GRID_SIZE // 2)

        glow_circle(screen, APPLE_RED, center, 10)

        pygame.draw.circle(screen, APPLE_RED, center, 10)
        pygame.draw.circle(screen, (255, 120, 140), center, 4)

# -------------------------
# Partículas
# -------------------------
particles = []

def create_particles(pos):
    for _ in range(20):
        particles.append({
            "x": pos[0],
            "y": pos[1],
            "vx": random.uniform(-3, 3),
            "vy": random.uniform(-3, 3),
            "life": random.randint(20, 40)
        })

def update_particles():
    for particle in particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["life"] -= 1

        alpha = max(0, particle["life"] * 6)

        surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(
            surf,
            (100, 255, 100, alpha),
            (4, 4),
            4
        )

        screen.blit(surf, (particle["x"], particle["y"]))

        if particle["life"] <= 0:
            particles.remove(particle)

# -------------------------
# Menu
# -------------------------
def draw_menu():
    draw_gradient(screen, BG_TOP, BG_BOTTOM)

    title = title_font.render("SNAKE", True, NEON_GREEN)
    subtitle = menu_font.render("NEON EDITION", True, WHITE)

    press = menu_font.render("Pressione ESPAÇO para começar", True, WHITE)

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 180))
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 260))
    screen.blit(press, (WIDTH // 2 - press.get_width() // 2, 450))

# -------------------------
# Game Over
# -------------------------
def draw_game_over(score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    text = title_font.render("GAME OVER", True, APPLE_RED)
    score_text = menu_font.render(f"Pontuação: {score}", True, WHITE)
    restart = menu_font.render("Pressione R para reiniciar", True, WHITE)

    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 220))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 340))
    screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, 420))

# -------------------------
# Objetos
# -------------------------
snake = Snake()
food = Food()

# -------------------------
# Estados
# -------------------------
MENU = 0
PLAYING = 1
GAME_OVER = 2

game_state = MENU

MOVE_EVENT = pygame.USEREVENT
pygame.time.set_timer(MOVE_EVENT, 110)

# -------------------------
# Loop principal
# -------------------------
running = True

while running:
    clock.tick(FPS)

    # Background
    draw_gradient(screen, BG_TOP, BG_BOTTOM)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_state = PLAYING

        elif game_state == PLAYING:

            if event.type == MOVE_EVENT:
                snake.move()

                # comer comida
                if snake.body[0] == food.position:
                    snake.grow()

                    fx = food.position[0] * GRID_SIZE
                    fy = food.position[1] * GRID_SIZE

                    create_particles((fx + 10, fy + 10))

                    while True:
                        food.randomize()
                        if food.position not in snake.body:
                            break

                if not snake.alive:
                    game_state = GAME_OVER

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP and snake.direction != (0, 1):
                    snake.direction = (0, -1)

                elif event.key == pygame.K_DOWN and snake.direction != (0, -1):
                    snake.direction = (0, 1)

                elif event.key == pygame.K_LEFT and snake.direction != (1, 0):
                    snake.direction = (-1, 0)

                elif event.key == pygame.K_RIGHT and snake.direction != (-1, 0):
                    snake.direction = (1, 0)

        elif game_state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    snake.reset()
                    food.randomize()
                    particles.clear()
                    game_state = PLAYING

    # -------------------------
    # Renderização
    # -------------------------
    if game_state == MENU:
        draw_menu()

    elif game_state == PLAYING:
        draw_grid()

        food.draw()
        snake.draw()

        update_particles()

        score_text = score_font.render(
            f"SCORE: {snake.score}",
            True,
            WHITE
        )

        screen.blit(score_text, (20, 20))

    elif game_state == GAME_OVER:
        draw_grid()

        food.draw()
        snake.draw()

        update_particles()

        draw_game_over(snake.score)

    pygame.display.update()

pygame.quit()
sys.exit()