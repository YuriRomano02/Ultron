import json
import subprocess
from pathlib import Path
from openai import OpenAI, OpenAIError

# Ollama in locale (nessuna chiave). Per un altro servizio cambia base_url,
# api_key e MODEL come negli script precedenti.
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    timeout=180,
    max_retries=0,
)
MODEL = "llama3.2:3b"

# Le note vengono scritte SOLO in questa cartella: quella dove si trova lo script.
CARTELLA_NOTE = Path(__file__).resolve().parent

# I file creati da Ultron vanno in una sottocartella, separata dal codice.
CARTELLA_FILE = CARTELLA_NOTE / "file_creati"
CARTELLA_FILE.mkdir(exist_ok=True)

# Tipi di file che Ultron può creare.
ESTENSIONI_OK = (".txt", ".md", ".csv", ".py")

# Gli strumenti vengono dati al modello SOLO se la tua frase contiene una di
# queste parole. Altrimenti Ultron risponde a parole, come una chat normale.
# Aggiungi qui altri verbi se ti servono.
PAROLE_AZIONE = (
    "apri", "aprimi", "avvia", "lancia",
    "salva", "annota", "appunta", "nota",
    "crea", "creami", "genera",
)


def serve_uno_strumento(testo):
    testo = testo.lower()
    return any(parola in testo for parola in PAROLE_AZIONE)


# ---------- GLI STRUMENTI: funzioni normali che esegue il tuo programma ----------

def apri_app(nome):
    """Apre un'app del Mac (es. Safari, Calculator, Notes)."""
    r = subprocess.run(["open", "-a", nome], capture_output=True, text=True)
    if r.returncode == 0:
        return f"Ho aperto {nome}."
    return f"Non sono riuscito ad aprire {nome}: {r.stderr.strip()}"


def scrivi_nota(nome_file, testo):
    """Aggiunge del testo a un file .txt nella cartella dello script."""
    nome = Path(nome_file).stem or "nota"   # tiene solo il nome, niente percorsi
    percorso = CARTELLA_NOTE / f"{nome}.txt"
    with open(percorso, "a", encoding="utf-8") as f:
        f.write(testo + "\n")
    return f"Ho scritto nel file {percorso}"


def crea_file(nome_file, contenuto):
    """Crea un NUOVO file nella cartella file_creati. Non sovrascrive mai."""
    nome = Path(nome_file).name.lstrip(".")   # niente percorsi, niente file nascosti
    if not nome:
        nome = "nuovo_file"
    percorso = CARTELLA_FILE / nome
    if percorso.suffix.lower() not in ESTENSIONI_OK:
        percorso = percorso.with_name(percorso.name + ".txt")
    if percorso.exists():
        return f"Il file {percorso.name} esiste già e non l'ho toccato. Proponi un altro nome."
    percorso.write_text(contenuto, encoding="utf-8")
    return f"Ho creato il file {percorso}"


FUNZIONI = {
    "apri_app": apri_app,
    "scrivi_nota": scrivi_nota,
    "crea_file": crea_file,
}

# ---------- LA DESCRIZIONE: è ciò che il modello legge per sapere cosa può fare ----------

STRUMENTI = [
    {
        "type": "function",
        "function": {
            "name": "apri_app",
            "description": (
                "Apre un'applicazione sul Mac. Usalo solo se l'utente chiede "
                "esplicitamente di aprire o avviare un'app."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {
                        "type": "string",
                        "description": "Nome dell'app, per esempio Safari o Calculator.",
                    }
                },
                "required": ["nome"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "scrivi_nota",
            "description": (
                "Salva del testo in una nota (file .txt). Usalo solo se l'utente "
                "chiede esplicitamente di salvare o annotare qualcosa."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_file": {
                        "type": "string",
                        "description": "Nome della nota, senza percorso, per esempio appunti.",
                    },
                    "testo": {"type": "string", "description": "Il testo da scrivere."},
                },
                "required": ["nome_file", "testo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crea_file",
            "description": (
                "Crea un nuovo file con il contenuto richiesto. Usalo solo se "
                "l'utente chiede esplicitamente di creare un file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_file": {
                        "type": "string",
                        "description": "Nome del file con estensione, per esempio ciao.txt o riassunto.md.",
                    },
                    "contenuto": {
                        "type": "string",
                        "description": "Il testo completo da scrivere nel file.",
                    },
                },
                "required": ["nome_file", "contenuto"],
            },
        },
    },
]

SYSTEM = """Il tuo nome è Ultron. Sei l'assistente personale di uno studente.
Rispondi in italiano, in modo chiaro e conciso.
Per domande, spiegazioni e conversazione (anche "chi sei" o "come stai")
rispondi normalmente a parole, senza usare strumenti.
Usa gli strumenti solo se l'utente chiede chiaramente di aprire un'app, di
salvare una nota o di creare un file. Non dire mai di aver fatto qualcosa se non hai usato lo
strumento. Se non sai una cosa, dillo invece di inventare."""


def esegui(chiamata):
    """Esegue lo strumento richiesto dal modello, ma SOLO dopo la tua conferma."""
    nome = chiamata.function.name
    try:
        argomenti = json.loads(chiamata.function.arguments)
    except json.JSONDecodeError:
        return "Argomenti non validi."
    if nome not in FUNZIONI:
        return "Strumento sconosciuto."

    print(f"\n[Ultron vuole eseguire: {nome} {argomenti}]")
    if input("Confermi? (s/n): ").strip().lower() != "s":
        return "L'utente ha rifiutato l'azione."
    try:
        return FUNZIONI[nome](**argomenti)
    except Exception as e:
        return f"Errore durante l'azione: {e}"


history = [{"role": "system", "content": SYSTEM}]

print("Ultron pronto. Scrivi 'esci' per chiudere.")

while True:
    domanda = input("\nTu: ").strip()
    if domanda.lower() in ("esci", "exit", "quit"):
        break
    if not domanda:
        continue

    inizio = len(history)
    history.append({"role": "user", "content": domanda})
    print("Ultron sta pensando...")

    # Gli strumenti si passano al modello solo se la frase chiede un'azione.
    extra = {"tools": STRUMENTI} if serve_uno_strumento(domanda) else {}

    try:
        for _ in range(5):  # al massimo 5 giri di "chiedo uno strumento, ricevo il risultato"
            risposta = client.chat.completions.create(
                model=MODEL,
                messages=history,
                **extra,
            )
            msg = risposta.choices[0].message

            if not msg.tool_calls:
                history.append({"role": "assistant", "content": msg.content})
                print(f"\nUltron: {msg.content}")
                break

            # Il modello ha chiesto uno o più strumenti: li eseguiamo e gli rimandiamo i risultati.
            history.append(
                {
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": c.id,
                            "type": "function",
                            "function": {
                                "name": c.function.name,
                                "arguments": c.function.arguments,
                            },
                        }
                        for c in msg.tool_calls
                    ],
                }
            )
            for c in msg.tool_calls:
                risultato = esegui(c)
                history.append(
                    {"role": "tool", "tool_call_id": c.id, "content": risultato}
                )
        else:
            print("\nUltron: mi sono fermato dopo troppi tentativi.")
    except OpenAIError as e:
        print(f"\nErrore: {e}")
        del history[inizio:]  # annulla questo turno, così puoi riprovare
