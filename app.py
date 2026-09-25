import streamlit as st
from docxtpl import DocxTemplate
import io
import os
from datetime import datetime

st.set_page_config(page_title="Tahkim Karar Otomasyonu v6", layout="wide", page_icon="⚖️")
st.title("⚖️ Sigorta Tahkim Komisyonu Karar Otomasyonu")

# Kullanıcı Yönetimi
KULLANICILAR = {"hakem1": "tahkim2026", "hakem2": "tahkim2026_ozel"}

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
            st.error("Hatalı kimlik bilgileri!")
else:
    sablonlar = [f for f in os.listdir(".") if f.endswith(".docx")]
    
    if not sablonlar:
        st.error("⚠️ Lütfen proje klasörüne en az bir adet .docx şablonu ekleyin.")
    else:
        st.sidebar.success("Sistem Aktif")
        if st.sidebar.button("Çıkış Yap"):
            st.session_state["authenticated"] = False
            st.rerun()

        st.markdown("### 📝 1. Şablon Seçimi")
        secilen_sablon = st.selectbox("Format Seçiniz:", sablonlar)

        st.markdown("---")
        st.markdown("### 📋 2. Şablona Göre Karar Parametreleri")

        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("##### 🔍 Başvuru ve Merci Seçimi")
            uyusmazlik_turu = st.selectbox(
                "Uyuşmazlık Konusu Nedir?",
                ["Değer Kaybı", "Hasar Bedeli", "Hasar Bedeli ve Değer Kaybı", "Araç Mahrumiyet Bedeli", "Diğer"]
            )
            
            if uyusmazlik_turu == "Değer Kaybı":
                uyusmazlik_konusu_eki = "değer kaybının"
            elif uyusmazlik_turu == "Hasar Bedeli":
                uyusmazlik_konusu_eki = "hasar bedelinin"
            elif uyusmazlik_turu == "Hasar Bedeli ve Değer Kaybı":
                uyusmazlik_konusu_eki = "hasar bedeli ve değer kaybının"
            elif uyusmazlik_turu == "Araç Mahrumiyet Bedeli":
                uyusmazlik_konusu_eki = "araç mahrumiyet bedelinin"
            else:
                uyusmazlik_konusu_eki = st.text_input("Lütfen uyuşmazlık konusunu ekli haliyle yazın:", placeholder="Örn: ikame araç bedelinin")

            # --- SİZİN HAZIRLADIĞINIZ degisken_1_3 (MERCI) ---
            merci_turu = st.radio("Karar Veren Merci:", ["Tek Hakem (Hakemliğimizce)", "Heyet (Heyetimizce)"])
            degisken_1_3 = "Hakemliğimizce" if "Tek Hakem" in merci_turu else "Heyetimizce"

            # --- SİZİN HAZIRLADIĞINIZ metin_1_2 İÇİN BİLİRKİŞİ SEÇİMİ ---
            bilirkisi_raporu_alindi_mi = st.radio("Bilirkişi Raporu Alındı mı?", ["Evet, Alındı", "Hayır, Alınmadı"])

            st.markdown("##### 📅 Süreç ve Temerrüt Tarihleri")
            kaza_tarihi = st.date_input("Kaza Tarihi", value=datetime.today()).strftime("%d.%m.%Y")
            basvuru_tarihi = st.date_input("Sigorta Şirketine Başvuru Tarihi", value=datetime.today()).strftime("%d.%m.%Y")
            faiz_tarihi = st.date_input("Temerrüt / Faiz Başlangıç Tarihi", value=datetime.today()).strftime("%d.%m.%Y")
            odeme_tarihi = st.date_input("Kaza Sonrası Kısmi Ödeme Tarihi (Varsa)", value=datetime.today()).strftime("%d.%m.%Y")

        with col2:
            st.markdown("##### 💰 Dava ve Bilrkişi Tutarları (TL)")
            dava_degeri = st.number_input("İlk Dava Değeri (Şimdilik Talep)", min_value=0.0, value=20.0, format="%.2f")
            islah_tutari = st.number_input("Islah Edilen Değer (Artırılan Tutar)", min_value=0.0, value=1250.0, format="%.2f")
            tespit_edilen_deger_kaybi = st.number_input("Bilirkişinin Tespit Ettiği Toplam Değer Kaybı", min_value=0.0, value=3500.0, format="%.2f")
            
            st.markdown("##### 📉 Ödeme ve Bakiye Hesapları")
            odeme_tutari = st.number_input("Şirketin Kaza Sonrası Ödediği Tutar", min_value=0.0, value=1780.0, format="%.2f")
            
            # --- SİZİN HAZIRLADIĞINIZ degisken_1_2 (ISLAH & ÖDEME MANTIĞI) ---
            has_islah = islah_tutari > 0
            has_payment = odeme_tutari > 0

            if has_islah and not has_payment:
                degisken_1_2 = "ıslah edilen"
            elif has_islah and has_payment:
                degisken_1_2 = "ıslah edilen ve konusuz kaldığı anlaşılan"
            elif not has_islah and has_payment:
                degisken_1_2 = "konusuz kaldığı anlaşılan"
            else:
                degisken_1_2 = ""

            # Kelime aralarındaki çift boşluk hatasını engellemek için düzeltme süzgeci
            ara_metin_eki = f" {degisken_1_2}".image_search() if degisken_1_2 else ""

            # --- SİZİN HAZIRLADIĞINIZ metin_1_2 KURALI ---
            if bilirkisi_raporu_alindi_mi == "Evet, Alındı":
                metin_1_2 = f"yargılama sırasında alınan bilirkişi raporunun taraflara tebliğ sonrasında{ara_metin_eki} uyuşmazlık {degisken_1_3} karara bağlanmıştır."
            else:
                metin_1_2 = f"dosya muhteviyatı ve ilgili mevzuat çerçevesinde uyuşmazlık {degisken_1_3} karara bağlanmıştır."

            # --- SİZİN HAZIRLADIĞINIZ nihai paragraf yapısı ---
            basvurunun_hakeme_intikaline_incelenmesine_iliskin_surec_paragrafi = (
                f"Başvuru sahibi talebinin davalı tarafından karşılanmaması nedeniyle ortaya çıkan uyuşmazlığın çözümü "
                f"için tahkim yargılamasına başvurulmuş, {metin_1_2}"
            )

            bakiye_bedel = tespit_edilen_deger_kaybi - odeme_tutari
            st.caption(f"**Otomatik Hesaplanan Bakiye:** {bakiye_bedel:,.2f} TL")
            
            kabul_edilen_tutar = st.number_input("Hakemce Hükmedilen (Kabul Edilen) Net Tutar", min_value=0.0, value=1000.0, format="%.2f")
            ekspertiz_ucreti = st.number_input("Hükmedilen Ekspertiz Masrafı", min_value=0.0, value=2500.0, format="%.2f")

        with col3:
            st.markdown("##### 🚗 Dosya ve Araç Bilgileri")
            sigorta_sirketi_unvani = st.text_input("Davalı Sigorta Şirketi Ünvanı", "AXA SİGORTA A.Ş.")
            davali_arac_plaka = st.text_input("Davalı (Sigortalı) Araç Plakası", "34 ** 02")
            basvuran_arac_plaka = st.text_input("Başvuran (Zarar Gören) Araç Plakası", "34 ** 11")
            sigortali_kusur_orani = st.text_input("Davalı Sürücü Kusur Oranı", "100")

            st.markdown("##### ⚖️ Yargılama Giderleri & Vekalet")
            basvuru_ucreti = st.number_input("Başvuru Ücreti", min_value=0.0, value=1750.0, format="%.2f")
            tebligat_ucreti = st.number_input("Tebligat Ücreti", min_value=0.0, value=75.0, format="%.2f")
            bilirkişi_ucreti = st.number_input("Bilirkişi Ücreti", min_value=0.0, value=1900.0, format="%.2f")
            
            toplam_yargilama_gideri = basvuru_ucreti + tebligat_ucreti + bilirkişi_ucreti
            st.caption(f"**Toplam Yargılama Gideri:** {toplam_yargilama_gideri:,.2f} TL")
            
            hukmedilen_vekalet_ucreti = st.number_input("Hükmedilen Avukatlık Vekalet Ücreti", min_value=0.0, value=1000.0, format="%.2f")
            talep_edilen_faiz = st.text_input("Faiz Türü", value="yasal faiz")

        st.markdown("##### ✍️ Savunma ve Beyan Özetleri")
        sigorta_sirketi_cevabi = st.text_area("Sigorta Kuruluşu Cevap Özeti", value="Tazminat hesabının Genel Şartlara göre yapılması gerektiği, yasal faizden sorumlu olunacağı belirtilerek reddi talep edilmiştir.", height=70)

        st.markdown("---")

        if st.button("📄 Karar Metnini Şablona İşle ve Hazırla", type="primary"):
            try:
                doc = DocxTemplate(secilen_sablon)
                
                def tr_money(val):
                    return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"

                veri_havuzu = {
                    "uyusmazlik_konusu_eki": uyusmazlik_konusu_eki,
                    # Word şablonuna doğrudan basılacak akıllı paragraf etiketi:
                    "basvurunun_hakeme_intikaline_incelenmesine_iliskin_surec_paragrafi": basvurunun_hakeme_intikaline_incelenmesine_iliskin_surec_paragrafi,
                    "kaza_tarihi": kaza_tarihi,
                    "basvuru_tarihi": basvuru_tarihi,
                    "faiz_tarihi": faiz_tarihi,
                    "odeme_tarihi": odeme_tarihi,
                    "davali_sigorta_sirketi_unvani": sigorta_sirketi_unvani,
                    "davali_arac_plaka": davali_arac_plaka,
                    "basvuran_arac_plaka": basvuran_arac_plaka,
                    "sigortali_kusur_orani": f"%{sigortali_kusur_orani}" if "%" not in sigortali_kusur_orani else sigortali_kusur_orani,
                    "dava_degeri": tr_money(dava_degeri),
                    "islah_tutari": tr_money(islah_tutari),
                    "tespit_edilen_deger_kaybi": tr_money(tespit_edilen_deger_kaybi),
                    "odeme_tutari": tr_money(odeme_tutari),
                    "bakiye_bedel": tr_money(bakiye_bedel),
                    "kabul_edilen_tutar": tr_money(kabul_edilen_tutar),
                    "ekspertiz_ucreti": tr_money(ekspertiz_ucreti),
                    "basvuru_ucreti": tr_money(basvuru_ucreti),
                    "tebligat_ucreti": tr_money(tebligat_ucreti),
                    "bilirkişi_ucreti": tr_money(bilirkişi_ucreti),
                    "toplam_yargilama_gideri": tr_money(toplam_yargilama_gideri),
                    "hukmedilen_vekalet_ucreti": tr_money(hukmedilen_vekalet_ucreti),
                    "talep_edilen_faiz": talep_edilen_faiz,
                    "sigorta_sirketi_cevabi": sigorta_sirketi_cevabi
                }

                doc.render(veri_havuzu)
                
                dosya_hafizasi = io.BytesIO()
                doc.save(dosya_hafizasi)
