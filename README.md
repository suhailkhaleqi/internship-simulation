# Stajyer Yerleştirme Simülatörü

Firmalara stajyer yerleştirme sürecini simüle eden Python uygulaması. İki farklı algoritmik yaklaşımla (Greedy ve Heuristic) öğrenci-firma eşleştirmesi yapar.

## Proje Hakkında

Bu proje, sınırlı firma kontenjanları altında öğrencilerin firmalara adil ve mantıklı biçimde yerleştirilmesini sağlar. Program sonunda hiçbir öğrenci açıkta kalmaz.

### Temel Özellikler

- 121 öğrenci, 30 firma, 141 toplam kontenjan
- Her öğrencinin 5 firma tercihi ve GNO'su var
- İki farklı algoritma: Greedy ve Heuristic
- 3 fazlı yerleştirme sistemi
- %30 firma reddetme mekanizması
- Basit Tkinter GUI

## Kurulum

### Gereksinimler

- Python 3.x (3.6 ve üzeri önerilir)
- Tkinter (genellikle Python ile birlikte gelir)

### Dosyalar

```
py_new/
├── stajyer_simulator.py    # Ana program
├── students.csv            # Öğrenci verileri (121 öğrenci)
├── firms.csv               # Firma verileri (30 firma)
├── technical_report.md     # Teknik rapor
└── README.md               # Bu dosya
```

## Kullanım

### Programı Çalıştırma

```bash
cd /home/okaybuyukdeveci/Desktop/py_new
python3 stajyer_simulator.py
```

### GUI Arayüzü

Program açıldığında 3 buton göreceksiniz:

| Buton | Açıklama |
|-------|----------|
| **Run Greedy** | Greedy algoritmasını çalıştırır |
| **Run Heuristic** | Heuristic algoritmasını çalıştırır |
| **Compare Results** | İki algoritmayı karşılaştırır |

### Sekmeler

1. **Loglar**: Algoritma çalışırken iterasyon loglarını gösterir
2. **Yerleştirmeler**: Hangi öğrenci hangi firmaya yerleşti listesi
3. **Karşılaştırma**: Greedy vs Heuristic metrik tablosu

## Algoritmalar

### Greedy (Açgözlü) Algoritma

```
1. Öğrencileri GNO'ya göre sırala (yüksek → düşük)
2. Her öğrenci için tercihlerini sırayla kontrol et
3. İlk boş kontenjanı olan firmaya yerleştir
4. %30 red uygula, reddedilenler sonraki iterasyona kalır
```

**Avantajları:**
- Hızlı çalışır
- Basit mantık
- Düşük bellek kullanımı

**Dezavantajları:**
- Yerel optimum çözümler
- Daha fazla tercih dışı yerleştirme

### Heuristic (Sezgisel) Algoritma

```
1. Tüm (öğrenci, firma) çiftleri için skor hesapla
2. En yüksek skorlu eşleşmeleri önce yap
3. %30 red uygula
```

**Skor Formülü:**
```
Skor = (GNO × 0.4) + (Tercih × 0.3) + (Uygunluk × 0.3)
```

**Avantajları:**
- Daha yüksek memnuniyet skoru
- Daha az tercih dışı yerleştirme

**Dezavantajları:**
- Daha yavaş
- Daha fazla bellek kullanır

## 3 Fazlı Yerleştirme Sistemi

### Faz 1: Tercihli Yerleştirme
- Sadece öğrencinin 5 tercihi içindeki firmalar değerlendirilir
- Firma reddetme aktif (%30)
- 5 iterasyon ilerleme yoksa Faz 2'ye geçilir

### Faz 2: Tercih Dışı Yerleştirme
- Tüm firmalar değerlendirilir (tercih dışı dahil)
- Firma reddetme aktif (%30)
- 5 iterasyon ilerleme yoksa Faz 3'e geçilir

### Faz 3: Zorunlu Yerleştirme
- Tercih kısıtı yok
- Firma reddetme YOK
- GNO sırasına göre ilk boş firmaya yerleştir
- Tüm öğrenciler yerleşene kadar devam

## Çıktılar

### Metrikler

| Metrik | Açıklama |
|--------|----------|
| Toplam İterasyon | Kaç tur çalıştığı |
| Toplam İşlem | Kaç firma kontrolü yapıldığı |
| Çalışma Süresi | Saniye cinsinden süre |
| Memnuniyet Skoru | Tercih bazlı puan (max: 605) |
| Toplam Red | Kaç öğrenci reddedildi |

### Örnek Karşılaştırma Çıktısı

```
============================================================
         GREEDY vs HEURİSTİK KARŞILAŞTIRMA
============================================================

Metrik                        Greedy       Heuristic
---------------------------------------------------------
Toplam İterasyon                   4               3
Toplam İşlem                     523            3842
Çalışma Süresi (sn)           0.0156          0.0891
Memnuniyet Skoru                 462             489
Toplam Red                        18              12
```

## Veri Formatı

### students.csv

```csv
student_id,preferences,gno
S1,"LogoYazilim,Insider,Huawei,Netflix,HAVELSAN",2.29
S2,"Huawei,Trendyol,SAP,HAVELSAN,TUBITAK_BILGEM",2.72
...
```

### firms.csv

```csv
firma_id,kapasite
Google,3
Microsoft,2
Amazon,4
...
```

## Sık Sorulan Sorular

### Neden bu kadar çok 1. tercih yerleşmesi var?

- Toplam kontenjan (141) öğrenci sayısından (121) fazla
- 30 firmaya 121 öğrenci dağılıyor
- Heuristic algoritma skor bazlı optimize ediyor

### Tercih dışı yerleştirme ne zaman olur?

- Öğrencinin 5 tercihinin hepsi dolu olduğunda
- Faz 2 veya Faz 3'te gerçekleşir
- Greedy'de daha sık, Heuristic'te daha nadir

### Firma reddetme nasıl çalışır?

- Her iterasyon sonunda yerleşenler değerlendirilir
- %30 olasılıkla reddedilir
- Reddedilen öğrenci havuza geri döner
- Aynı firmaya tekrar başvurabilir

### Algoritma neden 3 fazlı?

- Kilitlenmeyi önlemek için
- Faz 1'de ideal yerleştirme denenir
- Başarısız olursa kademeli gevşeme
- Faz 3 her zaman çözüm garantiler

## Teknik Detaylar

Daha fazla teknik bilgi için `technical_report.md` dosyasına bakınız:
- Veri yapıları
- Algoritma karmaşıklığı
- Skor hesaplama formülleri
- Performans analizi

## Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## İletişim

Sorularınız için proje sahibiyle iletişime geçebilirsiniz.
