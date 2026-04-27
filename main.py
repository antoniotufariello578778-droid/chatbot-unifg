from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag import get_rag_response
from scraper import get_professor_info

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

# =============================================
# INTENT DETECTION - Il cervello del chatbot
# =============================================

INTENT_KEYWORDS = {
    "docente": [
        "prof", "professore", "docente", "insegnante", "cattedra",
        "chi insegna", "email prof", "contatto prof", "ricevimento",
        "chi è il prof", "chi tiene il corso"
    ],
    "segreteria": [
        "ticket", "segreteria", "sportello", "ufficio", "apertura",
        "orari segreteria", "supporto", "assistenza", "segnalazione"
    ],
    "esami": [
        "esame", "esami", "prenotazione esame", "appello", "iscrizione esame",
        "verbalizzazione", "voto", "risultato esame", "calendario esami"
    ],
    "certificazioni": [
        "certificazione", "certificato", "riconoscimento", "ecdl", "icdl",
        "ielts", "toefl", "cambridge", "patente europea"
    ],
    "cambio_corso": [
        "cambiare corso", "cambio corso", "passaggio", "trasferimento",
        "cambiare facoltà", "altro corso", "altra laurea"
    ],
    "corsi_laurea": [
        "corso di laurea", "laurea triennale", "laurea magistrale",
        "dipartimento", "facoltà", "offerta formativa", "piano di studi",
        "cfu", "crediti"
    ],
    "tasse": [
        "tasse", "pagamento", "rata", "pagopa", "isee", "borsa di studio",
        "esonero", "riduzione tasse", "adisu"
    ],
    "materiali": [
        "riassunto", "appunti", "materiale", "libro", "testo", "docsity",
        "studiare", "dispense", "slide", "sbobine"
    ],
    "myunifg": [
        "myunifg", "portale", "accesso", "credenziali", "password",
        "login", "account universitario", "problema accesso"
    ],
    "elearning": [
        "elearning", "e-learning", "piattaforma", "moodle", "corso online",
        "materiale corso", "forum"
    ]
}

def detect_intent(question: str) -> str:
    """Rileva l'intento della domanda"""
    q = question.lower()
    
    scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in q)
        if score > 0:
            scores[intent] = score
    
    if not scores:
        return "generale"
    
    return max(scores, key=scores.get)

def get_intent_response(intent: str, question: str) -> dict:
    """Risposta personalizzata per ogni intent"""
    
    if intent == "docente":
        scraper_response = get_professor_info(question)
        return {
            "answer": scraper_response,
            "sources": ["E-Learning Unifg - elearning.unifg.it"]
        }
    
    elif intent == "elearning":
        scraper_response = get_professor_info(question)
        return {
            "answer": scraper_response,
            "sources": ["E-Learning Unifg - elearning.unifg.it"]
        }
    
    else:
        return get_rag_response(question)

# =============================================
# ENDPOINT
# =============================================

@app.get("/")
def home():
    return {"message": "Chatbot Unifg attivo"}

@app.post("/chat")
def chat(question: Question):
    user_question = question.question
    
    intent = detect_intent(user_question)
    result = get_intent_response(intent, user_question)
    
    # Gestiamo sia il caso dict che stringa
    if isinstance(result, dict):
        answer = result.get("answer", "")
        sources = result.get("sources", [])
    else:
        answer = result
        sources = ["Università di Foggia - unifg.it"]
    
    # Aggiungiamo le fonti alla risposta
    if sources:
        fonti_testo = "\n\n📚 Fonti:\n" + "\n".join(f"• {s}" for s in sources)
        risposta_finale = answer + fonti_testo
    else:
        risposta_finale = answer
    
    return {
        "response": risposta_finale,
        "intent": intent
    }