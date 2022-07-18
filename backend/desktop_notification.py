import os
from win10toast import ToastNotifier

class DesktopNotification:
    def __init__(self):
        self.toast = ToastNotifier()
    
    def _show_notification(self, title, body, duration, icon_path):
        toast.show_toast(title, body,duration=duration, icon_path=icon_path)
