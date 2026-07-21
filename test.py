import pygame, sys

pygame.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()
surface = pygame.Surface((100, 100))
surface.fill('red')

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)

    screen.blit(surface, (100, 0))
    pygame.display.update()
    clock.tick(60)
