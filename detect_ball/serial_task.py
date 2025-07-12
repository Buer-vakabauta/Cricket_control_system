import serial
import threading
class Ser:
    def __init__(self,port_='/dev/ttyUSB0',baudrate_=9600,timeout_=1):
        self.ser=serial.Serial(port=port_,baudrate=baudrate_,timeout=timeout_)
        self.message=None
        self.task="Waiting"
    def start(self):
        self.running=True
        self.wait_message_thread=threading.Thread(target=self._waiting_message)
        self.wait_message_thread.start()
    def stop(self):
        self.running=False
        if self.ser.is_open:
            self.ser.close()
    def _waiting_message(self):
        try:
            while self.running:
                if self.ser.in_waiting > 0:
                    self.message = self.ser.readline().decode('utf-8').strip()
                    if self.message and self.message.startswith("cmd:"):
                        self.task=self.message[4:].strip()
        except Exception as e:
            if self.ser.is_open:
                self.ser.close()
                pass
            print("Error:Serial port closed.")
        finally:
            if self.ser.is_open:
                self.ser.close()
            print("Serial port closed.")
    def get_message(self):
        return self.message
    def send(self, msg):
        """
        发送消息，自动加换行符
        Args:
            msg:要发送的字符串
        """
        msg=msg+'\n'
        self.ser.write(msg.encode())
    def clear_message(self):
        """
        清空message为None
        """
        self.message=None
    def Servo_set_angle(self,a1,a2,a3,a4):
        """
        设置舵机转动的角度
        Args:
            a1:舵机1
            a2:舵机2
            a3:舵机3
            a4:舵机4
        Returns:None
        """
        msg=f'({a1},{a2},{a3},{a4})'
        self.send(msg)