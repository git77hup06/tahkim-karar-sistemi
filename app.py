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

# --- FORMA GİRİLECEK BİLGİLER (SÜTUN DÜZENİ) ---
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
    degisken_4 = st.text_area("Başvuru Sahibi Beyan Özeti", value="oluşan hasarın tazmin edilmesi gerektiği")
    degisken_5 = st.selectbox("Talep Edilen Faiz Türü", ["avans", "yasal", "Faiz talebi yok"])
    degisken_6 = st.text_input("Başvuranın Sunduğu Ek Belgeler", value="kasko ekspertiz raporu")

with col2:
    st.subheader("🔬 2. Bilirkişi Raporu ve Ödemeler")
    degisken_12 = st.number_input("Raporda Tespit Edilen HB Tutarı (KDV Hariç)", min_value=0.0, value=0.0)
    degisken_13 = st.number_input("Raporda Tespit Edilen HB Tutarı (KDV Dahil)", min_value=0.0, value=0.0)
    degisken_14 = st.number_input("Sigorta Şirketi Hasar Ödemesi (TL)", min_value=0.0, value=0.0)
    degisken_15 = 0.0
    degisken_8 = st.number_input("Başvuru Sahibi Kusur Oranı (%)", min_value=0, max_value=100, value=0)
    degisken_9 = f"%{100 - degisken_8}"
    degisken_7 = st.text_input("Sigorta Şirketi Cevap Özeti (Boş bırakılırsa cevap sunulmadı basar)", value="")

    st.subheader("💸 3. Karar ve Yargılama Giderleri")
    degisken_21 = st.number_input("Hakem Tarafından Kabul Edilen Hasar Bedeli", min_value=0.0, value=0.0)
    degisken_22 = 0.0
    degisken_18 = st.number_input("Ekspertiz Ücreti (TL)", min_value=0.0, value=0.0)
    degisken_19_dt = st.date_input("Sigorta Şirketine Yapılan Başvuru Tarihi")
    degisken_19 = degisken_19_dt.strftime("%d.%m.%Y") if degisken_19_dt else ""
    
    degisken_24 = st.number_input("İlk Başvuru Ücreti (TL)", min_value=0.0, value=520.0)
    degisken_23 = st.number_input("Tebligat Ücreti (TL)", min_value=0.0, value=75.0)
    degisken_25 = st.number_input("Islah Tamamlama Harcı (TL)", min_value=0.0, value=0.0) if islah_var else 0.0
    degisken_26 = 0.0
    degisken_27 = st.number_input("Bilirkişi Ücreti - Hasar/Ortak (TL)", min_value=0.0, value=3500.0)
    degisken_28 = st.number_input("Bilirkişi Ücreti - Kusur (TL)", min_value=0.0, value=0.0)
    degisken_30 = st.number_input("Davalı Şirket Lehine Vekalet Ücreti (TL)", min_value=0.0, value=0.0)

# --- MATEMATİKSEL KURALLAR VE ARKA PLAN HESAPLAMALARI ---
degisken_16 = degisken_12 - degisken_14
degisken_17 = degisken_13 - degisken_14
degisken_20 = (degisken_19_dt + timedelta(days=9)).strftime("%d.%m.%Y") if degisken_19_dt else ""
degisken_31 = degisken_24 + degisken_25
degisken_32 = degisken_24 + degisken_25 + degisken_23 + degisken_18 + degisken_27 + degisken_28
degisken_29 = 45000.0 if degisken_21 > 45000.0 else degisken_21

if st.button("Karar Metnini Şablona İşle ve Hazırla"):
    degisken_50 = "Uyuşmazlığın çözümünde 5684 sayılı Sigortacılık Kanunu, 6102 sayılı Türk Ticaret Kanunu, 6098 sayılı Türk Borçlar Kanunu, 2918 sayılı Karayolları Trafik Kanunu, 6100 sayılı Hukuk Muhakemeleri Kanunu ve sair mevzuat dikkate alınmıştır."
    
    degisken_2_1_4 = "avans faizi ile birlikte" if degisken_5 == "avans" else "yasal faizi ile birlikte" if degisken_5 == "yasal" else " "
    degisken_1_1_1 = "hasar bedelinin"
    degisken_2_1_1 = " hasar meydana geldiği "
    degisken_2_1_3 = "avans faizi ile birlikte" if degisken_5 == "avans" else "yasal faizi ile birlikte"
    degisken_2_1_2 = f"hasar bedelinin {degisken_2_1_3}"
    degisken_4_1 = "hasar bedelinin"

    nihai_deger = degisken_3 if islah_var else degisken_2
    degisken_1_2_3 = "Hakemliğimizce" if nihai_deger < 122000 else "Heyetimizce"
    degisken_1_2_2 = "ıslah edilen" if islah_var else " "
    degisken_1_2_1 = f"yargılama sırasında alınan bilirkişi raporunun taraflara tebliğ sonrasında {degisken_1_2_2} uyuşmazlık {degisken_1_2_3} karara bağlanmıştır."

    uyusmazlik_konusu_olay_talep_paragrafi = f"Uyuşmazlık konusu; davalı Şirket nezdinde Karayolları Motorlu Araçlar Zorunlu Mali Sorumluluk Sigorta Poliçesi ile teminat altına alınan aracın {degisken_1} tarihinde karıştığı kaza sonucunda başvuru sahibine ait araçta oluşan {degisken_1_1_1} tazmin edilmesi talebine ilişkindir."
    basvurunun_hakeme_intikaline_incelenmesine_iliskin_surec_paragrafi = f"Başvuru sahibi talebinin davalı tarafından karşılanmaması nedeniyle ortaya çıkan uyuşmazlığın çözümü için tahkim yargılamasına başvurulmuş, {degisken_1_2_1}"
    basvuru_sahibinin_iddia_delil_talepleri_paragrafi = f"Başvuru sahibi vekili tarafından Sigorta Tahkim Komisyonu’na yapılan uyuşmazlık başvuru formu ve eki beyanında özetle; Davalı Şirket tarafından Karayolları Motorlu Araçlar Zorunlu Mali Sorumluluk Sigorta Poliçesi ile sigortalı aracın karıştığı kaza neticesinde müvekkiline ait araçta {degisken_2_1_1}, {degisken_4} belirtilerek, fazlaya ilişkin hakları saklı kalmak üzere şimdilik {degisken_2:,.2f} TL {degisken_2_1_2} davalı Şirket tarafından karşılanması talep edilmiştir. Vekaletname ile birlikte iddialara dayanak olarak, davalı şirkete gönderilen talep yazısı, {degisken_6}, hasarlı araç fotoğrafları, kaza tespit tutanağı, araç ruhsatı ve sair deliller dosyaya sunulmuştur."
    
    if degisken_7.strip() != "":
        sigorta_kuruluşunun_iddia_delil_talepleri_paragrafi = f"Davalı Şirket vekili tarafından Sigorta Tahkim Komisyonu’na sunulan cevap yazısında özetle;\n{degisken_7}"
    else:
        sigorta_kuruluşunun_iddia_delil_talepleri_paragrafi = "Davalı Şirket tarafından Sigorta Tahkim Komisyonu’na herhangi bir cevap sunulmamıştır."

    uyusmazliga_uygulanacak_hukumler_paragrafi = degisken_50

    islah_ihbar_metni = f"başvuru sahibi vekili tarafından ise dava değeri KDV dahil {degisken_3:,.2f} TL olarak ıslah edilmiştir." if islah_var else "başvuru sahibi vekili tarafından herhangi bir beyan sunulmamıştır."
    faiz_hukmu = f"{degisken_20} tarihinden itibaren işleyecek yasal faizi ile birlikte davalı Şirketten tahsiline" if degisken_5 != "Talep Yok" else "davalı Şirketten tahsiline"

    # --- 5. BÖLÜM METİNLERİ ARKA PLANDA HAZIRLANIYOR ---
    fıkra_1 = f"Başvuru sahibinin talebinin KABULÜ ile; {degisken_21:,.2f} TL hasar bedelinin {degisken_20} tarihinden itibaren işleyecek yasal faizi ile birlikte davalı Şirket tarafından başvuru sahibine ödenmesine,"
    fıkra_2 = f"Başvuru sahibinin sarf etmiş olduğu {degisken_31:,.2f} TL başvuru ücreti, {degisken_23:,.2f} TL tebligat ücreti, {degisken_18:,.2f} TL ekspertiz ücreti ve {degisken_27:,.2f} TL bilirkişi ücreti toplamı {degisken_32:,.2f} TL yargılama giderinin davalı Şirket tarafından başvuru sahibine ödenmesine,"
    fıkra_3 = f"Başvuru sahibi kendisini vekil ile temsil ettirdiğinden, 5684 sayılı Kanunun 30/17 maddesi ve AAÜT gereğince belirlenen {degisken_29:,.2f} TL vekalet ücretinin davalı Şirketten tahsil edilerek başvuru sahibine ödenmesine,"
    yasal_yol = "miktar itibariyle KESİN olmak üzere" if nihai_kontrol_tutari <= 40000 else "kararın tebliğinden itibaren 5 iş günü içinde Komisyon nezdinde İTİRAZ yolu açık olmak üzere"
    fıkra_kapanis = f"5684 sayılı Sigortacılık Kanunu’nun 30/12’nci maddesi hükmü gereği kararın bildirim tarihinden itibaren 10 gün içinde Sigorta Tahkim Komisyonu nezdinde İTİRAZ YOLU AÇIK OLMAK ÜZERE oy birliği ile karar verildi. {datetime.now().strftime('%d.%m.%Y')}"

    # --- 4. VE 5. BÖLÜMÜ TEK BİR DEV BLOK HALİNE GETİREN BİRLEŞTİRME MOTORU ---
    degerlendirme_gerekceli_karar_paragrafi = f"""Dosya konusu uyuşmazlık, başvuru sahibine ait araçta oluşan {degisken_4_1} Karayolları Motorlu Araçlar Zorunlu Mali Sorumluluk Sigorta Poliçesi kapsamında davalı Şirket tarafından tazminine ilişkindir.
Söz konusu kazanın oluşumunda davalı Şirkette sigortalı araç sürücüsünün % {degisken_8} kusurlu olduğu anlaşılmıştır.
Uyuşmazlık konusu kazanın trafik sözleşmenin vadesi içinde gerçekleştiği, tarafların taraf ve dava ehliyetlerinin olduğu tespit edilerek davanın esasına geçilmiştir.
2918 Sayılı Karayolları Trafik Kanunu’nun 85’nci maddesinde karayolunda işletilen araçlara ilişkin olarak işletenin sorumluluğu düzenlenmiştir. Söz konusu maddenin birinci fıkrasında “Bir motorlu aracın işletilmesi bir kimsenin ölümüne veya yaralanmasına yahut bir şeyin zarara uğramasına sebep olursa, motorlu aracın bir teşebbüsün unvanı veya işletme adı altında veya bu teşebbüs tarafından kesilen biletle işletilmesi halinde, motorlu aracın işleteni ve bağlı olduğu teşebbüsün sahibi, doğan zarardan müştereken ve müteselsilen sorumlu olurlar” hükmü düzenlenmiştir. Yine aynı Kanunun 91’nci maddesi, 85’inci maddesinde yer alan işletenin sorumluluğunun sigortacıya devrini öngörmüştür.
Uyuşmazlığın çözümü için alınan ara karar ile, kaza tarihindeki parça ve işçilik ücretleri dikkate alınarak ve eşdeğer parça and iskonto indirimi gibi piyasa koşulları gözetilerek kaza ile illiyet içindeki araç hasar zararının tespiti konusunda dosyanın bilirkişiye tevdiine karar verilmiştir.
