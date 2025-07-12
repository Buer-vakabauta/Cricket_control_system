
import time

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

    def update(self, x_now, y_now):
        """
        根据球的目标区域PID计算舵机角度,并累计计时器
        Args:
            x_now,y_now:小球当前的归一化坐标
        Returns:
            返回对应X,Y的角度值
        """
        if self.target_x is None or x_now is None:
            return 0, 0

        error_x = self.target_x - x_now
        error_y = self.target_y - y_now

        angle_x = self.pid_x.update(error_x)
        angle_y = self.pid_y.update(error_y)

        # 停留检测逻辑
        if self.is_in_target_area(x_now, y_now):
            if self.stay_start_time is None:
                self.stay_start_time = time.time()
        else:
            self.stay_start_time = None

        return angle_x, angle_y

    def is_in_target_area(self, x, y, threshold=0.05):
        """
        判断小球是否在目标区域内
        Args:
            x,y:小球当前的归一化坐标
            threshold:允许的最大误差(半径)
        """
        if self.target_x is None or x is None:
            return False
        dx = abs(x - self.target_x)
        dy = abs(y - self.target_y)
        return dx < threshold and dy < threshold

    def has_stayed_long_enough(self):
        """
        用于判断小球是否在某区域停留足够长的时间
        由self.stay_duration控制停留时间
        若目标在区域内停留足够时间后脱离区域仍然会返回False
        """
        if self.stay_start_time is None:
            return False
        return (time.time() - self.stay_start_time) >= self.stay_duration
    

    def jump_ball(self, send_func, times=10, jump_angle=10, interval=0.6):
        """
        控制板面上下跳动，实现球体弹跳效果
        Args:
            send_func: 函数接口 send_func(a1, a2, a3, a4) 向STM32发送四个舵机角度
            times: 跳动次数
            jump_angle: 跳动幅度（±范围）
            interval: 每次跳动的间隔时间（秒）
        """
        print(f"🎮 开始跳动，共 {times} 次，每次间隔 {interval:.2f} 秒，跳动幅度 ±{jump_angle}°")
        base_angle = 90  # 板面初始水平角度
        for i in range(times):
            # 1. 板面快速下沉
            a_down = base_angle - jump_angle
            send_func(a_down, a_down, a_down, a_down)
            time.sleep(0.1)  # 冲击瞬间

            # 2. 快速回到中间位
            send_func(base_angle, base_angle, base_angle, base_angle)
            time.sleep(interval)

            print(f"🔁 第 {i+1}/{times} 次跳动完成")
        
        print("✅ 跳动动作结束")

    def controller_init(self):
        """
        初始化PID和计时器
        """
        self.pid_x.reset()
        self.pid_y.reset()
        self.stay_start_time = None
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
