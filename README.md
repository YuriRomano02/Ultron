# Jarvis

Un piccolo assistente personale da terminale, scritto in Python.
Funziona anche offline, grazie a Ollama.

## Cosa fa

- Risponde a domande e scrive bozze di mail
- Apre app del Mac (es. "apri Safari")
- Salva note in `Documents/Jarvis` (es. "salva una nota: devo comprare il latte")
- Chiede sempre la tua conferma prima di eseguire un'azione

## Cosa serve

- Un Mac con Python 3
- Ollama (si scarica da https://ollama.com/download)
- La libreria Python `openai`

## Installazione

1. Installa Ollama.
2. Scarica un modello:
   ```
   ollama pull llama3.2:3b
   ```
3. Installa la libreria:
   ```
   python3 -m pip install openai
   ```

## Avvio

```
python3 jarvis_azioni.py
```

Scrivi `esci` per chiudere.

## Come personalizzarlo

Apri `ultron.py` e cerca queste parti:

- `SYSTEM`: il nome di Ultron e come deve comportarsi
- `MODEL`: il modello da usare (il nome esatto lo vedi con `ollama list`)
- `PAROLE_AZIONE`: le parole che fanno partire un'azione (apri, salva, nota...)

## Problemi comuni

- **Connection error**: Ollama non è attivo. Apri l'app Ollama.
- **model not found**: scarica il modello con `ollama pull` e controlla il nome con `ollama list`.
- **La prima risposta è lenta**: è normale, il modello deve caricarsi in memoria.

## Nota sulle chiavi

La versione offline non usa nessuna chiave. Se provi un servizio cloud, metti la chiave
in un file `.env` e non condividerlo mai (non caricarlo su GitHub e non incollarlo in chat).
