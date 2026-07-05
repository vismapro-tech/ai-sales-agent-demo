from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import re
from agent_core import (
    classify_intent,
    get_clarifying_question,
    recommend_tiered,
    get_order_status,
    build_context_from_history,
    SHOP_PHONE,
)

app = FastAPI(title="AI Sales Agent API", version="1.0")

# Allow requests from Tidio/Make.com
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SHOP_NAME = "Γεωργακόπουλος"
NO_MATCH_MSG = f"Δεν έχω αυτή τη στιγμή ακριβή πρόταση για αυτή την ανάγκη. Μπορείς να καλέσεις το μαγαζί στο **{SHOP_PHONE}** — θα σε βοηθήσουν να βρεις ακριβώς αυτό που ψάχνεις. 📞"


@app.get("/health")
def health():
    """Health check endpoint for Render.com"""
    return {"status": "ok", "service": "AI Sales Agent"}


@app.post("/recommend")
async def recommend(request: Request):
    """
    Main endpoint: chat message from Tidio (+ conversation history) → agent logic → recommendations
    
    Expected JSON:
    {
        "message": "θέλω ένα δράπανο",
        "conversation": [  ← OPTIONAL: full history για καλύτερο context
            {"role": "user", "text": "θέλω δράπανο"},
            {"role": "assistant", "text": "Τι δουλειά;"},
            {"role": "user", "text": "μπετόν"}
        ]
    }
    
    Returns:
    {
        "reply": "...",
        "products": [...],
        "intent": "direct_product|consultative|order_status",
        "shop_phone": "..."
    }
    """
    try:
        data = await request.json()
        user_message = data.get("message", "").strip()
        conversation = data.get("conversation", [])
        
        if not user_message:
            return JSONResponse(
                {"error": "Empty message"},
                status_code=400,
            )
        
        # Συγκεντρώνει ολόκληρο το context από την ιστορία
        full_context = build_context_from_history(conversation)
        search_query = f"{full_context} {user_message}".strip() if full_context else user_message
        
        # Intent classification (βάσει του τρέχοντος μηνύματος, όχι του context)
        intent = classify_intent(user_message)
        
        # Order status query
        if intent == "order_status":
            m = re.search(r"\d{4,}", user_message)
            if m:
                order = get_order_status(m.group())
                if order:
                    reply = f"Η παραγγελία σου είναι: **{order['status']}**"
                    if order.get("tracking"):
                        reply += f". Courier: {order['courier']}, tracking: {order['tracking']}"
                    return JSONResponse({
                        "reply": reply,
                        "products": [],
                        "intent": intent,
                        "shop_phone": SHOP_PHONE,
                    })
                else:
                    return JSONResponse({
                        "reply": "Δεν βρήκα παραγγελία με αυτόν τον αριθμό. Δοκίμασε ξανά ή κάλεσε το μαγαζί.",
                        "products": [],
                        "intent": intent,
                        "shop_phone": SHOP_PHONE,
                    })
            else:
                return JSONResponse({
                    "reply": "Πες μου τον αριθμό παραγγελίας σου.",
                    "products": [],
                    "intent": intent,
                    "shop_phone": SHOP_PHONE,
                })
        
        # Consultative (needs clarification)
        elif intent == "consultative":
            question = get_clarifying_question(user_message)
            return JSONResponse({
                "reply": question,
                "products": [],
                "intent": intent,
                "shop_phone": SHOP_PHONE,
            })
        
        # Direct product search — χρησιμοποιεί full context
        else:
            result = recommend_tiered(search_query)  # ← χρησιμοποιεί το συγκεντρωμένο context
            if result["products"]:
                note = " (από τον πλήρη κατάλογο)" if result.get("source") == "full_catalog" else ""
                reply = f"Βάσει αυτών που μου είπες, να τι προτείνω από την κατηγορία **{result['category']}**{note}:"
                
                # Format products for response
                products_data = [
                    {
                        "tier": p["tier"],
                        "name": p["name"],
                        "brand": p["brand"],
                        "price": round(p["price"], 2),
                        "url": p["url"],
                        "image": p["image"],
                    }
                    for p in result["products"]
                ]
                
                return JSONResponse({
                    "reply": reply,
                    "products": products_data,
                    "intent": intent,
                    "category": result["category"],
                    "shop_phone": SHOP_PHONE,
                })
            else:
                return JSONResponse({
                    "reply": NO_MATCH_MSG,
                    "products": [],
                    "intent": "no_match",
                    "shop_phone": SHOP_PHONE,
                })
    
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500,
        )


@app.post("/clarify")
async def clarify(request: Request):
    """
    Follow-up: full conversation history passed in
    
    Expected JSON:
    {
        "conversation": [
            {"role": "user", "text": "θέλω να κόψω έναν τοίχο"},
            {"role": "assistant", "text": "Τι υλικό;"},
            {"role": "user", "text": "μπετόν"}
        ]
    }
    
    Returns: same as /recommend
    """
    try:
        data = await request.json()
        conversation = data.get("conversation", [])
        
        if not conversation:
            return JSONResponse(
                {"error": "Missing conversation"},
                status_code=400,
            )
        
        # Συγκεντρώνει ολόκληρη την ιστορία
        combined_query = build_context_from_history(conversation)
        
        if not combined_query:
            return JSONResponse(
                {"error": "Empty conversation"},
                status_code=400,
            )
        
        result = recommend_tiered(combined_query)
        
        if result["products"]:
            note = " (από τον πλήρη κατάλογο)" if result.get("source") == "full_catalog" else ""
            reply = f"Τέλεια! Βάσει αυτών, να τι προτείνω από την κατηγορία **{result['category']}**{note}:"
            
            products_data = [
                {
                    "tier": p["tier"],
                    "name": p["name"],
                    "brand": p["brand"],
                    "price": round(p["price"], 2),
                    "url": p["url"],
                    "image": p["image"],
                }
                for p in result["products"]
            ]
            
            return JSONResponse({
                "reply": reply,
                "products": products_data,
                "intent": "direct_product",
                "category": result["category"],
                "shop_phone": SHOP_PHONE,
            })
        else:
            return JSONResponse({
                "reply": NO_MATCH_MSG,
                "products": [],
                "intent": "no_match",
                "shop_phone": SHOP_PHONE,
            })
    
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500,
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
