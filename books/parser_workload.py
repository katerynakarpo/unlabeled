import os
import shutil
from werkzeug.utils import secure_filename
from pathlib import Path
from books.models import book_upload, page_upload, fragment_upload, roi_upload
from books.parser_methods import pdf_to_imgs_converter, find_big_text_areas, find_letters, find_fragments, to_fragments


def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1
    while os.path.exists(path):
        path = f'{filename}({str(counter)}){extension}'
        counter += 1
    return path


STORAGE_PATH = './storage'
BOOKS_PATH = f'{STORAGE_PATH}/books'
IMG_PATH = f'{STORAGE_PATH}/imgs'
TEMP_PATH = f'{STORAGE_PATH}/temp'
FRAGMENTS_PATH = f'{STORAGE_PATH}/fragments'


#  rewrite it - process on another server send

def upload_book_gen(file):
    file_data = file.stream.read()
    os.makedirs(BOOKS_PATH, exist_ok=True)
    book_name = secure_filename(file.filename)
    file_path = uniquify(f'{BOOKS_PATH}/{book_name}')
    book_id = book_upload(book_name, file_path)
    with open(file_path, 'wb') as f:
        f.write(file_data)
    imgs_path = Path(f'{IMG_PATH}/{book_id}/')
    if imgs_path.exists() and imgs_path.is_dir():
        shutil.rmtree(imgs_path)
    os.makedirs(imgs_path, exist_ok=True)
    for page_number in pdf_to_imgs_converter(file_path, imgs_path):
        page_id = page_upload(book_id, page_number, f'{file_path}/page{str(page_number)}.jpg')
    for img_name in os.listdir(imgs_path):
        img_path = f'{imgs_path}/{img_name}'
        temp_img_path = f"{TEMP_PATH}/{book_id}/{img_name.split('.', 1)[0]}"
        os.makedirs(temp_img_path, exist_ok=True)
        for coords,temp_img_path in find_big_text_areas(img_path, temp_img_path):
            roi_id = roi_upload(page_id, coords[0], coords[1], coords[2], coords[3])
            df = find_letters(temp_img_path)
            df = find_fragments(df)
            fragments_path = f"{FRAGMENTS_PATH}/{book_id}/{img_name.split('.', 1)[0]}/{temp_img_path.split('/')[-1].split('.', 1)[0]}"
            os.makedirs(fragments_path, exist_ok=True)
            for (row_number, word_number, coordinate_x, coordinate_x_end,
                 coordinate_y, coordinate_y_end, file_location
                 ) in to_fragments(temp_img_path, fragments_path, df):
                fragment_upload(roi_id ,int(row_number), int(word_number), int(coordinate_x),
                                int(coordinate_x_end),int(coordinate_y), int(coordinate_y_end),
                                file_location)

        shutil.rmtree(f'{TEMP_PATH}/{book_id}')

    return f'file uploaded successfully: {book_name}'

# TODO: try to rewrite it. How it should work: book uploaded post request answer -> data post-processing