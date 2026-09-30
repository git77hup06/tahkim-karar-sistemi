import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime, timedelta
import io

st.set_page_config(layout="wide", page_title="Sigorta Tahkim Otomasyonu")
st.title("⚖️ Sigorta Tahkim Komisyonu Karar Otomasyonu")

if "file_ready" not in st.session_state:
    st.session_state.file_ready = False
if "download_data" not in st.session_state:
    st.session_state.download_data = None

col1, col2 = st.columns(2)
with col1:
    st.subheader("📋 1. Taraf, Plaka ve Talep Bilgileri")
    degisken_10 = st.text_input("Başvuru Sahibi Araç Plakası [degisken_10]", value="34ABC123")
    degisken_2 = st.number_input("İlk Dava Değeri - Hasar Bedeli (TL) [degisken_2]", min_value=0.0, value=1000.0)
    islah_var = st.checkbox("Talep Artırımı (Islah) Var mı?")
    degisken_3 = st.number_input("Hasar Bedeli Islah Artış Tutarı (TL) [degisken_3]", min_value=0.0, value=0.0) if islah_var else 0.0
    degisken_1_dt = st.date_input("Kaza Tarihi [degisken_1]")
    degisken_1 = degisken_1_dt.strftime("%d.%m.%Y")
    degisken_4 = st.text_area("Başvuru Sahibi Beyan Özeti [degisken_4]", value="hasarın tazmini")
    degisken_5 = st.selectbox("Talep Edilen Faiz Türü [degisken_5]", ["avans", "yasal", "Faiz talebi yok"])
    degisken_6 = st.text_input("Başvuranın Sunduğu Ek Belgeler [degisken_6]", value="kasko ekspertiz raporu")

with col2:
    st.subheader("🔬 2. Bilirkişi Raporu, Ödemeler ve Giderler")
    degisken_13 = st.number_input("Raporda Tespit Edilen HB Tutarı (KDV Dahil) [degisken_13]", min_value=0.0, value=0.0)
    degisken_14 = st.number_input("Sigorta Şirketi Hasar Ödemesi (TL) [degisken_14]", min_value=0.0, value=0.0)
    degisken_8 = st.number_input("Başvuru Sahibi Kusur Oranı (%) [degisken_8]", min_value=0, max_value=100, value=0)
    degisken_7 = st.text_input("Sigorta Şirketi Cevap Özeti [degisken_7]", value="")
    degisken_21 = st.number_input("Hakem Tarafından Kabul Edilen Hasar Bedeli [degisken_21]", min_value=0.0, value=0.0)
    degisken_18 = st.number_input("Ekspertiz Ücreti (TL) [degisken_18]", min_value=0.0, value=0.0)
    degisken_19_dt = st.date_input("Sigorta Şirketine Yapılan Başvuru Tarihi [degisken_19]")
    degisken_19 = degisken_19_dt.strftime("%d.%m.%Y") if degisken_19_dt else ""
    degisken_24 = st.number_input("İlk Başvuru Ücreti (TL) [degisken_24]", min_value=0.0, value=520.0)
    degisken_23 = st.number_input("Tebligat Ücreti (TL) [degisken_23]", min_value=0.0, value=75.0)
    degisken_25 = st.number_input("Islah Tamamlama Harcı (TL) [degisken_25]", min_value=0.0, value=0.0) if islah_var else 0.0
    degisken_27 = st.number_input("Bilirkişi Ücreti - Hasar/Ortak (TL) [degisken_27]", min_value=0.0, value=3500.0)

# --- MATEMATİKSEL ROBOTİK HESAPLAMALAR ---
degisken_17 = degisken_13 - degisken_14
degisken_20 = (degisken_19_dt + timedelta(days=9)).strftime("%d.%m.%Y") if degisken_19_dt else ""
degisken_31 = degisken_24 + degisken_25
degisken_32 = degisken_24 + degisken_25 + degisken_23 + degisken_18 + degisken_27
degisken_29 = 45000.0 if degisken_21 > 45000.0 else degisken_21

if st.button("Karar Metnini Şablona İşle ve Hazırla"):
    degisken_2_1_4 = "avans faizi ile birlikte" if degisken_5 == "avans" else "yasal faizi ile birlikte" if degisken_5 == "yasal" else " "
    degisken_1_2_3 = "Hakemliğimizce" if ((degisken_3 if islah_var else degisken_2) < 122000) else "Heyetimizce"
    degisken_1_2_2 = "ıslah edilen" if islah_var else " "
    sigorta_cevap = f"Davalı Şirket vekili tarafından sunulan cevap yazısında özetle; {degisken_7}" if degisken_7.strip() != "" else "Davalı Şirket tarafından herhangi bir cevap sunulmamıştır."
    islah_ihbar = f"dava değeri KDV dahil {degisken_3:,.2f} TL olarak ıslah edilmiştir." if islah_var else "herhangi bir beyan sunulmamıştır."
    faiz_red_metni = "Başvuru sahibi tarafından avans faizi talep edilmektedir. Uyuşmazlık konusu haksız fiil kaynaklı olup başvuru sahibi vekilinin avans faiz istemi haklı bulunmamıştır." if degisken_5 == "avans" else ""

    context = {
        "degisken_1": degisken_1, "degisken_2": f"{degisken_2:,.2f}", "degisken_3": f"{degisken_3:,.2f}", "degisken_4": degisken_4, "degisken_6": degisken_6,
        "degisken_8": str(degisken_8), "degisken_10": degisken_10, "degisken_13": f"{degisken_13:,.2f}", "degisken_14": f"{degisken_14:,.2f}",
        "degisken_17": f"{degisken_17:,.2f}", "degisken_18": f"{degisken_18:,.2f}", "degisken_19": degisken_19, "degisken_20": degisken_20,
        "degisken_21": f"{degisken_21:,.2f}", "degisken_23": f"{degisken_23:,.2f}", "degisken_27": f"{degisken_27:,.2f}", "degisken_29": f"{degisken_29:,.2f}",
        "degisken_31": f"{degisken_31:,.2f}", "degisken_32": f"{degisken_32:,.2f}", "degisken_2_1_4": degisken_2_1_4, "degisken_1_2_2": degisken_1_2_2,
        "degisken_1_2_3": degisken_1_2_3, "sigorta_kuruluşunun_iddia_delil_talepleri_paragrafi": sigorta_cevap, "islah_ihbar": islah_ihbar, "faiz_red_metni": faiz_red_metni,
        "karar_tarihi": datetime.now().strftime("%d.%m.%Y")
    }
    try:
        doc = DocxTemplate("master_karar_sablonu.docx")
        doc.render(context)
        bio = io.BytesIO()
        doc.save(bio)
        st.session_state.download_data = bio.getvalue()
        st.session_state.file_ready = True
        st.success("🎉 Karar başarıyla hesaplandı!")
    except Exception as e:
        st.error(f"Hata: {e}")

if st.session_state.file_ready and st.session_state.download_data is not None:
    st.download_button(label="📥 RESMİ KARARI İNDİR", data=st.session_state.download_data, file_name="Sigorta_Tahkim_Komisyonu_Karari.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
