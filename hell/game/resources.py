from pyglet.image import SolidColorImagePattern

player_image = SolidColorImagePattern((255, 255, 255, 255)).create_image(32, 32)
player_image.anchor_x = 16
player_image.anchor_y = 16

enemy_image = SolidColorImagePattern((0, 255, 255, 255)).create_image(32, 32)
enemy_image.anchor_x = 16
enemy_image.anchor_y = 16

key_timer_image = SolidColorImagePattern((255, 255, 255, 150)).create_image(16, 16)