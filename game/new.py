import sys, time, os
import pygame
from pygame.locals import *
import random

def read_dialogues(path):
    with open(path, 'r') as n:
        dialogue = n.read()
    dialogue = dialogue.split('\n')
    for item in dialogue:
        yield item


def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list


def physics(rect, movement, tiles):
    collide_dict = {"top": False, 'bottom': False, "right": False, "left": False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collide_dict["right"] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collide_dict["left"] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collide_dict["bottom"] = True
        elif movement[1] < movement[0]:
            rect.top = tile.bottom
            collide_dict["top"] = True
    return rect, collide_dict


def game_map(path):
    with open(path, 'r') as f:
        data = f.read()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map


def load_animation(path, frame_duration):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_duration:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '\\' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((255, 255, 255))
        animation_frames[animation_frame_id] = animation_image.copy()
        for foo in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data


def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame


pygame.init()

clock = pygame.time.Clock()

#screen settings
WINDOW_SIZE = (600, 400)
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
screen_resize = pygame.Surface((300, 200))

#map
game_map = game_map('gamemap/gamemap.txt')

#images
grass = pygame.image.load('images/grass.png').convert()
grass.set_colorkey((255, 255, 255))


#font
font = pygame.font.Font('font/Pixeltype.ttf', 23)
dialog = read_dialogues('Dialogue/dialogue.txt')
txt = ''


#keys and triggers
encounter = False

#player
player_img = pygame.image.load('images/char.png').convert_alpha()
rectangle = player_img.get_rect()
player_img.set_colorkey((255, 255, 255))


#npcs
npc_1 = pygame.image.load('npcs/idle/idle_0.png').convert_alpha()
npc_1_rect = npc_1.get_rect()
npc_1.set_colorkey((255, 255, 255))

#physics
moving_right = False
moving_left = False
player_y_momentum = 0
gravity = 0

#scrolling/airtimer
scroll = [0, 0]
air_timer = 0

#animation
animation_frames = {}
animation_database = {}
animation_database['idle'] = load_animation('player_animations/idle', [10, 30])
animation_database['run'] = load_animation('player_animations/run', [7, 9])
animation_database['jump'] = load_animation('player_animations/jump', [20])

player_action = 'idle'
player_frame = 0
player_flip = False

while True:
    screen_resize.fill((0,191,255))

    scroll[0] += (rectangle.x - scroll[0] - 152)/20
    scroll[1] += (rectangle.y - scroll[1] - 106)/20

    keypress = False

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_d:
                moving_right = True
            if event.key == K_a:
                moving_left = True
            if event.key == K_SPACE:
                if air_timer <= 6:
                    player_y_momentum = -4
            if event.key == K_RETURN:
                keypress = True
        if event.type == KEYUP:
            if event.key == K_d:
                moving_right = False
            if event.key == K_a:
                moving_left = False


    try:
        if keypress:
            txt = next(dialog)
    except StopIteration:
        pass

    npc_movement = [0, 0]
    npc_movement[1] += gravity
    gravity += 0.2
    if gravity > 3: gravity = 3

    player_movement = [0, 0]
    if moving_right: player_movement[0] += 1
    if moving_left: player_movement[0] -= 1
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2
    if player_y_momentum > 3: player_y_momentum = 3

    if player_movement[0] == 0:
        player_action, player_frame = change_action(player_action, player_frame, 'idle')
    if player_movement[0] > 0:
        player_action, player_frame = change_action(player_action, player_frame, 'run')
        player_flip = False
    if player_movement[0] < 0:
        player_action, player_frame = change_action(player_action, player_frame, 'run')
        player_flip = True
    if player_movement[1] < 0:
        player_action, player_frame = change_action(player_action, player_frame, 'jump')

    rect_list = []
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == '1':
                screen_resize.blit(grass, (x * 16 - int(scroll[0]), y * 16 - int(scroll[1])))
            if tile != '0':
                rect_list.append(pygame.Rect(x * 16, y * 16, 16, 16))
            x += 1
        y += 1

    

    player_rect, collision = physics(rectangle, player_movement, rect_list)
    npc_rect, npc_collision = physics(npc_1_rect, npc_movement, rect_list)

    if npc_collision['bottom']:
        gravity = 0

    if collision['bottom']:
        player_y_momentum = 0
        air_timer = 0
    else:
        air_timer += 1

    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]

    screen_resize.blit(pygame.transform.flip(player_img, player_flip, False),(player_rect.x - scroll[0], player_rect.y - scroll[1]))
    screen_resize.blit(npc_1, (npc_rect.x - scroll[0] + 200, npc_rect.y - scroll[1]))
    screen.blit(pygame.transform.scale(screen_resize, WINDOW_SIZE), (0,0))
    text_surface = font.render(txt, False, ('#4E4A48'))
    if player_rect.x > 180 and player_rect.x < 220:
        screen.blit(text_surface, (50, 300))


    clock.tick(60)
    pygame.display.update()
