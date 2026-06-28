import pygame
import sys
import random
import math

# 初始化
pygame.init()
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Obstacle Pixel Runner")

# 颜色配置
BLACK = (25, 25, 35)
WHITE = (255, 255, 255)
GROUND = (70, 70, 85)
SKIN = (255, 200, 150)
HAIR = (50, 30, 20)
SHIRT = (255, 180, 0)
PANTS = (50, 100, 200)
OBSTACLE_HIGH = (220, 60, 60)
OBSTACLE_FLOAT = (80, 200, 180)
BTN_GREEN = (0, 200, 100)
BTN_BLUE = (50, 150, 255)
BTN_RED = (220, 60, 60)
BTN_GRAY = (100, 100, 120)

# 字体
font_big = pygame.font.SysFont("SimHei", 48)
font_mid = pygame.font.SysFont("SimHei", 32)
font_small = pygame.font.SysFont("SimHei", 24)

# 按钮类
class Button:
    def __init__(self, x, y, w, h, text, color, hover):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover = hover
    def draw(self):
        current = self.hover if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(screen, current, self.rect, border_radius=8)
        txt = font_mid.render(self.text, True, WHITE)
        screen.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))
    def is_click(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

# 绘制像素小人
def draw_player_stand(x, y):
    pygame.draw.rect(screen, SKIN, (x+5, y, 20, 20))
    pygame.draw.rect(screen, HAIR, (x+5, y, 20, 6))
    pygame.draw.rect(screen, SHIRT, (x+3, y+20, 24, 18))
    pygame.draw.rect(screen, PANTS, (x+5, y+38, 8, 12))
    pygame.draw.rect(screen, PANTS, (x+17, y+38, 8, 12))

# 地面路障
def draw_obstacle_high(x, y, w, h):
    pygame.draw.rect(screen, OBSTACLE_HIGH, (x, y, w, h))
    for i in range(0, h, 15):
        pygame.draw.rect(screen, WHITE, (x, y+i, w, 5))

# 空中浮动障碍
def draw_obstacle_float(x, y, w, h):
    pygame.draw.rect(screen, OBSTACLE_FLOAT, (x, y, w, h))
    pygame.draw.rect(screen, WHITE, (x+3, y+3, w-6, h-6), 2)

# 按钮实例
btn_start = Button(300, 180, 200, 60, "开始游戏", BTN_GREEN, (0, 230, 120))
btn_help = Button(300, 260, 200, 60, "操作说明", BTN_BLUE, (70, 180, 255))
btn_quit = Button(300, 340, 200, 60, "退出游戏", BTN_RED, (250, 80, 80))
btn_back = Button(300, 380, 200, 60, "返回菜单", BTN_GRAY, (120, 120, 140))

# 主菜单
def main_menu():
    while True:
        screen.fill(BLACK)
        pygame.draw.rect(screen, GROUND, (0, 420, WIDTH, 80))
        title = font_big.render("Dynamic Obstacle Pixel Runner", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        btn_start.draw()
        btn_help.draw()
        btn_quit.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_start.is_click():
                    game_run()
                if btn_help.is_click():
                    help_page()
                if btn_quit.is_click():
                    pygame.quit()
                    sys.exit()
        pygame.display.flip()

# 操作说明
def help_page():
    while True:
        screen.fill(BLACK)
        title = font_big.render("操作说明", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        tips = [
            "←/A 向左移动   →/D 向右移动",
            "空格 跳跃（可二段跳）",
            "🔴 红色地面路障 → 跳跃躲避",
            "🟢 青色空中浮动障碍 → 预判时机二段跳",
            "游戏时间越长，场景移动速度越快",
            "ESC 返回主菜单"
        ]
        y = 140
        for t in tips:
            screen.blit(font_small.render(t, True, WHITE), (100, y))
            y += 38
        btn_back.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and btn_back.is_click():
                return
        pygame.display.flip()

# ======================
# 核心游戏逻辑（浮动幅度扩大3倍）
# ======================
def game_run():
    player_x = 100
    player_y = 350
    player_speed = 6
    vy = 0
    gravity = 0.7
    jump_count = 0
    max_jump = 2
    on_ground = True

    score = 0
    game_time = 0
    base_speed = 4
    max_speed = 9
    obstacles = []
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        game_time += 1
        screen.fill(BLACK)
        pygame.draw.rect(screen, GROUND, (0, 420, WIDTH, 80))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE:
                    if on_ground:
                        vy = -15
                        on_ground = False
                        jump_count = 1
                    elif jump_count < max_jump:
                        vy = -13
                        jump_count += 1

        # 左右移动
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_x += player_speed
        player_x = max(20, min(player_x, WIDTH - 60))

        # 重力物理
        vy += gravity
        player_y += vy
        if player_y >= 350:
            player_y = 350
            vy = 0
            on_ground = True
            jump_count = 0

        player_rect = pygame.Rect(player_x, player_y, 30, 50)

        # 速度随时间递增
        speed = base_speed + game_time // 1200
        if speed > max_speed:
            speed = max_speed

        # 生成障碍
        if random.randint(0, 55) == 0:
            obs_type = random.choice(["ground", "float"])
            if obs_type == "ground":
                obstacles.append([WIDTH, 350, 30, 70, "ground", 0])
            else:
                base_y = random.randint(260, 290)
                obstacles.append([WIDTH, base_y, 30, 35, "float", random.randint(50, 70)])

        # 更新障碍
        for obs in obstacles[:]:
            ox, base_y, w, h, o_type, cycle = obs

            # 空中障碍：浮动幅度从10改为30，扩大3倍
            if o_type == "float":
                float_offset = int(math.sin(game_time / cycle) * 30)
                real_y = base_y + float_offset
            else:
                real_y = base_y

            # 向左移动
            ox -= speed
            obs[0] = ox

            # 移除出界障碍并加分
            if ox < -50:
                obstacles.remove(obs)
                score += 10
                continue

            # 碰撞检测
            obs_rect = pygame.Rect(ox, real_y, w, h)
            if player_rect.colliderect(obs_rect):
                game_over(score)
                return

            # 绘制障碍
            if o_type == "ground":
                draw_obstacle_high(ox, real_y, w, h)
            else:
                draw_obstacle_float(ox, real_y, w, h)

        # 绘制角色
        draw_player_stand(player_x, player_y)

        # UI
        screen.blit(font_mid.render(f"分数：{score}", True, WHITE), (20, 10))
        screen.blit(font_small.render(f"时长：{game_time//60}s", True, WHITE), (20, 45))
        screen.blit(font_small.render(f"速度：{speed}", True, WHITE), (20, 80))

        pygame.display.flip()

# 游戏结束
def game_over(score):
    while True:
        screen.fill(BLACK)
        screen.blit(font_big.render("游戏结束", True, OBSTACLE_HIGH), (WIDTH//2 - 120, 100))
        screen.blit(font_mid.render(f"最终得分：{score}", True, WHITE), (WIDTH//2 - 100, 200))
        btn_back.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and btn_back.is_click():
                return
        pygame.display.flip()

if __name__ == "__main__":
    main_menu()