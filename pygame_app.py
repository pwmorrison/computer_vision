import pygame
from gray_code import generate_gray_code_sequence, generate_gray_code_bit_planes

def process_gray_code():
    print("Processing gray code.")
    pass

def car(x, y, gameDisplay, carImg):
    gameDisplay.blit(carImg, (x,y))

class GrayCodeState():
    """
    Class representing the sequence of gray code projections.
    This class supplies the bit planes that are rendered, and keeps track of the sequence of rendered bit planes.
    """
    def __init__(self, window_size):
        width = window_size[0]
        height = window_size[1]
        # Generate the gray code sequences to cover the largest possible coordinate.
        gray_code_arrays = generate_gray_code_sequence(max(width, height))

        # Convert the sequence to bit planes.
        self.bit_planes = generate_gray_code_bit_planes(gray_code_arrays)

        self.current_bit_plane = 0
        self.final_bit_plane = self.bit_planes.shape[0] - 1
        self.sequence_finished = False

    def progress_state(self):
        """
        Progress the current state to the next state.
        """
        self.current_bit_plane += 1
        if self.current_bit_plane > self.final_bit_plane:
            self.current_bit_plane = self.final_bit_plane
            self.sequence_finished = True

    def is_sequence_finished(self):
        return self.sequence_finished

    def get_current_bit_plane(self):
        """
        Gets the bit plane for the current state.
        """
        # TODO For now, just return the current bit plane number.
        bit_plane_index = len(self.bit_planes) - self.current_bit_plane - 1
        #print("Getting bit plane for index:", bit_plane_index)
        return self.bit_planes[bit_plane_index]
        # return self.bit_planes[self.current_bit_plane]

    def get_num_bit_planes(self):
        return len(self.bit_planes)

GRAYCODEEVENT = pygame.USEREVENT + 1

class GrayCodeController():
    def __init__(self, display_width, display_height):
        self.display_width = display_width
        self.display_height = display_height
        self.reset()

    def reset(self):
        self.render = True
        self.state = "BLACK"
        self.gray_code_state = GrayCodeState(
            (self.display_width, self.display_height))

    def process(self):
        """Called every timer tick."""
        if self.state == "BLACK":
            if self.render:
                print("Rendering black.")
                self.render = False
            else:
                print("Capturing black.")
                self.state = "WHITE"
                self.render = True
        elif self.state == "WHITE":
            if self.render:
                print("Rendering white.")
                self.render = False
            else:
                print("Capturing white.")
                self.state = "GRAYCODE"
                self.render = True
        elif self.state == "GRAYCODE":
            if self.render:
                print("Rendering gray code.")
                self.render = False
            else:
                print("Capturing gray code.")
                self.render = True
                if True:
                    print("Finished sequence.")
                    return False
        else:
            assert(False)

        return True

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

    gray_code_controller = GrayCodeController(display_width, display_height)

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
                if event.key == pygame.K_g:
                    if gray_code == False:
                        print("Starting gray code.")
                        pygame.time.set_timer(GRAYCODEEVENT, 1000)
                        gray_code = True
                    else:
                        print("Stopping gray code.")
                        pygame.time.set_timer(GRAYCODEEVENT, 0)
                        gray_code_controller.reset()
                        gray_code = False
            if event.type == GRAYCODEEVENT:
                print("Rendering / capturing gray code frame.")
                keep_processing = gray_code_controller.process()
                if not keep_processing:
                    pygame.time.set_timer(GRAYCODEEVENT, 0)
                    gray_code_controller.reset()
                    gray_code = False
            print(event)
        x += x_change

        gameDisplay.fill(white)
        car(x, y, gameDisplay, carImg)

        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    main()