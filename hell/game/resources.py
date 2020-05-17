from pyglet import resource, font
from pyglet.image import SolidColorImagePattern

# Make our resource imports relative to the hell/resources/ directory.
resource.path = ['resources']
resource.reindex()


def _set_anchor_center(img):
    """Centers the anchor point of img."""
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

resource.add_font('m5x7.ttf')
font_m5x7 = font.load('m5x7')  # Only assigned so it doesn't get garbage collected immediately
