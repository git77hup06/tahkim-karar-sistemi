import streamlit as st
from docxtpl import DocxTemplate
import io
import os
from datetime import datetime

# Sitenin Başlığı ve Geniş Ekran Ayarı
st.set_page_config(page_title="Tahkim Karar Sistemi", layout="wide")
st.title("⚖️ Sigorta Tahkim Komisyonu Karar Otomasyonu")

# 1. KULLANICI GİRİŞ KONTROLÜ (Sizin ve 2-3 arkadaşınızın şifresi)
KULLANICILAR = {
    "hakem1": "tahkim2026", 
    "hakem2": "tahkim2026_ozel",
    "hakem3": "tahkim2026_heyet"
}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.subheader("🔒 Güvenli Giriş")
    kullanici_adi = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş Yap"):
        if kullanici_adi in KULLANICILAR and KULLANICILAR[kullanici_adi] == sifre:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Hatalı kullanıcı adı veya şifre!")
else:
    # 2. KLASÖRDEKİ WORD ŞABLONLARINI BULMA
    sablonlar = [f for f in os.listdir(".") if f.endswith(".docx")]
    
    if not sablonlar:
        st.error("⚠️ Klasörde hiç Word (.docx) şablonu bulunamadı! Lütfen dosyalarınızı yükleyin.")
    else:
        st.sidebar.success("Sistem Aktif")
        if st.sidebar.button("Çıkış Yap"):
            st.session_state["authenticated"] = False
            st.rerun()

        # --- ADIM 1: ŞABLON SEÇİMİ ---
        st.markdown("### 📝 1. Karar Şablonu Seçimi")
        secilen_sablon = st.selectbox(
            "Hangi karar formatını doldurmak istiyorsunuz?",
            sablonlar,
            help="Klasöre yüklediğiniz Word dosyaları burada listelenir."
        )

        st.markdown("---")
        st.markdown("### 📋 2. Form Bilgilerini Giriniz")

        # --- ADIM 2: FORM ALANLARI (3 Sütunlu Tasarım) ---
        col1, col2, col3 = st.columns(3)
        
        with col1:
            kaza_tarihi_input = st.date_input("Kaza Tarihi", value=datetime.today())
            kaza_tarihi_str = kaza_tarihi_input.strftime("%d.%m.%Y") # Türkiye tarih formatı
            ilk_dava_degeri = st.number_input("İlk Dava Değeri (TL)", min_value=0.0, format="%.2f")
            kabul_edilen_tutar = st.number_input("Kabul Edilen Tutar (TL)", min_value=0.0, format="%.2f")
            
        with col2:
            kusur_orani = st.text_input("Sigorta Şirketi Kusur Oranı", placeholder="Örn: %75")
            ekspertiz_ucreti = st.number_input("Ekspertiz Ücreti (TL)", min_value=0.0, format="%.2f")
            basvuru_ucreti = st.number_input("Başvuru Ücreti (TL)", min_value=0.0, value=1200.0)

        with col3:
            tebligat_ucreti = st.number_input("Tebligat Ücreti (TL)", min_value=0.0, value=55.0)
            bilirkisi_ucreti = st.number_input("Bilirkişi Ücreti (TL)", min_value=0.0, value=2750.0)

        st.markdown("#### ✍️ Detaylı Metin Paragrafları")
        basvuru_sahibi_beyani = st.text_area("Başvuran Vekili Beyanı (Gerekirse uzun metin yapıştırın)")
        sigorta_sirketi_beyani = st.text_area("Sigorta Şirketi Beyanı / Cevap Yazısı Özeti")
        basvuran_ek_belgeleri = st.text_input("Başvuran Vekili Tarafından Sunulan Ek Belgeler")

        # --- ADIM 3: ARKA PLAN MATEMATİKSEL OTOMASYONU ---
        toplam_yargilama_gideri = basvuru_ucreti + tebligat_ucreti + bilirkisi_ucreti
        reddedilen_tutar = max(0.0, ilk_dava_degeri - kabul_edilen_tutar)
        kabul_orani = (kabul_edilen_tutar / ilk_dava_degeri) if ilk_dava_degeri > 0 else 0
        davali_yargilama_gideri_payi = toplam_yargilama_gideri * kabul_orani

        st.markdown("---")
        
        # --- ADIM 4: WORD ÜRETME VE İNDİRME ---
        if st.button("📄 Karar Metnini Doldur ve Word Dosyası Hazırla", type="primary"):
            try:
                # Seçilen Word dosyasını arka planda aç
                doc = DocxTemplate(secilen_sablon)
                
                # Word içindeki {{etiket}} isimleri ile formdaki kutuları eşleştiriyoruz
                veri_havuzu = {
                    "kaza_tarihi": kaza_tarihi_str,
                    "ilk_dava_degeri": f"{ilk_dava_degeri:,.2f}",
                    "kabul_edilen_tutar": f"{kabul_edilen_tutar:,.2f}",
                    "reddedilen_tutar": f"{reddedilen_tutar:,.2f}",
                    "kusur_orani": kusur_orani,
                    "ekspertiz_ucreti": f"{ekspertiz_ucreti:,.2f}",
                    "basvuru_sahibi_beyani": basvuru_sahibi_beyani,
                    "sigorta_sirketi_beyani": sigorta_sirketi_beyani,
                    "basvuran_ek_belgeleri": basvuran_ek_belgeleri,
                    # Kodun otomatik hesapladığı matematiksel sonuçlar:
                    "toplam_yargilama_gideri": f"{toplam_yargilama_gideri:,.2f}",
                    "davali_yargilama_gideri_payi": f"{davali_yargilama_gideri_payi:,.2f}"
                }
                
                # Verileri Word şablonuna bas
                doc.render(veri_havuzu)
                
                # Dosyayı indirmeye hazır hale getir
                dosya_hafizasi = io.BytesIO()
                doc.save(dosya_hafizasi)
                dosya_hafizasi.seek(0)
                
                st.success(f"🎉 Karar '{secilen_sablon}' şablonu kullanılarak başarıyla oluşturuldu!")
                
                # İndirme Butonu
                st.download_button(
                    label="📥 Word Dosyasını İndir (.docx)",
                    data=dosya_hafizasi,
                    file_name=f"Tahkim_Karari_{datetime.today().strftime('%Y%m%d')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"Sistemsel bir hata oluştu: {e}")
