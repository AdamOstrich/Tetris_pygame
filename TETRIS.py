#!usr/bin/env/python3
"""
Moja gra Tetris.
Tworzona przy pomocy tutorialu: https://www.youtube.com/watch?v=uoR4ilCWwKA&t=217s
W grze wciaz wystepuja bagi, konkretnie:
    - gracz jest w stanie wyklikac klocek w bok, tak ze zniknie z ekranu
    - czasami program usunie pelen wiersz bez przesuniecia wszystkiego ponad w dol
"""

import random
import pygame
from pygame.locals import *

pygame.font.init()

#Zmienne globalne:
SCREEN_WIDTH = 700 #szerokosc calego okna
SCREEN_HEIGHT = 700 #wysokosc calego okna
TABLE_WIDTH = 300 #szerokosc planszy 10x30px
TABLE_HEIGHT = 600 #wysokosc planszy 20x30px
CELL_SIZE = 30 #szerokosc i wysokosc jednej komorki na planszy
RESULT = 0 #zdobywane punkty
EXECUTED_ROWS = 250 #liczba usunietych wierszy
input_box = pygame.Rect(100, 100, 140, 32) #okienko do podowania nicka gracza
NICK = ""
SPEED_LEVEL = 10 #poziom od 1 do 10 - uzaleznione od liczby straconych wierszy
HIGHEST_RESULT = 0 #rekord pobrany z pliku
HIGHEST_RESULT_OWNER = "" #nick wpisany przy najwyzszym wyniku

#lista figur:
shapes = [
    [['.....', '0000.', '.....', '.....', '.....'], ['..0..', '..0..', '..0..', '..0..', '.....']],  # 1x4
    [['.....', '..00.', '..00.', '.....', '.....']],  # kwadrat
    [['.....', '..00.', '.00..', '.....', '.....'], ['.....', '.0...', '.00..', '..0..', '.....']],  # S
    [['.....', '.00..', '..00.', '.....', '.....'], ['.....', '..0..', '.00..', '.0...', '.....']],  # Z
    [['.....', '...0.', '.000.', '.....', '.....'], ['.....', '..0..', '..0..', '..00.', '.....'], \
     ['.....', '.....', '.000.', '.0...', '.....'], ['.....', '.00..', '..0..', '..0..', '.....']],  # L
    [['.....', '.0...', '.000.', '.....', '.....'], ['.....', '.00..', '.0...', '.0...', '.....'], \
     ['.....', '.....', '.000.', '...0.', '.....'], ['.....', '..0..', '..0..', '.00..', '.....']],  # J
    [['.....', '..0..', '.000.', '.....', '.....'],['.....', '..0..', '..00.', '..0..', '.....'],['.....', '.....', '.000.', '..0..', '.....'],['.....', '..0..', '.00..', '..0..', '.....']] #piramida
]
colors = [(255,0,0),(0,255,0),(0,0,255),(128,128,0),(0,128,128),(128,0,128),(128,128,128)] #kazda figura ma swoj ksztalt

class Klocek(object): #klasa do spadajacych klockow
    rows = 20
    columns = 10
    def __init__(self, columns, rows, shape):
        self.x = columns
        self.y = rows
        self.shape = shape
        self.color = colors[shapes.index(shape)]
        self.pozycja = 0

def tworzenie_klocka(): #przy nowym klocku pozycja startowa zawsze ta sama, a klocki sa losowe z listy figur
    global shapes, colors
    return Klocek(5,0, random.choice(shapes))

def obrot(klocek): #funkcja obracania klockow
    positions = []
    format = klocek.shape[klocek.pozycja % len(klocek.shape)] # % len(klocek.shape) - by mozna bylo zrobic wiecej niz pelen obrot klockiem
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((klocek.x + j, klocek.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions

def glowny_napis(text, size, color, surface): #funkcja do wyswietlania obrazu przerwy miedzy grami
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (75, 350))

def napis_w_czasie_gry(surface): #rzeczy wyswietlane po prawej stronie ekranu w czasie grania
    global RESULT, SPEED_LEVEL, NICK, HIGHEST_RESULT, HIGHEST_RESULT_OWNER
    font = pygame.font.SysFont('comicsans', 35, bold=True)
    label = font.render("RESULT: " + str(RESULT), 1, (255,255,255))
    surface.blit(label, (400, 450))
    font = pygame.font.SysFont('comicsans', 35, bold=True)
    label = font.render("LEVEL: " + str(SPEED_LEVEL), 1, (255, 255, 255))
    surface.blit(label, (400, 250))
    font = pygame.font.SysFont('comicsans', 35, bold=True)
    label = font.render("PLAYER: " + NICK, 1, (255, 255, 255))
    surface.blit(label, (400, 100))
    font = pygame.font.SysFont('comicsans', 25, bold=True)
    label = font.render("RECORD: " + str(HIGHEST_RESULT) + " - " + HIGHEST_RESULT_OWNER, 1, (0, 255, 0))
    surface.blit(label, (400, 50))

def draw_grid(surface, row, col): #szara siatka planszy
    sx = 50
    sy = 50
    for i in range(row):
        pygame.draw.line(surface, (128,128,128), (sx, sy+ i*30), (sx + TABLE_WIDTH, sy + i * 30))  # horizontal lines
        for j in range(col):
            pygame.draw.line(surface, (128,128,128), (sx + j * 30, sy), (sx + j * 30, sy + TABLE_HEIGHT))  # vertical lines

def all_window(surface): #funkcja do startowego ekranu gry (siatka + ramka)
    surface.fill((0, 50, 0))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (50 + j * 30, 50 + i * 30, 30, 30), 0) #start tego ekranu na (50,50)

    draw_grid(surface, 20, 10)
    pygame.draw.rect(surface, (255, 0, 0), (50, 50, TABLE_WIDTH, TABLE_HEIGHT), 5)
    # pygame.display.update()

def nastepny_klocek(shape, surface): #wyswietlanie nastepnych klockow
    format = shape.shape[shape.pozycja % len(shape.shape)]
    x, y = 400, 600

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':                                                           #rozkminic jak te klocki ogarniac
                speed_increase()
                pygame.draw.rect(surface, shape.color, (x + j*30, y + i*30, 30,30), 0)
                napis_w_czasie_gry(win)

def speed_increase(): #switch do ustalania szybkosci spadku klockow uzalezniony od ilosci zbitych linii
    global EXECUTED_ROWS, SPEED_LEVEL
    if EXECUTED_ROWS > 225:
        SPEED_LEVEL = 10
    elif EXECUTED_ROWS > 180:
        SPEED_LEVEL = 9
    elif EXECUTED_ROWS > 140:
        SPEED_LEVEL = 8
    elif EXECUTED_ROWS > 105:
        SPEED_LEVEL = 7
    elif EXECUTED_ROWS > 75:
        SPEED_LEVEL = 6
    elif EXECUTED_ROWS > 50:
        SPEED_LEVEL = 5
    elif EXECUTED_ROWS > 30:
        SPEED_LEVEL = 4
    elif EXECUTED_ROWS > 15:
        SPEED_LEVEL = 3
    elif EXECUTED_ROWS > 5:
        SPEED_LEVEL = 2

def usuwanie_wierszy(grid, locked): #funkcja zwalniania pelnych wierszy
    global RESULT, EXECUTED_ROWS

    licznik_usunietych_wierszy = 0 #
    pozycja_do_usuniecia = 0
    for i in range(len(grid) -1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            licznik_usunietych_wierszy += 1
            pozycja_do_usuniecia = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue

    if licznik_usunietych_wierszy == 4:
        RESULT += 1000
        EXECUTED_ROWS += 4
    elif licznik_usunietych_wierszy == 3:
        RESULT += 500
        EXECUTED_ROWS += 3
    elif licznik_usunietych_wierszy == 2:
        RESULT += 200
        EXECUTED_ROWS += 2
    elif licznik_usunietych_wierszy == 1:
        RESULT += 50
        EXECUTED_ROWS += 1

    if licznik_usunietych_wierszy > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < pozycja_do_usuniecia:
                newKey = (x, y + licznik_usunietych_wierszy)
                locked[newKey] = locked.pop(key)


def valid_space(shape, grid): #sprawdzanie wolnych pozycji dla wewnatrz planszy, by ewentualnie pozwolic klockowi na obrot
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = obrot(shape)
    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True


def create_grid(locked_positions={}): #tworzenie siatki/jej aktualizowanie
    grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid

def check_lost(positions): #sprawdza czy sprawdzana komorka jest wolna czy zajeta
    for pos in positions:
        x, y = pos
        if y == 0:
            return True
    return False

def speed_of_falling(): #przyspieszenie naszej gry
    global SPEED_LEVEL
    if SPEED_LEVEL == 1:
        return 0.3
    elif SPEED_LEVEL == 2:
        return 0.26
    if SPEED_LEVEL == 3:
        return 0.22
    if SPEED_LEVEL == 4:
        return 0.19
    elif SPEED_LEVEL == 5:
        return 0.17
    if SPEED_LEVEL == 6:
        return 0.15
    elif SPEED_LEVEL == 7:
        return 0.13
    if SPEED_LEVEL == 8:
        return 0.11
    if SPEED_LEVEL == 9:
        return 0.10
    elif SPEED_LEVEL == 10:
        return 0.09

def main(): #glowna funkcja grajaca, tu trwa rzeczywista gra
    global grid, RESULT, SPEED_LEVEL, EXECUTED_ROWS, HIGHEST_RESULT, HIGHEST_RESULT_OWNER

    with open("wyniki.txt") as f: #pobieranie nalepszego wyniku z pliku i jego wlasciciela
        data = f.read()
        veriable = ""
        i = 0
        while ord(data[i]) != 32:
            veriable += data[i]
            i += 1
        HIGHEST_RESULT = int(veriable)
        veriable = ""
        i += 1
        while ord(data[i]) != 32:
            veriable += data[i]
            i += 1
        HIGHEST_RESULT_OWNER = veriable
    #print(HIGHEST_RESULT_OWNER)
    RESULT = 0
    SPEED_LEVEL = 1
    EXECUTED_ROWS = 0
    locked_positions = {}
    grid = create_grid(locked_positions)

    running = True
    change = False
    current_klocek = tworzenie_klocka()
    next_klocek = tworzenie_klocka()
    clock = pygame.time.Clock()
    fall_time = 0

    while running:
        fall_speed = speed_of_falling()
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()
        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_klocek.y += 1
            if not valid_space(current_klocek, grid) and current_klocek.y > 0:
                current_klocek.y -= 1
                change = True

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_klocek.x -= 1
                    if not valid_space(current_klocek, grid):
                        current_klocek.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_klocek.x += 1
                    if not valid_space(current_klocek, grid):
                        current_klocek.x -= 1
                elif event.key == pygame.K_UP:
                    current_klocek.pozycja = current_klocek.pozycja + 1 % len(current_klocek.shape)
                    if not valid_space(current_klocek, grid):
                        current_klocek.pozycja = current_klocek.pozycja - 1 % len(current_klocek.shape)

                if event.key == pygame.K_DOWN:
                    RESULT += 1
                    current_klocek.y += 1
                    if not valid_space(current_klocek, grid):
                        current_klocek.y -= 1

        shape_pos = obrot(current_klocek)

        # add piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_klocek.color

        if change: #przy ladowaniu klocka, tworzenie kolejnego
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_klocek.color
            current_klocek = next_klocek
            next_klocek = tworzenie_klocka()
            change = False

            usuwanie_wierszy(grid, locked_positions) #sprawdzenie czterokrotne, by uniknac nie znikania

        all_window(win)
        nastepny_klocek(next_klocek, win)
        pygame.display.update()

        if check_lost(locked_positions): #sprawdzanie przegranej
            running = False
        #print("samoloty")
    text = "GAME OVER\nYOU HAVE " + str(RESULT)
    if HIGHEST_RESULT < RESULT:
        with open("wyniki.txt", "w") as f: #zapisywanie nowego najlepszego wyniku
            f.write(str(RESULT) + " " + NICK + " ")

    glowny_napis(text, 40, (255, 255, 255), win)
    pygame.display.update()
    pygame.time.delay(2000)

def start_z_podaniem_nicku(surface): #funkcja od przyjmowania nicku gracza, by zapisac ewentualny rekord
    global NICK

    glowny_napis('Enter your nick: ', 40, (255, 255, 255), win)
    pygame.display.update()
    text = ''
    Done = 0
    clock = pygame.time.Clock()
    input_box = pygame.Rect(400, 350, 140, 32)
    font = pygame.font.Font(None, 32)

    while Done == 0:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Done = 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    #print(text,"return1, Done= ", Done)
                    NICK = text
                    Done += 1
                    #print(text,"return2, Done= ", Done)
                    break
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                    #print("backspace")
                else:
                    text += event.unicode
                    #print("sign")
                #print(NICK)
        if Done != 0:
            #print("!=0")
            break
        surface.fill((30, 30, 30))
        txt_surface = font.render(text, True, (255,255,255))
        width = 200
        input_box.w = width
        surface.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(surface, (255,255,255), input_box, 2)
        glowny_napis('Enter your nick: ', 40, (255, 255, 255), win)
        pygame.display.flip()
        clock.tick(30)


def menu(): #funkcja startu rzeczywistej gry
    running = True
    start_z_podaniem_nicku(win)
    while running:
        win.fill((0,0,0))
        glowny_napis('Press enter to begin or press escape to quit.', 32, (255, 255, 255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    main()
                elif event.key == pygame.K_ESCAPE:
                    quit()
    pygame.quit()


win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris') #zdaje sie byc pointless
menu()