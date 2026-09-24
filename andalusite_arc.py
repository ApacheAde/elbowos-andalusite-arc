#!/usr/bin/env python3
"""Andalusite Arc — neon magnetic-volley arcade for ElbowOS."""
from __future__ import annotations

import math
import os
import random
import subprocess
import sys

import pygame

W, H = 1080, 1920
FPS = 30
TITLE = "ANDALUSITE ARC"
HANDLE = "x.com/ElbowOS"

VOID = (8, 6, 22)
INK = (18, 12, 40)
TEAL = (32, 214, 196)
GOLD = (255, 196, 72)
PINK = (255, 72, 168)
CREAM = (255, 244, 228)
VIO = (168, 92, 255)
COPPER = (255, 120, 48)
LIME = (140, 255, 90)
NAVY = (28, 22, 64)


class Spark:
    __slots__ = ("x", "y", "vx", "vy", "life", "col", "r")

    def __init__(self, x, y, vx, vy, life, col, r=4):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.life, self.col, self.r = life, col, r


class Game:
    def __init__(self, record: bool):
        self.record = record
        self.surf = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.Font(None, 56)
        self.font_md = pygame.font.Font(None, 42)
        self.font_sm = pygame.font.Font(None, 30)
        self.screen = None
        if not record:
            self.screen = pygame.display.set_mode((W, H))
            pygame.display.set_caption(TITLE)
        self.reset()

    def reset(self) -> None:
        self.t = 0.0
        self.score = 0
        self.opp = 0
        self.px = W * 0.5
        self.ox = W * 0.5
        self.pw = 168
        self.ow = 168
        self.cx, self.cy = W * 0.5, H * 0.46
        self.cr = 78
        self.spin = 0.0
        self.ball = [W * 0.5, H * 0.62, random.choice((-1, 1)) * 420, -640]
        self.sparks: list[Spark] = []
        self.pops: list[tuple] = []
        self.stars = [(random.randint(0, W), random.randint(0, H), random.random()) for _ in range(90)]
        self.running = True
        self.flash = 0.0
        self.trail: list[tuple] = []

    def burst(self, x, y, col, n=14) -> None:
        for _ in range(n):
            a = random.uniform(0, math.tau)
            sp = random.uniform(90, 420)
            self.sparks.append(Spark(x, y, math.cos(a) * sp, math.sin(a) * sp,
                                     random.uniform(0.18, 0.5), col, random.randint(3, 7)))

    def update(self, dt: float) -> None:
        self.t += dt
        self.flash = max(0.0, self.flash - dt)
        self.spin += dt * 1.8
        self.cr = 72 + 10 * math.sin(self.t * 2.4)
        if self.record:
            self.autoplay(dt)
        bx, by, vx, vy = self.ball
        dx, dy = self.cx - bx, self.cy - by
        dist = max(40.0, math.hypot(dx, dy))
        pull = 78000.0 / (dist * dist)
        vx += (dx / dist) * pull * dt
        vy += (dy / dist) * pull * dt
        pxp, pyp = -dy / dist, dx / dist
        swirl = 420.0 * math.sin(self.t * 1.7)
        vx += pxp * swirl * dt
        vy += pyp * swirl * dt
        spd = math.hypot(vx, vy)
        if spd > 980:
            vx, vy = vx / spd * 980, vy / spd * 980
        if spd < 380:
            vx, vy = vx / max(1, spd) * 380, vy / max(1, spd) * 380
        bx += vx * dt
        by += vy * dt
        if bx < 48 or bx > W - 48:
            vx *= -1
            bx = max(48, min(W - 48, bx))
            self.burst(bx, by, GOLD, 8)
        py, oy = 1688, 236
        if py - 18 <= by <= py + 28 and abs(bx - self.px) < self.pw * 0.55:
            by = py - 20
            vy = -abs(vy) - 40
            vx += (bx - self.px) * 3.2
            self.burst(bx, by, TEAL, 12)
        if oy - 28 <= by <= oy + 18 and abs(bx - self.ox) < self.ow * 0.55:
            by = oy + 22
            vy = abs(vy) + 40
            vx += (bx - self.ox) * 3.2
            self.burst(bx, by, PINK, 12)
        if by > H - 40:
            self.opp += 1
            self.pops.append(("RIFT +1", W // 2, H * 0.5, 0.7, PINK))
            self.flash = 0.18
            self.burst(bx, by, PINK, 22)
            bx, by, vx, vy = W * 0.5, H * 0.5, random.uniform(-200, 200), 520
        if by < 150:
            self.score += 1
            self.pops.append(("ARC +1", W // 2, H * 0.5, 0.7, TEAL))
            self.flash = 0.18
            self.burst(bx, by, TEAL, 22)
            bx, by, vx, vy = W * 0.5, H * 0.5, random.uniform(-200, 200), -520
        self.ball = [bx, by, vx, vy]
        self.trail.append((bx, by))
        self.trail = self.trail[-18:]
        sparks = []
        for sp in self.sparks:
            sp.x += sp.vx * dt
            sp.y += sp.vy * dt
            sp.life -= dt
            if sp.life > 0:
                sparks.append(sp)
        self.sparks = sparks[-220:]
        self.pops = [(a, x, y - 50 * dt, life - dt, c) for a, x, y, life, c in self.pops if life - dt > 0]
        self.px = max(110, min(W - 110, self.px))
        self.ox = max(110, min(W - 110, self.ox))

    def autoplay(self, dt: float) -> None:
        bx, by, vx, vy = self.ball
        aim = bx + vx * 0.18
        self.px += (aim - self.px) * min(1.0, 7.2 * dt)
        oaim = bx + vx * 0.12 + 40 * math.sin(self.t * 3.1)
        self.ox += (oaim - self.ox) * min(1.0, 6.4 * dt)

    def draw(self, s: pygame.Surface) -> None:
        s.fill(VOID)
        for sx, sy, tw in self.stars:
            yy = int((sy + self.t * (10 + tw * 28)) % H)
            c = 40 + int(tw * 80)
            pygame.draw.circle(s, (c // 3, c // 2, c), (sx, yy), 1 + int(tw * 2))
        pygame.draw.rect(s, INK, pygame.Rect(28, 160, W - 56, H - 280), border_radius=28)
        pygame.draw.rect(s, NAVY, pygame.Rect(28, 160, W - 56, H - 280), 3, border_radius=28)
        pygame.draw.line(s, (50, 40, 90), (60, H * 0.5), (W - 60, H * 0.5), 2)
        glow = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*COPPER, 36), (int(self.cx), int(self.cy)), int(self.cr + 70))
        pygame.draw.circle(glow, (*VIO, 50), (int(self.cx), int(self.cy)), int(self.cr + 28))
        s.blit(glow, (0, 0))
        pygame.draw.circle(s, COPPER, (int(self.cx), int(self.cy)), int(self.cr))
        pygame.draw.circle(s, GOLD, (int(self.cx), int(self.cy)), int(self.cr * 0.62))
        pygame.draw.circle(s, CREAM, (int(self.cx - 12), int(self.cy - 14)), 10)
        for i in range(6):
            a = self.spin + i * math.tau / 6
            pygame.draw.line(
                s, PINK,
                (self.cx + math.cos(a) * (self.cr + 8), self.cy + math.sin(a) * (self.cr + 8)),
                (self.cx + math.cos(a) * (self.cr + 46), self.cy + math.sin(a) * (self.cr + 46)), 3)
        for i, (tx, ty) in enumerate(self.trail):
            pygame.draw.circle(s, TEAL, (int(tx), int(ty)), max(2, i // 3))
        bx, by = self.ball[0], self.ball[1]
        pygame.draw.circle(s, CREAM, (int(bx), int(by)), 18)
        pygame.draw.circle(s, LIME, (int(bx), int(by)), 12)
        pygame.draw.circle(s, GOLD, (int(bx - 4), int(by - 4)), 4)
        pygame.draw.rect(s, TEAL, pygame.Rect(int(self.px - self.pw / 2), 1676, int(self.pw), 28), border_radius=10)
        pygame.draw.rect(s, CREAM, pygame.Rect(int(self.px - self.pw / 2), 1676, int(self.pw), 28), 2, border_radius=10)
        pygame.draw.rect(s, PINK, pygame.Rect(int(self.ox - self.ow / 2), 220, int(self.ow), 28), border_radius=10)
        pygame.draw.rect(s, CREAM, pygame.Rect(int(self.ox - self.ow / 2), 220, int(self.ow), 28), 2, border_radius=10)
        for sp in self.sparks:
            pygame.draw.circle(s, sp.col, (int(sp.x), int(sp.y)), max(1, int(sp.r * sp.life / 0.4)))
        if self.flash > 0:
            veil = pygame.Surface((W, H), pygame.SRCALPHA)
            veil.fill((255, 180, 80, int(48 * self.flash / 0.18)))
            s.blit(veil, (0, 0))
        title = self.font_lg.render(TITLE, True, GOLD)
        s.blit(title, title.get_rect(center=(W // 2, 52)))
        handle = self.font_sm.render(HANDLE, True, TEAL)
        s.blit(handle, handle.get_rect(center=(W // 2, 102)))
        s.blit(self.font_md.render(f"YOU  {self.score}", True, TEAL), (72, 1788))
        s.blit(self.font_md.render(f"RIFT  {self.opp}", True, PINK), (W - 280, 1788))
        hint = self.font_sm.render("bend the shard around the andalusite core", True, CREAM)
        s.blit(hint, hint.get_rect(center=(W // 2, 1844)))
        for tag, x, y, life, col in self.pops:
            img = self.font_md.render(tag, True, col)
            s.blit(img, img.get_rect(center=(int(x), int(y))))
        foot = self.font_sm.render("A/D move  R reset  ESC quit", True, (190, 170, 200))
        s.blit(foot, foot.get_rect(center=(W // 2, H - 24)))

    def handle(self, ev) -> None:
        if ev.type == pygame.QUIT:
            self.running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                self.running = False
            elif ev.key == pygame.K_r:
                self.reset()

    def play(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for ev in pygame.event.get():
                self.handle(ev)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.px -= 760 * dt
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.px += 760 * dt
            self.update(dt)
            self.draw(self.surf)
            self.screen.blit(self.surf, (0, 0))
            pygame.display.flip()

    def record_mp4(self, path: str) -> None:
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "fast", "-movflags", "+faststart", path,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        frames = FPS * 15
        for i in range(frames):
            self.update(1.0 / FPS)
            self.draw(self.surf)
            proc.stdin.write(pygame.image.tostring(self.surf, "RGB"))
            if i % 30 == 0:
                print(f"frame {i}/{frames}", flush=True)
        proc.stdin.close()
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed: {rc}")
        print("wrote", path)


def main() -> None:
    record = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
    play = "--play" in sys.argv
    if record or not play:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    g = Game(record or not play)
    if record or not play:
        out = os.environ.get("ELBOWOS_MP4", "/home/workdir/artifacts/ANDALUSITE_ARC_ElbowOS.mp4")
        g.record_mp4(out)
    else:
        g.play()
    pygame.quit()


if __name__ == "__main__":
    main()
