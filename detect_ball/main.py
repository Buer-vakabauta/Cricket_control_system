from camera import CameraCapture
from detect import detect_ball_pos
from serial_task import Ser
import cv2

Camera=CameraCapture(width=640,height=640,fps=90)
#Serial=Ser(baudrate_=15200,timeout_=1,port_='/dev/ttyUSB0')
Camera.start()
#Serial.start()
def main():
    while True:
        frame=Camera.get_frame()
        x,y=detect_ball_pos(frame)
#        Serial.send(f'{(x,y)}')
        if x is not -1:
            cv2.circle(frame, (x, y), 10, (0, 255, 0), 2)
            print(x,y)
        else:
            print("没有找到小球")
        cv2.imshow("ball_detect", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

def destroy(): 
    Camera.stop()
#    Serial.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
    destroy()    