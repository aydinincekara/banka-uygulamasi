import streamlit as st
import pandas as pd
import random
from datetime import datetime, date

# Sayfa Yapılandırması (Geniş masaüstü görünümü)
st.set_page_config(page_title="Banka Yönetim Sistemi", layout="wide", page_icon="🏦")

# 1. OTURUM DURUMU (SESSION STATE) İLKELENMESİ (RAM Üzerinde Veri Saklama)
if "musteriler" not in st.session_state:
    st.session_state.musteriler = [
        {
            "kimlik_no": "11111111111",
            "ad_soyad": "Ahmet Yılmaz",
            "iletisim": "05551112233",
            "hesaplar": [
                {
                    "hesap_no": "TR100001",
                    "tur": "Vadesiz",
                    "bakiye": 5000.0,
                    "islemler": [
                        {"tarih": datetime.now(), "tur": "Para Yatırma", "tutar": 5000.0, "aciklama": "Hesap açılış bakiyesi"}
                    ]
                }
            ]
        },
        {
            "kimlik_no": "22222222222",
            "ad_soyad": "Ayşe Kaya",
            "iletisim": "05329998877",
            "hesaplar": [
                {
                    "hesap_no": "TR100002",
                    "tur": "Vadeli",
                    "bakiye": 2500.0,
                    "islemler": [
                        {"tarih": datetime.now(), "tur": "Para Yatırma", "tutar": 2500.0, "aciklama": "Hesap açılış bakiyesi"}
                    ]
                }
            ]
        }
    ]

# Yardımcı Fonksiyonlar
def musteri_bul(tc):
    return next((m for m in st.session_state.musteriler if m["kimlik_no"] == tc), None)

def tum_hesaplar():
    hesap_listesi = []
    for m in st.session_state.musteriler:
        for h in m["hesaplar"]:
            hesap_listesi.append({**h, "sahip": m["ad_soyad"], "tc": m["kimlik_no"]})
    return hesap_listesi

def hesap_bul(hesap_no):
    for m in st.session_state.musteriler:
        for h in m["hesaplar"]:
            if h["hesap_no"] == hesap_no:
                return h, m
    return None, None

# SOL YAN MENÜ (SIDEBAR)
st.sidebar.title("🏦 Banka Paneli")
sayfa = st.sidebar.radio(
    "Gezinti Menüsü",
    [
        "Müşteri Kayıt & Güncelleme",
        "Hesap Yönetimi",
        "Para İşlemleri (Yatırma/Çekme)",
        "Para Transferi",
        "Arama & İşlem Raporları"
    ]
)

st.title("🏦 Banka Uygulaması Yönetim Masası")

# --- 1. MÜŞTERİ KAYIT & GÜNCELLEME ---
if sayfa == "Müşteri Kayıt & Güncelleme":
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Yeni Müşteri Kaydı")
        with st.form("yeni_musteri_form"):
            tc = st.text_input("T.C. Kimlik No", max_chars=11)
            ad = st.text_input("Ad Soyad")
            iletisim = st.text_input("İletişim Bilgisi (Telefon/E-posta)")
            kaydet_btn = st.form_submit_button("Müşteriyi Kaydet")
            
            if kaydet_btn:
                if not tc or not ad:
                    st.error("T.C. Kimlik No ve Ad Soyad boş bırakılamaz!")
                elif musteri_bul(tc):
                    st.error("Bu T.C. Kimlik numarasıyla kayıtlı müşteri zaten var!")
                else:
                    st.session_state.musteriler.append({
                        "kimlik_no": tc,
                        "ad_soyad": ad,
                        "iletisim": iletisim,
                        "hesaplar": []
                    })
                    st.success(f"✅ {ad} başarıyla sisteme eklendi.")

    with col2:
        st.subheader("Müşteri Bilgileri Güncelleme")
        duzenle_aktif = st.checkbox("Bilgi Güncelleme Modunu Aç")
        if duzenle_aktif and st.session_state.musteriler:
            secilen_tc = st.selectbox("Güncellenecek Müşteri", [m["kimlik_no"] + " - " + m["ad_soyad"] for m in st.session_state.musteriler])
            tc_no = secilen_tc.split(" - ")[0]
            m_obj = musteri_bul(tc_no)
            
            yeni_ad = st.text_input("Ad Soyad", value=m_obj["ad_soyad"])
            yeni_iletisim = st.text_input("İletişim", value=m_obj["iletisim"])
            
            if st.button("Bilgileri Güncelle", type="primary"):
                m_obj["ad_soyad"] = yeni_ad
                m_obj["iletisim"] = yeni_iletisim
                st.success("✅ Müşteri bilgileri güncellendi.")
                st.rerun()

# --- 2. HESAP YÖNETİMİ ---
elif sayfa == "Hesap Yönetimi":
    st.subheader("Müşteriye Özel Hesap Açılışı")
    if not st.session_state.musteriler:
        st.warning("Sistemde hesap açılabilecek müşteri bulunamadı.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            secilen_m = st.selectbox("Müşteri Seçin", [m["kimlik_no"] + " - " + m["ad_soyad"] for m in st.session_state.musteriler])
            hesap_turu = st.selectbox("Hesap Türü", ["Vadesiz", "Vadeli", "Döviz"])
            
            if st.button("Hesap Oluştur"):
                tc_no = secilen_m.split(" - ")[0]
                m_obj = musteri_bul(tc_no)
                yeni_hesap_no = f"TR{random.randint(100000, 999999)}"
                m_obj["hesaplar"].append({
                    "hesap_no": yeni_hesap_no,
                    "tur": hesap_turu,
                    "bakiye": 0.0,
                    "islemler": []
                })
                st.success(f"✅ {m_obj['ad_soyad']} adına {yeni_hesap_no} numaralı {hesap_turu} hesabı açıldı.")

    st.markdown("---")
    st.subheader("Sistemdeki Tüm Hesaplar")
    hesaplar_data = tum_hesaplar()
    if hesaplar_data:
        df_hesaplar = pd.DataFrame(hesaplar_data)[["hesap_no", "sahip", "tc", "tur", "bakiye"]]
        df_hesaplar.columns = ["Hesap No", "Müşteri Adı", "T.C. Kimlik No", "Hesap Türü", "Bakiye (TL)"]
        st.dataframe(df_hesaplar, use_container_width=True)

# --- 3. PARA İŞLEMLERİ ---
elif sayfa == "Para İşlemleri (Yatırma/Çekme)":
    st.subheader("Para Yatırma ve Çekme")
    hesaplar = tum_hesaplar()
    
    if not hesaplar:
        st.warning("İşlem yapılabilecek hesap bulunmuyor.")
    else:
        hesap_secim = st.selectbox("İşlem Yapılacak Hesap", [f"{h['hesap_no']} ({h['sahip']} - Bakiye: {h['bakiye']:.2f} TL)" for h in hesaplar])
        hesap_no = hesap_secim.split(" ")[0]
        h_obj, m_obj = hesap_bul(hesap_no)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mevcut Hesap Bakiyesi", f"{h_obj['bakiye']:.2f} TL")
            tutar = st.number_input("İşlem Tutarı (TL)", min_value=1.0, step=50.0)

        with col2:
            islem_tipi = st.radio("Yapılacak İşlem", ["Para Yatır", "Para Çek"])
            if st.button("İşlemi Onayla", type="primary"):
                if islem_tipi == "Para Yatır":
                    h_obj["bakiye"] += tutar
                    h_obj["islemler"].append({
                        "tarih": datetime.now(),
                        "tur": "Para Yatırma",
                        "tutar": tutar,
                        "aciklama": "Şube/ATM Yatırma"
                    })
                    st.success(f"✅ {tutar:.2f} TL yatırıldı. Yeni bakiye: {h_obj['bakiye']:.2f} TL")
                    st.rerun()
                else:
                    # Bakiye Kontrolü (Gereksinim 4)
                    if h_obj["bakiye"] >= tutar:
                        h_obj["bakiye"] -= tutar
                        h_obj["islemler"].append({
                            "tarih": datetime.now(),
                            "tur": "Para Çekme",
                            "tutar": tutar,
                            "aciklama": "Şube/ATM Çekme"
                        })
                        st.success(f"✅ {tutar:.2f} TL çekildi. Kalan bakiye: {h_obj['bakiye']:.2f} TL")
                        st.rerun()
                    else:
                        st.error("❌ Yetersiz Bakiye! İşlem gerçekleştirilemedi.")

# --- 4. PARA TRANSFERİ ---
elif sayfa == "Para Transferi":
    st.subheader("Hesaplar Arası Para Transferi")
    hesaplar = tum_hesaplar()
    
    if len(hesaplar) < 2:
        st.warning("Transfer yapabilmek için sistemde en az 2 hesap kayıtlı olmalıdır.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            gonderen_secim = st.selectbox("Gönderen Hesap", [f"{h['hesap_no']} ({h['sahip']} - Bakiye: {h['bakiye']:.2f} TL)" for h in hesaplar], key="gonderen")
        with col2:
            alici_liste = [h for h in hesaplar if h['hesap_no'] != gonderen_secim.split(" ")[0]]
            alici_secim = st.selectbox("Alıcı Hesap", [f"{h['hesap_no']} ({h['sahip']})" for h in alici_liste], key="alici")
        
        gonderen_no = gonderen_secim.split(" ")[0]
        alici_no = alici_secim.split(" ")[0]
        
        g_hesap, g_m = hesap_bul(gonderen_no)
        a_hesap, a_m = hesap_bul(alici_no)
        
        transfer_tutar = st.number_input("Transfer Tutarı (TL)", min_value=1.0, step=100.0)
        
        if st.button("Transferi Başlat", type="primary"):
            # Bakiye kontrolü (Gereksinim 4)
            if g_hesap["bakiye"] >= transfer_tutar:
                g_hesap["bakiye"] -= transfer_tutar
                a_hesap["bakiye"] += transfer_tutar
                
                # İşlem Logları Kaydı (Gereksinim 5)
                g_hesap["islemler"].append({
                    "tarih": datetime.now(),
                    "tur": "Transfer (Giden)",
                    "tutar": transfer_tutar,
                    "aciklama": f"Alıcı: {alici_no} ({a_m['ad_soyad']})"
                })
                a_hesap["islemler"].append({
                    "tarih": datetime.now(),
                    "tur": "Transfer (Gelen)",
                    "tutar": transfer_tutar,
                    "aciklama": f"Gönderen: {gonderen_no} ({g_m['ad_soyad']})"
                })
                st.success("✅ Transfer başarıyla gerçekleştirildi.")
                st.rerun()
            else:
                st.error("❌ Yetersiz Bakiye! Transfer başarısız.")

# --- 5. ARAMA VE İŞLEM RAPORLARI ---
elif sayfa == "Arama & İşlem Raporları":
    st.subheader("Arama ve Detaylı Raporlar")
    
    tab1, tab2 = st.tabs(["🔍 Müşteri / Hesap Arama", "📊 Hesap Hareket Raporları"])
    
    with tab1:
        arama_terimi = st.text_input("T.C. Kimlik No veya Hesap No Giriniz")
        if arama_terimi:
            m_sonuc = musteri_bul(arama_terimi)
            h_sonuc, m_sahip = hesap_bul(arama_terimi)
            
            if m_sonuc:
                st.success(f"Müşteri Bulundu: **{m_sonuc['ad_soyad']}** | İletişim: {m_sonuc['iletisim']}")
                if m_sonuc["hesaplar"]:
                    st.table(pd.DataFrame(m_sonuc["hesaplar"])[["hesap_no", "tur", "bakiye"]])
                else:
                    st.info("Bu müşterinin henüz hesabı bulunmuyor.")
            elif h_sonuc:
                st.success(f"Hesap Bulundu: **{h_sonuc['hesap_no']}** | Sahibi: {m_sahip['ad_soyad']} | Bakiye: {h_sonuc['bakiye']:.2f} TL")
            else:
                st.warning("Aranan bilgiyle eşleşen müşteri veya hesap bulunamadı.")
                
    with tab2:
        hesaplar = tum_hesaplar()
        if hesaplar:
            secilen_h = st.selectbox("Rapor Alınacak Hesabı Seçin", [h["hesap_no"] + " - " + h["sahip"] for h in hesaplar])
            h_no = secilen_h.split(" - ")[0]
            h_obj, m_obj = hesap_bul(h_no)
            
            # Filtreleme Özellikleri (Gereksinim 7)
            col1, col2 = st.columns(2)
            with col1:
                tarih_filtre = st.date_input("Tarih Aralığı Filtresi", value=(date(2025, 1, 1), date.today()))
            with col2:
                tur_filtre = st.selectbox("İşlem Türü Filtresi", ["Tümü", "Para Yatırma", "Para Çekme", "Transfer (Giden)", "Transfer (Gelen)"])
            
            raw_islemler = h_obj["islemler"]
            if raw_islemler:
                df = pd.DataFrame(raw_islemler)
                df["tarih_dt"] = df["tarih"].apply(lambda x: x.date() if isinstance(x, datetime) else x)
                
                # Tarih Aralığı ve İşlem Türü Filtrelemesi
                if isinstance(tarih_filtre, tuple) and len(tarih_filtre) == 2:
                    df = df[(df["tarih_dt"] >= tarih_filtre[0]) & (df["tarih_dt"] <= tarih_filtre[1])]
                if tur_filtre != "Tümü":
                    df = df[df["tur"] == tur_filtre]
                
                st.write(f"**Toplam Bulunan İşlem:** {len(df)}")
                st.dataframe(df[["tarih", "tur", "tutar", "aciklama"]], use_container_width=True)
            else:
                st.info("Bu hesaba ait herhangi bir işlem geçmişi bulunmuyor.")