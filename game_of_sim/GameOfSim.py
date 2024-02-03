import pygame
import sys
import math
from sim import Sim

POINT_SIZE = 5
HEXA_SIZE = 300
FONT_VERTEX_SIZE = 30
HOVER_DISTANCE = 5
SCREEN_WIDTH, SCREEN_HEIGHT = 1100, 700
points = {}
A = B = C = D = E = F = (0, 0)

# Initialize Pygame
pygame.init()

sim = Sim()
is_hovered = False
edge_hovered = ""

# Set up the window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game of Sim")
center_x, center_y = SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT // 2
font_vertex = pygame.font.Font(None, FONT_VERTEX_SIZE)

mnu_hm_rect = pygame.Rect(50, 20, 350, 50)
mnu_hh_rect = pygame.Rect(50, 80, 350, 50)
next_turn_rect = pygame.Rect(50, 130, 350, 50)
font_mnu = pygame.font.Font(None, 30)
font_info = pygame.font.Font(None, 22)

def draw_menu():
    for mnu_rect in [mnu_hm_rect, mnu_hh_rect]:
        pygame.draw.rect(screen, "lightgrey", mnu_rect)
        pygame.draw.rect(screen, "black", mnu_rect, 2)
        text = font_mnu.render("New game Human vs Machine" if mnu_rect == mnu_hm_rect else "New game Human vs Human", True, "darkgreen" if (sim.use_engine and mnu_rect==mnu_hm_rect) or (not sim.use_engine and mnu_rect==mnu_hh_rect) else "black")
        text_rect = text.get_rect(center=mnu_rect.center)
        screen.blit(text, text_rect)
def draw_info():
    screen.blit(font_info.render("Next turn:", True, "black"), (20, 250))
    if not sim.is_finished():
        if sim.is_blue_turn():
            text = font_info.render("Blue", True, "blue")
        else:
            text = font_info.render("Red", True, "red")
        screen.blit(text, (100, 250))
    screen.blit(font_info.render("Moves:", True, "black"), (20, 280))
    for i, edge in enumerate(sim.get_moves()):
        screen.blit(font_info.render(edge, True, "red" if i%2==0 else "blue"), (75 + i*26, 280))
    if sim.is_finished():
        screen.blit(font_info.render("Game over. The winner is:", True, "black"), (20, 310))
        screen.blit(font_mnu.render("Blue" if sim.is_blue_turn() else "Red", True, "blue" if sim.is_blue_turn() else "red"), (220, 306))
        screen.blit(font_info.render("The monochromatic triangle is:", True, "black"), (20, 340))
        for i, edge in enumerate(sim.get_triangle_edges()):
            screen.blit(font_mnu.render(edge, True, "red" if sim.is_blue_turn() else "blue"), (250 + i*35, 336))

def init(size):
    global A, B, C, D, E, F
    global points
    points = {'A': (0, size),
              'B': (math.sqrt(3)*size/2, size/2),
              'C': (math.sqrt(3)*size/2, -size/2),
              'D': (0, -size),
              'E': (-math.sqrt(3)*size/2, -size/2),
              'F': (-math.sqrt(3)*size/2, size/2)}
    for key, point in points.items():
        x, y = point
        new_point = (center_x + x, center_y - y)
        points[key] = new_point
    A, B, C, D, E, F = points['A'], points['B'], points['C'], points['D'], points['E'], points['F']

def draw_line(line, color="lightgrey", thickness=2):
    if len(line) != 2 or not (line[0]>='A' and line[0]<='F') or not (line[1]>='A' and line[1]<='F'):
        raise Exception(f"line {line} is not in a correct format")
    P1 = points[line[0]]
    P2 = points[line[1]]
    # global screen
    pygame.draw.line(screen, color, P1, P2, thickness)

def draw_point(label, point, color="black"):
    x,y = point
    pygame.draw.circle(screen, color, point, POINT_SIZE)
    if (label == 'A'):
        y-=15
    elif (label == 'D'):
        y+=18
    elif (label in ('B', 'F')):
        y-=5
    elif (label in ('C', 'E')):
        y+=5
    if (x < center_x):
        x-=15
    elif (x > center_x):
        x+=15
    text = font_vertex.render(label, True, "black")
    screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))

# Function to check if the mouse is within a certain distance from the line
def is_mouse_near_line(mouse_pos, line, distance):
    x1, y1 = points[line[0]]
    x2, y2 = points[line[1]]

    # Calculate the distance from the mouse to the line using the formula for the distance between a point and a line
    distance_to_line = abs((y2 - y1) * mouse_pos[0] - (x2 - x1) * mouse_pos[1] + x2 * y1 - y2 * x1) / math.sqrt((y2 - y1)**2 + (x2 - x1)**2)

    return distance_to_line <= distance and mouse_pos[0] <= max(x1, x2)+distance and mouse_pos[0] >= min(x1, x2)-distance and mouse_pos[1] <= max(y1, y2)+distance and mouse_pos[1] >= min(y1, y2)-distance

init(HEXA_SIZE)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if event.button == 1 and is_hovered:  # Left mouse button
                sim.play(edge_hovered)
            if mnu_hh_rect.collidepoint(x, y):
                sim.use_engine = False
                sim.reset()
            elif mnu_hm_rect.collidepoint(x, y):
                sim.use_engine = True
                sim.reset()

    # Clear the screen
    screen.fill("white")

    for edge in sim.get_all_edge_labels():
        draw_line(edge)

    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()

    # Check if the mouse is within a certain distance from the line
    for edge in sim.get_all_edge_labels():
        if (sim.get_edge_color(edge) > 0):
            continue
        is_hovered = is_mouse_near_line(mouse_pos, edge, HOVER_DISTANCE)
        if (is_hovered):
            draw_line(edge, "blue" if sim.is_blue_turn() else "red", thickness=4)
            pygame.mouse.set_cursor(*pygame.cursors.tri_left)
            edge_hovered = edge
            break
        else:
            draw_line(edge)
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
            edge_hovered = ""

    move_num = 1
    for edge in sim.get_moves():
        draw_line(edge, "red" if move_num % 2 == 1 else "blue")
        move_num += 1

    for label, point in points.items():
        draw_point(label, point)

    draw_menu()
    draw_info()

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
