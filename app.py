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
    st.subheader("📋 1. Başvuru ve Taraf Bilgileri")
    basvuru_konusu = st.selectbox("Başvuru Konusu", ["Değer Kaybı", "Değer Kaybı ve Kusur", "Hasar Bedeli", "Hasar Bedeli ve Kusur", "Hasar Bedeli ve Değer Kaybı", "Hasar Bedeli ve Değer Kaybı ve Kusur", "Rayiç Bedel Farkı"])
    ilk_dava_degeri_dk = st.number_input("İlk Dava Değeri - Değer Kaybı (TL)", min_value=0.0, value=0.0)
    ilk_dava_degeri_hb = st.number_input("İlk Dava Değeri - Hasar Bedeli (TL)", min_value=0.0, value=0.0)
    islah_var = st.checkbox("Talep Artırımı (Islah) Var mı?")
    deger_kaybi_islah_tutari = st.number_input("Değer Kaybı Islah Artış Tutarı (TL)", min_value=0.0, value=0.0) if islah_var else 0.0
    hasar_bedeli_kaybi_islah_tutari = st.number_input("Hasar Bedeli Islah Artış Tutarı (TL)", min_value=0.0, value=0.0) if islah_var else 0.0
    kaza_tarihi_dt = st.date_input("Kaza Tarihi")
    kaza_tarihi = kaza_tarihi_dt.strftime("%d.%m.%Y")
    basvuru_sahibine_ait_arac_plakasi = st.text_input("Başvuru Sahibine Ait Araç Plakası", value="34ABC123")
    davali_sirkete_sigortali_arac_plakasi = st.text_input("Davalı Şirkete Sigortalı Araç Plakası", value="34XYZ789")
    davalı_sigorta_sigorta_sirketi_unvani = st.text_input("Davalı Sigorta Şirketi Unvanı", value="X Sigorta A.Ş.")
    basvuru_sahibi_beyani = st.text_area("Başvuru Sahibi Beyanı Summary", value="oluşan hasarın tazmin edilmesi gerektiği")
    sirket_cevap_verdi_mi = st.checkbox("Davalı Şirket Cevap Dilekçesi Sundu mu?", value=True)
    sigorta_sirketi_beyani = st.text_area("Sigorta Şirketi Cevap Özeti") if sirket_cevap_verdi_mi else ""
    faiz_turu = st.selectbox("Talep Edilen Faiz Türü", ["Avans", "Yasal", "Talep Yok"])
    basvuran_ek_belgeleri = st.text_input("Başvuran Ek Belgeleri", value="ekspertiz raporu")
    başvurunun_niteligi = st.text_input("Başvurunun Niteliği", value="kısmi dava olarak")

with col2:
    st.subheader("🔬 2. Bilirkişi Raporu ve Ödeme Alanları")
    bilirkisi_raporu_alindi = st.checkbox("Bilirkişi Raporu Alındı mı?", value=True)
    bilirkişi_raporunda_tespit_edilen_dk_tutari = st.number_input("Raporda Tespit Edilen Değer Kaybı Tutarı", min_value=0.0) if (bilirkisi_raporu_alindi and "Değer Kaybı" in basvuru_konusu) else 0.0
    davali_siket_dk_odemesi = st.number_input("Davalı Şirket Değer Kaybı Ödemesi (TL)", min_value=0.0) if (bilirkisi_raporu_alindi and "Değer Kaybı" in basvuru_konusu) else 0.0
    bilirkişi_raporunda_tespit_edilen_hb_tutari_kdv_haric = st.number_input("Raporda Tespit Edilen HB Tutarı (KDV Hariç)", min_value=0.0) if (bilirkisi_raporu_alindi and "Hasar Bedeli" in basvuru_konusu) else 0.0
    bilirkişi_raporunda_tespit_edilen_hb_tutari_kdv_dahil = st.number_input("Raporda Tespit Edilen HB Tutarı (KDV Dahil)", min_value=0.0) if (bilirkisi_raporu_alindi and "Hasar Bedeli" in basvuru_konusu) else 0.0
    davali_siket_hb_odemesi = st.number_input("Davalı Şirket Hasar Bedeli Ödemesi (TL)", min_value=0.0) if (bilirkisi_raporu_alindi and "Hasar Bedeli" in basvuru_konusu) else 0.0
    bilirkişi_raporunda_uygulan_yedek_parca_iskonto_orani = st.text_input("Yedek Parça İskonto Oranı", value="%0")
    bilirkişi_raporunda_uygulan_iscilik_iskonto_orani = st.text_input("İşçilik İskonto Oranı", value="%0")
    basvuru_sahibine_ait_arac_kusuru_orani = st.number_input("Başvuru Sahibi Kusur Oranı (%)", min_value=0, max_value=100, value=0)
    davali_sirkete_sigortali_arac_kusuru = f"%{100 - basvuru_sahibine_ait_arac_kusuru_orani}"
    st.subheader("💸 3. Karar ve Yargılama Giderleri")
    hakem_tarafinden_kabul_edilen_deger_kaybi_tutari = st.number_input("Hakem Tarafından Kabul Edilen Değer Kaybı Tutarı", min_value=0.0)
    hakem_tarafinden_kabul_edilen_hasar_bedeli_tutari = st.number_input("Hakem Tarafından Kabul Edilen Hasar Bedeli Tutarı", min_value=0.0)
    ekspertiz_ucreti_tutari = st.number_input("Ekspertiz Ücreti Tutarı (TL)", min_value=0.0)
    basvuru_tarihi_dt = st.date_input("Sigorta Şirketine Yapılan Başvuru Tarihi")
    tebligat_ucreti = st.number_input("Tebligat Ücreti (TL)", min_value=0.0)
    ilk_basvuru_ucreti = st.number_input("İlk Başvuru Ücreti (TL)", min_value=0.0)
    islah_tamamlama_harci = st.number_input("Islah Tamamlama Harcı (TL)", min_value=0.0)
    bilirkişi_ücreti_dk = st.number_input("Bilirkişi Ücreti - Değer Kaybı (TL)", min_value=0.0)
    bilirkişi_ücreti_hb_dk = st.number_input("Bilirkişi Ücreti - Hasar/Değer Kaybı Ortak (TL)", min_value=0.0)
    bilirkişi_ücreti_kusur = st.number_input("Bilirkişi Ücreti - Kusur (TL)", min_value=0.0)
    başvuran_lehine_vekalet_ucreti = st.number_input("Başvuran Lehine Vekalet Ücreti (TL)", min_value=0.0)

toplam_islah_tutari = hasar_bedeli_kaybi_islah_tutari + deger_kaybi_islah_tutari
ilk_dava_degeri = ilk_dava_degeri_dk + ilk_dava_degeri_hb
nihai_kontrol_tutari = toplam_islah_tutari if islah_var else ilk_dava_degeri

if st.button("Karar Metnini Şablona İşle ve Hazırla"):
    degisken_1_1 = "değer kaybının" if "Değer Kaybı" in basvuru_konusu else "hasar bedelinin"
    uyusmazlik_konusu_olay_talep_paragrafi = f"Uyuşmazlık konusu; davalı Şirket nezdinde Karayolları Motorlu Araçlar Zorunlu Mali Sorumluluk Sigorta Poliçesi ile teminat altına alınan aracın {kaza_tarihi} tarihinde karıştığı kaza sonucunda başvuru sahibine ait araçta oluşan {degisken_1_1} tazmin edilmesi talebine ilişkindir."
    degisken_1_3 = "Hakemliğimizce" if nihai_kontrol_tutari < 122000 else "Heyetimizce"
    degisken_1_2 = "ıslah edilen ve konusuz kaldığı anlaşılan" if (islah_var and (davali_siket_dk_odemesi > 0 or davali_siket_hb_odemesi > 0)) else "ıslah edilen" if islah_var else "konusuz kaldığı anlaşılan" if (davali_siket_dk_odemesi > 0 or davali_siket_hb_odemesi > 0) else ""
    metin_1_2 = f"yargılama sırasında alınan bilirkişi raporunun taraflara tebliğ sonrasında {degisken_1_2} uyuşmazlık {degisken_1_3} karara bağlanmıştır." if bilirkisi_raporu_alindi else f"dosya muhteviyatı ve ilgili mevzuat çerçevesinde uyuşmazlık {degisken_1_3} karara bağlanmıştır."
    basvurunun_hakeme_intikaline_incelenmesine_iliskin_surec_paragrafi = f"Başvuru sahibi talebinin davalı tarafından karşılanmaması nedeniyle ortaya çıkan uyuşmazlığın çözümü için tahkim yargılamasına başvurulmuş, {metin_1_2}"
    degisken_2_1_4 = "avans faizi ile birlikte" if faiz_turu == "Avans" else "yasal faizi ile birlikte" if faiz_turu == "Yasal" else " "
    degisken_2_1_1 = "oluşan hasar nedeniyle aracın değer kaybına uğradığı" if "Değer Kaybı" in basvuru_konusu else "hasar meydana geldiği"
    degisken_2_1_3 = f"hasar bedeli ve değer kaybı bedelinin {başvurunun_niteligi} {degisken_2_1_4} ve {ekspertiz_ucreti_tutari:,.2f} TL ekspertiz ücretinin yargılama giderleri arasında" if ekspertiz_ucreti_tutari > 0 else f"hasar bedeli ve değer kaybının {başvurunun_niteligi} {degisken_2_1_4}"
    basvuru_sahibinin_iddia_delil_talepleri_paragrafi = f"Başvuru sahibi vekili tarafından uyuşmazlık başvuru formu ve eki beyanında özetle; araçta {degisken_2_1_1}, {basvuru_sahibi_beyani} belirtilerek, şimdilik {nihai_kontrol_tutari:,.2f} TL {degisken_2_1_3} davalı Şirket tarafından karşılanması talep edilmiştir. İddialara dayanak olarak, {basvuran_ek_belgeleri} dosyaya sunulmuştur."
    sigorta_kuruluşunun_iddia_delil_talepleri_paragrafi = f"Davalı Şirket vekili tarafından sunulan cevap yazısında özetle; {sigorta_sirketi_beyani} belirtilerek davanın reddi savunulmuştur." if sirket_cevap_verdi_mi else "Davalı Şirket tarafından herhangi bir cevap sunulmamıştır."
    uyusmazliga_uygulanacak_hukumler_paragrafi = "Uyuşmazlığın çözümünde 5684 sayılı Sigortacılık Kanunu, 6102 sayılı Türk Ticaret Kanunu, 6098 sayılı Türk Borçlar Kanunu, 2918 sayılı Karayolları Trafik Kanunu, 6100 sayılı Hukuk Muhakemeleri Kanunu dikkate alınmıştır."
        degisken_4_1 = f"Dosya konusu uyuşmazlık, araçta oluşan {degisken_1_1} Zorunlu Mali Sorumluluk Sigortası kapsamında tazminine ilişkindir."
    degisken_4_4 = f"Söz konusu kazanın oluşumunda davalı Şirkette sigortalı araç sürücüsünün {davali_sirkete_sigortali_arac_kusuru} kusurlu olduğu anlaşılmıştır."
    degisken_4_5 = "Uyuşmazlık konusu kazanın trafik sözleşmenin vadesi içinde gerçekleştiği tespit edilerek davanın esasına geçilmiştir."
    degisken_4_6 = "2918 Sayılı Karayolları Trafik Kanunu’nun 85’nci ve 91'nci maddeleri uyarınca işletenin sorumluluğu düzenlenmiştir."
    degisken_4_7 = "Anayasa Mahkemesi kararları doğrultusunda, değer kaybı tespitinin Borçlar Kanunu hükümleri çerçevesinde piyasa koşullarına göre belirlenmesi gerektiği değerlendirilmiştir." if "Değer Kaybı" in basvuru_konusu else ""
    degisken_4_8 = "Uyuşmazlığın çözümü için alınan ara karar ile dosyanın teknik tespiti için bilirkişiye tevdiine karar verilmiştir." if bilirkisi_raporu_alindi else ""
    temerrut_tarihi_str = (basvuru_tarihi_dt + timedelta(days=9)).strftime("%d.%m.%Y") if basvuru_tarihi_dt else ""
    basvuru_sahibi_faiz_talebi_paragrafi = f"Davalı Şirketin temerrüt tarihi olan {temerrut_tarihi_str} tarihinden itibaren yasal faiz işletilmesine karar verilmiştir." if faiz_turu != "Talep Yok" else "Faiz talebi bulunmadığından hüküm kurulmamıştır."
    degisken_4_44 = bilirkişi_raporunda_tespit_edilen_dk_tutari - davali_siket_dk_odemesi
    degisken_4_45 = bilirkişi_raporunda_tespit_edilen_hb_tutari_kdv_dahil - davali_siket_hb_odemesi
    degisken_4_38 = f"Tespit edilen {degisken_4_45:,.2f} TL bakiye hasar bedelinin kabulüne karar verilmiştir." if "Hasar Bedeli" in basvuru_konusu else f"Tespit edilen {degisken_4_44:,.2f} TL bakiye değer kaybının kabulüne karar verilmiştir."
    degisken_4_32 = f"Bilirkişi raporuna göre araç hasar zararı KDV dahil {bilirkişi_raporunda_tespit_edilen_hb_tutari_kdv_dahil:,.2f} TL, değer kaybı {bilirkişi_raporunda_tespit_edilen_dk_tutari:,.2f} TL hesaplanmıştır."
    bilirkisi_raporunun_taraflara_tebligi_paragrafi = "Bilirkişi raporu tebliğ edilmiş, dava değeri ıslah edilmiştir." if islah_var else "Bilirkişi raporu taraflara tebliğ edilmiştir."
    karar_paragrafi = f"Bilirkişi raporu denetime elverişli görülmüş and rapordaki tespiti itibar edilerek, {degisken_4_38}"
    ekspertiz_ücreti_paragrafi = f"Talep edilen {ekspertiz_ucreti_tutari:,.2f} TL ekspertiz masrafının karşılanması gerektiğine karar verilmiştir." if ekspertiz_ucreti_tutari > 0 else ""
    vekalet_ücreti_paragrafi = "5684 sayılı Kanun uyarınca vekalet ücretine hükmedilmiştir."
    faiz_hukmu = f"{temerrut_tarihi_str} tarihinden itibaren işleyecek yasal faizi ile tahsiline" if faiz_turu != "Talep Yok" else "tahsiline"
    degisken_4_50 = f"Başvuranın talebinin kabulü ile {hakem_tarafinden_kabul_edilen_hasar_bedeli_tutari:,.2f} TL hasar bedeli and {hakem_tarafinden_kabul_edilen_deger_kaybi_tutari:,.2f} TL değer kaybı tazminatının {faiz_hukmu} karar verilmiştir."
    toplam_gider = ilk_basvuru_ucreti + tebligat_ucreti + islah_tamamlama_harci + bilirkişi_ücreti_dk + bilirkişi_ücreti_hb_dk + bilirkişi_ücreti_kusur + ekspertiz_ucreti_tutari
    degisken_4_51 = f"Yapılan toplam {toplam_gider:,.2f} TL yargılama giderinin davalı Şirketten alınarak başvuran tarafa verilmesine karar verilmiştir."
    degisken_4_52 = f"AAÜT uyarınca hesaplanan {başvuran_lehine_vekalet_ucreti:,.2f} TL vekalet ücretinin davalı Şirketten alınarak başvurana verilmesine karar verilmiştir."
    yasal_yol = "miktar itibariyle KESİN olmak üzere" if nihai_kontrol_tutari <= 40000 else "kararın tebliğinden itibaren 5 iş günü içinde Komisyon nezdinde İTİRAZ yolu açık olmak üzere"
    degisken_4_62 = f"Sigortacılık Kanununun 30. maddesi uyarınca, {yasal_yol} oy birliği ile karar verildi. {datetime.now().strftime('%d.%m.%Y')}"

    try:
        doc = DocxTemplate("master_karar_sablonu.docx")
        context = {"uyusmazlik_konusu_olay_talep_paragrafi": uyusmazlik_konusu_olay_talep_paragrafi, "basvurunun_hakeme_intikaline_incelenmesine_iliskin_surec_paragrafi": basvurunun_hakeme_intikaline_incelenmesine_iliskin_surec_paragrafi, "basvuru_sahibinin_iddia_delil_talepleri_paragrafi": basvuru_sahibinin_iddia_delil_talepleri_paragrafi, "sigorta_kuruluşunun_iddia_delil_talepleri_paragrafi": sigorta_kuruluşunun_iddia_delil_talepleri_paragrafi, "uyusmazliga_uygulanacak_hukumler_paragrafi": uyusmazliga_uygulanacak_hukumler_paragrafi, "degisken_4_1": degisken_4_1, "degisken_4_4": degisken_4_4, "degisken_4_5": degisken_4_5, "degisken_4_6": degisken_4_6, "degisken_4_7": degisken_4_7, "degisken_4_8": degisken_4_8, "degisken_4_32": degisken_4_32, "bilirkisi_raporunun_taraflara_tebligi_paragrafi": bilirkisi_raporunun_taraflara_tebligi_paragrafi, "karar_paragrafi": karar_paragrafi, "ekspertiz_ücreti_paragrafi": ekspertiz_ücreti_paragrafi, "basvuru_sahibi_faiz_talebi_paragrafi": basvuru_sahibi_faiz_talebi_paragrafi, "vekalet_ücreti_paragrafi": vekalet_ücreti_paragrafi, "degisken_4_50": degisken_4_50, "degisken_4_51": degisken_4_51, "degisken_4_52": degisken_4_52, "degisken_4_62": degisken_4_62}
        doc.render(context)
        bio = io.BytesIO()
        doc.save(bio)
        st.session_state.download_data = bio.getvalue()
        st.session_state.file_ready = True
        st.success("🎉 Karar başarıyla hesaplandı and şablona işlendi!")
    except Exception as e:
        st.error(f"Şablon hatası: {e}")

if st.session_state.file_ready and st.session_state.download_data is not None:
    st.download_button(label="📥 WORD DOSYASINI İNDİR", data=st.session_state.download_data, file_name="Sigorta_Tahkim_Komisyonu_Karari_Nihai.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
