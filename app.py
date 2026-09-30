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
    degisken_0 = st.selectbox("Başvuru Konusu", ["hasar bedeli", "hasar bedeli ve kusur"])
    degisken_10 = st.text_input("Başvuru Sahibi Araç Plakası", value="34ABC123")
    degisken_11 = st.text_input("Davalı Şirket Araç Plakası", value="34XYZ789")
    davali_unvan = st.text_input("Davalı Sigorta Şirketi Unvanı", value="X Sigorta A.Ş.")
    degisken_2 = st.number_input("İlk Dava Değeri - Hasar Bedeli (TL)", min_value=0.0, value=1000.0)
    islah_var = st.checkbox("Talep Artırımı (Islah) Var mı?")
    degisken_3 = st.number_input("Hasar Bedeli Islah Artış Tutarı (TL)", min_value=0.0, value=0.0) if islah_var else 0.0
    degisken_1_dt = st.date_input("Kaza Tarihi")
    degisken_1 = degisken_1_dt.strftime("%d.%m.%Y")
    degisken_4 = st.text_area("Başvuru Sahibi Beyan Özeti", value="hasarın tazmini")
    degisken_5 = st.selectbox("Talep Edilen Faiz Türü", ["avans", "yasal", "Faiz talebi yok"])
    degisken_6 = st.text_input("Başvuranın Sunduğu Ek Belgeler", value="kasko ekspertiz raporu")

with col2:
    st.subheader("🔬 2. Bilirkişi Raporu ve Ödemeler")
    degisken_12 = st.number_input("Raporda Tespit Edilen HB Tutarı (KDV Hariç)", min_value=0.0, value=0.0)
    degisken_13 = st.number_input("Raporda Tespit Edilen HB Tutarı (KDV Dahil)", min_value=0.0, value=0.0)
    degisken_14 = st.number_input("Sigorta Şirketi Hasar Ödemesi (TL)", min_value=0.0, value=0.0)
    degisken_8 = st.number_input("Başvuru Sahibi Kusur Oranı (%)", min_value=0, max_value=100, value=0)
    degisken_9 = f"%{100 - degisken_8}"
    degisken_7 = st.text_input("Sigorta Şirketi Cevap Özeti", value="")
    st.subheader("💸 3. Karar ve Yargılama Giderleri")
    degisken_21 = st.number_input("Hakem Tarafından Kabul Edilen Hasar Bedeli", min_value=0.0, value=0.0)
    degisken_18 = st.number_input("Ekspertiz Ücreti (TL)", min_value=0.0, value=0.0)
    degisken_19_dt = st.date_input("Sigorta Şirketine Yapılan Başvuru Tarihi")
    degisken_19 = degisken_19_dt.strftime("%d.%m.%Y") if degisken_19_dt else ""
    degisken_24 = st.number_input("İlk Başvuru Ücreti (TL)", min_value=0.0, value=520.0)
    degisken_23 = st.number_input("Tebligat Ücreti (TL)", min_value=0.0, value=75.0)
    degisken_25 = st.number_input("Islah Tamamlama Harcı (TL)", min_value=0.0, value=0.0) if islah_var else 0.0
    degisken_27 = st.number_input("Bilirkişi Ücreti - Hasar/Ortak (TL)", min_value=0.0, value=3500.0)
    degisken_28 = st.number_input("Bilirkişi Ücreti - Kusur (TL)", min_value=0.0, value=0.0)
    degisken_30 = st.number_input("Davalı Şirket Lehine Vekalet Ücreti (TL)", min_value=0.0, value=0.0)

degisken_16 = degisken_12 - degisken_14
degisken_17 = degisken_13 - degisken_14
degisken_20 = (degisken_19_dt + timedelta(days=9)).strftime("%d.%m.%Y") if degisken_19_dt else ""
degisken_31 = degisken_24 + degisken_25
degisken_32 = degisken_24 + degisken_25 + degisken_23 + degisken_18 + degisken_27 + degisken_28
degisken_29 = 45000.0 if degisken_21 > 45000.0 else degisken_21

if st.button("Karar Metnini Şablona İşle ve Hazırla"):
    degisken_50 = "Uyuşmazlığın çözümünde 5684 sayılı Sigortacılık Kanunu, 6102 sayılı Türk Ticaret Kanunu, 6098 sayılı Türk Borçlar Kanunu, 2918 sayılı Karayolları Trafik Kanunu, 6100 sayılı Hukuk Muhakemeleri Kanunu ve sair mevzuat dikkate alınmıştır."
    degisken_2_1_4 = "avans faizi ile birlikte" if degisken_5 == "avans" else "yasal faizi ile birlikte" if degisken_5 == "yasal" else " "
    degisken_2_1_2 = f"hasar bedelinin {degisken_2_1_4}"
    nihai_deger = degisken_3 if islah_var else degisken_2
    degisken_1_2_3 = "Hakemliğimizce" if nihai_deger < 122000 else "Heyetimizce"
    degisken_1_2_2 = "ıslah edilen" if islah_var else " "
    degisken_1_2_1 = f"yargılama sırasında alınan bilirkişi raporunun taraflara tebliğ sonrasında {degisken_1_2_2} uyuşmazlık {degisken_1_2_3} karara bağlanmıştır."
    uyusmazlik_konusu_olay_talep_paragrafi = f"Uyuşmazlık konusu; davalı Şiriket nezdinde Karayolları Motorlu Araçlar Zorunlu Mali Sorumluluk Sigorta Poliçesi ile teminat altına alınan aracın {degisken_1} tarihinde karıştığı kaza sonucunda başvuru sahibine ait araçta oluşan hasar bedelinin tazmin edilmesi talebine ilişkindir."
    basvurunun_hakeme_intikaline_incelenmesine_iliskin_surec_paragrafi = f"Başvuru sahibi talebinin davalı tarafından karşılanmaması nedeniyle ortaya çıkan uyuşmazlığın çözümü için tahkim yargılamasına başvurulmuş, {degisken_1_2_1}"
    basvuru_sahibinin_iddia_delil_talepleri_paragrafi = f"Başvuru sahibi vekili beyanında özetle; müvekkiline ait araçta hasar meydana geldiği, {degisken_4} belirtilerek, şimdilik {degisken_2:,.2f} TL {degisken_2_1_2} davalı Şirket tarafından karşılanması talep edilmiştir. Delil olarak {degisken_6} dosyaya sunulmuştur."
    sigorta_kuruluşunun_iddia_delil_talepleri_paragrafi = f"Davalı Şirket vekili tarafından sunulan cevap yazısında özetle; {degisken_7}" if degisken_7.strip() != "" else "Davalı Şirket tarafından herhangi bir cevap sunulmamıştır."
    uyusmazliga_uygulanacak_hukumler_paragrafi = degisken_50
    islah_ihbar = f"başvuru sahibi vekili tarafından ise dava değeri KDV dahil {degisken_3:,.2f} TL olarak ıslah edilmiştir." if islah_var else "başvuru sahibi vekili tarafından herhangi bir beyan sunulmamıştır."
    
    f1 = f"Başvuru sahibinin talebinin KABULÜ ile; {degisken_21:,.2f} TL hasar bedelinin {degisken_20} tarihinden itibaren işleyecek yasal faizi ile birlikte davalı Şirket tarafından başvuru sahibine ödenmesine,"
    f2 = f"Başvuru sahibinin sarf etmiş olduğu {degisken_31:,.2f} TL başvuru ücreti, {degisken_23:,.2f} TL tebligat ücreti, {degisken_18:,.2f} TL ekspertiz ücreti ve {degisken_27:,.2f} TL bilirkişi ücreti toplamı {degisken_32:,.2f} TL yargılama giderinin davalı Şirket tarafından başvuru sahibine ödenmesine,"
    f3 = f"Başvuru sahibi kendisini vekil ile temsil ettirdiğinden, 5684 sayılı Kanunun 30/17 maddesi and AAÜT gereğince belirlenen {degisken_29:,.2f} TL vekalet ücretinin davalı Şirketten tahsil edilerek başvuru sahibine ödenmesine,"
    f4 = f"5684 sayılı Sigortacılık Kanununun 30/12 maddesi hükmü gereği kararın bildirim tarihinden itibaren 10 gün içinde Sigorta Tahkim Komisyonu nezdinde İTİRAZ YOLU AÇIK OLMAK ÜZERE oy birliği ile karar verildi. {datetime.now().strftime('%d.%m.%Y')}"
    
    degerlendirme_gerekceli_karar_paragrafi = f"Dosya konusu uyuşmazlık, başvuru sahibine ait araçta oluşan hasar bedelinin Karayolları Motorlu Araçlar Zorunlu Mali Sorumluluk Sigorta Poliçesi kapsamında davalı Şirket tarafından tazminine ilişkindir. Söz konusu kazanın oluşumunda davalı Şirkette sigortalı araç sürücüsünün {degisken_9} kusurlu olduğu anlaşılmıştır. Uyuşmazlık konusu kazanın trafik sözleşmenin vadesi içinde gerçekleştiği, tarafların dava ehliyetlerinin olduğu tespit edilerek davanın esasına geçilmiştir. KTK 85 ve 91 maddeleri uyarınca işletenin sorumluluğunun sigortacıya devri öngörülmüştür. Uyuşmazlığın çözümü amacıyla dosya uzman bilirkişiye tevdi edilerek rapor tanzim edilmesi istenmiştir. Bilirkişi raporuna göre, Başvuru sahibine ait {degisken_10} plakalı aracın kaza öncesi ağır hasar kaydına rastlanılmadığı, araçta oluşan hasar miktarının KDV dahil {degisken_13:,.2f} TL olduğu, davalı Şirket tarafından yapılan {degisken_14:,.2f} TL ödemenin mahsubu ile KDV dahil {degisken_17:,.2f} TL bakiye hasar bedeli olacağı tespit edilmiştir. Rapor taraflara tebliğ edilmiş, davalı Şirket vekili tarafından herhangi bir beyan sunulmamış, {islah_ihbar} Bilirkişi raporu ayrıntılı, gerekçeli ve denetime elverişli olduğu görülmüş ve rapordaki tespit miktarına itibar edilerek, KDV dahil {degisken_21:,.2f} TL bakiye tazminatın tahsiline karar verilmiştir. Başvuru sahibi vekili tarafından talep edilen {degisken_18:,.2f} TL ekspertiz masrafının TTK 1426 kapsamında makul olduğuna karar verilmiştir. Davalı Şirkete {degisken_19} tarihinde başvuru yapıldığı anlaşılmakla KTK 99/1 maddesine istinaden temerrüt tarihi olan {degisken_20} tarihinden itibaren yasal faiz işletilmesine karar verilmiştir. 5684 sayılı Kanunun 30 maddesi and AAÜT gereğince vekalet ücretine hükmedilmiştir.\n\n5. KARAR\nYapılan değerlendirmeler ve belirtilen gerekçeler neticesinde;\n1- {f1}\n2- {f2}\n3- {f3}\n{f4}"

    try:
        doc = DocxTemplate("master_karar_sablonu.docx")
        context = {"uyusmazlik_konusu_olay_talep_paragrafi": uyusmazlik_konusu_olay_talep_paragrafi, "basvurunun_hakeme_intikaline_incelenmesine_iliskin_surec_paragrafi": basvurunun_hakeme_intikaline_incelenmesine_iliskin_surec_paragrafi, "basvuru_sahibinin_iddia_delil_talepleri_paragrafi": basvuru_sahibinin_iddia_delil_talepleri_paragrafi, "sigorta_kuruluşunun_iddia_delil_talepleri_paragrafi": sigorta_kuruluşunun_iddia_delil_talepleri_paragrafi, "uyusmazliga_uygulanacak_hukumler_paragrafi": uyusmazliga_uygulanacak_hukumler_paragrafi, "değerlendirme_gerekceli_karar_paragrafi": degerlendirme_gerekceli_karar_paragrafi}
        doc.render(context)
        bio = io.BytesIO()
        doc.save(bio)
        st.session_state.download_data = bio.getvalue()
        st.session_state.file_ready = True
        st.success("🎉 Karar metni ve 5. Karar başlığı tek bir büyük gövdede başarıyla birleştirildi!")
    except Exception as e:
        st.error(f"Şablon hatası: {e}")

if st.session_state.file_ready and st.session_state.download_data is not None:
    st.download_button(
        label="📥 TEK BLOKLU RESMİ KARARI İNDİR",
        data=st.session_state.download_data,
        file_name="Sigorta_Tahkim_Komisyonu_Karari_Nihai.docx",
