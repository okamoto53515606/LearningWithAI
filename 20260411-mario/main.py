import pygame
import sys
import os

pygame.init()

info = pygame.display.Info()
screen_w, screen_h = info.current_w, info.current_h
screen = pygame.display.set_mode((screen_w, screen_h), pygame.FULLSCREEN)
pygame.display.set_caption("マリオワンダー")

base = os.path.dirname(__file__)
image_files = ["zelda_battle.jpg", "zelda_weapon.jpg", "badges_all.png"]
bg_colors = [(30, 50, 30), (40, 40, 60), (50, 50, 80)]

images = []
positions = []
for fname in image_files:
    path = os.path.join(base, "images", fname)
    img = pygame.image.load(path).convert()
    iw, ih = img.get_size()
    sc = min(screen_w / iw, screen_h / ih)
    nw, nh = int(iw * sc), int(ih * sc)
    img = pygame.transform.smoothscale(img, (nw, nh))
    images.append(img)
    positions.append(((screen_w - nw) // 2, (screen_h - nh) // 2))

current = 0
font = pygame.font.SysFont("meiryo", 40)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE:
                current = (current + 1) % len(images)
            if event.key == pygame.K_LEFT:
                current = (current - 1) % len(images)

    screen.fill(bg_colors[current % len(bg_colors)])
    screen.blit(images[current], positions[current])

    names = ["ゼルダ ライネルとたたかう！", "ゼルダ ぶき！", "ワンダー バッジいちらん"]
    label = font.render(names[current], True, (255, 255, 255))
    screen.blit(label, (screen_w // 2 - label.get_width() // 2, 30))

    hint = font.render("← → キーで きりかえ ／ Escでとじる", True, (200, 200, 200))
    screen.blit(hint, (screen_w // 2 - hint.get_width() // 2, screen_h - 60))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
