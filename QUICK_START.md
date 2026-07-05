# ⚡ Quick Start: 5 λεπτά για Deploy

## Τι έχω μέσα;
- `api.py` — FastAPI server (το κύριο)
- `agent_core.py` — Agent logic (δεδομένα + TF-IDF search)
- `products_ai.db`, `tfidf_index_ai.pkl` — Database + index
- `render.yaml` — Render.com configuration
- `render_requirements.txt` — Python dependencies
- `RENDER_DEPLOYMENT_GUIDE.md` — Πλήρες guide

---

## 🚀 Βήμα 1: Ανέβασε τα αρχεία στο GitHub repo

```
github.com/vismapro-tech/ai-sales-agent-demo
```

Κάνε upload στο root:
1. `api.py` ← νέο
2. `agent_core.py` ← αποθήκευση ξανά (ενημερωμένο)
3. `products_ai.db`
4. `tfidf_index_ai.pkl`
5. `render.yaml` ← νέο
6. Μετονομάστε το παλιό `requirements.txt` και ανέβασε τα περιεχόμενα από `render_requirements.txt`

**Commit changes.**

---

## 🎯 Βήμα 2: Signup Render.com

1. `https://render.com`
2. "Sign up with GitHub" → δώσε πρόσβαση
3. Dashboard → "New +" → "Web Service"
4. Επίλεξε repo: `ai-sales-agent-demo`
5. Όνομα: `ai-sales-agent-api`
6. **Build Command:**
   ```
   pip install -r requirements.txt
   ```
7. **Start Command:**
   ```
   uvicorn api:app --host 0.0.0.0 --port 8000
   ```
8. **Instance:** Free
9. "Create Web Service"

Περίμενε ~2-3 λεπτά μέχρι "Live" (πράσινο).

**Πρέπει να δεις URL:** `https://ai-sales-agent-api.onrender.com` (ή παρόμοιο)

---

## ✅ Βήμα 3: Test το API

```bash
curl -X POST https://ai-sales-agent-api.onrender.com/recommend \
  -H "Content-Type: application/json" \
  -d '{"message": "θέλω ένα δράπανο"}'
```

Θα δεις response με προϊόντα. Αν δουλεύει, → Βήμα 4.

---

## 🔌 Βήμα 4: Σύνδεση Make.com

Ανοίγ το scenario "Integration Webhooks" (ή φτιάξε καινούργιο):

1. **HTTP Module** (αν δεν υπάρχει):
   - URL: `https://ai-sales-agent-api.onrender.com/recommend`
   - Method: POST
   - Body:
     ```json
     {
       "message": "{{webhook_data.text}}"
     }
     ```

2. **Tidio Module** (για να στέλνει πίσω):
   - Conversation ID: από webhook
   - Message: από HTTP response

---

## 🎉 Βήμα 5: Test end-to-end

1. Ανοίγ το Tidio chat σου
2. Πληκτρολόγησε: "θέλω ένα δράπανο"
3. Περίμενε 2-3 δευτερόλεπτα
4. Θα δεις: "Βάσει αυτού, να τι προτείνω..." + 3 προϊόντα

---

## 📖 Πλήρες guide

Αν θέλεις περισσότερες λεπτομέρειες → Δες το `RENDER_DEPLOYMENT_GUIDE.md`

---

## 🆘 Common Issues

| Πρόβλημα | Λύση |
|---------|------|
| "Service failed to start" | Κοίτα Render logs → πιθανόν missing DB files |
| "Empty products response" | Test API τοπικά με curl → βλέπε τι επιστρέφει |
| "Tidio doesn't show response" | Check Make.com logs + Tidio API headers |
| Render API is slow | Normal στο free tier — sleep όταν δεν χρησιμοποιείται |

---

## ⏰ Χρόνος setup

- GitHub upload: 2 λεπτά
- Render deploy: 3 λεπτά
- Make.com config: 5 λεπτά
- **Σύνολο: ~10 λεπτά**

🚀
