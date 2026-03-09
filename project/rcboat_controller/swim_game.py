import cv2
import numpy as np
import pygame
import sys
from pathlib import Path

# ── HSV skin detection parameters ──────────────────────────────────────────
LOWER_SKIN = np.array([0,  80,  80], dtype=np.uint8)
UPPER_SKIN = np.array([20, 150, 255], dtype=np.uint8)

# ── Game window settings ────────────────────────────────────────────────────
GAME_W, GAME_H   = 600, 600
GRID_CELLS       = 10           # grid lines
BALL_RADIUS      = 18
TRAIL_LEN        = 40           # number of past positions to draw
SPEED_SCALE      = 0.15         # pixel-velocity → ball pixels per frame
DIRECTION_SCALE  = 0.25         # direction imbalance → horizontal pixels per frame
SMOOTHING        = 0.75         # exponential smoothing factor (higher = more inertia)
MAX_SPEED        = 8.0          # cap ball movement per frame
DECEL            = 0.92         # friction when no arms detected

# ── Video source ────────────────────────────────────────────────────────────
VIDEO_PATH = str(Path(__file__).resolve().parent / "alexmove.mp4")


def get_skin_mask(frame):
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    hsv     = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask       = cv2.inRange(hsv, LOWER_SKIN, UPPER_SKIN)
    green_mask = cv2.inRange(hsv, np.array([25, 30,  30]), np.array([85,  255, 200]))
    gray_mask  = cv2.inRange(hsv, np.array([0,   0,  40]), np.array([180,  49, 220]))
    exclusion  = cv2.bitwise_or(green_mask, gray_mask)
    mask       = cv2.bitwise_and(mask, cv2.bitwise_not(exclusion))

    kernel = np.ones((5, 5), np.uint8)
    mask   = cv2.erode(mask,  kernel, iterations=1)
    mask   = cv2.dilate(mask, kernel, iterations=3)
    return mask


def get_arm_candidates(mask, frame_w):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates  = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500:
            continue
        _, _, bw, _ = cv2.boundingRect(cnt)
        if bw > frame_w * 0.4:
            continue
        hull_area = cv2.contourArea(cv2.convexHull(cnt))
        if area / (hull_area + 1e-5) < 0.4:
            continue
        # centroid
        M  = cv2.moments(cnt)
        cx = int(M["m10"] / (M["m00"] + 1e-5))
        cy = int(M["m01"] / (M["m00"] + 1e-5))
        candidates.append((cnt, cx, cy, area))
    # sort by area descending, keep top 2
    candidates.sort(key=lambda x: x[3], reverse=True)
    return candidates[:2]


def draw_cv_overlay(frame, arms, speed_L, speed_R, smooth_speed, smooth_dir):
    colors = [(255, 100, 0), (0, 100, 255)]  # orange=left, blue=right
    labels = ["L", "R"]
    for i, (cnt, cx, cy, _) in enumerate(arms):
        cv2.drawContours(frame, [cnt], -1, colors[i], 2)
        cv2.circle(frame, (cx, cy), 8, colors[i], -1)
        cv2.putText(frame, labels[i], (cx + 10, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, colors[i], 2)

    cv2.putText(frame, f"Speed L: {speed_L:.1f}  R: {speed_R:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"Ball spd: {smooth_speed:.2f}  dir: {smooth_dir:+.2f}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 255, 100), 2)
    return frame


def draw_game(screen, ball_pos, trail, smooth_speed, smooth_dir):
    screen.fill((15, 15, 30))

    # grid
    cell = GAME_W // GRID_CELLS
    for i in range(GRID_CELLS + 1):
        pygame.draw.line(screen, (40, 40, 70), (i * cell, 0), (i * cell, GAME_H))
        pygame.draw.line(screen, (40, 40, 70), (0, i * cell), (GAME_W, i * cell))

    # trail
    for i, pos in enumerate(trail):
        alpha = int(255 * i / max(len(trail), 1))
        radius = max(3, int(BALL_RADIUS * i / max(len(trail), 1)))
        pygame.draw.circle(screen, (alpha, 200, 100), (int(pos[0]), int(pos[1])), radius)

    # ball
    bx, by = int(ball_pos[0]), int(ball_pos[1])
    pygame.draw.circle(screen, (255, 220, 50), (bx, by), BALL_RADIUS)
    pygame.draw.circle(screen, (255, 255, 255), (bx, by), BALL_RADIUS, 2)

    # HUD
    font = pygame.font.SysFont("consolas", 18)
    screen.blit(font.render(f"Speed: {smooth_speed:.2f}", True, (200, 255, 100)), (10, 10))
    screen.blit(font.render(f"Direction: {'RIGHT' if smooth_dir > 0.1 else 'LEFT' if smooth_dir < -0.1 else 'STRAIGHT'}", True, (200, 255, 100)), (10, 35))
    screen.blit(font.render("Q = quit", True, (120, 120, 120)), (10, GAME_H - 30))

    pygame.display.flip()


def main():
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"Error: cannot open {VIDEO_PATH}")
        sys.exit(1)

    pygame.init()
    screen = pygame.display.set_mode((GAME_W, GAME_H))
    pygame.display.set_caption("Swim Game — Arm Tracker")
    clock = pygame.time.Clock()

    # Ball state
    ball_pos   = [GAME_W / 2, GAME_H / 2]
    trail      = []
    smooth_speed = 0.0
    smooth_dir   = 0.0

    # Previous arm centroids for velocity calculation
    prev_centroids = {}  # key: "L" or "R", value: (cx, cy)

    running = True
    while running:
        # ── Pygame event handling ─────────────────────────────────────────
        pygame.event.pump()  # keep OS window responsive during heavy CV frames
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False

        if not running:
            break

        # ── Read video frame ──────────────────────────────────────────────
        ret, frame = cap.read()
        if not ret:
            # loop video
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            prev_centroids.clear()
            continue

        frame_h, frame_w = frame.shape[:2]

        # ── Arm detection ─────────────────────────────────────────────────
        mask = get_skin_mask(frame)
        arms = get_arm_candidates(mask, frame_w)

        # Assign left/right by x-centroid (smaller x = left arm)
        arms.sort(key=lambda a: a[1])  # sort by cx
        assigned = {}
        if len(arms) >= 1:
            assigned["L"] = arms[0]
        if len(arms) >= 2:
            assigned["R"] = arms[1]

        # Compute per-arm pixel velocity
        speed_L, speed_R = 0.0, 0.0
        for side, (cnt, cx, cy, _) in assigned.items():
            if side in prev_centroids:
                pcx, pcy = prev_centroids[side]
                dist = np.hypot(cx - pcx, cy - pcy)
                if side == "L":
                    speed_L = dist
                else:
                    speed_R = dist
            prev_centroids[side] = (cx, cy)

        # ── Compute game signals ──────────────────────────────────────────
        if assigned:
            raw_speed = (speed_L + speed_R) / max(len(assigned), 1)
            # direction: R faster → move right, L faster → move left
            raw_dir   = (speed_R - speed_L) / (frame_w * 0.1 + 1e-5)
            raw_dir   = np.clip(raw_dir, -1.0, 1.0)
        else:
            raw_speed = 0.0
            raw_dir   = 0.0

        # Exponential smoothing
        smooth_speed = SMOOTHING * smooth_speed + (1 - SMOOTHING) * raw_speed
        smooth_dir   = SMOOTHING * smooth_dir   + (1 - SMOOTHING) * raw_dir

        # ── Update ball position ──────────────────────────────────────────
        if len(assigned) == 0:
            # no arms → decelerate
            smooth_speed *= DECEL

        fwd   = min(smooth_speed * SPEED_SCALE, MAX_SPEED)
        horiz = np.clip(smooth_dir * DIRECTION_SCALE * frame_w, -MAX_SPEED, MAX_SPEED)

        ball_pos[0] += horiz
        ball_pos[1] -= fwd   # move "up" = forward

        # Wrap at edges
        ball_pos[0] = ball_pos[0] % GAME_W
        ball_pos[1] = ball_pos[1] % GAME_H

        # Update trail
        trail.append((ball_pos[0], ball_pos[1]))
        if len(trail) > TRAIL_LEN:
            trail.pop(0)

        # ── Draw OpenCV window ────────────────────────────────────────────
        draw_cv_overlay(frame, list(assigned.values()), speed_L, speed_R, smooth_speed, smooth_dir)
        cv2.imshow("Arm Detection", frame)
        cv2.imshow("Mask", mask)

        # ── Draw Pygame window (always called so window stays alive) ──────
        draw_game(screen, ball_pos, trail, smooth_speed, smooth_dir)

        clock.tick(30)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()


if __name__ == "__main__":
    main()
