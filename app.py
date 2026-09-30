import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io

st.set_page_config(layout="wide", page_title="Sigorta Tahkim Otomasyonu")
st.title("⚖️ Çok Kullanıcılı Bulut Tahkim Karar Otomasyonu")

# 1. GitHub'a yüklediğimiz Excel veri tabanını arkada sessizce okuyoruz
@st.cache_data
def veri_tabanini_yukle():
    try:
        return pd.read_excel("kurallar.xlsx")
    except:
        return None

df = veri_tabanini_yukle()

if df is not None:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 1. Senaryo ve Dinamik Form Alanları")
        # Excel'deki senaryo isimleri otomatik olarak kutucuğa geliyor!
        secilen_senaryo = st.selectbox("Lütfen Uygulanacak Hukuki Senaryoyu Seçin", df["senaryo_adi"].tolist())
        
        degisken_1 = st.text_input("Kaza Tarihi", value="01.01.2026")
        degisken_10 = st.text_input("Başvuru Sahibi Araç Plakası", value="34ABC123")
        degisken_4 = st.text_area("Başvuru Sahibi Beyan Özeti", value="hasarın tazmini talebi")

    with col2:
        st.subheader("🔬 2. Bilirkişi ve Hesaplama Alanları")
        degisken_13 = st.number_input("Raporda Tespit Edilen HB Tutarı (KDV Dahil)", min_value=0.0, value=15000.0)
        degisken_8 = st.number_input("Davalı Şirket Sürücüsü Kusur Oranı (%)", min_value=0, max_value=100, value=100)
        degisken_21 = st.number_input("Hakem Tarafından Kabul Edilen Hasar Bedeli", min_value=0.0, value=15000.0)

    if st.button("Karar Metnini Şablona İşle ve Hazırla"):
        # Excel'den seçilen senaryoya ait satırı cımbızla çekiyoruz
        satir = df[df["senaryo_adi"] == secilen_senaryo].iloc[0]
        
        # Excel içindeki taslak metinleri alıyoruz
        olay_ve_talep_taslak = satir["olay_ve_talep"]
        gerekceli_karar_taslak = satir["gerekceli_karar"]
        
        # Rakamları ve verileri şablon diliyle harmanlıyoruz
        context = {
            "degisken_1": degisken_1, "degisken_10": degisken_10, "degisken_4": degisken_4,
            "degisken_13": f"{degisken_13:,.2f}", "degisken_8": str(degisken_8), "degisken_21": f"{degisken_21:,.2f}"
        }
        
        # Excel'den gelen metinlerin içindeki değişkenleri de dinamik dolduruyoruz
        uyusmazlik_konusu_olay_talep_paragrafi = olay_ve_talep_taslak
        degerlendirme_gerekceli_karar_paragrafi = gerekceli_karar_taslak
        
        for k, v in context.items():
            degerlendirme_gerekceli_karar_paragrafi = degerlendirme_gerekceli_karar_paragrafi.replace(f"{{{{ {k} }}}}", v)

        try:
            doc = DocxTemplate("master_karar_sablonu.docx")
            doc.render({
                "uyusmazlik_konusu_olay_talep_paragrafi": uyusmazlik_konusu_olay_talep_paragrafi,
                "değerlendirme_gerekceli_karar_paragrafi": degerlendirme_gerekceli_karar_paragrafi
            })
            bio = io.BytesIO()
            doc.save(bio)
            st.success("🎉 Karar Excel'den başarıyla üretildi!")
            st.download_button(label="📥 RESMİ BULUT KARARINI İNDİR", data=bio.getvalue(), file_name="Tahkim_Karari.docx")
        except Exception as e:
            st.error(f"Şablon hatası: {e}")
else:
    st.warning("Lütfen GitHub deponuza 'kurallar.xlsx' dosyasını yükleyin.")
