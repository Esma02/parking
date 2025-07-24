import cv2
import pickle

#park yeri için gereken dikdörtgenler
width = 27
height = 13

#Varsa park yeri konumları onu gösterir yoksa boş döndürür.
try:
    with open("CarParkPos","rb") as f:
        posList = pickle.load(f)
except:
    posList=[]

try:
    with open("EntryPoints","rb") as f:
        entryPoints = pickle.load(f)
except:
    entryPoints=[]

def mouseClick(events, x , y, flags,params):
    global entryPoints
    entry_point_silme_width = 50
    entry_point_silme_height = 20

    if events==cv2.EVENT_LBUTTONDOWN:#ekleme için
        if flags & cv2.EVENT_FLAG_CTRLKEY:
            entryPoints.append((x,y))
            print(f"Giriş noktası eklendi: ({x},{y})")
        else:
            posList.append((x,y))
            print(f"Park yeri eklendi: ({x},{y})")

    if events==cv2.EVENT_RBUTTONDOWN:#silme işlemi için
        for i ,pos in enumerate(posList):
            x1,y1=pos
            if x1 < x < x1 + width and y1 < y < y1 + height:
                posList.pop(i)
                print(f"Park yeri silindi: ({x1},{y1})")
                break
        for i, ep_pos in enumerate(entryPoints):
            ep_x, ep_y = ep_pos
            if ep_x < x < ep_x + entry_point_silme_width and ep_y < y < ep_y + entry_point_silme_height:
                entryPoints.pop(i)
                print(f"Giriş noktası silindi: ({ep_x},{ep_y})")
                break

    with open("CarParkPos","wb") as f:
        pickle.dump(posList,f)
    with open("EntryPoints","wb") as f:
        pickle.dump(entryPoints,f)


while True:
    img = cv2.imread("first_frame.png")
    if img is None:
        print("Hata: 'first_frame.png' bulunamadı. Lütfen videodan ilk kareyi oluşturun.")
        break

    for pos in posList: #dikdörtgen çizme işlemi 
        cv2.rectangle(img, pos, (pos[0] + width,pos[1]+ height), (255,0,0))

    entry_point_display_width = 50
    entry_point_display_height =20
    for ep_pos in entryPoints:
        ep_x, ep_y = ep_pos
        cv2.rectangle(img, ep_pos, (ep_x + entry_point_display_width, ep_y + entry_point_display_height), (0, 255, 255), 2)
        cv2.putText(img, "Entry", (ep_x, ep_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

    #fotoğrafı büyütme için
    scale_percent = 200 # %200 büyütme (2 kat)
    new_width = int(img.shape[1] * scale_percent / 100)
    new_height = int(img.shape[0] * scale_percent / 100)
    img = cv2.resize(img, (new_width, new_height))

    cv2.imshow("img",img)#pencerede görüntüyü gösterir
    cv2.setMouseCallback("img", mouseClick)
    key = cv2.waitKey(1)#tıklamadan sonra 1 milisaniye bekler
    if key == 27:#☺esc tuşu ile kapat
        break

cv2.destroyAllWindows()# Tüm OpenCV pencerelerini kapatır