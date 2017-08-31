import pygame
import cv2
from PIL import Image
import os
import numpy as np
from gray_code import generate_gray_code_sequence, generate_gray_code_bit_planes, \
    generate_warp_map, combine_warp_maps, find_homographies, \
    allocate_warp_map_pts_to_planes

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY_CODE_DIR = "gray_code_projector_500x500_corner"
GRAY_CODE_DELAY = 500
GRAY_CODE_FILENAME_HORIZ = r"graycode*horiz.png"
GRAY_CODE_FILENAME_VERT = r"graycode*vert.png"
PROJ_DIM = (800, 600)
CAM_DIM = (640, 480)

class Camera():
    def __init__(self, grayscale=True):
        camera_number = 2
        self.capture = cv2.VideoCapture(camera_number)
        self.grayscale = grayscale

    def capture_frame(self):
        frame, width, height = self.capture_frame_opencv()
        im = Image.frombytes("RGB", (640, 480), frame)
        if self.grayscale:
            im = im.convert('L')
        return im

    def capture_frame_opencv(self):
        for i in range(5):
            ret, frame = self.capture.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width = frame.shape[:2]
        print(width, height)
        return frame, width, height

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

def render_home_screen(gameDisplay):

    gameDisplay.fill(BLACK)

    font = pygame.font.SysFont("monospace", 15)
    label = font.render("G - Render/capture gray code patterns", 1, (255, 255, 0))
    gameDisplay.blit(label, (100, 100))
    label = font.render("W - Generate warp map from gray code", 1, (255, 255, 0))
    gameDisplay.blit(label, (100, 120))
    label = font.render("E - Render edges", 1, (255, 255, 0))
    gameDisplay.blit(label, (100, 140))
    label = font.render("P - Render planes", 1, (255, 255, 0))
    gameDisplay.blit(label, (100, 160))


def render_edges(gameDisplay, warp_map_im_horiz, warp_map_im_vert,
                 proj_cam_warp_map, cam_proj_warp_map):
    if 1:
        img_data = np.array(warp_map_im_horiz)
        # Find the edge pixels. This returns a [height, width] array.
        # Note that the returned edge pixels may lie just outside the projection.
        edges = cv2.Canny(img_data, 100, 200, 13)
        im = Image.fromarray(edges, "L").convert("RGB")
    else:
        im = warp_map_im_horiz

    if 0:
        # Simply display the camera image.
        mode = im.mode
        size = im.size
        data = im.tobytes()
        im_surface = pygame.image.fromstring(data, size, mode)
        gameDisplay.blit(im_surface, (0, 0))
    elif 1:
        # Render one of the images, but from the PoV of the projector.
        gameDisplay.fill(BLACK)
        for y in range(PROJ_DIM[1]):
            for x in range(PROJ_DIM[0]):
                proj_pos = (x, y)
                if proj_pos not in proj_cam_warp_map.keys():
                    continue
                cam_pos = proj_cam_warp_map[proj_pos]
                im_pixel = im.getpixel(cam_pos)
                pygame.draw.circle(gameDisplay, im_pixel, proj_pos, 1, 0)
    elif 0:
        # Render the projector pixels that correspond to edges.
        gameDisplay.fill(BLACK)
        for y in range(PROJ_DIM[1]):
            for x in range(PROJ_DIM[0]):
                proj_pos = (x, y)
                if proj_pos not in proj_cam_warp_map.keys():
                    continue
                cam_pos = proj_cam_warp_map[proj_pos]
                edge_pixel = im.getpixel(cam_pos)
                if edge_pixel == (255, 255, 255):
                    pygame.draw.circle(gameDisplay, (255, 0, 0), proj_pos,
                                       10, 0)
    elif 1:
        # Render the projector pixels that correspond to edges, but map the
        # other way, from edge pixels to projector pixels.
        # I think the two methods have the exact same result.
        gameDisplay.fill(BLACK)
        for y in range(CAM_DIM[1]):
            for x in range(CAM_DIM[0]):
                cam_pos = (x, y)
                edge_pixel = im.getpixel(cam_pos)
                if edge_pixel != (255, 255, 255):
                    continue
                if cam_pos not in cam_proj_warp_map.keys():
                    continue
                proj_pos = cam_proj_warp_map[cam_pos]
                pygame.draw.circle(gameDisplay, (255, 0, 0), proj_pos, 10, 0)


def render_planes(gameDisplay, cam_proj_warp_map, proj_cam_warp_map):
    """
    Determines the planes in an image, and renders the warp maps according to the
    planes.
    """
    homogs, plane_quads = find_homographies(
        cam_proj_warp_map, proj_cam_warp_map, CAM_DIM, PROJ_DIM)

    cam_planes_dict, proj_planes_dict, cam_plane_img = \
        allocate_warp_map_pts_to_planes(cam_proj_warp_map, homogs, CAM_DIM)

    # Render the projector pixels according to the plane they are assigned to.
    gameDisplay.fill(BLACK)
    proj_pts = list(proj_planes_dict.keys())
    for proj_pt in proj_pts:
        plane = proj_planes_dict[proj_pt]
        if plane is None:
            continue
            
        if plane == 0:
            colour = (255, 0, 0)
        elif plane == 1:
            colour = (0, 255, 0)
        else:
            colour = (0, 0, 255)
        pygame.draw.circle(gameDisplay, colour, proj_pt, 2, 0)


def create_warp_map_from_dir():
    warp_map_horiz, warp_map_vert, im_horiz, im_vert = generate_warp_map(
        GRAY_CODE_DIR, GRAY_CODE_FILENAME_HORIZ, GRAY_CODE_FILENAME_VERT, CAM_DIM,
        PROJ_DIM)

    if im_horiz is not None:
        im_horiz.save(os.path.join(GRAY_CODE_DIR, "warp_map_horiz.png"))
        # plt.figure()
        # plt.imshow(np.asarray(im_horiz))
    if im_vert is not None:
        im_vert.save(os.path.join(GRAY_CODE_DIR, "warp_map_vert.png"))
        # plt.figure()
        # plt.imshow(np.asarray(im_vert))

    return warp_map_horiz, warp_map_vert, im_horiz, im_vert


class GrayCodeController():
    def __init__(self, display_width, display_height, gameDisplay, camera):
        self.display_width = display_width
        self.display_height = display_height
        self.gameDisplay = gameDisplay
        self.camera = camera
        self.reset()

    def reset(self):
        self.render = True
        self.state = "BLACK"
        self.horizontal = True
        self.gray_code_num = 0
        self.gray_code_state = GrayCodeState(
            (self.display_width, self.display_height))

    def process(self):
        """Called every timer tick."""
        if self.state == "BLACK":
            if self.render:
                print("Rendering black.")
                self.gameDisplay.fill((0, 0, 0))
                self.render = False
            else:
                print("Capturing black.")
                im = self.camera.capture_frame()
                im.save(os.path.join(GRAY_CODE_DIR, "black.png"))
                self.state = "WHITE"
                self.render = True
        elif self.state == "WHITE":
            if self.render:
                print("Rendering white.")
                self.gameDisplay.fill((255, 255, 255))
                self.render = False
            else:
                print("Capturing white.")
                im = self.camera.capture_frame()
                im.save(os.path.join(GRAY_CODE_DIR, "white.png"))
                self.state = "GRAYCODE"
                self.render = True
        elif self.state == "GRAYCODE":
            if self.render:
                print("Rendering gray code.")
                # self.gameDisplay.fill((128, 128, 128))
                self.gameDisplay.fill((0, 0, 0))
                bit_plane = self.gray_code_state.get_current_bit_plane()
                for x, bit_val in enumerate(bit_plane):
                    if bit_val == 1:
                        if self.horizontal:
                            pygame.draw.rect(self.gameDisplay, (255, 255, 255),
                                             (x, 0, 1, self.display_height), 1)
                        else:
                            pygame.draw.rect(self.gameDisplay, (255, 255, 255),
                                             (0, x, self.display_width, 1), 1)
                self.gray_code_state.progress_state()
                self.render = False
            else:
                print("Capturing gray code.")
                im = self.camera.capture_frame()
                horiz_label = "horiz" if self.horizontal else "vert"
                im.save(os.path.join(GRAY_CODE_DIR,
                                     "graycode_%02d_%s.png" % (self.gray_code_num, horiz_label)))
                self.render = True
                self.gray_code_num += 1
                if self.gray_code_state.is_sequence_finished():
                    if self.horizontal:
                        print("Finished horizontal sequence.")
                        self.horizontal = False
                        self.gray_code_state = GrayCodeState(
                            (self.display_width, self.display_height))
                    else:
                        print("Finished vertical sequence.")
                        return False
        else:
            assert(False)

        return True


class App():
    def __init__(self):
        self.warp_map_horiz = None
        self.warp_map_vert = None

    def main(self):
        pygame.init()

        camera = Camera()
        # im = camera.capture_frame()
        # im.save("pygame_camera_im.png")

        gameDisplay = pygame.display.set_mode(PROJ_DIM)
        pygame.display.set_caption('Projection mapping')

        clock = pygame.time.Clock()

        # carImg = pygame.image.load('racecar.png')
        # x = (display_width * 0.45)
        # y = (display_height * 0.8)
        # x_change = 0
        # car_speed = 0

        gray_code_controller = GrayCodeController(
            PROJ_DIM[0], PROJ_DIM[1], gameDisplay, camera)

        crashed = False
        gray_code = False
        edges = False
        planes = False
        while not crashed:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    crashed = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_g:
                        if gray_code == False:
                            print("Starting gray code.")
                            pygame.time.set_timer(GRAYCODEEVENT, GRAY_CODE_DELAY)
                            gray_code = True
                        else:
                            print("Stopping gray code.")
                            pygame.time.set_timer(GRAYCODEEVENT, 0)
                            gray_code_controller.reset()
                            gray_code = False
                    elif event.key == pygame.K_w:
                        print("Generating warp map from gray code.")
                        self.warp_map_horiz, self.warp_map_vert, self.im_horiz, \
                            self.im_vert = create_warp_map_from_dir()
                        self.cam_proj_warp_map, self.proj_cam_warp_map = \
                            combine_warp_maps(self.warp_map_horiz, self.warp_map_vert)
                    elif event.key == pygame.K_e:
                        if edges == False:
                            print("Rendering edges.")
                            render_edges(gameDisplay, self.im_horiz, self.im_vert,
                                         self.proj_cam_warp_map,
                                         self.cam_proj_warp_map)
                            edges = True
                        else:
                            print("Stopping rendering edges.")
                            edges = False
                    elif event.key == pygame.K_p:
                        if planes == False:
                            print("Rendering planes.")
                            render_planes(gameDisplay, self.cam_proj_warp_map,
                                          self.proj_cam_warp_map)
                            planes = True
                        else:
                            print("Stopping rendering planes.")
                            planes = False
                if event.type == GRAYCODEEVENT:
                    print("Rendering / capturing gray code frame.")
                    keep_processing = gray_code_controller.process()
                    if not keep_processing:
                        pygame.time.set_timer(GRAYCODEEVENT, 0)
                        gray_code_controller.reset()
                        gray_code = False
                print(event)

            if not gray_code and not edges and not planes:
                render_home_screen(gameDisplay)

            pygame.display.update()
            clock.tick(60)

if __name__ == '__main__':
    app = App()
    app.main()