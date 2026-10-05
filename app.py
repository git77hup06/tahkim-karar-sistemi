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

# 2. Üst Menü: Şablon Seçimi (Tek Yetkili Seçim Kutusu)
konu_listesi = df_kurallar["Basvuru_Konusu"].unique()
secilen_konu = st.selectbox("📋 Başvuru Konusu Seçiniz:", konu_listesi)

secilen_satir_df = df_kurallar[df_kurallar["Basvuru_Konusu"] == secilen_konu]

if secilen_satir_df.empty:
    st.error(f"Hata: Excel'de '{secilen_konu}' konusuna ait hiçbir veri bulunamadı!")
    st.stop()

secilen_satir = secilen_satir_df.iloc
sablon_yolu = secilen_satir["Word_Sablon_Yolu"]
alanlar_ham = secilen_satir["Gerekli_Alanlar"]

# Parametreleri listeye temizleyerek aktar
gerekli_parametreler = [alan.strip() for alan in str(alanlar_ham).split(",") if alan.strip()]

st.markdown("---")
st.subheader(f"🔬 {secilen_konu} - Karar Parametreleri Giriş Formu")

input_verileri = {}

# 3. Streamlit Form Yapısı
with st.form(key="tahkim_formu"):
    col1, col2 = st.columns(2)
    
    # Excel'den gelen listeyi ekrana döküyoruz
    for index, alan in enumerate(gerekli_parametreler):
        hedef_kol = col1 if index % 2 == 0 else col2
        etiket = alan.replace("_", " ").title()
        alan_key = alan.strip()
        
        # Mükerrerliği önlemek için eğer kazara excelde kaldıysa basvuru_konusu'nu form içinde es geç
        if "basvuru_konusu" in alan_key.lower():
            continue
            
        # Özel Tiplerin Ayrıştırılması
        if "faiz_turu" in alan_key.lower() or "faiz_türü" in alan_key.lower():
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

# 4. Yardımcı Esnek Veri Okuyucu
def safe_get(sozluk, anahtar_kelime, varsayilan=0.0):
    for k, v in sozluk.items():
        if anahtar_kelime.lower().replace("ı","i").replace("ş","s").replace("ü","u").replace("ç","c").replace("ğ","g").replace("ö","o") in k.lower().replace("ı","i").replace("ş","s").replace("ü","u").replace("ç","c").replace("ğ","g").replace("ö","o"):
            return v
    return varsayilan

# 5. Form Gönderildiğinde Tetiklenen Hesaplama Alanı
if submit_button:
    # Ana menüden seçilen konuyu doğrudan içeriye enjekte ediyoruz (Çakışmayı önleyen kısım)
    input_verileri["basvuru_konusu"] = secilen_konu.lower()
    
    # Tarih formatlamaları
    kaza_tarihi_dt = safe_get(input_verileri, "kaza_tarihi", datetime.now())
    kaza_tarihi = kaza_tarihi_dt.strftime("%d.%m.%Y") if isinstance(kaza_tarihi_dt, datetime) else str(kaza_tarihi_dt)
    
    basvuru_tarihi_dt = safe_get(input_verileri, "basvuru_tarihi", datetime.now())
    
    # Faiz cümle kurucusu
    faiz_secimi = safe_get(input_verileri, "faiz_turu", "yasal")
    degisken_2_1_4 = "avans faizi ile birlikte" if faiz_secimi == "avans" else "yasal faizi ile birlikte" if faiz_secimi == "yasal" else " "
    
    degisken_1_1_1 = "hasar bedelinin"
    
    # Finansal Veriler
    d12 = float(safe_get(input_verileri, "kdv_haric", 0))
    d13 = float(safe_get(input_verileri, "kdv_dahil", 0))
    d14 = float(safe_get(input_verileri, "odemesi_hb", 0))
    
    degisken_16 = d12 - d14
    degisken_17 = d13 - d14
    
    # Temerrüt Tarihi Hesaplama (+9 gün)
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
        
    # Gider Toplamları
    d18 = float(safe_get(input_verileri, "ekspertiz", 0))
    d23 = float(safe_get(input_verileri, "tebligat", 0))
    d24 = float(safe_get(input_verileri, "ilk_basvuru", 0))
    d25 = float(safe_get(input_verileri, "islah_tamamlama", 0))
    d27 = float(safe_get(input_verileri, "bilirkisi_ucreti", 0))
    
    degisken_31 = d24 + d25
    degisken_32 = d24 + d25 + d23 + d18 + d27

    # Hakem mi Heyet mi? (122.000 TL Sınırı)
    nihai_deger_kontrol = d25 if islah_var else d24  
    degisken_1_2_2 = "ıslah edilen" if islah_var else " "
    degisken_1_2_3 = "Hakemliğimizce" if nihai_deger_kontrol < 122000 else "Heyetimizce"
    degisken_1_2_1 = f"yargılama sırasında alınan bilirkişi raporunun taraflara tebliğ sonrasında {degisken_1_2_2} uyuşmazlık {degisken_1_2_3} karara bağlanmıştır."

    # Şirket Cevap Beyanı
    sigorta_beyani = str(safe_get(input_verileri, "sigorta_sirketi_beyani", "")).strip()
    if not sigorta_beyani or sigorta_beyani == "0.0":
        sigorta_beyani = str(safe_get(input_verileri, "sirket_beyani", "")).strip()
        
    if sigorta_beyani and sigorta_beyani != "0.0":
        sigorta_kurulusunun_iddia_delil_talepleri_paragrafi = f"Davalı Şirket vekili tarafından Sigorta Tahkim Komisyonu’na sunulan cevap yazısında özetle; {sigorta_beyani}"
    else:
        sigorta_kurulusunun_iddia_delil_talepleri_paragrafi = "Davalı Şirket tarafından Sigorta Tahkim Komisyonu’na herhangi bir cevap sunulmamıştır."

    islah_tutar_hb = float(safe_get(input_verileri, "islah_edilen_tutar", 0))
    islah_metni = f"dava değeri KDV dahil {islah_tutar_hb:,.2f} TL olarak ıslah edilmiştir." if islah_var else "herhangi bir beyan sunulmamıştır."

    f1 = f"Başvuru sahibinin talebinin KABULÜ ile; {d21:,.2f} TL hasar bedelinin {degisken_20} tarihinden itibaren işleyecek {degisken_2_1_4} davalı Şirket tarafından başvuru sahibine ödenmesine,"

    # Word Context Paketi
    word_context = {
        "degisken_1": kaza_tarihi,
        "degisken_2": f"{float(safe_get(input_verileri, 'ilk_dava_degeri_hb', 0)):,.2f}",
        "degisken_3": f"{islah_tutar_hb:,.2f}",
        "degisken_4": str(safe_get(input_verileri, "basvuru_sahibi_beyani", "")),
        "degisken_6": str(safe_get(input_verileri, "sunulan_ek_belgeler", "")),
        "degisken_8": safe_get(input_verileri, "kusur_orani", 0),
        "degisken_10": str(safe_get(input_verileri, "arac_plakasi", "")),
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
        "sigorta_kurulusunun_iddia_delil_talepleri_paragrafi": sigorta_kurulusunun_iddia_delil_talepleri_paragrafi,
        "islah_metni": islah_metni,
        "f1": f1
    }

    # 6. Belge Oluşturma Motoru
    try:
        hedef_sablon = str(sablon_yolu).strip()
        if "deger_kaybi" in hedef_sablon and "hasar" in secilen_konu.lower():
            hedef_sablon = "templates/hasar_bedeli.docx"
            
        doc = DocxTemplate(hedef_sablon)
        doc.render(word_context)
        
        mem_file = io.BytesIO()
        doc.save(mem_file)
        mem_file.seek(0)
        
        st.success("🎉 Mükerrerlik giderildi! Karar metni başarıyla hazırlandı.")
        st.download_button(
            label="📄 Hazır Word Dosyasını İndirmek İçin Tıklayın",
            data=mem_file,
            file_name=f"Tahkim_Karar_Taslagi_{secilen_konu.replace(' ','_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as err:
        st.error(f"Word şablonu işlenirken bir hata oluştu: {err}")
