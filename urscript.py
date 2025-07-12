import requests
import numpy as np
import cv2
import socket
import time
import speech_recognition as sr
from difflib import get_close_matches

UR_IP         = "192.168.1.13"
ROBOT_PORT    = 30002
GRIPPER_PORT  = 63352

CAMERA_URL    = f"http://{UR_IP}:4242/current.jpg?annotations=off"
IMG_W, IMG_H  = 866, 650
REAL_W, REAL_H = 0.375, 0.285

co = 0 # Counter used at pick and place

CX, CY = IMG_W//2, IMG_H//2 # Center of the image
BASE_X, BASE_Y, BASE_Z = 0.133, -0.486, 0.504 #Robot home position to capture image
ORIENTATION = (0.0, -3.14, 0.0)  #Robot orientation to be changed after capturing the image

# HSV thresholds
COLOURS = {
    'red':   ([0, 120, 70],   [10, 255, 255], [170, 120, 70], [180, 255, 255]),
    'green': ([35, 45, 45],   [89, 255, 255]),
    'yellow':([20,100,100],   [30, 255, 255]),
}
VALID_COMMANDS = list(COLOURS.keys()) + ['go home', 'bye']


def get_camera_image():
    try:
        r = requests.get(CAMERA_URL, timeout=5)
        r.raise_for_status()
        arr = np.frombuffer(r.content, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except Exception as e:
        print("Camera fetch failed:", e)
        return None

def detect_objects(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    out = img.copy()
    results = {}
    for colour, ranges in COLOURS.items():
        if colour == 'red':
            l1,u1,l2,u2 = [np.array(r) for r in ranges]
            mask = cv2.bitwise_or(cv2.inRange(hsv, l1, u1),
                                  cv2.inRange(hsv, l2, u2))
        else:
            low, high = [np.array(r) for r in ranges]
            mask = cv2.inRange(hsv, low, high)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        pts = []
        for c in cnts:
            if cv2.contourArea(c) < 500:
                continue
            M = cv2.moments(c)
            if M['m00'] == 0:
                continue
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            pts.append((cx, cy))
            x,y,w,h = cv2.boundingRect(c)
            cv2.circle(out, (int(x+w/2), int(y+h/2)), 4, (0, 0, 255), -1)
            cv2.rectangle(out, (x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(out, colour, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0),2)
        results[colour] = pts
    return out, results

def pixel_to_robot(x_px, y_px):
    sx = REAL_W / IMG_W
    sy = REAL_H / IMG_H

    du = x_px - CX
    dv = y_px - CY
    dx = dy = 0.0

    # Quadrant logic
    if x_px <= CX and y_px <= CY:  # Top Left
        dx = ((du+70) * sx)
        dy = -((dv-10) * sy)
    elif x_px > CX and y_px <= CY:  # Top Right
        dx = ((du+200) * sx)
        dy = -((dv-10) * sy)
    elif x_px <= CX and y_px > CY:  # Bottom Left
        dx = ((du+70) * sx)
        dy = ((dv-10) * sy)
    else:                           # Bottom Right
        dx = ((du+200) * sx)
        dy = ((dv-10) * sy)

    x = BASE_X + dx
    y = BASE_Y + dy
    z = BASE_Z
    print(f"Pixel→Robot | du={du:+.1f}px, dv={dv:+.1f}px  →  dx={dx:+.3f}m, dy={dy:+.3f}m")
    print(f"Final target | x={x:.3f}, y={y:.3f}, z={z:.3f}")
    return x, y, z, *ORIENTATION

def connect_to_ur():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((UR_IP, ROBOT_PORT))
    print(f"Connected to UR at {UR_IP}:{ROBOT_PORT}")
    return s

def send_gripper_command(cmd):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as g:
        g.connect((UR_IP, GRIPPER_PORT))
        g.sendall(b"SET SPE 255\n")
        g.sendall((cmd + '\n').encode('utf-8'))
        resp = g.recv(1024).decode().strip()
        print(f"Gripper | Sent: {cmd} | Resp: {resp}")

def go_home(s):
    print(" Going Home…")
    s.send(b"movej(p[0.13385, -0.48665, 0.50415, 0.0, 3.035, -0.785], a=1.0, v=0.5)\n")
    time.sleep(2.5)
    send_gripper_command("SET POS 255")
    time.sleep(1)
    send_gripper_command("SET POS 0")
    time.sleep(2)

def pick_it(s, x, y, z, rx, ry, rz):
    print(f" Picking at {x:.3f}, {y:.3f}, {z:.3f}")
    time.sleep(0.5)
    send_gripper_command("SET POS 0")
    time.sleep(1)
    s.send(f"movel(p[{x:.3f}, {y:.3f}, {z-0.20:.3f}, {rx}, {ry}, {rz}], a=0.2, v=0.5)\n".encode())
    time.sleep(3.0)
    s.send(f"movel(p[{x:.3f}, {y:.3f}, {z-0.25:.3f}, {rx}, {ry}, {rz}], a=0.5, v=0.5)\n".encode())
    time.sleep(2.0)
    send_gripper_command("SET POS 100")
    time.sleep(1.0)
    s.send(f"movel(p[{x:.3f}, {y:.3f}, {z-0.20:.3f}, {rx}, {ry}, {rz}], a=0.5, v=0.5)\n".encode())
    time.sleep(1)

def place_it(s, px, py, pz, rx, ry, rz):
    global co
    offset = 0.1 if (co % 2) == 1 else 0.2
    print("counter value is:", co)
    print(f"Placing at {px:.3f}, {py:.3f}, {pz:.3f}")
    s.send(f"movej(p[{px+offset:.3f}, {py:.3f}, {pz+0.10:.3f}, {rx}, {ry}, {rz}], a=0.8, v=0.5)\n".encode())
    time.sleep(3)
    s.send(f"movel(p[{px+offset:.3f}, {py:.3f}, {pz:.3f}, {rx}, {ry}, {rz}], a=0.5, v=0.5)\n".encode())
    time.sleep(2.0)
    send_gripper_command("SET POS 0")
    time.sleep(1)
    s.send(f"movel(p[{px+offset:.3f}, {py:.3f}, {pz+0.10:.3f}, {rx}, {ry}, {rz}], a=1.0, v=0.8)\n".encode())
    time.sleep(1)
    co += 1
    if co >= 3:
        co = 0

def map_command(spoken_text):
    matches = get_close_matches(spoken_text, VALID_COMMANDS, n=1, cutoff=0.6)
    return matches[0] if matches else None

def recognize_command():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("Listening for a command (say: red, green, yellow, go home, or bye)...")
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"Raw input: {command}")
        mapped = map_command(command)
        if not mapped:
            print("Unrecognized command.")
        return mapped
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print(f"API error: {e}")
    return None


def main():
    
    s = connect_to_ur()
    
    go_home(s)

    while True:
        img = get_camera_image()
        if img is None:
            print("No image...")
            time.sleep(1)
            continue
        vis, det = detect_objects(img)
        cv2.imshow("Detect", vis)
        cv2.waitKey(1)

        cmd = recognize_command()
        if not cmd:
            continue
        if cmd == 'bye':
            print("Bye")
            break
        if cmd == 'go home':
            go_home(s)
            continue

        pts = det.get(cmd, [])
        if not pts:
            print(f"No {cmd} detected.")
            continue
        x_px, y_px = pts[0]
        print("the points value is", pts)
        pose = pixel_to_robot(x_px, y_px)
        pick_it(s, *pose)
        place_it(s, 0.30, -0.30, 0.25, *ORIENTATION)
        go_home(s)

    cv2.destroyAllWindows()
    s.close()

if __name__ == "__main__":
    main()

