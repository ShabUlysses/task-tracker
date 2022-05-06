import secrets
import os
from main import app
from flask_login import current_user
from PIL import Image


def save_picture(form_picture):
    '''This function saves the picture in static directory, generates random filename and
    returns filename as function output.'''
    random_hex = secrets.token_hex(8) # Create a random name for saved picture
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    prev_picture = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
    if os.path.exists(prev_picture) and os.path.basename(prev_picture) != 'default.jpg':
        os.remove(prev_picture)
    return picture_fn
