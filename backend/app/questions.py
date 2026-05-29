"""
Definizione bilingue (IT/EN) dei questionari PRAXIS.

Replica esatta dello strumento originale (studenti + insegnanti, 2024) per
consentire il confronto longitudinale. Le chiavi (`key`) coincidono con le
etichette sintetiche di `analisi_praxis_python/question_mapping.py` del
progetto CNR-articolo-quantitativo, cosi' i dati raccolti qui sono
direttamente comparabili con il dataset originale.

Dimensioni PRAXIS:
  profile  -> anagrafica (non PRAXIS)
  P        -> Practice patterns
  R        -> Readiness beliefs (competenza)
  A        -> Adequacy & support (formazione)
  X        -> eXpectations (impatto atteso)
  I        -> Interpersonal trust (fiducia)
  S        -> Skepticisms (preoccupazioni)

Tipi domanda (type):
  likert    -> scala 1-7 con ancore testuali
  number    -> numero (ore/eta')
  boolean   -> Si'/No
  single    -> scelta singola
  multi     -> scelta multipla
  text      -> testo libero
"""

# Set di ancore Likert riutilizzati (it/en) -------------------------------

ANCHORS = {
    "intensita": {
        "it": ["Per niente", "Poco", "Moderatamente", "Neutrale",
               "Piuttosto", "Molto", "Estremamente"],
        "en": ["Not at all", "Slightly", "Moderately", "Neutral",
               "Fairly", "Very", "Extremely"],
    },
    "fiducia": {
        "it": ["Per niente fiducioso", "Poco fiducioso", "Moderatamente fiducioso",
               "Neutrale", "Piuttosto fiducioso", "Molto fiducioso", "Estremamente fiducioso"],
        "en": ["Not at all confident", "Slightly confident", "Moderately confident",
               "Neutral", "Fairly confident", "Very confident", "Extremely confident"],
    },
    "preoccupazione": {
        "it": ["Per niente preoccupato", "Poco preoccupato", "Moderatamente preoccupato",
               "Neutrale", "Piuttosto preoccupato", "Molto preoccupato", "Estremamente preoccupato"],
        "en": ["Not at all worried", "Slightly worried", "Moderately worried",
               "Neutral", "Fairly worried", "Very worried", "Extremely worried"],
    },
}


def _likert(key, dim, it, en, anchor="intensita", note_it=None, note_en=None):
    return {
        "key": key, "dimension": dim, "type": "likert",
        "scale_min": 1, "scale_max": 7,
        "anchors": ANCHORS[anchor],
        "label": {"it": it, "en": en},
        "note": {"it": note_it, "en": note_en},
        "required": True,
    }


def _q(key, dim, qtype, it, en, **kw):
    base = {
        "key": key, "dimension": dim, "type": qtype,
        "label": {"it": it, "en": en},
        "note": {"it": kw.get("note_it"), "en": kw.get("note_en")},
        "required": kw.get("required", True),
    }
    if "options" in kw:
        base["options"] = kw["options"]
    if qtype == "number":
        base["min"] = kw.get("min", 0)
        base["max"] = kw.get("max")
    return base


def _opts(pairs):
    """pairs: list of (it, en) -> [{value, label{it,en}}]"""
    return [{"value": it, "label": {"it": it, "en": en}} for it, en in pairs]


# === STUDENTI ============================================================

STUDENTI = [
    _q("Codice_Anonimo", "profile", "text",
       "Inserisci un codice di 6 caratteri costituito dalle ultime 4 lettere del cognome di tua madre, seguite dal suo giorno di nascita nel formato gg (es.: se il cognome e' Greco e il giorno di nascita e' il 3, scrivi reco03).",
       "Enter a 6-character code made of the last 4 letters of your mother's surname followed by her day of birth as dd (e.g. if the surname is Greco and the birthday is the 3rd, write reco03)."),
    _q("Eta_Num", "profile", "number",
       "Quanti anni hai? (scrivi un numero, es.: 29)",
       "How old are you? (write a number, e.g. 29)", min=10, max=99),
    _q("Genere", "profile", "single", "Il tuo genere e'", "Your gender is",
       options=_opts([("Femmina", "Female"), ("Maschio", "Male"),
                      ("Altro o preferisco non specificare", "Other or prefer not to say")])),
    _q("Scuola_Freq", "profile", "single", "Che scuola frequenti?", "Which school do you attend?",
       options=_opts([
           ("Secondaria di primo grado", "Lower secondary school"),
           ("Secondaria di secondo grado", "Upper secondary school"),
           ("Universita' triennale", "Bachelor's degree"),
           ("Universita' - magistrale o a ciclo unico", "Master's / single-cycle degree"),
           ("Specializzazione post laurea / Master / Dottorato di ricerca", "Postgraduate / Master / PhD")])),
    _q("Titolo_Studio", "profile", "single", "Titolo di studio", "Educational qualification",
       options=_opts([
           ("Licenza media superiore", "Upper secondary diploma"),
           ("Laurea triennale", "Bachelor's degree"),
           ("Laurea magistrale o a ciclo unico", "Master's / single-cycle degree"),
           ("Specializzazione post laurea / Master / Dottorato di ricerca", "Postgraduate / Master / PhD")])),
    _q("Tipo_Percorso", "profile", "single",
       "Il tuo percorso attuale di studio e' di tipo", "Your current field of study is",
       required=False,
       options=_opts([("STEM (Science, Technology, Engineering, Mathematics)", "STEM (Science, Technology, Engineering, Mathematics)"),
                      ("umanistico", "Humanities")])),

    _likert("Comp_Pratica", "R",
            "Su una scala da 1 a 7, quanto ti consideri competente nell'uso pratico di strumenti o tecnologie legati all'intelligenza artificiale?",
            "On a scale from 1 to 7, how competent do you consider yourself in the practical use of AI tools or technologies?",
            note_it="Con \"uso pratico\" intendiamo la capacita' di utilizzare concretamente strumenti, applicazioni o piattaforme di IA.",
            note_en="By \"practical use\" we mean the ability to concretely use AI tools, apps or platforms."),
    _likert("Comp_Teorica", "R",
            "Su una scala da 1 a 7, quanto ritieni adeguata la tua competenza teorica riguardo l'intelligenza artificiale?",
            "On a scale from 1 to 7, how adequate is your theoretical competence about AI?",
            note_it="Con \"competenza teorica\" si intende la conoscenza dei principi, concetti e modelli fondamentali dell'IA.",
            note_en="By \"theoretical competence\" we mean knowledge of the fundamental principles, concepts and models of AI."),
    _likert("Impatto_Studio", "X",
            "Su una scala da 1 a 7, quanto pensi che l'intelligenza artificiale cambiera' il tuo modo di studiare?",
            "On a scale from 1 to 7, how much do you think AI will change the way you study?"),
    _likert("Formazione_Adeguata", "A",
            "Su una scala da 1 a 7, quanto ritieni adeguata la formazione ricevuta in merito all'intelligenza artificiale?",
            "On a scale from 1 to 7, how adequate is the training you received about AI?",
            note_it="Considera le opportunita' formative offerte dalla scuola e gli strumenti di apprendimento messi a disposizione.",
            note_en="Consider the training opportunities offered by your school and the learning tools made available."),
    _likert("Fiducia_Integrazione", "I",
            "Su una scala da 1 a 7, quanto sei fiducioso nell'integrazione dell'intelligenza artificiale nella scuola o universita'?",
            "On a scale from 1 to 7, how confident are you about integrating AI in school or university?",
            anchor="fiducia"),
    _likert("Fiducia_Insegnanti_Competenza", "I",
            "Su una scala da 1 a 7, quanto ritieni che i tuoi attuali insegnanti siano preparati e competenti nell'insegnare l'uso dell'intelligenza artificiale?",
            "On a scale from 1 to 7, how prepared and competent do you think your current teachers are in teaching the use of AI?"),
    _likert("Preocc_Integrazione", "S",
            "Su una scala da 1 a 7, quanto ti preoccupa l'inserimento dell'intelligenza artificiale nella scuola o nell'universita'?",
            "On a scale from 1 to 7, how worried are you about introducing AI in school or university?",
            anchor="preoccupazione"),
    _likert("Preocc_Compagni", "S",
            "Su una scala da 1 a 7, quanto sei preoccupato riguardo all'utilizzo dell'intelligenza artificiale da parte dei tuoi compagni di scuola o universita'?",
            "On a scale from 1 to 7, how worried are you about your schoolmates' use of AI?",
            anchor="preoccupazione"),

    _q("Uso_Quotidiano_Check", "P", "boolean",
       "Nella tua vita quotidiana utilizzi l'intelligenza artificiale?",
       "Do you use AI in your daily life?"),
    _q("Ore_Quotidiane", "P", "number",
       "Se si', quante ore alla settimana in media utilizzi strumenti di IA per le tue attivita' quotidiane? (se non li utilizzi, indica 0)",
       "If yes, how many hours per week on average do you use AI tools for your daily activities? (if you don't, enter 0)",
       min=0, max=168, required=False),
    _q("Uso_Studio_Check", "P", "boolean",
       "Utilizzi l'intelligenza artificiale nello studio?",
       "Do you use AI in your studies?"),
    _q("Ore_Studio", "P", "number",
       "Quante ore alla settimana mediamente utilizzi l'IA per le attivita' riguardanti lo studio?",
       "How many hours per week on average do you use AI for study-related activities?",
       min=0, max=168, required=False),
    _q("Ore_Informarsi", "P", "number",
       "Quante ore alla settimana mediamente dedichi a informarti sui nuovi strumenti di IA per lo studio?",
       "How many hours per week on average do you spend keeping up with new AI tools for studying?",
       min=0, max=168, required=False),
    _q("Ore_Risparmiate", "P", "number",
       "Quante ore ti fa risparmiare l'uso dell'intelligenza artificiale nel tuo studio in una settimana?",
       "How many hours per week does using AI save you in your studies?",
       min=0, max=168, required=False),
    _q("Strumenti_Usi", "P", "text",
       "Quali sono gli strumenti di intelligenza artificiale che utilizzi?",
       "Which AI tools do you use?",
       note_it="Considera chatbot, app di supporto ai compiti, piattaforme di organizzazione delle informazioni.",
       note_en="Consider chatbots, homework-support apps, information-organising platforms.",
       required=False),
    _q("Scopi_Uso", "P", "text",
       "Per quali scopi usi l'intelligenza artificiale nei tuoi studi?",
       "For what purposes do you use AI in your studies?", required=False),
    _q("Non_Uso_Scopi", "S", "text",
       "Per quali tipi di attivita' NON deve essere utilizzata l'intelligenza artificiale per apprendere?",
       "For which kinds of activities should AI NOT be used for learning?", required=False),
    _q("Strumenti_Regolari", "P", "text",
       "Quali strumenti di intelligenza artificiale utilizzi regolarmente nel tuo studio?",
       "Which AI tools do you use regularly in your studies?", required=False),
]


# === INSEGNANTI ==========================================================

INSEGNANTI = [
    _q("Codice_Anonimo", "profile", "text",
       "Inserisci un codice di 6 caratteri costituito dalle ultime 4 lettere del cognome di tua madre, seguite dal suo giorno di nascita nel formato gg (es.: reco03).",
       "Enter a 6-character code made of the last 4 letters of your mother's surname followed by her day of birth as dd (e.g. reco03)."),
    _q("Stato_Insegnamento", "profile", "single",
       "Attualmente insegni o hai intenzione di intraprendere la professione docente?",
       "Do you currently teach or intend to enter the teaching profession?",
       options=_opts([
           ("Attualmente insegno.", "I currently teach."),
           ("Ancora non insegno, ma sto seguendo o ho concluso un percorso PEF.",
            "I don't teach yet, but I am attending or have completed an initial teacher-training (PEF) path.")])),
    _q("Eta_Num", "profile", "number", "Quanti anni hai? (es.: 29)",
       "How old are you? (e.g. 29)", min=18, max=99),
    _q("Genere", "profile", "single", "Il tuo genere e'", "Your gender is",
       options=_opts([("Femmina", "Female"), ("Maschio", "Male"),
                      ("Altro o preferisco non specificare", "Other or prefer not to say")])),
    _q("Titolo_Studio", "profile", "single", "Titolo di studio", "Educational qualification",
       options=_opts([
           ("Licenza media superiore", "Upper secondary diploma"),
           ("Laurea triennale", "Bachelor's degree"),
           ("Laurea magistrale o a ciclo unico", "Master's / single-cycle degree"),
           ("Specializzazione post laurea / Master / Dottorato di ricerca", "Postgraduate / Master / PhD")])),
    _q("Ordine_Scuola", "profile", "single",
       "In quale ordine di scuola insegni (o vorresti insegnare)?",
       "In which school level do you teach (or wish to teach)?", required=False,
       options=_opts([
           ("Infanzia", "Pre-primary"), ("Primaria", "Primary"),
           ("Secondaria di primo grado", "Lower secondary"),
           ("Secondaria di secondo grado", "Upper secondary"),
           ("Universita'", "University")])),
    _q("Materia", "profile", "single", "Insegna (o insegnera') una materia",
       "You teach (or will teach) a subject that is", required=False,
       options=_opts([("STEM (Science, Technology, Engineering, Mathematics)", "STEM (Science, Technology, Engineering, Mathematics)"),
                      ("Umanistica", "Humanities")])),
    _q("Classe_Concorso", "profile", "text",
       "Qual e' il tuo settore scientifico-disciplinare o la tua classe di concorso?",
       "What is your scientific-disciplinary sector or teaching subject class?", required=False),

    _likert("Comp_Pratica", "R",
            "Su una scala da 1 a 7, quanto ti consideri competente nell'uso pratico di strumenti o tecnologie legati all'intelligenza artificiale?",
            "On a scale from 1 to 7, how competent do you consider yourself in the practical use of AI tools or technologies?",
            note_it="Con \"uso pratico\" intendiamo la capacita' di utilizzare concretamente strumenti, applicazioni o piattaforme di IA.",
            note_en="By \"practical use\" we mean the ability to concretely use AI tools, apps or platforms."),
    _likert("Comp_Teorica", "R",
            "Su una scala da 1 a 7, quanto ritieni adeguata la tua competenza teorica riguardo l'intelligenza artificiale?",
            "On a scale from 1 to 7, how adequate is your theoretical competence about AI?",
            note_it="Conoscenza dei principi, concetti e modelli fondamentali dell'IA.",
            note_en="Knowledge of the fundamental principles, concepts and models of AI."),
    _likert("Formazione_Adeguata", "A",
            "Su una scala da 1 a 7, quanto ritieni adeguata la formazione ricevuta in merito all'intelligenza artificiale?",
            "On a scale from 1 to 7, how adequate is the training you received about AI?",
            note_it="Considera i corsi frequentati, le opportunita' formative della scuola e gli strumenti messi a disposizione.",
            note_en="Consider the courses you attended, your school's training opportunities and the tools provided."),
    _likert("Impatto_Didattica_Gen", "X",
            "Su una scala da 1 a 7, quanto pensi che l'intelligenza artificiale cambiera' la didattica?",
            "On a scale from 1 to 7, how much do you think AI will change teaching in general?"),
    _likert("Impatto_Mia_Didattica", "X",
            "Su una scala da 1 a 7, quanto pensi che l'intelligenza artificiale cambiera' la tua didattica?",
            "On a scale from 1 to 7, how much do you think AI will change your own teaching?"),
    _likert("Fiducia_Integrazione", "I",
            "Su una scala da 1 a 7, quanto sei fiducioso nell'integrazione dell'intelligenza artificiale nella pratica educativa?",
            "On a scale from 1 to 7, how confident are you about integrating AI into educational practice?",
            anchor="fiducia"),
    _likert("Fiducia_Studenti_Responsabile", "I",
            "Su una scala da 1 a 7, quanto sei fiducioso che gli studenti facciano un uso responsabile e maturo dell'intelligenza artificiale?",
            "On a scale from 1 to 7, how confident are you that students make responsible and mature use of AI?",
            anchor="fiducia"),
    _likert("Preocc_Educazione", "S",
            "Su una scala da 1 a 7, quanto sei preoccupato riguardo all'utilizzo dell'intelligenza artificiale nel mondo dell'educazione?",
            "On a scale from 1 to 7, how worried are you about the use of AI in education?",
            anchor="preoccupazione"),
    _likert("Preocc_Studenti_Uso", "S",
            "Su una scala da 1 a 7, quanto sei preoccupato riguardo all'utilizzo dell'intelligenza artificiale da parte degli studenti?",
            "On a scale from 1 to 7, how worried are you about students' use of AI?",
            anchor="preoccupazione"),

    _q("Uso_Quotidiano_Check", "P", "boolean",
       "Nella tua vita quotidiana utilizzi l'intelligenza artificiale?",
       "Do you use AI in your daily life?"),
    _q("Ore_Quotidiane", "P", "number",
       "Se si', quante ore alla settimana in media utilizzi strumenti di IA per le tue attivita' quotidiane? (se non li utilizzi, indica 0)",
       "If yes, how many hours per week on average do you use AI tools for your daily activities? (if you don't, enter 0)",
       min=0, max=168, required=False),
    _q("Uso_Didattica_Check", "P", "boolean",
       "Utilizzi l'intelligenza artificiale nella didattica?",
       "Do you use AI in your teaching?"),
    _q("Ore_Formazione", "P", "number",
       "Quante ore alla settimana dedichi mediamente alla formazione e all'aggiornamento sulle tecnologie di IA per l'insegnamento?",
       "How many hours per week on average do you spend on training and updating on AI technologies for teaching?",
       min=0, max=168, required=False),
    _q("Ore_Integrazione_Lezioni", "P", "number",
       "Quante ore alla settimana dedichi mediamente a integrare strumenti di IA nei tuoi piani di lezione?",
       "How many hours per week on average do you spend integrating AI tools into your lesson plans?",
       min=0, max=168, required=False),
    _q("Non_Uso_Attivita", "S", "text",
       "Per quali tipi di attivita' NON deve essere utilizzata l'intelligenza artificiale nell'insegnamento?",
       "For which kinds of activities should AI NOT be used in teaching?", required=False),
    _q("Strumenti_Usi", "P", "text",
       "Quali sono gli strumenti di intelligenza artificiale che utilizzi?",
       "Which AI tools do you use?", required=False),
    _q("Attivita_Uso", "P", "text",
       "Per quali tipi di attivita' usi l'intelligenza artificiale?",
       "For which kinds of activities do you use AI?", required=False),
]


QUESTIONNAIRES = {
    "studenti": {
        "id": "studenti",
        "title": {"it": "Questionario Studenti", "en": "Students Questionnaire"},
        "questions": STUDENTI,
    },
    "insegnanti": {
        "id": "insegnanti",
        "title": {"it": "Questionario Insegnanti", "en": "Teachers Questionnaire"},
        "questions": INSEGNANTI,
    },
}

# Dimensioni PRAXIS per etichette dashboard
DIMENSIONS = {
    "profile": {"it": "Profilo", "en": "Profile"},
    "P": {"it": "Practice (uso)", "en": "Practice patterns"},
    "R": {"it": "Readiness (competenza)", "en": "Readiness beliefs"},
    "A": {"it": "Adequacy (formazione)", "en": "Adequacy & support"},
    "X": {"it": "eXpectations (impatto)", "en": "eXpectations"},
    "I": {"it": "Interpersonal trust (fiducia)", "en": "Interpersonal trust"},
    "S": {"it": "Skepticisms (preoccupazioni)", "en": "Skepticisms"},
}


def get_questionnaire(qid: str):
    return QUESTIONNAIRES.get(qid)


def question_index(qid: str):
    q = QUESTIONNAIRES.get(qid)
    if not q:
        return {}
    return {item["key"]: item for item in q["questions"]}
