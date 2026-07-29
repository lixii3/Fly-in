from fly_in.src.rendering.graphRenderer import GraphRenderer
import pygame as pg
from fly_in.src.graph import Graph
from fly_in.src.parser import Parser
import sys
import os


def test_graph_rendering(graph: Graph):
    pg.init()
    pg.display.set_caption(f"{graph.get_name()} rendering test by lixi")
    screen = pg.display.set_mode()
    screen.fill("#FFFFFF")
    clock = pg.time.Clock()
    graph_sourface = pg.Surface((600, 400))
    graph_rect = graph_sourface.get_rect(topleft=(150,50))
    gr = GraphRenderer(graph_sourface)
    running = True
    while running:
        to_screen = gr.drawGraph(graph)
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
    