import pygame

def process_gray_code():
    print("Processing gray code.")
    pass

def car(x, y, gameDisplay, carImg):
    gameDisplay.blit(carImg, (x,y))

def main():
    pygame.init()

    display_width = 800
    display_height = 600

    gameDisplay = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption('A bit Racey')

    clock = pygame.time.Clock()

    black = (0, 0, 0)
    white = (255, 255, 255)

    carImg = pygame.image.load('racecar.png')
    x = (display_width * 0.45)
    y = (display_height * 0.8)
    x_change = 0
    car_speed = 0

    crashed = False
    gray_code = False
    while not crashed:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -5
                elif event.key == pygame.K_RIGHT:
                    x_change = 5
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    x_change = 0
            print(event)
        x += x_change

        if gray_code:
            process_gray_code()

        gameDisplay.fill(white)
        car(x, y, gameDisplay, carImg)

        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    main()