import cv2
import pickle
import numpy as np
import math

# Sabitler
width = 27
height = 13
entry_point_width = 50
entry_point_height = 20
car_min_area = 500#hareketli nesnelerin araç sayılması için kontur
movement_threshold = 25 #arka plan farkında hareket olarak kabul edilecek piksel değeri eşiği
park_threshold = 150
parking_completion_distance = 20 #park etmeden önceki uzaklık
VIDEO_FRAME_DELAY_MS = 200 #video bekleme süresi

# Global değişkenler: Uygulamanın farklı yerlerinden erişilen ve değiştirilen durum bilgileri
car_detected = False             # Bir aracın giriş noktasında algılanıp algılanmadığını tutar
target_park_spot = None          # Aracın yönlendirileceği boş park yerinin koordinatları
car_position = None              # Algılanan aracın güncel pozisyonu (merkez x, merkez y)
guidance_message = ""            # Ekranda ve konsolda gösterilecek yönlendirme mesajı
pause_video = False              # Videoyu duraklatma/oynatma durumu
video_paused_by_system = False   # Videonun sistem tarafından duraklatılıp duraklatılmadığı
mouse_click_to_continue = False  # Sistemin duraklamasının fare tıklamasıyla devam edip etmeyeceği

# Kayıtlı pozisyonları ve giriş noktalarını yükle
try:
    with open("CarParkPos", "rb") as f:
        posList = pickle.load(f)
except:
    posList = []
    print("CarParkPos dosyası bulunamadı. Lütfen parking_space_picker.py'yi çalıştırın.")

try:
    with open("EntryPoints", "rb") as f:
        entryPoints = pickle.load(f)
except:
    entryPoints = []
    print("EntryPoints dosyası bulunamadı. Lütfen parking_space_picker.py'yi çalıştırın ve giriş alanlarını belirleyin (Ctrl+tık).")

# Mouse callback fonksiyonu
def mouseClick(events, x, y, flags, params):
    global pause_video, video_paused_by_system, mouse_click_to_continue
    if events == cv2.EVENT_LBUTTONDOWN and video_paused_by_system and mouse_click_to_continue:
        pause_video = False
        video_paused_by_system = False
        mouse_click_to_continue = False
        print("Tıklama algılandı, video devam ediyor.")

# Park alanlarının durumunu kontrol et ve çiz
def checkParkSpace(imgg, original_img):
    spaceCounter = 0
    empty_spots = []

    for i, pos in enumerate(posList):
        x, y = pos
        
        img_crop = imgg[y: y + height, x:x + width]
        count = cv2.countNonZero(img_crop)
        
        if count < park_threshold:
            color = (0, 255, 0)
            spaceCounter += 1
            empty_spots.append((pos, i))
        else:
            color = (0, 0, 255)
    
        cv2.rectangle(original_img, pos, (pos[0] + width, pos[1] + height), color, 2) 
        cv2.putText(original_img, str(count), (x, y + height - 2), cv2.FONT_HERSHEY_PLAIN, 1, color, 1)
    
    #ekranda dolu/boş oranını göstermek için
    cv2.putText(original_img, f"Bos: {spaceCounter}/{len(posList)}", (15,24), cv2.FONT_HERSHEY_PLAIN, 2,(0,255,255),4)

    return empty_spots

# Giriş noktasında araç algıla
#mevcut video karesi ile videonun başında aldığımız first_frame.png (sabit arka plan) arasındaki mutlak farkı (cv2.absdiff) hesaplar. Bu fark görüntüsü, sadece hareketli bölgeleri içerir.
def detect_car_in_entry_point(frame_dilated, original_frame):
    global car_detected, car_position, pause_video, video_paused_by_system, guidance_message, target_park_spot, mouse_click_to_continue
    
    if not entryPoints:
        return False

    for ep_x, ep_y in entryPoints:
        cv2.rectangle(original_frame, (ep_x, ep_y), (ep_x + entry_point_width, ep_y + entry_point_height), (0, 255, 255), 2)
    
    contours, _ = cv2.findContours(frame_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > car_min_area:
            x, y, w, h = cv2.boundingRect(cnt)
            center_x = x + w // 2
            center_y = y + h // 2

            for ep_x, ep_y in entryPoints:
                if ep_x < center_x < ep_x + entry_point_width and \
                   ep_y < center_y < ep_y + entry_point_height:
                    
                    if not car_detected and not video_paused_by_system:
                        car_detected = True
                        car_position = (center_x, center_y)
                        pause_video = True
                        video_paused_by_system = True
                        mouse_click_to_continue = True
                        guidance_message = "Yeni arac algilandi! Boş yer aranıyor..."
                        print(guidance_message)
                        return True
                    elif car_detected:
                        car_position = (center_x, center_y)
                        cv2.rectangle(original_frame, (x, y), (x + w, y + h), (0, 165, 255), 2)
                        cv2.putText(original_frame, "Arac Algilandi", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)
                        return True
    return False

def find_nearest_empty_spot(car_pos, empty_spots):
    if not car_pos or not empty_spots:
        return None
    
    min_dist = float('inf')
    nearest_spot = None

    for spot_pos, spot_idx in empty_spots:
        spot_center_x = spot_pos[0] + width // 2
        spot_center_y = spot_pos[1] + height // 2
        
        dist = math.hypot(car_pos[0] - spot_center_x, car_pos[1] - spot_center_y)
        
        if dist < min_dist:
            min_dist = dist
            nearest_spot = spot_pos
    
    return nearest_spot

def provide_guidance(car_pos, target_spot_pos):
    global guidance_message
    if not car_pos or not target_spot_pos:
        guidance_message = "Hedef veya arac konumu belirlenemedi."
        print(guidance_message)
        return

    car_x, car_y = car_pos
    spot_x, spot_y = target_spot_pos[0] + width // 2, target_spot_pos[1] + height // 2

    old_guidance_message = guidance_message

    if math.hypot(car_x - spot_x, car_y - spot_y) < parking_completion_distance:
        guidance_message = "Park et!"
    elif abs(car_x - spot_x) > abs(car_y - spot_y):
        if car_x < spot_x:
            guidance_message = "Sola dogru ilerle!"
        else:
            guidance_message = "Saga dogru ilerle!"
    else:
        if car_y < spot_y:
            guidance_message = "Asagiya (ileri) dogru ilerle!"
        else:
            guidance_message = "Yukariya (geri) dogru ilerle!"
            
    if guidance_message != old_guidance_message:
        print(guidance_message)

cap = cv2.VideoCapture("video.mp4")

ret, first_frame = cap.read()
if not ret:
    print("Video okunamadı. 'video.mp4' dosyasının doğru yolda olduğundan emin olun.")
    exit()

first_frame_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
first_frame_blur = cv2.GaussianBlur(first_frame_gray, (21, 21), 0)

cv2.namedWindow("img")
cv2.setMouseCallback("img", mouseClick)

while True:
    current_frame_read = False

    if not pause_video:
        success, img = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, img = cap.read()
            if not success:
                print("Video tekrar başlatılamadı. Çıkılıyor.")
                break
        current_frame_read = True
    
    if pause_video and not current_frame_read and 'img' in locals():
        pass
    elif not current_frame_read:
        continue

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3,3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    imgDilate = cv2.dilate(imgMedian, np.ones((3,3)), iterations = 1)
    
    frame_diff = cv2.absdiff(first_frame_blur, imgBlur)
    _, frame_thresh = cv2.threshold(frame_diff, movement_threshold, 255, cv2.THRESH_BINARY)
    frame_dilated = cv2.dilate(frame_thresh, None, iterations=2)


    empty_spots = checkParkSpace(imgDilate, img)

    car_in_entry = detect_car_in_entry_point(frame_dilated, img)

    if car_detected and target_park_spot is None and video_paused_by_system:
        target_park_spot = find_nearest_empty_spot(car_position, empty_spots)
        if target_park_spot:
            guidance_message = "Hedef boş yer bulundu. Yönlendiriliyor... Devam etmek için tıklayın."
            print(guidance_message)
        else:
            guidance_message = "Boş park yeri bulunamadı! Video devam ediyor."
            print(guidance_message)
            car_detected = False
            pause_video = False
            video_paused_by_system = False
            mouse_click_to_continue = False

    if car_detected and target_park_spot:
        cv2.rectangle(img, target_park_spot, (target_park_spot[0] + width, target_park_spot[1] + height), (255, 255, 0), 3)
        cv2.putText(img, "Hedef", (target_park_spot[0], target_park_spot[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        
        if car_position:
            provide_guidance(car_position, target_park_spot)
            
            spot_center_x = target_park_spot[0] + width // 2
            spot_center_y = target_park_spot[1] + height // 2
            
            if math.hypot(car_position[0] - spot_center_x, car_position[1] - spot_center_y) < parking_completion_distance:
                guidance_message = "Arac park edildi! Video devam ediyor."
                print(guidance_message)
                car_detected = False
                target_park_spot = None
                pause_video = False
                video_paused_by_system = False
                mouse_click_to_continue = False

    cv2.putText(img, guidance_message, (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    if mouse_click_to_continue:
        cv2.putText(img, "Devam etmek icin tiklayin...", (15, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # <<<<<<<<< BURADA YENİ BOYUTLANDIRMA SATIRLARINI EKLEYİN >>>>>>>>>
    # Örnek: img = cv2.resize(img, (1280, 720)) # Full HD boyutunda
    # Veya orijinal boyutun belirli bir katı:
    scale_percent = 150 # %150 büyütme (1.5 kat)
    new_width = int(img.shape[1] * scale_percent / 100)
    new_height = int(img.shape[0] * scale_percent / 100)
    img = cv2.resize(img, (new_width, new_height))
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    cv2.imshow("img", img)
    
    key = cv2.waitKey(VIDEO_FRAME_DELAY_MS if not pause_video else 0) & 0xFF 

    if key == ord('p'):
        pause_video = not pause_video
        video_paused_by_system = False
        mouse_click_to_continue = False
        print(f"Video manuel olarak {'duraklatıldı' if pause_video else 'devam ettirildi'}.")
    elif key == 27:
        break

cap.release()
cv2.destroyAllWindows()