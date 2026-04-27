import requests
from bs4 import BeautifulSoup

BASE_ELEARNING = "https://elearning.unifg.it"

def get_professor_info(query):
    
    # Estraiamo le parole chiave dalla domanda
    parole_da_ignorare = ["prof", "professore", "docente", "insegnante", "chi", "è",
                          "il", "la", "lo", "di", "del", "della", "come", "contatto",
                          "contatti", "email", "trovare", "trovo", "corso", "unifg",
                          "insegna", "tiene", "chi", "qual", "quale", "quando", "dove",
                          "cosa", "per", "con", "che", "un", "una", "uno", "gli", "le",
                          "mi", "si", "se", "ha", "ho", "hai", "sa", "sai", "può",
                          "puoi", "vorrei", "sapere", "informazioni", "info"]
    
    parole = [p for p in query.lower().split() if p not in parole_da_ignorare and len(p) > 2]
    
    if not parole:
        return "Per cercare un docente visita: https://elearning.unifg.it/course/search.php"
    
    keyword = " ".join(parole[:3])
    
    url = f"{BASE_ELEARNING}/course/search.php?search={keyword.replace(' ', '+')}"
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Cerchiamo i corsi trovati
        corsi = soup.find_all("div", class_="coursename")
        
        if not corsi:
            # Proviamo con un selettore alternativo
            corsi = soup.find_all("h3", class_="coursename")
        
        if not corsi:
            # Ultimo tentativo con tag a
            corsi = soup.find_all("a", href=lambda x: x and "course/view" in str(x))
        
        if corsi:
            risultati = []
            for corso in corsi[:4]:
                testo = corso.get_text().strip()
                link = corso.find("a")
                if link:
                    href = link.get("href", "")
                    risultati.append(f"• {testo}: {href}")
                else:
                    risultati.append(f"• {testo}")
            
            return (f"Ho trovato questi corsi per '{keyword}' su E-Learning Unifg:\n\n" + 
                    "\n".join(risultati) + 
                    f"\n\nPer maggiori dettagli e contatti docenti: {url}")
        
        # Se non trova nulla con lo scraping, risposta utile
        return (f"Non ho trovato risultati specifici per '{keyword}'.\n"
                f"Puoi cercare direttamente su: {url}\n"
                f"oppure su: {BASE_ELEARNING}/course/search.php")
    
    except requests.exceptions.Timeout:
        return f"Il sito E-Learning non risponde. Prova direttamente: {url}"
    
    except Exception as e:
        return (f"Non riesco a contattare E-Learning Unifg in questo momento.\n"
                f"Cerca direttamente qui: {url}")