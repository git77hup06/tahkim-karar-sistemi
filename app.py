import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
from datetime import datetime, timedelta
import io

st.set_page_config(layout="wide", page_title="Sigorta Tahkim Otomasyonu")
st.title("⚖️ Sigorta Tahkim Komisyonu Karar Otomasyonu (Master Şablon)")

# 1. Kurallar Tablosunu Yükle
try:
    df_kurallar = pd.read_excel("kurallar.xlsx")
except Exception as e:
    st.error("Lütfen 'kurallar.xlsx' dosyasının mevcut olduğundan emin olun.")
    st.stop()

# 2. Üst Menü: Şablon Seçimi
konu_listesi = df_kurallar["Basvuru_Konusu"].unique()
secilen_konu = st.selectbox("📋 Başvuru Konusu Seçiniz:", konu_listesi)

secilen_satir_df = df_kurallar[df_kurallar["Basvuru_Konusu"] == secilen_konu]

if secilen_satir_df.empty:
    st.error(f"Hata: Excel'de '{secilen_konu}' konusuna ait hiçbir veri bulunamadı!")
    st.stop()

secilen_satir = secilen_satir_df.iloc[0]
sablon_yolu = secilen_satir["Word_Sablon_Yolu"]
alanlar_ham = secilen_satir["Gerekli_Alanlar"]

gerekli_parametreler = [alan.strip() for alan in str(alanlar_ham).split(",") if alan.strip()]

st.markdown("---")
st.subheader(f"🔬 {secilen_konu} - Karar Parametreleri Giriş Formu")

input_verileri = {}

# 3. Streamlit Akıllı Form Yapısı
with st.form(key="tahkim_formu"):
    col1, col2 = st.columns(2)
    
    for index, alan in enumerate(gerekli_parametreler):
        hedef_kol = col1 if index % 2 == 0 else col2
        etiket = alan.replace("_", " ").title()
        alan_key = alan.strip()
        
        if "basvuru_konusu" in alan_key.lower():
            continue
            
        # Dinamik Checkbox (Mantıksal Senaryoları Değiştiren Alanlar)
        if "alindi" in alan_key.lower() or "verdi_mi" in alan_key.lower():
            input_verileri[alan_key] = hedef_kol.checkbox(etiket, value=True, key=alan_key)
        elif "faiz_turu" in alan_key.lower() or "faiz_türü" in alan_key.lower():
            input_verileri[alan_key] = hedef_kol.selectbox(etiket, ["avans", "yasal", "Faiz talebi yok"], key=alan_key)
        elif "tarih" in alan_key.lower():
            tarih_dt = hedef_kol.date_input(f"📅 {etiket}", key=alan_key)
            input_verileri[alan_key] = tarih_dt
        elif any(x in alan_key.lower() for x in ["ucreti", "ücreti", "harci", "harcı", "tutari", "tutarı", "bedeli", "degeri", "değeri", "orani", "oranı", "odemesi", "ödemesi"]):
            input_verileri[alan_key] = hedef_kol.number_input(f"💳 {etiket}", min_value=0.0, value=0.0, step=50.0, key=alan_key)
        elif "beyani" in alan_key.lower() or "beyanı" in alan_key.lower() or "belgeler" in alan_key.lower():
            input_verileri[alan_key] = hedef_kol.text_area(f"📝 {etiket}", key=alan_key)
        else:
            input_verileri[alan_key] = hedef_kol.text_input(f"✍️ {etiket}", key=alan_key)
            
    st.markdown("---")
    islah_var = st.checkbox("🔄 Talep Artırımı (Islah) Var mı?", value=True)
    
    submit_button = st.form_submit_button(label="🚀 Karar Metnini Şablona İşle ve Hazırla")

# 4. Esnek Veri Okuyucu Yardımcı Fonksiyon
def safe_get(sozluk, anahtar_kelime, varsayilan=0.0):
    for k, v in sozluk.items():
        clean_k = k.lower().replace("ı","i").replace("ş","s").replace("ü","u").replace("ç","c").replace("ğ","g").replace("ö","o")
        clean_target = anahtar_kelime.lower().replace("ı","i").replace("ş","s").replace("ü","u").replace("ç","c").replace("ğ","g").replace("ö","o")
        if clean_target in clean_k:
            return v
    return varsayilan

# 5. Form Gönderildiğinde Koşul Hesaplama Motoru
if submit_button:
    input_verileri["basvuru_konusu"] = secilen_konu.lower()
    
    # Checkbox Durumlarını Doğrudan Word Şablonuna Göndermek İçin Alıyoruz (Yeni Kısım)
    bilirkisi_raporu_alindi = bool(safe_get(input_verileri, "alindi", True))
    sigorta_sirketi_cevap_verdi_mi = bool(safe_get(input_verileri, "verdi_mi", True))
    
    kaza_tarihi_dt = safe_get(input_verileri, "kaza_tarihi", datetime.now())
    kaza_tarihi = kaza_tarihi_dt.strftime("%d.%m.%Y") if isinstance(kaza_tarihi_dt, datetime) else str(kaza_tarihi_dt)
    
    basvuru_tarihi_dt = safe_get(input_verileri, "basvuru_tarihi", datetime.now())
    
    faiz_secimi = safe_get(input_verileri, "faiz_turu", "yasal")
    degisken_2_1_4 = "avans faizi ile birlikte" if faiz_secimi == "avans" else "yasal faizi ile birlikte" if faiz_secimi == "yasal" else " "
    
    degisken_1_1_1 = "hasar bedelinin"
    
    d12 = float(safe_get(input_verileri, "kdv_haric", 0))
    d13 = float(safe_get(input_verileri, "kdv_dahil", 0))
    d14 = float(safe_get(input_verileri, "odemesi_hb", 0))
    
    degisken_16 = d12 - d14
    degisken_17 = d13 - d14
    
    try:
        degisken_20 = (basvuru_tarihi_dt + timedelta(days=9)).strftime("%d.%m.%Y")
    except:
        degisken_20 = datetime.now().strftime("%d.%m.%Y")
        
    d21 = float(safe_get(input_verileri, "kabul_en_hb", 0))
    if d21 == 0:
        d21 = float(safe_get(input_verileri, "kabul_edilen_hasar", 0))
    
    # Vekalet Sınırı
    if d21 > 45000:
        degisken_29 = 45000.0
    else:
        degisken_29 = d21 if d21 > 0 else 45000.0
        
    # Yargılama Giderleri
    d18 = float(safe_get(input_verileri, "ekspertiz", 0))
    d23 = float(safe_get(input_verileri, "tebligat", 0))
    d24 = float(safe_get(input_verileri, "ilk_basvuru", 0))
    d25 = float(safe_get(input_verileri, "islah_tamamlama", 0))
    d27 = float(safe_get(input_verileri, "bilirkisi_ucreti", 0))
    
    degisken_31 = d24 + d25
    degisken_32 = d24 + d25 + d23 + d18 + d27

    nihai_deger_kontrol = d25 if islah_var else d24  
    degisken_1_2_2 = "ıslah edilen" if islah_var else " "
    degisken_1_2_3 = "Hakemliğimizce" if nihai_deger_kontrol < 122000 else "Heyetimizce"
    degisken_1_2_1 = f"yargılama sırasında alınan bilirkişi raporunun taraflara tebliğ sonrasında {degisken_1_2_2} uyuşmazlık {degisken_1_2_3} karara bağlanmıştır."

    islah_tutar_hb = float(safe_get(input_verileri, "islah_edilen_tutar", 0))
    islah_metni = f"dava değeri KDV dahil {islah_tutar_hb:,.2f} TL olarak ıslah edilmiştir." if islah_var else "herhangi bir beyan sunulmamıştır."

    f1 = f"Başvuru sahibinin talebinin KABULÜ ile; {d21:,.2f} TL hasar bedelinin {degisken_20} tarihinden itibaren işleyecek {degisken_2_1_4} davalı Şirket tarafından başvuru sahibine ödenmesine,"

    # Word Şablonuna ve İçindeki {% if %} Bloklarına Gönderilecek Context Paketi
    word_context = {
        # Mantıksal Senaryo Sinyalleri (Word'deki {% if %} bloklarını yöneten değişkenler)
        "bilirkisi_raporu_alindi": bilirkisi_raporu_alindi,
        "sigorta_sirketi_cevap_verdi_mi": sigorta_sirketi_cevap_verdi_mi,
        
        # Standart Veri Girişleri
        "degisken_1": kaza_tarihi,
        "degisken_2": f"{float(safe_get(input_verileri, 'ilk_dava_degeri_hb', 0)):,.2f}",
        "degisken_3": f"{islah_tutar_hb:,.2f}",
        "degisken_4": str(safe_get(input_verileri, "basvuru_sahibi_beyani", "")),
        "degisken_6": str(safe_get(input_verileri, "sunulan_ek_belgeler", "")),
        "degisken_7": str(safe_get(input_verileri, "sigorta_sirketi_beyani", "")),
        "degisken_9": safe_get(input_verileri, "sigorta_sirketi_kusur_orani", 100),
        "degisken_10": str(safe_get(input_verileri, "basvuru_sahibi_arac_plakasi", "")),
        "degisken_13": f"{d13:,.2f}",
        "degisken_14": f"{d14:,.2f}",
        "degisken_17": f"{degisken_17:,.2f}",
        "degisken_18": f"{d18:,.2f}",
        "degisken_21": f"{d21:,.2f}",
        "degisken_29": f"{degisken_29:,.2f}",
        "degisken_31": f"{degisken_31:,.2f}",
        "degisken_32": f"{degisken_32:,.2f}",
        "degisken_50": "Uyuşmazlığın çözümünde 5684 sayılı Sigortacılık Kanunu, 6102 sayılı Türk Ticaret Kanunu, 6098 sayılı Türk Borçlar Kanunu, 2918 sayılı Karayolları Trafik Kanunu, 6100 sayılı Hukuk Muhakemeleri Kanunu ve sair mevzuat dikkate alınmıştır.",
        "degisken_1_1_1": degisken_1_1_1,
        "degisken_1_2_1": degisken_1_2_1,
        "degisken_2_1_1": "hasar meydana geldiği",
        "degisken_2_1_2": f"hasar bedelinin {degisken_2_1_4}",
        "degisken_4_1": "hasar bedelinin",
        "islah_metni": islah_metni,
        "f1": f1
    }

    # 6. Belge Üretim Motoru
    try:
        doc = DocxTemplate(str(sablon_yolu).strip())
        doc.render(word_context)
        
        mem_file = io.BytesIO()
        doc.save(mem_file)
        mem_file.seek(0)
        
        st.success("🎉 Dinamik tek master şablon başarıyla işlendi!")
        st.download_button(
            label="📄 Master Word Dosyasını İndir",
            data=mem_file,
            file_name=f"Tahkim_Dinamik_Karari.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as err:
        st.error(f"Master şablon işlenirken hata oluştu: {err}")
