from camera import CameraCapture
from detect import detect_ball_pos,detect_clips,normalize_ball_position
from serial_task import Ser
from control import PID,BallPIDController,task4_path
import cv2
import time
#####################初始化#################################
Camera=CameraCapture(width=640,height=640,fps=90)
Serial=Ser(baudrate_=9600,timeout_=1,port_='/dev/ttyUSB0')
Pid_X = PID(Kp=10, Ki=0.2, Kd=10, output_limit=30, integral_limit=100)
Pid_Y = PID(Kp=10, Ki=0.2, Kd=10, output_limit=30, integral_limit=100)
Ball=BallPIDController(Pid_X,Pid_Y,stay_duration=5)

#####################启动线程###############################
Camera.start()
Serial.start()
Pid_X.reset()
Pid_Y.reset()
###########################################################

def main():
    task_flag=0#用于在需要的时候记录任务的进度
    while True:
#########################循环处理###########################
        frame=Camera.get_frame()#获取视频帧
        x_pos,y_pos,ball_regin=normalize_ball_position(frame)#尝试寻找球
        if x_pos is None or y_pos is None:#未找到球，重新寻找
            cv2.imshow("ball_detect", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break        
            print("No ball detect")
            continue

######################任务选择###############################
        if(Serial.task=='task1'):
            task_flag=1
            Ball.stay_duration=5
            Ball.set_target_region(2)
            angle_x,angle_y=Ball.update(x_pos,y_pos)
            Serial.Servo_set_angle(angle_x,angle_y,-angle_x,-angle_y)

    
        elif(Serial.task=='task2'):
            task_flag=2
            Ball.stay_duration=5
            Ball.set_target_region(2)
            angle_x,angle_y=Ball.update(x_pos,y_pos)
            Serial.Servo_set_angle(angle_x,angle_y,-angle_x,-angle_y)


        elif(Serial.task=='task3'):
            Ball.stay_duration=5
            if task_flag<3 or task_flag>3:
                task_flag=3.1
                Ball.set_target_region(4)
            elif Ball.has_stayed_long_enough() and task_flag==3.1:
                task_flag=3.2
                Ball.set_target_region(9)
            angle_x,angle_y=Ball.update(x_pos,y_pos)
            Serial.Servo_set_angle(angle_x,angle_y,-angle_x,-angle_y)
        

        elif(Serial.task=="task4"):
            if task_flag<4 or task_flag>4:
                task_flag=4.1
                Ball.stay_duration=1

            elif Ball.has_stayed_long_enough and task_flag>=4 and task_flag<5:
                task_flag+=0.1
                Ball.controller_init()
    
            index=int((task_flag-4)*10)
            index = index if index < len(task4_path) else len(task4_path) - 1
            Ball.target_x,Ball.target_y=task4_path[index]
            angle_x,angle_y=Ball.update()
            Serial.Servo_set_angle(angle_x,angle_y,-angle_x,-angle_y)

        elif(Serial.task=='task5'):
            Ball.jump_ball(Serial.Servo_set_angle,1,15,1)
#####################本地控制(调试数据)#######################

        ball_x,ball_y=detect_ball_pos(frame)
#        points=detect_clips(frame)
#        if points is not None:
#            for i, point in enumerate(points):
#                x, y = int(point[0]), int(point[1])
#                cv2.circle(frame, (x, y), radius=5, color=(0, 0, 255), thickness=-1)  # 红色实心圆
#                cv2.putText(frame, f"P{i+1}", (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)  # 标记编号
        cv2.circle(frame,(ball_x,ball_y),radius=5,color=(0,255,0),thickness=-1)
#######################显示内容#############################
        #绘制任务进程
        cv2.putText(frame,f'task:{task_flag},ball:{ball_x},{ball_y},{ball_regin}',(0,10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv2.imshow("ball_detect", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break



def destroy():
    """
    释放线程和窗口对象
    退出程序
    """ 
    Camera.stop()
    Serial.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
    destroy()