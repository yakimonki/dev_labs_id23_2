#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pygame
import random
import time
import sys

# Настройки экрана
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (255, 255, 255)

# Настройка Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Симуляция птиц на столбах")

# Цвета
BIRD_COLOR = (0, 0, 255)
POLE_COLOR = (0, 255, 0)
FALLEN_POLE_COLOR = (255, 0, 0)

# Параметры столбов и птиц
POLE_SPACING = WIDTH // 6
POLE_WIDTH, POLE_HEIGHT = 20, 200
POLE_STRENGTH = 5  # Максимальное количество птиц на столбе
BIRD_SIZE = 6
BIRD_SITTING_TIME_RANGE = (3, 7)  # Время, которое птица сидит на столбе
POLE_REPAIR_TIME = 5  # Время восстановления упавшего столба

# Инициализация столбов
poles = [{
    'position': (POLE_SPACING * (i + 1), HEIGHT - POLE_HEIGHT),
    'strength': POLE_STRENGTH,
    'birds': [],
    'is_fallen': False,
    'fall_time': None
} for i in range(5)]

# Инициализация птиц
birds = [{
    'position': (random.randint(0, WIDTH), random.randint(0, HEIGHT // 2)),
    'sitting': False,
    'sitting_start': None,
    'sitting_time': random.randint(*BIRD_SITTING_TIME_RANGE),
    'target_pole': None
} for _ in range(10)]

# Основной игровой цикл
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BACKGROUND_COLOR)

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

    # Обновление состояния столбов
    for pole in poles:
        if pole['is_fallen'] and time.time() - pole['fall_time'] > POLE_REPAIR_TIME:
            pole['is_fallen'] = False

    # Обновление состояния птиц
    for bird in birds:
        if not bird['sitting']:
            # Если птица не сидит, выбираем случайный столб для посадки
            if bird['target_pole'] is None or bird['target_pole']['is_fallen']:
                available_poles = [pole for pole in poles if not pole['is_fallen']]
                if available_poles:
                    bird['target_pole'] = random.choice(available_poles)

            # Птица летит к столбу
            if bird['target_pole']:
                target_x, target_y = bird['target_pole']['position']
                bird['position'] = (
                    bird['position'][0] + (target_x - bird['position'][0]) * 0.02,
                    bird['position'][1] + (target_y - bird['position'][1]) * 0.02
                )

                # Проверяем, достигла ли птица столба
                if abs(bird['position'][0] - target_x) < 5:
                    if len(bird['target_pole']['birds']) < bird['target_pole']['strength']:
                        bird['target_pole']['birds'].append(bird)
                        bird['sitting'] = True
                        bird['sitting_start'] = time.time()
                    else:
                        bird['target_pole']['is_fallen'] = True
                        bird['target_pole']['fall_time'] = time.time()
                        bird['target_pole']['birds'].clear()
        else:
            # Если птица сидит, проверяем, прошло ли время ожидания
            if time.time() - bird['sitting_start'] >= bird['sitting_time']:
                bird['sitting'] = False
                bird['target_pole']['birds'].remove(bird)
                bird['target_pole'] = None
                bird['sitting_start'] = None

    # Отрисовка столбов
    for pole in poles:
        color = FALLEN_POLE_COLOR if pole['is_fallen'] else POLE_COLOR
        pygame.draw.rect(screen, color, (pole['position'][0] - POLE_WIDTH // 2, pole['position'][1], POLE_WIDTH, POLE_HEIGHT))

    # Отрисовка птиц
    for bird in birds:
        pygame.draw.circle(screen, BIRD_COLOR, (int(bird['position'][0]), int(bird['position'][1])), BIRD_SIZE)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()


# In[ ]:




