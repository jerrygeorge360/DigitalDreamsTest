import pygame
import sys
import math
from elements import Ball, Force

WIDTH, HEIGHT = 800, 600
SCALE = 50  # pixels per meter
GROUND_Y = 0  # ground at y=0 in world coords

BG_COLOR = (30, 30, 30)
BALL_COLOR = (220, 80, 80)
GROUND_COLOR = (100, 100, 100)
TEXT_COLOR = (220, 220, 220)


def world_to_screen(x, y):
    sx = int(50 + x * SCALE)
    sy = int(HEIGHT - (y * SCALE) - 50)
    return sx, sy


def screen_to_world(sx, sy):
    x = (sx - 50) / SCALE
    y = (HEIGHT - sy - 50) / SCALE
    return x, y


def draw_ball(screen, ball):
    sx, sy = world_to_screen(ball.x, ball.y)
    radius_px = max(2, int(ball.radius * SCALE))
    pygame.draw.circle(screen, BALL_COLOR, (sx, sy), radius_px)


def draw_ground(screen):
    y = world_to_screen(0, 0)[1]
    pygame.draw.rect(screen, GROUND_COLOR, (0, y, WIDTH, HEIGHT - y))


def draw_text(screen, text, pos, font):
    surf = font.render(text, True, TEXT_COLOR)
    screen.blit(surf, pos)


def run():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ball Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)

    # create simulation objects
    ball = Ball(0, 10, 0.3)
    applied = Force(10, math.pi / 4)

    # wall height (meters)
    wall_height_m = 12.0

    dt = 1.0 / 60.0
    # apply a single impulse at start
    applied.apply_to(ball, dt)

    running = True
    paused = False
    dragging = False
    drag_start = (0, 0)
    drag_end = (0, 0)
    right_holding = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click start drag for impulse
                    dragging = True
                    drag_start = event.pos
                    drag_end = event.pos
                elif event.button == 3:  # right click hold for continuous force
                    right_holding = True
                    drag_start = event.pos
                    drag_end = event.pos
            elif event.type == pygame.MOUSEMOTION:
                if dragging or right_holding:
                    drag_end = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging:
                    # apply impulse from drag vector
                    sx0, sy0 = drag_start
                    sx1, sy1 = drag_end
                    wx0, wy0 = screen_to_world(sx0, sy0)
                    wx1, wy1 = screen_to_world(sx1, sy1)
                    dx = wx1 - wx0
                    dy = wy1 - wy0
                    mag = math.hypot(dx, dy)
                    if mag > 0:
                        # scale impulse so reasonable from drag length
                        scale = 50.0
                        fx = dx * scale
                        fy = dy * scale
                        ball.apply_impulse(fx, fy)
                    dragging = False
                if event.button == 3 and right_holding:
                    right_holding = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    ball.x, ball.y = 0, 10
                    ball.vx, ball.vy = 0, 0
                    applied.apply_to(ball, dt)

        if not paused:
            # physics step
            ball.apply_acceleration(0, -Ball.gravity, dt)
            # continuous force while right mouse held
            if right_holding:
                sx0, sy0 = drag_start
                sx1, sy1 = drag_end
                wx0, wy0 = screen_to_world(sx0, sy0)
                wx1, wy1 = screen_to_world(sx1, sy1)
                dx = wx1 - wx0
                dy = wy1 - wy0
                mag = math.hypot(dx, dy)
                if mag > 0:
                    direction = math.atan2(dy, dx)
                    # scale force magnitude from drag length
                    magnitude = mag * 200.0
                    f = Force(magnitude, direction)
                    f.apply_to(ball, dt)
            ball.update(dt)
            # compute walls at current screen edges (in world coords)
            left_wall_x = (0 - 50) / SCALE
            right_wall_x = (WIDTH - 50) / SCALE
            # wall collisions (reflect horizontal velocity)
            if ball.x - ball.radius < left_wall_x:
                ball.x = left_wall_x + ball.radius
                ball.vx = -ball.vx * ball.elasticity()
                ball.vx *= 0.99
            if ball.x + ball.radius > right_wall_x:
                ball.x = right_wall_x - ball.radius
                ball.vx = -ball.vx * ball.elasticity()
                ball.vx *= 0.99

        screen.fill(BG_COLOR)
        draw_ground(screen)
        draw_ball(screen, ball)

        # draw walls (at screen edges)
        wall_top_px = world_to_screen(0, wall_height_m)[1]
        ground_px = world_to_screen(0, 0)[1]
        wall_h_px = max(2, ground_px - wall_top_px)
        wall_w_px = max(3, int(0.1 * SCALE))
        # compute pixel x positions from world coords used for collisions
        left_wall_x = (0 - 50) / SCALE
        right_wall_x = (WIDTH - 50) / SCALE
        sx_left = world_to_screen(left_wall_x, 0)[0]
        sx_right = world_to_screen(right_wall_x, 0)[0]
        pygame.draw.rect(screen, (120, 120, 200), (sx_left - wall_w_px // 2, wall_top_px, wall_w_px, wall_h_px))
        pygame.draw.rect(screen, (120, 120, 200), (sx_right - wall_w_px // 2, wall_top_px, wall_w_px, wall_h_px))

        # draw drag vector
        if dragging or right_holding:
            sx0, sy0 = drag_start
            sx1, sy1 = drag_end
            pygame.draw.line(screen, (200, 200, 50), (sx0, sy0), (sx1, sy1), 2)
            # draw arrowhead
            ax = sx1 - sx0
            ay = sy1 - sy0
            ang = math.atan2(ay, ax)
            ah = 8
            left = (int(sx1 - ah * math.cos(ang - 0.4)), int(sy1 - ah * math.sin(ang - 0.4)))
            right = (int(sx1 - ah * math.cos(ang + 0.4)), int(sy1 - ah * math.sin(ang + 0.4)))
            pygame.draw.polygon(screen, (200, 200, 50), [(sx1, sy1), left, right])

        draw_text(screen, f"pos=({ball.x:.2f}, {ball.y:.2f})", (10, 10), font)
        draw_text(screen, f"vel=({ball.vx:.2f}, {ball.vy:.2f})", (10, 30), font)
        draw_text(screen, "SPACE: pause/resume  R: reset", (10, 50), font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()
