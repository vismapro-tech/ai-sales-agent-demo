# Deployment Guide: FastAPI AI Agent → Render.com → Make.com → Tidio

## 🎯 Στόχος
Να κάνουμε deploy το FastAPI server μας στο Render.com (δωρεάν, 24/7), ώστε το Make.com να μπορεί να του κάνει κλήσεις από το Tidio χωρίς ngrok.

---

## 📋 Προαπαιτούμενα
- [ ] GitHub account (δωρεάν)
- [ ] Render.com account (δωρεάν)
- [ ] Το repo σου `vismapro-tech/ai-sales-agent-demo` με τα αρχεία

---

## 🔧 Βήμα 1: Προετοιμασία αρχείων στο GitHub

Τα παρακάτω αρχεία πρέπει να υπάρχουν στο root του repo σου:

```
vismapro-tech/ai-sales-agent-demo/
├── api.py                    ← NEW: FastAPI server
├── agent_core.py             ← ήδη υπάρχει
├── products_ai.db            ← ήδη υπάρχει
├── tfidf_index_ai.pkl        ← ήδη υπάρχει
├── products.db               ← ήδη υπάρχει
├── tfidf_index.pkl           ← ήδη υπάρχει
├── requirements.txt          ← αλλάξ'το σε αυτό που είναι στο guide
├── render.yaml               ← NEW
└── README.md
```

**Ενέργειες:**
1. Άνοιξε `github.com/vismapro-tech/ai-sales-agent-demo`
2. "Add file" → "Upload files"
3. Ανέβασε τα **νέα αρχεία**: `api.py` και `render.yaml`
4. **Άλλαξε το `requirements.txt`** (delete παλιό, upload το νέο με fastapi + uvicorn)
5. Commit changes

---

## 🚀 Βήμα 2: Signup + Connect στο Render.com

1. Πήγαινε στο `https://render.com`
2. "Sign up" → GitHub (click "Continue with GitHub")
3. Δώσε πρόσβαση στο account σου
4. Στο Render dashboard, πάτα **"New +"** → **"Web Service"**
5. Επίλεξε το repo: `ai-sales-agent-demo`
6. Συμπλήρωσε:
   - **Name:** `ai-sales-agent-api`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api:app --host 0.0.0.0 --port 8000`
   - **Instance Type:** Free
7. Πάτα **"Create Web Service"**

Περιμένει ~2-3 λεπτά να κάνει deploy. Μόλις δεις "Live" (πράσινο), είναι έτοιμο!

**Το URL σου θα είναι κάτι σαν:** `https://ai-sales-agent-api.onrender.com`

---

## ✅ Βήμα 3: Test το API τοπικά

Πρώτα δοκίμασε το API τοπικά:

```bash
cd ~/ai-sales-agent-demo
pip install fastapi uvicorn
python api.py
```

Μετά δοκίμασε ένα request (σε άλλο terminal):

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"message": "θέλω ένα δράπανο"}'
```

Θα πρέπει να δεις response με προϊόντα + σχέδια.

---

## 🔌 Βήμα 4: Σύνδεση Make.com με το Render API

### Δημιουργία νέου scenario στο Make.com

1. Πήγαινε στο Make.com → "Create Scenario"
2. Trigger: **Webhook** → "Custom Webhook"
3. Στο webhook module:
   - Πάτα "Determine data structure"
   - Δες το webhook URL που σε δίνει Make.com (κάτι σαν `https://hook.eu1.make.com/xxxxx`)
   - **Αντίγραψε αυτό το URL** (θα το δώσεις στο Tidio)

### Πρόσθεσε HTTP Module

4. Πάτα "+" → Add module → **HTTP** → **Make a request**
5. **Method:** POST
6. **URL:** `https://ai-sales-agent-api.onrender.com/recommend` (or `/clarify`)
7. **Headers:**
   ```
   Content-Type: application/json
   ```
8. **Body:**
   ```json
   {
     "message": "{{1.text}}"
   }
   ```
   (το `{{1.text}}` παίρνει το μήνυμα από το webhook)

9. **Output:** Πάτα "Determine output structure" → δώσε δείγμα response (copy από το curl test πάνω)

### Πρόσθεσε Tidio module

10. Πάτα "+" → Add module → **Tidio** → **Send Chat Message** (ή όποιο module έχει)
11. **Conversation ID:** από το webhook payload (`{{1.conversationId}}`)
12. **Text:** Χρησιμοποίησε το response από το HTTP module:
    ```
    {{2.reply}}
    
    {{#if 2.products}}
    Επιλογές:
    {{#each 2.products}}
    - {{this.tier}}: {{this.name}} — €{{this.price}}
    [Δες περισσότερα]({{this.url}})
    {{/each}}
    {{/if}}
    ```

---

## 🎯 Βήμα 5: Σύνδεση Tidio με Make.com Webhook

1. Άνοιξε το Tidio Flow builder σου
2. Δημιούργησε ένα node: **Chat → API Call (HTTP)**
3. **URL:** Το webhook URL που αντίγραψες από το Make.com
4. **Method:** POST
5. **Body:**
   ```json
   {
     "text": "{{message}}",
     "conversationId": "{{conversation.id}}"
   }
   ```

Τώρα:
- Πελάτης πληκτρολογεί στο Tidio
- Tidio στέλνει μήνυμα στο Make.com webhook
- Make.com καλεί το `/recommend` endpoint σου στο Render
- Το API σου επιστρέφει προϊόντα
- Make.com στέλνει πίσω στο Tidio
- Tidio εμφανίζει την απάντηση

---

## 🐛 Troubleshooting

### "Service failed to start"
Κοίτα το Render logs:
1. Render dashboard → web service → "Logs"
2. Ψάξε για error messages
3. Πιθανή αιτία: missing database files (`products_ai.db`, `tfidf_index_ai.pkl`) — βεβαιώσου ότι είναι στο repo

### "API returns empty products"
1. Test το API τοπικά (curl command πάνω)
2. Δες τι επιστρέφει στο Make.com logs
3. Πιθανή αιτία: λάθος intent classification ή πολύ αδύναμο TF-IDF match

### "Tidio doesn't show response"
1. Έλεγξε τα Make.com logs (history tab του scenario)
2. Βεβαιώσου ότι το Tidio API module έχει τα σωστά headers (Content-Type: application/json)

---

## 📞 API Endpoints Reference

### POST `/recommend`
Input:
```json
{"message": "θέλω ένα δράπανο"}
```

Output:
```json
{
  "reply": "Βάσει αυτού...",
  "products": [
    {
      "tier": "Οικονομική επιλογή",
      "name": "...",
      "brand": "...",
      "price": 99.99,
      "url": "...",
      "image": "..."
    }
  ],
  "intent": "direct_product",
  "category": "Δράπανα",
  "shop_phone": "210 574 1109"
}
```

### POST `/clarify`
Input:
```json
{
  "original_need": "θέλω να κόψω τοίχο",
  "clarification": "μπετόν, επαγγελματική"
}
```

Output: ίδιο με `/recommend`

### GET `/health`
Απλό health check για Render.

---

## ✨ Bonus: Monitoring

Στο Render dashboard, μπορείς να δεις:
- CPU/Memory usage
- Logs
- Redeploy history
- Custom domains (αν θέλεις να αλλάξεις το URL)

---

## 🎉 Δεν χρειάζεται περισσότερα!

Όταν ολοκληρωθούν τα πάντα, έχεις:
- ✅ FastAPI running 24/7 στο Render
- ✅ Make.com calls → Agent Logic → Recommendations
- ✅ Tidio Users chat naturally, get smart suggestions
- ✅ No ngrok, no local server needed
