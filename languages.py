# languages.py
# Bu dosya, uygulama için farklı dillerdeki metinleri .lang dosyalarından yükler.

import os
import configparser

# Desteklenen diller ve karşılık gelen .lang dosya yolları
# .lang dosyalarının 'lang' alt dizininde olduğunu belirtiyoruz.
LANGUAGES = {
    "English🇺🇸": "lang/eng.lang", # Yol güncellendi
    "Türkçe🇹🇷": "lang/tr.lang"   # Yol güncellendi
}

# Varsayılan dil
# BU SATIRIN languages.py DOSYANIZDA OLDUĞUNDAN EMİN OLUN.
DEFAULT_LANGUAGE = "English🇺🇸"

# Yüklenmiş metinleri önbelleğe almak için sözlük
_language_cache = {}

def load_language_strings(file_path):
    """Belirtilen .lang dosyasından metinleri yükler."""
    strings = {}
    # Dosya yolunun var olup olmadığını kontrol et
    if not os.path.exists(file_path):
        print(f"Uyarı: Dil dosyası bulunamadı: {file_path}")
        return strings # Dosya yoksa boş sözlük döndür

    # configparser kullanarak key=value formatını oku
    # Basit ayrıştırma yöntemi
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue # Boş satırları ve yorumları atla
                if '=' in line:
                    key, value = line.split('=', 1)
                    strings[key.strip()] = value.strip()
    except Exception as e:
        print(f"Hata: Dil dosyası '{file_path}' okunurken bir hata oluştu: {e}")
        return {} # Hata durumunda boş sözlük döndür

    return strings

def get_strings(language_key):
    """
    Seçilen dile ait metin sözlüğünü döndürür.
    Metinler önbelleğe alınır.
    """
    # languages.LANGUAGES sözlüğünün yüklendiğinden emin ol
    if not LANGUAGES:
         print("Hata: LANGUAGES sözlüğü languages.py içinde tanımlı değil veya boş.")
         return {} # LANGUAGES tanımlı değilse veya boşsa boş sözlük döndür

    if language_key not in LANGUAGES:
        print(f"Uyarı: Desteklenmeyen dil anahtarı '{language_key}'. Varsayılan dil kullanılıyor.")
        # DEFAULT_LANGUAGE'a erişmeden önce tanımlı olduğunu kontrol et
        if 'DEFAULT_LANGUAGE' in globals():
            language_key = DEFAULT_LANGUAGE
        else:
             print("Hata: DEFAULT_LANGUAGE languages.py içinde tanımlı değil.")
             return {} # DEFAULT_LANGUAGE tanımlı değilse boş sözlük döndür


    # Önbellekte varsa önbellekten döndür
    if language_key in _language_cache:
        return _language_cache[language_key]

    # Dosya yolunu al
    file_path = LANGUAGES[language_key]

    # Metinleri yükle
    strings = load_language_strings(file_path)

    # Yüklenen metinleri önbelleğe al
    _language_cache[language_key] = strings

    return strings

# Uygulama başladığında varsayılan dili yükle (isteğe bağlı ama iyi bir başlangıç)
# Bu satır, ilk çalıştırmada DEFAULT_LANGUAGE'ın yüklenmesini sağlar.
# DEFAULT_LANGUAGE'ın tanımlı olduğunu kontrol ederek daha güvenli hale getirelim.
if 'DEFAULT_LANGUAGE' in globals():
    get_strings(DEFAULT_LANGUAGE)
else:
    print("Hata: languages.py içinde DEFAULT_LANGUAGE tanımlı değil. Varsayılan dil yüklenemedi.")

