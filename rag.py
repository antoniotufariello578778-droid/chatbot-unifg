from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Cliente Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Modello per creare embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Documenti reali dell'università
documents = [
    # SEGRETERIA E TICKET
    "Per aprire un ticket alla segreteria studenti bisogna accedere al portale MyUnifg su myunifg.unifg.it, andare nella sezione 'Supporto' e cliccare su 'Nuovo ticket'.",
    "La segreteria studenti dell'Università di Foggia si trova in Via Gramsci 89-91, Foggia. Orari: lunedì, mercoledì e venerdì 10:00-12:00, martedì e giovedì 15:00-17:00.",
    "Per contattare la segreteria studenti via email scrivere a segreteria.studenti@unifg.it oppure chiamare il numero 0881 338111.",
    "Per problemi con la carriera universitaria, pagamento tasse, o iscrizione agli esami aprire un ticket su MyUnifg nella sezione Supporto.",

    # CERTIFICAZIONI
    "Per il riconoscimento delle certificazioni linguistiche come IELTS, TOEFL o Cambridge bisogna compilare il modulo su MyUnifg e allegare copia della certificazione originale.",
    "Le certificazioni informatiche riconosciute dall'Università di Foggia includono ECDL e ICDL. Per il riconoscimento presentare domanda in segreteria con copia del certificato.",
    "Il riconoscimento delle certificazioni avviene tramite delibera del consiglio di corso di studi. I tempi medi sono 30-60 giorni.",
    "Per certificazioni estere è necessaria la traduzione giurata in italiano prima di presentare domanda di riconoscimento.",

    # CAMBIO CORSO
    "Per cambiare corso di studi bisogna presentare domanda alla segreteria studenti tramite MyUnifg entro le scadenze dell'ateneo, solitamente entro dicembre.",
    "Il passaggio ad altro corso di studi prevede una valutazione degli esami già sostenuti per eventuale riconoscimento dei crediti CFU.",
    "Per il cambio corso di studi è necessario compilare il modulo disponibile su MyUnifg nella sezione 'Domande e Istanze'.",
    "Il trasferimento da un altro ateneo all'Università di Foggia richiede domanda entro luglio/agosto. Informazioni su unifg.it nella sezione Ammissioni.",

    # CORSI DI LAUREA
    "L'Università degli Studi di Foggia offre corsi di laurea triennale, magistrale e magistrale a ciclo unico.",
    "Il Dipartimento di Economia dell'Università di Foggia offre corsi in Economia Aziendale, Economia e Management, Scienze Economiche.",
    "Il Dipartimento di Giurisprudenza offre la laurea magistrale a ciclo unico in Giurisprudenza della durata di 5 anni.",
    "Il Dipartimento di Medicina e Chirurgia offre il corso di laurea magistrale a ciclo unico in Medicina e Chirurgia della durata di 6 anni.",
    "Il Dipartimento di Agraria offre corsi in Scienze e Tecnologie Agrarie e Scienze Forestali.",
    "Il Dipartimento di Studi Umanistici offre corsi in Lettere, Scienze della Formazione e Beni Culturali.",
    "Per informazioni dettagliate sui piani di studio visitare il sito unifg.it nella sezione Didattica e scegliere il proprio corso.",

    # CONTATTI DOCENTI
    "I contatti dei professori e docenti sono disponibili sulla piattaforma E-Learning di Unifg all'indirizzo elearning.unifg.it.",
    "Per trovare l'email di un professore visitare la pagina del corso su E-Learning Unifg oppure la sezione Docenti su unifg.it.",
    "Su elearning.unifg.it ogni docente ha una pagina personale con email istituzionale, orari di ricevimento e materiali del corso.",
    "Per contattare un professore tramite email usare sempre l'indirizzo istituzionale nome.cognome@unifg.it oppure cercare su elearning.unifg.it.",

    # MYUNIFG
    "MyUnifg è il portale studenti dell'Università di Foggia accessibile su myunifg.unifg.it con le credenziali universitarie.",
    "Su MyUnifg è possibile: iscriversi agli esami, visualizzare la carriera universitaria, pagare le tasse, aprire ticket alla segreteria.",
    "Le credenziali MyUnifg vengono fornite al momento dell'immatricolazione. In caso di problemi di accesso contattare il supporto informatico.",
    "La piattaforma E-Learning di Unifg è disponibile su elearning.unifg.it e contiene i materiali dei corsi, forum e contatti dei docenti.",

    # ESAMI
    "Per prenotarsi agli esami bisogna accedere a MyUnifg, andare nella sezione Esami e selezionare l'appello desiderato entro la scadenza.",
    "I risultati degli esami vengono pubblicati su MyUnifg dal docente entro 30 giorni dalla data dell'esame.",
    "Per verbalizzare un esame il docente inserisce il voto su MyUnifg. Lo studente riceve una notifica via email.",
    "Per richiedere il certificato di laurea o di iscrizione bisogna fare richiesta tramite MyUnifg nella sezione Certificati.",

    # TASSE
    "Le tasse universitarie si pagano tramite il sistema PagoPA accessibile da MyUnifg. Le scadenze sono indicate sul portale.",
    "Per problemi con i pagamenti delle tasse universitarie aprire un ticket su MyUnifg o contattare l'ufficio contabilità.",
    "Gli studenti con ISEE basso possono richiedere la riduzione delle tasse universitarie tramite domanda su MyUnifg.",
    "Le borse di studio dell'Università di Foggia sono gestite da ADISU Puglia. Informazioni su adisupuglia.it.",

    # DOCSITY
    "Per trovare riassunti e appunti sui libri di testo universitari puoi consultare Docsity su docsity.com cercando il nome del corso.",
    "Su Docsity è possibile trovare riassunti, schemi e appunti per la maggior parte dei corsi universitari italiani in modo gratuito.",
    "Per cercare materiali su Docsity vai su docsity.com, clicca su 'Cerca' e inserisci il nome del corso o del libro di testo.",
]

# Creiamo gli embeddings
embeddings = model.encode(documents)
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

def get_rag_response(question):
    question_embedding = model.encode([question])
    D, I = index.search(np.array(question_embedding), k=2)

    contexts = [documents[I[0][i]] for i in range(2)]
    context = "\n".join(contexts)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Sei un assistente virtuale dell'Università degli Studi di Foggia. Rispondi in italiano in modo chiaro, preciso e utile agli studenti. Usa solo le informazioni fornite nel contesto. Se non hai abbastanza informazioni suggerisci di visitare unifg.it o myunifg.unifg.it."
            },
            {
                "role": "user",
                "content": f"Contesto:\n{context}\n\nDomanda: {question}"
            }
        ],
        temperature=0.3,
        max_tokens=500
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": ["Università di Foggia - unifg.it", "MyUnifg - myunifg.unifg.it"]
    }