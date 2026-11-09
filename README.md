# rag-noter

Et lille projekt, hvor jeg kan stille spørgsmål til mine egne studienoter. Systemet finder de relevante sider i mine PDF'er og lader en lokal sprogmodel svare ud fra dem, med henvisning til fil og sidetal.

Projektet er lavet for at forstå, hvordan Retrieval-Augmented Generation (RAG) fungerer i praksis, og hvad der påvirker kvaliteten af svarene.

## Sådan virker det

1. **Indlæsning** (`ingest.py`): PDF'erne i `data/` læses side for side og deles i overlappende tekststykker (chunks).
2. **Embeddings**: Hvert stykke omdannes til en vektor og gemmes i ChromaDB sammen med filnavn og sidetal.
3. **Søgning** (`ask.py`): Spørgsmålet omdannes også til en vektor, og de fire mest lignende stykker hentes frem.
4. **Svar**: Stykkerne sendes sammen med spørgsmålet til en lokal model via Ollama, som svarer ud fra konteksten og angiver kilderne.

Alt kører lokalt. Ingen noter forlader computeren.

## Teknologi

- Python
- ChromaDB (vektordatabase)
- pypdf (tekstudtræk fra PDF)
- Ollama med `llama3.2` (lokal sprogmodel)
- Udviklet i Ubuntu under WSL

## Kom i gang

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Installer Ollama og hent modellen
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```

Læg nogle PDF'er i `data/`, og byg databasen:

```bash
python ingest.py
```

Stil et spørgsmål:

```bash
python ask.py "What is SSE and how is it used in gradient descent?"
```

Eller se kun hvilke tekststykker, der bliver fundet, uden at spørge modellen:

```bash
python ask.py --retrieve-only "SSE"
```

## Hvad jeg har lært

- **Vektorsøgning matcher på betydning.** En søgning på "SSE" fandt også en side, der kun skrev "sum of squared errors" ud.
- **Promptens sprog styrer svarets sprog.** Med en dansk prompt-skabelon svarede modellen på dansk, også på engelske spørgsmål. Efter jeg skrev prompten på engelsk og bad den svare på spørgsmålets sprog, blev svarene bedre.
- **Små modeller er svage på dansk.** `llama3.2` (3B) svarer mærkbart bedre på engelsk og finder til tider på danske ord.
- **Støj i kildematerialet fylder.** Slides gentager den samme menulinje øverst på hver side, og den kommer med i alle chunks.

## Næste skridt

- En simpel chat-brugerflade med Streamlit
- En flersproget embedding-model, så danske noter søges bedre
- Fjerne gentagne overskrifter og menulinjer fra slides
- En lille evaluering med kendte spørgsmål og svar for at sammenligne chunk-størrelser
