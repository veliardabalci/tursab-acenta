from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import os
from datetime import datetime

# Database imports
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Database configuration
Base = declarative_base()

class Agency(Base):
    """Acenta modeli"""
    __tablename__ = 'agencies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    belge_no = Column(String(20), nullable=True)
    acenta_adi = Column(String(255), nullable=True)
    telefon = Column(String(50), nullable=True)
    faks = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    adres = Column(Text, nullable=True)
    ilce = Column(String(100), nullable=True)
    sehir = Column(String(100), nullable=True)
    btk = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Agency(belge_no='{self.belge_no}', acenta_adi='{self.acenta_adi}')>"

class DatabaseManager:
    """Database yönetimi"""
    
    def __init__(self, db_url=None):
        if db_url is None:
            # Default PostgreSQL connection
            db_url = "postgresql://postgres:postgres@localhost:5432/tursab"
        
        try:
            self.engine = create_engine(db_url, echo=False)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.create_tables()
            self.connected = True
        except Exception as e:
            print(f"Database bağlantı hatası: {e}")
            self.connected = False
            raise
    
    def create_tables(self):
        """Tabloları oluştur"""
        try:
            Base.metadata.create_all(bind=self.engine)
            print("✅ Database tabloları hazır")
        except Exception as e:
            print(f"Database tablo oluşturma hatası: {e}")
            raise
    
    def get_session(self):
        """Database session'ı al"""
        if not self.connected:
            raise Exception("Database bağlantısı yok")
        return self.SessionLocal()
    
    def save_agencies(self, agencies_data):
        """Acenta verilerini kaydet"""
        if not self.connected:
            print("⚠️  Database bağlantısı yok")
            return 0
            
        if not agencies_data:
            print("Kaydedilecek veri yok")
            return 0
        
        session = self.get_session()
        saved_count = 0
        
        try:
            for agency_data in agencies_data:
                # Mevcut kaydı kontrol et
                existing = session.query(Agency).filter_by(belge_no=agency_data.get('belge_no')).first()
                
                if existing:
                    # Güncelle
                    for key, value in agency_data.items():
                        setattr(existing, key, value)
                    print(f"🔄 Güncellendi: {agency_data.get('acenta_adi', 'N/A')}")
                else:
                    # Yeni kayıt oluştur
                    agency = Agency(**agency_data)
                    session.add(agency)
                    print(f"✅ Eklendi: {agency_data.get('acenta_adi', 'N/A')}")
                
                saved_count += 1
            
            session.commit()
            print(f"💾 {saved_count} adet kayıt veritabanına kaydedildi")
            return saved_count
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database kayıt hatası: {e}")
            return 0
        finally:
            session.close()
    
    def get_all_agencies(self):
        """Tüm acentaları getir"""
        if not self.connected:
            return []
            
        session = self.get_session()
        try:
            agencies = session.query(Agency).all()
            return agencies
        except SQLAlchemyError as e:
            print(f"Database okuma hatası: {e}")
            return []
        finally:
            session.close()
    
    def get_agency_by_belge_no(self, belge_no):
        """Belge numarasıyla acenta getir"""
        if not self.connected:
            return None
            
        session = self.get_session()
        try:
            agency = session.query(Agency).filter_by(belge_no=belge_no).first()
            return agency
        except SQLAlchemyError as e:
            print(f"Database arama hatası: {e}")
            return None
        finally:
            session.close()

class TursabBot:
    def __init__(self, db_url=None):
        self.driver = None
        self.wait = None
        self.db_manager = DatabaseManager(db_url) if db_url else None
        self._setup_driver()
    
    def enable_database(self, db_url):
        """Database'i etkinleştir"""
        self.db_manager = DatabaseManager(db_url)
        print("✅ Database bağlantısı aktif")
    
    def _get_correct_chromedriver_path(self):
        """ChromeDriver path'ini düzelt"""
        driver_path = ChromeDriverManager().install()
        
        if 'THIRD_PARTY_NOTICES' in driver_path or driver_path.endswith('.chromedriver'):
            driver_dir = os.path.dirname(driver_path)
            if os.path.exists(driver_dir):
                files = os.listdir(driver_dir)
                for file in files:
                    if file == 'chromedriver' and not file.endswith('.chromedriver'):
                        correct_path = os.path.join(driver_dir, file)
                        os.chmod(correct_path, 0o755)
                        return correct_path
        
        if os.path.exists(driver_path) and not driver_path.endswith(('.txt', '.chromedriver')):
            os.chmod(driver_path, 0o755)
            return driver_path
            
        raise Exception("ChromeDriver bulunamadı")
    
    def _setup_driver(self):
        """WebDriver'ı kur ve yapılandır"""
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        correct_driver_path = self._get_correct_chromedriver_path()
        self.driver = webdriver.Chrome(service=Service(correct_driver_path), options=options)
        self.wait = WebDriverWait(self.driver, 20)
        
        # Anti-detection scriptleri
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_script("window.navigator.chrome = {runtime: {}};")
        self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});")
        self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});")
    
    def open_site(self):
        """TÜRSAB sitesini aç"""
        self.driver.get("https://www.tursab.org.tr/acenta-arama")
        time.sleep(random.uniform(3, 5))
    
    def find_tursab_input(self):
        """Farklı yöntemlerle TÜRSAB input'unu bul"""
        # Sayfa kaynağını kontrol et
        try:
            page_source = self.driver.page_source
            if "ContentPlaceHolder1_TursabNoText" in page_source:
                print("Element sayfa kaynağında mevcut")
            else:
                print("Element sayfa kaynağında bulunamadı")
        except Exception as e:
            print(f" Sayfa kontrolü hatası: {e}")
        
        # Frame kontrol et
        try:
            frames = self.driver.find_elements(By.TAG_NAME, "iframe")
            if frames:
                for i, frame in enumerate(frames):
                    self.driver.switch_to.frame(frame)
                    try:
                        element = self.driver.find_element(By.ID, "ContentPlaceHolder1_TursabNoText")
                        return element
                    except:
                        self.driver.switch_to.default_content()
                        continue
        except Exception as e:
            print(f" Frame kontrolü hatası: {e}")
        
        # Yöntem 1: ID ile
        try:
            element = self.wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TursabNoText")))
            return element
        except:
            print("ID ile bulunamadı")
        
        return None
    
    def search_agency(self, code):
        """Acenta ara"""
        print(f"🔍 {code} numaralı acenta aranıyor...")
        
        input_element = self.find_tursab_input()
        if not input_element:
            print("Input elementi bulunamadı")
            return False
        
        try:
            # Input'a tıkla ve temizle
            ActionChains(self.driver).move_to_element(input_element).click().perform()
            time.sleep(0.5)
            input_element.clear()
            time.sleep(0.2)
            
            # Kodu yaz
            for char in code:
                input_element.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            print(f"'{code}' başarıyla yazıldı!")
            
            # Arama yap
            search_button = self.driver.find_element(By.ID, "ContentPlaceHolder1_SearchButton")
            search_button.click()
            print("Arama butonuna tıklandı...")
            
            # Sonuçların yüklenmesi için bekle
            time.sleep(random.uniform(3, 5))
            
            return True
            
        except Exception as e:
            print(f"Arama işlemi hatası: {e}")
            return False
    
    def extract_agency_data(self):
        """Acenta verilerini çek"""
        try:
            # Önce hata mesajını kontrol et
            try:
                form_message_panel = self.driver.find_element(By.ID, "ContentPlaceHolder1_FormMessagePanel")
                if form_message_panel and form_message_panel.is_displayed():
                    # Hata mesajı var mı kontrol et
                    error_panels = form_message_panel.find_elements(By.CSS_SELECTOR, ".w3-panel.w3-pale-red")
                    for error_panel in error_panels:
                        error_text = error_panel.text.strip()
                        if "Arama kriterlerinize uygun sonuç bulunamamıştır" in error_text:
                            print("⚠️  Sonuç bulunamadı")
                            return []
                        elif "Hata" in error_text:
                            print(f"⚠️  Sistem hatası: {error_text}")
                            return []
            except:
                # FormMessagePanel yoksa devam et
                pass
            
            # Normal sonuç panelini kontrol et
            result_panel = self.wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ResultPanel")))
            
            # ResultPanel'in görünür olup olmadığını kontrol et
            if not result_panel.is_displayed():
                print("⚠️  Sonuç paneli görünmüyor")
                return []
            
            agency_containers = result_panel.find_elements(By.CLASS_NAME, "lit-container")
            
            if not agency_containers:
                print("⚠️  Acenta konteynerı bulunamadı")
                return []
            
            agencies = []
            
            for container in agency_containers:
                agency_data = self._parse_agency_container(container)
                if agency_data:
                    agencies.append(agency_data)
            
            if agencies:
                print(f"✅ {len(agencies)} acenta bulundu")
            else:
                print("⚠️  Parse edilebilir acenta bulunamadı")
            
            return agencies
            
        except Exception as e:
            print(f"Veri çekme hatası: {e}")
            return []
    
    def _parse_agency_container(self, container):
        """Tek acenta konteynerini analiz et"""
        try:
            agency = {}
            
            # Belge No
            belge_element = container.find_element(By.CSS_SELECTOR, ".w3-col.l1 .litc")
            agency['belge_no'] = belge_element.text.strip()
            
            # Acenta Adı
            acenta_element = container.find_element(By.CSS_SELECTOR, ".w3-col.l5 .litc")
            acenta_text = acenta_element.text.strip()
            agency['acenta_adi'] = acenta_text.replace("Acenta Adı : ", "").strip()
            
            # Telefon ve Faks
            telefon_element = container.find_element(By.CSS_SELECTOR, ".w3-col.l3 .litc")
            telefon_text = telefon_element.text.strip()
            agency['telefon'] = ""
            agency['faks'] = ""
            
            for line in telefon_text.split('\n'):
                if "Telefon : " in line:
                    agency['telefon'] = line.replace("Telefon : ", "").strip()
                elif "Faks : " in line:
                    agency['faks'] = line.replace("Faks : ", "").strip()
            
            # Email
            try:
                email_element = container.find_element(By.CSS_SELECTOR, ".w3-col.l3:last-child .litc")
                email_text = email_element.text.strip()
                agency['email'] = email_text.replace("Email : ", "").strip() if "Email : " in email_text else ""
            except:
                agency['email'] = ""
            
            # Adres ve Şehir
            try:
                adres_row = container.find_element(By.CSS_SELECTOR, ".w3-row:nth-child(2) .lit2")
                adres_text = adres_row.text.strip()
                agency['adres'] = adres_text.replace("Adres : ", "").strip()
                
                # İlçe ve Şehir
                bold_elements = adres_row.find_elements(By.TAG_NAME, "b")
                if len(bold_elements) >= 2:
                    agency['ilce'] = bold_elements[0].text.strip()
                    agency['sehir'] = bold_elements[1].text.strip()
                else:
                    agency['ilce'] = ""
                    agency['sehir'] = ""
            except:
                agency['adres'] = ""
                agency['ilce'] = ""
                agency['sehir'] = ""
            
            # BTK
            try:
                btk_row = container.find_element(By.CSS_SELECTOR, ".w3-row:nth-child(3) .lit2")
                btk_text = btk_row.text.strip()
                agency['btk'] = btk_text.replace("BTK :", "").strip() if "BTK :" in btk_text else ""
            except:
                agency['btk'] = ""
            
            return agency
            
        except Exception as e:
            print(f"Acenta verisi parse hatası: {e}")
            return None
    
    def save_to_database(self, agencies):
        """Verileri veritabanına kaydet"""
        if not self.db_manager:
            print("⚠️  Database bağlantısı aktif değil")
            return 0
        
        return self.db_manager.save_agencies(agencies)
    
    def display_agency_data(self, agencies):
        """Acenta verilerini göster"""
        if not agencies:
            print("Gösterilecek veri yok")
            return
        
        print("\n" + "="*80)
        print("ACENTA BİLGİLERİ")
        print("="*80)
        
        for i, agency in enumerate(agencies, 1):
            print(f"\n--- ACENTA {i} ---")
            print(f"📄 Belge No: {agency.get('belge_no', 'N/A')}")
            print(f"🏢 Acenta Adı: {agency.get('acenta_adi', 'N/A')}")
            print(f"📞 Telefon: {agency.get('telefon', 'N/A')}")
            print(f"📠 Faks: {agency.get('faks', 'N/A')}")
            print(f"📧 Email: {agency.get('email', 'N/A')}")
            print(f"📍 Adres: {agency.get('adres', 'N/A')}")
            print(f"🏙️ İlçe: {agency.get('ilce', 'N/A')}")
            print(f"🌆 Şehir: {agency.get('sehir', 'N/A')}")
            print(f"🏛️ BTK: {agency.get('btk', 'N/A')}")
        
        print("\n" + "="*80)
        
        # Database'e kaydet
        if self.db_manager:
            saved_count = self.save_to_database(agencies)
            print(f"💾 {saved_count} kayıt veritabanına kaydedildi")
    
    def clear_results(self):
        """Sonuçları temizle"""
        try:
            clear_button = self.driver.find_element(By.ID, "ContentPlaceHolder1_CleanButton")
            clear_button.click()
            print("Temizle butonuna tıklandı")
            time.sleep(1)
        except Exception as e:
            print(f"Temizleme hatası: {e}")
    
    def close(self):
        """Browser'ı kapat"""
        if self.driver:
            self.driver.quit()

def main():
    # Database URL'ini otomatik olarak ayarla
    db_url = "postgresql://postgres:postgres@localhost:5432/tursab"
    
    # Database ile bot oluştur
    print("🔗 Database bağlantısı kuruluyor...")
    
    try:
        bot = TursabBot(db_url)
        print("✅ Database bağlantısı başarılı")
    except Exception as e:
        print(f"⚠️  Database bağlantı hatası: {e}")
        print("🔄 Database olmadan devam ediliyor...")
        bot = TursabBot()
    
    try:
        bot.open_site()
        
        successful_searches = 0
        failed_searches = 0
        consecutive_failures = 0
        
        print("🚀 Acenta taraması başlıyor...")
        print("=" * 60)
        
        for i in range(1000, 100000):
            try:
                if bot.search_agency(str(i)):
                    agencies = bot.extract_agency_data()
                    
                    if agencies:
                        # Sonuç bulundu
                        bot.display_agency_data(agencies)
                        successful_searches += 1
                        consecutive_failures = 0
                        
                        print(f"📊 Başarılı: {successful_searches}, Başarısız: {failed_searches}")
                        print("-" * 40)
                        
                    else:
                        # Sonuç bulunamadı
                        failed_searches += 1
                        consecutive_failures += 1
                        
                        # Çok fazla ardışık başarısızlık varsa uyar
                        if consecutive_failures >= 50:
                            print(f"⚠️  {consecutive_failures} ardışık başarısızlık. Biraz bekleyip devam ediyorum...")
                            time.sleep(10)  # 10 saniye bekle
                            consecutive_failures = 0
                    
                    # Temizle ve bir sonraki arama için hazırlan
                    bot.clear_results()
                    
                    # Aramalar arası küçük mola
                    time.sleep(random.uniform(1, 3))
                    
                else:
                    print(f"❌ {i} numarası için arama yapılamadı")
                    failed_searches += 1
                    consecutive_failures += 1
                    
            except KeyboardInterrupt:
                print("\n\n⏹️  Kullanıcı tarafından durduruldu")
                break
                
            except Exception as e:
                print(f"❌ {i} numarası için hata: {e}")
                failed_searches += 1
                consecutive_failures += 1
                
                # Ciddi hata varsa biraz bekle
                time.sleep(5)
        
        print("\n" + "=" * 60)
        print("🏁 Tarama tamamlandı")
        print(f"📊 Toplam başarılı arama: {successful_searches}")
        print(f"📊 Toplam başarısız arama: {failed_searches}")
        
    except Exception as e:
        print(f"Ana işlem hatası: {e}")
    finally:
        bot.close()
        print("✅ Bot kapatıldı")

if __name__ == "__main__":
    main()
