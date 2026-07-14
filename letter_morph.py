"""
Letter Morph Birthday Animation
Scattered dots form a name letter by letter, then fireworks celebrate.
Usage: python letter_morph.py [NAME]
"""

import pygame
import numpy as np
import sys
from PIL import Image, ImageDraw, ImageFont

# ─── Config ─────────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 720
FPS = 60
BG_COLOR = (10, 10, 40)
DOT_COLOR = (120, 200, 255)
DOT_RADIUS = 2
DOTS_PER_LETTER = 400
FONT_SIZE = 160
LETTER_GAP = 25
MORPH_TIME = 2.0
CELEB_TIME = 8.0

# ─── Font Loading ──────────────────────────────────────────
def load_font(size):
    paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/Arial.ttf",
        "arial.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except (IOError, OSError):
            pass
    return ImageFont.load_default()


# ─── Letter Point Cloud Extraction ─────────────────────────
def get_letter_clouds(text, dots_per_letter, font_size):
    font = load_font(font_size)
    letter_data = []
    cursor_x = 0

    for char in text.upper():
        if char == ' ':
            cursor_x += font_size // 3
            continue

        try:
            bbox = font.getbbox(char)
        except AttributeError:
            bbox = None

        if bbox:
            pad = 15
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            img = Image.new('L', (w + 2 * pad, h + 2 * pad), 0)
            draw = ImageDraw.Draw(img)
            draw.text((pad - bbox[0], pad - bbox[1]), char, fill=255, font=font)
        else:
            s = font_size + 40
            img = Image.new('L', (s, s), 0)
            draw = ImageDraw.Draw(img)
            draw.text((20, 20), char, fill=255, font=font)
            w = s

        mask = np.array(img)
        ys, xs = np.where(mask > 128)

        if len(xs) == 0:
            cursor_x += w + LETTER_GAP
            continue

        points = np.column_stack([xs.astype(float), ys.astype(float)])
        centroid = points.mean(axis=0)
        points -= centroid

        rng = np.random.RandomState(hash(char) % 2 ** 31)
        if len(points) < dots_per_letter:
            extra = rng.choice(len(points), dots_per_letter - len(points))
            points = np.vstack([points, points[extra]])
        elif len(points) > dots_per_letter:
            idx = rng.choice(len(points), dots_per_letter, replace=False)
            points = points[idx]

        angles = np.arctan2(points[:, 1], points[:, 0])
        points = points[np.argsort(angles)]

        letter_data.append({
            'points':   points,
            'offset_x': cursor_x,
            'width':    w,
            'char':     char,
        })
        cursor_x += w + LETTER_GAP

    text_w = cursor_x - LETTER_GAP
    start_x = (WIDTH - text_w) / 2
    center_y = HEIGHT / 2 + 15

    for ld in letter_data:
        ld['points'][:, 0] += start_x + ld['offset_x']
        ld['points'][:, 1] += center_y

    return letter_data, text_w


# ─── Sparkles & Shooting Stars ─────────────────────────────
SPARKLE_COLORS = [
    (255, 220, 50), (255, 150, 50), (80, 255, 150),
    (255, 80, 130), (80, 180, 255), (255, 255, 80),
    (200, 100, 255), (255, 100, 200), (255, 200, 150),
]

class Sparkle:
    def __init__(self, pos):
        self.pos = pos.copy()
        angle = np.random.uniform(0, 2 * np.pi)
        speed = np.random.uniform(150, 600)
        self.vel = np.array([np.cos(angle), np.sin(angle)]) * speed
        self.life = np.random.uniform(0.5, 2.5)
        self.max_life = self.life
        self.color = SPARKLE_COLORS[np.random.randint(len(SPARKLE_COLORS))]

    def update(self, dt):
        self.pos += self.vel * dt
        self.vel *= 0.94
        self.life -= dt

    def draw(self, screen):
        if self.life > 0:
            t = self.life / self.max_life
            size = max(1, int(6 * t))
            alpha = int(255 * t)
            s = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (size + 1, size + 1), size)
            screen.blit(s, self.pos - np.array([size + 1, size + 1]))


class BurstParticle:
    """Shooting star that bursts upward from a letter position."""
    def __init__(self, pos, color):
        self.pos = pos.copy()
        spread = np.random.uniform(-0.35, 0.35)
        speed = np.random.uniform(350, 700)
        self.vel = np.array([
            np.sin(spread) * speed * 0.3,
            -np.cos(spread) * speed
        ])
        self.gravity = np.random.uniform(200, 350)
        self.life = np.random.uniform(0.6, 1.4)
        self.max_life = self.life
        self.color = color

    def update(self, dt):
        self.vel[1] += self.gravity * dt
        self.pos += self.vel * dt
        self.life -= dt

    def draw_trail(self, trail_surf):
        if self.life <= 0:
            return
        t = max(0, self.life / self.max_life)
        alpha = int(180 * t)
        speed = np.linalg.norm(self.vel)
        if speed > 5:
            vel_norm = self.vel / speed
            tail_len = min(speed * 0.15, 55)
            tail_start = self.pos - vel_norm * tail_len
            for i in range(2):
                w = max(1, int(3 * t) - i)
                if w > 0:
                    pygame.draw.line(trail_surf, (*self.color, alpha // (i + 1)),
                        tail_start.astype(int), self.pos.astype(int), w)

    def draw_head(self, screen):
        if self.life <= 0:
            return
        t = max(0, self.life / self.max_life)
        head_size = max(1, int(3 * t))
        pygame.draw.circle(screen, (255, 255, 255), self.pos.astype(int), head_size + 1)
        pygame.draw.circle(screen, self.color, self.pos.astype(int), head_size)


class ShootingStar:
    def __init__(self):
        side = np.random.randint(4)
        if side == 0:
            x, y = np.random.uniform(0, WIDTH), -20
            dx, dy = np.random.uniform(-80, 80), np.random.uniform(300, 700)
        elif side == 1:
            x, y = np.random.uniform(0, WIDTH), HEIGHT + 20
            dx, dy = np.random.uniform(-80, 80), np.random.uniform(-700, -300)
        elif side == 2:
            x, y = -20, np.random.uniform(0, HEIGHT)
            dx, dy = np.random.uniform(300, 700), np.random.uniform(-80, 80)
        else:
            x, y = WIDTH + 20, np.random.uniform(0, HEIGHT)
            dx, dy = np.random.uniform(-700, -300), np.random.uniform(-80, 80)

        self.pos = np.array([x, y], dtype=float)
        self.vel = np.array([dx, dy], dtype=float)
        self.life = np.random.uniform(0.4, 1.0)
        self.max_life = self.life

    def update(self, dt):
        self.pos += self.vel * dt
        self.life -= dt

    def draw(self, screen):
        if self.life > 0:
            t = self.life / self.max_life
            alpha = int(255 * t)
            tail_len = int(120 * t)
            vel_norm = self.vel / (np.linalg.norm(self.vel) + 1e-8)
            end = (self.pos - vel_norm * tail_len).astype(int)
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            color = (255, 255, 220, alpha)
            pygame.draw.line(s, color, self.pos.astype(int), end, max(1, int(3 * t)))
            screen.blit(s, (0, 0))


# ─── Particle System ───────────────────────────────────────
LETTER_COLORS = [
    (120, 200, 255),    # S - blue
    (255, 180, 100),    # H - orange
    (100, 255, 180),    # A - green
    (255, 120, 180),    # M - pink
    (200, 140, 255),    # S - purple
    (255, 230, 80),     # T - yellow
    (80, 220, 255),     # A - cyan
    (255, 150, 220),    # R - rose
]

BURST_INTERVAL = 0.40  # seconds between each letter burst

class MorphAnimation:
    def __init__(self, text):
        self.text = text
        self.letter_data, self.text_width = get_letter_clouds(
            text, DOTS_PER_LETTER, FONT_SIZE
        )

        num_letters = len(self.letter_data)
        n = DOTS_PER_LETTER * num_letters
        self.n = n

        # Per-dot state
        self.positions = np.random.rand(n, 2) * np.array([WIDTH, HEIGHT])
        self.starts = self.positions.copy()
        self.final_targets = np.zeros((n, 2), dtype=float)
        self.dot_letter = np.zeros(n, dtype=int)

        for i in range(num_letters):
            start = i * DOTS_PER_LETTER
            end = start + DOTS_PER_LETTER if i < num_letters - 1 else n
            self.dot_letter[start:end] = i
            pts = self.letter_data[i]['points']
            for j, idx in enumerate(range(start, end)):
                self.final_targets[idx] = pts[j % len(pts)]

        # Animation state
        self.state = 'idle'
        self.timer = 0
        self.letter_idx = 0
        self.morph_t = 1.0
        self.dot_surf = None
        self.celeb_surfs = []
        self.celebrated = False

        # Burst cascade state
        self.burst_particles = []
        self.burst_letter_idx = 0
        self.burst_timer = 0
        self.cascade_done = False

        # General fireworks
        self.sparkles = []
        self.shooting_stars = []

    def start(self):
        if self.letter_data:
            self.state = 'morphing'
            self._start_morph()

    def _start_morph(self):
        self.starts = self.positions.copy()
        self.morph_t = 0.0

    def _spawn_letter_burst(self, letter_idx):
        ld = self.letter_data[letter_idx]
        color = LETTER_COLORS[letter_idx % len(LETTER_COLORS)]
        for _ in range(120):
            idx = np.random.randint(len(ld['points']))
            self.burst_particles.append(BurstParticle(ld['points'][idx], color))

    def update(self, dt):
        self.timer += dt

        if self.state == 'morphing':
            self.morph_t = min(1.0, self.morph_t + dt / MORPH_TIME)
            t = self.morph_t
            ease = t * t * (3 - 2 * t)

            mask = self.dot_letter == self.letter_idx
            indices = np.where(mask)[0]
            for idx in indices:
                self.positions[idx] = (
                    self.starts[idx]
                    + (self.final_targets[idx] - self.starts[idx]) * ease
                )

            unrevealed = self.dot_letter > self.letter_idx
            if np.any(unrevealed):
                jitter = np.random.uniform(-1, 1, size=(np.sum(unrevealed), 2))
                self.positions[unrevealed] += jitter * dt * 30

            if self.morph_t >= 1.0:
                self.letter_idx += 1
                if self.letter_idx < len(self.letter_data):
                    self._start_morph()
                else:
                    self.state = 'celebrating'
                    self.celebrated = True
                    self.timer = 0
                    self.burst_timer = 0

        elif self.state == 'celebrating':
            # ── Phase 1: Burst cascade ──
            if not self.cascade_done:
                self.burst_timer += dt

                # Start new letter bursts at intervals
                while (self.burst_letter_idx < len(self.letter_data) and
                       self.burst_timer >= self.burst_letter_idx * BURST_INTERVAL):
                    self._spawn_letter_burst(self.burst_letter_idx)
                    self.burst_letter_idx += 1

                # Update burst particles
                for p in self.burst_particles:
                    p.update(dt)
                self.burst_particles = [p for p in self.burst_particles if p.life > 0]

                # Transition to general celebration when all bursts are done
                if (self.burst_letter_idx >= len(self.letter_data) and
                        len(self.burst_particles) == 0):
                    self.cascade_done = True
                    self.timer = 0

            # ── Phase 2: General fireworks ──
            if self.cascade_done and self.timer < CELEB_TIME:
                if np.random.random() < 0.6:
                    ld = np.random.choice(self.letter_data)
                    idx = np.random.randint(len(ld['points']))
                    self.sparkles.append(Sparkle(ld['points'][idx]))
                if np.random.random() < 0.15:
                    hx = np.random.uniform(200, WIDTH - 200)
                    hy = np.random.uniform(20, 80)
                    self.sparkles.append(Sparkle(np.array([hx, hy])))
                if np.random.random() < 0.10:
                    self.shooting_stars.append(ShootingStar())

                shimmer = np.random.uniform(-1, 1, (self.n, 2))
                self.positions += shimmer * dt * 20

            # Update all non-burst particles
            self.sparkles = [s for s in self.sparkles if s.life > 0]
            self.shooting_stars = [s for s in self.shooting_stars if s.life > 0]
            for s in self.sparkles:
                s.update(dt)
            for s in self.shooting_stars:
                s.update(dt)

    def set_dot_surfaces(self, normal_surf, celeb_surfs):
        self.dot_surf = normal_surf
        self.celeb_surfs = celeb_surfs

    def draw(self, screen):
        # Draw letter dots
        for idx in range(self.n):
            pos = self.positions[idx]
            lid = self.dot_letter[idx]
            if self.celebrated:
                surf = self.celeb_surfs[lid % len(self.celeb_surfs)]
            else:
                placed = lid < self.letter_idx or (
                    lid == self.letter_idx and self.morph_t >= 0.01
                )
                if placed:
                    surf = self.dot_surf
                else:
                    pygame.draw.circle(
                        screen, (40, 40, 80),
                        pos.astype(int), max(1, DOT_RADIUS - 1)
                    )
                    continue
            half = surf.get_width() // 2
            screen.blit(surf, pos.astype(int) - np.array([half, half]))

        # Draw burst particle trails (one shared alpha surface)
        if self.state == 'celebrating' and not self.cascade_done:
            trail_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for p in self.burst_particles:
                p.draw_trail(trail_surf)
            screen.blit(trail_surf, (0, 0))
            for p in self.burst_particles:
                p.draw_head(screen)

        # Draw general fireworks
        for s in self.shooting_stars:
            s.draw(screen)
        for s in self.sparkles:
            s.draw(screen)


# ─── Main Loop ─────────────────────────────────────────────
def main():
    text = sys.argv[1] if len(sys.argv) > 1 else "Shamstar"

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("Happy Birthday!")
    clock = pygame.time.Clock()

    anim = MorphAnimation(text)
    running = True
    idle_timer = 0.0
    auto_start_delay = 2.0

    # Pre-render glowing dot surfaces
    glow_size = DOT_RADIUS * 5

    def make_dot_surf(color):
        s = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, 40), (glow_size // 2, glow_size // 2), glow_size // 2)
        pygame.draw.circle(s, (*color, 140), (glow_size // 2, glow_size // 2), DOT_RADIUS + 1)
        pygame.draw.circle(s, color, (glow_size // 2, glow_size // 2), DOT_RADIUS - 1)
        return s

    normal_surf = make_dot_surf(DOT_COLOR)
    celeb_surfs = [make_dot_surf(c) for c in LETTER_COLORS[:len(anim.letter_data)]]
    anim.set_dot_surfaces(normal_surf, celeb_surfs)

    # Fonts for UI
    header_font = pygame.font.SysFont("arial", 44, bold=True)
    hint_font = pygame.font.SysFont("arial", 24)

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and anim.state == 'idle':
                    idle_timer = auto_start_delay
                    anim.start()
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    anim = MorphAnimation(text)
                    anim.set_dot_surfaces(normal_surf, celeb_surfs)
                    idle_timer = 0.0

        if anim.state == 'idle':
            idle_timer += dt
            if idle_timer >= auto_start_delay:
                anim.start()

        anim.update(dt)

        screen.fill(BG_COLOR)

        # ── Draw header ──
        header_text = "Happy Birthday!"
        if anim.state == 'celebrating':
            # Golden glow pulse
            pulse = 0.5 + 0.5 * np.sin(anim.timer * 3)
            glow_color = (200, 180, 80)
            for i, offset in enumerate([(0, 0), (2, 0), (0, 2), (-2, 0), (0, -2)]):
                glow = header_font.render(header_text, True,
                    (int(200 * pulse * (1 - i * 0.15)),
                     int(180 * pulse * (1 - i * 0.15)),
                     int(80 * pulse * (1 - i * 0.15))))
                screen.blit(glow, (WIDTH // 2 - glow.get_width() // 2 + offset[0], 25 + offset[1]))
        header = header_font.render(header_text, True, (255, 220, 100))
        screen.blit(header, (WIDTH // 2 - header.get_width() // 2, 25))

        # ── Draw dots ──
        anim.draw(screen)

        # ── UI hints ──
        if anim.state == 'idle':
            remaining = max(0, auto_start_delay - idle_timer)
            hint = hint_font.render(
                f"SPACE = start  ({remaining:.0f}s auto)  |  ESC = quit  |  R = restart",
                True, (130, 130, 150),
            )
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 40))

        elif anim.state == 'celebrating' and anim.cascade_done and anim.timer >= CELEB_TIME:
            hint = hint_font.render("R = restart  •  ESC = quit", True, (130, 130, 150))
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 40))

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
