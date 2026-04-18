# medical_dataset.py

# A comprehensive dataset for preliminary medical diagnosis.
# Each key is a disease, and the dictionary acts as its "frame".
# It contains:
# - description (slot)
# - prevalence (slot)
# - severity (slot)
# - category (slot) - body system classification
# - symptoms (filler/relationship targets)
# - treatments (filler/relationship targets)
# - risk_factors (filler/relationship targets)

MEDICAL_KNOWLEDGE_BASE = {
    # =========================================================================
    # RESPIRATORY
    # =========================================================================
    "Influenza (Flu)": {
        "description": "A viral infection that attacks your respiratory system.",
        "prevalence": "Common",
        "severity": "Moderate",
        "category": "Respiratory",
        "symptoms": ["Fever", "Chills", "Muscle aches", "Cough", "Congestion", "Runny nose", "Headache", "Fatigue"],
        "treatments": ["Rest", "Fluid intake", "Antiviral medication", "Pain relievers"],
        "risk_factors": ["Weakened immune system", "Age (under 5 or over 65)", "Chronic illness"]
    },
    "Common Cold": {
        "description": "A viral infection of your nose and throat (upper respiratory tract).",
        "prevalence": "Very Common",
        "severity": "Mild",
        "category": "Respiratory",
        "symptoms": ["Runny nose", "Sore throat", "Cough", "Congestion", "Slight body aches", "Mild headache", "Sneezing", "Low-grade fever"],
        "treatments": ["Rest", "Fluid intake", "Decongestants", "Pain relievers"],
        "risk_factors": ["Weakened immune system", "Seasonal changes", "Close contact with infected persons"]
    },
    "COVID-19": {
        "description": "An infectious disease caused by the SARS-CoV-2 virus.",
        "prevalence": "Common",
        "severity": "High",
        "category": "Respiratory",
        "symptoms": ["Fever", "Chills", "Cough", "Shortness of breath", "Fatigue", "Muscle aches", "Headache", "Loss of taste or smell", "Sore throat", "Congestion"],
        "treatments": ["Rest", "Fluid intake", "Antiviral medication", "Monoclonal antibodies", "Pain relievers"],
        "risk_factors": ["Age (over 65)", "Obesity", "Diabetes", "Cardiovascular disease", "Immunocompromised"]
    },
    "Bronchitis": {
        "description": "An inflammation of the lining of your bronchial tubes, which carry air to and from your lungs.",
        "prevalence": "Common",
        "severity": "Moderate",
        "category": "Respiratory",
        "symptoms": ["Cough", "Production of mucus (sputum)", "Fatigue", "Shortness of breath", "Slight fever", "Chills", "Chest discomfort"],
        "treatments": ["Rest", "Fluid intake", "Cough medicine", "Humidifier", "Inhaler"],
        "risk_factors": ["Smoking", "Weakened immune system", "Exposure to irritants", "GERD"]
    },
    "Pneumonia": {
        "description": "An infection that inflames the air sacs in one or both lungs.",
        "prevalence": "Common",
        "severity": "High",
        "category": "Respiratory",
        "symptoms": ["Chest pain when breathing", "Cough with phlegm", "Fatigue", "Fever", "Sweating", "Chills", "Nausea", "Vomiting", "Shortness of breath"],
        "treatments": ["Antibiotics", "Antiviral medication", "Antipyretics", "Rest", "Fluid intake"],
        "risk_factors": ["Age (under 2 or over 65)", "Hospitalization", "Chronic disease", "Smoking", "Weakened immune system"]
    },
    "Asthma": {
        "description": "A condition in which your airways narrow and swell and may produce extra mucus.",
        "prevalence": "Common",
        "severity": "Variable",
        "category": "Respiratory",
        "symptoms": ["Shortness of breath", "Chest tightness", "Wheezing", "Coughing attacks"],
        "treatments": ["Inhaled corticosteroids", "Rescue inhalers", "Bronchodilators", "Trigger avoidance"],
        "risk_factors": ["Family history of asthma", "Allergies", "Obesity", "Smoking", "Air pollution exposure"]
    },
    "Tuberculosis": {
        "description": "An infectious bacterial disease characterized by the growth of nodules (tubercles) in the tissues, especially the lungs.",
        "prevalence": "Common globally",
        "severity": "High",
        "category": "Respiratory",
        "symptoms": ["Persistent cough", "Chest pain", "Coughing up blood", "Fatigue", "Night sweats", "Chills", "Fever", "Loss of appetite", "Weight loss"],
        "treatments": ["Long-term antibiotics", "Rest"],
        "risk_factors": ["HIV/AIDS", "Weakened immune system", "Close contact with TB patients", "Malnutrition", "Substance abuse"]
    },
    "Chronic Obstructive Pulmonary Disease (COPD)": {
        "description": "A group of lung diseases that block airflow and make it difficult to breathe.",
        "prevalence": "Common",
        "severity": "High",
        "category": "Respiratory",
        "symptoms": ["Shortness of breath", "Wheezing", "Chest tightness", "Chronic cough", "Respiratory infections", "Lack of energy", "Unintended weight loss"],
        "treatments": ["Smoking cessation", "Bronchodilators", "Inhaled steroids", "Oxygen therapy", "Pulmonary rehabilitation"],
        "risk_factors": ["Smoking", "Long-term exposure to air pollutants", "Genetic factors (alpha-1 antitrypsin deficiency)", "Occupational dust exposure"]
    },

    # =========================================================================
    # ALLERGIC / IMMUNOLOGICAL
    # =========================================================================
    "Allergic Rhinitis (Allergies)": {
        "description": "An allergic response causing itchy, watery eyes, sneezing, and other similar symptoms.",
        "prevalence": "Very Common",
        "severity": "Mild",
        "category": "Immunological",
        "symptoms": ["Sneezing", "Runny nose", "Itchy eyes", "Watery eyes", "Congestion"],
        "treatments": ["Antihistamines", "Decongestants", "Nasal corticosteroids", "Allergen avoidance"],
        "risk_factors": ["Family history of allergies", "Asthma", "Eczema", "Environmental allergen exposure"]
    },

    # =========================================================================
    # NEUROLOGICAL
    # =========================================================================
    "Migraine": {
        "description": "A headache that can cause severe throbbing pain or a pulsing sensation, usually on one side of the head.",
        "prevalence": "Common",
        "severity": "Moderate to High",
        "category": "Neurological",
        "symptoms": ["Throbbing head pain", "Nausea", "Vomiting", "Sensitivity to light", "Sensitivity to sound"],
        "treatments": ["Pain relievers", "Triptans", "Ergots", "Rest in a dark quiet room"],
        "risk_factors": ["Family history", "Age (peaks in 30s)", "Hormonal changes", "Stress", "Sleep disturbances"]
    },
    "Epilepsy": {
        "description": "A neurological disorder in which brain activity becomes abnormal, causing seizures or periods of unusual behavior and sensations.",
        "prevalence": "Common",
        "severity": "High",
        "category": "Neurological",
        "symptoms": ["Seizures", "Temporary confusion", "Staring spells", "Uncontrollable jerking movements", "Loss of consciousness", "Anxiety", "Deja vu"],
        "treatments": ["Anti-seizure medications", "Vagus nerve stimulation", "Ketogenic diet", "Surgery"],
        "risk_factors": ["Head trauma", "Brain tumors", "Stroke", "Genetic factors", "Prenatal brain damage"]
    },
    "Parkinson's Disease": {
        "description": "A progressive nervous system disorder that affects movement, often starting with a barely noticeable tremor in one hand.",
        "prevalence": "Uncommon",
        "severity": "High",
        "category": "Neurological",
        "symptoms": ["Tremor", "Slowed movement", "Rigid muscles", "Impaired posture and balance", "Loss of automatic movements", "Speech changes", "Writing changes"],
        "treatments": ["Levodopa", "Dopamine agonists", "MAO B inhibitors", "Physical therapy", "Deep brain stimulation"],
        "risk_factors": ["Age (over 60)", "Heredity", "Male sex", "Exposure to toxins"]
    },
    "Meningitis": {
        "description": "An inflammation of the membranes (meninges) surrounding the brain and spinal cord, usually caused by infection.",
        "prevalence": "Uncommon",
        "severity": "Critical",
        "category": "Neurological",
        "symptoms": ["Sudden high fever", "Stiff neck", "Severe headache", "Nausea", "Vomiting", "Sensitivity to light", "Confusion", "Skin rash", "Seizures"],
        "treatments": ["Antibiotics", "Antiviral medication", "Corticosteroids", "Hospitalization", "IV fluids"],
        "risk_factors": ["Age (under 20)", "Community living", "Compromised immune system", "Skipping vaccinations"]
    },

    # =========================================================================
    # CARDIOVASCULAR
    # =========================================================================
    "Hypertension (High Blood Pressure)": {
        "description": "A condition in which the force of the blood against the artery walls is too high.",
        "prevalence": "Very Common",
        "severity": "Moderate to High",
        "category": "Cardiovascular",
        "symptoms": ["Headache", "Shortness of breath", "Nosebleeds", "Flushing", "Dizziness", "Chest pain"],
        "treatments": ["Dietary changes", "Exercise", "Weight loss", "Antihypertensive medications", "Stress reduction"],
        "risk_factors": ["Obesity", "High salt intake", "Sedentary lifestyle", "Family history", "Age", "Smoking", "Excessive alcohol"]
    },
    "Coronary Artery Disease": {
        "description": "A disease caused by plaque buildup in the walls of the arteries that supply blood to the heart.",
        "prevalence": "Very Common",
        "severity": "High",
        "category": "Cardiovascular",
        "symptoms": ["Chest pain", "Chest pressure", "Shortness of breath", "Pain in neck or jaw", "Pain in shoulder or arm", "Fatigue", "Dizziness", "Nausea"],
        "treatments": ["Lifestyle changes", "Statins", "Blood thinners", "Beta-blockers", "Angioplasty", "Coronary artery bypass surgery"],
        "risk_factors": ["High cholesterol", "High blood pressure", "Diabetes", "Smoking", "Obesity", "Family history", "Sedentary lifestyle"]
    },
    "Heart Failure": {
        "description": "A chronic condition in which the heart doesn't pump blood as well as it should.",
        "prevalence": "Common",
        "severity": "High",
        "category": "Cardiovascular",
        "symptoms": ["Shortness of breath", "Fatigue", "Swollen legs and ankles", "Rapid heartbeat", "Persistent cough", "Wheezing", "Swelling of abdomen", "Rapid weight gain"],
        "treatments": ["ACE inhibitors", "Beta-blockers", "Diuretics", "Lifestyle modifications", "Heart transplant"],
        "risk_factors": ["Coronary artery disease", "High blood pressure", "Diabetes", "Obesity", "Smoking", "Age"]
    },
    "Atrial Fibrillation": {
        "description": "An irregular and often very rapid heart rhythm that can lead to blood clots in the heart.",
        "prevalence": "Common",
        "severity": "Moderate to High",
        "category": "Cardiovascular",
        "symptoms": ["Heart palpitations", "Shortness of breath", "Fatigue", "Dizziness", "Chest pain", "Reduced ability to exercise", "Weakness"],
        "treatments": ["Blood thinners", "Rate control medications", "Rhythm control medications", "Cardioversion", "Catheter ablation"],
        "risk_factors": ["Age", "Heart disease", "High blood pressure", "Obesity", "Family history", "Excessive alcohol", "Sleep apnea"]
    },

    # =========================================================================
    # GASTROINTESTINAL
    # =========================================================================
    "Gastroenteritis (Stomach Flu)": {
        "description": "An intestinal infection marked by diarrhea, cramps, nausea, vomiting, and fever.",
        "prevalence": "Common",
        "severity": "Moderate",
        "category": "Gastrointestinal",
        "symptoms": ["Watery diarrhea", "Abdominal cramps", "Nausea", "Vomiting", "Muscle aches", "Low-grade fever"],
        "treatments": ["Fluid replacement", "Electrolytes", "Rest", "Bland diet"],
        "risk_factors": ["Close contact with infected persons", "Contaminated food or water", "Weakened immune system"]
    },
    "Gastroesophageal Reflux Disease (GERD)": {
        "description": "A digestive disease in which stomach acid or bile irritates the food pipe lining.",
        "prevalence": "Very Common",
        "severity": "Mild to Moderate",
        "category": "Gastrointestinal",
        "symptoms": ["Heartburn", "Chest pain", "Difficulty swallowing", "Regurgitation of food or sour liquid", "Sensation of a lump in your throat", "Chronic cough"],
        "treatments": ["Antacids", "Proton pump inhibitors", "Dietary changes", "Weight loss", "Elevating the head of the bed"],
        "risk_factors": ["Obesity", "Hiatal hernia", "Pregnancy", "Smoking", "Eating large meals late at night", "Spicy or fatty foods"]
    },
    "Irritable Bowel Syndrome (IBS)": {
        "description": "A common disorder that affects the large intestine, causing cramping, abdominal pain, bloating, gas, diarrhea and constipation.",
        "prevalence": "Common",
        "severity": "Moderate",
        "category": "Gastrointestinal",
        "symptoms": ["Abdominal pain", "Bloating", "Gas", "Diarrhea", "Constipation", "Mucus in stool", "Abdominal cramps"],
        "treatments": ["Dietary changes", "Fiber supplements", "Anti-diarrheal medications", "Antispasmodics", "Stress management", "Probiotics"],
        "risk_factors": ["Age (under 50)", "Female sex", "Family history of IBS", "Anxiety", "Depression", "Food intolerance"]
    },
    "Peptic Ulcer Disease": {
        "description": "Open sores that develop on the inside lining of the stomach and the upper portion of the small intestine.",
        "prevalence": "Common",
        "severity": "Moderate",
        "category": "Gastrointestinal",
        "symptoms": ["Burning stomach pain", "Bloating", "Heartburn", "Nausea", "Intolerance to fatty foods", "Feeling of fullness"],
        "treatments": ["Proton pump inhibitors", "Antibiotics (for H. pylori)", "Antacids", "H2-receptor blockers", "Dietary modifications"],
        "risk_factors": ["H. pylori infection", "Regular use of NSAIDs", "Smoking", "Excessive alcohol", "Stress"]
    },
    "Hepatitis B": {
        "description": "A serious liver infection caused by the hepatitis B virus that can become chronic.",
        "prevalence": "Common globally",
        "severity": "High",
        "category": "Gastrointestinal",
        "symptoms": ["Abdominal pain", "Dark urine", "Fever", "Joint pain", "Loss of appetite", "Nausea", "Vomiting", "Weakness", "Jaundice"],
        "treatments": ["Antiviral medications", "Liver transplant (severe cases)", "Interferon injections", "Regular monitoring"],
        "risk_factors": ["Unprotected sex", "Sharing needles", "Mother-to-child transmission", "Healthcare worker exposure", "Travel to endemic regions"]
    },

    # =========================================================================
    # ENDOCRINE
    # =========================================================================
    "Diabetes Type 2": {
        "description": "A chronic condition that affects the way the body processes blood sugar (glucose).",
        "prevalence": "Very Common",
        "severity": "Moderate to High",
        "category": "Endocrine",
        "symptoms": ["Increased thirst", "Frequent urination", "Increased hunger", "Unintended weight loss", "Fatigue", "Blurred vision", "Slow-healing sores", "Frequent infections"],
        "treatments": ["Diet modification", "Exercise", "Weight loss", "Oral medication", "Insulin therapy"],
        "risk_factors": ["Obesity", "Sedentary lifestyle", "Family history", "Age (over 45)", "Polycystic ovary syndrome", "Prediabetes"]
    },
    "Hypothyroidism": {
        "description": "A condition in which the thyroid gland doesn't produce enough thyroid hormone.",
        "prevalence": "Common",
        "severity": "Moderate",
        "category": "Endocrine",
        "symptoms": ["Fatigue", "Weight gain", "Cold intolerance", "Constipation", "Dry skin", "Puffy face", "Hoarse voice", "Muscle weakness", "Elevated cholesterol", "Depression"],
        "treatments": ["Levothyroxine", "Regular thyroid function tests", "Dosage adjustments"],
        "risk_factors": ["Female sex", "Age (over 60)", "Autoimmune disease", "Family history", "Radiation therapy", "Thyroid surgery"]
    },
    "Hyperthyroidism": {
        "description": "A condition in which the thyroid gland produces too much thyroid hormone.",
        "prevalence": "Common",
        "severity": "Moderate",
        "category": "Endocrine",
        "symptoms": ["Rapid heartbeat", "Weight loss", "Increased appetite", "Tremor", "Sweating", "Nervousness", "Anxiety", "Irregular menstrual periods", "Heat intolerance", "Sleep difficulty"],
        "treatments": ["Anti-thyroid medications", "Radioactive iodine", "Beta-blockers", "Thyroidectomy"],
        "risk_factors": ["Female sex", "Family history of Graves disease", "Personal history of autoimmune disease"]
    },
    "Cushing's Syndrome": {
        "description": "A condition caused by prolonged exposure to high levels of cortisol.",
        "prevalence": "Rare",
        "severity": "High",
        "category": "Endocrine",
        "symptoms": ["Weight gain (especially face and abdomen)", "Purple stretch marks", "Thin fragile skin", "Slow healing", "Acne", "Fatigue", "Muscle weakness", "High blood pressure", "High blood sugar"],
        "treatments": ["Reducing corticosteroid use", "Surgery", "Radiation therapy", "Medications to control cortisol"],
        "risk_factors": ["Long-term corticosteroid use", "Pituitary tumors", "Adrenal tumors", "Ectopic ACTH syndrome"]
    },

    # =========================================================================
    # DERMATOLOGICAL
    # =========================================================================
    "Eczema (Atopic Dermatitis)": {
        "description": "A condition that makes your skin red and itchy, common in children but can occur at any age.",
        "prevalence": "Very Common",
        "severity": "Mild to Moderate",
        "category": "Dermatological",
        "symptoms": ["Dry skin", "Itching", "Red or brownish-gray patches", "Small raised bumps", "Thickened cracked skin", "Raw sensitive skin from scratching"],
        "treatments": ["Moisturizers", "Topical corticosteroids", "Antihistamines", "Immunosuppressants", "Light therapy"],
        "risk_factors": ["Family history of eczema or allergies", "Asthma", "Allergic rhinitis", "Environmental factors"]
    },
    "Psoriasis": {
        "description": "A skin disease that causes red, itchy scaly patches most commonly on the knees, elbows, trunk, and scalp.",
        "prevalence": "Common",
        "severity": "Moderate",
        "category": "Dermatological",
        "symptoms": ["Red patches of skin covered with silvery scales", "Dry cracked skin that may bleed", "Itching", "Burning or soreness", "Thickened or ridged nails", "Swollen stiff joints"],
        "treatments": ["Topical corticosteroids", "Vitamin D analogues", "Retinoids", "Light therapy", "Methotrexate", "Biologics"],
        "risk_factors": ["Family history", "Stress", "Smoking", "Obesity", "Viral and bacterial infections"]
    },
    "Cellulitis": {
        "description": "A common and potentially serious bacterial skin infection that causes redness, swelling, and pain in the infected area.",
        "prevalence": "Common",
        "severity": "Moderate to High",
        "category": "Dermatological",
        "symptoms": ["Red area of skin that tends to expand", "Swelling", "Tenderness", "Pain", "Warmth", "Fever", "Red spots", "Blistering", "Skin dimpling"],
        "treatments": ["Antibiotics", "Rest", "Elevation of affected area", "Pain relievers", "Wound care"],
        "risk_factors": ["Skin injury", "Weakened immune system", "Chronic skin conditions", "Obesity", "Lymphedema", "Diabetes"]
    },

    # =========================================================================
    # PSYCHIATRIC
    # =========================================================================
    "Major Depression": {
        "description": "A mood disorder that causes a persistent feeling of sadness and loss of interest in activities.",
        "prevalence": "Very Common",
        "severity": "Moderate to High",
        "category": "Psychiatric",
        "symptoms": ["Persistent sadness", "Loss of interest", "Sleep disturbances", "Fatigue", "Feelings of worthlessness", "Difficulty concentrating", "Appetite changes", "Thoughts of death", "Irritability"],
        "treatments": ["Antidepressants", "Psychotherapy", "Cognitive behavioral therapy", "Exercise", "Electroconvulsive therapy"],
        "risk_factors": ["Family history", "Major life changes", "Trauma", "Certain medications", "Chronic illness", "Substance abuse"]
    },
    "Generalized Anxiety Disorder": {
        "description": "A mental health disorder characterized by persistent and excessive worry about various activities or events.",
        "prevalence": "Common",
        "severity": "Moderate",
        "category": "Psychiatric",
        "symptoms": ["Excessive worry", "Restlessness", "Fatigue", "Difficulty concentrating", "Irritability", "Muscle tension", "Sleep disturbances", "Sweating", "Nausea"],
        "treatments": ["Cognitive behavioral therapy", "Anti-anxiety medications", "Antidepressants", "Relaxation techniques", "Mindfulness"],
        "risk_factors": ["Family history", "Trauma", "Chronic medical conditions", "Substance abuse", "Female sex", "Stress"]
    },
    "Panic Disorder": {
        "description": "A type of anxiety disorder causing recurring unexpected panic attacks of intense fear and anxiety.",
        "prevalence": "Common",
        "severity": "Moderate to High",
        "category": "Psychiatric",
        "symptoms": ["Sudden intense fear", "Heart palpitations", "Sweating", "Trembling", "Shortness of breath", "Chest pain", "Nausea", "Dizziness", "Fear of losing control", "Numbness or tingling"],
        "treatments": ["Cognitive behavioral therapy", "SSRIs", "SNRIs", "Benzodiazepines", "Relaxation techniques"],
        "risk_factors": ["Family history", "Major life stress", "Traumatic events", "Smoking", "Excessive caffeine"]
    },

    # =========================================================================
    # INFECTIOUS
    # =========================================================================
    "Strep Throat": {
        "description": "A bacterial infection that may cause a sore, scratchy throat.",
        "prevalence": "Common",
        "severity": "Moderate",
        "category": "Infectious",
        "symptoms": ["Throat pain", "Difficulty swallowing", "Red and swollen tonsils", "Swollen lymph nodes", "Fever", "Headache", "Rash"],
        "treatments": ["Antibiotics", "Pain relievers", "Rest", "Warm liquids"],
        "risk_factors": ["Age (5-15 years)", "Season (late fall to early spring)", "Close contact with infected person"]
    },
    "Malaria": {
        "description": "A disease caused by a plasmodium parasite, transmitted by the bite of infected mosquitoes.",
        "prevalence": "Common in tropical regions",
        "severity": "High",
        "category": "Infectious",
        "symptoms": ["Fever", "Chills", "Sweating", "Headache", "Nausea", "Vomiting", "Muscle aches", "Fatigue"],
        "treatments": ["Antimalarial drugs", "Supportive care"],
        "risk_factors": ["Travel to tropical regions", "Lack of preventive medication", "Exposure to mosquitoes", "Weakened immune system"]
    },
    "Dengue Fever": {
        "description": "A mosquito-borne viral disease occurring in tropical and subtropical areas.",
        "prevalence": "Common in tropical regions",
        "severity": "Moderate to High",
        "category": "Infectious",
        "symptoms": ["High fever", "Severe headache", "Pain behind the eyes", "Joint and muscle pain", "Fatigue", "Nausea", "Vomiting", "Skin rash"],
        "treatments": ["Fluid replacement", "Pain relievers", "Rest"],
        "risk_factors": ["Living in tropical areas", "Prior dengue infection", "Lack of mosquito protection"]
    },
    "Chickenpox": {
        "description": "A highly contagious viral infection causing an itchy, blister-like rash on the skin.",
        "prevalence": "Common",
        "severity": "Mild to Moderate",
        "category": "Infectious",
        "symptoms": ["Itchy blister-like rash", "Fever", "Fatigue", "Loss of appetite", "Headache", "General feeling of being unwell"],
        "treatments": ["Calamine lotion", "Antihistamines", "Antiviral medication (acyclovir)", "Rest", "Oatmeal baths"],
        "risk_factors": ["Not vaccinated", "Age (children under 12)", "Close contact with infected persons", "Weakened immune system"]
    },
    "Measles": {
        "description": "A highly contagious viral disease that causes fever, cough, and a distinctive skin rash.",
        "prevalence": "Uncommon (where vaccinated)",
        "severity": "Moderate to High",
        "category": "Infectious",
        "symptoms": ["High fever", "Cough", "Runny nose", "Red watery eyes", "Skin rash", "Koplik spots (white spots inside cheeks)", "Sore throat"],
        "treatments": ["Supportive care", "Vitamin A supplements", "Fever reducers", "Antibiotics for secondary infections"],
        "risk_factors": ["Not vaccinated", "International travel", "Vitamin A deficiency", "Immunodeficiency"]
    },
    "Typhoid Fever": {
        "description": "A bacterial infection caused by Salmonella typhi, spread through contaminated food and water.",
        "prevalence": "Common in developing countries",
        "severity": "High",
        "category": "Infectious",
        "symptoms": ["Sustained high fever", "Weakness", "Abdominal pain", "Headache", "Diarrhea or constipation", "Rose-colored spots on chest", "Loss of appetite", "Enlarged spleen"],
        "treatments": ["Antibiotics", "Fluid replacement", "Rest", "Bland diet"],
        "risk_factors": ["Travel to endemic areas", "Contaminated food or water", "Close contact with carrier", "Poor sanitation"]
    },
    "Cholera": {
        "description": "An acute diarrheal illness caused by infection of the intestine with Vibrio cholerae bacteria.",
        "prevalence": "Common in areas with poor sanitation",
        "severity": "Critical",
        "category": "Infectious",
        "symptoms": ["Profuse watery diarrhea", "Vomiting", "Rapid dehydration", "Muscle cramps", "Low blood pressure", "Thirst", "Rapid heart rate", "Loss of skin elasticity"],
        "treatments": ["Oral rehydration salts", "IV fluids", "Antibiotics", "Zinc supplements"],
        "risk_factors": ["Contaminated water", "Poor sanitation", "Raw or undercooked seafood", "Type O blood", "Low stomach acid"]
    },

    # =========================================================================
    # MUSCULOSKELETAL
    # =========================================================================
    "Osteoarthritis": {
        "description": "A type of arthritis that occurs when flexible tissue at the ends of bones wears down.",
        "prevalence": "Very Common",
        "severity": "Moderate",
        "category": "Musculoskeletal",
        "symptoms": ["Joint pain", "Joint stiffness", "Tenderness", "Loss of flexibility", "Grating sensation", "Bone spurs"],
        "treatments": ["Pain relievers", "Physical therapy", "Joint replacement surgery", "Exercise", "Weight loss"],
        "risk_factors": ["Older age", "Obesity", "Joint injuries", "Repeated stress on joints", "Genetics", "Female sex"]
    },
    "Rheumatoid Arthritis": {
        "description": "A chronic autoimmune disorder that primarily affects joints, causing painful swelling that can eventually result in bone erosion.",
        "prevalence": "Common",
        "severity": "Moderate to High",
        "category": "Musculoskeletal",
        "symptoms": ["Tender swollen joints", "Joint stiffness (worse in morning)", "Fatigue", "Fever", "Loss of appetite", "Firm bumps under skin on arms", "Joint warmth and redness"],
        "treatments": ["NSAIDs", "Corticosteroids", "DMARDs", "Biologic agents", "Physical therapy", "Surgery"],
        "risk_factors": ["Female sex", "Age (40-60)", "Family history", "Smoking", "Obesity", "Environmental exposures"]
    },
    "Gout": {
        "description": "A form of arthritis characterized by severe, sudden pain, swelling, redness, and tenderness in joints.",
        "prevalence": "Common",
        "severity": "Moderate",
        "category": "Musculoskeletal",
        "symptoms": ["Intense joint pain (often big toe)", "Lingering discomfort", "Inflammation and redness", "Limited range of motion", "Warmth in joint"],
        "treatments": ["NSAIDs", "Colchicine", "Corticosteroids", "Urate-lowering therapy", "Dietary changes"],
        "risk_factors": ["High-purine diet", "Obesity", "Medical conditions (hypertension, diabetes)", "Family history", "Male sex", "Excessive alcohol"]
    },

    # =========================================================================
    # RENAL / UROLOGICAL
    # =========================================================================
    "Urinary Tract Infection (UTI)": {
        "description": "An infection in any part of the urinary system, the kidneys, bladder, or urethra.",
        "prevalence": "Common",
        "severity": "Mild to Moderate",
        "category": "Renal",
        "symptoms": ["Strong, persistent urge to urinate", "Burning sensation when urinating", "Passing frequent, small amounts of urine", "Urine that appears cloudy", "Urine that appears red", "Strong-smelling urine", "Pelvic pain"],
        "treatments": ["Antibiotics", "Increased water intake", "Pain relievers"],
        "risk_factors": ["Female anatomy", "Sexual activity", "Certain types of birth control", "Menopause", "Urinary tract abnormalities", "Kidney stones"]
    },
    "Kidney Stones": {
        "description": "Hard deposits made of minerals and salts that form inside your kidneys.",
        "prevalence": "Common",
        "severity": "Moderate to High",
        "category": "Renal",
        "symptoms": ["Severe pain in side and back", "Pain that radiates to lower abdomen and groin", "Pain during urination", "Pink red or brown urine", "Nausea", "Vomiting", "Persistent need to urinate", "Fever and chills (if infection)"],
        "treatments": ["Pain relievers", "Alpha-blockers", "Lithotripsy", "Ureteroscopy", "Increased water intake"],
        "risk_factors": ["Dehydration", "High-protein diet", "Obesity", "Family history", "Digestive diseases", "Certain supplements and medications"]
    },
    "Chronic Kidney Disease": {
        "description": "A gradual loss of kidney function over time, potentially leading to kidney failure.",
        "prevalence": "Common",
        "severity": "High",
        "category": "Renal",
        "symptoms": ["Nausea", "Vomiting", "Loss of appetite", "Fatigue", "Sleep problems", "Decreased mental sharpness", "Muscle cramps", "Swelling of feet and ankles", "Dry itchy skin", "Chest pain", "Shortness of breath"],
        "treatments": ["Blood pressure medications", "Cholesterol medications", "Anemia treatment", "Dialysis", "Kidney transplant", "Low-protein diet"],
        "risk_factors": ["Diabetes", "High blood pressure", "Heart disease", "Smoking", "Obesity", "Family history", "Age (over 65)"]
    },

    # =========================================================================
    # HEMATOLOGICAL
    # =========================================================================
    "Anemia": {
        "description": "A condition in which you lack enough healthy red blood cells to carry adequate oxygen to your body's tissues.",
        "prevalence": "Common",
        "severity": "Moderate",
        "category": "Hematological",
        "symptoms": ["Fatigue", "Weakness", "Pale skin", "Chest pain", "Cold hands and feet", "Shortness of breath", "Dizziness", "Irregular heartbeats"],
        "treatments": ["Iron supplements", "Vitamin B supplements", "Dietary changes", "Blood transfusions"],
        "risk_factors": ["Iron-poor diet", "Intestinal disorders", "Menstruation", "Pregnancy", "Chronic conditions", "Family history"]
    }
}
