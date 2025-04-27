# Album Poster Creater - Core Logic
# Made by Elliot Jarnit
# Refactored for use as a module

import os
import sys
import re
import math
import warnings
import json # JSON işlemleri için gerekli
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO # Gerekirse BytesIO için

# Fonksiyonların dışarıdan erişilebilir olması için gerekli importlar (PIL, vs.)
# Ancak Streamlit tarafında da Pillow yüklü olmalı.

warnings.filterwarnings("ignore", category=DeprecationWarning)

def resource_path(relative_path):
    """Kaynak dosyalarının mutlak yolunu alır."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    # Font klasörünün resource_path içinde olduğundan emin olun
    # Örneğin, 'fonts' klasörünüz betikle aynı dizindeyse, bu doğru olacaktır.
    # Eğer farklı bir yerdeyse, bu fonksiyonu veya font yollarını ayarlamanız gerekebilir.
    return os.path.join(base_path, relative_path)

def read_local_json(uploaded_file):
    """Yüklenen bir Streamlit dosyasını okur ve JSON olarak ayrıştırır."""
    try:
        # Streamlit UploadedFile nesnesini kullanarak dosyayı oku
        data = json.load(uploaded_file)
        return data
    except json.JSONDecodeError:
        print("Hata: Yüklenen dosya geçerli bir JSON dosyası değil.") # Loglama için print
        return None
    except Exception as e:
        print(f"Yüklenen dosya okunurken bir hata oluştu: {e}") # Loglama için print
        return None

def get_colors(img):
    """Bir resimden baskın renkleri alır."""
    try:
        if img.mode != 'RGB':
            img = img.convert('RGB')

        paletted = img.convert('P', palette=Image.ADAPTIVE, colors=10)
        palette = paletted.getpalette()
        color_counts = sorted(paletted.getcolors(), reverse=True)
        colors = list()
        for i in range(min(len(color_counts), 5)):
            palette_index = color_counts[i][1]
            dominant_color = palette[palette_index * 3:palette_index * 3 + 3]
            colors.append(tuple(dominant_color))
    except Exception as e:
        print(f"Baskın renkler alınırken hata: {e}") # Loglama için print kullanılabilir
        colors = [(0, 0, 0)]
    return colors

def remove_featured(track_name):
    """Parantez içindeki öne çıkan sanatçı bilgilerini parça adından kaldırır."""
    if not isinstance(track_name, str):
        return track_name
    return re.sub(r'\s*\(.*?\)\s*', '', track_name).strip()

def format_time(duration_ms):
    """Parça süresini milisaniyeden M:SS dizesine biçimlendirir."""
    if duration_ms is None:
        return "N/A"
    try:
        duration_ms = int(duration_ms)
        seconds = (duration_ms // 1000) % 60
        minutes = (duration_ms // (1000 * 60)) % 60
        return f"{minutes}:{seconds:02d}"
    except (ValueError, TypeError):
        return "N/A"

# Font Seçenekleri (Çizim mantığına ait olduğu için burada kalabilir)
fonts = {
    "albumname": "VeryBold",
    "albumartist": "SemiBold",
    "tracklist": "SemiBold",
    "copyright": "Light"
}

# Ana poster oluşturma fonksiyonu
# Bu fonksiyon, albüm verilerini, albüm kapağı resmini (PIL Image nesnesi olarak)
# ve GUI'den gelen seçenekleri alacak.
def create_album_poster(album_data, albumart_image, options):
    """
    Creates an album poster image based on provided data and options.

    Args:
        album_data (dict): Dictionary containing album information (name, artist, tracks, etc.).
        albumart_image (PIL.Image.Image or None): The album artwork image object, or None.
        options (dict): Dictionary containing poster creation options:
            - 'poster_size' (str): "A4", "A3", or "A2".
            - 'tracks_per_column' (int): Number of tracks to display per column.
            - 'tracklist_font_size_search_range' (tuple): (min_size, max_size) for tracklist font.
            - 'include_copyright' (bool): Whether to include copyright info.
            - 'copyright_bottom_padding_px' (int): Padding from the bottom for copyright.
            - 'tracklist_horizontal_offset' (int): Horizontal offset for the tracklist start position.

    Returns:
        PIL.Image.Image or None: The created poster image object, or None if creation fails.
    """
    if not album_data:
        print("Poster oluşturmak için albüm verisi sağlanmadı.")
        return None

    # Seçenekleri al
    poster_size_key = options.get('poster_size', 'A4')
    tracks_per_column = options.get('tracks_per_column', 6)
    tracklist_font_size_search_range = options.get('tracklist_font_size_search_range', (10, 20))
    include_copyright = options.get('include_copyright', True)
    copyright_bottom_padding_px = options.get('copyright_bottom_padding_px', 20)
    tracklist_horizontal_offset = options.get('tracklist_horizontal_offset', 0) # Yeni seçenek, varsayılan 0

    size_presets = {
        "A4": (720, 960),
        "A3": (1024, 1365),
        "A2": (1440, 1920),
    }

    poster_width, poster_height = size_presets.get(poster_size_key, size_presets["A4"])
    scale_factor = poster_width / 720 # 720 A4'e göre ölçeklendirme

    # Ölçeklendirilmiş boşluk değerleri
    scaled_column_spacing = int(40 * scale_factor)
    scaled_name_time_spacing = int(25 * scale_factor)
    scaled_copyright_bottom_padding = int(copyright_bottom_padding_px * scale_factor)
    scaled_copyright_right_padding = int(60 * scale_factor)

    # Albüm verilerini çıkar
    album_name = album_data.get("name", "Bilinmeyen Albüm")
    album_artist = album_data.get("artist", "Bilinmeyen Sanatçı") # GUI'den formatlanmış gelecek
    album_copyright = album_data.get("copyright", "Telif Hakkı Bilgisi Yok") # GUI'den formatlanmış gelecek
    tracks_list = album_data.get("tracks", []) # GUI'den formatlanmış gelecek


    poster = Image.new("RGB", (poster_width, poster_height), color=(255, 255, 255))
    posterdraw = ImageDraw.Draw(poster)

    # Albüm kapağını yapıştır
    if albumart_image:
        try:
            # Gelen resmin doğru boyutta olduğundan emin ol (GUI'de boyutlandırıldı)
            # Eğer GUI'de boyutlandırılmadıysa burada boyutlandırılabilir:
            # albumart_image_resized = albumart_image.resize((int(600 * scale_factor), int(600 * scale_factor)))
            poster.paste(albumart_image, (int(60 * scale_factor), int(60 * scale_factor)))
        except Exception as e:
            print(f"Albüm kapağı yapıştırılırken hata: {e}")


    # Çizgi ayırıcıyı çiz
    posterdraw.rectangle([int(60 * scale_factor), int(740 * scale_factor), int(660 * scale_factor), int(745 * scale_factor)], fill=(0, 0, 0))

    # Fontları yükle
    font_name_path = resource_path('fonts/' + fonts["albumname"].lower() + '.otf')
    font_artist_path = resource_path('fonts/' + fonts["albumartist"].lower() + '.otf')
    tracklist_font_path_base = fonts["tracklist"].lower().replace(" ", "")
    tracklist_font_path = resource_path(f'fonts/{tracklist_font_path_base}.otf')
    font_copyright_path = resource_path('fonts/' + fonts["copyright"].lower() + '.otf')

    # Albüm adı fontu
    cursize_name = int(55 * scale_factor)
    font_name = None
    if os.path.exists(font_name_path):
        try:
            font_name = ImageFont.truetype(font_name_path, cursize_name)
            # Albüm adı uzunsa boyutu ayarla
            uzunluk_siniri = 14
            if len(album_name) > uzunluk_siniri:
                 try:
                     length_name_piksel = font_name.getlength(album_name)
                     while length_name_piksel > int(400 * scale_factor):
                         cursize_name -= 1
                         if cursize_name <= int(10 * scale_factor):
                             break
                         font_name = ImageFont.truetype(font_name_path, cursize_name)
                         length_name_piksel = font_name.getlength(album_name)
                 except Exception as e:
                     print(f"Albüm adı font boyutu ayarlanırken hata: {e}. Varsayılan boyut kullanılıyor.")
                     cursize_name = int(30 * scale_factor)
                     try:
                          font_name = ImageFont.truetype(font_name_path, cursize_name)
                     except:
                          print(f"'{font_name_path}' fontu varsayılan boyutla yüklenemedi. Varsayılana dönülüyor.")
                          font_name = ImageFont.load_default()

        except Exception as e:
            print(f"Albüm adı fontu '{font_name_path}' yüklenirken hata: {e}. Varsayılana dönülüyor.")
            font_name = ImageFont.load_default()
    else:
        print(f"Albüm adı fontu '{font_name_path}' bulunamadı. Varsayılana dönülüyor.")
        font_name = ImageFont.load_default()


    # Sanatçı fontu
    font_artist = None
    if os.path.exists(font_artist_path):
        try:
             font_artist = ImageFont.truetype(font_artist_path, int(25 * scale_factor))
        except Exception as e:
            print(f"Sanatçı fontu '{font_artist_path}' yüklenirken hata: {e}. Varsayılana dönülüyor.")
            font_artist = ImageFont.load_default()
    else:
         print(f"Sanatçı fontu '{font_artist_path}' bulunamadı. Varsayılana dönülüyor.")
         font_artist = ImageFont.load_default()

    # Telif hakkı fontu
    font_copyright = None
    if os.path.exists(font_copyright_path):
        try:
            font_copyright = ImageFont.truetype(font_copyright_path, int(10 * scale_factor))
        except Exception as e:
             print(f"Telif hakkı fontu '{font_copyright_path}' yüklenirken hata: {e}. Varsayılana dönülüyor.")
             font_copyright = ImageFont.load_default()
    else:
         print(f"Telif hakkı fontu '{font_copyright_path}' bulunamadı. Varsayılana dönülüyor.")
         font_copyright = ImageFont.load_default()


    # Tracklist font boyutu hesaplama ve font yükleme
    total_tracks_count = len(tracks_list)
    bestsize = 0
    font_tracks = None
    font_times = None

    if total_tracks_count == 0:
         print("Tracklist'te görüntülenecek parça yok.")
         # Parça yoksa varsayılan veya yedek font/boyut ayarla
         if os.path.exists(tracklist_font_path):
             try:
                 bestsize = max(1, tracklist_font_size_search_range[0])
                 font_tracks = ImageFont.truetype(tracklist_font_path, int(bestsize * scale_factor))
                 font_times = ImageFont.truetype(tracklist_font_path, int(bestsize * scale_factor))
             except Exception as e:
                 print(f"Boş tracklist için tracklist fontu yüklenirken hata (min boyut): {e}. Varsayılana dönülüyor.")
                 font_tracks = ImageFont.load_default()
                 font_times = ImageFont.load_default()
                 bestsize = 10
         else:
             print(f"Tracklist fontu '{tracklist_font_path}' bulunamadı. Boş tracklist için varsayılana dönülüyor.")
             font_tracks = ImageFont.load_default()
             font_times = ImageFont.load_default()
             bestsize = 10
    else:
        # Dinamik font boyutlandırma
        available_vertical_space = int(920 * scale_factor) - int(775 * scale_factor)
        min_size_to_try = max(1, tracklist_font_size_search_range[0])
        max_size_to_try = tracklist_font_size_search_range[1]

        bestsize = 0

        if not os.path.exists(tracklist_font_path):
             print(f"Tracklist fontu '{tracklist_font_path}' bulunamadı. Boyutlandırma için varsayılana dönülüyor.")
             font_tracks_test = ImageFont.load_default()
             bestsize = 10
             try:
                  _, top, _, bottom = font_tracks_test.getbbox("AgjypQ")
                  line_height_estimate = bottom - top + int(bestsize * scale_factor) * 0.8
             except:
                  line_height_estimate = int(bestsize * scale_factor) * 1.8
        else:
            for cursize_tracks in range(max_size_to_try, min_size_to_try -1, -1):
                 try:
                     font_tracks_test = ImageFont.truetype(tracklist_font_path, int(cursize_tracks * scale_factor))
                     _, top, _, bottom = font_tracks_test.getbbox("AgjypQ")
                     temp_line_height = bottom - top + int(cursize_tracks * scale_factor) * 0.8
                     vertical_space_this_size = tracks_per_column * temp_line_height

                     if vertical_space_this_size <= available_vertical_space * 1.05:
                         font_times_test_current_size = ImageFont.truetype(tracklist_font_path, int(cursize_tracks * scale_factor))
                         max_name_width_overall_for_size = 0
                         for track_info in tracks_list:
                             # Adapt based on expected keys from different JSON structures
                             if 'track' in track_info and isinstance(track_info['track'], dict): # For 'rip.json' structure
                                 track_name = track_info['track'].get('name', 'Unknown Track Name')
                             else: # For 'spotify.json' structure (or direct track list)
                                 track_name = track_info.get('name', 'Unknown Track Name')
                             display_track_name = remove_featured(track_name)
                             try:
                                 max_name_width_overall_for_size = max(max_name_width_overall_for_size, font_tracks_test.getlength(display_track_name))
                             except:
                                 max_name_width_overall_for_size = max(max_name_width_overall_for_size, len(display_track_name) * int(cursize_tracks * scale_factor) * 0.6)

                         max_time_width_for_spacing = 0
                         try:
                             max_time_width_for_spacing = font_times_test_current_size.getlength("00:00")
                         except:
                             max_time_width_for_spacing = int(cursize_tracks * scale_factor) * 3

                         estimated_columns = math.ceil(total_tracks_count / (tracks_per_column if tracks_per_column > 0 else 1))
                         if total_tracks_count > 0 and estimated_columns <= 0:
                             estimated_columns = 1

                         estimated_total_horizontal_width = (max_name_width_overall_for_size + scaled_name_time_spacing + max_time_width_for_spacing) * estimated_columns + scaled_column_spacing * max(0, estimated_columns - 1)
                         available_horizontal_space = int(720 * scale_factor) - int(60 * scale_factor) - int(60 * scale_factor)

                         if estimated_total_horizontal_width <= available_horizontal_space * 1.05:
                             bestsize = cursize_tracks
                             break
                 except Exception as e:
                     # print(f"Boyutlandırma sırasında font veya metrik hesaplama hatası (boyut {cursize_tracks}): {e}. Aramaya devam ediliyor.")
                     continue

            if bestsize == 0:
                 print("Belirtilen aralıkta istenen kolon başına parça sayısına dikey ve yatay olarak uyan uygun bir font boyutu bulunamadı. Varsayılan boyut kullanılıyor.")
                 bestsize = 10

        # Nihai tracklist fontlarını yükle
        if os.path.exists(tracklist_font_path):
            try:
                font_tracks = ImageFont.truetype(tracklist_font_path, int(bestsize * scale_factor))
                font_times = ImageFont.truetype(tracklist_font_path, int(bestsize * scale_factor))
            except Exception as e:
                print(f"Nihai tracklist fontu '{tracklist_font_path}' yüklenirken hata: {e}. Varsayılana dönülüyor.")
                font_tracks = ImageFont.load_default()
                font_times = ImageFont.load_default()
        else:
            print(f"Tracklist fontu '{tracklist_font_path}' bulunamadı. Varsayılana dönülüyor.")
            font_tracks = ImageFont.load_default()
            font_times = ImageFont.load_default()

    # Nihai fontlarla satır yüksekliği ve maksimum zaman genişliğini yeniden hesapla
    line_height_estimate = 0
    max_time_width = 0

    try:
        if font_tracks and hasattr(font_tracks, 'getbbox'):
            _, top, _, bottom = font_tracks.getbbox("AgjypQ")
            vertical_line_spacing = int(bestsize * scale_factor) * 0.8
            line_height_estimate = bottom - top + vertical_line_spacing
        else:
             line_height_estimate = int(bestsize * scale_factor) * 1.8
    except Exception as e:
        print(f"Çizim için satır yüksekliği tahmini yeniden hesaplanırken hata: {e}. Önceki tahmin kullanılıyor.")

    try:
        if font_times and hasattr(font_times, 'getlength'):
             max_time_width = font_times.getlength("00:00")
        else:
             max_time_width = int(bestsize * scale_factor) * 3
    except Exception as e:
        print(f"Çizim için maksimum zaman genişliği tahmini yeniden hesaplanırken hata: {e}. Önceki tahmin kullanılıyor.")


    # --- DİNAMİK KOLONLU TRACKLİST ÇİZİMİ ---
    # Başlangıç X koordinatına yatay ofseti ekle
    start_x = int(60 * scale_factor) + tracklist_horizontal_offset
    start_y = int(775 * scale_factor)

    cur_x = start_x
    tracks_to_process = list(tracks_list)
    current_column = 0

    if not tracks_list:
        print("Çizilecek parça yok.")
    else:
        linesoftracks_for_drawing = tracks_per_column
        if linesoftracks_for_drawing <= 0:
             linesoftracks_for_drawing = 1
             print("Kolon başına parça sayısı 0 veya daha az olarak ayarlanmıştı. 1 parça/kolon kullanılıyor.")

        while tracks_to_process:
            column_tracks_data = []
            max_name_width_in_current_column = 0
            tracks_for_this_column = tracks_to_process[:min(linesoftracks_for_drawing, len(tracks_to_process))]

            if not tracks_for_this_column:
                break

            # --- 1. Geçiş: Mevcut kolon için verileri topla ve maksimum isim genişliğini bul ---
            for track_info in tracks_for_this_column:
                # Adapt based on expected keys from different JSON structures
                if 'track' in track_info and isinstance(track_info['track'], dict): # For 'rip.json' structure
                    track_name = track_info['track'].get('name', 'Unknown Track Name')
                    duration_ms = track_info['track'].get('duration_ms')
                else: # For 'spotify.json' structure (or direct track list)
                    track_name = track_info.get('name', 'Unknown Track Name')
                    duration_ms = track_info.get('duration_ms')

                display_track_name = remove_featured(track_name)
                formatted_duration = format_time(duration_ms)

                try:
                    if font_tracks and hasattr(font_tracks, 'getlength'):
                         current_name_width = font_tracks.getlength(display_track_name)
                    else:
                         current_name_width = len(display_track_name) * int(bestsize * scale_factor) * 0.6
                except Exception as e:
                    print(f"Çizim geçişi sırasında parça adı '{display_track_name}' için genişlik alınırken hata: {e}. Tahmin ediliyor.")
                    current_name_width = len(display_track_name) * int(bestsize * scale_factor) * 0.6

                max_name_width_in_current_column = max(max_name_width_in_current_column, current_name_width)

                column_tracks_data.append({
                    "name": display_track_name,
                    "time": formatted_duration
                })

            # --- 2. Geçiş: Hesaplanan max_name_width kullanarak kolonu çiz ---
            for i, track_data in enumerate(column_tracks_data):
                text_y = start_y + i * line_height_estimate
                name_x = cur_x
                if font_tracks:
                     posterdraw.text((name_x, text_y), track_data["name"], font=font_tracks, fill=(0, 0, 0))

                time_x = cur_x + max_name_width_in_current_column + scaled_name_time_spacing
                if font_times:
                     posterdraw.text((time_x, text_y), track_data["time"], font=font_times, fill=(0, 0, 0))

            tracks_to_process = tracks_to_process[len(tracks_for_this_column):]
            column_drawn_width = max_name_width_in_current_column + scaled_name_time_spacing + max_time_width
            cur_x += column_drawn_width + scaled_column_spacing
            current_column += 1

    # --- Albüm Adı, Sanatçı ve Renkleri Çiz ---
    if font_name:
        posterdraw.text((int(65 * scale_factor), int(725 * scale_factor)),
                        album_name,
                        font=font_name,
                        fill=(0, 0, 0),
                        anchor='ls')
    else:
        print("Albüm adı fontu yüklenmedi, albüm adı çizilemiyor.")

    if albumart_image:
        domcolors = get_colors(albumart_image)
        x = int(660 * scale_factor)
        rectanglesize = int(30 * scale_factor)
        for i in domcolors:
            if isinstance(i, tuple) and len(i) == 3:
                posterdraw.rectangle([(x - rectanglesize, int(670 * scale_factor)), (x, int(670 * scale_factor) + rectanglesize)],
                                     fill=(i))
            x -= rectanglesize

    if font_artist:
        posterdraw.text((int(660 * scale_factor), int(725 * scale_factor)),
                        album_artist,
                        font=font_artist,
                        fill=(0, 0, 0),
                        anchor='rs')
    else:
         print("Sanatçı fontu yüklenmedi, albüm sanatçısı çizilemiyor.")

    # Telif hakkı metnini alta çiz
    if include_copyright and album_copyright and album_copyright != "Telif Hakkı Bilgisi Yok":
        try:
            if font_copyright and hasattr(font_copyright, 'getbbox'):
                _, top, _, bottom = font_copyright.getbbox(album_copyright)
                copyright_text_height = bottom - top
            else:
                copyright_text_height = int(10 * scale_factor) * 1.2

            copyright_y_position = poster_height - scaled_copyright_bottom_padding - copyright_text_height

            if font_copyright and hasattr(font_copyright, 'getlength'):
                copyright_width = font_copyright.getlength(album_copyright)
            else:
                copyright_width = len(album_copyright) * int(10 * scale_factor) * 0.6

            copyright_x_position = poster_width - scaled_copyright_right_padding - copyright_width

            posterdraw.text((copyright_x_position, copyright_y_position),
                            album_copyright,
                            font=font_copyright,
                            fill=(0, 0, 0))

        except Exception as e:
            print(f"Telif hakkı metni çizilirken hata: {e}")


    # Oluşturulan PIL Image nesnesini döndür
    return poster
