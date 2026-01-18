from pathlib import Path
import re
import time
import pandas as pd
from sec_edgar_downloader import Downloader
import os
from dotenv import load_dotenv
import json
import sqlite3
import html
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
import yfinance as yf


PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "biotech_intelligence.db"
base_path = PROJECT_ROOT / "sec-edgar-filings"



FUNDS = {
    "Baker Bros": "0001263508",
    "OrbiMed": "0001055951",
    "Deerfield": "0001009258",
    "RA Capital": "0001346824",
    "Redmile": "0001425738",
    "Avoro": "0001633313",
    "RTW": "0001493215",
    "Perceptive": "0001224962",
    "Armistice": "0001601086",
    "BVF": "0001055947",
    "Vivo": "0001674712",
    "Casdin": "0001534261",
    "Deep Track": "0001856083",
    "Braidwell": "0001920938",
    "Rock Springs": "0001595725",
    "EcoR1": "0001587114",
    "Cormorant": "0001583977",
    "Camber": "0001444043",
    "Foresite": "0001562157",
    "Logos": "0001792126",
    "Boxer": "0001465837",
    "Tang": "0001232621",
    "PFM": "0001442756",
    "Commodore": "0001831942",
    "Samsara": "0001744967",
    "Great Point": "0001281446",
    "Soleus": "0001802630",
    "venBio": "0001776382",
    "Sarissa": "0001577524",
    "Caligan": "0001727492",
    "Foresite VI": "0002013341",
    "Decheng": "0002010850",
    "SV Health": "0001587143",
    "Osage": "0001492594",
    "Aisling Capital": "0001766721",
    "TCG Crossover": "0001851080",
    "Fairmount": "0001802528",
    "Paradigm BioCapital": "0001855655",
    "Sofinnova Investments": "0001631134",
    "Bain Life Sciences": "0001703031",
    "Pura Vida": "0001796129",
    "Octagon": "0001839435",
    "Ghost Tree": "0001632854",
    "Altium": "0001551065",
    "Frazier Life Sciences": "0001402204",
    "Artia Global": "0001824707",
    "Kynam Capital": "0001819584",
    "StemPoint": "0001886877",
    "Atlas Venture": "0001431431",
    "Adar1": "0001908759",
    "Ikarian Capital": "0001723467"
}


# PFUDA Scraper
PDUFA_CALENDAR_URL = (
    "https://clients6.google.com/calendar/v3/calendars/"
    "5dso8589486irtj53sdkr4h6ek%40group.calendar.google.com/events"
    "?calendarId=5dso8589486irtj53sdkr4h6ek%40group.calendar.google.com"
    "&singleEvents=true&maxResults=250&sanitizeHtml=true"
    "&timeMin={year}-01-01T00%3A00%3A00-00%3A00"
    "&timeMax={year}-12-30T23%3A59%3A59-00%3A00"
    "&key=AIzaSyDOtGM5jr8bNp1utVpG2_gSRH03RNGBkI8"
)

# Phase success rates by disease category
# Updated Phase 3 success rates by disease category (2010-2026 Benchmarks)
# Transition: Phase III -> Approval Success Likelihood (Likelihood of Approval)
PHASE3_SUCCESS_RATES = {
    # Oncology
    "oncology": 0.475,
    "cancer": 0.475,
    "tumor": 0.475,
    "tumour": 0.475,
    "carcinoma": 0.475,
    "adenocarcinoma": 0.475,
    "sarcoma": 0.475,
    "glioblastoma": 0.088,
    "melanoma": 0.475,
    "mesothelioma": 0.475,
    "neoplasm": 0.475,
    "malignancy": 0.475,
    "malignant": 0.475,
    "metastatic": 0.475,
    "solid tumor": 0.475,
    "nsclc": 0.515,
    "non-small cell lung": 0.515,
    "small cell lung": 0.475,
    "breast cancer": 0.475,
    "prostate cancer": 0.475,
    "colorectal": 0.475,
    "pancreatic": 0.042,
    "ovarian": 0.475,
    "bladder cancer": 0.475,
    "renal cell carcinoma": 0.475,
    "hepatocellular": 0.475,
    "gastric cancer": 0.475,
    "esophageal": 0.475,
    "head and neck": 0.475,
    "squamous cell": 0.475,
    "basal cell": 0.475,

    # Hematology
    "hematology": 0.692,
    "blood": 0.692,
    "anemia": 0.692,
    "leukemia": 0.692,
    "lymphoma": 0.692,
    "myelodysplastic": 0.692,
    "mds": 0.692,
    "myeloma": 0.692,
    "multiple myeloma": 0.692,
    "myeloid": 0.692,
    "bone marrow": 0.692,
    "plasma cell": 0.692,
    "sickle cell": 0.692,
    "thalassemia": 0.692,
    "hemophilia": 0.692,
    "hemoglobinopathy": 0.692,
    "thrombocytopenia": 0.692,
    "neutropenia": 0.692,
    "hemolytic": 0.692,
    "aplastic anemia": 0.692,
    "polycythemia": 0.692,
    "myelofibrosis": 0.692,
    "acute myeloid": 0.692,
    "aml": 0.692,
    "acute lymphoblastic": 0.692,
    "all": 0.692,
    "chronic myeloid": 0.692,
    "cml": 0.692,
    "chronic lymphocytic": 0.692,
    "cll": 0.692,
    "hodgkin": 0.692,
    "non-hodgkin": 0.692,
    "diffuse large b-cell": 0.692,
    "marginal zone": 0.692,

    # Cardiovascular
    "cardiovascular": 0.575,
    "heart": 0.575,
    "cardiac": 0.575,
    "hypercholesterolemia": 0.575,
    "cholesterol": 0.575,
    "lipid": 0.575,
    "dyslipidemia": 0.575,
    "atherosclerosis": 0.575,
    "heart failure": 0.575,
    "hf": 0.575,
    "arrhythmia": 0.575,
    "atrial fibrillation": 0.575,
    "afib": 0.575,
    "hypertension": 0.575,
    "myocardial infarction": 0.575,
    "coronary": 0.575,
    "angina": 0.575,
    "cardiomyopathy": 0.575,
    "valvular": 0.575,

    # Infectious Disease
    "infectious disease": 0.65,
    "infection": 0.65,
    "antibiotic": 0.65,
    "antiviral": 0.65,
    "antibacterial": 0.65,
    "antimicrobial": 0.65,
    "bacterial": 0.65,
    "viral": 0.65,
    "fungal": 0.65,
    "sepsis": 0.65,
    "pneumonia": 0.65,
    "tuberculosis": 0.65,
    "tb": 0.65,
    "hiv": 0.65,
    "hepatitis": 0.65,
    "hcv": 0.65,
    "hbv": 0.65,
    "influenza": 0.65,
    "flu": 0.65,
    "covid": 0.65,
    "coronavirus": 0.65,
    "rsv": 0.65,
    "respiratory syncytial": 0.65,
    "c. difficile": 0.65,
    "cdiff": 0.65,
    "clostridium difficile": 0.65,
    "mrsa": 0.65,
    "methicillin-resistant": 0.65,

    # Metabolic
    "metabolic": 0.60,
    "endocrine": 0.60,
    "diabetes": 0.60,
    "diabetic": 0.60,
    "type 2 diabetes": 0.60,
    "t2d": 0.60,
    "type 1 diabetes": 0.60,
    "t1d": 0.60,
    "obesity": 0.60,
    "weight loss": 0.60,
    "thyroid": 0.60,
    "hyperthyroidism": 0.60,
    "hypothyroidism": 0.60,
    "metabolic syndrome": 0.60,
    "hyperglycemia": 0.60,
    "hypoglycemia": 0.60,
    "achondroplasia": 0.60,
    "dwarfism": 0.60,
    "growth disorder": 0.60,

    # Gastroenterology
    "gastroenterology": 0.60,
    "gi": 0.60,
    "ibd": 0.60,
    "inflammatory bowel": 0.60,
    "crohn": 0.60,
    "crohn's disease": 0.60,
    "colitis": 0.60,
    "ulcerative": 0.60,
    "ulcerative colitis": 0.60,
    "uc": 0.60,
    "irritable bowel": 0.60,
    "ibs": 0.60,
    "celiac": 0.60,
    "eosinophilic esophagitis": 0.60,
    "eoe": 0.60,
    "gastric": 0.60,
    "gastritis": 0.60,
    "gerd": 0.60,
    "reflux": 0.60,

    # Liver
    "nash": 0.60,
    "mash": 0.60,
    "liver": 0.60,
    "hepatic": 0.60,
    "cirrhosis": 0.60,
    "fibrosis": 0.60,
    "liver fibrosis": 0.60,
    "nonalcoholic steatohepatitis": 0.60,
    "nonalcoholic fatty liver": 0.60,
    "nafld": 0.60,
    "primary biliary": 0.60,
    "pbc": 0.60,
    "primary sclerosing": 0.60,
    "psc": 0.60,

    # Respiratory
    "respiratory": 0.60,
    "asthma": 0.60,
    "copd": 0.60,
    "chronic obstructive": 0.60,
    "pulmonary": 0.60,
    "lung": 0.60,
    "bronchitis": 0.60,
    "emphysema": 0.60,
    "interstitial lung": 0.60,
    "ild": 0.60,
    "pulmonary fibrosis": 0.60,
    "ipf": 0.60,
    "idiopathic pulmonary fibrosis": 0.60,
    "cystic fibrosis": 0.60,
    "cf": 0.60,
    "pulmonary hypertension": 0.60,
    "pah": 0.60,

    # Genitourinary/Kidney
    "genitourinary": 0.692,
    "urology": 0.692,
    "kidney": 0.692,
    "renal": 0.692,
    "chronic kidney": 0.692,
    "ckd": 0.692,
    "kidney disease": 0.692,
    "nephropathy": 0.692,
    "diabetic kidney": 0.692,
    "dialysis": 0.692,
    "glomerulonephritis": 0.692,
    "nephrotic": 0.692,
    "bladder": 0.692,
    "urinary": 0.692,
    "prostate": 0.692,
    "bph": 0.692,
    "benign prostatic": 0.692,

    # Dermatology/Allergy (BIO: Adjusted for 2026 Benchmarks)
    "dermatology": 0.65,
    "skin": 0.65,
    "psoriasis": 0.65,
    "atopic": 0.65,
    "eczema": 0.65,
    "atopic dermatitis": 0.65,
    "ad": 0.65,
    "urticaria": 0.65,
    "hives": 0.65,
    "pruritus": 0.65,
    "itching": 0.65,
    "acne": 0.65,
    "rosacea": 0.65,
    "vitiligo": 0.65,
    "alopecia": 0.65,
    "alopecia areata": 0.65,
    "hair loss": 0.65,
    "allergy": 0.72,
    "allergic": 0.72,
    "anaphylaxis": 0.72,
    "forehead lines": 0.65,
    "wrinkles": 0.65,

    # Rheumatology/Autoimmune
    "rheumatology": 0.60,
    "autoimmune": 0.60,
    "arthritis": 0.60,
    "rheumatoid arthritis": 0.60,
    "ra": 0.60,
    "osteoarthritis": 0.60,
    "psoriatic arthritis": 0.60,
    "psa": 0.60,
    "ankylosing spondylitis": 0.60,
    "as": 0.60,
    "axial spondyloarthritis": 0.60,
    "lupus": 0.60,
    "systemic lupus erythematosus": 0.60,
    "sle": 0.60,
    "scleroderma": 0.60,
    "systemic sclerosis": 0.60,
    "ssc": 0.60,
    "myositis": 0.60,
    "dermatomyositis": 0.60,
    "polymyositis": 0.60,
    "sjogren": 0.60,
    "vasculitis": 0.60,
    "giant cell arteritis": 0.60,
    "gca": 0.60,
    "polymyalgia rheumatica": 0.60,
    "pmr": 0.60,
    "gout": 0.60,
    "hyperuricemia": 0.60,

    # Neurology/Sleep (Adjusted for 2026 Sleep-Wake Success)
    "neurology": 0.60,
    "cns": 0.60,
    "central nervous system": 0.60,
    "alzheimer": 0.60,
    "dementia": 0.60,
    "parkinson": 0.60,
    "parkinson's disease": 0.60,
    "pd": 0.60,
    "multiple sclerosis": 0.60,
    "ms": 0.60,
    "epilepsy": 0.60,
    "seizure": 0.60,
    "migraine": 0.60,
    "headache": 0.60,
    "neuropathy": 0.60,
    "peripheral neuropathy": 0.60,
    "neuropathic pain": 0.60,
    "stroke": 0.60,
    "cerebrovascular": 0.60,
    "als": 0.60,
    "amyotrophic lateral sclerosis": 0.60,
    "huntington": 0.60,
    "myasthenia gravis": 0.60,
    "mg": 0.60,
    "duchenne": 0.60,
    "duchenne muscular dystrophy": 0.60,
    "dmd": 0.60,
    "muscular dystrophy": 0.60,
    "spinal muscular atrophy": 0.60,
    "sma": 0.60,
    "charcot-marie-tooth": 0.60,
    "cmt": 0.60,
    "friedreich ataxia": 0.60,
    "ataxia": 0.60,
    "insomnia": 0.60,
    "sleep disorder": 0.60,

    # Psychiatry
    "psychiatry": 0.575,
    "depression": 0.575,
    "major depressive disorder": 0.575,
    "mdd": 0.575,
    "anxiety": 0.575,
    "generalized anxiety": 0.575,
    "gad": 0.575,
    "panic disorder": 0.575,
    "ptsd": 0.575,
    "post-traumatic stress": 0.575,
    "ocd": 0.575,
    "obsessive-compulsive": 0.575,
    "bipolar": 0.575,
    "schizophrenia": 0.575,
    "psychosis": 0.575,
    "adhd": 0.575,
    "attention deficit": 0.575,
    "autism": 0.575,
    "asd": 0.575,
    "autism spectrum": 0.575,

    "ophthalmology": 0.512,
    "eye": 0.512,
    "vision": 0.512,
    "ocular": 0.512,
    "retina": 0.512,
    "retinal": 0.512,
    "macular degeneration": 0.512,
    "amd": 0.512,
    "namd": 0.512,
    "wet amd": 0.512,
    "age-related macular": 0.512,
    "diabetic retinopathy": 0.512,
    "glaucoma": 0.512,
    "uveitis": 0.512,
    "dry eye": 0.512,
    "keratoconjunctivitis": 0.512,
    "geographic atrophy": 0.512,

    # Rare/Orphan (Adjusted for 2026 Benchmark: ~60%)
    "orphan": 0.60,
    "rare disease": 0.60,
    "ultra-rare": 0.60,
    "genetic disorder": 0.60,
    "inherited": 0.60,
    "lysosomal storage": 0.60,
    "gaucher": 0.60,
    "fabry": 0.60,
    "pompe": 0.60,
    "mucopolysaccharidosis": 0.60,
    "mps": 0.60,
}

# Transition: Phase II -> Phase III Transition Success
PHASE2_SUCCESS_RATES = {
    # Oncology (2026 Baseline: ~25-29%)
    "oncology": 0.29,
    "cancer": 0.29,
    "tumor": 0.29,
    "tumour": 0.29,
    "adenocarcinoma": 0.29,
    "sarcoma": 0.29,
    "melanoma": 0.29,
    "carcinoma": 0.29,
    "glioblastoma": 0.29,
    "mesothelioma": 0.29,
    "neoplasm": 0.29,
    "malignancy": 0.29,
    "malignant": 0.29,
    "metastatic": 0.29,
    "solid tumor": 0.29,
    "nsclc": 0.29,
    "non-small cell lung": 0.29,
    "small cell lung": 0.29,
    "breast cancer": 0.29,
    "prostate cancer": 0.29,
    "colorectal": 0.29,
    "pancreatic": 0.29,
    "ovarian": 0.29,
    "bladder cancer": 0.29,
    "renal cell carcinoma": 0.29,
    "hepatocellular": 0.29,
    "gastric cancer": 0.29,
    "esophageal": 0.29,
    "head and neck": 0.29,
    "squamous cell": 0.29,
    "basal cell": 0.29,

    # Hematology (Highest Phase 2 Success: ~48%)
    "hematology": 0.481,
    "myelodysplastic": 0.481,
    "mds": 0.481,
    "myeloma": 0.481,
    "multiple myeloma": 0.481,
    "myeloid": 0.481,
    "bone marrow": 0.481,
    "plasma cell": 0.481,
    "sickle cell": 0.481,
    "thalassemia": 0.481,
    "blood": 0.481,
    "anemia": 0.481,
    "leukemia": 0.481,
    "lymphoma": 0.481,
    "hemophilia": 0.481,
    "hemoglobinopathy": 0.481,
    "thrombocytopenia": 0.481,
    "neutropenia": 0.481,
    "hemolytic": 0.481,
    "aplastic anemia": 0.481,
    "polycythemia": 0.481,
    "myelofibrosis": 0.481,
    "acute myeloid": 0.481,
    "aml": 0.481,
    "acute lymphoblastic": 0.481,
    "all": 0.481,
    "chronic myeloid": 0.481,
    "cml": 0.481,
    "chronic lymphocytic": 0.481,
    "cll": 0.481,
    "hodgkin": 0.481,
    "non-hodgkin": 0.481,
    "diffuse large b-cell": 0.481,
    "marginal zone": 0.481,

    # Cardiovascular (~24-25%)
    "cardiovascular": 0.245,
    "heart": 0.245,
    "cardiac": 0.245,
    "hypercholesterolemia": 0.245,
    "cholesterol": 0.245,
    "lipid": 0.245,
    "dyslipidemia": 0.245,
    "atherosclerosis": 0.245,
    "heart failure": 0.245,
    "hf": 0.245,
    "arrhythmia": 0.245,
    "atrial fibrillation": 0.245,
    "afib": 0.245,
    "hypertension": 0.245,
    "myocardial infarction": 0.245,
    "coronary": 0.245,
    "angina": 0.245,
    "cardiomyopathy": 0.245,
    "valvular": 0.245,

    # Infectious Disease (~43%)
    "infectious disease": 0.43,
    "infection": 0.43,
    "antibiotic": 0.43,
    "antiviral": 0.43,
    "antibacterial": 0.43,
    "antimicrobial": 0.43,
    "bacterial": 0.43,
    "viral": 0.43,
    "fungal": 0.43,
    "sepsis": 0.43,
    "pneumonia": 0.43,
    "tuberculosis": 0.43,
    "tb": 0.43,
    "hiv": 0.43,
    "hepatitis": 0.43,
    "hcv": 0.43,
    "hbv": 0.43,
    "influenza": 0.43,
    "flu": 0.43,
    "covid": 0.43,
    "coronavirus": 0.43,
    "rsv": 0.43,
    "respiratory syncytial": 0.43,
    "c. difficile": 0.43,
    "cdiff": 0.43,
    "clostridium difficile": 0.43,
    "mrsa": 0.43,
    "methicillin-resistant": 0.43,

    # Metabolic (~42.5%)
    "metabolic": 0.425,
    "endocrine": 0.425,
    "diabetes": 0.425,
    "diabetic": 0.425,
    "type 2 diabetes": 0.425,
    "t2d": 0.425,
    "type 1 diabetes": 0.425,
    "t1d": 0.425,
    "obesity": 0.425,
    "weight loss": 0.425,
    "thyroid": 0.425,
    "hyperthyroidism": 0.425,
    "hypothyroidism": 0.425,
    "metabolic syndrome": 0.425,
    "hyperglycemia": 0.425,
    "hypoglycemia": 0.425,
    "achondroplasia": 0.425,
    "dwarfism": 0.425,
    "growth disorder": 0.425,

    # Gastroenterology (~32.5%)
    "gastroenterology": 0.325,
    "nash": 0.325,
    "mash": 0.325,
    "gi": 0.325,
    "ulcerative": 0.325,
    "ulcerative colitis": 0.325,
    "uc": 0.325,
    "inflammatory bowel": 0.325,
    "ibd": 0.325,
    "crohn": 0.325,
    "crohn's disease": 0.325,
    "colitis": 0.325,
    "irritable bowel": 0.325,
    "ibs": 0.325,
    "celiac": 0.325,
    "eosinophilic esophagitis": 0.325,
    "eoe": 0.325,
    "gastric": 0.325,
    "gastritis": 0.325,
    "gerd": 0.325,
    "reflux": 0.325,
    "liver": 0.325,
    "hepatic": 0.325,
    "cirrhosis": 0.325,
    "fibrosis": 0.325,
    "liver fibrosis": 0.325,
    "nonalcoholic steatohepatitis": 0.325,
    "nonalcoholic fatty liver": 0.325,
    "nafld": 0.325,
    "primary biliary": 0.325,
    "pbc": 0.325,
    "primary sclerosing": 0.325,
    "psc": 0.325,

    # Respiratory (~32.5%)
    "respiratory": 0.325,
    "asthma": 0.325,
    "copd": 0.325,
    "chronic obstructive": 0.325,
    "pulmonary": 0.325,
    "lung": 0.325,
    "bronchitis": 0.325,
    "emphysema": 0.325,
    "interstitial lung": 0.325,
    "ild": 0.325,
    "pulmonary fibrosis": 0.325,
    "ipf": 0.325,
    "idiopathic pulmonary fibrosis": 0.325,
    "cystic fibrosis": 0.325,
    "cf": 0.325,
    "pulmonary hypertension": 0.325,
    "pah": 0.325,

    # Genitourinary/Kidney (~22-25% in 2026)
    "genitourinary": 0.25,
    "chronic kidney": 0.25,
    "ckd": 0.25,
    "renal": 0.25,
    "kidney": 0.25,
    "kidney disease": 0.25,
    "nephropathy": 0.25,
    "diabetic kidney": 0.25,
    "dialysis": 0.25,
    "glomerulonephritis": 0.25,
    "nephrotic": 0.25,
    "urology": 0.25,
    "bladder": 0.25,
    "urinary": 0.25,
    "prostate": 0.25,
    "bph": 0.25,
    "benign prostatic": 0.25,

    # Dermatology/Allergy (Adjusted to ~38-40% for 2026)
    "atopic": 0.38,
    "eczema": 0.38,
    "atopic dermatitis": 0.38,
    "ad": 0.38,
    "psoriasis": 0.38,
    "urticaria": 0.38,
    "hives": 0.38,
    "pruritus": 0.38,
    "itching": 0.38,
    "dermatology": 0.38,
    "skin": 0.38,
    "acne": 0.38,
    "rosacea": 0.38,
    "vitiligo": 0.38,
    "alopecia": 0.38,
    "alopecia areata": 0.38,
    "hair loss": 0.38,
    "allergy": 0.38,
    "allergic": 0.38,
    "anaphylaxis": 0.38,
    "forehead lines": 0.38,
    "wrinkles": 0.38,

    # Rheumatology/Autoimmune (~32.5%)
    "autoimmune": 0.325,
    "rheumatology": 0.325,
    "arthritis": 0.325,
    "rheumatoid arthritis": 0.325,
    "ra": 0.325,
    "osteoarthritis": 0.325,
    "psoriatic arthritis": 0.325,
    "psa": 0.325,
    "ankylosing spondylitis": 0.325,
    "as": 0.325,
    "axial spondyloarthritis": 0.325,
    "lupus": 0.325,
    "systemic lupus erythematosus": 0.325,
    "sle": 0.325,
    "scleroderma": 0.325,
    "systemic sclerosis": 0.325,
    "ssc": 0.325,
    "myositis": 0.325,
    "dermatomyositis": 0.325,
    "polymyositis": 0.325,
    "sjogren": 0.325,
    "vasculitis": 0.325,
    "giant cell arteritis": 0.325,
    "gca": 0.325,
    "polymyalgia rheumatica": 0.325,
    "pmr": 0.325,
    "gout": 0.325,
    "hyperuricemia": 0.325,

    # Neurology (~32.5%)
    "neurology": 0.325,
    "cns": 0.325,
    "central nervous system": 0.325,
    "alzheimer": 0.325,
    "dementia": 0.325,
    "parkinson": 0.325,
    "parkinson's disease": 0.325,
    "pd": 0.325,
    "multiple sclerosis": 0.325,
    "ms": 0.325,
    "epilepsy": 0.325,
    "seizure": 0.325,
    "migraine": 0.325,
    "headache": 0.325,
    "neuropathy": 0.325,
    "peripheral neuropathy": 0.325,
    "neuropathic pain": 0.325,
    "stroke": 0.325,
    "cerebrovascular": 0.325,
    "als": 0.325,
    "amyotrophic lateral sclerosis": 0.325,
    "huntington": 0.325,
    "myasthenia gravis": 0.325,
    "mg": 0.325,
    "duchenne": 0.325,
    "duchenne muscular dystrophy": 0.325,
    "dmd": 0.325,
    "muscular dystrophy": 0.325,
    "spinal muscular atrophy": 0.325,
    "sma": 0.325,
    "charcot-marie-tooth": 0.325,
    "cmt": 0.325,
    "friedreich ataxia": 0.325,
    "ataxia": 0.325,

    # Psychiatry (~24-28% in 2026)
    "psychiatry": 0.28,
    "depression": 0.28,
    "major depressive disorder": 0.28,
    "mdd": 0.28,
    "anxiety": 0.28,
    "generalized anxiety": 0.28,
    "gad": 0.28,
    "panic disorder": 0.28,
    "ptsd": 0.28,
    "post-traumatic stress": 0.28,
    "ocd": 0.28,
    "obsessive-compulsive": 0.28,
    "bipolar": 0.28,
    "schizophrenia": 0.28,
    "psychosis": 0.28,
    "adhd": 0.28,
    "attention deficit": 0.28,
    "autism": 0.28,
    "asd": 0.28,
    "autism spectrum": 0.28,
    "insomnia": 0.28,
    "sleep disorder": 0.28,

    # Ophthalmology (~40-42% in 2026)
    "ophthalmology": 0.447,
    "eye": 0.447,
    "vision": 0.447,
    "ocular": 0.447,
    "retina": 0.447,
    "retinal": 0.447,
    "macular degeneration": 0.447,
    "amd": 0.447,
    "namd": 0.447,
    "wet amd": 0.447,
    "age-related macular": 0.447,
    "diabetic retinopathy": 0.447,
    "glaucoma": 0.447,
    "uveitis": 0.447,
    "dry eye": 0.447,
    "keratoconjunctivitis": 0.447,
    "geographic atrophy": 0.447,

    # Rare/Orphan (Adjusted for 2026 Phase 2 Benchmark: 51.5%)
    "orphan": 0.515,
    "rare disease": 0.515,
    "ultra-rare": 0.515,
    "genetic disorder": 0.515,
    "inherited": 0.515,
    "lysosomal storage": 0.515,
    "gaucher": 0.515,
    "fabry": 0.515,
    "pompe": 0.515,
    "mucopolysaccharidosis": 0.515,
    "mps": 0.515,
}

# NOTE: Ensure your .env file has the correct keys/emails if needed by the libraries
downloader = Downloader("Personal", os.getenv("SEC_EMAIL"))


#Helper - don't have to call
def normalize_fund_name(fund_name):
    """
    Convert CIK numbers to fund names
    Also handles some common variations
    """
    # Reverse lookup: CIK → Name
    cik_to_name = {v: k for k, v in FUNDS.items()}

    # If it's a CIK number, convert it
    if fund_name in cik_to_name:
        return cik_to_name[fund_name]

    # Otherwise return as-is
    return fund_name

#Classify disease category. Helper function, do not need to call. 
def classify_disease_category(indication: str) -> tuple:
    """
    Classify indication into disease category and return success rates
    
    Uses comprehensive keyword matching across all BIO disease areas.
    Checks longer/more specific terms first to avoid false matches.
    
    Returns: (category_name, phase3_success_rate, phase2_success_rate)
    """
    if not indication:
        avg_phase3 = sum(PHASE3_SUCCESS_RATES.values()) / len(PHASE3_SUCCESS_RATES)
        avg_phase2 = sum(PHASE2_SUCCESS_RATES.values()) / len(PHASE2_SUCCESS_RATES)
        return ('unknown', avg_phase3, avg_phase2)
    
    indication_lower = indication.lower()
    
    # Sort keywords by length (descending) to match specific terms first
    # e.g., "chronic kidney disease" before "kidney" or "chronic"
    sorted_keywords = sorted(PHASE3_SUCCESS_RATES.keys(), key=len, reverse=True)
    
    for keyword in sorted_keywords:
        if keyword in indication_lower:
            phase2_rate = PHASE2_SUCCESS_RATES.get(keyword)
            if phase2_rate is None:
                # If no Phase 2 rate exists for this keyword, use average
                phase2_rate = sum(PHASE2_SUCCESS_RATES.values()) / len(PHASE2_SUCCESS_RATES)
            
            phase3_rate = PHASE3_SUCCESS_RATES[keyword]
            return (keyword, phase3_rate, phase2_rate)
    
    # Default to average if no match found
    avg_phase3 = sum(PHASE3_SUCCESS_RATES.values()) / len(PHASE3_SUCCESS_RATES)
    avg_phase2 = sum(PHASE2_SUCCESS_RATES.values()) / len(PHASE2_SUCCESS_RATES)
    return ('unknown', avg_phase3, avg_phase2)


# --- 1. DOWNLOADER ---
def file_downloader(): 
    print("--- Starting SEC Downloads ---")
    for fund_name, cik in FUNDS.items():
        print(f"Processing {fund_name} ({cik})...")
        try:
            downloader.get("13F-HR", cik, limit=80)
            # FIX 6: Rate Limiting
            time.sleep(0.5) 
            print(f"Done downloading {fund_name}")
        except Exception as e:
            print(f"Failed for {fund_name}: {e}")


cik_to_name = {v: k for k, v in FUNDS.items()}

all_latest_stocks = []

#Helper function, prevents CUSIPS being updated from 004728139123 to 4728139123
def normalize_cusip(cusip):
    """
    Normalize CUSIP to 9 digits with leading zeros
    Handles cases where Excel/CSV stripped leading zeros
    """
    if pd.isna(cusip):
        return None
    
    cusip = str(cusip).strip()
    
    # Remove any non-alphanumeric characters
    cusip = ''.join(c for c in cusip if c.isalnum())
    
    # Pad to 9 digits if needed
    if len(cusip) < 9:
        cusip = cusip.zfill(9)
    
    return cusip

# --- 2. PROCESS FILINGS ---
def process_filings():
    global all_latest_stocks
    # FIX 2: Clear global list to prevent duplicates on re-runs
    all_latest_stocks = []
    
    print("\n--- Processing Filings ---")
    
    for cik_dir in base_path.iterdir():
        if not cik_dir.is_dir():
            continue
        
        cik = cik_dir.name
        fund_name = cik_to_name.get(cik, cik)
        holdings = []
        
        # Check if the 13F-HR directory exists for the CIK
        if not (cik_dir / "13F-HR").is_dir():
            print(f"Skipping {fund_name}: '13F-HR' directory not found.")
            continue
            
        for txt_file in (cik_dir / "13F-HR").glob("*/full-submission.txt"):
            content = txt_file.read_text(errors='ignore')

            # Handle optional XML namespace prefix (e.g., ns1:)
            filing_date = re.search(r'<(?:\w+:)?signatureDate>(\d{2}-\d{2}-\d{4})</(?:\w+:)?signatureDate>', content)
            report_date = re.search(r'<(?:\w+:)?periodOfReport>(\d{2}-\d{2}-\d{4})</(?:\w+:)?periodOfReport>', content)

            # Match infoTable with optional namespace prefix
            for match in re.findall(r'<(?:\w+:)?infoTable>(.*?)</(?:\w+:)?infoTable>', content, re.DOTALL | re.I):

                def extract(tag):
                    # Handle optional namespace prefix in child tags
                    m = re.search(f'<(?:\\w+:)?{tag}>(.*?)</(?:\\w+:)?{tag}>', match, re.I)
                    return m.group(1).strip() if m else ""
                
                holdings.append({
                    "filing_date": filing_date.group(1) if filing_date else "",
                    "report_date": report_date.group(1) if report_date else "",
                    "issuer": extract("nameOfIssuer"),
                    "cusip": extract("cusip"),
                    "shares": extract("sshPrnamt"),
                    "value": extract("value"),
                })
        
        if not holdings:
            print(f"Skipping {fund_name}: No holdings data extracted.")
            continue
        
        df = pd.DataFrame(holdings)

        # Normalize CUSIPs (handles leading zeros)
        df['cusip'] = df['cusip'].apply(normalize_cusip)


        df["shares"] = pd.to_numeric(df["shares"], errors="coerce")
        # Value is reported in thousands, so multiply by 1000
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        
        # FIX 5: Flexible Date Parsing (Removed hardcoded format)
        df["report_date"] = pd.to_datetime(df["report_date"], errors='coerce')
        df["filing_date"] = pd.to_datetime(df["filing_date"], errors='coerce')
        
        df = df.sort_values(["report_date", "value"], ascending=[False, False])
        
        df["quarter"] = df["report_date"].dt.to_period("Q").astype(str)
        
        totals = df.groupby("report_date")["value"].transform("sum")
        df["weight_pct"] = (df["value"] / totals * 100).round(2)
        
        df = df.sort_values(["cusip", "report_date"])
        df["prev_value"] = df.groupby("cusip")["value"].shift(1)
        df["prev_shares"] = df.groupby("cusip")["shares"].shift(1)
        
        # Calculate changes
        df["value_change_pct"] = ((df["value"] - df["prev_value"]) / df["prev_value"] * 100).round(2)
        df["shares_change_pct"] = ((df["shares"] - df["prev_shares"]) / df["prev_shares"] * 100).round(2)
        df = df.replace([float('inf'), float('-inf')], pd.NA)

        # Collect latest quarter stocks for Perplexity
        latest_quarter = df["report_date"].max()
        latest_df = df[df["report_date"] == latest_quarter]
        
        for _, row in latest_df.iterrows():
            all_latest_stocks.append({
                "fund": fund_name,
                "cik": cik,
                "issuer": row["issuer"],
                "cusip": row["cusip"],
                "weight_pct": row["weight_pct"],
                "shares_change_pct": row["shares_change_pct"]
            })
        
        df = df.sort_values(["report_date", "value"], ascending=[False, False])
        
        out = df[["filing_date", "report_date", "quarter", "issuer", "cusip", "shares", "value", "weight_pct", "value_change_pct", "shares_change_pct"]]
        
        # Prepare for CSV output formatting
        quarters = out["quarter"].unique()
        chunks = [out[out["quarter"] == q] for q in quarters]
        blank = pd.DataFrame([[""] * len(out.columns)], columns=out.columns)
        
        if len(chunks) > 0:
            result = pd.concat([chunk for q in chunks for chunk in (q, blank, blank)][:-2])
            result.to_csv(cik_dir / f"{fund_name}.csv", index=False)
            print(f"✓ {fund_name}: {len(df)} holdings across {len(quarters)} quarters")
        else:
            print(f"⚠ {fund_name}: No quarters found.")


#4. MASTER SET GENERATION ---
def master_set(base_path):
    print("\n--- Generating Master Set ---")
    all_latest_fund_holdings = []
    
    for cik_dir in base_path.iterdir():
        if not cik_dir.is_dir():
            continue
        csvs = [f for f in cik_dir.glob("*.csv") 
                if 'bet_tracker' not in f.name 
                and 'high_conviction' not in f.name]    
        # FIX 4: Explicit CSV discovery (Safer)
        if len(csvs) == 0:
            continue
        
        # If multiple CSVs exist, prefer the one matching the known fund name if possible,
        # otherwise take the first one found.
        fund_name_file = csvs[0]
        
        try:
            df = pd.read_csv(fund_name_file)
            df = df.dropna(subset=['issuer'])
            
            # FIX 5: Flexible date parsing again
            df['filing_date'] = pd.to_datetime(df['filing_date'], errors='coerce')
            
            max_filing_date = df['filing_date'].dropna().max()
            if pd.isna(max_filing_date):
                continue
            
            latest_fund_holdings = df[df['filing_date'] == max_filing_date].copy()
            latest_fund_holdings['fund_name'] = fund_name_file.stem
            
            latest_fund_holdings['shares_change_pct'] = pd.to_numeric(
                latest_fund_holdings['shares_change_pct'], errors='coerce'
            )
            all_latest_fund_holdings.append(latest_fund_holdings)
        except Exception as e:
            print(f"Error processing {fund_name_file.name}: {e}")
            
    if not all_latest_fund_holdings:
        print("FATAL: No fund data found to create master set.")
        return
    master_df = pd.concat(all_latest_fund_holdings, ignore_index=True)
    
    # Find largest holder for each CUSIP
    largest_holder_lookup = master_df.loc[master_df.groupby('cusip')['value'].idxmax()][['cusip', 'fund_name']].rename(
        columns={'fund_name': 'largest_holder'}
    )
    
    agg_functions = {
        'shares': 'sum',
        'value': 'sum',
        'weight_pct': 'mean',
        'shares_change_pct': 'mean',
        'fund_name': 'nunique',
    }
    
    aggregated_data = master_df.groupby('cusip').agg(agg_functions).reset_index()
    
    aggregated_data = aggregated_data.rename(columns={
        'shares': 'sum_of_all_funds_shares',
        'value': 'sum_of_all_funds_value',
        'weight_pct': 'avg_fund_allocation_pct',
        'shares_change_pct': 'avg_shares_change_pct',
        'fund_name': 'number_of_funds_holding'
    })
    
    def get_most_frequent(series):
        return series.mode()[0] if not series.empty else None
    issuer_lookup = master_df.groupby('cusip')['issuer'].apply(get_most_frequent).reset_index()
    aggregated_data = aggregated_data.merge(issuer_lookup, on='cusip', how='left')
    
    # Merge largest holder information
    aggregated_data = aggregated_data.merge(largest_holder_lookup, on='cusip', how='left')
    
    total_unique_funds = master_df['fund_name'].nunique()
    aggregated_data['number_of_funds_holding_pct'] = (
        aggregated_data['number_of_funds_holding'] / total_unique_funds * 100
    ).round(2)
    
    latest_info = master_df[['filing_date', 'report_date', 'quarter']].max()
    aggregated_data.insert(0, 'filing_date', latest_info['filing_date'])
    aggregated_data.insert(1, 'report_date', latest_info['report_date'])
    aggregated_data.insert(2, 'quarter', latest_info['quarter'])
    
    final_master_table = aggregated_data.sort_values(
        by=['number_of_funds_holding', 'sum_of_all_funds_value'],
        ascending=[False, False]
    )
    
    final_columns = [
        'filing_date', 'report_date', 'quarter', 'issuer', 'cusip',
        'sum_of_all_funds_shares', 'sum_of_all_funds_value',
        'avg_fund_allocation_pct',
        'number_of_funds_holding',
        'number_of_funds_holding_pct',
        'avg_shares_change_pct',
        'largest_holder'
    ]
    final_master_table = final_master_table[final_columns].copy()
    final_master_table['avg_shares_change_pct'] = final_master_table['avg_shares_change_pct'].round(2)
    
    output_path = base_path / "master.csv"
    final_master_table.to_csv(output_path, index=False)
    print(f"\n✅ Master data generated. Saved {len(final_master_table)} unique CUSIPs to {output_path}")
    return final_master_table

#4.5
def populate_fund_holdings_database():
    """
    Load all fund CSV files into the fund_holdings database table
    Run this after generate_master_holdings() to sync CSVs to database
    """
    print("\n=== POPULATING FUND HOLDINGS DATABASE ===\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    # Clear existing data
    conn.execute("DELETE FROM fund_holdings")
    
    total_rows = 0
    
    for fund_name, cik in FUNDS.items():
        fund_csv = base_path / cik / f"{fund_name}.csv"
        
        if not fund_csv.exists():
            continue
        
        print(f"Loading {fund_name}...", end=' ', flush=True)
        
        try:
            df = pd.read_csv(fund_csv)
            df = df.dropna(subset=['cusip', 'quarter', 'report_date'])
            
            # Normalize CUSIPs
            df['cusip'] = df['cusip'].apply(normalize_cusip)
            
            # Insert into database
            for _, row in df.iterrows():
                conn.execute('''
                    INSERT INTO fund_holdings 
                    (fund_name, cusip, quarter, report_date, filing_date, 
                     shares, value, position_pct, shares_change_pct, value_change_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fund_name,
                    row['cusip'],
                    row['quarter'],
                    row['report_date'],
                    row['filing_date'],
                    row.get('shares'),
                    row.get('value'),
                    row.get('weight_pct'),  # Note: CSV calls it weight_pct
                    row.get('shares_change_pct'),
                    row.get('value_change_pct')
                ))
            
            total_rows += len(df)
            print(f"✓ {len(df)} holdings")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            continue
    
    conn.commit()
    
    # Verify
    count = conn.execute("SELECT COUNT(*) FROM fund_holdings").fetchone()[0]
    funds_count = conn.execute("SELECT COUNT(DISTINCT fund_name) FROM fund_holdings").fetchone()[0]
    
    conn.close()
    
    print(f"\n✅ Loaded {count:,} holdings from {funds_count} funds into database")


def setup_database():
    """
    Initialize SQLite database with all required tables
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Table 1: Companies
    c.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            cusip TEXT PRIMARY KEY,
            issuer_name_raw TEXT,
            issuer_name_clean TEXT,
            ticker TEXT,
            market_cap REAL,
            last_updated DATE
        )
    ''')
    
    # Table 2: Clinical Trials - FIXED SCHEMA
    c.execute('''
        CREATE TABLE IF NOT EXISTS clinical_trials (
            nct_id TEXT,
            cusip TEXT,
            drug_name TEXT,
            indication TEXT,
            phase TEXT,
            sponsor_name TEXT,
            trial_status TEXT,
            is_lead_sponsor INTEGER DEFAULT 1,
            start_date TEXT,
            primary_completion_date TEXT,
            completion_date TEXT,
            last_updated TEXT,
            PRIMARY KEY (nct_id, cusip),
            FOREIGN KEY (cusip) REFERENCES companies(cusip)
        )
    ''')
    
    # Table 3: Catalyst Calendar
    c.execute('''
        CREATE TABLE IF NOT EXISTS catalyst_calendar (
            catalyst_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cusip TEXT,
            ticker TEXT,
            drug_name TEXT,
            indication TEXT,
            catalyst_type TEXT,
            catalyst_date TEXT,
            estimated INTEGER,
            outcome TEXT,
            source TEXT,
            notes TEXT,
            FOREIGN KEY (cusip) REFERENCES companies(cusip)
        )
    ''')
    
    # Table 4: Fund Holdings
    c.execute('''
        CREATE TABLE IF NOT EXISTS fund_holdings (
            holding_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fund_name TEXT,
            cusip TEXT,
            quarter TEXT,
            report_date TEXT,
            filing_date TEXT,
            shares REAL,
            value REAL,
            position_pct REAL,
            shares_change_pct REAL,
            value_change_pct REAL,
            FOREIGN KEY (cusip) REFERENCES companies(cusip)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized at", DB_PATH)

def clean_company_name(raw_name: str) -> str:
    """
    Clean company name for ClinicalTrials.gov search
    
    Removes:
    - CDATA tags
    - Inc, Corp, Ltd, etc.
    - Special characters
    - Trailing whitespace
    """
    # Remove CDATA tags
    name = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', raw_name)
    
    # Decode HTML entities
    name = html.unescape(name)
    
    # Remove common suffixes (AGGRESSIVE - removes all variants)
    suffixes = [
        r'\s+INC\.?$',
        r'\s+CORP\.?$', 
        r'\s+LTD\.?$',
        r'\s+LLC\.?$',
        r'\s+CO\.?$',
        r'\s+PLC\.?$',
        r',?\s*INC\.?$',
        r',?\s*CORP\.?$',
        r'\s+INCORPORATED$',
        r'\s+CORPORATION$',
        r'\s+COMPANY$',
        r'\s+ORD$',  # "Bristol Myers Squibb Ord" → "Bristol Myers Squibb"
        r'\s+FORMERLY.*$',  # "Elevance Health Inc Formerly..." → "Elevance Health"
        r'\s+DEL$',  # "Centene Corp Del" → "Centene"
    ]
    
    for suffix in suffixes:
        name = re.sub(suffix, '', name, flags=re.IGNORECASE)
    
    # Remove "& CO" type patterns
    name = re.split(r'\s*&\s*', name)[0]
    
    # Clean up whitespace
    name = ' '.join(name.split())
    name = name.strip()
    
    # Title case
    name = name.title()
    
    # Special cases (brand names)
    replacements = {
        'Abbvie': 'AbbVie',
        'Biomarin': 'BioMarin',
        'Biogen': 'Biogen',
        'Biontech': 'BioNTech',
        'Moderna': 'Moderna',
        'Pfizer': 'Pfizer',
        'Crispr': 'CRISPR',
        'Grail': 'GRAIL',
        'Mckesson': 'McKesson',
    }
    
    for old, new in replacements.items():
        if old.lower() in name.lower():
            name = re.sub(old, new, name, flags=re.IGNORECASE)
    
    return name

def build_company_mapping():
    """
    Extract unique companies from master.csv and store in database
    """
    print("\n=== BUILDING COMPANY MAPPING ===\n")
    
    master_path = base_path / "master.csv"
    if not master_path.exists():
        print("⚠ master.csv not found. Run generate_master_holdings() first.")
        return
    
    master_df = pd.read_csv(master_path)
    companies = master_df[['cusip', 'issuer']].drop_duplicates()
    companies['issuer_clean'] = companies['issuer'].apply(clean_company_name)
    
    conn = sqlite3.connect(DB_PATH)
    
    for _, row in companies.iterrows():
        conn.execute('''
            INSERT OR REPLACE INTO companies (cusip, issuer_name_raw, issuer_name_clean, last_updated)
            VALUES (?, ?, ?, ?)
        ''', (row['cusip'], row['issuer'], row['issuer_clean'], datetime.now().date()))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Mapped {len(companies)} companies to database")
    return companies

CLINICAL_TRIALS_API = "https://clinicaltrials.gov/api/v2/studies"

def query_clinicaltrials_for_company(
    company_name: str,
    phases_to_keep: List[str] = ['PHASE1', 'PHASE2', 'PHASE3', 'PHASE1|PHASE2', 'PHASE2|PHASE3'],
    years_back: int = 20,
    page_size: int = 1000
) -> List[Dict]:
    """
    Query ClinicalTrials.gov API using query.spons (lead sponsor only)
    
    FIXED: 
    - Proper name cleaning (no Inc, CDATA, etc.)
    - Includes Phase 1/2 trials
    - Larger page size
    - Better error handling
    - Multiple sponsor name variations
    """
    start_year = date.today().year - years_back
    all_trials = []
    seen_nct_ids = set()
    
    # Generate sponsor name variations
    variations = [company_name, company_name.lower()]
    
    # Remove common suffixes - try ALL of them, not just first match
    suffixes = [' Pharmaceuticals', ' Pharma', ' Therapeutics', ' Biotherapeutics', 
                ' SE', ' S.E.', ' SA', ' S.A.', ' Inc', ' Inc.', ' Corp', ' Corp.', ' Ltd', ' Ltd.', 
                ' LLC', ' Plc', ' NV', ' N.V.', ',', ' Company', ' Co', ' Co.']
    
    base = company_name
    for suffix in suffixes:
        if base.endswith(suffix):
            base = base[:-len(suffix)].strip()
            variations.extend([base, base.lower()])
            # Try removing more suffixes from the base
            for suffix2 in suffixes:
                if base.endswith(suffix2):
                    base2 = base[:-len(suffix2)].strip()
                    variations.extend([base2, base2.lower()])
    
    # First word only (e.g., "Avadel Pharmaceuticals" → "Avadel")
    words = company_name.split()
    if len(words) > 1 and len(words[0]) > 3:
        variations.extend([words[0], words[0].lower()])
    
    # Add period versions (e.g., "SA" → "S.A.")
    if ' SA' in company_name or ' Sa' in company_name:
        variations.append(company_name.replace(' SA', ' S.A.').replace(' Sa', ' S.A.'))
    if ' SE' in company_name or ' Se' in company_name:
        variations.append(company_name.replace(' SE', ' S.E.').replace(' Se', ' S.E.'))
    if ' NV' in company_name or ' Nv' in company_name:
        variations.append(company_name.replace(' NV', ' N.V.').replace(' Nv', ' N.V.'))
    
    # Uppercase version (for acronyms like "ADC")
    if company_name != company_name.upper():
        variations.append(company_name.upper())
    
    variations = list(set(variations))
    
    # Try each variation until we find trials
    for variation in variations:
        page_token = None
        
        while True:
            params = {
                "query.spons": variation,
                "filter.advanced": f"AREA[StartDate]RANGE[{start_year}-01-01,MAX]",
                "pageSize": page_size,
                "format": "json"
            }
            
            if page_token:
                params["pageToken"] = page_token
            
            try:
                response = requests.get(CLINICAL_TRIALS_API, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                studies = data.get('studies', [])
                
                for study in studies:
                    protocol = study.get('protocolSection', {})
                    
                    ident = protocol.get('identificationModule', {})
                    nct_id = ident.get('nctId')
                    
                    # Skip duplicates
                    if nct_id in seen_nct_ids:
                        continue
                    seen_nct_ids.add(nct_id)
                    
                    status = protocol.get('statusModule', {})
                    design = protocol.get('designModule', {})
                    sponsor = protocol.get('sponsorCollaboratorsModule', {})
                    
                    # Get phase
                    phases = design.get('phases', [])
                    phase_str = '|'.join(phases) if phases else None
                    
                    # Filter by phase in Python
                    if phase_str not in phases_to_keep:
                        continue
                    
                    # Get intervention (drug name)
                    interventions = protocol.get('armsInterventionsModule', {}).get('interventions', [])
                    drug_name = interventions[0].get('name') if interventions else None
                    
                    # Get indication
                    conditions = protocol.get('conditionsModule', {}).get('conditions', [])
                    indication = ', '.join(conditions) if conditions else None
                    
                    trial = {
                        'nct_id': nct_id,
                        'title': ident.get('briefTitle'),
                        'drug_name': drug_name,
                        'indication': indication,
                        'phase': phase_str,
                        'sponsor': sponsor.get('leadSponsor', {}).get('name'),
                        'status': status.get('overallStatus'),
                        'start_date': status.get('startDateStruct', {}).get('date'),
                        'primary_completion_date': status.get('primaryCompletionDateStruct', {}).get('date'),
                        'completion_date': status.get('completionDateStruct', {}).get('date'),
                        'last_updated': status.get('lastUpdatePostDateStruct', {}).get('date')
                    }
                    
                    all_trials.append(trial)
                
                # Check for next page
                page_token = data.get("nextPageToken")
                if not page_token:
                    break
                
                time.sleep(0.2)  # Rate limiting
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [400, 403, 404]:
                    # No trials or blocked - normal, just break
                    break
                else:
                    print(f"  ✗ HTTP {e.response.status_code}: {variation}")
                    break
            except Exception as e:
                print(f"  ✗ Error: {variation}: {e}")
                break
        
        # If we found trials with this variation, we can stop trying others
        if all_trials:
            break
    
    return all_trials
def populate_clinical_trials_database():
    """
    Query ClinicalTrials.gov for all companies and store in database
    
    FIXED: 
    - Actually stores data in database now
    - Validates sponsor name matches before storing
    """
    print("\n=== QUERYING CLINICALTRIALS.GOV ===\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    # Get companies
    companies = pd.read_sql("""
        SELECT cusip, issuer_name_clean 
        FROM companies
        WHERE is_biotech = 1
        ORDER BY ticker
    """, conn)
    
    total_trials = 0
    companies_with_trials = 0
    skipped_sponsor_mismatch = 0
    
    for idx, row in companies.iterrows():
        cusip = row['cusip']
        company_name = row['issuer_name_clean']
        
        print(f"[{idx+1}/{len(companies)}] {company_name}...", end=' ', flush=True)
        
        trials = query_clinicaltrials_for_company(company_name)
        
        if trials:
            valid_trials = 0
            
            # ================================================================
            # CRITICAL FIX: Validate sponsor name matches
            # ================================================================
            for trial in trials:
                sponsor_name = trial['sponsor']
                
                # Check if sponsor name reasonably matches company name
                # Allow partial matches (e.g., "Incyte" matches "Incyte Corporation")
                sponsor_lower = sponsor_name.lower() if sponsor_name else ""
                company_lower = company_name.lower()
                
                # Extract first word of company name (e.g., "Incyte" from "Incyte Corporation")
                company_first_word = company_lower.split()[0] if company_lower else ""
                
                # Match if:
                # 1. Exact match (case insensitive)
                # 2. Sponsor contains company name
                # 3. Company name contains sponsor
                # 4. First word matches (for "Incyte Corp" vs "Incyte")
                is_sponsor_match = (
                    sponsor_lower == company_lower or
                    company_lower in sponsor_lower or
                    sponsor_lower in company_lower or
                    (len(company_first_word) > 3 and company_first_word in sponsor_lower)
                )
                
                if not is_sponsor_match:
                    skipped_sponsor_mismatch += 1
                    continue
                # ================================================================
                
                try:
                    conn.execute('''
                        INSERT OR IGNORE INTO clinical_trials 
                        (nct_id, cusip, drug_name, indication, phase, sponsor_name, trial_status,
                         is_lead_sponsor, start_date, primary_completion_date, completion_date, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        trial['nct_id'],
                        cusip,
                        trial['drug_name'],
                        trial['indication'],
                        trial['phase'],
                        trial['sponsor'],
                        trial['status'],
                        1,  # is_lead_sponsor = True
                        trial['start_date'],
                        trial['primary_completion_date'],
                        trial['completion_date'],
                        trial['last_updated']
                    ))
                    valid_trials += 1
                except Exception as e:
                    print(f"\n  ⚠ Error inserting {trial['nct_id']}: {e}")
            
            total_trials += valid_trials
            
            if valid_trials > 0:
                companies_with_trials += 1
                print(f"✓ {valid_trials} trials (validated)")
            else:
                print("✓ 0 trials (all filtered)")
        else:
            print("✓ 0 trials")
        
        # Commit every 10 companies
        if (idx + 1) % 10 == 0:
            conn.commit()
            print(f"  💾 Committed batch ({idx+1}/{len(companies)})")
        
        time.sleep(0.3)
    
    # Final commit
    conn.commit()
    
    # Verify data was stored
    cursor = conn.execute("SELECT COUNT(*) FROM clinical_trials")
    stored_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n✅ Results:")
    print(f"   - Companies with trials: {companies_with_trials}/{len(companies)}")
    print(f"   - Total trials found: {total_trials}")
    print(f"   - Trials skipped (sponsor mismatch): {skipped_sponsor_mismatch}")
    print(f"   - Total trials in database: {stored_count}")
    
    if stored_count == 0:
        print("\n⚠️ WARNING: No trials stored in database!")
    elif stored_count < total_trials * 0.9:
        print(f"\n⚠️ WARNING: Only {stored_count}/{total_trials} trials stored (possible data loss)")

def export_companies_for_ticker_entry():
    """
    Export companies list to CSV for manual ticker entry
    
    Creates: tickers.csv with columns:
    - cusip
    - company_name
    - ticker (empty - YOU fill this in)
    - exchange (empty - YOU fill this in)
    - is_biotech (empty - for your comments)
    """
    print("\n=== EXPORTING COMPANIES FOR TICKER ENTRY ===\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    companies = pd.read_sql("""
        SELECT 
            cusip,
            issuer_name_raw as company_name_raw,
            issuer_name_clean as company_name,
            ticker,
            '' as exchange,
            '' as is_biotech
        FROM companies
        ORDER BY issuer_name_clean
    """, conn)
    
    conn.close()
    
    output_path = base_path / "tickers.csv"
    companies.to_csv(output_path, index=False)
    
    print(f"✅ Exported {len(companies)} companies")
    print(f"📁 Saved to: {output_path}")
    print("\n📝 Instructions:")
    print("   1. Open tickers.csv in Excel/Numbers")
    print("   2. Fill in 'ticker' column (e.g., AKRO, PFE, MRNA)")
    print("   3. Fill in 'exchange' column (e.g., NASDAQ, NYSE, LSE)")
    print("   5. Save and run import_tickers_from_csv()")
    
    return companies

def import_tickers_from_csv():
    """
    Import manually-entered tickers from tickers.csv back into database
    """
    print("\n=== IMPORTING TICKERS FROM CSV ===\n")
    
    csv_path = base_path / "tickers.csv"
    
    if not csv_path.exists():
        print("⚠ tickers.csv not found. Run export_companies_for_ticker_entry() first.")
        return
    
    tickers_df = pd.read_csv(csv_path)
    
    # Normalize CUSIPs to match database (9 digits with leading zeros)
    tickers_df['cusip'] = tickers_df['cusip'].apply(normalize_cusip)
    
    # Filter for rows with tickers entered
    tickers_df = tickers_df[tickers_df['ticker'].notna() & (tickers_df['ticker'] != '')]
    
    print(f"Found {len(tickers_df)} companies with tickers entered")
    
    if tickers_df.empty:
        print("⚠ No tickers to import")
        return
    
    conn = sqlite3.connect(DB_PATH)
    
    # ADD COLUMN IF NOT EXISTS
    try:
        conn.execute('ALTER TABLE companies ADD COLUMN is_biotech INTEGER DEFAULT 1')
    except:
        pass  # Column already exists
    
    imported = 0
    
    for _, row in tickers_df.iterrows():
        cusip = row['cusip']
        ticker = str(row['ticker']).strip().upper()
        
        # NEW: Get is_biotech flag (default to Yes if missing)
        is_biotech_str = str(row.get('is_biotech', 'Yes')).strip().lower()
        is_biotech = 1 if is_biotech_str in ['yes', 'y', '1', 'true'] else 0
        
        # Update database with is_biotech flag
        conn.execute('''
            UPDATE companies 
            SET ticker = ?, is_biotech = ?, last_updated = ?
            WHERE cusip = ?
        ''', (ticker, is_biotech, datetime.now().date(), cusip))
        
        imported += 1
    
    conn.commit()
    
    # Show stats
    biotech_count = conn.execute('SELECT COUNT(*) FROM companies WHERE is_biotech = 1').fetchone()[0]
    non_biotech_count = conn.execute('SELECT COUNT(*) FROM companies WHERE is_biotech = 0').fetchone()[0]
    
    conn.close()
    
    print(f"✅ Imported {imported} tickers into database")
    print(f"   Biotech: {biotech_count}")
    print(f"   Non-biotech: {non_biotech_count}")
    
    print(f"✅ Imported {imported} tickers into database")

def download_10y_price_history_for_all_tickers():
    """
    Download 10 years of daily price history for all tickers

    Stores in database for instant access later
    Much faster than fetching on-demand
    """
    print("\n=== DOWNLOADING 20-YEAR PRICE HISTORY ===\n")

    conn = sqlite3.connect(DB_PATH)

    # Create price history table if not exists
    conn.execute('''
        CREATE TABLE IF NOT EXISTS daily_stock_prices (
            ticker TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            daily_change_pct REAL,
            PRIMARY KEY (ticker, date)
        )
    ''')
    conn.commit()

    # Get all tickers
    tickers = pd.read_sql("""
        SELECT DISTINCT ticker
        FROM companies
        WHERE ticker IS NOT NULL AND ticker != ''
        ORDER BY ticker
    """, conn)

    print(f"Found {len(tickers)} unique tickers")
    print("Downloading 10 years of daily prices (this will take ~30-45 minutes)...\n")

    import yfinance as yf

    ten_years_ago = datetime.now() - timedelta(days=7300)
    today = datetime.now()

    success_count = 0

    for idx, row in tickers.iterrows():
        ticker = row['ticker']

        print(f"[{idx+1}/{len(tickers)}] {ticker:6s}...", end=' ', flush=True)

        # Check if already downloaded
        existing = conn.execute(
            'SELECT COUNT(*) FROM daily_stock_prices WHERE ticker = ?',
            (ticker,)
        ).fetchone()[0]

        if existing > 0:
            print(f"⏭ Already cached ({existing} days)")
            continue

        try:
            # Download 10 years of data
            stock = yf.Ticker(ticker)
            hist = stock.history(start=ten_years_ago, end=today, interval='1d')

            if hist.empty:
                print("✗ No data")
                continue

            # Calculate daily change %
            hist['daily_change_pct'] = hist['Close'].pct_change() * 100

            # Prepare for database insertion
            hist_reset = hist.reset_index()
            hist_reset['ticker'] = ticker
            hist_reset['date'] = hist_reset['Date'].dt.strftime('%Y-%m-%d')

            # Insert into database
            for _, price_row in hist_reset.iterrows():
                conn.execute('''
                    INSERT OR IGNORE INTO daily_stock_prices
                    (ticker, date, open, high, low, close, volume, daily_change_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    ticker,
                    price_row['date'],
                    float(price_row['Open']) if pd.notna(price_row['Open']) else None,
                    float(price_row['High']) if pd.notna(price_row['High']) else None,
                    float(price_row['Low']) if pd.notna(price_row['Low']) else None,
                    float(price_row['Close']) if pd.notna(price_row['Close']) else None,
                    float(price_row['Volume']) if pd.notna(price_row['Volume']) else None,
                    float(price_row['daily_change_pct']) if pd.notna(price_row['daily_change_pct']) else None
                ))

            conn.commit()
            success_count += 1
            print(f"✓ {len(hist)} days")

        except Exception as e:
            print(f"✗ Error: {e}")

        time.sleep(0.2)  # Rate limiting

    conn.close()

    print(f"\n✅ Downloaded price history for {success_count}/{len(tickers)} tickers")

#Helper function, don't call it itself - it standardises data for fetch_historical_stock_prices_for_trials()
def get_stock_price_around_catalyst_from_cache(
    ticker: str,
    catalyst_date: str,
    days_before: int = 30,
    days_after: int = 120
) -> Optional[Dict]:
    """
    Get stock prices around catalyst from cached daily_stock_prices table
    Uses 120-day window for delayed announcements
    """
    conn = sqlite3.connect(DB_PATH)

    try:
        catalyst_date = pd.to_datetime(catalyst_date)
        start_date = catalyst_date - timedelta(days=days_before + 10)
        end_date = catalyst_date + timedelta(days=days_after + 10)

        # Query cached data
        query = f"""
            SELECT date, close
            FROM daily_stock_prices
            WHERE ticker = '{ticker}'
            AND date >= '{start_date.date()}'
            AND date <= '{end_date.date()}'
            ORDER BY date
        """

        hist = pd.read_sql(query, conn)
        conn.close()

        if hist.empty:
            return None

        hist['date'] = pd.to_datetime(hist['date'])
        hist = hist.set_index('date')

        def get_closest_price(target_date):
            """Get price for closest trading day to target"""
            target_date = pd.Timestamp(target_date)
            if target_date in hist.index:
                return hist.loc[target_date, 'close']
            future_dates = hist.index[hist.index >= target_date]
            if len(future_dates) > 0:
                return hist.loc[future_dates[0], 'close']
            return hist.iloc[-1]['close']

        # Get prices at key timepoints
        price_30d_before = get_closest_price(catalyst_date - timedelta(days=30))
        price_1d_before = get_closest_price(catalyst_date - timedelta(days=1))
        price_on_catalyst = get_closest_price(catalyst_date)
        price_1d_after = get_closest_price(catalyst_date + timedelta(days=1))
        price_7d_after = get_closest_price(catalyst_date + timedelta(days=7))
        price_30d_after = get_closest_price(catalyst_date + timedelta(days=30))
        price_90d_after = get_closest_price(catalyst_date + timedelta(days=90))
        price_120d_after = get_closest_price(catalyst_date + timedelta(days=120))

        # Calculate returns
        return_1d = ((price_1d_after - price_on_catalyst) / price_on_catalyst) if price_on_catalyst else None
        return_7d = ((price_7d_after - price_on_catalyst) / price_on_catalyst) if price_on_catalyst else None
        return_30d = ((price_30d_after - price_30d_before) / price_30d_before) if price_30d_before else None
        return_90d = ((price_90d_after - price_on_catalyst) / price_on_catalyst) if price_on_catalyst else None
        return_120d = ((price_120d_after - price_on_catalyst) / price_on_catalyst) if price_on_catalyst else None

        return {
            'ticker': ticker,
            'catalyst_date': str(catalyst_date.date()),
            'price_30d_before': float(price_30d_before) if pd.notna(price_30d_before) else None,
            'price_1d_before': float(price_1d_before) if pd.notna(price_1d_before) else None,
            'price_on_catalyst': float(price_on_catalyst) if pd.notna(price_on_catalyst) else None,
            'price_1d_after': float(price_1d_after) if pd.notna(price_1d_after) else None,
            'price_7d_after': float(price_7d_after) if pd.notna(price_7d_after) else None,
            'price_30d_after': float(price_30d_after) if pd.notna(price_30d_after) else None,
            'price_90d_after': float(price_90d_after) if pd.notna(price_90d_after) else None,
            'price_120d_after': float(price_120d_after) if pd.notna(price_120d_after) else None,
            'return_1d_pct': float(return_1d * 100) if return_1d else None,
            'return_7d_pct': float(return_7d * 100) if return_7d else None,
            'return_30d_pct': float(return_30d * 100) if return_30d else None,
            'return_90d_pct': float(return_90d * 100) if return_90d else None,
            'return_120d_pct': float(return_120d * 100) if return_120d else None,
        }

    except Exception as e:
        print(f"  ⚠ Error getting prices for {ticker}: {e}")
        return None

def fetch_historical_stock_prices_for_trials():
    """
    For all historical COMPLETED trials, fetch stock prices around completion date

    Uses tickers from tickers.csv (manually entered)
    """
    print("\n=== FETCHING HISTORICAL STOCK PRICES ===\n")

    conn = sqlite3.connect(DB_PATH)

    # Get all COMPLETED trials from last 10 years with tickers
    ten_years_ago = (datetime.now() - timedelta(days=3650)).date()
    today = datetime.now().date()  # ADDED: Don't include future dates

    query = f"""
        SELECT
            ct.nct_id,
            ct.cusip,
            c.ticker,
            c.issuer_name_clean,
            ct.drug_name,
            ct.phase,
            ct.primary_completion_date,
            ct.trial_status
        FROM clinical_trials ct
        JOIN companies c ON ct.cusip = c.cusip
        WHERE ct.trial_status = 'COMPLETED'
        AND ct.primary_completion_date >= '{ten_years_ago}'
        AND ct.primary_completion_date <= '{today}'  -- ADDED: Only past dates
        AND c.ticker IS NOT NULL
        AND c.ticker != ''
        AND ct.phase IN ('PHASE2', 'PHASE3', 'PHASE2|PHASE3')
        ORDER BY ct.primary_completion_date DESC
    """
    
    trials_df = pd.read_sql(query, conn)
    
    print(f"Found {len(trials_df)} completed Phase 2/3 trials with tickers (last 10 years)")
    
    if trials_df.empty:
        print("⚠ No trials to process")
        print("💡 Tip: Run import_tickers_from_csv() to load manually-entered tickers")
        conn.close()
        return
    
    # Create table for stock prices if not exists
    conn.execute('''
        CREATE TABLE IF NOT EXISTS trial_stock_prices (
            nct_id TEXT PRIMARY KEY,
            ticker TEXT,
            catalyst_date TEXT,
            price_30d_before REAL,
            price_1d_before REAL,
            price_on_catalyst REAL,
            price_1d_after REAL,
            price_7d_after REAL,
            price_30d_after REAL,
            price_90d_after REAL,
            price_120d_after REAL,
            return_1d_pct REAL,
            return_7d_pct REAL,
            return_30d_pct REAL,
            return_90d_pct REAL,
            return_120d_pct REAL,
            FOREIGN KEY (nct_id) REFERENCES clinical_trials(nct_id)
    )
    ''')
    conn.commit()
    
    prices_fetched = 0
    
    for idx, trial in trials_df.iterrows():
        ticker = trial['ticker']
        nct_id = trial['nct_id']
        completion_date = trial['primary_completion_date']
        drug_name = trial['drug_name'] if trial['drug_name'] else 'Unknown'
        
        print(f"[{idx+1}/{len(trials_df)}] {ticker:6s} - {drug_name[:30]:30s}...", end=' ', flush=True)
        
        # Normalize date if incomplete
        if len(completion_date) == 7:  # "YYYY-MM"
            completion_date = f"{completion_date}-01"
        elif len(completion_date) == 4:  # "YYYY"
            completion_date = f"{completion_date}-01-01"
        
        # Check if already exists
        existing = conn.execute(
            'SELECT nct_id FROM trial_stock_prices WHERE nct_id = ?', 
            (nct_id,)
        ).fetchone()
        
        if existing:
            print("⏭ Already cached")
            continue

        # CHANGED: Use cached prices instead of yfinance
        price_data = get_stock_price_around_catalyst_from_cache(ticker, completion_date)
        
        if price_data:
            return_str = f"{price_data['return_30d_pct']:+.1f}%" if price_data['return_30d_pct'] else "N/A"
            print(f"✓ {return_str:>8s} (30d)")
            
            # Insert into database
            conn.execute('''
            INSERT OR REPLACE INTO trial_stock_prices 
            (nct_id, ticker, catalyst_date, 
            price_30d_before, price_1d_before, price_on_catalyst, 
            price_1d_after, price_7d_after, price_30d_after, price_90d_after, price_120d_after,
            return_1d_pct, return_7d_pct, return_30d_pct, return_90d_pct, return_120d_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
            nct_id, price_data['ticker'], price_data['catalyst_date'],
            price_data['price_30d_before'], price_data['price_1d_before'], 
            price_data['price_on_catalyst'], price_data['price_1d_after'],
            price_data['price_7d_after'], price_data['price_30d_after'],
            price_data['price_90d_after'], price_data['price_120d_after'],
            price_data['return_1d_pct'], price_data['return_7d_pct'], 
            price_data['return_30d_pct'], price_data['return_90d_pct'],
            price_data['return_120d_pct']
    ))
            
            prices_fetched += 1
        else:
            print("✗ No data")
        
        # Commit every 10 trials
        if (idx + 1) % 10 == 0:
            conn.commit()
        
        time.sleep(0.3)  # Rate limiting for yfinance
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Fetched prices for {prices_fetched}/{len(trials_df)} trials")

#11.5 - Feeder function to help 12.
def get_peak_daily_move_in_announcement_window(ticker, completion_date,
                                                window_start=30, window_end=210):
    """
    Find the largest single-day % move in the 50-90 day window after trial completion

    This captures the announcement day when results are presented at conferences
    """
    conn = sqlite3.connect(DB_PATH)

    try:
        completion_date = pd.to_datetime(completion_date)
        search_start = completion_date + timedelta(days=window_start)
        search_end = completion_date + timedelta(days=window_end)

        # Get daily prices in announcement window
        query = f"""
            SELECT date, close, daily_change_pct
            FROM daily_stock_prices
            WHERE ticker = '{ticker}'
            AND date BETWEEN '{search_start.date()}' AND '{search_end.date()}'
            AND daily_change_pct IS NOT NULL
            ORDER BY date
        """

        prices = pd.read_sql(query, conn)
        conn.close()

        if prices.empty:
            return None

        # Find peak absolute daily move
        peak_idx = prices['daily_change_pct'].abs().idxmax()
        peak_daily_change = prices.loc[peak_idx, 'daily_change_pct']
        peak_date = prices.loc[peak_idx, 'date']
        peak_price = prices.loc[peak_idx, 'close']

        days_after_completion = (pd.to_datetime(peak_date) - completion_date).days

        return {
            'ticker': ticker,
            'completion_date': str(completion_date.date()),
            'peak_announcement_date': peak_date,
            'peak_daily_change_pct': float(peak_daily_change),
            'peak_price': float(peak_price),
            'days_after_completion': int(days_after_completion)
        }

    except Exception as e:
        print(f"  ⚠ Error for {ticker}: {e}")
        return None

#12:
#12:
def label_trial_outcomes_from_announcement_spike():
    """
    Label trial outcomes based on actual returns from entry to announcement
    
    Entry: 30 days before trial completion
    Exit: On the peak announcement day (within 30-210 days after completion)
    
    Returns actual % return instead of just spike direction
    """
    print("\n=== LABELING TRIALS FROM ACTUAL RETURNS (ENTRY TO ANNOUNCEMENT) ===\n")

    conn = sqlite3.connect(DB_PATH)

    # Add new columns if they don't exist
    try:
        conn.execute('ALTER TABLE trial_stock_prices ADD COLUMN entry_to_announcement_return_pct REAL')
        conn.execute('ALTER TABLE trial_stock_prices ADD COLUMN trial_outcome_by_return TEXT')
    except:
        pass  # Columns already exist

    # ========================================================================
    # NEW SECTION: ADD DISEASE CATEGORY COLUMNS TO clinical_trials IF MISSING
    # ========================================================================
    try:
        conn.execute('ALTER TABLE clinical_trials ADD COLUMN disease_category TEXT')
        conn.execute('ALTER TABLE clinical_trials ADD COLUMN phase3_success_rate REAL')
        conn.execute('ALTER TABLE clinical_trials ADD COLUMN phase2_success_rate REAL')
        print("✓ Added disease category columns to clinical_trials table\n")
    except:
        pass  # Columns already exist
    # ========================================================================
    # END NEW SECTION
    # ========================================================================

    # Get all trials that already have peak announcement data (from your existing step #12)
    trials = pd.read_sql("""
        SELECT
            nct_id,
            ticker,
            catalyst_date,
            price_30d_before,
            peak_announcement_date,
            peak_daily_change_pct,
            days_after_completion
        FROM trial_stock_prices
        WHERE price_30d_before IS NOT NULL
        AND peak_announcement_date IS NOT NULL
    """, conn)

    print(f"Processing {len(trials)} completed trials...\n")

    updated = 0

    for idx, trial in trials.iterrows():
        ticker = trial['ticker']
        entry_price = trial['price_30d_before']
        announcement_date = trial['peak_announcement_date']
        
        # Get the actual stock price on announcement day
        result = conn.execute("""
            SELECT close
            FROM daily_stock_prices
            WHERE ticker = ?
            AND date = ?
        """, (ticker, announcement_date)).fetchone()
        
        if not result or not result[0]:
            continue
            
        exit_price = result[0]
        
        # Calculate actual return from entry (30d before) to announcement day
        actual_return_pct = ((exit_price - entry_price) / entry_price) * 100
        
        # ============================================================
        # ADD THIS VALIDATION CHECK
        # ============================================================
        if abs(actual_return_pct) > 500:
            print(f"  ⚠ SUSPICIOUS: {ticker} on {announcement_date}: "
                  f"Entry=${entry_price:.2f}, Exit=${exit_price:.2f}, "
                  f"Return={actual_return_pct:+.1f}% - SKIPPING")
            continue


        # Label based on return thresholds (CHANGED TO 10% FROM 20%)
        if actual_return_pct > 5:  # Changed from 20
            outcome = 'success'
        elif actual_return_pct < -5:  # Changed from -20
            outcome = 'failure'
        else:
            outcome = 'neutral'
        
        # Update database
        conn.execute('''
            UPDATE trial_stock_prices
            SET entry_to_announcement_return_pct = ?,
                trial_outcome_by_return = ?,
                trial_outcome = ?
            WHERE nct_id = ?
        ''', (actual_return_pct, outcome, outcome, trial['nct_id']))

        updated += 1

        if updated % 100 == 0:
            days = trial['days_after_completion']
            print(f"  [{updated}/{len(trials)}] {ticker:6s}: {actual_return_pct:+6.1f}% over {days} days")
            conn.commit()

    conn.commit()

    # ========================================================================
    # NEW SECTION: POPULATE DISEASE CATEGORIES FOR ALL COMPLETED TRIALS
    # ========================================================================
    print(f"\n{'='*80}")
    print("POPULATING DISEASE CATEGORIES FOR COMPLETED TRIALS")
    print(f"{'='*80}\n")
    
    # Get all trials from clinical_trials that need disease categories
    trials_to_classify = pd.read_sql("""
        SELECT 
            ct.nct_id,
            ct.indication,
            ct.phase
        FROM clinical_trials ct
        WHERE ct.trial_status = 'COMPLETED'
        AND (ct.disease_category IS NULL OR ct.disease_category = '')
    """, conn)
    
    print(f"Found {len(trials_to_classify)} completed trials without disease categories")
    
    classified = 0
    
    for idx, row in trials_to_classify.iterrows():
        # Use your existing classify_disease_category function
        category, phase3_rate, phase2_rate = classify_disease_category(row['indication'])
        
        # Update the clinical_trials table
        conn.execute('''
            UPDATE clinical_trials
            SET disease_category = ?,
                phase3_success_rate = ?,
                phase2_success_rate = ?
            WHERE nct_id = ?
        ''', (category, phase3_rate, phase2_rate, row['nct_id']))
        
        classified += 1
        
        if classified % 100 == 0:
            print(f"  [{classified}/{len(trials_to_classify)}] Classified")
            conn.commit()
    
    conn.commit()
    
    print(f"\n✓ Classified {classified} completed trials by disease category")
    
    # Show distribution
    category_dist = pd.read_sql("""
        SELECT 
            disease_category,
            phase,
            COUNT(*) as count,
            ROUND(AVG(phase3_success_rate), 3) as avg_phase3_rate,
            ROUND(AVG(phase2_success_rate), 3) as avg_phase2_rate
        FROM clinical_trials
        WHERE trial_status = 'COMPLETED'
        AND disease_category IS NOT NULL
        GROUP BY disease_category, phase
        ORDER BY count DESC
        LIMIT 20
    """, conn)
    
    print(f"\n{'='*80}")
    print("DISEASE CATEGORY DISTRIBUTION (TOP 20)")
    print(f"{'='*80}\n")
    print(category_dist.to_string(index=False))
    # ========================================================================
    # END NEW SECTION
    # ========================================================================

    # Show summary of outcomes
    summary = pd.read_sql("""
        SELECT
            trial_outcome_by_return as outcome,
            COUNT(*) as count,
            ROUND(AVG(entry_to_announcement_return_pct), 1) as avg_return_pct,
            ROUND(MIN(entry_to_announcement_return_pct), 1) as min_return_pct,
            ROUND(MAX(entry_to_announcement_return_pct), 1) as max_return_pct
        FROM trial_stock_prices
        WHERE trial_outcome_by_return IS NOT NULL
        GROUP BY trial_outcome_by_return
    """, conn)

    conn.close()

    print(f"\n{'='*80}")
    print(f"LABELING COMPLETE")
    print(f"{'='*80}")
    print(f"\n✅ Labeled {updated} trials based on actual returns")
    print("\nOutcome Distribution:")
    print(summary.to_string(index=False))
    print(f"\n{'='*80}\n")

    return summary

#13 - generates bet history for each fund.
def generate_fund_bet_trackers():
    """
    For each fund, track all their positions that went into clinical trial completions
    
    Creates: /sec-edgar-filings/{cik}/{fund_name}/bet_tracker.csv
    
    Columns:
    - ticker, issuer, cusip
    - entry_date, entry_quarter, entry_weight_pct
    - peak_weight_pct (max concentration before trial)
    - pre_trial_weight_pct (concentration in quarter before trial)
    - trial_completion_date, drug_name, indication, phase
    - stock_outcome (success/neutral/failure based on price spike)
    - peak_daily_change_pct (the announcement day spike)
    - days_held_before_completion
    """
    print("\n=== GENERATING FUND BET TRACKERS ===\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    # Get all trials with outcomes
    trials = pd.read_sql("""
        SELECT 
            ct.cusip,
            c.ticker,
            c.issuer_name_clean as issuer,
            ct.nct_id,
            ct.drug_name,
            ct.indication,
            ct.phase,
            ct.primary_completion_date,
            tsp.peak_daily_change_pct,
            tsp.peak_announcement_date,
            CASE 
                WHEN tsp.peak_daily_change_pct > 10 THEN 'success'
                WHEN tsp.peak_daily_change_pct < -10 THEN 'failure'
                ELSE 'neutral'
            END as stock_outcome
        FROM clinical_trials ct
        JOIN companies c ON ct.cusip = c.cusip
        LEFT JOIN trial_stock_prices tsp ON ct.nct_id = tsp.nct_id
        WHERE ct.trial_status = 'COMPLETED'
        AND ct.primary_completion_date IS NOT NULL
        AND tsp.peak_daily_change_pct IS NOT NULL
    """, conn)
    
    # Normalize incomplete dates
    def normalize_date(date_str):
        if pd.isna(date_str):
            return None
        date_str = str(date_str).strip()
        if len(date_str) == 7:  # "YYYY-MM"
            return f"{date_str}-01"
        elif len(date_str) == 4:  # "YYYY"
            return f"{date_str}-01-01"
        return date_str
    
    trials['primary_completion_date'] = trials['primary_completion_date'].apply(normalize_date)
    trials['primary_completion_date'] = pd.to_datetime(trials['primary_completion_date'], errors='coerce')
    
    # Remove rows with invalid dates
    trials = trials.dropna(subset=['primary_completion_date'])
    
    print(f"Found {len(trials)} completed trials with stock outcomes\n")
    
    # Process each fund
    for fund_name, cik in FUNDS.items():
        fund_dir = base_path / cik
        csv_path = fund_dir / f"{fund_name}.csv"
        
        if not csv_path.exists():
            print(f"⚠ Skipping {fund_name}: CSV not found")
            continue
        
        print(f"Processing {fund_name}...", end=' ', flush=True)
        
        # Load fund holdings
        holdings = pd.read_csv(csv_path)
        holdings = holdings.dropna(subset=['cusip', 'report_date'])
        holdings['report_date'] = pd.to_datetime(holdings['report_date'], errors='coerce')
        holdings = holdings.dropna(subset=['report_date'])
        
        bets = []
        
        # For each trial, check if fund held it
        for _, trial in trials.iterrows():
            cusip = trial['cusip']
            completion_date = trial['primary_completion_date']
            
            # Get all holdings of this stock by this fund
            stock_holdings = holdings[holdings['cusip'] == cusip].copy()
            
            if stock_holdings.empty:
                continue
            
            stock_holdings = stock_holdings.sort_values('report_date')
            
            # Find entry point (first appearance)
            entry = stock_holdings.iloc[0]
            entry_date = entry['report_date']
            
            # They must have entered BEFORE trial completion
            if entry_date >= completion_date:
                continue
            
            # Find holdings before trial completion
            holdings_before = stock_holdings[stock_holdings['report_date'] <= completion_date]
            
            if holdings_before.empty:
                continue
            
            # Peak concentration before trial
            peak_weight = holdings_before['weight_pct'].max()
            
            # Concentration in last quarter before trial
            pre_trial = holdings_before.iloc[-1]
            pre_trial_weight = pre_trial['weight_pct']
            
            # Days held before completion
            days_held = (completion_date - entry_date).days
            
            bets.append({
                'ticker': trial['ticker'],
                'issuer': trial['issuer'],
                'cusip': cusip,
                'entry_date': entry_date.date(),
                'entry_quarter': entry['quarter'],
                'entry_weight_pct': entry['weight_pct'],
                'peak_weight_pct': peak_weight,
                'pre_trial_weight_pct': pre_trial_weight,
                'pre_trial_quarter': pre_trial['quarter'],
                'trial_completion_date': completion_date.date(),
                'drug_name': trial['drug_name'],
                'indication': trial['indication'],
                'phase': trial['phase'],
                'stock_outcome': trial['stock_outcome'],
                'peak_daily_change_pct': trial['peak_daily_change_pct'],
                'announcement_date': trial['peak_announcement_date'],
                'days_held_before_completion': days_held,
                'nct_id': trial['nct_id']
            })
        
        if not bets:
            print("✓ 0 bets")
            continue
        
        # Create DataFrame and save
        bets_df = pd.DataFrame(bets)
        bets_df = bets_df.sort_values('trial_completion_date', ascending=False)
        
        output_path = fund_dir / "bet_tracker.csv"
        bets_df.to_csv(output_path, index=False)
        
        # Calculate stats
        total_bets = len(bets_df)
        success_count = len(bets_df[bets_df['stock_outcome'] == 'success'])
        failure_count = len(bets_df[bets_df['stock_outcome'] == 'failure'])
        success_rate = (success_count / total_bets * 100) if total_bets > 0 else 0
        
        print(f"✓ {total_bets} bets ({success_rate:.1f}% success rate)")
    
    conn.close()
    
    # Generate summary across all funds
    print("\n=== FUND PERFORMANCE SUMMARY ===\n")
    
    summary = []
    for fund_name, cik in FUNDS.items():
        bet_tracker_path = base_path / cik / "bet_tracker.csv"
        
        if not bet_tracker_path.exists():
            continue
        
        bets = pd.read_csv(bet_tracker_path)
        
        if bets.empty:
            continue
        
        total = len(bets)
        success = len(bets[bets['stock_outcome'] == 'success'])
        failure = len(bets[bets['stock_outcome'] == 'failure'])
        neutral = len(bets[bets['stock_outcome'] == 'neutral'])
        success_rate = (success / total * 100) if total > 0 else 0
        avg_peak_weight = bets['peak_weight_pct'].mean()
        avg_spike = bets['peak_daily_change_pct'].mean()
        
        summary.append({
            'fund_name': fund_name,
            'total_bets': total,
            'success': success,
            'failure': failure,
            'neutral': neutral,
            'success_rate_%': round(success_rate, 1),
            'avg_peak_weight_%': round(avg_peak_weight, 2),
            'avg_announcement_spike_%': round(avg_spike, 1)
        })
    
    summary_df = pd.DataFrame(summary)
    summary_df = summary_df.sort_values('success_rate_%', ascending=False)
    
    summary_path = base_path / "fund_bet_tracker_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    
    print(f"\n{'Fund':<25} {'Bets':<6} {'Success':<8} {'Failure':<8} {'Rate':<8} {'Avg Weight':<12}")
    print("="*80)
    for _, row in summary_df.iterrows():
        print(f"{row['fund_name']:<25} {row['total_bets']:<6} "
              f"{row['success']:<8} {row['failure']:<8} "
              f"{row['success_rate_%']:>5.1f}%{'':<2} {row['avg_peak_weight_%']:>6.2f}%")
    
    print(f"\n✅ Summary saved to: {summary_path}")
    print(f"✅ Individual bet trackers saved to each fund's directory")


#14- Fund concentration index
def generate_high_conviction_bet_analysis():
    """
    Analyze fund performance by conviction level (position size bands)
    
    Creates: 
    - /sec-edgar-filings/{cik}/{fund_name}/high_conviction_bet_history.csv
    - /sec-edgar-filings/high_conviction_performance.json (all funds summary)
    
    Only includes positions >3% going into trial
    Shows success rate by position size bands
    SUCCESS RATE = (success + neutral) / total
    """
    print("\n=== GENERATING HIGH CONVICTION BET ANALYSIS ===\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    # Get all trials with outcomes
    trials = pd.read_sql("""
        SELECT 
            ct.cusip,
            c.ticker,
            c.issuer_name_clean as issuer,
            ct.nct_id,
            ct.drug_name,
            ct.indication,
            ct.phase,
            ct.primary_completion_date,
            tsp.entry_to_announcement_return_pct as actual_return_pct,
            tsp.trial_outcome_by_return as stock_outcome,
            tsp.price_30d_before as entry_price,
            tsp.peak_announcement_date
        FROM clinical_trials ct
        JOIN companies c ON ct.cusip = c.cusip
        LEFT JOIN trial_stock_prices tsp ON ct.nct_id = tsp.nct_id
        WHERE ct.trial_status = 'COMPLETED'
        AND ct.primary_completion_date IS NOT NULL
        AND tsp.trial_outcome_by_return IS NOT NULL
        AND c.is_biotech = 1
    """, conn)

    """
        SELECT 
            ct.cusip,
            c.ticker,
            c.issuer_name_clean as issuer,
            ct.nct_id,
            ct.drug_name,
            ct.indication,
            ct.phase,
            ct.primary_completion_date,
            tsp.peak_daily_change_pct,
            tsp.peak_announcement_date,
            CASE 
                WHEN tsp.peak_daily_change_pct > 10 THEN 'success'
                WHEN tsp.peak_daily_change_pct < -10 THEN 'failure'
                ELSE 'neutral'
            END as stock_outcome
        FROM clinical_trials ct
        JOIN companies c ON ct.cusip = c.cusip
        LEFT JOIN trial_stock_prices tsp ON ct.nct_id = tsp.nct_id
        WHERE ct.trial_status = 'COMPLETED'
        AND ct.primary_completion_date IS NOT NULL
        AND tsp.peak_daily_change_pct IS NOT NULL
    """
    
    # Normalize incomplete dates
    def normalize_date(date_str):
        if pd.isna(date_str):
            return None
        date_str = str(date_str).strip()
        if len(date_str) == 7:  # "YYYY-MM"
            return f"{date_str}-01"
        elif len(date_str) == 4:  # "YYYY"
            return f"{date_str}-01-01"
        return date_str
    
    trials['primary_completion_date'] = trials['primary_completion_date'].apply(normalize_date)
    trials['primary_completion_date'] = pd.to_datetime(trials['primary_completion_date'], errors='coerce')
    trials = trials.dropna(subset=['primary_completion_date'])

    # Right after loading trials, add:
    today = datetime.now().date()
    trials = trials[trials['primary_completion_date'].dt.date <= today]
    
    print(f"Found {len(trials)} completed trials with stock outcomes\n")
    
    # Position size bands
    bands = [
        (1.5, 2, "1.5-2%"),
        (2,3,"2-3%"),
        (3, 4, "3-4%"),
        (4, 5, "4-5%"),
        (5, 6, "5-6%"),
        (6, 7, "6-7%"),
        (7, 8, "7-8%"),
        (8, 9, "8-9%"),
        (9, 10, "9-10%"),
        (10, 15, "10-15%"),
        (15, 100, ">15%")
    ]
    
    # Master JSON for all funds
    performance_json = {}
    
    # Process each fund
    for fund_name, cik in FUNDS.items():
        fund_dir = base_path / cik
        csv_path = fund_dir / f"{fund_name}.csv"
        
        if not csv_path.exists():
            continue
        
        print(f"Processing {fund_name}...", end=' ', flush=True)
        
        # Load fund holdings
        holdings = pd.read_csv(csv_path)
        holdings = holdings.dropna(subset=['cusip', 'report_date'])
        holdings['report_date'] = pd.to_datetime(holdings['report_date'], errors='coerce')
        holdings = holdings.dropna(subset=['report_date'])
        
        high_conviction_bets = []
        
        # For each trial, check if fund held it with >3% conviction
        for _, trial in trials.iterrows():
            cusip = trial['cusip']
            completion_date = trial['primary_completion_date']
            
            # Get all holdings of this stock by this fund
            stock_holdings = holdings[holdings['cusip'] == cusip].copy()
            
            if stock_holdings.empty:
                continue
            
            stock_holdings = stock_holdings.sort_values('report_date')
            
            # Find entry point
            entry = stock_holdings.iloc[0]
            entry_date = entry['report_date']
            
            # Must have entered BEFORE trial completion
            if entry_date >= completion_date:
                continue
            
            # Find holdings before trial completion
            holdings_before = stock_holdings[stock_holdings['report_date'] <= completion_date]
            
            if holdings_before.empty:
                continue
            
            # Pre-trial weight (last quarter before trial)
            pre_trial = holdings_before.iloc[-1]
            pre_trial_weight = pre_trial['weight_pct']
            
            # FILTER: Only >1.5% positions
            if pre_trial_weight < 1.5:
                continue
            
            # Find exit date (when position dropped to <1%)
            holdings_after = stock_holdings[stock_holdings['report_date'] > completion_date]
            exit_date = None
            exit_quarter = None
            
            for _, row in holdings_after.iterrows():
                if row['weight_pct'] < 0.9:
                    exit_date = row['report_date']
                    exit_quarter = row['quarter']
                    break
            
            # If never dropped below 1%, use last available date
            if exit_date is None and not stock_holdings.empty:
                last_holding = stock_holdings.iloc[-1]
                exit_date = last_holding['report_date']
                exit_quarter = last_holding['quarter']
            
            # Determine position band
            position_band = None
            for low, high, label in bands:
                if low <= pre_trial_weight < high:
                    position_band = label
                    break
            
            peak_weight = holdings_before['weight_pct'].max()
            days_held = (completion_date - entry_date).days
            
            high_conviction_bets.append({
                'ticker': trial['ticker'],
                'issuer': trial['issuer'],
                'cusip': cusip,
                'entry_date': entry_date.date(),
                'entry_quarter': entry['quarter'],
                'entry_weight_pct': entry['weight_pct'],
                'peak_weight_pct': peak_weight,
                'pre_trial_weight_pct': pre_trial_weight,
                'position_band': position_band,
                'pre_trial_quarter': pre_trial['quarter'],
                'trial_completion_date': completion_date.date(),
                'exit_date': exit_date.date() if exit_date else None,
                'exit_quarter': exit_quarter,
                'drug_name': trial['drug_name'],
                'indication': trial['indication'],
                'phase': trial['phase'],
                'stock_outcome': trial['stock_outcome'],
                #'peak_daily_change_pct': trial['peak_daily_change_pct'],
                'actual_return_pct': trial['actual_return_pct'],  # ← NEW: actual % return
                'entry_price': trial['entry_price'],               # ← NEW: entry price
                'announcement_date': trial['peak_announcement_date'],
                'days_held_before_completion': days_held,
                'nct_id': trial['nct_id']
            })
        #DEDUPLICATION CHECK BELOW TO END DEDUPLICATION.
        if not high_conviction_bets:
            print("✓ 0 high conviction bets")
            continue
        
        # Create DataFrame and save
        bets_df = pd.DataFrame(high_conviction_bets)
        bets_df = bets_df.sort_values('trial_completion_date', ascending=False)
        
        # ===== DEDUPLICATION (BEFORE SAVING CSV) =====
        # Diagnostic first
        duplicates_check = bets_df.groupby(['cusip', 'entry_date']).size()
        if (duplicates_check > 1).any():
            print(f" [{len(bets_df)} trials → ", end='')
    
        # Deduplicate: Keep only first trial per position
        bets_df = bets_df.groupby(['cusip', 'entry_date'], as_index=False).first()

        if (duplicates_check > 1).any():
            print(f"{len(bets_df)} positions]", end=' ')
        # ===== END DEDUPLICATION ===== 


        output_path = fund_dir / "high_conviction_bet_history.csv"
        bets_df.to_csv(output_path, index=False)
        
        # Calculate performance by position band for JSON
        band_stats = {}
        for low, high, label in bands:
            band_bets = bets_df[(bets_df['pre_trial_weight_pct'] >= low) & 
                                (bets_df['pre_trial_weight_pct'] < high)]
            
            if band_bets.empty:
                continue
            
            total = len(band_bets)
            success = len(band_bets[band_bets['stock_outcome'] == 'success'])
            failure = len(band_bets[band_bets['stock_outcome'] == 'failure'])
            neutral = len(band_bets[band_bets['stock_outcome'] == 'neutral'])
            #SUCCESS = (NEUTRAL + SUCCES)/N -> below
            #success_rate = ((success + neutral) / total * 100)if total > 0 else 0
            #SUCCESS = SUCCESS/N
            success_rate = (success / total * 100) if total > 0 else 0
            
            band_stats[label] = {
                'total_bets': int(total),
                'success': int(success),
                'failure': int(failure),
                'neutral': int(neutral),
                'success_rate_%': round(success_rate, 1),
                #'avg_spike_%': round(band_bets['peak_daily_change_pct'].mean(), 1),
                'avg_return_%': round(band_bets['actual_return_pct'].mean(), 1)
            }
        
        # Overall stats for this fund
        total_bets = len(bets_df)
        overall_success = len(bets_df[bets_df['stock_outcome'] == 'success'])
        overall_neutral = len(bets_df[bets_df['stock_outcome'] == 'neutral'])
        # CHANGED: Overall success rate now includes neutral outcomes
        overall_rate = ((overall_success + overall_neutral) / total_bets * 100) if total_bets > 0 else 0
        
        performance_json[fund_name] = {
            'total_high_conviction_bets': int(total_bets),
            'overall_success_rate_%': round(overall_rate, 1),
            'by_position_band': band_stats
        }
        
        print(f"✓ {total_bets} bets ({overall_rate:.1f}% success)")
    
    conn.close()
    
    # Save master JSON
    json_path = base_path / "high_conviction_performance.json"
    with open(json_path, 'w') as f:
        json.dump(performance_json, f, indent=2)
    
    print(f"\n✅ JSON summary saved to: {json_path}")
    print(f"✅ Individual CSV histories saved to each fund's directory")


#14.5 Helper Function - Classify Disease Category
def classify_disease_category(indication: str) -> tuple:
    """
    Classify indication into disease category and return success rates
    
    Uses comprehensive keyword matching with fallback to broad categories.
    """
    if not indication or str(indication).strip() == '' or indication == 'None':
        avg_phase3 = sum(PHASE3_SUCCESS_RATES.values()) / len(PHASE3_SUCCESS_RATES)
        avg_phase2 = sum(PHASE2_SUCCESS_RATES.values()) / len(PHASE2_SUCCESS_RATES)
        return ('unknown', avg_phase3, avg_phase2)
    
    indication_lower = str(indication).lower()
    
    # Sort keywords by length (longest first) to match specific terms before general
    sorted_keywords = sorted(PHASE3_SUCCESS_RATES.keys(), key=len, reverse=True)
    
    for keyword in sorted_keywords:
        if keyword in indication_lower:
            phase2_rate = PHASE2_SUCCESS_RATES.get(keyword)
            if phase2_rate is None:
                phase2_rate = sum(PHASE2_SUCCESS_RATES.values()) / len(PHASE2_SUCCESS_RATES)
            
            phase3_rate = PHASE3_SUCCESS_RATES[keyword]
            return (keyword, phase3_rate, phase2_rate)
    
    # FALLBACK: Broad category matching using word stems
    # This catches cases where specific terms aren't in the dictionary
    
    # Check for cancer-related
    if any(word in indication_lower for word in ['malign', 'neoplasm', 'metasta', 'stage', 'advanced', 'recurrent']):
        return ('oncology', 0.475, 0.29)
    
    # Check for genetic/rare
    if any(word in indication_lower for word in ['genetic', 'congenital', 'hereditary', 'familial', 'syndrome']):
        return ('rare disease', 0.70, 0.425)
    
    # Check for immune-related
    if any(word in indication_lower for word in ['immune', 'inflammatory']):
        return ('autoimmune', 0.60, 0.325)
    
    # Check for metabolic
    if any(word in indication_lower for word in ['metabol', 'enzyme', 'deficiency']):
        return ('metabolic', 0.60, 0.425)
    
    # Default to average
    avg_phase3 = sum(PHASE3_SUCCESS_RATES.values()) / len(PHASE3_SUCCESS_RATES)
    avg_phase2 = sum(PHASE2_SUCCESS_RATES.values()) / len(PHASE2_SUCCESS_RATES)
    return ('unknown', avg_phase3, avg_phase2)

#15 - Scrape PFUDA dates from Fdatracker.com
def harvest_pdufa_dates():
    """Get PDUFA dates from FDA Tracker calendar"""
    print("\n=== HARVESTING PDUFA DATES ===\n")
    
    all_events = []
    current_year = datetime.now().year
    
    for year in [current_year, current_year + 1]:
        try:
            response = requests.get(PDUFA_CALENDAR_URL.format(year=year), timeout=30)
            response.raise_for_status()
            data = response.json()
            
            for event in data.get('items', []):
                summary = event.get('summary', '')
                description = event.get('description', '')
                pdufa_date = event.get('start', {}).get('date')
                
                # Extract ticker (first word)
                ticker_match = re.match(r'^([A-Z]{2,5})\s', summary)
                ticker = ticker_match.group(1) if ticker_match else None
                
                # Extract drug name (after ticker, before " - ")
                drug_match = re.match(r'^[A-Z]{2,5}\s+(.+?)(?:\s+-\s+|$)', summary)
                drug_name = drug_match.group(1).strip() if drug_match else None
                
                if ticker and pdufa_date:
                    all_events.append({
                        'ticker': ticker,
                        'catalyst_date': pdufa_date,
                        'drug_name': drug_name,
                        'indication': description if description else None,
                        'catalyst_type': 'PDUFA',
                        'source': 'fdatracker'
                    })
            
            print(f"✓ {year}: {len(data.get('items', []))} events")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"✗ {year}: {e}")
    
    df = pd.DataFrame(all_events)
    if not df.empty:
        df['catalyst_date'] = pd.to_datetime(df['catalyst_date'])
        df = df.sort_values('catalyst_date')
        print(f"\n✅ Found {len(df)} PDUFA dates\n")
    
    return df


#16. Harvest upcoming ClinicalTrial.gov clinical trials in next 2 years. 730 days.
def harvest_upcoming_clinical_trials():
    """
    Query ClinicalTrials.gov for ACTIVE Phase 2/3 trials with future completion dates
    Uses existing query_clinicaltrials_for_company() function
    """
    print("\n=== HARVESTING UPCOMING CLINICAL TRIALS ===\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    # Add columns if needed
    try:
        conn.execute('ALTER TABLE clinical_trials ADD COLUMN is_upcoming INTEGER DEFAULT 0')
        conn.execute('ALTER TABLE clinical_trials ADD COLUMN disease_category TEXT')
        conn.execute('ALTER TABLE clinical_trials ADD COLUMN phase3_success_rate REAL')
        conn.execute('ALTER TABLE clinical_trials ADD COLUMN phase2_success_rate REAL')
    except:
        pass
    conn.commit()
    
    companies = pd.read_sql("""
        SELECT cusip, ticker, issuer_name_clean 
        FROM companies 
        WHERE ticker IS NOT NULL
        AND is_biotech = 1
        ORDER BY ticker
    """, conn)
    
    today = datetime.now().date()
    future_cutoff = today + timedelta(days=730)
    
    total_found = 0
    all_trials_list = []
    
    for idx, row in companies.iterrows():
        ticker = row['ticker']
        company = row['issuer_name_clean']
        cusip = row['cusip']
        
        print(f"[{idx+1}/{len(companies)}] {ticker:6s} - {company[:35]:35s}...", end=' ', flush=True)
        
        # Use existing function!
        trials = query_clinicaltrials_for_company(
            company, 
            phases_to_keep=['PHASE2', 'PHASE3', 'PHASE2|PHASE3']
        )
        
        upcoming_count = 0
        
        for trial in trials:
            # Only ACTIVE trials
            if trial['status'] not in ['RECRUITING', 'ACTIVE_NOT_RECRUITING', 'ENROLLING_BY_INVITATION']:
                continue
            
            # Get completion date
            completion_date = trial.get('primary_completion_date')
            if not completion_date:
                continue
            
            # Normalize date
            if len(completion_date) == 7:
                completion_date = f"{completion_date}-01"
            elif len(completion_date) == 4:
                completion_date = f"{completion_date}-01-01"
            
            try:
                completion_dt = datetime.strptime(completion_date, '%Y-%m-%d').date()
            except:
                continue
            
            # Filter: Must complete in next 2 years
            if not (today <= completion_dt <= future_cutoff):
                continue
            
            # Classify disease category
            category, phase3_rate, phase2_rate = classify_disease_category(trial['indication'])
            
            # Store in database
            conn.execute('''
                INSERT OR REPLACE INTO clinical_trials 
                (nct_id, cusip, drug_name, indication, phase, sponsor_name, trial_status,
                 is_lead_sponsor, primary_completion_date, last_updated, 
                 is_upcoming, disease_category, phase3_success_rate, phase2_success_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trial['nct_id'], cusip, trial['drug_name'], trial['indication'],
                trial['phase'], trial['sponsor'], trial['status'], 1,
                completion_date, today, 1, category, phase3_rate, phase2_rate
            ))
            
            # Collect for CSV
            all_trials_list.append({
                'ticker': ticker,
                'nct_id': trial['nct_id'],
                'drug_name': trial['drug_name'],
                'indication': trial['indication'],
                'disease_category': category,
                'phase': trial['phase'],
                'trial_status': trial['status'],
                'catalyst_date': completion_date,
                'catalyst_type': f"{trial['phase']}_completion",
                'phase3_success_rate': phase3_rate,
                'phase2_success_rate': phase2_rate,
                'source': 'clinicaltrials.gov'
            })
            
            upcoming_count += 1
        
        total_found += upcoming_count
        print(f"✓ {upcoming_count} upcoming")
        
        if (idx + 1) % 10 == 0:
            conn.commit()
        
        time.sleep(0.3)
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Found {total_found} upcoming Phase 2/3 trials")
    
    # Save CSV
    if all_trials_list:
        trials_df = pd.DataFrame(all_trials_list)
        trials_df['catalyst_date'] = pd.to_datetime(trials_df['catalyst_date'])
        trials_df = trials_df.sort_values('catalyst_date')
        
        output_date = datetime.now().strftime('%Y%m%d')
        output_path = base_path / f"upcoming_trials_{output_date}.csv"
        trials_df.to_csv(output_path, index=False)
        print(f"📁 Saved: {output_path}")
    
    # Re-classify all upcoming trials to fix "unknown" categories
    print("\n=== RE-CLASSIFYING DISEASE CATEGORIES ===\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    trials = pd.read_sql("""
        SELECT nct_id, indication
        FROM clinical_trials
        WHERE is_upcoming = 1
    """, conn)
    
    print(f"Re-classifying {len(trials)} upcoming trials...")
    
    for idx, row in trials.iterrows():
        category, phase3_rate, phase2_rate = classify_disease_category(row['indication'])
        
        conn.execute('''
            UPDATE clinical_trials
            SET disease_category = ?,
                phase3_success_rate = ?,
                phase2_success_rate = ?
            WHERE nct_id = ?
        ''', (category, phase3_rate, phase2_rate, row['nct_id']))
        
        if (idx + 1) % 100 == 0:
            print(f"  [{idx+1}/{len(trials)}]")
            conn.commit()
    
    conn.commit()
    
    # Show results
    summary = pd.read_sql("""
        SELECT disease_category, COUNT(*) as count
        FROM clinical_trials
        WHERE is_upcoming = 1
        GROUP BY disease_category
        ORDER BY count DESC
    """, conn)
    
    conn.close()
    
    print(f"\n✅ Re-classified {len(trials)} trials")
    print("\nDisease Category Distribution:")
    print(summary)
    # ===== END ADDITION =====

    return total_found


#17. Combines everything + matches to funds
def generate_catalyst_calendar():
    """
    Combine PDUFA dates + upcoming trials + match to fund holdings
    
    Output: catalyst_calendar_YYYYMMDD.csv
    """
    print("\n=== GENERATING CATALYST CALENDAR ===\n")
    
    # Get PDUFA dates
    pdufa_df = harvest_pdufa_dates()
    
    # Get upcoming trials from database
    conn = sqlite3.connect(DB_PATH)
    trials_df = pd.read_sql("""
        SELECT 
            c.ticker,
            ct.nct_id,
            ct.drug_name,
            ct.indication,
            ct.disease_category,
            ct.phase,
            ct.trial_status,
            ct.primary_completion_date as catalyst_date,
            ct.phase || '_completion' as catalyst_type,
            ct.phase3_success_rate,
            ct.phase2_success_rate,
            'clinicaltrials.gov' as source
        FROM clinical_trials ct
        JOIN companies c ON ct.cusip = c.cusip
        WHERE ct.is_upcoming = 1
        AND ct.primary_completion_date IS NOT NULL
    """, conn)
    
    # Add disease categories to PDUFA dates
    if not pdufa_df.empty:
        pdufa_df[['disease_category', 'phase3_success_rate', 'phase2_success_rate']] = pdufa_df['indication'].apply(
            lambda x: pd.Series(classify_disease_category(x))
        )
    
    # Combine
    if not pdufa_df.empty and not trials_df.empty:
        all_catalysts = pd.concat([pdufa_df, trials_df], ignore_index=True)
    elif not pdufa_df.empty:
        all_catalysts = pdufa_df
    elif not trials_df.empty:
        all_catalysts = trials_df
    else:
        print("⚠ No catalysts found")
        conn.close()
        return
    
    # Get latest fund holdings
    latest_quarter = pd.read_sql("SELECT MAX(quarter) as q FROM fund_holdings", conn).iloc[0]['q']
    
    holdings = pd.read_sql(f"""
        SELECT 
            fh.fund_name,
            c.ticker,
            fh.position_pct,
            fh.shares,
            fh.value
        FROM fund_holdings fh
        JOIN companies c ON fh.cusip = c.cusip
        WHERE fh.quarter = '{latest_quarter}'
        AND fh.position_pct >= 2.0
    """, conn)
    
    conn.close()
    
    # Match to holdings
    matched = all_catalysts.merge(holdings, on='ticker', how='left')
    matched['catalyst_date'] = pd.to_datetime(matched['catalyst_date'])
    matched['days_until'] = (matched['catalyst_date'] - pd.Timestamp.now()).dt.days
    matched = matched.sort_values(['days_until', 'ticker'])
    
    # Save
    output_date = datetime.now().strftime('%Y%m%d')
    output_path = base_path / f"catalyst_calendar_{output_date}.csv"
    matched.to_csv(output_path, index=False)
    
    # Save fund-only subset
    with_funds = matched[matched['fund_name'].notna()].copy()
    if not with_funds.empty:
        fund_output = base_path / f"catalyst_calendar_funds_{output_date}.csv"
        with_funds.to_csv(fund_output, index=False)
        print(f"📁 Saved (funds): {fund_output}")
    
    print(f"📁 Saved (all): {output_path}")
    
    # Print summary
    print(f"\n{'='*80}")
    print("CATALYST CALENDAR SUMMARY")
    print(f"{'='*80}")
    print(f"Total catalysts: {len(matched)}")
    print(f"PDUFA dates: {len(matched[matched['catalyst_type'] == 'PDUFA'])}")
    print(f"Phase 3 completions: {len(matched[matched['catalyst_type'] == 'PHASE3_completion'])}")
    print(f"Phase 2 completions: {len(matched[matched['catalyst_type'] == 'PHASE2_completion'])}")
    print(f"With fund exposure (≥2%): {with_funds['ticker'].nunique() if not with_funds.empty else 0}")
    
    # Next 90 days
    next_90 = matched[matched['days_until'] <= 90].copy()
    if not next_90.empty:
        print(f"\n{'='*80}")
        print(f"NEXT 90 DAYS ({len(next_90)} catalysts)")
        print(f"{'='*80}")
        
        for _, row in next_90.head(15).iterrows():
            funds = f"[{row['fund_name']}]" if pd.notna(row['fund_name']) else ""
            success_rate = row.get('phase3_success_rate', 0.5) * 100 if row['catalyst_type'] != 'PDUFA' else 'N/A'
            success_str = f"{success_rate:.0f}%" if success_rate != 'N/A' else 'N/A'
            
            print(f"{row['catalyst_date'].strftime('%Y-%m-%d')} ({row['days_until']:3d}d) "
                  f"{row['ticker']:6s} - {row['catalyst_type']:20s} "
                  f"| {str(row['drug_name'])[:25]:25s} | P(success): {success_str:>4s} {funds}")
    
    print(f"{'='*80}\n")
    
    return matched

#17. Final STEP. Bayes calculator step. Bayesian Analysis of Upcoming Catalysts -
def generate_bayesian_catalyst_analysis():
    """
    Generate Bayesian analysis for upcoming catalysts based on current fund holdings
    
    Uses CONVICTION-WEIGHTED Bayesian updating:
    - Conviction = position_pct / 10 (10% position = 1.0x weight)
    - Credibility = track record quality (penalizes <3 bets)
    - Signal weight = conviction × credibility × 100
    
    For each upcoming catalyst:
    1. Get disease category base rate
    2. Find all funds currently holding ≥3%
    3. Look up their historical success rate at that position band
    4. Update probability using conviction-weighted signals
    
    Output: Bayes_Score_YYYYMMDD.json
    """
    
    print("\n=== GENERATING BAYESIAN CATALYST ANALYSIS ===\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    # Load high conviction performance data
    json_path = base_path / "high_conviction_performance.json"
    if not json_path.exists():
        print("⚠ high_conviction_performance.json not found. Run generate_high_conviction_bet_analysis() first.")
        conn.close()
        return
    
    with open(json_path, 'r') as f:
        fund_performance = json.load(f)
    
    # Get upcoming catalysts from database
    upcoming = pd.read_sql("""
        SELECT 
            c.ticker,
            c.cusip,
            c.issuer_name_clean as company,
            ct.drug_name,
            ct.indication,
            ct.disease_category,
            ct.phase,
            ct.primary_completion_date as catalyst_date,
            ct.phase || '_completion' as catalyst_type,
            ct.phase3_success_rate as base_rate,
            ct.phase2_success_rate as base_rate_phase2
        FROM clinical_trials ct
        JOIN companies c ON ct.cusip = c.cusip
        WHERE ct.is_upcoming = 1
        AND ct.primary_completion_date IS NOT NULL
        AND c.is_biotech = 1
    """, conn)
    
    conn.close()

    # Load ALL fund holdings from individual CSV files
    print("Loading fund holdings from CSV files...")
    all_holdings = []
    
    for fund_name, cik in FUNDS.items():
        fund_csv = base_path / cik / f"{fund_name}.csv"
        
        if not fund_csv.exists():
            continue
        
        try:
            df = pd.read_csv(fund_csv)
            df = df.dropna(subset=['cusip', 'quarter', 'weight_pct'])
            
            # Get latest quarter only
            latest_quarter = df['quarter'].max()
            latest_holdings = df[df['quarter'] == latest_quarter].copy()
            
            # Filter for ≥3% positions
            latest_holdings = latest_holdings[latest_holdings['weight_pct'] >= 3.0]
            
            if not latest_holdings.empty:
                latest_holdings['fund_name'] = fund_name
                all_holdings.append(latest_holdings[['fund_name', 'cusip', 'weight_pct']])
        
        except Exception as e:
            print(f"  ⚠ Error reading {fund_name}: {e}")
            continue
    
    if not all_holdings:
        print("⚠ No fund holdings found")
        return
    
    holdings_df = pd.concat(all_holdings, ignore_index=True)
    print(f"✓ Loaded {len(holdings_df)} high-conviction positions (≥3%) from {len(all_holdings)} funds\n")
    
    # Position bands (for matching)
    bands = [
        (1.5, 2, "1.5-2%"),
        (2,3,"2-3%"),
        (3, 4, "3-4%"),
        (4, 5, "4-5%"),
        (5, 6, "5-6%"),
        (6, 7, "6-7%"),
        (7, 8, "7-8%"),
        (8, 9, "8-9%"),
        (9, 10, "9-10%"),
        (10, 15, "10-15%"),
        (15, 100, ">15%")
    ]
    
    def find_position_band(position_pct):
        """Find which band a position falls into"""
        for low, high, label in bands:
            if low <= position_pct < high:
                return label
        return None
    
    def get_nearest_band_data(fund_name, target_band_label, fund_perf_data):
        """
        Find nearest band with data, but don't go below 3-4%
        
        Returns: (success_rate, num_bets) or (None, None)
        """
        if fund_name not in fund_perf_data:
            return None, None
        
        band_data = fund_perf_data[fund_name].get('by_position_band', {})
        
        # Try exact match first
        if target_band_label in band_data:
            return (
                band_data[target_band_label]['success_rate_%'] / 100,
                band_data[target_band_label]['total_bets']
            )
        
        # Find target band index
        target_idx = None
        for idx, (low, high, label) in enumerate(bands):
            if label == target_band_label:
                target_idx = idx
                break
        
        if target_idx is None:
            return None, None
        
        # Search nearby bands (±1, ±2, etc.) but don't go below 3-4%
        for distance in range(1, len(bands)):
            # Try higher band
            if target_idx + distance < len(bands):
                higher_label = bands[target_idx + distance][2]
                if higher_label in band_data:
                    return (
                        band_data[higher_label]['success_rate_%'] / 100,
                        band_data[higher_label]['total_bets']
                    )
            
            # Try lower band (but not below 3-4%)
            if target_idx - distance >= 0:  # Index 0 is 3-4%
                lower_label = bands[target_idx - distance][2]
                if lower_label in band_data:
                    return (
                        band_data[lower_label]['success_rate_%'] / 100,
                        band_data[lower_label]['total_bets']
                    )
        
        return None, None
    
    # Generate analysis for each catalyst
    results = {}
    
    for idx, catalyst in upcoming.iterrows():
        ticker = catalyst['ticker']
        cusip = catalyst['cusip']
        
        print(f"[{idx+1}/{len(upcoming)}] {ticker:6s} - {str(catalyst['drug_name'])[:30]:30s}...", end=' ')
        
        # Get funds holding this stock
        stock_holdings = holdings_df[holdings_df['cusip'] == cusip].copy()
        
        if stock_holdings.empty:
            print("✗ No fund holdings ≥3%")
            continue
        
        # Sort by position size descending (biggest holders first)
        stock_holdings = stock_holdings.sort_values('weight_pct', ascending=False)
        
        # Base rate
        base_rate = catalyst['base_rate']
        if pd.isna(base_rate) or base_rate == 0:
            base_rate = 0.50  # Fallback
        
        # === CONVICTION-WEIGHTED BAYESIAN UPDATE ===
        fund_signals = []
        prior_weight = 100  # Base rate weight (represents historical disease category data)
        weighted_sum = base_rate * prior_weight
        total_weight = prior_weight
        
        for _, holding in stock_holdings.iterrows():
            fund_name = holding['fund_name']
            position_pct = holding['weight_pct']
            
            # Find position band
            band_label = find_position_band(position_pct)
            if not band_label:
                continue
            
            # Get historical performance
            success_rate, num_bets = get_nearest_band_data(fund_name, band_label, fund_performance)
            
            if success_rate is None or num_bets is None or num_bets == 0:
                continue
            
            # 1. Conviction: How much capital at risk? (10% position = 1.0x weight)
            conviction = position_pct / 10.0
            
            # 2. Credibility: Track record quality (penalize small samples)
            if num_bets < 3:
                credibility = 0.3  # Low credibility for <3 bets
            elif num_bets < 10:
                credibility = (num_bets / 10) ** 0.5  # sqrt scaling for 3-10 bets
            else:
                credibility = 1.0  # Full credibility for 10+ bets
            
            # 3. Combined signal strength
            signal_weight = conviction * credibility * 100
            
            # 4. Update posterior
            weighted_sum += success_rate * signal_weight
            total_weight += signal_weight
            current_posterior = weighted_sum / total_weight
            
            fund_signals.append({
                'fund_name': fund_name,
                'position_pct': round(position_pct, 2),
                'position_band': band_label,
                'historical_success_rate': round(success_rate, 3),
                'historical_bets_in_band': int(num_bets),
                'conviction_weight': round(conviction, 2),
                'credibility_score': round(credibility, 2),
                'signal_weight': round(signal_weight, 1),
                'posterior_after_this_fund': round(current_posterior, 3)
            })
        
        if not fund_signals:
            print("✗ No valid fund signals")
            continue
        
        # Final posterior
        final_posterior = current_posterior
        
        # Generate interpretation
        diff = final_posterior - base_rate
        if abs(diff) < 0.02:
            interpretation = "Consistent with base rate"
        elif diff > 0.10:
            interpretation = f"Significantly above base rate (+{diff*100:.1f}pp) - strong fund confidence"
        elif diff > 0.05:
            interpretation = f"Moderately above base rate (+{diff*100:.1f}pp)"
        elif diff > 0:
            interpretation = f"Slightly above base rate (+{diff*100:.1f}pp)"
        elif diff < -0.10:
            interpretation = f"Significantly below base rate ({diff*100:.1f}pp) - weak fund confidence"
        elif diff < -0.05:
            interpretation = f"Moderately below base rate ({diff*100:.1f}pp)"
        else:
            interpretation = f"Slightly below base rate ({diff*100:.1f}pp)"
        
        # Store result
        results[ticker] = {
            'company': catalyst['company'],
            'catalyst_date': str(catalyst['catalyst_date']),
            'catalyst_type': catalyst['catalyst_type'],
            'drug_name': catalyst['drug_name'],
            'indication': catalyst['indication'],
            'disease_category': catalyst['disease_category'],
            'bayesian_analysis': {
                'base_rate': round(base_rate, 3),
                'base_rate_source': f"{catalyst['phase']} {catalyst['disease_category']} historical avg",
                'base_confidence': 100,
                'fund_signals': fund_signals,
                'final_posterior': round(final_posterior, 3),
                'interpretation': interpretation,
                'num_funds_analyzed': len(fund_signals),
                'total_signal_weight': round(total_weight - 100, 1)  # Exclude base weight
            }
        }
        
        print(f"✓ {len(fund_signals)} funds | Base: {base_rate:.1%} → Final: {final_posterior:.1%}")
    
    # Save to JSON
    output_date = datetime.now().strftime('%Y%m%d')
    output_path = PROJECT_ROOT / f"Bayes_Score_{output_date}.json"
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Analyzed {len(results)} catalysts")
    print(f"📁 Saved to: {output_path}")
    
    # Print top 10 by posterior probability
    if results:
        print(f"\n{'='*80}")
        print("TOP 10 CATALYSTS BY BAYESIAN PROBABILITY")
        print(f"{'='*80}")
        
        sorted_results = sorted(results.items(), 
                               key=lambda x: x[1]['bayesian_analysis']['final_posterior'], 
                               reverse=True)
        
        for ticker, data in sorted_results[:10]:
            ba = data['bayesian_analysis']
            print(f"{ticker:6s} | {str(data['drug_name'])[:25]:25s} | "
                  f"Base: {ba['base_rate']:.1%} → Final: {ba['final_posterior']:.1%} "
                  f"({ba['num_funds_analyzed']} funds)")
    
    return results



#18 - Backtest Bayesian Strategy
def backtest_bayesian_strategy(
    train_end_date,
    test_start_date,
    test_end_date,
    long_threshold,
    short_threshold,
    min_funds,
    min_sample_size
):
    """
    Backtest Bayesian clinical trial prediction strategy with proper train/test split
    
    METHODOLOGY:
    1. TRAIN: Build fund performance curves from historical trials (before train_end_date)
    2. TEST: Generate signals on out-of-sample trials (test_start_date to test_end_date)
    3. No data leakage - only use fund holdings that existed BEFORE each trial
    
    Args:
        train_end_date: End of training period for building fund curves
        test_start_date: Start of test period
        test_end_date: End of test period
        long_threshold: Posterior > base + threshold → LONG
        short_threshold: Posterior < base - threshold → SHORT
        min_funds: Minimum funds required to generate signal
        min_sample_size: Minimum historical bets per fund band
    
    Returns:
        DataFrame with backtest results
    """
    
    # Create Backtest directory if it doesn't exist
    backtest_dir = PROJECT_ROOT / "Backtest"
    backtest_dir.mkdir(exist_ok=True)
    
    print("\n" + "="*80)
    print("BACKTESTING BAYESIAN STRATEGY")
    print("="*80)
    print(f"\nTRAINING PERIOD: Up to {train_end_date}")
    print(f"TESTING PERIOD: {test_start_date} to {test_end_date}")
    print(f"\nParameters:")
    print(f"  Long threshold: +{long_threshold*100:.0f}pp")
    print(f"  Short threshold: -{short_threshold*100:.0f}pp")
    print(f"  Min funds: {min_funds}")
    print(f"  Min sample size: {min_sample_size}")
    print("="*80 + "\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    bands = [
        (1.5, 2, "1.5-2%"),
        (2,3,"2-3%"),
        (3, 4, "3-4%"),
        (4, 5, "4-5%"),
        (5, 6, "5-6%"),
        (6, 7, "6-7%"),
        (7, 8, "7-8%"),
        (8, 9, "8-9%"),
        (9, 10, "9-10%"),
        (10, 15, "10-15%"),
        (15, 100, ">15%")
    ]
    
    # ========================================================================
    # STEP 1: BUILD FUND PERFORMANCE CURVES FROM TRAINING DATA
    # ========================================================================
    
    print("STEP 1: Building fund performance curves from training data...")
    
    fund_performance_curves = {}
    fund_training_stats = []
    
    for fund_name, cik in FUNDS.items():
        # Load individual fund CSV (has ALL holdings across time)
        fund_csv = base_path / cik / f"{fund_name}.csv"
        
        if not fund_csv.exists():
            continue
        
        try:
            holdings = pd.read_csv(fund_csv)
            holdings = holdings.dropna(subset=['cusip', 'report_date', 'weight_pct'])
            holdings['cusip'] = holdings['cusip'].apply(normalize_cusip)
            holdings['report_date'] = pd.to_datetime(holdings['report_date'], errors='coerce')
            holdings = holdings.dropna(subset=['report_date'])
            
            # Get all completed trials from database (with outcomes) in TRAINING period
            trials_with_outcomes = pd.read_sql(f"""
                SELECT 
                    ct.cusip,
                    ct.nct_id,
                    ct.primary_completion_date,
                    ct.drug_name,
                    ct.indication,
                    ct.phase,
                    tsp.trial_outcome_by_return as stock_outcome
                FROM clinical_trials ct
                JOIN trial_stock_prices tsp ON ct.nct_id = tsp.nct_id
                WHERE ct.trial_status = 'COMPLETED'
                AND ct.primary_completion_date IS NOT NULL
                AND ct.primary_completion_date != ''
                AND ct.primary_completion_date < '{train_end_date}'
                AND tsp.trial_outcome_by_return IS NOT NULL
                AND ABS(tsp.entry_to_announcement_return_pct) <= 200
            """, conn)
            
            if trials_with_outcomes.empty:
                continue
            
            # Normalize dates
            def normalize_date(date_str):
                if pd.isna(date_str):
                    return None
                date_str = str(date_str).strip()
                if len(date_str) == 7:
                    return f"{date_str}-01"
                elif len(date_str) == 4:
                    return f"{date_str}-01-01"
                return date_str
            
            trials_with_outcomes['primary_completion_date'] = trials_with_outcomes['primary_completion_date'].apply(normalize_date)
            trials_with_outcomes['primary_completion_date'] = pd.to_datetime(
                trials_with_outcomes['primary_completion_date'], 
                errors='coerce'
            )
            trials_with_outcomes = trials_with_outcomes.dropna(subset=['primary_completion_date'])
            
            # Build training bets for THIS fund
            training_bets = []
            
            for _, trial in trials_with_outcomes.iterrows():
                cusip = trial['cusip']
                completion_date = trial['primary_completion_date']
                
                # Get fund's holdings of this stock
                stock_holdings = holdings[holdings['cusip'] == cusip].copy()
                
                if stock_holdings.empty:
                    continue
                
                # Must have held BEFORE trial completion
                holdings_before = stock_holdings[stock_holdings['report_date'] < completion_date]
                
                if holdings_before.empty:
                    continue
                
                # Get position in last quarter before trial
                pre_trial = holdings_before.sort_values('report_date').iloc[-1]
                pre_trial_weight = pre_trial['weight_pct']
                
                # Only ≥3% positions
                if pre_trial_weight < 1.5:
                    continue
                
                training_bets.append({
                    'cusip': cusip,
                    'trial_completion_date': completion_date,
                    'pre_trial_weight_pct': pre_trial_weight,
                    'stock_outcome': trial['stock_outcome']
                })
            
            if not training_bets:
                continue
            
            training_df = pd.DataFrame(training_bets)
            
            # Calculate performance by position band
            band_stats = {}
            
            for low, high, label in bands:
                band_bets = training_df[
                    (training_df['pre_trial_weight_pct'] >= low) &
                    (training_df['pre_trial_weight_pct'] < high)
                ]
                
                if len(band_bets) >= min_sample_size:
                    success_count = len(band_bets[band_bets['stock_outcome'] == 'success'])
                    total_count = len(band_bets)
                    success_rate = success_count / total_count
                    
                    band_stats[label] = {
                        'success_rate': success_rate,
                        'num_bets': total_count
                    }
                    
                    fund_training_stats.append({
                        'fund_name': fund_name,
                        'position_band': label,
                        'num_bets': total_count,
                        'success_count': success_count,
                        'success_rate': round(success_rate, 3)
                    })
            
            if band_stats:
                fund_performance_curves[fund_name] = band_stats
                print(f"  ✓ {fund_name}: {len(band_stats)} bands, {len(training_df)} total bets")
        
        except Exception as e:
            print(f"  ⚠ Error processing {fund_name}: {e}")
            continue
    
    print(f"\n✓ Built performance curves for {len(fund_performance_curves)} funds\n")
    
    # Save training curves to CSV
    if fund_training_stats:
        training_stats_df = pd.DataFrame(fund_training_stats)
        training_output = backtest_dir / f"training_curves_{datetime.now().strftime('%Y%m%d')}.csv"
        training_stats_df.to_csv(training_output, index=False)
        print(f"📁 Saved training curves to: {training_output}\n")
    
    # ========================================================================
    # STEP 2: GET TEST TRIALS
    # ========================================================================
    
    print("STEP 2: Loading test trials...")
    
    test_trials = pd.read_sql(f"""
        SELECT 
            ct.cusip,
            c.ticker,
            c.issuer_name_clean as company,
            ct.nct_id,
            ct.drug_name,
            ct.indication,
            ct.disease_category,
            ct.phase,
            ct.primary_completion_date,
            ct.phase3_success_rate as base_rate_phase3,
            ct.phase2_success_rate as base_rate_phase2,
            tsp.entry_to_announcement_return_pct as actual_return,
            tsp.trial_outcome_by_return as actual_outcome,
            tsp.price_30d_before as entry_price
        FROM clinical_trials ct
        JOIN companies c ON ct.cusip = c.cusip
        JOIN trial_stock_prices tsp ON ct.nct_id = tsp.nct_id
        WHERE ct.trial_status = 'COMPLETED'
        AND ct.primary_completion_date >= '{test_start_date}'
        AND ct.primary_completion_date <= '{test_end_date}'
        AND ct.primary_completion_date IS NOT NULL
        AND ct.primary_completion_date != ''
        AND tsp.trial_outcome_by_return IS NOT NULL
        AND tsp.entry_to_announcement_return_pct IS NOT NULL
        AND ABS(tsp.entry_to_announcement_return_pct) <= 200
        AND c.ticker IS NOT NULL
        AND c.is_biotech = 1
        ORDER BY ct.primary_completion_date
    """, conn)
    
    conn.close()
    
    print(f"✓ Found {len(test_trials)} test trials\n")
    
    if test_trials.empty:
        print("⚠ No test trials found")
        return pd.DataFrame()
    
    # ========================================================================
    # STEP 3: GENERATE SIGNALS AND CALCULATE P&L
    # ========================================================================
    
    print("STEP 3: Generating signals and calculating P&L...\n")
    
    backtest_results = []
    signal_details = []
    
    for idx, trial in test_trials.iterrows():
        trial_date = pd.to_datetime(trial['primary_completion_date'])
        cusip = trial['cusip']
        
        # Get fund holdings BEFORE trial
        fund_positions = []
        
        for fund_name, cik in FUNDS.items():
            if fund_name not in fund_performance_curves:
                continue
            
            fund_csv = base_path / cik / f"{fund_name}.csv"
            
            if not fund_csv.exists():
                continue
            
            try:
                holdings = pd.read_csv(fund_csv)
                holdings = holdings.dropna(subset=['cusip', 'report_date', 'weight_pct'])
                holdings['cusip'] = holdings['cusip'].apply(normalize_cusip)
                holdings['report_date'] = pd.to_datetime(holdings['report_date'], errors='coerce')
                holdings = holdings.dropna(subset=['report_date'])
                
                # Get holdings BEFORE trial
                stock_holdings = holdings[
                    (holdings['cusip'] == cusip) &
                    (holdings['report_date'] < trial_date) &
                    (holdings['weight_pct'] >= 1.5)
                ]
                
                if stock_holdings.empty:
                    continue
                
                # Most recent position
                latest = stock_holdings.sort_values('report_date').iloc[-1]
                position_pct = latest['weight_pct']
                
                # Find position band
                position_band = None
                for low, high, label in bands:
                    if low <= position_pct < high:
                        position_band = label
                        break
                
                if not position_band:
                    continue
                
                # Get performance from TRAINING curves
                if position_band not in fund_performance_curves[fund_name]:
                    continue
                
                perf = fund_performance_curves[fund_name][position_band]
                
                fund_positions.append({
                    'fund_name': fund_name,
                    'position_pct': position_pct,
                    'position_band': position_band,
                    'success_rate': perf['success_rate'],
                    'num_bets': perf['num_bets']
                })
                
            except Exception as e:
                continue
        
        # Determine base rate
        base_rate_phase3 = trial['base_rate_phase3']
        base_rate_phase2 = trial['base_rate_phase2']
        
        if trial['phase'] == 'PHASE3':
            base_rate = base_rate_phase3
        elif trial['phase'] == 'PHASE2':
            base_rate = base_rate_phase2
        else:
            if pd.notna(base_rate_phase3) and pd.notna(base_rate_phase2):
                base_rate = (base_rate_phase3 + base_rate_phase2) / 2
            elif pd.notna(base_rate_phase3):
                base_rate = base_rate_phase3
            elif pd.notna(base_rate_phase2):
                base_rate = base_rate_phase2
            else:
                base_rate = None
        
        if pd.isna(base_rate) or base_rate == 0 or base_rate is None:
            base_rate = 0.50
        
        # Calculate Bayesian posterior (CONVICTION-WEIGHTED)
        prior_weight = 100
        weighted_sum = base_rate * prior_weight
        total_weight = prior_weight
        
        for pos in fund_positions:
            conviction = pos['position_pct'] / 10.0
            
            if pos['num_bets'] < 3:
                credibility = 0.3
            elif pos['num_bets'] < 10:
                credibility = (pos['num_bets'] / 10) ** 0.5
            else:
                credibility = 1.0
            
            signal_weight = conviction * credibility * 100
            
            weighted_sum += pos['success_rate'] * signal_weight
            total_weight += signal_weight
        
        bayesian_posterior = weighted_sum / total_weight
        
        # Generate signal
        signal = 'PASS'
        
        if len(fund_positions) >= min_funds:
            if bayesian_posterior > base_rate + long_threshold:
                signal = 'LONG'
            elif bayesian_posterior < base_rate - short_threshold:
                signal = 'SHORT'
        
        # Calculate P&L
        actual_return = trial['actual_return'] if not pd.isna(trial['actual_return']) else 0
        
        if signal == 'LONG':
            pnl = actual_return
        elif signal == 'SHORT':
            pnl = -actual_return
        else:
            pnl = 0
        
        # Transaction costs
        if signal == 'LONG':
            transaction_cost = -0.3
        elif signal == 'SHORT':
            transaction_cost = -1.16
        else:
            transaction_cost = 0
        
        net_pnl = pnl + transaction_cost
        
        backtest_results.append({
            'trial_date': trial_date.date(),
            'ticker': trial['ticker'],
            'company': trial['company'],
            'drug_name': trial['drug_name'],
            'indication': trial['indication'],
            'phase': trial['phase'],
            'disease_category': trial['disease_category'],
            'base_rate': round(base_rate, 3),
            'posterior': round(bayesian_posterior, 3),
            'diff': round(bayesian_posterior - base_rate, 3),
            'num_funds': len(fund_positions),
            'signal': signal,
            'actual_outcome': trial['actual_outcome'],
            'actual_return_%': round(actual_return, 1),
            'gross_pnl_%': round(pnl, 1),
            'transaction_cost_%': round(transaction_cost, 2),
            'net_pnl_%': round(net_pnl, 1)
        })
        
        if signal != 'PASS':
            for pos in fund_positions:
                signal_details.append({
                    'trial_date': trial_date.date(),
                    'ticker': trial['ticker'],
                    'signal': signal,
                    'fund_name': pos['fund_name'],
                    'position_pct': round(pos['position_pct'], 2),
                    'position_band': pos['position_band'],
                    'historical_success_rate': round(pos['success_rate'], 3),
                    'historical_num_bets': pos['num_bets']
                })
        
        if (idx + 1) % 20 == 0:
            print(f"  [{idx+1}/{len(test_trials)}] Processed")
    
    # Convert to DataFrames
    backtest_df = pd.DataFrame(backtest_results)
    signal_details_df = pd.DataFrame(signal_details)
    
    # Print results
    print("\n" + "="*80)
    print("BACKTEST RESULTS")
    print("="*80)
    
    traded = backtest_df[backtest_df['signal'] != 'PASS']
    
    if not traded.empty:
        longs = traded[traded['signal'] == 'LONG']
        shorts = traded[traded['signal'] == 'SHORT']
        
        print(f"\nTotal trials: {len(backtest_df)}")
        print(f"Signals generated: {len(traded)} ({len(traded)/len(backtest_df)*100:.1f}%)")
        print(f"  - Long: {len(longs)}")
        print(f"  - Short: {len(shorts)}")
        
        print(f"\nPERFORMANCE (NET OF COSTS):")
        print(f"  Win rate: {(traded['net_pnl_%'] > 0).sum()/len(traded)*100:.1f}%")
        print(f"  Avg net P&L: {traded['net_pnl_%'].mean():.1f}%")
        print(f"  Total net P&L: {traded['net_pnl_%'].sum():.1f}%")
        print(f"  Sharpe ratio: {traded['net_pnl_%'].mean() / traded['net_pnl_%'].std():.2f}")
        print(f"  Best trade: {traded['net_pnl_%'].max():.1f}%")
        print(f"  Worst trade: {traded['net_pnl_%'].min():.1f}%")
        
        if not longs.empty:
            print(f"\nLONG SIGNALS ({len(longs)}):")
            print(f"  Win rate: {(longs['actual_outcome']=='success').sum()/len(longs)*100:.1f}%")
            print(f"  Avg return: {longs['net_pnl_%'].mean():.1f}%")
        
        if not shorts.empty:
            print(f"\nSHORT SIGNALS ({len(shorts)}):")
            print(f"  Win rate: {(shorts['actual_outcome']=='failure').sum()/len(shorts)*100:.1f}%")
            print(f"  Avg return: {shorts['net_pnl_%'].mean():.1f}%")
    
    # Save results
    output_date = datetime.now().strftime('%Y%m%d')
    
    main_output = backtest_dir / f"backtest_results_{output_date}.csv"
    backtest_df.to_csv(main_output, index=False)
    print(f"\n📁 Main results: {main_output}")
    
    if not signal_details_df.empty:
        details_output = backtest_dir / f"signal_details_{output_date}.csv"
        signal_details_df.to_csv(details_output, index=False)
        print(f"📁 Signal details: {details_output}")
    
    summary_stats = {
        'backtest_date': datetime.now().strftime('%Y-%m-%d'),
        'train_period': f"Up to {train_end_date}",
        'test_period': f"{test_start_date} to {test_end_date}",
        'long_threshold': long_threshold,
        'short_threshold': short_threshold,
        'min_funds': min_funds,
        'total_test_trials': len(backtest_df),
        'signals_generated': len(traded),
        'long_signals': len(longs) if not longs.empty else 0,
        'short_signals': len(shorts) if not shorts.empty else 0,
        'win_rate_%': round((traded['net_pnl_%'] > 0).sum()/len(traded)*100, 1) if not traded.empty else 0,
        'avg_net_pnl_%': round(traded['net_pnl_%'].mean(), 1) if not traded.empty else 0,
        'total_net_pnl_%': round(traded['net_pnl_%'].sum(), 1) if not traded.empty else 0,
        'sharpe_ratio': round(traded['net_pnl_%'].mean() / traded['net_pnl_%'].std(), 2) if not traded.empty else 0
    }
    
    summary_df = pd.DataFrame([summary_stats])
    summary_output = backtest_dir / f"backtest_summary_{output_date}.csv"
    summary_df.to_csv(summary_output, index=False)
    print(f"📁 Summary stats: {summary_output}")
    
    print("="*80 + "\n")
    
    return backtest_df

#19b - Portfolio-Level Statistics (More Realistic)
def calculate_portfolio_level_statistics(backtest_csv_path=None, position_size=0.025, max_concurrent=40):
    """
    Calculate realistic portfolio-level statistics
    
    Assumes you run this as a portfolio strategy with multiple concurrent positions,
    not as a single sequential strategy.
    
    Args:
        backtest_csv_path: Path to backtest CSV
        position_size: Size of each position (default 2.5% = 40 max positions)
        max_concurrent: Maximum concurrent positions (default 40)
    
    Returns:
        Dictionary with portfolio-level statistics
    """
    import numpy as np
    
    print("\n" + "="*80)
    print("PORTFOLIO-LEVEL STATISTICS (REALISTIC)")
    print("="*80 + "\n")
    
    # Load backtest
    if backtest_csv_path is None:
        backtest_dir = PROJECT_ROOT / "Backtest"
        csv_files = list(backtest_dir.glob("backtest_results_*.csv"))
        if not csv_files:
            print("⚠ No backtest CSV found")
            return None
        backtest_csv_path = max(csv_files, key=lambda p: p.stat().st_mtime)
    
    backtest_df = pd.read_csv(backtest_csv_path)
    traded = backtest_df[backtest_df['signal'] != 'PASS'].copy()
    traded['trial_date'] = pd.to_datetime(traded['trial_date'])
    traded = traded.sort_values('trial_date')
    
    returns = traded['net_pnl_%'].values / 100
    
    # Time period
    start_date = traded['trial_date'].min()
    end_date = traded['trial_date'].max()
    years = (end_date - start_date).days / 365.25
    
    print(f"Assumptions:")
    print(f"  Position size: {position_size*100:.1f}% per trade")
    print(f"  Max concurrent positions: {max_concurrent}")
    print(f"  Period: {start_date.date()} to {end_date.date()} ({years:.1f} years)")
    print(f"  Total signals: {len(traded)}\n")
    
    # Portfolio-level return per trade
    portfolio_returns_per_trade = returns * position_size
    
    # Aggregate by month (assuming overlapping positions)
    traded['year_month'] = traded['trial_date'].dt.to_period('M')
    monthly_returns = traded.groupby('year_month')['net_pnl_%'].apply(
        lambda x: (x / 100 * position_size).sum()
    )
    
    # Calculate statistics on monthly returns
    monthly_mean = monthly_returns.mean()
    monthly_std = monthly_returns.std()
    
    # Annualize
    annual_return = monthly_mean * 12
    annual_volatility = monthly_std * np.sqrt(12)
    sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
    
    # CAGR from monthly compounding
    monthly_cagr = (1 + monthly_returns).prod() ** (1 / len(monthly_returns)) - 1
    annual_cagr = (1 + monthly_cagr) ** 12 - 1
    
    # Max drawdown on monthly portfolio level
    cumulative_portfolio = (1 + monthly_returns).cumprod()
    running_max = np.maximum.accumulate(cumulative_portfolio)
    drawdown = (cumulative_portfolio - running_max) / running_max
    max_drawdown = drawdown.min()
    
    # Win rate and profit factor (same as before)
    win_rate = (returns > 0).sum() / len(returns)
    winners = returns[returns > 0]
    losers = returns[returns < 0]
    avg_win = winners.mean() if len(winners) > 0 else 0
    avg_loss = losers.mean() if len(losers) > 0 else 0
    profit_factor = abs(winners.sum() / losers.sum()) if len(losers) > 0 and losers.sum() != 0 else np.inf
    
    # Calmar ratio
    calmar_ratio = annual_cagr / abs(max_drawdown) if max_drawdown != 0 else 0
    
    # Expected value per trade (portfolio level)
    ev_per_trade = portfolio_returns_per_trade.mean()
    
    stats = {
        'position_size_%': position_size * 100,
        'max_concurrent_positions': max_concurrent,
        'years': round(years, 2),
        'total_trades': len(traded),
        'trades_per_year': round(len(traded) / years, 1),
        
        'monthly_mean_return_%': round(monthly_mean * 100, 2),
        'monthly_volatility_%': round(monthly_std * 100, 2),
        
        'annual_return_%': round(annual_return * 100, 2),
        'annual_volatility_%': round(annual_volatility * 100, 2),
        'cagr_%': round(annual_cagr * 100, 2),
        
        'sharpe_ratio': round(sharpe_ratio, 3),
        'max_drawdown_%': round(max_drawdown * 100, 2),
        'calmar_ratio': round(calmar_ratio, 3),
        
        'win_rate_%': round(win_rate * 100, 2),
        'avg_win_%': round(avg_win * 100, 2),
        'avg_loss_%': round(avg_loss * 100, 2),
        'profit_factor': round(profit_factor, 2) if profit_factor != np.inf else 'Inf',
        
        'expected_value_per_trade_%': round(ev_per_trade * 100, 3),
        'expected_value_per_year_%': round(ev_per_trade * len(traded) / years * 100, 2)
    }
    
    print(f"{'='*80}")
    print("PORTFOLIO PERFORMANCE")
    print(f"{'='*80}\n")
    
    print(f"Monthly Returns:")
    print(f"  Mean: {stats['monthly_mean_return_%']:>8.2f}%")
    print(f"  Volatility: {stats['monthly_volatility_%']:>8.2f}%")
    
    print(f"\nAnnualized Performance:")
    print(f"  Annual return: {stats['annual_return_%']:>8.2f}%")
    print(f"  Annual volatility: {stats['annual_volatility_%']:>8.2f}%")
    print(f"  CAGR: {stats['cagr_%']:>8.2f}%")
    
    print(f"\nRisk Metrics:")
    print(f"  Sharpe ratio: {stats['sharpe_ratio']:>8.3f}")
    print(f"  Max drawdown: {stats['max_drawdown_%']:>8.2f}%")
    print(f"  Calmar ratio: {stats['calmar_ratio']:>8.3f}")
    
    print(f"\nTrade Statistics:")
    print(f"  Win rate: {stats['win_rate_%']:>8.2f}%")
    print(f"  Avg win: {stats['avg_win_%']:>8.2f}%")
    print(f"  Avg loss: {stats['avg_loss_%']:>8.2f}%")
    print(f"  Profit factor: {stats['profit_factor']}")
    
    print(f"\nExpected Value:")
    print(f"  Per trade (portfolio level): {stats['expected_value_per_trade_%']:>8.3f}%")
    print(f"  Per year (portfolio level): {stats['expected_value_per_year_%']:>8.2f}%")
    
    print(f"\n{'='*80}\n")
    
    return stats




if __name__ == '__main__':

    #1. Load environment variables
    load_dotenv() 
    
    #2. Download files for all FUNDS
    file_downloader()
    
    #3. Process filings
    process_filings()
    
    #4. master sheet
    master_table = master_set(base_path)

    #4.5 Needs to ensure backtest has data.
    populate_fund_holdings_database()

    #5. Create database for clinical trial storage
    setup_database()
    
    #5.5 clean_company_name() & query_clinicaltrials_for_company() ARE HELPER FUNCTIONS, do not call.

    #6. Build company mapping from master.csv -> extracts unique companies -> cleans company name -> stores company
    build_company_mapping()

    #7. Download clinical trail databases 
    populate_clinical_trials_database()

    #8. Turn cusip -> create tickers.csv -> I need to fill in manually
    export_companies_for_ticker_entry()

    #9. Imports ticker symbols, so Step 12. can create yfinance for each company.
    #import_tickers_from_csv()

    #10. Downloads last 10 years stock information from each firm.
    #download_10y_price_history_for_all_tickers()

    #10.5 get_stock_price_around_catalyst_from_cache() is a helper function to get 11 to work.

    #11. Fetches stock prices and matches to trial date
    #fetch_historical_stock_prices_for_trials()

    #11.5 Feeder to help 12. get_peak_daily_move_in_announcement_window

    #12. Labels trial outcome (success or fail based on ±10% movement 30-210 days after trial).
    #label_trial_outcomes_from_announcement_spike()

    #13 - Generates FULL BETTING history for each fund - generating bet_tracker.csv
    #generate_fund_bet_trackers()

    #14 - Generates 1 csv high_conviction_bet_history.csv per fund (>3% holding), and 1 JSON summary (high_conviction_performance.json).
    #generate_high_conviction_bet_analysis()

    #14.5 Helper Function - Classify Disease Category classify_disease_category()

    #15 - Scrapes PFUDA calendar (backend FDAtracker.com google calendar API to get up to date calendar dates)
    #harvest_pdufa_dates()

    #16 - Query ClinicalTrial.gov for upcoming Phase 2, Phase 2/3, Phase 3 clinical trials for companies with tickers. generate_catalyst_calendar() generates CSV.
    #harvest_upcoming_clinical_trials()
    #generate_catalyst_calendar()

    #17 Final step, JSON generater in Fixed_Biotech/JSON - with historic likelihood, Bayes updator for each fund holding, based on conviction (% of portfolio), and implied success.
    #generate_bayesian_catalyst_analysis()

#Backtesting - Delete the """ to use it.
"""
    #18 Backtester
    # 18 is backtester that creates the CSV's but this can be called in #19 as backtest_df = backtest_bayesian
    #18 also doesn't contain any dates, so that can be configured below, in #19.

    #19 Backtester
    backtest_df = backtest_bayesian_strategy(
    train_end_date='2021-03-30',
    test_start_date='2021-04-01',
    test_end_date='2026-01-16',
    long_threshold=0.0001,      # 2pp above base
    short_threshold=0.50,     # 15pp below base
    min_funds=2,              # Single fund can trigger signal
    min_sample_size=2         # Accept even 1 historical bet
    )

    stats_realistic = calculate_portfolio_level_statistics(
    position_size=0.02,  # 2% per position
    max_concurrent=50     # Up to 50 positions at once
    )"""


    #SUCCESS
""" INSTRUCTIONS
QUARTERLY (Every 13 weeks - after new 13F filings)
#2. file_downloader()          # Download new 13F filings
#3. process_filings()           # Parse the new filings
#4. master_set()                # Update master holdings summary
#13. generate_fund_bet_trackers()  # Update full bet history
#14. generate_high_conviction_bet_analysis()  # Update conviction analysis
#17. generate_bayesian_catalyst_analysis()  # Update Bayesian scores with new holdings


MONTHLY:
#15. harvest_pdufa_dates()      # PDUFA calendar updates regularly
#16. harvest_upcoming_clinical_trials()  # New trials get announced
#16. generate_catalyst_calendar()  # Combine catalysts with holdings
#17. generate_bayesian_catalyst_analysis()  # Update with new catalysts
#10. download_10y_price_history_for_all_tickers()  # Run once, takes 30-45 min
#11. fetch_historical_stock_prices_for_trials()     # Run once
#12. label_trial_outcomes_from_announcement_spike() # Run once


ONE TIME:
#1. load_dotenv()               # Always runs (loads API keys)
#5. setup_database()            # Run once to create database
#6. build_company_mapping()     # Run once, then only when new companies appear
#7. populate_clinical_trials_database()  # Run once for historical data
#8. export_companies_for_ticker_entry()  # Run once, then manual ticker entry
#9. import_tickers_from_csv()   # Run once after manual ticker entry


"""
