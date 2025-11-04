import cv2
import mediapipe as mp
from pynput.keyboard import Controller, Key
from handTrackingModule import handDetector
import cvzone
import time

class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text
        self.clicked = False
        self.lastClickTime = 0

def drawAll(img, buttonList, hoveredButton=None):
    overlay = img.copy()
    alpha_default = 0.6  # Độ trong suốt mặc định (các phím thông thường)
    alpha_hover = 1.0    # Độ trong suốt khi hover (hoàn toàn không mờ)

    for button in buttonList:
        x, y = button.pos
        w, h = button.size

        # Kiểm tra trạng thái nút
        # if button.text == "SHIFT" and isUppercase:
        #     color = (0, 255, 0)  # Màu xanh lá nếu SHIFT đang bật
        #     alpha = alpha_hover
        if button.text == "CAPS" and isUppercase:
            color = (0, 255, 0)  # Màu xanh lá khi chế độ CAPS LOCK đang bật
            alpha = alpha_hover
        elif button == hoveredButton:
            color = (0, 255, 0)  # Màu xanh lá nếu đang hover
            alpha = alpha_hover
        else:
            color = (255, 255, 255)  # Màu trắng mặc định
            alpha = alpha_default

        # Tạo lớp nút trên overlay
        button_overlay = overlay.copy()
        cvzone.cornerRect(button_overlay, (x, y, w, h), 20, rt=0)
        cv2.rectangle(button_overlay, button.pos, (x + w, y + h), color, cv2.FILLED)

        # Tùy chỉnh font scale và căn giữa chữ
        font_scale = 4
        text_size = cv2.getTextSize(button.text, cv2.FONT_HERSHEY_PLAIN, font_scale, 4)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2

        # Vẽ chữ lên lớp nút
        cv2.putText(button_overlay, button.text, (text_x, text_y),
                    cv2.FONT_HERSHEY_PLAIN, font_scale, (0, 0, 0), 4)  # Chữ màu đen

        # Kết hợp lớp nút với overlay chính bằng alpha
        cv2.addWeighted(button_overlay, alpha, overlay, 1 - alpha, 0, overlay)

    # Kết hợp overlay với ảnh gốc
    cv2.addWeighted(overlay, 1, img, 0, 0, img)
    return img

isUppercase = False  # Mặc định là chữ thường

# Danh sách phím cho 2 chế độ
lowercase_keys = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
    ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
    ["z", "x", "c", "v", "b", "n", "m", "", "DEL"],
    ["", "", "", "CAPS", "", "SPACE", "", "", "CLR"]
]

uppercase_keys = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["Z", "X", "C", "V", "B", "N", "M", "", "DEL"],
    ["", "", "", "CAPS", "", "SPACE", "", "", "CLR"]
]

# Hàm tạo lại danh sách nút
def createButtons(keys):
    buttonList = []
    buttonSpacing = 125
    for i in range(len(keys)):
        for j, key in enumerate(keys[i]):
            if key == "":
                continue
            width = 60
            if key == "SPACE":
                width = 300
            elif key == "DEL" or key == "CLR" or key == "CAPS":
                width = 175
            buttonList.append(Button([buttonSpacing * j + 50, 100 * i + 50], key, size=[width, 85]))
    return buttonList

# Tạo danh sách nút ban đầu (chữ thường)
buttonList = createButtons(lowercase_keys)

def main():
    global isUppercase, buttonList
    caretVisible = True
    caretLastToggle = time.time()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    cv2.namedWindow("Virtual Keyboard", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Virtual Keyboard", 1920, 1080)

    detector = handDetector(detectionCon=0.8)
    keyboard = Controller()

    finalText = ""
    noClickMode = False  # Biến trạng thái No Click Mode

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        img = detector.findHands(img, draw=True)  # Bật chế độ vẽ xương tay
        lmList, bbox = detector.findPosition(img, draw=False)  # Lấy danh sách các điểm mốc

        hoveredButton = None

        if len(lmList) > 0:
            fingers = detector.fingersUp()

            # Kiểm tra trạng thái No Click Mode
            if all(fingers):  # Tất cả 5 ngón tay giơ lên
                noClickMode = True
                cv2.putText(img, "NO CLICK MODE", (50, 500),
                            cv2.FONT_HERSHEY_PLAIN, 1.8, (0, 0, 255), 4)
            else:
                noClickMode = False

            if not noClickMode:
                x1, y1 = lmList[8][1], lmList[8][2]

                # Kiểm tra nút đang được hover
                for button in buttonList:
                    bx, by = button.pos
                    bw, bh = button.size

                    if bx < x1 < bx + bw and by < y1 < by + bh:
                        hoveredButton = button
                        break

                # Kiểm tra click
                if hoveredButton:
                    l, _, _ = detector.findDistance(8, 12, img, draw=False)
                    if l < 25 and not hoveredButton.clicked and time.time() - hoveredButton.lastClickTime > 1.5:  # Giới hạn thời gian nhấn
                        if hoveredButton.text == "CAPS":
                            # Chuyển đổi chế độ
                            isUppercase = not isUppercase
                            buttonList = createButtons(uppercase_keys if isUppercase else lowercase_keys)
                        elif hoveredButton.text == "DEL":  # Xử lý nút backspace
                            if len(finalText) > 0:
                                finalText = finalText[:-1]
                                keyboard.press(Key.backspace)
                                keyboard.release(Key.backspace)
                        elif hoveredButton.text == "SPACE":  # Xử lý nút Space
                            finalText += " "
                            keyboard.press(Key.space)
                            keyboard.release(Key.space)
                        elif hoveredButton.text == "CLR":  # Xử lý nút CLEAR
                            finalText = ""
                            keyboard.press(Key.ctrl)
                            keyboard.press('a')
                            keyboard.release('a')
                            keyboard.release(Key.ctrl)
                            keyboard.press(Key.delete)
                            keyboard.release(Key.delete)
                        else:
                            finalText += hoveredButton.text
                            keyboard.press(hoveredButton.text)
                            keyboard.release(hoveredButton.text)

                        hoveredButton.clicked = True
                        hoveredButton.lastClickTime = time.time()  # Cập nhật thời gian click

                # Reset trạng thái clicked nếu tay rời khỏi nút
                if hoveredButton and hoveredButton.clicked:
                    l, _, _ = detector.findDistance(8, 12, img, draw=False)
                    if l > 25:
                        hoveredButton.clicked = False

        else: 
            if len(lmList) == 0:  # Không phát hiện tay
                cv2.putText(img, "NO HAND DETECTED", (50, 500),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 4)
            
        # Vẽ các nút với hiệu ứng hover
        img = drawAll(img, buttonList, hoveredButton)

        # Hiển thị text
        cv2.rectangle(img, (50, 600), (1200, 700), (255, 255, 255), cv2.FILLED)
        
        displayText = finalText + ("|" if caretVisible else "")
        cv2.putText(img, displayText, (60, 680),
                    cv2.FONT_HERSHEY_PLAIN, 5, (0, 0, 0), 5)

        # Hiển thị hình ảnh
        cv2.imshow("Virtual Keyboard", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
