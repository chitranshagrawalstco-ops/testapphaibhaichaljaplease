import os
from werkzeug.utils import secure_filename
from flask import current_app
import uuid

def save_image(file):
    if not file:
        return None
        
    filename = secure_filename(file.filename)
    # Give it a unique name to avoid collisions
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)
    return unique_filename

def delete_image(filename):
    if not filename:
        return
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
