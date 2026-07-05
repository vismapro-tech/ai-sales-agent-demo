import sqlite3
import pickle
import re
from sklearn.metrics.pairwise import cosine_similarity

DB = "products_ai.db"
INDEX_FILE = "tfidf_index_ai.pkl"

with open(INDEX_FILE, "rb") as f:
    _idx = pickle.load(f)

_ids = _idx["ids"]
_vectorizer = _idx["vectorizer"]
_matrix = _idx["matrix"]

TIER_LABELS = ["Οικονομική επιλογή", "Καλή σχέση ποιότητας/τιμής", "Επαγγελματική επιλογή"]


def _best_category(query: str, top_n_categories: int = 1):
    """Find the best matching category (or categories) for a free-text need."""
    q_vec = _vectorizer.transform([query])
    sims = cosine_similarity(q_vec, _matrix).flatten()
    ranked = sorted(zip(_ids, sims), key=lambda x: x[1], reverse=True)
    top_ids = [pid for pid, score in ranked if score > MIN_RELEVANCE_THRESHOLD][:15]
    if not top_ids:
        return []

    score_by_id = dict(ranked)
    conn = sqlite3.connect(DB)
    placeholders = ",".join("?" * len(top_ids))
    rows = conn.execute(
        f"SELECT id, category FROM products_ai WHERE id IN ({placeholders})", top_ids
    ).fetchall()
    conn.close()

    # Weight by relevance score, not raw frequency, so a single strong match
    # beats several weak matches from an unrelated category.
    from collections import defaultdict
    cat_scores = defaultdict(float)
    for pid, cat in rows:
        cat_scores[cat] += score_by_id.get(pid, 0)

    ranked_cats = sorted(cat_scores.items(), key=lambda x: x[1], reverse=True)
    return [c for c, _ in ranked_cats[:top_n_categories]]


def recommend_tiered(query: str, max_price: float | None = None):
    """Core Pre-Sales function: find best category for the need, return
    up to 3 products (cheap/medium/expensive) with photo + link."""
    categories = _best_category(query)
    if not categories:
        return {"category": None, "products": []}

    category = categories[0]
    conn = sqlite3.connect(DB)
    sql = """SELECT id, name, brand, final_price_vat, quantity, stock_status,
                     product_url, image, use_case
              FROM products_ai WHERE category = ? AND quantity > 0"""
    params = [category]
    if max_price is not None:
        sql += " AND final_price_vat <= ?"
        params.append(max_price)
    sql += " ORDER BY final_price_vat ASC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    products = []
    for i, r in enumerate(rows[:3]):
        tier = TIER_LABELS[i] if len(rows[:3]) == 3 else ("Προτεινόμενο" if len(rows) == 1 else TIER_LABELS[i])
        products.append({
            "tier": tier,
            "id": r[0], "name": r[1], "brand": r[2], "price": r[3],
            "quantity": r[4], "stock_status": r[5],
            "url": r[6], "image": r[7], "use_case": r[8],
        })

    return {"category": category, "products": products}


# --- Intent classification (rule-based fallback; swap for LLM when API key available) ---

ORDER_PATTERNS = [r"παραγγελ", r"\border\b", r"tracking", r"απεστ", r"κατάσταση.*παραγγελ"]
VAGUE_NEED_PATTERNS = [
    r"θέλω να (κόψω|τρυπήσω|σπάσω|καθαρίσω|βάψω|λειάν|τρίψω|γυαλίσω|βιδώσω|ξεβιδώσω|στερεώσω|σφίξω|μετρήσω)",
    r"χρειάζομαι κάτι (για|να)",
    r"τι μου προτείνετε",
    r"ψάχνω κάτι",
    r"\bτοίχο\b|\bτοίχους\b|\bτούβλο\b|\bπλακάκι\b",
]

MIN_RELEVANCE_THRESHOLD = 0.08


def classify_intent(message: str) -> str:
    msg = message.lower()
    for pat in ORDER_PATTERNS:
        if re.search(pat, msg):
            return "order_status"
    for pat in VAGUE_NEED_PATTERNS:
        if re.search(pat, msg):
            return "consultative"
    return "direct_product"


CLARIFYING_QUESTIONS = {
    "κόψω": "Τι υλικό θέλεις να κόψεις — μπετόν, πέτρα, μέταλλο ή ξύλο; Και είναι για επαγγελματική ή οικιακή χρήση;",
    "τρυπήσω": "Σε τι υλικό θα τρυπήσεις — τοίχο/μπετόν, μέταλλο ή ξύλο; Μπαταρία ή ρεύμα προτιμάς;",
    "default": "Πες μου λίγο περισσότερο για τη δουλειά που θέλεις να κάνεις (υλικό, συχνότητα χρήσης, επαγγελματική ή οικιακή), για να σου προτείνω το κατάλληλο εργαλείο.",
}


def get_clarifying_question(message: str) -> str:
    msg = message.lower()
    for kw, q in CLARIFYING_QUESTIONS.items():
        if kw != "default" and kw in msg:
            return q
    return CLARIFYING_QUESTIONS["default"]


# Mock order data — swap with gspread call to the real Vouchers sheet later
MOCK_ORDERS = {
    "12345": {"status": "Απεστάλη", "courier": "ELTA Courier", "tracking": "EL123456789GR"},
    "99999": {"status": "Σε επεξεργασία", "courier": None, "tracking": None},
}


def get_order_status(order_id: str):
    return MOCK_ORDERS.get(order_id.strip())


if __name__ == "__main__":
    tests = [
        "θέλω να κόψω έναν τοίχο από μπετόν",
        "θέλω ένα δράπανο",
        "ψάχνω γεννήτρια βενζίνης μέχρι 450 ευρώ",
        "πού είναι η παραγγελία μου 12345;",
    ]
    for t in tests:
        intent = classify_intent(t)
        print(f"\n>>> '{t}'  ->  intent: {intent}")
        if intent == "consultative":
            print("   Ερώτηση:", get_clarifying_question(t))
        elif intent == "order_status":
            m = re.search(r"\d{4,}", t)
            if m:
                print("   Order:", get_order_status(m.group()))
        else:
            res = recommend_tiered(t)
            print("   Κατηγορία:", res["category"])
            for p in res["products"]:
                print(f"   [{p['tier']}] {p['name'][:60]} — €{p['price']:.2f} — {p['url']}")
