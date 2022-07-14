from pdf2image import convert_from_path
import cv2
from imutils import contours
import pandas as pd
import numpy as np


def pdf_to_imgs_converter(file_path, path_on_server):
    images = convert_from_path(file_path)

    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save(f'{path_on_server}/page{str(i)}.jpg', 'JPEG')
        yield i


def find_big_text_areas(img_path, path_to):
    image = cv2.imread(img_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # grayscale
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)  # threshold

    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    dilated = cv2.dilate(thresh, kernel, iterations=13)  # dilate
    contours, hierarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # get contours

    # for each contour found, draw a rectangle around it on original image
    ROI_number = 0
    for contour in contours:
        # get rectangle bounding contour
        [x, y, w, h] = cv2.boundingRect(contour)

        # discard areas that are too small
        if h < 60 or w < 60:
            continue
        ROI = 255 - image[y:y + h, x:x + w]
        cv2.imwrite(f'{path_to}/ROI_{ROI_number}.png', ROI)
        yield [x,y,w,h],f'{path_to}/ROI_{ROI_number}.png'

        # draw rectangle around contour on original image
        # cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 2)
        ROI_number += 1


def find_letters(img_path):
    image = cv2.imread(img_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)[1]

    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    cnts, _ = contours.sort_contours(cnts, method="top-to-bottom")

    coords_lst = []

    for c in cnts:
        area = cv2.contourArea(c)
        if area > 10:
            x, y, w, h = cv2.boundingRect(c)
            coords_lst.append(
                dict(
                    x=x,
                    y=y,
                    w=w,
                    h=h,
                    y_med=y + h / 2,
                )
            )
    df = pd.DataFrame(coords_lst)
    return df


def get_diff_up_down_values(df_temp) -> tuple:
    diff = df_temp.y_end.max() - df_temp.y.min()
    y_med_mean = df_temp.y_med.mean()
    up_value = int(y_med_mean - diff / 2)
    down_value = np.floor(y_med_mean + diff / 2)
    return diff, up_value, down_value


def update_df_by_mask_and_get_new_mask(df, mask, up=True) -> tuple:
    diff, up_value, down_value = get_diff_up_down_values(df[mask])
    mask2 = df['y_med'].between(up_value, down_value)
    df.loc[mask2, 'row'] = up_value
    if up:
        new_mask = df.y_med.between(up_value - diff, down_value - diff)
    else:
        new_mask = df.y_med.between(up_value + diff, down_value + diff)
    return df, new_mask


def find_fragments(df):
    if df.shape[0] > 0:
        df['y_end'] = df['y'] + df['h']
        df['x_end'] = df['x'] + df['w']
        df['step'] = df.y_med // (df.h.median() + 1)
        df['row'] = np.nan

        get_first_row_val = df.groupby(['step']).w.sum().idxmax()

        mask1 = df['step'] == get_first_row_val
        while mask1.sum():
            df, mask1 = update_df_by_mask_and_get_new_mask(df, mask1)
            # break

        mask1 = df['step'] == get_first_row_val
        while mask1.sum():
            df, mask1 = update_df_by_mask_and_get_new_mask(df, mask1, up=False)

    df = df[df['row'].notna()]
    df = df.sort_values(['row', 'x'])
    df['row'] = df['row'].replace({r: i for i, r in enumerate(df['row'].unique())})
    df['last_x'] = df.groupby(['row']).x_end.shift(1)
    df['has_last_x'] = (df['x'] - df['last_x']) <= 15
    mask = df.has_last_x == False
    df["word_id"] = np.nan
    df.loc[mask, 'word_id'] = np.arange(df[mask].shape[0])
    df["word_id"] = df["word_id"].fillna(method="ffill")

    df_res = pd.DataFrame()
    grp_data = df.groupby(['row', 'word_id'])
    df_res['x'] = grp_data.x.min()
    df_res['y'] = grp_data.y.min()
    df_res['x_end'] = grp_data.x_end.max()
    df_res['y_end'] = grp_data.y_end.max()

    return df_res


def plot_area(image, x, y, x_end, y_end):
    cv2.rectangle(image, (x, y), (x_end, y_end), (36, 255, 12), 1)


# we save img into server storage

def to_fragments(img_path, path_to_db, df_res):
    """
    :param img_path: path to image for fragmenting
    :param path_to_db: path for fragment to db write
    :param df_res: pandas df with coordinates for fragmenting
    :return:
    """
    image = cv2.imread(img_path)

    def save_fragment(fragment_data):
        path_fr = f'{path_to_db}/word_{int(fragment_data.name[1])}.png'
        img_fr = 255 - image[fragment_data.y:fragment_data.y_end, fragment_data.x:fragment_data.x_end]
        cv2.imwrite(filename=path_fr, img=img_fr)
        return (fragment_data.name[0], fragment_data.name[1],
                fragment_data.x, fragment_data.x_end, fragment_data.y, fragment_data.y_end,
                path_fr)

    # df_res.apply(lambda i: save_fragment(i), axis=1)
    for index, row in df_res.iterrows():
        yield save_fragment(row)
