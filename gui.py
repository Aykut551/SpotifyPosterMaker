import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import requests
import json
from io import BytesIO
import re # Dosya adını temizlemek için
from dotenv import load_dotenv # Ortam değişkenlerini yüklemek için
from PIL import Image # Image sınıfını doğrudan import et

# poster_core modülünü import et
import poster_core
# languages modülünü import et
import languages

# .env dosyasından ortam değişkenlerini yükle
load_dotenv()

# --- Streamlit GUI Başlangıcı ---

# Oturum durumu (session state) kullanarak dil seçimini sakla
# languages.DEFAULT_LANGUAGE'ı kullanmadan önce languages modülünün yüklendiğinden emin olmalıyız.
# Streamlit'in çalışma şekli gereği, bu importlar ve ilk atamalar her yeniden çalıştırmada gerçekleşir.
# Bu nedenle DEFAULT_LANGUAGE'a erişim burada genellikle sorunsuz olmalıdır.
if 'selected_language' not in st.session_state:
    st.session_state['selected_language'] = languages.DEFAULT_LANGUAGE

# Seçilen dile ait metinleri al (her yeniden çalıştırmada güncellenir)
# Bu çağrı languages.py içindeki get_strings fonksiyonunu çalıştırır ve metinleri yükler.
strings = languages.get_strings(st.session_state['selected_language'])

# Spotify API Bağlantısı (Dil metinleri yüklendikten sonra uyarıları kullanabiliriz)
sp = None
try:
    if os.environ.get("SPOTIPY_CLIENT_ID") and os.environ.get("SPOTIPY_CLIENT_SECRET"):
         sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    else:
         # API anahtarları ayarlanmamışsa uyarı göster (dil dosyasından al)
         # Burada strings sözlüğünün artık yüklü olduğunu varsayıyoruz.
         st.warning(strings["spotify_api_not_initialized_warning"])
except Exception as e:
    # Hata durumunda hata mesajını göster (dil dosyasından al)
    st.error(strings["spotify_api_init_error"].format(error_message=e))
    st.warning(strings["spotify_api_init_check"])
    sp = None


# Sidebar'a dil seçimi ekle
# strings sözlüğünü burada kullanmak güvenlidir çünkü yukarıda yüklendi.
st.sidebar.header(strings["poster_options_header"]) # Poster seçenekleri başlığını dil dosyasından alalım

# Dil seçimi için selectbox
selected_language_key = st.sidebar.selectbox(
    strings["data_source_label"], # Dil seçimi etiketi olarak veri kaynağı etiketini kullanıyoruz
    list(languages.LANGUAGES.keys()), # languages.LANGUAGES sözlüğünün anahtarlarını kullan
    index=list(languages.LANGUAGES.keys()).index(st.session_state['selected_language']), # Varsayılan veya kayıtlı dili seç
    key='language_select_box' # Oturum durumu anahtarı ekleyelim
)

# Dil seçimi değiştiğinde oturum durumunu güncelle ve sayfayı yeniden yükle
if selected_language_key != st.session_state['selected_language']:
    st.session_state['selected_language'] = selected_language_key
    st.rerun() # Dil değiştiğinde sayfayı yeniden yükle

# Seçilen dile ait metinleri al (yeniden yükleme sonrası güncel metinler)
# st.rerun() sonrası bu satır tekrar çalışır ve güncel dili yükler.
strings = languages.get_strings(st.session_state['selected_language'])


st.title(strings["app_title"])
st.markdown(strings["app_description"])

# Kullanıcı girdileri
data_source = st.radio(
    strings["data_source_label"],
    (strings["data_source_spotify"], strings["data_source_local_json"])
)

album_data_raw = None # Spotify veya JSON'dan gelen ham veri
album_data_processed = {} # Poster core'a gönderilecek işlenmiş veri
album_artwork_url = None # Spotify'dan gelen kapak URL'si

if data_source == strings["data_source_spotify"]: # Karşılaştırmayı metinle yap
    if sp is None:
        st.warning(strings["spotify_api_not_initialized_warning"])
    else:
        search_input = st.text_input(strings["search_input_label"])
        if search_input:
            try:
                with st.spinner(strings["searching_album"].format(search_term=search_input)):
                    results = sp.search(q=search_input, type='album', limit=10)
                    albums = results['albums']['items']

                if not albums:
                    st.warning(strings["no_album_found"].format(search_term=search_input))
                else:
                    st.subheader(strings["found_albums_subheader"])
                    album_choices = []
                    # Spotify API yanıtından gerekli bilgileri çıkar ve göster
                    for i, album in enumerate(albums):
                         artists = ", ".join([artist['name'] for artist in album['artists']])
                         release_year = album.get('release_date', '')[:4]
                         album_choices.append(f"{album['name']} by {artists} ({release_year})")

                    selected_album_choice = st.selectbox(strings["select_album_label"], album_choices)

                    if selected_album_choice:
                        selected_album_index = album_choices.index(selected_album_choice)
                        selected_album_id = albums[selected_album_index]['id']

                        with st.spinner(strings["fetching_album_info"]):
                            album_data_raw = sp.album(selected_album_id)

                        # Poster core'a göndermek için veriyi işle
                        if album_data_raw:
                            album_data_processed["name"] = album_data_raw.get("name", strings["album_data_unknown_album"]) # Varsayılan metni dil dosyasından al
                            if album_data_raw.get('artists'):
                                artist_names = [artist['name'] for artist in album_data_raw['artists'] if isinstance(artist, dict) and 'name' in artist]
                                album_data_processed["artist"] = ", ".join(artist_names) if artist_names else strings["album_data_unknown_artist"] # Varsayılan metni dil dosyasından al
                            else:
                                album_data_processed["artist"] = strings["album_data_unknown_artist"] # Varsayılan metni dil dosyasından al

                            if album_data_raw.get('copyrights'):
                                copyright_texts = [cp['text'] for cp in album_data_raw['copyrights'] if isinstance(cp, dict) and 'text' in cp]
                                album_data_processed["copyright"] = " | ".join(copyright_texts) if copyright_texts else strings["album_data_no_copyright"] # Varsayılan metni dil dosyasından al
                                album_data_processed["copyright"] = album_data_processed["copyright"].replace("℗", "(P)").replace("©", "(C)")
                            else:
                                album_data_processed["copyright"] = strings["album_data_no_copyright"] # Varsayılan metni dil dosyasından al

                            if album_data_raw.get('images'):
                                 if album_data_raw['images']:
                                     largest_image = album_data_raw['images'][0]
                                     album_artwork_url = largest_image.get('url') # Kapak URL'sini sakla
                            album_data_processed["tracks"] = album_data_raw.get('tracks', {}).get('items', []) # Parça listesini sakla

            except Exception as e:
                st.error(strings["search_or_select_error"].format(error_message=e)) # Hata mesajını dil dosyasından al

elif data_source == strings["data_source_local_json"]: # Karşılaştırmayı metinle yap
    # accept_multiple_files=False ekledik (varsayılan olsa da açıkça belirtildi)
    uploaded_json_file = st.file_uploader(strings["upload_json_label"], type=['json'], accept_multiple_files=False)
    if uploaded_json_file is not None:
        # poster_core.read_local_json fonksiyonunu kullan
        album_data_raw = poster_core.read_local_json(uploaded_json_file)

        if album_data_raw:
            st.success(strings["json_loaded_success"])

            # JSON yapısına göre verileri işle
            if 'tracks' in album_data_raw and 'items' in album_data_raw['tracks'] and album_data_raw['tracks']['items'] and 'track' in album_data_raw['tracks']['items'][0]:
                # Rip.json formatı gibi görünüyor
                album_data_processed["name"] = album_data_raw.get("name", strings["album_data_unknown_album"] + " (Rip JSON)") # Varsayılan metni dil dosyasından al
                if album_data_raw.get('owner') and album_data_raw['owner'].get('display_name'):
                     album_data_processed["artist"] = album_data_raw['owner']['display_name']
                else:
                    if album_data_raw.get('tracks') and album_data_raw['tracks'].get('items'):
                        if album_data_raw['tracks']['items'] and album_data_raw['tracks']['items'][0].get('track') and album_data_raw['tracks']['items'][0]['track'].get('artists'):
                             first_track_artists = [artist['name'] for artist in album_data_raw['tracks']['items'][0]['track']['artists'] if isinstance(artist, dict) and 'name' in artist]
                             album_data_processed["artist"] = ", ".join(first_track_artists) if first_track_artists else strings["album_data_unknown_artist"] # Varsayılan metni dil dosyasından al
                    else:
                         album_data_processed["artist"] = strings["album_data_unknown_artist"] # Varsayılan metni dil dosyasından al

                album_data_processed["copyright"] = strings["album_data_no_copyright"] # Varsayılan metni dil dosyasından al
                album_artwork_url = None
                album_data_processed["tracks"] = album_data_raw['tracks']['items']

            elif 'name' in album_data_raw and 'artists' in album_data_raw and 'tracks' in album_data_raw:
                 # Spotify API yanıt formatı gibi görünüyor
                 album_data_processed["name"] = album_data_raw.get("name", strings["album_data_unknown_album"] + " (Spotify JSON)") # Varsayılan metni dil dosyasından al
                 if album_data_raw.get('artists'):
                     artist_names = [artist['name'] for artist in album_data_raw['artists'] if isinstance(artist, dict) and 'name' in artist]
                     album_data_processed["artist"] = ", ".join(artist_names) if artist_names else strings["album_data_unknown_artist"] # Varsayılan metni dil dosyasından al
                 else:
                     album_data_processed["artist"] = strings["album_data_unknown_artist"] # Varsayılan metni dil dosyasından al

                 if album_data_raw.get('copyrights'):
                     copyright_texts = [cp['text'] for cp in album_data_raw['copyrights'] if isinstance(cp, dict) and 'text' in cp]
                     album_data_processed["copyright"] = " | ".join(copyright_texts) if copyright_texts else strings["album_data_no_copyright"] # Varsayılan metni dil dosyasından al
                     album_data_processed["copyright"] = album_data_processed["copyright"].replace("℗", "(P)").replace("©", "(C)")
                 else:
                     album_data_processed["copyright"] = strings["album_data_no_copyright"] # Varsayılan metni dil dosyasından al

                 if album_data_raw.get('images'):
                      if album_data_raw['images']:
                          largest_image = album_data_raw['images'][0]
                          album_artwork_url = largest_image.get('url')
                 album_data_processed["tracks"] = album_data_raw.get('tracks', {}).get('items', [])

            else:
                st.error(strings["json_format_unrecognized"]) # Hata mesajını dil dosyasından al
                album_data_raw = None
                album_data_processed = {}

        else:
            st.error(strings["json_load_error"]) # Hata mesajını dil dosyasından al


# Poster oluşturma seçenekleri
st.sidebar.header(strings["poster_options_header"])
poster_size = st.sidebar.selectbox(strings["poster_size_label"], ("A4", "A3", "A2"))

# Ölçeklendirme faktörü (seçilen boyuta göre hesaplanır)
size_presets_for_scaling = {
    "A4": (720, 960),
    "A3": (1024, 1365),
    "A2": (1440, 1920),
}
current_poster_width, _ = size_presets_for_scaling.get(poster_size, size_presets_for_scaling["A4"])
scale_factor_for_options = current_poster_width / 720

tracks_per_column = st.sidebar.slider(strings["tracks_per_column_label"], 1, 20, 6)
tracklist_font_size_min = st.sidebar.slider(strings["tracklist_font_size_min_label"], 5, 30, 10)
tracklist_font_size_max = st.sidebar.slider(strings["tracklist_font_size_max_label"], 10, 40, 20)
tracklist_font_size_search_range = (tracklist_font_size_min, tracklist_font_size_max)

# Tracklist yatay konum kaydırıcısı
max_horizontal_offset = int(current_poster_width / 2)
min_horizontal_offset = -int(current_poster_width / 2)

tracklist_horizontal_offset = st.sidebar.slider(
    strings["tracklist_horizontal_offset_label"],
    min_horizontal_offset,
    max_horizontal_offset,
    int(0)
)

include_copyright = st.sidebar.checkbox(strings["include_copyright_label"], value=True)
copyright_bottom_padding_px = st.sidebar.slider(strings["copyright_bottom_padding_label"], 0, 100, 20)


# Albüm kapağı kaynağı seçimi
image_source = st.radio(
    strings["image_source_label"],
    (strings["image_source_url"], strings["image_source_local_file"])
)
uploaded_image_file = None
albumart_image_for_core = None # Poster core'a gönderilecek PIL Image nesnesi

if image_source == strings["image_source_local_file"]: # Karşılaştırmayı metinle yap
    # accept_multiple_files=False ekledik (varsayılan olsa da açıkça belirtildi)
    uploaded_image_file = st.file_uploader(strings["upload_image_label"], type=['png', 'jpg', 'jpeg'], accept_multiple_files=False)
    if uploaded_image_file is not None:
        # PIL.Image.open kullanıyoruz
        try:
            albumart_image_for_core = Image.open(uploaded_image_file)
            if albumart_image_for_core:
                 # Poster core'a göndermeden önce boyutu ayarla
                 try:
                     albumart_image_for_core = albumart_image_for_core.resize((int(600 * scale_factor_for_options), int(600 * scale_factor_for_options)))
                 except Exception as e:
                     st.error(strings["local_image_resize_error"].format(error_message=e)) # Hata mesajını dil dosyasından al
                     albumart_image_for_core = None
            else:
                st.error(strings["local_image_load_error"]) # Hata mesajını dil dosyasından al
        except Exception as e:
             st.error(strings["local_image_load_error"].format(error_message=e)) # Hata mesajını dil dosyasından al
             albumart_image_for_core = None


# Poster Oluştur butonu
if st.button(strings["create_poster_button"]):
    if not album_data_processed:
        st.warning(strings["no_album_data_warning"]) # Uyarı mesajını dil dosyasından al
    else:
        with st.spinner(strings["creating_poster_spinner"]): # Spinner metnini dil dosyasından al
            # Eğer yerel resim yüklenmediyse ve URL varsa, URL'den indir
            if albumart_image_for_core is None and album_artwork_url:
                try:
                    response = requests.get(album_artwork_url)
                    response.raise_for_status()
                    # PIL.Image.open kullanıyoruz
                    img = Image.open(BytesIO(response.content))
                    # Poster core'a göndermeden önce boyutu ayarla
                    img_resized = img.resize((int(600 * scale_factor_for_options), int(600 * scale_factor_for_options)))
                    albumart_image_for_core = img_resized
                    st.success(strings["downloading_album_cover"]) # Başarı mesajını dil dosyasından al
                except requests.exceptions.RequestException as e:
                     st.warning(strings["album_cover_download_error"].format(error_message=e)) # Uyarı mesajını dil dosyasından al
                except Exception as e:
                     st.warning(strings["album_cover_process_error"].format(error_message=e)) # Uyarı mesajını dil dosyasından al

            if albumart_image_for_core is None:
                st.warning(strings["album_cover_not_found_warning"]) # Uyarı mesajını dil dosyasından al


            # Seçenekleri bir sözlükte topla
            poster_options = {
                'poster_size': poster_size,
                'tracks_per_column': tracks_per_column,
                'tracklist_font_size_search_range': tracklist_font_size_search_range,
                'include_copyright': include_copyright,
                'copyright_bottom_padding_px': copyright_bottom_padding_px,
                'tracklist_horizontal_offset': tracklist_horizontal_offset # Yeni eklenen seçenek
            }

            # poster_core'daki fonksiyonu çağır
            created_poster_image = poster_core.create_album_poster(
                album_data_processed,
                albumart_image_for_core,
                poster_options
            )

            if created_poster_image:
                # use_column_width yerine use_container_width kullan
                st.image(created_poster_image, caption=f"{album_data_processed.get('name', strings['album_data_unknown_album'])} Posteri", use_container_width=True) # Albüm adını ve varsayılanı dil dosyasından al

                # Posteri indirme butonu
                buf = BytesIO()
                created_poster_image.save(buf, format="PNG")
                byte_im = buf.getvalue()
                # Dosya adını albüm adına göre temizle
                safe_album_name = re.sub(r'[^\w\-_\. ]', '', album_data_processed.get('name', 'album_poster')).replace(' ', '_')
                st.download_button(
                    label=strings["download_poster_button"], # Buton metnini dil dosyasından al
                    data=byte_im,
                    file_name=f"{safe_album_name}_poster.png",
                    mime="image/png"
                )

                st.success(strings["poster_created_success"]) # Başarı mesajını dil dosyasından al
                # İsteğe bağlı olarak font boyutu bilgisini göster
                # Best size bilgisi poster_core içinde hesaplanıyor, bunu döndürmek veya ayrı loglamak gerekebilir
                # Şimdilik bu bilgiyi GUI'de göstermiyoruz.
            else:
                st.error(strings["poster_creation_error"]) # Hata mesajını dil dosyasından al

