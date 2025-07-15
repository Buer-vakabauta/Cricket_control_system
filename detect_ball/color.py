import cv2
import numpy as np
from camera import CameraCapture

Camera = CameraCapture(width=640, height=640, fps=90)
Camera.start()

drawing = False
ix, iy = -1, -1
rect = None
image = None

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, rect, image

    if image is None:
        return

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        img_copy = image.copy()
        cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
        cv2.imshow("Select", img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rect = (min(ix, x), min(iy, y), abs(x - ix), abs(y - iy))
        process_roi()

def process_roi():
    x, y, w, h = rect
    roi = image[y:y + h, x:x + w]

    if roi.size == 0:
        print("⚠ 区域为空，请重新框选")
        return

    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    b_min, g_min, r_min = np.min(roi.reshape(-1, 3), axis=0)
    b_max, g_max, r_max = np.max(roi.reshape(-1, 3), axis=0)
    #print("▶ RGB范围：")
    #print(f"Min: [{r_min}, {g_min}, {b_min}]")
    #print(f"Max: [{r_max}, {g_max}, {b_max}]")

    h_min, s_min, v_min = np.min(hsv_roi.reshape(-1, 3), axis=0)
    h_max, s_max, v_max = np.max(hsv_roi.reshape(-1, 3), axis=0)
    print("▶ HSV范围：")
    print(f"Min: [{h_min}, {s_min}, {v_min}]")
    print(f"Max: [{h_max}, {s_max}, {v_max}]")

    cv2.imshow("Selected ROI", roi)

# === 主函数 ===
if __name__ == "__main__":
    cv2.namedWindow("Select")
    cv2.setMouseCallback("Select", draw_rectangle)

    print("✅ 鼠标框选区域查看 RGB / HSV 范围，按 ESC 退出")

    while True:
        frame = Camera.get_frame()
        image = frame.copy()  # 同步给回调处理

        if image is None:
            continue

        cv2.imshow("Select", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC退出
            print("🛑 已退出")
            break

    cv2.destroyAllWindows()
