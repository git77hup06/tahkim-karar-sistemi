import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime, timedelta
import io

st.set_page_config(layout="wide", page_title="Sigorta Tahkim Otomasyonu")
st.title("⚖️ Sigorta Tahkim Komisyonu Karar Otomasyonu (Zenginleştirilmiş Hukuki Versiyon)")

if "file_ready" not in st.session_state:
    st.session_state.file_ready = False
if "download_data" not in st.session_state:
    st.session_state.download_data = None

# --- FORMA GİRİLECEK BİLGİLER (SÜTUN DÜZENİ) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 1. Başvuru ve Taraf Bilgileri")
    basvuru_konusu = st.selectbox("Başvuru Konusu", ["Değer Kaybı", "Değer Kaybı ve Kusur", "Hasar Bedeli", "Hasar Bedeli ve Kusur", "Hasar Bedeli ve Değer Kaybı", "Hasar Bedeli ve Değer Kaybı ve Kusur", "Rayiç Bedel Farkı"])
    ilk_dava_degeri_dk = st.number_input("İlk Dava Değeri - Değer Kaybı (TL) [ilk_dava_degeri_dk]", min_value=0.0, value=0.0)
    ilk_dava_degeri_hb = st.number_input("İlk Dava Değeri - Hasar Bedeli (TL) [ilk_dava_degeri_hb]", min_value=0.0, value=0.0)
    islah_var = st.checkbox("Talep Artırımı (Islah) Var mı?")
    deger_kaybi_islah_tutari = st.number_input("Değer Kaybı Islah Artış Tutarı (TL)", min_value=0.0, value=0.0) if islah_var else 0.0
    hasar_bedeli_kaybi_islah_tutari = st.number_input("Hasar Bedeli Islah Artış Tutarı (TL)", min_value=0.0, value=0.0) if islah_var else 0.0
    kaza_tarihi_dt = st.date_input("Kaza Tarihi [kaza_tarihi]")
    kaza_tarihi = kaza_tarihi_dt.strftime("%d.%m.%Y")
    basvuru_sahibine_ait_arac_plakasi = st.text_input("Başvuru Sahibine Ait Araç Plakası [basvuru_sahibine_ait_arac_plakasi]", value="34ABC123")
    davali_sirkete_sigortali_arac_plakasi = st.text_input("Davalı Şirkete Sigortalı Araç Plakası [davali_sirkete_sigortali_arac_plakasi]", value="34XYZ789")
    davalı_sigorta_sigorta_sirketi_unvani = st.text_input("Davalı Sigorta Şirketi Unvanı [davalı_sigorta_sigorta_sirketi_unvani]", value="X Sigorta A.Ş.")
    basvuru_sahibi_beyani = st.text_area("Başvuru Sahibi Beyanı Summary [basvuru_sahibi_beyani]", value="oluşan hasarın tazmin edilmesi gerektiği")
    sirket_cevap_verdi_mi = st.checkbox("Davalı Şirket Cevap Dilekçesi Sundu mu?", value=True)
    sigorta_sirketi_beyani = st.text_area("Sigorta Şirketi Cevap Özeti [sigorta_sirketi_beyani]") if sirket_cevap_verdi_mi else ""
    faiz_turu = st.selectbox("Talep Edilen Faiz Türü [faiz_turu]", ["Avans", "Yasal", "Talep Yok"])
    basvuran_ek_belgeleri = st.text_input("Başvuran Ek Belgeleri [basvuran_ek_belgeleri]", value="ekspertiz raporu, kaza fotoğrafları, servis dökümleri")
    başvurunun_niteligi = st.text_input("Başvurunun Niteliği [başvurunun_niteligi]", value="kısmi dava olarak")

with col2:
    st.subheader("🔬 2. Bilirkişi Raporu ve Ödeme Alanları")
    bilirkisi_raporu_alindi = st.checkbox("Bilirkişi Raporu Alındı mı?", value=True)
    bilirkişi_raporunda_tespit_edilen_dk_tutari = st.number_input("Raporda Tespit Edilen Değer Kaybı Tutarı", min_value=0.0) if (bilirkisi_raporu_alindi and "Değer Kaybı" in basvuru_konusu) else 0.0
    davali_siket_dk_odemesi = st.number_input("Davalı Şirket Değer Kaybı Ödemesi (TL)", min_value=0.0) if (bilirkisi_raporu_alindi and "Değer Kaybı" in basvuru_konusu) else 0.0
    bilirkişi_raporunda_tespit_edilen_hb_tutari_kdv_haric = st.number_input("Raporda Tespit Edilen HB Tutarı (KDV Hariç)", min_value=0.0) if (bilirkisi_raporu_alindi and "Hasar Bedeli" in basvuru_konusu) else 0.0
    bilirkişi_raporunda_tespit_edilen_hb_tutari_kdv_dahil = st.number_input("Raporda Tespit Edilen HB Tutarı (KDV Dahil)", min_value=0.0) if (bilirkisi_raporu_alindi and "Hasar Bedeli" in basvuru_konusu) else 0.0
    bilirkişi_raporunda_tespit_edilen_hb_tutari_iskontolu_kdv_haric = st.number_input("Raporda Tespit Edilen İskontolu HB (KDV Hariç)", min_value=0.0) if (bilirkisi_raporu_alindi and "Hasar Bedeli" in basvuru_konusu) else 0.0
    bilirkişi_raporunda_tespit_edilen_hb_tutari_iskontolu_kdv_dahil = st.number_input("Raporda Tespit Edilen İskontolu HB (KDV Dahil)", min_value=0.0) if (bilirkisi_raporu_alindi and "Hasar Bedeli" in basvuru_konusu) else 0.0
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
    bilirkişi_ücreti_hb_dk = st.number_input("Bilirkişi Ücreti - Ortak (TL)", min_value=0.0)
    bilirkişi_ücreti_kusur = st.number_input("Bilirkişi Ücreti - Kusur (TL)", min_value=0.0)
    başvuran_lehine_vekalet_ucreti = st.number_input("Başvuran Lehine Vekalet Ücreti (TL)", min_value=0.0)
    davali_sirket_lehine_vekalet_ücreti = st.number_input("Davalı Şirket Lehine Vekalet Ücreti (TL)", min_value=0.0)

toplam_islah_tutari = hasar_bedeli_kaybi_islah_tutari + deger_kaybi_islah_tutari
ilk_dava_degeri = ilk_dava_degeri_dk + ilk_dava_degeri_hb
nihai_kontrol_tutari = toplam_islah_tutari if islah_var else ilk_dava_degeri

if st.button("Karar Metnini Şablona İşle ve Hazırla"):
    # --- 1.1 ZENGİN PARAGRAF MOTORU ---
    degisken_1_1 = "değer kaybının" if "Değer Kaybı" in basvuru_konusu else "hasar bedelinin"
    uyusmazlik_konusu_olay_talep_paragrafi = f"Uyuşmazlık konusu; davalı Şirket nezdinde Karayolları Motorlu Araçlar Zorunlu Mali Sorumluluk Sigorta Poliçesi ile teminat altına alınan {davali_sirkete_sigortali_arac_plakasi} plakalı aracın {kaza_tarihi} tarihinde karıştığı kaza sonucunda başvuru sahibine ait {basvuru_sahibine_ait_arac_plakasi} plakalı araçta oluşan {degisken_1_1} Zorunlu Mali Sorumluluk Sigortası genel şartları ve poliçe limitleri çerçevesinde tazmin edilmesi talebine ilişkindir."

    # --- 1.2 ZENGİN PARAGRAF MOTORU ---
    degisken_1_3 = "Hakemliğimizce" if nihai_kontrol_tutari < 122000 else "Heyetimizce"
    degisken_1_2 = "ıslah edilen ve konusuz kaldığı anlaşılan" if (islah_var and (davali_siket_dk_odemesi > 0 or davali_siket_hb_odemesi > 0)) else "ıslah edilen" if islah_var else "konusuz kaldığı anlaşılan" if (davali_siket_dk_odemesi > 0 or davali_siket_hb_odemesi > 0) else ""
    metin_1_2 = f"yargılama sırasında dosya kapsamından alınan bilirkişi raporunun taraflara tebliği sonrasında {degisken_1_2} uyuşmazlık, tarafların iddia, savunma ve delilleri hep birlikte değerlendirilerek {degisken_1_3} esastan incelenmiş ve karara bağlanmıştır." if bilirkisi_raporu_alindi else f"dosya muhteviyatı, mevcut delil durumu ve ilgili mevzuat çerçevesinde uyuşmazlık {degisken_1_3} esastan karara bağlanmıştır."
    basvurunun_hakeme_intikaline_incelenmesine_iliskin_surec_paragrafi = f"Başvuru sahibi talebinin davalı tarafından karşılanmaması nedeniyle ortaya çıkan uyuşmazlığın çözümü için tahkim yargılamasına başvurulmuş, {metin_1_2}"

    # --- 2.1 ZENGİN PARAGRAF MOTORU ---
    degisken_2_1_4 = "avans faizi ile birlikte" if faiz_turu == "Avans" else "yasal faizi ile birlikte" if faiz_turu == "Yasal" else " "
    
    if basvuru_konusu in ["Değer Kaybı", "Değer Kaybı ve Kusur"]:
        degisken_2_1_1 = "oluşan hasar nedeniyle aracın değer kaybına uğradığı"
    elif basvuru_konusu in ["Hasar Bedeli", "Hasar Bedeli ve Kusur"]:
        degisken_2_1_1 = "hasar meydana geldiği"
    else:
        degisken_2_1_1 = "hasar meydana geldiği ve aracın değer kaybına uğradığı"

    nitelik_ve_faiz = f"{başvurunun_niteligi} {degisken_2_1_4}".strip()
    
    degisken_2_1_3 = f"değer kaybı bedelinin {nitelik_ve_faiz}"
    if "Değer Kaybı" in basvuru_konusu and "Hasar Bedeli" not in basvuru_konusu and ekspertiz_ucreti_tutari > 0:
        degisken_2_1_3 = f"değer kaybı bedelinin {nitelik_ve_faiz} ve {ekspertiz_ucreti_tutari:,.2f} TL ekspertiz ücretinin yargılama giderleri arasında"
        
    if "Hasar Bedeli" in basvuru_konusu and "Değer Kaybı" not in basvuru_konusu:
        degisken_2_1_3 = f"hasar bedelinin {nitelik_ve_faiz}"
        if ekspertiz_ucreti_tutari > 0:
            degisken_2_1_3 = f"hasar bedelinin {nitelik_ve_faiz} ve {ekspertiz_ucreti_tutari:,.2f} TL ekspertiz ücretinin yargılama giderleri arasında"
            
    if basvuru_konusu == "Rayiç Bedel Farkı":
        degisken_2_1_3 = f"hasar bedelinin (rayiç bedel farkının) {nitelik_ve_faiz}"
        if ekspertiz_ucreti_tutari > 0:
            degisken_2_1_3 = f"hasar bedelinin (rayiç bedel farkının) {nitelik_ve_faiz} ve {ekspertiz_ucreti_tutari:,.2f} TL ekspertiz ücretinin yargılama giderleri arasında"
            
    if "Hasar Bedeli" in basvuru_konusu and "Değer Kaybı" in basvuru_konusu:
        degisken_2_1_3 = f"hasar bedeli ve değer kaybının {nitelik_ve_faiz}"
        if ekspertiz_ucreti_tutari > 0:
            degisken_2_1_3 = f"hasar bedeli ve değer kaybı bedelinin {nitelik_ve_faiz} ve {ekspertiz_ucreti_tutari:,.2f} TL ekspertiz ücretinin yargılama giderleri arasında"

    basvuru_sahibinin_iddia_delil_talepleri_paragrafi = f"Başvuru sahibi vekili tarafından Sigorta Tahkim Komisyonu’na yapılan uyuşmazlık başvuru formu ve eki beyanında özetle; Davalı Şirket tarafından Karayolları Motorlu Araçlar Zorunlu Mali Sorumluluk Sigorta Poliçesi ile sigortalı {davali_sirkete_sigortali_arac_plakasi} aracın karıştığı kaza neticesinde müvekkiline ait {basvuru_sahibine_ait_arac_plakasi} plakalı araçta {degisken_2_1_1}, {basvuru_sahibi_beyani} belirtilerek, fazlaya ilişkin hakları saklı kalmak üzere şimdilik {ilk_dava_degeri:,.2f} TL {degisken_2_1_3} davalı Şirket tarafından karşılanması talep edilmiştir. Vekaletname ile birlikte iddialara dayanak olarak, davalı şirkete gönderilen talep yazısı, {basvuran_ek_belgeleri}, hasarlı araç fotoğrafları, kaza tespit tutanağı, araç ruhsatı ve sair deliller dosyaya sunulmuştur."

    if sirket_cevap_verdi_mi:
        sigorta_kuruluşunun_iddia_delil_talepleri_paragrafi = f"Davalı {davalı_sigorta_sigorta_sirketi_unvani} vekili tarafından Sigorta Tahkim Komisyonu’na sunulan cevap yazısında özetle; {sigorta_sirketi_beyani} hususları ileri sürülerek, davanın esastan reddine karar verilmesi savunulmuştur."
    else:
        sigorta_kuruluşunun_iddia_delil_talepleri_paragrafi = f"Davalı {davalı_sigorta_sigorta_sirketi_unvani} tarafından Sigorta Tahkim Komisyonu’na yasal süresi içerisinde herhangi bir cevap dilekçesi veya savunma sunulmamıştır."

    uyusmazliga_uygulanacak_hukumler_paragrafi = "Uyuşmazlığın hukuki çözümünde; 5684 sayılı Sigortacılık Kanunu, 6102 sayılı Türk Ticaret Kanunu, 6098 sayılı Türk Borçlar Kanunu Sorumluluk Hükümleri, 2918 sayılı Karayolları Trafik Kanunu, Karayolları Motorlu Araçlar Zorunlu Mali Sorumluluk Sigortası Genel Şartları, 6100 sayılı Hukuk Muhakemeleri Kanunu ve tahkim yargılamasına ilişkin sair ilgili mevzuat dikkate alınmıştır."

    degisken_4_2 = "hasar bedeli ve değer kaybının"
    if basvuru_konusu in ["Değer Kaybı", "Değer Kaybı ve Kusur"]:
        degisken_4_2 = "değer kaybının"
    elif basvuru_konusu in ["Hasar Bedeli", "Hasar Bedeli ve Kusur"]:
        degisken_4_2 = "hasar bedelinin"
        
    degisken_4_1 = f"Dosya konusu uyuşmazlık, başvuru sahibine ait {basvuru_sahibine_ait_arac_plakasi} plakalı araçta meydana gelen {degisken_4_2} Karayolları Motorlu Araçlar Zorunlu Mali Sorumluluk Sigorta Poliçesi kapsamında davalı Şirket sorumluluğunda tazmini talebine ilişkindir."
    degisken_4_4 = f"Dosya kapsamında yer alan kaza tespit tutanağı ve kusur incelemelerine göre; söz konusu kazanın oluşumunda davalı Şirkette sigortalı araç sürücüsünün {davali_sirkete_sigortali_arac_kusuru}, başvuru sahibi araç sürücüsünün ise %{basvuru_sahibine_ait_arac_kusuru_orani} oranında kusurlu olduğu anlaşılmıştır."
    degisken_4_5 = "Uyuşmazlık konusu kazanın trafik sigorta sözleşmesinin yürürlük ve vade tarihi sınırları içinde gerçekleştiği, tarafların yasal taraf ve dava ehliyetlerinin tam olduğu tespit edilerek davanın esasına geçilmiştir."
    degisken_4_6 = "2918 Sayılı KTK’nun 85/1 maddesinde, bir motorlu aracın işletilmesi bir kimsenin ölümüne veya yaralanmasına yahut bir şeyin zarara uğramasına sebep olursa, motorlu aracın işleteninin bu zarardan sorumlu olacağı; aynı Kanunun 91. maddesinde ise işletenlerin bu sorumluluklarını sigorta ettirmekle yükümlü oldukları hüküm altına alınmıştır."
    degisken_4_7 = "Anayasa Mahkemesi’nin kararları doğrultusunda, değer kaybı zararının Borçlar Kanunu tazminat ilkeleri çerçevesinde, aracın kazadan önceki piyasa rayiç değeri ile kazadan sonraki onarılmış halindeki piyasa rayiç değeri arasındaki farka göre hesaplanması gerekmektedir." if "Değer Kaybı" in basvuru_konusu else ""
    degisken_4_8 = "Uyuşmazlığın çözümü, parça iskonto indirimi ve işçilik piyasa koşullarının teknik tespiti amacıyla dosya uzman bilirkişiye tevdi edilerek rapor tanzim edilmesi istenmiştir." if bilirkisi_raporu_alindi else ""

    temerrut_tarihi_str = ""
    if faiz_turu != "Talep Yok" and basvuru_tarihi_dt:
        basvuru_tarihi_str = basvuru_tarihi_dt.strftime("%d.%m.%Y")
        temerrut_dt = basvuru_tarihi_dt + timedelta(days=9)
        temerrut_tarihi_str = temerrut_dt.strftime("%d.%m.%Y")
        basvuru_sahibi_faiz_talebi_paragrafi = f"Davalı Şirkete {basvuru_tarihi_str} tarihinde başvuru yapıldığı anlaşılmakla, Karayolları Trafik Kanunu'nun 99/1 maddesine istinaden davalı Şirketin temerrüt tarihi olan {temerrut_tarihi_str} tarihinden itibaren yasal faiz işletilmesine karar verilmiştir."
    else:
        basvuru_sahibi_faiz_talebi_paragrafi = "Başvuru sahibi vekilinin faiz talebi bulunmadığından, taleple bağlı kalınarak bu yönde hüküm kurulmamıştır."

    degisken_4_44 = bilirkişi_raporunda_tespit_edilen_dk_tutari - davali_siket_dk_odemesi
    degisken_4_45 = bilirkişi_raporunda_tespit_edilen_hb_tutari_kdv_dahil - davali_siket_hb_odemesi
    fark_hb_haric = bilirkişi_raporunda_tespit_edilen_hb_tutari_kdv_haric - davali_siket_hb_odemesi
    
    degisken_4_32 = f"Dosyaya sunulan uzman bilirkişi raporuna göre; {basvuru_sahibine_ait_arac_plakasi} plakalı araçta uygulanan {bilirkişi_raporunda_uygulan_yedek_parca_iskonto_orani} yedek parça ve {bilirkişi_raporunda_uygulan_iscilik_iskonto_orani} işçilik iskontoları neticesinde hasar zararı KDV hariç {bilirkişi_raporunda_tespit_edilen_hb_tutari_kdv_haric:,.2f} TL, KDV dahil {bilirkişi_raporunda_tespit_edilen_hb_tutari_kdv_dahil:,.2f} TL; reel değer kaybı ise {bilirkişi_raporunda_tespit_edilen_dk_tutari:,.2f} TL olarak hesaplanmıştır."
    
    degisken_4_38 = f"tespit edilen bakiye {degisken_4_45:,.2f} TL bakiye hasar bedelinin kabulüne karar verilmiştir." if "Hasar Bedeli" in basvuru_konusu else f"tespit edilen {degisken_4_44:,.2f} TL bakiye değer kaybının kabulüne karar verilmiştir."
    if "Hasar Bedeli" in basvuru_konusu and "Değer Kaybı" in basvuru_konusu:
        degisken_4_38 = f"{degisken_4_45:,.2f} TL bakiye hasar bedeli ve {degisken_4_44:,.2f} TL bakiye değer kaybı olmak üzere toplam talebin kabulüne karar verilmiştir."

    bilirkisi_raporunun_taraflara_tebligi_paragrafi = f"Uzman bilirkişi raporu taraflara usulüne uygun tebliğ edilmiş olup, davalı Şirket vekili rapora karşı beyanda bulunmamış, başvuran vekili ise rapor doğrultusunda dava değerini {toplam_islah_tutari:,.2f} TL olarak ıslah etmiştir." if islah_var else "Bilirkişi raporu taraflara tebliğ edilmiş, yasal süre içerisinde rapora karşı denetimi sarsacak mahiyette bir itiraz ileri sürülmemiştir."
    karar_paragrafi = f"Bilirkişi raporunun mevzuata, kaza illiyet bağına ve denetime elverişli olduğu saptanarak rapora itibar edilmiş ve neticeden; {degisken_4_38}"

    ekspertiz_ücreti_paragrafi = f"Başvuru sahibi vekili tarafından talep edilen {ekspertiz_ucreti_tutari:,.2f} TL ekspertiz masrafının TTK madde 1426 kapsamında makul olduğuna ve davalı Şirket tarafından yargılama giderleri arasında karşılanması gerektiğine karar verilmiştir." if ekspertiz_ucreti_tutari > 0 else ""
    vekalet_ücreti_paragrafi = "5684 sayılı Sigortacılık Kanunu’nun 30’ncu maddesi, 1136 sayılı Avukatlık Kanunu’nun 164’ünчү maddesi ile AAÜT’nin 17.maddesinin 2.fıkrası ve Sigortacılıkta Tahkime İlişkin Yönetmeliğin 16. maddesinin 13. fıkrası gereğince vekalet ücretine hükmedilmiştir."

    faiz_hukmu = f"{temerrut_tarihi_str} tarihinden itibaren işleyecek yasal faizi ile birlikte davalı Şikten tahsiline" if faiz_turu != "Talep Yok" else "davalı Şirketten tahsiline"
    if basvuru_konusu in ["Değer Kaybı", "Değer Kaybı ve Kusur"]:
        degisken_4_50 = f"Başvuranın değer kaybı talebinin kabulü ile bakiye {hakem_tarafinden_kabul_edilen_deger_kaybi_tutari:,.2f} TL tazminatın {faiz_hukmu} karar verilmiştir."
    elif basvuru_konusu in ["Hasar Bedeli", "Hasar Bedeli ve Kusur"]:
        degisken_4_50 = f"Başvuranın hasar bedeli talebinin kabulü ile bakiye {hakem_tarafinden_kabul_edilen_hasar_bedeli_tutari:,.2f} TL tazminatın {faiz_hukmu} karar verilmiştir."
    else:
  
