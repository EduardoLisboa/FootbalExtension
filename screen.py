import pygame
import os
pygame.init()
W, H = 630, 468

win = pygame.display.set_mode((W, H))

pygame.display.set_caption('Field')

bg = pygame.image.load(os.path.join('images', 'bg.png')).convert()
bgX = 0
bgX2 = bg.get_width()
Field_height = 408


class std_button():
    def __init__(self,text = '',filled=0,fontScale= 50,colorFont = (0,0,0)):
        self.filled = filled
        self.fontScale = fontScale
        self.colorFont = colorFont
        self.text = text

#A Classe implementa o padrão Introduce Parameter Object
class button():

    def __init__(self, color, x, y, width, height, std):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.std = std

    def draw(self, win, outline=None):

        if outline:
            pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), self.std.filled)

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), self.std.filled)

        if self.std.text != '':
            font = pygame.font.SysFont('comicsans', self.std.fontScale)
            text = font.render(self.std.text, 1, self.std.colorFont)
            win.blit(text, (self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):

        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True

        return False



def RedrawBefore(field,field2):
    win.fill((0,0,0))
    win.blit(bg, (bgX, 0))
    before = button((220, 220, 220), 110, 412, 50, 50, std_button('<'))
    after = button((0, 255, 0), 470, 412, 50, 50, std_button('>'))
    font = pygame.font.SysFont('comicsans', 30)
    field_text = font.render("Campo Antes",1,(255,255,255))
    player_with_ball = False
    for index, team in enumerate([field.left_team, field.right_team], start=1):
        team_color = [0,0,255] if index == 1 else [255,255,0]
        for player in team.team:
            if player.has_ball:
                player_with_ball = True
                pygame.draw.circle(win, [255, 0, 0], (player.x * 6, Field_height - (player.y * 6)), 8)
            pygame.draw.circle(win, team_color, (player.x * 6, Field_height - (player.y * 6)), 5)

    if not player_with_ball:
        pygame.draw.circle(win, [0,0,0], (field.ball_x * 6, Field_height - (field.ball_y * 6)), 5)
    before.draw(win, (0, 0, 0))
    after.draw(win, (0, 0, 0))
    win.blit(field_text,(W/2 - field_text.get_width()/2,412))
    pygame.display.update()
    run = True
    while run:
        pygame.time.delay(100)
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if after.isOver(pos):
                    RedrawAfter(field2,field)
                    run = False


def RedrawAfter(field,field2):
    win.fill((0, 0, 0))
    win.blit(bg, (bgX, 0))
    before = button((0, 255, 0), 110, 412, 50, 50, std_button('<'))
    after = button((220, 220, 220), 470, 412, 50, 50, std_button('>'))
    font = pygame.font.SysFont('comicsans', 30)
    field_text = font.render("Campo Depois", 1, (255, 255, 255))
    player_with_ball = False
    for index, team in enumerate([field.left_team, field.right_team], start=1):
        team_color = [0,0,255] if index == 1 else [255,255,0]
        i = 0
        for player in team.team:
            if player.has_ball:
                player_with_ball = True
                pygame.draw.circle(win, [255, 0, 0], (player.x * 6, Field_height - (player.y * 6)), 8)
            if index == 1:
                pygame.draw.line(win, [255, 0, 0], (field2.left_team.team[i].x * 6,Field_height - (field2.left_team.team[i].y * 6)),(player.x * 6, Field_height - (player.y * 6)),2)
            else:
                pygame.draw.line(win, [255, 0, 0],
                                 (field2.right_team.team[i].x * 6, Field_height - (field2.right_team.team[i].y * 6)),
                                 (player.x * 6, Field_height - (player.y * 6)),2)
            pygame.draw.circle(win, team_color, (player.x * 6, Field_height - (player.y * 6)), 5)
            i +=1
    if not player_with_ball:
        pygame.draw.circle(win, [0,0,0], (field.ball_x * 6, Field_height - (field.ball_y * 6)), 5)
    before.draw(win, (0, 0, 0))
    after.draw(win, (0, 0, 0))
    win.blit(field_text, (W / 2 - field_text.get_width() / 2, 412))
    pygame.display.update()
    run = True
    while run:
        pygame.time.delay(100)
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if before.isOver(pos):
                    RedrawBefore(field2, field)
                    run = False

def DrawField(before,after):
    run = True
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        RedrawBefore(before,after)