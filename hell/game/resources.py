from pyglet import resource, font
from pyglet.image import SolidColorImagePattern

from . import WIDTH, HEIGHT

resource.path = ['resources']
resource.reindex()


def _set_anchor_center(img):
    img.anchor_x = int(img.width / 2)
    img.anchor_y = int(img.height / 2)


player_image = SolidColorImagePattern((255, 255, 255, 255)).create_image(32, 32)
_set_anchor_center(player_image)

enemy_pawn_image = resource.image('enemy/pawn.png')
_set_anchor_center(enemy_pawn_image)

enemy_slider_image = resource.image('enemy/slider.png')
_set_anchor_center(enemy_slider_image)

pellet_image = resource.image('pellet.png')
_set_anchor_center(pellet_image)

overlay_image = SolidColorImagePattern((255, 255, 255, 255)).create_image(WIDTH, HEIGHT)

resource.add_font('m5x7.ttf')
font_m5x7 = font.load('m5x7')
