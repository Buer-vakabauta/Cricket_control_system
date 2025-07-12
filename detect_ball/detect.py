import cv2
import numpy as np

def detect_ball_pos(frame):
    """
    检测球的位置
    Args:
        frame: 视频帧(BGR格式)
    Returns:
        (x, y): 球心位置坐标，未检测到返回 (-1, -1)
    """
    no_result=(-1,-1)
    # 转换为HSV颜色空间
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 设定橙黄色HSV阈值范围（根据你提供的RGB粗略估算）
    # HSV色调H: 10~30为橙黄，S: 高饱和，V: 高亮
    lower = np.array([10, 100, 100])     # H S V
    upper = np.array([30, 255, 255])

    # 创建掩码
    mask = cv2.inRange(hsv, lower, upper)

    # 去除小噪声
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return no_result

    # 找到最大轮廓
    max_contour = max(contours, key=cv2.contourArea)

    # 轮廓面积筛选（防止误检）
    if cv2.contourArea(max_contour) < 100:
        return no_result

    # 拟合最小外接圆
    (x, y), radius = cv2.minEnclosingCircle(max_contour)

    if radius < 3:  # 半径太小认为是误检
        return no_result

    return (int(x), int(y))
