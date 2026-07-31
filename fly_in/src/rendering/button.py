import pygame as pg
import sys

class Button():
	def __init__(self, image: pg.Surface,
              x_pos: int, y_pos: int,
              text_input: str, font: pg.font.Font):
		self.image = image
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.font = font
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_input = text_input
		self.text = font.render(self.text_input, True, "white")
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def draw(self, screen):
		screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)
	

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			print("Button Press!")

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, "green")
		else:
			self.text = self.font.render(self.text_input, True, "white")

'''
button_surface = pygame.image.load("fly_in/src/rendering/resources/pokeball.png")
button_surface = pygame.transform.scale(button_surface, (400, 150))

button = Button(button_surface, 400, 300, "Button")

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.MOUSEBUTTONDOWN:
			button.checkForInput(pygame.mouse.get_pos())

	screen.fill("white")

	button.update()
	button.changeColor(pygame.mouse.get_pos())

	pygame.display.update()
 '''