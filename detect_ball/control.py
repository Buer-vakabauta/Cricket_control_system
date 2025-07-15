
import time
import cv2
class PID:
    def __init__(self, Kp, Ki, Kd, output_limit=None, integral_limit=None):
        self.Kp = Kp  # 比例系数
        self.Ki = Ki  # 积分系数
        self.Kd = Kd  # 微分系数

        self.output_limit = output_limit  # 输出限幅
        self.integral_limit = integral_limit  # 积分限幅

        self.integral = 0    
        self.prev_error = 0

    def reset(self):
        """重置 PID 状态"""
        self.integral = 0
        self.prev_error = 0

    def update(self, error, dt=1.0):
        """
        输入误差，返回控制值
        Args:
            error: 当前误差（目标 - 实际）
            dt: 时间间隔，默认为1，可按实际帧率调整
        Returns:
            PID 输出值
        """
        # 积分项
        self.integral += error * dt
        if self.integral_limit is not None:
            self.integral = max(min(self.integral, self.integral_limit), -self.integral_limit)

        # 微分项
        derivative = (error - self.prev_error) / dt
        self.prev_error = error

        # PID 计算
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # 输出限幅
        if self.output_limit is not None:
            output = max(min(output, self.output_limit), -self.output_limit)

        return output

def get_region_center(region_id):
    """
    获取区域中心坐标
    Args：
        region_id:传入区域ID
    Return：
        x,y:区域的中心坐标
        区域不存在返回None,None
    """
    if not 1 <= region_id <= 9:
        return None, None
    row = (region_id - 1) // 3
    col = (region_id - 1) % 3
    x = (col * 2 + 1) / 6
    y = (row * 2 + 1) / 6
    return x, y

def goto_region(Pid_X,Pid_Y,x_pos,y_pos,region_id,target_x=0,target_y=0):
    """
    计算一次Pid，使小球向指定区域
    Args:
        Pid_X,PidY:XY轴对应的PID
        x_pos,y_pos:小球当前所在的x,y坐标
        region_id:目标区域的ID(传入无效值时，可指定目标位置)
        target_x:目标X坐标
        target_y:目标Y坐标
        
    Returns:
        返回对应X,Y的PID值(X,Y)
    """
    if region_id>0 and region_id<10:
        target_x,target_y=get_region_center(region_id)
    angle_x=Pid_X.update(target_x-x_pos)
    angle_y=Pid_Y.update(target_y-y_pos)
    return (angle_x,angle_y)


class BallPIDController:
    def __init__(self, pid_x,pid_y,stay_duration=5):
        self.pid_x = pid_x
        self.pid_y = pid_y
        self.target_region = None
        self.target_x = None
        self.target_y = None
        self.stay_duration = stay_duration
        self.stay_start_time = None
        self.last_
    def set_target_region(self, region_id):
        """
        更新目标区域，当目标区域更新时初始化停留时间
        Args:
            region_id:传入区域ID
        """
        if region_id != self.target_region:
            self.target_region = region_id
            self.target_x, self.target_y = get_region_center(region_id)
            self.pid_x.reset()
            self.pid_y.reset()
            self.stay_start_time = None  # 重置停留计时器
            print(f"设置目标区域 {region_id}，目标=({self.target_x:.2f},{self.target_y:.2f})")

import time

class BallPIDController:
    def __init__(self, pid_x, pid_y, vel_pid_x, vel_pid_y, stay_duration=5):
        self.pid_x = pid_x
        self.pid_y = pid_y
        self.vel_pid_x = vel_pid_x
        self.vel_pid_y = vel_pid_y

        self.target_region = None
        self.target_x = None
        self.target_y = None

        self.stay_duration = stay_duration
        self.stay_start_time = None

        self.last_time = None
        self.last_x = None
        self.last_y = None

    def set_target_region(self, region_id):
        if region_id != self.target_region:
            self.target_region = region_id
            self.target_x, self.target_y = get_region_center(region_id)
            self.pid_x.reset()
            self.pid_y.reset()
            self.vel_pid_x.reset()
            self.vel_pid_y.reset()
            self.stay_start_time = None
            self.last_time = None
            self.last_x = None
            self.last_y = None
            print(f"设置目标区域 {region_id}，目标=({self.target_x:.2f},{self.target_y:.2f})")

    def update(self, x_now, y_now):
        if self.target_x is None or x_now is None:
            return 0, 0

        # === 速度估算 ===
        now_time = time.time()
        vx, vy = 0, 0
        if self.last_time is not None:
            dt = now_time - self.last_time
            if dt > 0:
                vx = (x_now - self.last_x) / dt
                vy = (y_now - self.last_y) / dt

        self.last_time = now_time
        self.last_x = x_now
        self.last_y = y_now

        # === PID 控制 ===
        error_x = self.target_x - x_now
        error_y = self.target_y - y_now

        control_x = self.pid_x.update(error_x)
        control_y = self.pid_y.update(error_y)

        brake_x = self.vel_pid_x.update(-vx)  # 速度越大，刹车越重
        brake_y = self.vel_pid_y.update(-vy)

        angle_x = control_x + brake_x
        angle_y = control_y + brake_y

        # === 停留检测 ===
        if self.is_in_target_area(x_now, y_now):
            if self.stay_start_time is None:
                self.stay_start_time = now_time
        else:
            self.stay_start_time = None

        return angle_x, angle_y

    def is_in_target_area(self, x, y, threshold=0.05):
        if self.target_x is None or x is None:
            return False
        dx = abs(x - self.target_x)
        dy = abs(y - self.target_y)
        return dx < threshold and dy < threshold

    def has_stayed_long_enough(self):
        if self.stay_start_time is None:
            return False
        print(time.time() - self.stay_start_time)
        return (time.time() - self.stay_start_time) >= self.stay_duration

    def jump_ball(self, send_func, times=10, jump_angle=10, interval=0.6):
        print(f"🎮 开始跳动，共 {times} 次，每次间隔 {interval:.2f} 秒，跳动幅度 ±{jump_angle}°")
        base_angle = 90
        for i in range(times):
            send_func(base_angle - jump_angle, base_angle - jump_angle, base_angle - jump_angle, base_angle - jump_angle)
            time.sleep(0.1)
            send_func(base_angle, base_angle, base_angle, base_angle)
            time.sleep(interval)
            print(f"🔁 第 {i+1}/{times} 次跳动完成")
        print("✅ 跳动动作结束")

    def controller_init(self):
        self.pid_x.reset()
        self.pid_y.reset()
        self.vel_pid_x.reset()
        self.vel_pid_y.reset()
        self.stay_start_time = None
        self.last_time = None
        self.last_x = None
        self.last_y = None

# 预定义路径点（归一化坐标）
task4_path = [
    get_region_center(1),
    ((0.1667 + 0.5000) / 2, (0.1667 + 0.1667) / 2),  # 1->2 中点
    get_region_center(2),
    ((0.5000 + 0.8333) / 2, (0.1667 + 0.5000) / 2),  # 2->6 中点
    get_region_center(6),
    ((0.8333 + 0.8333) / 2, (0.5000 + 0.8333) / 2),  # 6->9 中点
    get_region_center(9)
]


def draw_region_centers(frame, width=640, height=640):
    """
    在图像上画出 9 宫格区域中心点（根据归一化坐标转换）
    Args:
        frame: 原始图像（BGR）
        width, height: 图像尺寸（默认640x640）
    """
    for region_id in range(1, 10):
        norm_x, norm_y = get_region_center(region_id)
        if norm_x is None:
            continue
        # 转换为像素坐标
        px = int(norm_x * width)
        py = int(norm_y * height)

        # 画圆圈标记中心点
        cv2.circle(frame, (px, py), 6, (0, 255, 255), -1)
        # 写上区域号
        cv2.putText(frame, f"{region_id}", (px + 5, py - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
