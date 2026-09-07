from fly_in.src.rendering.renderer import Renderer
import pygame as pg
from fly_in.src.graph import Graph
from fly_in.src.parser import Parser
import os


def test_graph_rendering(graph: Graph):
    pg.init()

    pg.display.set_caption(f"{graph.get_name()} rendering test by lixi")
    screen = pg.display.set_mode()
    background = pg.image.load("fly_in/src/rendering/"
                               "resources/bg/latios.jpg").convert()
    background = pg.transform.scale(background, (screen.get_width(),
                                                 screen.get_height()))
    screen.blit(background, (0, 0))
    graph_sourface = pg.Surface((1500, 900), flags=pg.SRCALPHA)
    graph_rect = graph_sourface.get_rect()
    graph_rect.center = screen.get_width() // 2, screen.get_height() // 2
    gr = Renderer.GraphRenderer()

    clock = pg.time.Clock()
    running = True
    while running:
        screen.blit(graph_sourface, graph_rect)
        pg.display.flip()
        clock.tick(60)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

    pg.quit()


if __name__ == "__main__":
    dir_path = "fly_in/maps/easy/"
    parser: Parser = Parser
    try:
        file_list = [f for f in os.listdir(dir_path) if f.endswith('.txt')]
    except OSError as e:
        raise e
    print(file_list)
    for f in file_list:
        graph = parser.parse_map(dir_path+f)
        test_graph_rendering(graph)
