# 🚗 Otomatik Araç Park Yeri Tespiti (OpenCV ile)

Bu proje, **Python** ve **OpenCV** kullanarak bir otopark görüntüsündeki boş ve dolu park alanlarını tespit eder.
Görüntü işleme teknikleriyle her park alanı analiz edilir ve sonuçlar görsel olarak renklendirilmiş bir çıktı ile gösterilir.
Yeni gelen araç en yakın alana yönlendirilir.

## 📸 Proje Görseli

![Park Durumu](./2ac8f19f-399f-4374-8304-7046538209cb.png)

---

## 🔧 Kullanılan Teknolojiler

- Python 3.11
- OpenCV
- NumPy
- Pickle

---

## ⚙️ Özellikler

- Boş ve dolu park yerlerinin tespiti
- Her park alanı için beyaz piksel yoğunluğu analizi
- Görsel çıktıda:
  - 🟥 Kırmızı kutu: Dolu park yeri
  - 🟩 Yeşil kutu: Boş park yeri
  - 🔢 Sayılar: Piksel sayısı (yoğunluk)
  - 🟨 Üstte: Boş / Toplam park sayısı (`Free: 43/89`)

---

## 📁 Proje Dosya Yapısı

.
├── CarParkPos # Pickle dosyası: Park yerlerinin koordinatları
├── video.mp4 # Otopark videosu
├── main.py # Ana Python betiği
├── README.md # Açıklama dosyası


---

## ▶️ Kurulum ve Kullanım

1. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install opencv-python numpy
CarParkPos adlı Pickle dosyası içerisinde park alanı koordinatlarının bulunduğundan emin olun. (Eğer dosya yoksa, cv2.setMouseCallback() ile koordinatları manuel olarak belirleyip kaydedebilirsiniz.)

Projeyi başlatın:


Kopyala
python main.py
📌 Notlar
Her park alanı, cv2.countNonZero() ile analiz edilir.

count < 150 ise boş sayılır, değilse dolu kabul edilir.

Eşik değeri (150) ihtiyaca göre ayarlanabilir.

💡 Geliştirme Fikirleri
Derin öğrenme ile daha doğru tespit
Gerçek zamanlı IP kamera desteği
Web arayüzü ve mobil uygulama entegrasyonu
Park süresi takibi

