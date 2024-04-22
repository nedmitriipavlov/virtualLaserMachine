import cv2
import numpy as np


def image_processing(filename):
    initial_img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

    if initial_img.shape[0] > 60 or initial_img.shape[1] > 60:
        initial_img = cv2.resize(initial_img, (60, 60), interpolation=cv2.INTER_CUBIC)

    thresh_img = cv2.adaptiveThreshold(initial_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 111, 2)

    contours, hiearchy = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    img_contours = np.zeros((initial_img.shape[0], initial_img.shape[1], 3), np.uint8)

    for x in range(len(contours)):
        cv2.drawContours(img_contours, contours, x, (255, 255, 255), 1)

    return img_contours


def get_img_matrix(img):
    img_matrix = [[0 for x in range(img.shape[1])] for i in range(img.shape[0])]
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            if np.all(np.equal(img[y][x], np.array([255, 255, 255], dtype=np.uint8))):
                img_matrix[y][x] = 1
    return_matrix = [[x for x in line] for line in img_matrix[::-1]]
    return return_matrix


# with open('h.txt', 'rw') as file:
#     for x in range(img.shape[0]):
#         for y in range(img.shape[1]):
#             if np.all(np.equal(img[y][x], np.array([255, 255, 255], dtype=np.uint8))):
#                 print(1, file=file, end=' ')
#             else:
#                 print(' ', end='')
#         print('\n', file=file)
