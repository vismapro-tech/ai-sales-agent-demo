# Make.com Setup: Conversation History Passing

## 📌 Τι χρειάζεται

Το Make.com θα πρέπει να συγκεντρώνει **ΟΛΟ** το conversation history από το Tidio και να το στέλνει στο API μας σε κάθε request.

---

## 🔧 Βήμα 1: Στο Tidio — Κατά την αποθήκευση ιστορίας

Κάθε μήνυμα που σε ζητάει το Tidio θα πρέπει να έχει:
- Το μήνυμα του πελάτη (`message`)
- **Ολόκληρη την ιστορία** (`conversation`)

Παράδειγμα payload που θα στέλνει το Tidio:

```json
{
  "conversationId": "conv_12345",
  "message": "μπετόν",
  "conversation": [
    {
      "role": "user",
      "text": "θέλω δράπανο"
    },
    {
      "role": "assistant",
      "text": "Τι δουλειά θέλεις να κάνεις;"
    },
    {
      "role": "user",
      "text": "μπετόν και τούβλο"
    },
    {
      "role": "assistant",
      "text": "Μπαταρία ή ρεύμα;"
    },
    {
      "role": "user",
      "text": "μπαταρία"
    }
  ]
}
```

---

## 🔌 Βήμα 2: Στο Make.com — HTTP Module

**Setup του HTTP request:**

### URL
```
POST https://ai-sales-agent-api.onrender.com/recommend
```

### Headers
```
Content-Type: application/json
```

### Body
```json
{
  "message": "{{1.message}}",
  "conversation": "{{1.conversation}}"
}
```

**Όπου:**
- `{{1.message}}` = το τρέχον μήνυμα από το Tidio webhook
- `{{1.conversation}}` = ολόκληρη η ιστορία (array με όλα τα μηνύματα)

---

## ✅ Τι επιστρέφει το API

```json
{
  "reply": "Τέλεια! Βάσει αυτών, να τι προτείνω...",
  "products": [
    {
      "tier": "Οικονομική επιλογή",
      "name": "Bosch GSB 12V-15",
      "brand": "Bosch",
      "price": 89.99,
      "url": "https://...",
      "image": "https://..."
    },
    ...
  ],
  "intent": "direct_product",
  "category": "Δράπανα Μπαταρίας",
  "shop_phone": "210 574 1109"
}
```

---

## 🎯 Make.com → Tidio Response

Το **Send Chat Message** module (ή αντίστοιχο) θα λάβει το response και θα το στείλει πίσω:

```
{{2.reply}}

Εναλλακτικές:
{{#each 2.products}}
• {{this.tier}}: {{this.name}} — €{{this.price}} [Link]({{this.url}})
{{/each}}

📞 {{2.shop_phone}}
```

---

## ⚠️ Important Notes

1. **Conversation format:** Το array πρέπει να έχει σωστή μορφή JSON με `role` (user/assistant) και `text`
2. **Order matters:** Η σειρά των μηνυμάτων πρέπει να είναι χρονολογική (παλιά → νέα)
3. **Tide history limit:** Αν το conversation έχει 50+ μηνύματα, σκέψου να στέλνεις μόνο τα τελευταία 10 για faster processing

---

## 🔄 Alternative: Όταν δεν υπάρχει full history

Αν το Tidio δεν μπορεί να στείλει ολόκληρη την ιστορία, μπορείς να στείλεις μόνο τα βασικά:

```json
{
  "message": "{{1.message}}"
}
```

Αλλά **δεν θα έχει context** από τις προηγούμενες ερωτήσεις/απαντήσεις — θα κάνει μια καθαρή αναζήτηση.

---

## 🧪 Test

Στο Make.com, πριν την ολοκλήρωση, πάτα **"Test"** και δες:

1. Η HTTP κλήση να επιστρέφει 200 OK
2. Τα products να φαίνονται στο response
3. Το Tidio να εμφανίζει το μήνυμα + προϊόντα σωστά
