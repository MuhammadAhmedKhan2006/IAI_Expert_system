import streamlit as st
import sqlite3
import datetime

st.set_page_config(page_title="IAI Medical Expert System", page_icon="🩺")
DB_NAME = "doctor_ai.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("CREATE TABLE IF NOT EXISTS consultations (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, symptoms TEXT, report_values TEXT, suggestion TEXT)")
    conn.commit(); conn.close()

def save_to_db(symptoms, report_values, suggestion):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT INTO consultations (timestamp, symptoms, report_values, suggestion) VALUES (?, ?, ?, ?)", (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(symptoms), str(report_values), suggestion))
    conn.commit(); conn.close()

init_db()
s = st.session_state
if 'step' not in s:
    s.step = 'start'; s.patient_data = {}; s.report_data = {}; s.risk = 0; s.reasons = []; s.saved = False; s.show_data = False

st.title("🩺 IAI Expert System: Medical Assistant")
st.warning("⚠️ Disclaimer: Yeh DECISION SUPPORT tool hai, real doctor nahi. Hamesha doctor se checkup karwayein.")

conn = sqlite3.connect(DB_NAME)
db_count = conn.execute("SELECT COUNT(*) FROM consultations").fetchone()[0]
conn.close()
st.sidebar.write("📊 Saved consultations: " + str(db_count))
if st.sidebar.button("📂 View Saved Data", key="viewdata"):
    s.show_data = not s.show_data
    st.rerun()
if s.show_data:
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute("SELECT id, timestamp, symptoms, report_values, suggestion FROM consultations ORDER BY id DESC").fetchall()
    conn.close()
    st.subheader("📂 Saved Consultations")
    if len(rows) == 0: st.write("Abhi koi data save nahi hua.")
    for r in rows:
        st.write("**#" + str(r[0]) + "** | " + str(r[1])); st.write("Symptoms: " + str(r[2])); st.write("Reports: " + str(r[3])); st.write("Suggestion: " + str(r[4])); st.divider()

step = s.step

# ================= START =================
if step == 'start':
    st.subheader("Aapko kya problem hai? (Select main complaint)")
    a, b = st.columns(2)
    if a.button("🤧 Cough / Fever (Khansi / Bukhar)", key="p1"): s.patient_data['main_complaint'] = "Cough/Fever"; s.step = 'cf1'; st.rerun()
    if b.button("💔 Chest Pain (Seene mein dard)", key="p2"): s.patient_data['main_complaint'] = "Chest Pain"; s.step = 'cp1'; st.rerun()
    c, d = st.columns(2)
    if c.button("🤢 Stomach Pain (Pet dard)", key="p3"): s.patient_data['main_complaint'] = "Stomach Pain"; s.step = 'sp1'; st.rerun()
    if d.button("🤕 Headache (Sar dard)", key="p4"): s.patient_data['main_complaint'] = "Headache"; s.step = 'hd1'; st.rerun()

# ================= PATH 1: COUGH / FEVER =================
elif step == 'cf1':
    st.subheader("🫁 [Cough/Fever] Q1: Kya aapko 2 hafte se zyada khansi (cough) hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf1y"):
        s.patient_data['cough_2wk'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Cough more than 2 weeks: +15 risk"); s.step = 'cf2'; st.rerun()
    if c2.button("No / Nahi", key="cf1n"): s.patient_data['cough_2wk'] = "No"; s.step = 'cf2'; st.rerun()
elif step == 'cf2':
    st.subheader("🫁 Q2: Raat ko paseena (night sweats) ya wazan kam ho raha hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf2y"):
        s.patient_data['night_sweats_weight_loss'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Night sweats / weight loss: +15 risk"); s.step = 'cf3'; st.rerun()
    if c2.button("No / Nahi", key="cf2n"): s.patient_data['night_sweats_weight_loss'] = "No"; s.step = 'cf3'; st.rerun()
elif step == 'cf3':
    st.subheader("🫁 Q3: Khansi mein khoon (blood in cough) aata hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf3y"):
        s.patient_data['blood_cough'] = "Yes"; s.risk = s.risk + 25; s.reasons.append("Blood in cough: +25 risk"); s.step = 'cf4'; st.rerun()
    if c2.button("No / Nahi", key="cf3n"): s.patient_data['blood_cough'] = "No"; s.step = 'cf4'; st.rerun()
elif step == 'cf4':
    st.subheader("🫁 Q4: Kya saans phoolti hai (breathlessness)?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf4y"):
        s.patient_data['breathless'] = "Yes"
        if s.patient_data['blood_cough'] == "Yes": s.risk = max(s.risk + 40, 70); s.reasons.append("Breathlessness together with blood in cough: risk raised to at least 70"); s.step = 'end'
        else: s.risk = s.risk + 15; s.reasons.append("Breathlessness: +15 risk"); s.step = 'cf5'
        st.rerun()
    if c2.button("No / Nahi", key="cf4n"): s.patient_data['breathless'] = "No"; s.step = 'cf5'; st.rerun()
elif step == 'cf5':
    st.subheader("🫁 Q5: Kya bukhar 100.4°F se zyada hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf5y"):
        s.patient_data['fever_high'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Fever above 100.4F: +10 risk"); s.step = 'cf_plt'; st.rerun()
    if c2.button("No / Nahi", key="cf5n"): s.patient_data['fever_high'] = "No"; s.step = 'cf_plt'; st.rerun()
elif step == 'cf_plt':
    st.subheader("📋 Q6 (Report): Platelet count (normal 150000-450000)")
    plt = st.number_input("Apni report se platelet count likhein", min_value=0, max_value=1000000, value=250000, step=1000, key="plt_in")
    if st.button("Submit Report", key="plt_btn"):
        s.report_data['platelets'] = plt
        if plt < 20000: s.risk = max(s.risk + 60, 70); s.reasons.append("Platelets critically low (" + str(plt) + "): risk raised to at least 70"); s.step = 'end'
        elif plt < 150000: s.risk = s.risk + 15; s.reasons.append("Platelets low (" + str(plt) + "): +15 risk"); s.step = 'cf6'
        else: s.step = 'cf6'
        st.rerun()
elif step == 'cf6':
    st.subheader("🫁 Q7: Kya aapne TB ka test karwaya hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf6y"): s.patient_data['tb_test_done'] = "Yes"; s.step = 'cf7'; st.rerun()
    if c2.button("No / Nahi", key="cf6n"):
        s.patient_data['tb_test_done'] = "No"; s.risk = max(s.risk + 20, 40); s.reasons.append("Relevant test (TB) not done yet: risk raised to at least 40, test zaroori hai"); s.step = 'end'; st.rerun()
elif step == 'cf7':
    st.subheader("🫁 Q8: Kya TB test positive aaya?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf7y"):
        s.patient_data['tb_positive'] = "Yes"; s.risk = max(s.risk + 30, 40); s.reasons.append("Test report positive (needs doctor confirmation): risk raised to at least 40"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="cf7n"): s.patient_data['tb_positive'] = "No"; s.step = 'cf8'; st.rerun()
elif step == 'cf8':
    st.subheader("🫁 Q9: Test negative aane ke bawajood kya symptoms abhi bhi hain? (False negative ho sakta hai)"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf8y"):
        s.patient_data['symptoms_despite_negative'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Symptoms continue despite negative test (false negative possible): +15 risk"); s.step = 'cf_mg'; st.rerun()
    if c2.button("No / Nahi", key="cf8n"): s.patient_data['symptoms_despite_negative'] = "No"; s.step = 'cf11'; st.rerun()
elif step == 'cf_mg':
    st.subheader("📋 Q10 (Report): Magnesium level (normal 1.7-2.2 mg/dL)")
    mg = st.number_input("Apni report se magnesium likhein", min_value=0.0, max_value=10.0, value=2.0, step=0.1, key="mg_in")
    if st.button("Submit Report", key="mg_btn"):
        s.report_data['magnesium'] = mg
        if mg < 1.7: s.risk = s.risk + 10; s.reasons.append("Magnesium low (" + str(mg) + "): +10 risk"); s.step = 'cf9'
        else: s.step = 'cf9'
        st.rerun()
elif step == 'cf9':
    st.subheader("🫁 Q11: Kya aap roz 6 ghante se kam sote hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf9y"):
        s.patient_data['sleep_less_6'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Sleep less than 6 hours: +10 risk"); s.step = 'cf10'; st.rerun()
    if c2.button("No / Nahi", key="cf9n"): s.patient_data['sleep_less_6'] = "No"; s.step = 'cf10'; st.rerun()
elif step == 'cf10':
    st.subheader("🫁 Q12: Kya bukhar ya peela/hara balgham (yellow-green phlegm) hai? (Body infection)"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf10y"):
        s.patient_data['infection_phlegm'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Fever / yellow-green phlegm (possible infection): +15 risk"); s.step = 'cf11'; st.rerun()
    if c2.button("No / Nahi", key="cf10n"): s.patient_data['infection_phlegm'] = "No"; s.step = 'cf11'; st.rerun()
elif step == 'cf11':
    st.subheader("🫁 Q13: Kya ghar mein koi TB ka mareez hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf11y"):
        s.patient_data['tb_contact'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("TB patient at home (contact risk): +15 risk"); s.step = 'cf12'; st.rerun()
    if c2.button("No / Nahi", key="cf11n"): s.patient_data['tb_contact'] = "No"; s.step = 'cf12'; st.rerun()
elif step == 'cf12':
    st.subheader("🫁 Q14: Kya aap smoking karte hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf12y"):
        s.patient_data['smoking'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Smoking: +5 risk"); s.step = 'cf13'; st.rerun()
    if c2.button("No / Nahi", key="cf12n"): s.patient_data['smoking'] = "No"; s.step = 'cf13'; st.rerun()
elif step == 'cf13':
    st.subheader("🫁 Q15: Kya aapko asthma ya allergy hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf13y"):
        s.patient_data['asthma_allergy'] = "Yes"; s.reasons.append("Asthma/allergy history: cough may have a non-infectious cause (no risk added)"); s.step = 'cf14'; st.rerun()
    if c2.button("No / Nahi", key="cf13n"): s.patient_data['asthma_allergy'] = "No"; s.step = 'cf14'; st.rerun()
elif step == 'cf14':
    st.subheader("🫁 Q16: Kya khansi ke saath seene mein dard (chest pain) hota hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf14y"):
        s.patient_data['chest_pain_with_cough'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Chest pain with cough: +10 risk"); s.step = 'cf15'; st.rerun()
    if c2.button("No / Nahi", key="cf14n"): s.patient_data['chest_pain_with_cough'] = "No"; s.step = 'cf15'; st.rerun()
elif step == 'cf15':
    st.subheader("🫁 Q17: Kya sunghne ya zaiqa (smell / taste) ki salahiyat kam hui hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf15y"):
        s.patient_data['smell_taste_loss'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Loss of smell / taste: +5 risk"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="cf15n"): s.patient_data['smell_taste_loss'] = "No"; s.step = 'end'; st.rerun()

# ================= PATH 2: CHEST PAIN =================
elif step == 'cp1':
    st.subheader("💔 [Chest Pain] Q1: Kya seene mein pressure / squeezing (dabao) mehsoos hota hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp1y"):
        s.patient_data['pressure_pain'] = "Yes"; s.risk = s.risk + 25; s.reasons.append("Chest pressure / squeezing: +25 risk"); s.step = 'cp2'; st.rerun()
    if c2.button("No / Nahi", key="cp1n"): s.patient_data['pressure_pain'] = "No"; s.step = 'cp2'; st.rerun()
elif step == 'cp2':
    st.subheader("💔 Q2: Kya dard bazu, jabde (jaw) ya peeth tak phailta hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp2y"):
        s.patient_data['pain_spreads'] = "Yes"; s.risk = s.risk + 20; s.reasons.append("Pain spreading to arm/jaw/back: +20 risk"); s.step = 'cp3'; st.rerun()
    if c2.button("No / Nahi", key="cp2n"): s.patient_data['pain_spreads'] = "No"; s.step = 'cp3'; st.rerun()
elif step == 'cp3':
    st.subheader("💔 Q3: Kya paseena, ulti jaisa mann (nausea) ya chakkar aa rahe hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp3y"):
        s.patient_data['sweat_nausea_dizzy'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Sweating / nausea / dizziness: +15 risk"); s.step = 'cp4'; st.rerun()
    if c2.button("No / Nahi", key="cp3n"): s.patient_data['sweat_nausea_dizzy'] = "No"; s.step = 'cp4'; st.rerun()
elif step == 'cp4':
    st.subheader("💔 Q4: Kya saans phoolti hai (breathlessness)?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp4y"):
        s.patient_data['breathless'] = "Yes"
        if s.patient_data['pressure_pain'] == "Yes": s.risk = max(s.risk + 40, 70); s.reasons.append("Breathlessness together with chest pressure: risk raised to at least 70"); s.step = 'end'
        else: s.risk = s.risk + 10; s.reasons.append("Breathlessness: +10 risk"); s.step = 'cp5'
        st.rerun()
    if c2.button("No / Nahi", key="cp4n"): s.patient_data['breathless'] = "No"; s.step = 'cp5'; st.rerun()
elif step == 'cp5':
    st.subheader("💔 Q5: Kya dard 20 minute se zyada raha?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp5y"):
        s.patient_data['pain_over_20min'] = "Yes"; s.risk = s.risk + 20; s.reasons.append("Pain lasting more than 20 minutes: +20 risk"); s.step = 'cp_bp'; st.rerun()
    if c2.button("No / Nahi", key="cp5n"): s.patient_data['pain_over_20min'] = "No"; s.step = 'cp_bp'; st.rerun()
elif step == 'cp_bp':
    st.subheader("📋 Q6 (Report): Systolic BP (normal 90-139 mmHg)")
    bp = st.number_input("Apna systolic BP likhein", min_value=40, max_value=300, value=120, step=1, key="cpbp_in")
    if st.button("Submit Report", key="cpbp_btn"):
        s.report_data['systolic_bp'] = bp
        if bp >= 180: s.risk = max(s.risk + 60, 70); s.reasons.append("BP very high (" + str(bp) + "): risk raised to at least 70"); s.step = 'end'
        elif bp < 90: s.risk = s.risk + 20; s.reasons.append("BP low (" + str(bp) + "): +20 risk"); s.step = 'cp6'
        else: s.step = 'cp6'
        st.rerun()
elif step == 'cp6':
    st.subheader("💔 Q7: Kya aapne ECG karwaya hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp6y"): s.patient_data['ecg_done'] = "Yes"; s.step = 'cp7'; st.rerun()
    if c2.button("No / Nahi", key="cp6n"):
        s.patient_data['ecg_done'] = "No"
        if s.risk >= 40: s.reasons.append("ECG not done while risk is already high: urgent ECG and doctor visit needed"); s.step = 'end'
        else: s.step = 'cp8'
        st.rerun()
elif step == 'cp7':
    st.subheader("💔 Q8: Kya ECG report abnormal aayi?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp7y"):
        s.patient_data['ecg_abnormal'] = "Yes"; s.risk = max(s.risk + 30, 70); s.reasons.append("Abnormal ECG report: risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="cp7n"): s.patient_data['ecg_abnormal'] = "No"; s.step = 'cp8'; st.rerun()
elif step == 'cp8':
    st.subheader("💔 Q9: Kya hilne-julne ya saans lene par dard barh jata hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp8y"):
        s.patient_data['worse_with_movement'] = "Yes"; s.reasons.append("Pain worse with movement: may be muscle strain (no risk added)"); s.step = 'cp9'; st.rerun()
    if c2.button("No / Nahi", key="cp8n"):
        s.patient_data['worse_with_movement'] = "No"; s.risk = s.risk + 10; s.reasons.append("Pain NOT related to movement: +10 risk"); s.step = 'cp9'; st.rerun()
elif step == 'cp9':
    st.subheader("💔 Q10: Kya aap roz aspirin ya blood thinner lete hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp9y"):
        s.patient_data['aspirin_thinner'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Daily aspirin / blood thinner: +10 risk"); s.step = 'cp10'; st.rerun()
    if c2.button("No / Nahi", key="cp9n"): s.patient_data['aspirin_thinner'] = "No"; s.step = 'cp10'; st.rerun()
elif step == 'cp10':
    st.subheader("💔 Q11: Kya aapko diabetes (sugar) hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp10y"):
        s.patient_data['diabetes'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Diabetes: +10 risk"); s.step = 'cp11'; st.rerun()
    if c2.button("No / Nahi", key="cp10n"): s.patient_data['diabetes'] = "No"; s.step = 'cp11'; st.rerun()
elif step == 'cp11':
    st.subheader("💔 Q12: Kya aapko high BP ki history hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp11y"):
        s.patient_data['high_bp_history'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("High BP history: +10 risk"); s.step = 'cp12'; st.rerun()
    if c2.button("No / Nahi", key="cp11n"): s.patient_data['high_bp_history'] = "No"; s.step = 'cp12'; st.rerun()
elif step == 'cp12':
    st.subheader("💔 Q13: Kya family mein kisi ko dil ki bimari hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp12y"):
        s.patient_data['family_heart'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Family history of heart disease: +10 risk"); s.step = 'cp13'; st.rerun()
    if c2.button("No / Nahi", key="cp12n"): s.patient_data['family_heart'] = "No"; s.step = 'cp13'; st.rerun()
elif step == 'cp13':
    st.subheader("💔 Q14: Kya aap smoking karte hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp13y"):
        s.patient_data['smoking'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Smoking: +5 risk"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="cp13n"): s.patient_data['smoking'] = "No"; s.step = 'end'; st.rerun()

# ================= PATH 3: STOMACH PAIN =================
elif step == 'sp1':
    st.subheader("🤢 [Stomach] Q1: Pet dard kab hota hai?"); c1, c2, c3 = st.columns(3)
    if c1.button("Khali pet (Empty)", key="sp1a"): s.patient_data['pain_timing'] = "Empty stomach"; s.step = 'sp2'; st.rerun()
    if c2.button("Khane ke baad", key="sp1b"): s.patient_data['pain_timing'] = "After eating"; s.step = 'sp3'; st.rerun()
    if c3.button("Hamesha (Always)", key="sp1c"): s.patient_data['pain_timing'] = "Always"; s.step = 'sp4'; st.rerun()
elif step == 'sp2':
    st.subheader("🤢 Q2: Kya khana khane se dard kam hota hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp2y"):
        s.patient_data['relieved_by_food'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Pain relieved by food (pattern doctor should check): +15 risk"); s.step = 'sp5'; st.rerun()
    if c2.button("No / Nahi", key="sp2n"): s.patient_data['relieved_by_food'] = "No"; s.step = 'sp5'; st.rerun()
elif step == 'sp3':
    st.subheader("🤢 Q3: Kya seene mein jalan (heartburn) hoti hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp3y"): s.patient_data['heartburn'] = "Yes"; s.reasons.append("Pain after eating with heartburn: acidity is possible (no risk added)"); s.step = 'sp5'; st.rerun()
    if c2.button("No / Nahi", key="sp3n"): s.patient_data['heartburn'] = "No"; s.reasons.append("Pain after eating without heartburn: gas is possible (no risk added)"); s.step = 'sp5'; st.rerun()
elif step == 'sp4':
    st.subheader("🤢 Q4: Kya kala stool (black stool) ya khoon ki ulti (vomiting blood) hui?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp4y"):
        s.patient_data['black_stool_blood_vomit'] = "Yes"; s.risk = max(s.risk + 35, 70); s.reasons.append("Black stool / vomiting blood: risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="sp4n"): s.patient_data['black_stool_blood_vomit'] = "No"; s.step = 'sp5'; st.rerun()
elif step == 'sp5':
    st.subheader("🤢 Q5: Kya aap painkiller (ibuprofen / aspirin) use karte hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp5y"):
        s.patient_data['painkiller_use'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Painkiller (ibuprofen/aspirin) use: +10 risk"); s.step = 'sp_hb'; st.rerun()
    if c2.button("No / Nahi", key="sp5n"): s.patient_data['painkiller_use'] = "No"; s.step = 'sp_hb'; st.rerun()
elif step == 'sp_hb':
    st.subheader("📋 Q6 (Report): Hemoglobin (normal 12-17 g/dL)")
    hb = st.number_input("Apni report se hemoglobin likhein", min_value=0.0, max_value=25.0, value=13.0, step=0.1, key="hb_in")
    if st.button("Submit Report", key="hb_btn"):
        s.report_data['hemoglobin'] = hb
        if hb < 8: s.risk = max(s.risk + 40, 70); s.reasons.append("Hemoglobin very low (" + str(hb) + "): risk raised to at least 70"); s.step = 'end'
        elif hb < 12: s.risk = s.risk + 15; s.reasons.append("Hemoglobin low (" + str(hb) + "): +15 risk"); s.step = 'sp6'
        else: s.step = 'sp6'
        st.rerun()
elif step == 'sp6':
    st.subheader("🤢 Q7: Kya bohat shadeed dard + pet sakht (rigid) + bukhar hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp6y"):
        s.patient_data['severe_rigid_fever'] = "Yes"; s.risk = max(s.risk + 40, 70); s.reasons.append("Severe pain + rigid abdomen + fever: risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="sp6n"): s.patient_data['severe_rigid_fever'] = "No"; s.step = 'sp7'; st.rerun()
elif step == 'sp7':
    st.subheader("🤢 Q8: Kya bagair wajah wazan kam ho raha hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp7y"):
        s.patient_data['weight_loss'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Unexplained weight loss: +15 risk"); s.step = 'sp8'; st.rerun()
    if c2.button("No / Nahi", key="sp7n"): s.patient_data['weight_loss'] = "No"; s.step = 'sp8'; st.rerun()
elif step == 'sp8':
    st.subheader("🤢 Q9: Kya baar baar ulti (repeated vomiting) ho rahi hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp8y"):
        s.patient_data['repeated_vomiting'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Repeated vomiting: +10 risk"); s.step = 'sp9'; st.rerun()
    if c2.button("No / Nahi", key="sp8n"): s.patient_data['repeated_vomiting'] = "No"; s.step = 'sp9'; st.rerun()
elif step == 'sp9':
    st.subheader("🤢 Q10: Kya 3 din se zyada dast (diarrhea) hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp9y"):
        s.patient_data['diarrhea_3days'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Diarrhea more than 3 days: +10 risk"); s.step = 'sp10'; st.rerun()
    if c2.button("No / Nahi", key="sp9n"): s.patient_data['diarrhea_3days'] = "No"; s.step = 'sp10'; st.rerun()
elif step == 'sp10':
    st.subheader("🤢 Q11: Kya aankhein ya skin peeli (yellow) ho rahi hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp10y"):
        s.patient_data['yellow_eyes_skin'] = "Yes"; s.risk = s.risk + 20; s.reasons.append("Yellow eyes / skin: +20 risk"); s.step = 'sp11'; st.rerun()
    if c2.button("No / Nahi", key="sp10n"): s.patient_data['yellow_eyes_skin'] = "No"; s.step = 'sp11'; st.rerun()
elif step == 'sp11':
    st.subheader("🤢 Q12: Kya aap zyada chai ya masaledar khana khate hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp11y"):
        s.patient_data['tea_spicy'] = "Yes"; s.reasons.append("Tea / spicy food habit: acidity is possible (no risk added)"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="sp11n"): s.patient_data['tea_spicy'] = "No"; s.step = 'end'; st.rerun()

# ================= PATH 4: HEADACHE =================
elif step == 'hd1':
    st.subheader("🤕 [Headache] Q1: Kya achanak sab se shadeed sar dard (thunderclap) hua?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd1y"):
        s.patient_data['thunderclap'] = "Yes"; s.risk = max(s.risk + 60, 70); s.reasons.append("Sudden worst headache: risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="hd1n"): s.patient_data['thunderclap'] = "No"; s.step = 'hd2'; st.rerun()
elif step == 'hd2':
    st.subheader("🤕 Q2: Kya bukhar + gardan akdi hui (stiff neck) + rash hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd2y"):
        s.patient_data['fever_neck_rash'] = "Yes"; s.risk = max(s.risk + 50, 70); s.reasons.append("Fever + stiff neck + rash: risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="hd2n"): s.patient_data['fever_neck_rash'] = "No"; s.step = 'hd3'; st.rerun()
elif step == 'hd3':
    st.subheader("🤕 Q3: Kya sar ke ek taraf dhadakta hua (throbbing) dard hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd3y"):
        s.patient_data['one_sided_throbbing'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("One-sided throbbing headache: +5 risk"); s.step = 'hd4'; st.rerun()
    if c2.button("No / Nahi", key="hd3n"): s.patient_data['one_sided_throbbing'] = "No"; s.step = 'hd6'; st.rerun()
elif step == 'hd4':
    st.subheader("🤕 Q4: Kya roshni ya awaaz se takleef (light/sound sensitivity) hoti hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd4y"): s.patient_data['light_sound_sensitive'] = "Yes"; s.reasons.append("Throbbing + light/sound sensitivity: migraine-type pattern is possible (no risk added)"); s.step = 'hd5'; st.rerun()
    if c2.button("No / Nahi", key="hd4n"): s.patient_data['light_sound_sensitive'] = "No"; s.reasons.append("No light/sound sensitivity: tension-type pattern is possible (no risk added)"); s.step = 'hd6'; st.rerun()
elif step == 'hd5':
    st.subheader("🤕 Q5: Kya nazar ka masla, kamzori ya bolne mein dikkat hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd5y"):
        s.patient_data['vision_weakness_speech'] = "Yes"; s.risk = max(s.risk + 50, 70); s.reasons.append("Vision / weakness / speech problem: risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="hd5n"): s.patient_data['vision_weakness_speech'] = "No"; s.step = 'hd7'; st.rerun()
elif step == 'hd6':
    st.subheader("🤕 Q6: Kya dono taraf sar tight hai aur stress / tension hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd6y"): s.patient_data['both_sides_stress'] = "Yes"; s.reasons.append("Both-sided tight headache with stress: tension-type pattern is possible (no risk added)"); s.step = 'hd7'; st.rerun()
    if c2.button("No / Nahi", key="hd6n"): s.patient_data['both_sides_stress'] = "No"; s.step = 'hd7'; st.rerun()
elif step == 'hd7':
    st.subheader("🤕 Q7: Kya subah uthte waqt sar dard zyada hota hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd7y"):
        s.patient_data['worse_on_waking'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Headache worse on waking: +10 risk"); s.step = 'hd_sleep'; st.rerun()
    if c2.button("No / Nahi", key="hd7n"): s.patient_data['worse_on_waking'] = "No"; s.step = 'hd_sleep'; st.rerun()
elif step == 'hd_sleep':
    st.subheader("📋 Q8 (Input): Aap roz kitne ghante sote hain? (normal 7-9)")
    sl = st.number_input("Sleep hours likhein", min_value=0.0, max_value=24.0, value=7.0, step=0.5, key="sl_in")
    if st.button("Submit", key="sl_btn"):
        s.report_data['sleep_hours'] = sl
        if sl < 5: s.risk = s.risk + 15; s.reasons.append("Sleep less than 5 hours (" + str(sl) + "): +15 risk"); s.step = 'hd8'
        else: s.step = 'hd8'
        st.rerun()
elif step == 'hd8':
    st.subheader("🤕 Q9: Kya aap roz 8 ghante se zyada screen (mobile/computer) dekhte hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd8y"):
        s.patient_data['screen_over_8h'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Screen time over 8 hours daily: +10 risk"); s.step = 'hd_bp'; st.rerun()
    if c2.button("No / Nahi", key="hd8n"): s.patient_data['screen_over_8h'] = "No"; s.step = 'hd_bp'; st.rerun()
elif step == 'hd_bp':
    st.subheader("📋 Q10 (Report): Systolic BP (normal 90-139 mmHg)")
    hbp = st.number_input("Apna systolic BP likhein", min_value=40, max_value=300, value=120, step=1, key="hdbp_in")
    if st.button("Submit Report", key="hdbp_btn"):
        s.report_data['systolic_bp'] = hbp
        if hbp >= 180: s.risk = max(s.risk + 60, 70); s.reasons.append("BP very high (" + str(hbp) + "): risk raised to at least 70"); s.step = 'end'
        elif hbp >= 140: s.risk = s.risk + 15; s.reasons.append("BP high (" + str(hbp) + "): +15 risk"); s.step = 'hd9'
        else: s.step = 'hd9'
        st.rerun()
elif step == 'hd9':
    st.subheader("🤕 Q11: Kya haal hi mein sar par chot (head injury) lagi?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd9y"):
        s.patient_data['head_injury'] = "Yes"; s.risk = s.risk + 30; s.reasons.append("Recent head injury: +30 risk"); s.step = 'hd10'; st.rerun()
    if c2.button("No / Nahi", key="hd9n"): s.patient_data['head_injury'] = "No"; s.step = 'hd10'; st.rerun()
elif step == 'hd10':
    st.subheader("🤕 Q12: Kya sar dard ke saath ulti jaisa mann (nausea) hota hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd10y"):
        s.patient_data['nausea'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Nausea with headache: +5 risk"); s.step = 'hd11'; st.rerun()
    if c2.button("No / Nahi", key="hd10n"): s.patient_data['nausea'] = "No"; s.step = 'hd11'; st.rerun()
elif step == 'hd11':
    st.subheader("🤕 Q13: Kya haal hi mein chai/coffee (caffeine) ki aadat change hui?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd11y"): s.patient_data['caffeine_change'] = "Yes"; s.reasons.append("Recent caffeine change: withdrawal headache is possible (no risk added)"); s.step = 'hd12'; st.rerun()
    if c2.button("No / Nahi", key="hd11n"): s.patient_data['caffeine_change'] = "No"; s.step = 'hd12'; st.rerun()
elif step == 'hd12':
    st.subheader("🤕 Q14: Kya aapki nazar kamzor hai ya chashma (glasses) ka number badla hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd12y"): s.patient_data['eyesight_problem'] = "Yes"; s.reasons.append("Eyesight problem: eye strain is possible (no risk added)"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="hd12n"): s.patient_data['eyesight_problem'] = "No"; s.step = 'end'; st.rerun()

# ================= FINAL RESULT =================
elif step == 'end':
    if s.risk > 100: s.risk = 100
    if s.risk >= 70: urgency = "EMERGENCY"; st.error("🚨 EMERGENCY: Go to hospital immediately!"); suggestion = "Go to the hospital immediately. Please consult a doctor right now."
    elif s.risk >= 40: urgency = "URGENT"; st.warning("⚠️ URGENT: Doctor se aaj milein"); suggestion = "Please consult a doctor today and get a medical checkup."
    elif s.risk >= 20: urgency = "ROUTINE"; st.info("📅 ROUTINE: 1-2 hafte mein checkup karwayein"); suggestion = "Get a medical checkup within 1-2 weeks. Please consult a doctor."
    else: urgency = "SELF-CARE"; st.success("🏠 SELF-CARE: Ghar pe rest karein"); suggestion = "Take rest at home. Please consult a doctor if symptoms continue."
    st.write("Risk Score: " + str(s.risk) + "/100"); st.progress(s.risk)
    st.write("**🧠 Yeh decision kyun? (Why this decision)**")
    if len(s.reasons) == 0: st.write("• No major red flags found from your answers.")
    for r in s.reasons: st.write("• " + r)
    st.info("💡 " + suggestion)
    st.write("This is NOT a diagnosis. Hamesha qualified doctor se confirm karwayein.")
    if s.saved == False:
        save_to_db(s.patient_data, s.report_data, "[" + urgency + "] Risk " + str(s.risk) + "/100 | " + suggestion + " | Reasons: " + "; ".join(s.reasons))
        s.saved = True
        st.rerun()
    st.success("💾 Consultation database mein save ho gayi.")
    if st.button("🔄 Start New Consultation", key="new"):
        s.step = 'start'; s.patient_data = {}; s.report_data = {}; s.risk = 0; s.reasons = []; s.saved = False
        st.rerun()
else:
    st.error("Unknown step. Dobara shuru karein.")
    if st.button("Restart", key="restart"):
        s.step = 'start'; s.patient_data = {}; s.report_data = {}; s.risk = 0; s.reasons = []; s.saved = False
        st.rerun()

# Total if/else count: 208
# Total questions: 57
