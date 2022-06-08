import cv2
import math
import numpy as np
import random
from .utils import *


# Function chuyen dap an tu number sang ki tu
def func_ans(ans):
    converter = {
        0: 'A',
        1: 'B',
        2: 'C',
        3: 'D',
        4: 'E'
    }
    return converter.get(ans, None)


def detect_image(img_name):
    img_path = "static/media/" + img_name
    img = cv2.imread(img_path)
    cv2.imwrite(img_name, img)
    # 1. Doc anh, chuyen thanh anh xam
    image = cv2.imread(img_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 2. Nhi phan hoa anh voi nguong 255
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 3)

    # 3. Tim khung ben ngoai de tach van ban khoi nen
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda x: cv2.contourArea(x),
                      reverse=True)  # Sap xep dien tich contours tu lon den be
    approx = cv2.approxPolyDP(contours[1], 0.01 * cv2.arcLength(contours[1], True), True)
    rect = cv2.minAreaRect(contours[1])
    box = cv2.boxPoints(rect)
    rectCon = []
    for i in contours:
        area = cv2.contourArea(i)
        if area > 1000:
            rectCon.append(i)
    cv2.drawContours(image, rectCon, -1, (0, 255, 0), 2)

    # 4. Thuc hien transform de xoay van ban
    corner = find_corner_by_rotated_rect(box, approx)
    image = four_point_transform(image, corner)
    wrap = four_point_transform(thresh, corner)

    # 5. Tim cac o tick trong hinh
    contours, _ = cv2.findContours(wrap, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    tickcontours = []

    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        if w >= 30 and h >= 30 and 0.8 <= ar <= 1.2:
            tickcontours.append(c)
    cv2.drawContours(image, tickcontours, -1, (0, 255, 0), 2)

    # 6. So sanh cac o tick voi dap an

    # Dinh nghia dap an
    right_answer = {0: 1, 1: 4, 2: 0, 3: 3, 4: 1, 5: 1, 6: 4, 7: 0, 8: 3, 9: 1}

    # Sap xep cac contour theo hang
    tickcontours = sort_contours(tickcontours, method="top-to-bottom")[0]

    correct = 0
    ur_ans = []

    for (q, i) in enumerate(np.arange(0, len(tickcontours), 5)):

        # Dinh nghia mau rieng cho tung cau hoi
        color = (0, 255, 255)
        # Sap xep cac contour theo cot
        cnts = sort_contours(tickcontours[i:i + 5])[0]
        cv2.drawContours(image, cnts, -1, color, 3)

        choice = (0, 0)
        total = 0
        count = 0
        chuan = 0
        for (j, c) in enumerate(cnts):
            # Tao mask de xem muc do to mau cua contour
            mask = np.zeros(wrap.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)
            mask = cv2.bitwise_and(wrap, wrap, mask=mask)
            total = cv2.countNonZero(mask)
            print(total)
            if chuan < total:
                chuan = total
        # Duyet qua cac contour trong hang
        print("---", chuan, "----")
        for (j, c) in enumerate(cnts):
            # Tao mask de xem muc do to mau cua contour
            mask = np.zeros(wrap.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)
            mask = cv2.bitwise_and(wrap, wrap, mask=mask)
            total = cv2.countNonZero(mask)

            # Lap de chon contour to mau dam nhat
            # print(total)
            if total > chuan - 60:
                choice = (total, j)
                count += 1

        # Lay dap an cua cau hien tai
        current_right = right_answer[q]
        # print("-----")
        ######Chuyen lua chon cua nguoi dung tu number sang char
        if count == 0 or count > 1:
            ur_ans.append('')
        else:
            ans = func_ans(choice[1])
            ur_ans.append(ans)
            # Kiem tra voi lua chon cua nguoi dung
            if current_right == choice[1]:
                # Neu dung Thi to mau xanh
                color = (0, 255, 0)
                correct += 1
            else:
                # Neu sai Thi to mau do
                color = (0, 0, 255)
            # Ve ket qua len anh
            cv2.drawContours(image, [cnts[current_right]], -1, color, 3)

    # In ra man hinh
    print('So cau hoi:' + str(len(right_answer)))
    print('so cau tra loi dung: ' + str(correct))
    diem = (correct / len(right_answer)) * 10
    print('Diem:' + str(diem))
    dapAn = []
    for i in right_answer:
        ans = func_ans(right_answer[i])
        dapAn.append(ans)

    print('Dap an:')
    dem = 0
    for i in range(len(dapAn)):
        if i == len(dapAn) - 1:
            print(i + 1, ':', str(dapAn[i]))
        else:
            print(i + 1, ':', str(dapAn[i]), end="\t")

    print('Cau tra loi cua ban:')
    for i in range(len(ur_ans)):
        if i == len(ur_ans) - 1:
            print(i + 1, ':', str(ur_ans[i]))
        else:
            print(i + 1, ':', str(ur_ans[i]), end="\t")
    return diem
