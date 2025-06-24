# TÜRSAB Acenta Bot 🤖

TÜRSAB (Türkiye Seyahat Acentaları Birliği) sitesinden acenta bilgilerini otomatik olarak çeken Python bot'u.

## 📋 Özellikler

- ✅ **Otomatik Web Scraping** - TÜRSAB sitesinden acenta verilerini çeker
- ✅ **PostgreSQL Entegrasyonu** - Verileri otomatik olarak veritabanına kaydeder
- ✅ **Anti-Bot Detection** - Bot tespitini önleyici teknolojiler
- ✅ **Akıllı Hata Yönetimi** - Site hatalarını algılar ve yönetir
- ✅ **Toplu Tarama** - 1000-100000 arası tüm kodları tarar
- ✅ **Güvenli Çalışma** - Hatalı durumları yönetir, bot durdurmaz
- ✅ **İstatistik Takibi** - Başarılı/başarısız işlem sayısını tutar

## 🗄️ Çekilen Veriler

Her acenta için şu bilgileri toplar:
- 📄 **Belge No** - TÜRSAB belge numarası
- 🏢 **Acenta Adı** - Firma adı
- 📞 **Telefon** - İletişim telefonu
- 📠 **Faks** - Faks numarası
- 📧 **Email** - Email adresi
- 📍 **Adres** - Tam adres bilgisi
- 🏙️ **İlçe** - İlçe bilgisi
- 🌆 **Şehir** - Şehir bilgisi
- 🏛️ **BTK** - Bölgesel Turizm Komisyonu

## 🚀 Kurulum

### 1. Gereksinimler

- Python 3.8+
- PostgreSQL 12+
- Chrome Browser
- Git

### 2. Projeyi İndirin

```bash
git clone https://github.com/veliardabalci/tursab-bot.git
cd tursab-bot
```

### 3. Paketleri Yükleyin

```bash
pip install -r requirements.txt
```

## 📖 Kullanım

### Basit Kullanım

```bash
python3 tursab_bot.py
```

Bot otomatik olarak:
1. PostgreSQL'e bağlanır
2. TÜRSAB sitesini açar
3. 1000-100000 arası kodları tarar
4. Bulunan acentaları database'e kaydeder

### Manuel Database Bağlantısı

```python
from tursab_bot import TursabBot

# Özel database URL ile
db_url = "postgresql://user:password@localhost:5432/tursab"
bot = TursabBot(db_url)

# Tek acenta arama
bot.open_site()
if bot.search_agency("1001"):
    agencies = bot.extract_agency_data()
    bot.display_agency_data(agencies)
    bot.clear_results()

bot.close()
```

## 🗄️ Database Yapısı

### `agencies` Tablosu

| Sütun | Tip | Açıklama |
|-------|-----|----------|
| `id` | INTEGER | Primary Key (Auto) |
| `belge_no` | VARCHAR(20) | TÜRSAB Belge No |
| `acenta_adi` | VARCHAR(255) | Acenta Adı |
| `telefon` | VARCHAR(50) | Telefon |
| `faks` | VARCHAR(50) | Faks |
| `email` | VARCHAR(100) | Email |
| `adres` | TEXT | Adres |
| `ilce` | VARCHAR(100) | İlçe |
| `sehir` | VARCHAR(100) | Şehir |
| `btk` | VARCHAR(100) | BTK |
| `created_at` | DATETIME | Oluşturma Tarihi |

## ⚙️ Konfigürasyon

### Database Ayarları

Default bağlantı bilgileri (`tursab_bot.py` içinde):
```python
db_url = "postgresql://postgres:postgres@localhost:5432/tursab"
```

### Bot Ayarları

```python
# Tarama aralığı
for i in range(1000, 100000):  # 1000'den 100000'e kadar

# Aramalar arası bekleme süresi
time.sleep(random.uniform(1, 3))  # 1-3 saniye

# Ardışık başarısızlık limiti
if consecutive_failures >= 50:  # 50 başarısızlıkta mola ver
```

## 🛠️ Troubleshooting

### Chrome Driver Hatası
```bash
OSError: [Errno 8] Exec format error
```
**Çözüm:** Chrome browser'ın yüklü olduğundan emin olun:
```bash
# macOS
brew install --cask google-chrome

# Ubuntu
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo apt update
sudo apt install google-chrome-stable
```

### Database Bağlantı Hatası
```bash
Database bağlantı hatası: connection refused
```
**Çözüm:** PostgreSQL'in çalıştığından emin olun:

### Element Bulunamadı Hatası
```bash
Element bulunamadı
```
**Çözüm:** TÜRSAB sitesi değişmiş olabilir. Site yapısını kontrol edin.

## 📊 Çıktı Örneği

```
🔗 Database bağlantısı kuruluyor...
✅ Database bağlantısı başarılı
🚀 Acenta taraması başlıyor...
============================================================

🔍 1001 numaralı acenta aranıyor...
✅ 1 acenta bulundu

================================================================================
ACENTA BİLGİLERİ
================================================================================

--- ACENTA 1 ---
📄 Belge No: 1001
🏢 Acenta Adı: ÖRNEK TURİZM SEYAHAT ACENTASI
📞 Telefon: +90 212 123 45 67
📧 Email: info@ornek.com
📍 Adres: ÖRNEK MAH. ÖRNEK CAD. NO:1 ŞIŞLI / İSTANBUL
🏙️ İlçe: ŞİŞLİ
🌆 Şehir: İSTANBUL
🏛️ BTK: İSTANBUL

✅ Eklendi: ÖRNEK TURİZM SEYAHAT ACENTASI
💾 1 adet kayıt veritabanına kaydedildi
💾 1 kayıt veritabanına kaydedildi
📊 Başarılı: 1, Başarısız: 0
----------------------------------------
```
### Test Etme

```python
# Tek acenta test
bot = TursabBot()
bot.open_site()
agencies = bot.search_agency("1001")
print(agencies)
```


## ⚠️ Yasal Uyarı

Bu bot eğitim amaçlıdır. TÜRSAB sitesinin kullanım koşullarına uygun olarak kullanın.

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📞 İletişim

Sorularınız için issue açabilirsiniz.
