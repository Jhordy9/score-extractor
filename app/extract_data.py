import cv2
from PIL import Image
import numpy as np
import easyocr
import requests


class ImageProcessor:
    def __init__(self, image_path):
        self.reader = easyocr.Reader(['pt', 'en'])
        image_content = requests.get(image_path)
        image_np = np.asarray(bytearray(image_content.content), dtype="uint8")
        self.image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

    def get_match_info(self):
        top_percentage = 7
        right_percentage = 32

        rows, cols = self.image.shape[:2]
        top_rows = int(rows * (top_percentage / 100))
        right_cols = int(cols * (right_percentage / 100))

        img_data = self.image[:top_rows, -right_cols:]

        img_data = cv2.cvtColor(img_data, cv2.COLOR_BGR2GRAY)
        _, img_data = cv2.threshold(
            img_data, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        zoomed_image = cv2.resize(
            img_data, None, fx=3, fy=3, interpolation=cv2.INTER_LINEAR)
        Image.fromarray(zoomed_image).save("tmp.jpg")

        results = self.reader.readtext("tmp.jpg", detail=0)

        return results

    def modify_image(self):
        modified_image = self.image.copy()  # create a new reference

        h, w = modified_image.shape[:2]
        slice_w = int(w * 0.2)

        left = modified_image[:, :w // 2 - slice_w // 2]
        right = modified_image[:, w // 2 + slice_w // 2:]
        modified_image = np.concatenate((left, right), axis=1)

        h, w = modified_image.shape[:2]
        border_percentage = 0.13
        border_width = int(w * border_percentage)
        modified_image = modified_image[:, border_width:w - border_width]

        h, w = modified_image.shape[:2]
        border_percentage = 0.2
        border_height = int(h * border_percentage)
        modified_image = modified_image[border_height:h - border_height, :]

        return modified_image

    def get_username(self):
        lower_yellow = (145, 120, 70)
        upper_yellow = (210, 180, 180)
        modified_image = self.modify_image()

        yellow_mask = cv2.inRange(modified_image, lower_yellow, upper_yellow)

        kernel_size = (1, 5)
        kernel = np.ones(kernel_size, np.uint8)

        yellow_mask = cv2.dilate(yellow_mask, kernel, iterations=2)
        yellow_mask = cv2.erode(yellow_mask, kernel, iterations=1)
        yellow_mask = cv2.blur(yellow_mask, kernel_size)

        contours, _ = cv2.findContours(
            yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        largest_contour = None
        largest_area = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h

            if area > largest_area and aspect_ratio > 2:
                largest_area = area
                largest_contour = contour

        if largest_contour is not None:
            x, y, w, h = cv2.boundingRect(largest_contour)
            yellow_region = modified_image[y:y + h, x: x + w]

            gray_image = cv2.cvtColor(yellow_region, cv2.COLOR_BGR2GRAY)
            _, gray_image = cv2.threshold(
                gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            Image.fromarray(gray_image).save("tmp.jpg")
            results = self.reader.readtext("tmp.jpg", detail=0)
            return results[0]
        return None
