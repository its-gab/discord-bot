import cv2

def capture_frame():
    camera = cv2.VideoCapture(0)
    #camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    #camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not camera.isOpened():
        return None

    ret, frame = camera.read()
    camera.release()

    if not ret:
        return None
    return frame