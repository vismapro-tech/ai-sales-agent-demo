# AI Sales Agent — Local Demo

## Τι είναι αυτό
Αυτόνομο demo του Pre-Sales / After-Sales AI Agent, χωρίς καμία εξάρτηση από το
live eshop σου. Δουλεύει πάνω στο curated dataset Products_AI (422 προϊόντα, 187
κατηγορίες) που είχες ήδη ετοιμάσει.

Καλύπτει τα 3 σενάρια που περιέγραψες:
1. **Order tracking** (mock data προς το παρόν — order IDs: 12345, 99999)
2. **Άμεσο αίτημα προϊόντος** ("θέλω ένα δράπανο") → 3 τιμολογιακές προτάσεις
   (Οικονομική / Καλή σχέση τιμής-ποιότητας / Επαγγελματική) με φωτό + link
3. **Συμβουλευτική πώληση** ("θέλω να κόψω τοίχο") → κάνει διευκρινιστική ερώτηση
   πριν προτείνει

## Τοπικό τρέξιμο (στο δικό σου μηχάνημα)

```bash
cd ai_sales_agent_demo
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Θα ανοίξει αυτόματα στο http://localhost:8501

## Δωρεάν online demo (Streamlit Community Cloud)

1. Ανέβασε τον φάκελο `ai_sales_agent_demo/` σε ένα **δημόσιο GitHub repo**
   (χρειάζεται δωρεάν λογαριασμό GitHub αν δεν έχεις).
2. Πήγαινε στο https://share.streamlit.io και κάνε login με το GitHub σου.
3. "New app" → επίλεξε το repo, branch `main`, main file path `app.py`.
4. Deploy. Σε ~1 λεπτό θα έχεις public link (π.χ. `https://yourapp.streamlit.app`)
   που μπορείς να στείλεις σε οποιονδήποτε — δουλεύει 24/7 δωρεάν χωρίς να
   εξαρτάται από το eshop σου.

## Επόμενα βήματα (μετά το test)
- Σύνδεση του order tracking με το πραγματικό Vouchers Google Sheet (gspread)
- Αντικατάσταση του rule-based intent classifier με πραγματικό LLM
  (Claude ή OpenAI) για πιο φυσική/ευέλικτη συνομιλία
- Ενημέρωση του products_ai.db από το ζωντανό Skroutz XML feed σου
  (μόλις το site είναι πάλι online)
