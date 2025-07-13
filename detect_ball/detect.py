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
    # HSV色调H: 10~30为橙黄，S: 高饱和，V: 高亮\
    #乒乓球
    lower = np.array([10, 100, 100])     # H S V
    upper = np.array([30, 255, 255])
    #lower = (70, 33, 79)
    #upper = (102, 96, 116)
    # 创建掩码
    mask = cv2.inRange(hsv, lower, upper)
    # 去除小噪声
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    #cv2.imshow("ball_mask", mask)
    #cv2.waitKey(1) & 0xFF
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
    使用HSV检测绿色夹子位置，返回四个点：[top, right, bottom, left]
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # HSV绿色范围
    lower_hsv = np.array([50, 100, 40])
    upper_hsv = np.array([80, 255, 255])
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    
    # 增强闭操作处理连通区域
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centers = []
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:  # 面积阈值
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                centers.append((cx, cy))
    
    # 改进的去重逻辑：使用更严格的距离阈值
    dedup_centers = []
    min_distance = 30  # 增加最小距离阈值
    
    for c in centers:
        is_duplicate = False
        for dc in dedup_centers:
            distance = np.sqrt((c[0] - dc[0])**2 + (c[1] - dc[1])**2)
            if distance < min_distance:
                is_duplicate = True
                break
        
        if not is_duplicate:
            dedup_centers.append(c)
    
    # 如果检测到的点不是4个，返回None
    if len(dedup_centers) != 4:
        #print(f"检测到 {len(dedup_centers)} 个点，需要4个点")
        return None
    
    # 将点按照 [top, right, bottom, left] 的顺序排序
    points = np.array(dedup_centers)
    
    # 找到质心
    center_x = np.mean(points[:, 0])
    center_y = np.mean(points[:, 1])
    
    # 计算每个点相对于质心的角度
    angles = []
    for point in points:
        dx = point[0] - center_x
        dy = point[1] - center_y
        angle = np.arctan2(dy, dx)
        angles.append(angle)
    
    # 将角度和点组合，按角度排序
    points_with_angles = list(zip(angles, points))
    points_with_angles.sort(key=lambda x: x[0])
    
    # 提取排序后的点
    sorted_points = [point for angle, point in points_with_angles]
    
    # 根据角度确定top, right, bottom, left
    # 角度从-π到π，-π/2附近是top，0附近是right，π/2附近是bottom，π/-π附近是left
    
    # 找到最上面的点（y值最小）
    top_idx = np.argmin([p[1] for p in sorted_points])
    top = tuple(sorted_points[top_idx])
    
    # 找到最右边的点（x值最大）
    right_idx = np.argmax([p[0] for p in sorted_points])
    right = tuple(sorted_points[right_idx])
    
    # 找到最下面的点（y值最大）
    bottom_idx = np.argmax([p[1] for p in sorted_points])
    bottom = tuple(sorted_points[bottom_idx])
    
    # 找到最左边的点（x值最小）
    left_idx = np.argmin([p[0] for p in sorted_points])
    left = tuple(sorted_points[left_idx])
    
    result = [top, right, bottom, left]
    
    # 验证结果：确保四个点都不相同
    for i in range(4):
        for j in range(i + 1, 4):
            if result[i] == result[j]:
                print(f"警告：检测到重复点 {result[i]}")
                return None
    
    # 转换为numpy数组格式，供cv2.getPerspectiveTransform使用
    result_array = np.array(result, dtype=np.float32)
    
    return result_array



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