"""
Smart Fertilizer Recommendation
A five-page multilingual agricultural support application.
Pure Python (Flask) + HTML/CSS/JS (Leaflet map, no paid API keys required).
"""

from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "smart-fertilizer"  # change before real deployment

# ----------------------------------------------------------------------
# 1. STATIC REFERENCE DATA
# ----------------------------------------------------------------------

CROPS = ["Rice", "Wheat", "Maize", "Sugarcane", "Cotton",
         "Groundnut", "Soybean", "Vegetables", "Pulses"]

SOILS = ["Sandy", "Clay", "Loamy", "Black (Regur)", "Red", "Alluvial"]

SEASONS = ["Kharif (Monsoon)", "Rabi (Winter)", "Zaid (Summer)"]

# Soil fertility assumption -> drives the "Less Soil Fertility?" branch in the block diagram
SOIL_FERTILITY = {
    "Sandy": "Low",
    "Red": "Low",
    "Clay": "Medium",
    "Black (Regur)": "Medium",
    "Loamy": "High",
    "Alluvial": "High",
}

CROP_ICON = {
    "Rice": "🌾", "Wheat": "🌾", "Maize": "🌽", "Sugarcane": "🎋",
    "Cotton": "☁️", "Groundnut": "🥜", "Soybean": "🫘",
    "Vegetables": "🥬", "Pulses": "🫘",
}

SOIL_ICON = {
    "Sandy": "🏖️", "Clay": "🧱", "Loamy": "🌱",
    "Black (Regur)": "⬛", "Red": "🟥", "Alluvial": "🏞️",
}

# Base NPK / fertilizer guidance per crop (typical extension-service style values, for demo purposes)
CROP_FERTILIZER = {
    "Rice":        {"npk": "100:50:50 kg/ha", "primary": "Urea + DAP", "secondary": "Zinc Sulphate", "brands": ["IFFCO Urea", "Coromandel DAP", "Zuari Zinc"]},
    "Wheat":       {"npk": "120:60:40 kg/ha", "primary": "Urea + SSP", "secondary": "Muriate of Potash (MOP)", "brands": ["NFL Urea", "GSFC SSP", "IPL MOP"]},
    "Maize":       {"npk": "150:75:60 kg/ha", "primary": "Urea + DAP", "secondary": "Boron Mix", "brands": ["KRIBHCO Urea", "Coromandel DAP"]},
    "Sugarcane":   {"npk": "280:90:90 kg/ha", "primary": "NPK Complex (19:19:19)", "secondary": "Sulphur", "brands": ["IFFCO NPK", "Zuari Sulphur"]},
    "Cotton":      {"npk": "100:50:50 kg/ha", "primary": "Urea + SSP", "secondary": "Potash", "brands": ["Rallis Urea", "GSFC SSP"]},
    "Groundnut":   {"npk": "25:50:75 kg/ha", "primary": "SSP + Gypsum", "secondary": "MOP", "brands": ["GSFC SSP", "Coromandel Gypsum"]},
    "Soybean":     {"npk": "30:60:40 kg/ha", "primary": "DAP + MOP", "secondary": "Sulphur", "brands": ["Coromandel DAP", "IPL MOP"]},
    "Vegetables":  {"npk": "100:100:100 kg/ha", "primary": "NPK Complex (19:19:19)", "secondary": "Micronutrient Mix", "brands": ["IFFCO NPK", "Tata Micronutrients"]},
    "Pulses":      {"npk": "20:40:20 kg/ha", "primary": "DAP + Rhizobium Culture", "secondary": "Sulphur", "brands": ["Coromandel DAP", "NBF Rhizobium"]},
}

# Growth-stage based application schedule (generic, per crop group)
CROP_STAGES = {
    "Rice":       ["Basal (at transplanting)", "Tillering (20-25 days)", "Panicle Initiation (40-45 days)", "Grain Filling (60-70 days)"],
    "Wheat":      ["Basal (at sowing)", "Crown Root Initiation (20-25 days)", "Tillering (40 days)", "Flowering (60-65 days)"],
    "Maize":      ["Basal (at sowing)", "Knee-high stage (25-30 days)", "Tasseling (45-50 days)", "Grain Filling (65-70 days)"],
    "Sugarcane":  ["Basal (at planting)", "Tillering (45 days)", "Grand Growth (90-120 days)", "Maturity (180+ days)"],
    "Cotton":     ["Basal (at sowing)", "Squaring (30-35 days)", "Flowering (55-60 days)", "Boll Development (80-90 days)"],
    "Groundnut":  ["Basal (at sowing)", "Vegetative (25-30 days)", "Pegging (45 days)", "Pod Development (65-70 days)"],
    "Soybean":    ["Basal (at sowing)", "Vegetative (20-25 days)", "Flowering (40 days)", "Pod Filling (60 days)"],
    "Vegetables": ["Basal (at transplanting)", "Vegetative Growth (15-20 days)", "Flowering (30-35 days)", "Fruiting (45+ days)"],
    "Pulses":     ["Basal (at sowing)", "Vegetative (20 days)", "Flowering (35-40 days)", "Pod Filling (55 days)"],
}

# Sample vendors around a default demo location (Chikodi, Karnataka) — replace with a real
# vendor database + geocoding service for production use.
BASE_LAT, BASE_LNG = 16.4230, 74.6015
VENDORS = [
    {"name": "Krishi Seva Kendra", "lat": 16.4510, "lng": 74.6400, "distance_km": 5, "contact": "+91-98xxxxxx01"},
    {"name": "Raitha Fertilizers & Seeds", "lat": 16.3900, "lng": 74.5600, "distance_km": 12, "contact": "+91-98xxxxxx02"},
    {"name": "Annapurna Agro Center", "lat": 16.4800, "lng": 74.5300, "distance_km": 18, "contact": "+91-98xxxxxx03"},
    {"name": "Bharat Krishi Bhandar", "lat": 16.3500, "lng": 74.6900, "distance_km": 22, "contact": "+91-98xxxxxx04"},
    {"name": "Green Field Agro Suppliers", "lat": 16.5200, "lng": 74.6800, "distance_km": 27, "contact": "+91-98xxxxxx05"},
]

# ----------------------------------------------------------------------
# 2. TRANSLATIONS (English / Hindi / Kannada)
# ----------------------------------------------------------------------

TRANSLATIONS = {
    "en": {
        "app_name": "Smart Fertilizer Recommendation",
        "tagline": "Right fertilizer. Right time. Right place.",
        "choose_language": "Choose your language",
        "start": "Start",
        "page1_title": "Tell us about your field",
        "area": "Area / City", "area_ph": "e.g. Chikodi",
        "season": "Season", "crop": "Crop Type", "soil": "Soil Type",
        "next": "Next",
        "page2_title": "Confirm your details",
        "page2_sub": "Please check everything before we recommend fertilizers.",
        "edit": "Edit Details", "correct": "Correct, Continue",
        "page3_title": "Recommended Fertilizer",
        "fert_type": "Fertilizer Type", "suitable_for": "Suitable Crop & Soil",
        "season_lbl": "Recommended Season", "brand": "Brand / Company",
        "npk": "Nutrient Requirement (N:P:K)",
        "fertility": "Soil Fertility Level",
        "view_duration": "View Application Duration",
        "page4_title": "Fertilizer Application Duration",
        "stage": "Crop Growth Stage", "apply_at": "When to Apply",
        "freq": "Frequency of Application", "freq_val": "Once per stage, split-dose recommended",
        "find_vendors": "Find Nearby Vendors",
        "page5_title": "Nearby Fertilizer Vendors",
        "page5_sub": "Vendors within 5-70 km of your selected area",
        "distance": "Distance", "contact": "Contact", "navigate": "Navigate",
        "restart": "Start Over",
        "back": "Back",
        "km": "km",
    },
    "hi": {
        "app_name": "स्मार्ट उर्वरक सिफारिश",
        "tagline": "सही उर्वरक। सही समय। सही स्थान।",
        "choose_language": "अपनी भाषा चुनें",
        "start": "शुरू करें",
        "page1_title": "अपने खेत के बारे में बताएं",
        "area": "क्षेत्र / शहर", "area_ph": "उदा. चिकोडी",
        "season": "मौसम", "crop": "फसल का प्रकार", "soil": "मिट्टी का प्रकार",
        "next": "आगे",
        "page2_title": "अपना विवरण जांचें",
        "page2_sub": "उर्वरक सुझाने से पहले कृपया सब कुछ जांच लें।",
        "edit": "विवरण संपादित करें", "correct": "सही है, आगे बढ़ें",
        "page3_title": "अनुशंसित उर्वरक",
        "fert_type": "उर्वरक प्रकार", "suitable_for": "उपयुक्त फसल एवं मिट्टी",
        "season_lbl": "अनुशंसित मौसम", "brand": "ब्रांड / कंपनी",
        "npk": "पोषक तत्व आवश्यकता (N:P:K)",
        "fertility": "मिट्टी की उर्वरता स्तर",
        "view_duration": "उपयोग अवधि देखें",
        "page4_title": "उर्वरक उपयोग अवधि",
        "stage": "फसल वृद्धि चरण", "apply_at": "कब लगाएं",
        "freq": "प्रयोग की आवृत्ति", "freq_val": "प्रति चरण एक बार, विभाजित मात्रा अनुशंसित",
        "find_vendors": "नज़दीकी विक्रेता खोजें",
        "page5_title": "नज़दीकी उर्वरक विक्रेता",
        "page5_sub": "आपके क्षेत्र के 5-70 किमी के भीतर विक्रेता",
        "distance": "दूरी", "contact": "संपर्क", "navigate": "दिशा-निर्देश",
        "restart": "फिर से शुरू करें",
        "back": "वापस",
        "km": "किमी",
    },
    "kn": {
        "app_name": "ಸ್ಮಾರ್ಟ್ ಗೊಬ್ಬರ ಶಿಫಾರಸು",
        "tagline": "ಸರಿಯಾದ ಗೊಬ್ಬರ. ಸರಿಯಾದ ಸಮಯ. ಸರಿಯಾದ ಸ್ಥಳ.",
        "choose_language": "ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆರಿಸಿ",
        "start": "ಪ್ರಾರಂಭಿಸಿ",
        "page1_title": "ನಿಮ್ಮ ಹೊಲದ ಬಗ್ಗೆ ತಿಳಿಸಿ",
        "area": "ಪ್ರದೇಶ / ಊರು", "area_ph": "ಉದಾ. ಚಿಕ್ಕೋಡಿ",
        "season": "ಋತು", "crop": "ಬೆಳೆ ಪ್ರಕಾರ", "soil": "ಮಣ್ಣಿನ ಪ್ರಕಾರ",
        "next": "ಮುಂದೆ",
        "page2_title": "ನಿಮ್ಮ ವಿವರಗಳನ್ನು ಖಚಿತಪಡಿಸಿ",
        "page2_sub": "ಗೊಬ್ಬರ ಶಿಫಾರಸು ಮಾಡುವ ಮೊದಲು ದಯವಿಟ್ಟು ಎಲ್ಲವನ್ನೂ ಪರಿಶೀಲಿಸಿ.",
        "edit": "ವಿವರ ಬದಲಿಸಿ", "correct": "ಸರಿ, ಮುಂದುವರಿಸಿ",
        "page3_title": "ಶಿಫಾರಸು ಮಾಡಿದ ಗೊಬ್ಬರ",
        "fert_type": "ಗೊಬ್ಬರದ ಪ್ರಕಾರ", "suitable_for": "ಸೂಕ್ತ ಬೆಳೆ ಮತ್ತು ಮಣ್ಣು",
        "season_lbl": "ಶಿಫಾರಸು ಮಾಡಿದ ಋತು", "brand": "ಬ್ರಾಂಡ್ / ಕಂಪನಿ",
        "npk": "ಪೋಷಕಾಂಶ ಅಗತ್ಯ (N:P:K)",
        "fertility": "ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಮಟ್ಟ",
        "view_duration": "ಬಳಕೆ ಅವಧಿ ವೀಕ್ಷಿಸಿ",
        "page4_title": "ಗೊಬ್ಬರ ಬಳಕೆ ಅವಧಿ",
        "stage": "ಬೆಳೆ ಬೆಳವಣಿಗೆ ಹಂತ", "apply_at": "ಯಾವಾಗ ಹಾಕಬೇಕು",
        "freq": "ಬಳಕೆಯ ಆವರ್ತನೆ", "freq_val": "ಪ್ರತಿ ಹಂತಕ್ಕೆ ಒಮ್ಮೆ, ವಿಭಜಿತ ಪ್ರಮಾಣ ಶಿಫಾರಸು",
        "find_vendors": "ಹತ್ತಿರದ ಮಾರಾಟಗಾರರನ್ನು ಹುಡುಕಿ",
        "page5_title": "ಹತ್ತಿರದ ಗೊಬ್ಬರ ಮಾರಾಟಗಾರರು",
        "page5_sub": "ನಿಮ್ಮ ಪ್ರದೇಶದ 5-70 ಕಿ.ಮೀ ಒಳಗಿನ ಮಾರಾಟಗಾರರು",
        "distance": "ದೂರ", "contact": "ಸಂಪರ್ಕ", "navigate": "ಮಾರ್ಗದರ್ಶನ",
        "restart": "ಮತ್ತೆ ಪ್ರಾರಂಭಿಸಿ",
        "back": "ಹಿಂದೆ",
        "km": "ಕಿ.ಮೀ",
    },
}


def t():
    """Return the translation dict for the currently selected language."""
    lang = session.get("lang", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"])


# ----------------------------------------------------------------------
# 3. ROUTES — one per page of the 5-page workflow
# ----------------------------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def page1():
    """Page 1: Language selection + input interface."""
    if request.method == "POST":
        session["lang"] = request.form.get("lang", session.get("lang", "en"))
        session["area"] = request.form.get("area", "").strip() or "Chikodi"
        session["season"] = request.form.get("season", SEASONS[0])
        session["crop"] = request.form.get("crop", CROPS[0])
        session["soil"] = request.form.get("soil", SOILS[0])
        return redirect(url_for("page2"))

    # Selecting a language re-renders this same page (GET) without advancing the workflow
    lang_param = request.args.get("lang")
    if lang_param in TRANSLATIONS:
        session["lang"] = lang_param

    return render_template("index.html", t=t(), langs=[("en", "English"), ("hi", "हिन्दी"), ("kn", "ಕನ್ನಡ")],
                            crops=CROPS, soils=SOILS, seasons=SEASONS,
                            cur_lang=session.get("lang", "en"), stage=1)


@app.route("/confirm")
def page2():
    """Page 2: Visual confirmation of inputs."""
    if "crop" not in session:
        return redirect(url_for("page1"))
    crop, soil = session["crop"], session["soil"]
    return render_template("confirm.html", t=t(), stage=2,
                            area=session["area"], season=session["season"],
                            crop=crop, soil=soil,
                            crop_icon=CROP_ICON.get(crop, "🌱"),
                            soil_icon=SOIL_ICON.get(soil, "🟫"))


@app.route("/recommend")
def page3():
    """Page 3: Fertilizer recommendation (core of the block diagram logic)."""
    if "crop" not in session:
        return redirect(url_for("page1"))
    crop, soil, season = session["crop"], session["soil"], session["season"]
    fertility = SOIL_FERTILITY.get(soil, "Medium")
    data = CROP_FERTILIZER.get(crop, CROP_FERTILIZER["Rice"])

    if fertility == "Low":
        recommendation = f"{data['primary']} + {data['secondary']} (enriched dose)"
        note = "Soil fertility is low — an enriched/compound fertilizer dose is recommended."
    elif fertility == "Medium":
        recommendation = data["primary"]
        note = "Soil fertility is moderate — standard recommended fertilizer dose applies."
    else:
        recommendation = f"Maintenance dose of {data['primary']}"
        note = "Soil fertility is high — only a pre-required (maintenance) fertilizer dose is needed."

    return render_template("recommend.html", t=t(), stage=3,
                            crop=crop, soil=soil, season=season,
                            crop_icon=CROP_ICON.get(crop, "🌱"),
                            fertility=fertility, recommendation=recommendation,
                            note=note, npk=data["npk"], brands=data["brands"])


@app.route("/duration")
def page4():
    """Page 4: Fertilizer application duration / crop growth stage guidance."""
    if "crop" not in session:
        return redirect(url_for("page1"))
    crop = session["crop"]
    stages = CROP_STAGES.get(crop, CROP_STAGES["Rice"])
    return render_template("duration.html", t=t(), stage=4,
                            crop=crop, crop_icon=CROP_ICON.get(crop, "🌱"),
                            stages=stages)


@app.route("/vendors")
def page5():
    """Page 5: Map-based vendor location."""
    if "crop" not in session:
        return redirect(url_for("page1"))
    return render_template("vendors.html", t=t(), stage=5,
                            area=session["area"], vendors=VENDORS,
                            base_lat=BASE_LAT, base_lng=BASE_LNG)


@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("page1"))


# ----------------------------------------------------------------------
# 4. PWA-lite files so the site can be "added to Home Screen" on a phone
# ----------------------------------------------------------------------

@app.route("/manifest.json")
def manifest():
    return {
        "name": "Smart Fertilizer Recommendation",
        "short_name": "FertiSmart",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#F7F3E8",
        "theme_color": "#4A7C59",
        "icons": [
            {"src": "/static/icon.svg", "sizes": "any", "type": "image/svg+xml"}
        ],
    }


if __name__ == "__main__":
    # host="0.0.0.0" lets you open the site from your phone's browser
    # over your home WiFi at http://<your-computer-ip>:5000
    app.run(host="0.0.0.0", port=5000, debug=True)
