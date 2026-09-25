import streamlit as st
from docxtpl import DocxTemplate
import io
import os
from datetime import datetime

# Sitenin Başlığı ve Geniş Ekran Ayarı
st.set_page_config(page_title="Tahkim Karar Sistemi", layout="wide")
st.title("⚖️ Sigorta Tahkim Komisyonu Karar Otomasyonu")

# 1. KULLANICI GİRİŞ KONTROLÜ
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

        # --- ADIM 2: FORM ALANLARI (3 Sütunlu Gelişmiş Tasarım) ---
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("##### 📅 Tarih ve Süreç Bilgileri")
            kaza_tarihi_input = st.date_input("Kaza Tarihi", value=datetime.today())
            kaza_tarihi_str = kaza_tarihi_input.strftime("%d.%m.%Y")
            
            basvuru_tarihi_input = st.date_input("Sigorta Şirketine Başvuru Tarihi", value=datetime.today())
            basvuru_tarihi_str = basvuru_tarihi_input.strftime("%d.%m.%Y")
            
            faiz_tarihi_input = st.date_input("Faiz Başlangıç Tarihi", value=datetime.today())
            faiz_tarihi_str = faiz_tarihi_input.strftime("%d.%m.%Y")
            
            odeme_tarihi_input = st.date_input("Sigorta Şirketi Ödeme Tarihi (Varsa)", value=datetime.today())
            odeme_tarihi_str = odeme_tarihi_input.strftime("%d.%m.%Y")

        with col2:
            st.markdown("##### 💰 Parasal Değerler (TL)")
            dava_degeri = st.number_input("Dava Değeri (İlk Talep)", min_value=0.0, format="%.2f")
            islah_tutari = st.number_input("Islah Tutarı (Varsa)", min_value=0.0, format="%.2f")
            kabul_edilen_tutar = st.number_input("Hakem Tarafından Kabul Edilen Tutar", min_value=0.0, format="%.2f")
            odeme_tutari = st.number_input("Sigorta Şirketi Ödeme Tutarı (Varsa)", min_value=0.0, format="%.2f")
            ekspertiz_ucreti = st.number_input("Talep Edilen Ekspertiz Ücreti", min_value=0.0, format="%.2f")
            tespit_edilen_deger_kaybi = st.number_input("Bilirkişi Raporunda Tespit Edilen Değer Kaybı", min_value=0.0, format="%.2f")

        with col3:
            st.markdown("##### 🚗 Araç, Şirket ve Kusur Bilgileri")
            sigorta_sirketi_unvani = st.text_input("Davalı Sigorta Şirketi Ünvanı", placeholder="Örn: X Sigorta A.Ş.")
            sigortali_arac_plaka = st.text_input("Sigorta Şirketine Sigortalı Araç Plakası")
            sigortali_kusur_orani = st.text_input("Sigorta Şirketine Sigortalı Araç Kusur Oranı", placeholder="Örn: %75 veya 8/8")
            basvuran_arac_plaka = st.text_input("Başvuru Sahibine Ait Araç Plakası")
            talep_edilen_faiz = st.text_input("Talep Edilen Faiz Türü", value="Yasal Faiz")

        st.markdown("#### ✍️ Detaylı Metin / Beyan Alanları")
        sigorta_sirketi_cevabi = st.text_area("Sigorta Şirketi Cevap Yazısı Özeti (Beyanı)", height=100)

        st.markdown("---")
        
        # --- ADIM 4: WORD ÜRETME VE İNDİRME ---
        if st.button("📄 Karar Metnini Doldur ve Word Dosyası Hazırla", type="primary"):
            try:
                # Seçilen Word dosyasını arka planda açıyoruz
                doc = DocxTemplate(secilen_sablon)
                
                # Word içindeki {{etiket}} isimleri ile formdaki kutuları tam olarak eşleştiriyoruz
                veri_havuzu = {
                    "kaza_tarihi": kaza_tarihi_str,
                    "dava_degeri": f"{dava_degeri:,.2f} TL",
                    "talep_edilen_faiz": talep_edilen_faiz,
                    "sigorta_sirketi_cevabi": sigorta_sirketi_cevabi,
                    "sigorta_sirketine_sigortali_arac_plakasi": sigortali_arac_plaka,
                    "sigorta_sirketine_sigortali_arac_kusur_orani": sigortali_kusur_orani,
                    "basvuru_sahibine_ait_arac_plakasi": basvuran_arac_plaka,
                    "bilirkişi_raporunda_tespit_edilen_deger_kaybi_tutari": f"{tespit_edilen_deger_kaybi:,.2f} TL",
                    "davalı_sigorta_sirketi_unvani": sigorta_sirketi_unvani,
                    "davali_sigorta_sirketi_deger_kaybi_ödeme_tarihi": odeme_tarihi_str,
                    "davali_sigorta_sirketi_deger_kaybi_ödeme_tutari": f"{odeme_tutari:,.2f} TL",
                    "basvuru_sahibi_islah_tutari": f"{islah_tutari:,.2f} TL",
                    "hakem_tarafından_kabul_edilen_tutar": f"{kabul_edilen_tutar:,.2f} TL",
                    "basvuru_sahibi_tarafından_talep_edilen_ekspertiz_ücreti": f"{ekspertiz_ucreti:,.2f} TL",
                    "basvuru_sahibi_tarafindan_davali_sigorta_sirketine_yapilan_basvuri_tarihi": basvuru_tarihi_str,
                    "hakem_tarafindan_kabul_edilen_faiz_baslangic_tarihi": faiz_tarihi_str
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
