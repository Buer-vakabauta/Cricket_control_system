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



def detect_clips(frame):
    """
    检测黑色夹子中点位置（基于RGB阈值），返回顺序：[top, right, bottom, left]
    """
    # 构建黑色掩膜
    lower_black = np.array([30, 30, 30])
    upper_black = np.array([90, 110, 90])
    mask = cv2.inRange(frame, lower_black, upper_black)

    # 开闭操作，消除小杂点
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 轮廓查找
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.imshow("mask_img",mask)
    cv2.waitKey(1) & 0xFF
    centers = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100:  # 可调，排除小干扰
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                centers.append((cx, cy))

    if len(centers) != 4:
        return None  # 检测失败

    # 排序：上、右、下、左（用于透视变换）
    # 先按Y排序（取上和下），再按X区分左右
    centers = sorted(centers, key=lambda p: p[1])  # 按y坐标从小到大
    top = min(centers[:2], key=lambda p: p[0])
    bottom = max(centers[2:], key=lambda p: p[0])
    right = max(centers, key=lambda p: p[0])
    left = min(centers, key=lambda p: p[0])



    return np.float32([top, right, bottom, left])


def normalize_ball_position(frame):
    """
    获取小球相对板子的归一化坐标及九宫格区域编号
    Returns:
        x_norm, y_norm: 归一化坐标 (0~1)
        region_id: 区域编号 (1~9)
    """
    ball_x, ball_y = detect_ball_pos(frame)
    if ball_x is None:
        return None, None, None

    clips = detect_clips(frame)
    if clips is None:
        return None, None, None

    # 设置目标映射点（300x300板面）
    pts_dst = np.float32([
        [150, 0],     # top
        [300, 150],   # right
        [150, 300],   # bottom
        [0, 150],     # left
    ])

    # 获取透视变换矩阵
    M = cv2.getPerspectiveTransform(clips, pts_dst)

    # 转换球心坐标
    ball_pt = np.array([[[ball_x, ball_y]]], dtype=np.float32)
    norm_pt = cv2.perspectiveTransform(ball_pt, M)
    x_n, y_n = norm_pt[0][0]

    # 归一化
    x_norm = x_n / 300
    y_norm = y_n / 300

    # 判断区域编号（1~9）
    col = int(x_n // 100)
    row = int(y_n // 100)
    if 0 <= row <= 2 and 0 <= col <= 2:
        region_id = row * 3 + col + 1
    else:
        region_id = None

    return x_norm, y_norm, region_id