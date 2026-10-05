import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
from datetime import datetime, timedelta
import io

st.set_page_config(layout="wide", page_title="Sigorta Tahkim Otomasyonu")
st.title("⚖️ Sigorta Tahkim Komisyonu Karar Otomasyonu")

# 1. Kurallar Tablosunu Yükle
try:
    df_kurallar = pd.read_excel("kurallar.xlsx")
except Exception as e:
    st.error("Lütfen 'kurallar.xlsx' dosyasının mevcut olduğundan emin olun.")
    st.stop()

# 2. Şablon Seçimi
konu_listesi = df_kurallar["Basvuru_Konusu"].unique()
secilen_konu = st.selectbox("📋 Başvuru Konusu Seçiniz:", konu_listesi)

secilen_satir = df_kurallar[df_kurallar["Basvuru_Konusu"] == secilen_konu].iloc
sablon_yolu = secilen_satir["Word_Sablon_Yolu"]
gerekli_alanlar = [alan.strip() for alan in str(secilen_satir["Gerekli_Alanlar"]).split(",") if alan.strip()]

st.markdown("---")
st.subheader("📝 Karar Parametreleri Bilgi Girişi")

# Form Girdilerini Toplama Sözlüğü
input_verileri = {}
col1, col2 = st.columns(2)

# 3. Alan Tiplerini Akıllıca Ayrıştırıp Ekrana Basma
for index, alan in enumerate(gerekli_parametreler):
    hedef_kol = col1 if index % 2 == 0 else col2
    etiket = alan.replace("_", " ").title()
    
    # Özel Kontroller (Seçim kutuları, Tarihler ve Sayılar)
    if alan == "basvuru_konusu":
        input_verileri[alan] = hedef_kol.selectbox(etiket, ["hasar bedeli", "hasar bedeli ve kusur"], key=alan)
    elif alan == "basvuru_sahibi_tarafindan_talep_edilen_faiz_turu":
        input_verileri[alan] = hedef_kol.selectbox(etiket, ["avans", "yasal", "Faiz talebi yok"], key=alan)
    elif "tarih" in alan:
        tarih_dt = hedef_kol.date_input(etiket, key=alan)
        input_verileri[alan] = tarih_dt
    elif any(x in alan for x in ["ucreti", "harci", "tutari", "bedeli", "degeri", "orani", "odemesi"]):
        input_verileri[alan] = hedef_kol.number_input(etiket, min_value=0.0, value=0.0, step=50.0, key=alan)
    elif "beyani" in alan or "belgeler" in alan:
        input_verileri[alan] = hedef_kol.text_area(etiket, key=alan)
    else:
        input_verileri[alan] = hedef_kol.text_input(etiket, key=alan)

st.markdown("---")
islah_var = st.checkbox("🔄 Talep Artırımı (Islah) Var mı?")

# 4. "Karar Hazırla" Butonuna Basıldığında Formülleri Çalıştırma
if st.button("🚀 Karar Metnini Şablona İşle ve Hazırla"):
    # Formülleri güvenli işletmek için verileri yerel değişkenlere çıkarıyoruz
    kaza_tarihi_dt = input_verileri.get("kaza_tarihi", datetime.now())
    kaza_tarihi = kaza_tarihi_dt.strftime("%d.%m.%Y") if isinstance(kaza_tarihi_dt, datetime) else str(kaza_tarihi_dt)
    
    basvuru_tarihi_dt = input_verileri.get("basvuru_sahibi_tarafindan_sigorta_sirketine_basvuru_tarihi", datetime.now())
    
    # Faiz Mantığı
    faiz_secimi = input_verileri.get("basvuru_sahibi_tarafindan_talep_edilen_faiz_turu", "yasal")
    degisken_2_1_4 = "avans faizi ile birlikte" if faiz_secimi == "avans" else "yasal faizi ile birlikte" if faiz_secimi == "yasal" else " "
    
    # Konu Mantığı
    degisken_1_1_1 = "hasar bedelinin" if input_verileri.get("basvuru_konusu") == "hasar bedeli" else "hasar bedeli ve kusur payının"
    
    # Hesaplamalar
    d12 = float(input_verileri.get("bilirkisi_raporunda_tespit_edilen_hasar_bedeli_kdv_haric", 0))
    d13 = float(input_verileri.get("bilirkisi_raporunda_tespit_edilen_hasar_bedeli_kdv_dahil", 0))
    d14 = float(input_verileri.get("sigorta_sirketi_odemesi_hb", 0))
    
    degisken_16 = d12 - d14
    degisken_17 = d13 - d14
    
    # Temerrüt Tarihi (+9 gün)
    try:
        degisken_20 = (basvuru_tarihi_dt + timedelta(days=9)).strftime("%d.%m.%Y")
    except:
        degisken_20 = datetime.now().strftime("%d.%m.%Y")
        
    d21 = float(input_verileri.get("uyusmazlik_hakemi_tarafindan_kabul_en_hb", 0))
    
    # Vekalet Ücreti Sınırı Sizin Formülünüz
    if d21 > 45000:
        degisken_29 = 45000.0
    else:
        degisken_29 = d21
        
    # Yargılama Giderleri Toplamı Formülleri
    d18 = float(input_verileri.get("basvuru_sahibi_ekspertiz_ucreti_talebi", 0))
    d23 = float(input_verileri.get("tebligat_ucreti", 0))
    d24 = float(input_verileri.get("ilk_basvuru_ucreti", 0))
    d25 = float(input_verileri.get("islah_tamamlama_harci", 0))
    d27 = float(input_verileri.get("bilirkisi_ucreti_hb_dk", 0))
    
    degisken_31 = d24 + d25
    degisken_32 = d24 + d25 + d23 + d18 + d27

    # Islah Kontrolü ve Hakem/Heyet Kararı Mantığı
    nihai_deger_kontrol = d25 if islah_var else d24  # Islah varsa ıslah tutarı kontrolü
    degisken_1_2_2 = "ıslah edilen" if islah_var else " "
    degisken_1_2_3 = "Hakemliğimizce" if nihai_deger_kontrol < 122000 else "Heyetimizce"
    degisken_1_2_1 = f"yargılama sırasında alınan bilirkişi raporunun taraflara tebliğ sonrasında {degisken_1_2_2} uyuşmazlık {degisken_1_2_3} karara bağlanmıştır."

    # Şirket Cevap Dilekçesi Özeti Mantığı
    sigorta_beyani = str(input_verileri.get("sigorta_sirketi_beyani", "")).strip()
    if sigorta_beyani:
        sigorta_kurulusunun_iddia_delil_talepleri_paragrafi = f"Davalı Şirket vekili tarafından Sigorta Tahkim Komisyonu’na sunulan cevap yazısında özetle; {sigorta_beyani}"
    else:
        sigorta_kurulusunun_iddia_delil_talepleri_paragrafi = "Davalı Şirket tarafından Sigorta Tahkim Komisyonu’na herhangi bir cevap sunulmamıştır."

    # Islah Metni Paragrafı Kontrolü
    islah_tutar_hb = float(input_verileri.get("islah_edilen_tutar_hb", 0))
    islah_metni = f"başvuru sahibi vekili tarafından dava değeri KDV dahil {islah_tutar_hb:,.2f} TL olarak ıslah edilmiştir." if islah_var else "başvuru sahibi vekili tarafından herhangi bir ıslah talebinde bulunulmamıştır."

    # Hüküm Fıkrası Paragrafı
    f1 = f"Başvuru sahibinin talebinin KABULÜ ile; {d21:,.2f} TL hasar bedelinin {degisken_20} tarihinden itibaren işleyecek {degisken_2_1_4} davalı Şirket tarafından başvuru sahibine ödenmesine,"

    # Word'e Gönderilecek Tüm Veri Paketi (Sözlük)
    word_context = {
        "degisken_1": kaza_tarihi,
        "degisken_2": f"{float(input_verileri.get('ilk_dava_degeri_hb', 0)):,.2f}",
        "degisken_3": f"{islah_tutar_hb:,.2f}",
        "degisken_4": input_verileri.get("basvuru_sahibi_beyani", ""),
        "degisken_6": input_verileri.get("basvuru_sahibi_tarafindan_sunulan_ek_belgeler", ""),
        "degisken_8": input_verileri.get("basvuru_sahibi_kusur_orani", 0),
        "degisken_10": input_verileri.get("basvuru_sahibi_arac_plakasi", ""),
        "degisken_13": f"{d13:,.2f}",
        "degisken_14": f"{d14:,.2f}",
        "degisken_17": f"{degisken_17:,.2f}",
        "degisken_18": f"{d18:,.2f}",
        "degisken_21": f"{d21:,.2f}",
        "degisken_29": f"{degisken_29:,.2f}",
        "degisken_31": f"{degisken_31:,.2f}",
        "degisken_32": f"{degisken_32:,.2f}",
        "degisken_50": "Uyuşmazlığın çözümünde 5684 sayılı Sigortacılık Kanunu, 6102 sayılı Türk Ticaret Kanunu, 6098 sayılı Türk Borçlar Kanunu, 2918 sayılı Karayolları Trafik Kanunu, 6100 sayılı Hukuk Muhameleri Kanunu ve sair mevzuat dikkate alınmıştır.",
        "degisken_1_1_1": degisken_1_1_1,
        "degisken_1_2_1": degisken_1_2_1,
        "degisken_2_1_1": "hasar meydana geldiği",
        "degisken_2_1_2": f"hasar bedelinin {degisken_2_1_4}",
        "degisken_4_1": "hasar bedelinin",
        "sigorta_kurulusunun_iddia_delil_talepleri_paragrafi": sigorta_kurulusunun_iddia_delil_talepleri_paragrafi,
        "islah_metni": islah_metni,
        "f1": f1
    }

    # 5. Render ve İndirme Aşaması
    try:
        doc = DocxTemplate(sablon_yolu)
        doc.render(word_context)
        
        mem_file = io.BytesIO()
        doc.save(mem_file)
        mem_file.seek(0)
        
        st.success("🎉 Karar metni başarıyla işlendi ve taslak hazırlandı!")
        st.download_button(
            label="📄 Word Dosyasını İndir",
            data=mem_file,
            file_name=f"Tahkim_Karar_Taslagi_{secilen_konu}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as err:
        st.error(f"Word şablonu işlenirken bir hata oluştu: {err}")
