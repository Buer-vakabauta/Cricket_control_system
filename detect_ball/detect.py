import cv2
import numpy as np
from control import get_region_center
def detect_ball_pos(frame):
    """
    检测小球的位置（增强版）：允许高速模糊残影情况
    Returns:
        (x, y): 球心位置坐标，未检测到返回 (None, None)
    """
    no_result = (None, None)

    # 转HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    v_channel = hsv[:, :, 2]  # 提取亮度通道

    # 橙红色小球主颜色掩码
    lower_main = np.array([0, 40, 80])
    upper_main = np.array([15, 170, 175])
    mask_main = cv2.inRange(hsv, lower_main, upper_main)

    # 高亮残影（可能偏白、偏黄）额外掩码（高V值）
    lower_bright = np.array([0, 0, 80])
    upper_bright = np.array([180, 60, 175])
    mask_bright = cv2.inRange(hsv, lower_bright, upper_bright)

    # 合并两个掩码
    mask = cv2.bitwise_or(mask_main, mask_bright)

    # 形态学操作去噪
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
    area = cv2.contourArea(max_contour)

    if area < 50:
        return no_result

    # 拟合外接圆
    (x, y), radius = cv2.minEnclosingCircle(max_contour)
    circularity = 4 * np.pi * area / (cv2.arcLength(max_contour, True) ** 2 + 1e-6)

    # 圆度筛选防止误检（残影通常也比较圆）
    if radius < 3 or circularity < 0.3:
        return no_result

    return int(x), int(y)



def smart_select_four_points(candidates, min_distance=40):
    """
    从候选点中智能选择4个点，优先选择面积大且距离合适的点
    candidates: [(center, area, contour), ...]
    """
    if len(candidates) < 4:
        return None
    
    # 第一步：按面积排序，已经在调用前完成
    selected = []
    
    # 贪心算法选择4个点
    for candidate in candidates:
        center, area, contour = candidate
        
        # 检查与已选择的点的距离
        is_valid = True
        for selected_center in selected:
            distance = np.sqrt((center[0] - selected_center[0])**2 + 
                             (center[1] - selected_center[1])**2)
            if distance < min_distance:
                is_valid = False
                break
        
        if is_valid:
            selected.append(center)
            
        # 如果已经选择了4个点，跳出循环
        if len(selected) == 4:
            break
    
    # 如果选择的点少于4个，尝试降低距离阈值
    if len(selected) < 4:
        return smart_select_four_points(candidates, min_distance * 0.8)
    
    # 进一步优化：确保选择的4个点能形成一个合理的四边形
    if len(selected) == 4:
        # 检查4个点是否能形成凸四边形
        if is_valid_quadrilateral(selected):
            return selected
        else:
            # 如果不是有效四边形，尝试其他组合
            return try_other_combinations(candidates, min_distance)
    
    return selected if len(selected) == 4 else None

def is_valid_quadrilateral(points):
    """
    检查4个点是否能形成一个合理的四边形
    """
    if len(points) != 4:
        return False
    
    # 计算质心
    center_x = np.mean([p[0] for p in points])
    center_y = np.mean([p[1] for p in points])
    
    # 计算每个点到质心的距离
    distances = []
    for point in points:
        distance = np.sqrt((point[0] - center_x)**2 + (point[1] - center_y)**2)
        distances.append(distance)
    
    # 检查距离是否相对均匀（不应该有点过于接近或过于远离质心）
    mean_distance = np.mean(distances)
    for distance in distances:
        if distance < mean_distance * 0.3 or distance > mean_distance * 3:
            return False
    
    return True

def try_other_combinations(candidates, min_distance):
    """
    尝试其他4个点的组合
    """
    from itertools import combinations
    
    # 尝试所有可能的4个点的组合
    for combo in combinations(candidates, 4):
        centers = [c[0] for c in combo]
        
        # 检查距离约束
        valid = True
        for i in range(4):
            for j in range(i+1, 4):
                distance = np.sqrt((centers[i][0] - centers[j][0])**2 + 
                                 (centers[i][1] - centers[j][1])**2)
                if distance < min_distance:
                    valid = False
                    break
            if not valid:
                break
        
        if valid and is_valid_quadrilateral(centers):
            return centers
    
    # 如果没有找到合适的组合，返回面积最大的4个点
    return [c[0] for c in candidates[:4]]

def detect_clips(frame):
    """
    使用HSV检测绿色夹子位置，返回四个点：[top, right, bottom, left]
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # HSV绿色范围
    lower_hsv = np.array([60, 120, 134])
    upper_hsv = np.array([75, 197, 218])
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    
    # 增强闭操作处理连通区域
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # 调试查看
    #cv2.imshow("green_clip_mask", mask)
    #cv2.waitKey(1) & 0xFF
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []  # 存储候选点信息：(center, area, contour)
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:  # 面积阈值
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                candidates.append(((cx, cy), area, cnt))
    
    if len(candidates) < 4:
        #print(f"检测到 {len(candidates)} 个候选点，少于4个")
        return None
    
    # 如果候选点多于4个，需要筛选出最佳的4个点
    if len(candidates) > 4:
        # 按面积排序，优先选择面积大的
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 使用改进的去重和筛选算法
        selected_points = smart_select_four_points(candidates)
        
        if selected_points is None:
            print("无法筛选出合适的4个点")
            return None
    else:
        # 正好4个点，直接使用
        selected_points = [candidate[0] for candidate in candidates]
    
    # 将点按照 [top, right, bottom, left] 的顺序排序
    points = np.array(selected_points)
    
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
                #print(f"警告：检测到重复点 {result[i]}")
                return None
    
    # 转换为numpy数组格式，供cv2.getPerspectiveTransform使用
    result_array = np.array(result, dtype=np.float32)
    
    return result_array

def draw_board_centers_on_frame(frame, M, color=(255, 255, 0)):
    """
    在图像上绘制板子上的九宫格区域中心（透视映射）
    Args:
        frame: 摄像头图像
        M: 透视变换矩阵 clips → board (300x300)
        color: 显示颜色
    """
    # 计算 M 的逆矩阵：将板子坐标 → 图像坐标
    M_inv = np.linalg.inv(M)

    for region_id in range(1, 10):
        x_norm, y_norm = get_region_center(region_id)  # 归一化坐标
        if x_norm is None:
            continue

        # 映射到板子上的坐标
        px = x_norm * 300
        py = y_norm * 300

        # 变换到图像坐标
        board_pt = np.array([[[px, py]]], dtype=np.float32)
        image_pt = cv2.perspectiveTransform(board_pt, M_inv)
        x_img, y_img = int(image_pt[0][0][0]), int(image_pt[0][0][1])

        # 显示中心点和编号
        cv2.circle(frame, (x_img, y_img), 5, color, -1)
        cv2.putText(frame, str(region_id), (x_img + 5, y_img - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)



def normalize_ball_position(frame):
    """
    获取小球相对板子的归一化坐标及九宫格区域编号
    Returns:
        x_norm, y_norm: 归一化坐标 (0~1)
        region_id: 区域编号 (1~9)
    """
    ball_x, ball_y = detect_ball_pos(frame)
    if ball_x is None:
#        print("No ball detect")
        return None, None, None
    clips = detect_clips(frame)
    
    if clips is None:
        print("No clips detect")
        return None, None, None
    else:
        
        M = cv2.getPerspectiveTransform(clips, np.float32([
        [150, 0],
        [300, 150],
        [150, 300],
        [0, 150]
    ]))
        draw_board_centers_on_frame(frame, M)

        for i, point in enumerate(clips):
            x, y = int(point[0]), int(point[1])
            cv2.circle(frame, (x, y), radius=5, color=(0, 0, 255), thickness=-1)  # 红色实心圆
            cv2.putText(frame, f"P{i+1}", (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)  # 标记编号

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
    if not (0<=x_norm<=1 and 0<=y_norm<=1):
#        print("no ball detect")
        return None,None,None
    else:
        cv2.circle(frame,(ball_x,ball_y),radius=5,color=(0,255,0),thickness=-1)
    # 判断区域编号（1~9）
    col = int(x_n // 100)
    row = int(y_n // 100)
    if 0 <= row <= 2 and 0 <= col <= 2:
        region_id = row * 3 + col + 1
    else:
        region_id = None

    return x_norm, y_norm, region_id