import hmac
from urllib.parse import quote_plus

import streamlit as st


st.set_page_config(page_title="Fitness Coach", page_icon="💪", layout="centered")


def check_password() -> bool:
    expected = st.secrets.get("APP_PASSWORD", "")
    if not expected:
        return True

    entered = st.text_input("Mot de passe", type="password")
    if not entered:
        return False
    if hmac.compare_digest(entered, expected):
        return True
    st.error("Mot de passe incorrect.")
    return False


EXERCISES = {
    "Échauffement": [
        ("Marche dynamique", "Bouge les bras et monte progressivement le rythme.", "45 sec"),
        ("Cercles de bras", "Petits puis grands cercles, épaules relâchées.", "30 sec"),
        ("Montées de genoux douces", "Reste droit et garde un rythme confortable.", "30 sec"),
    ],
    "Renforcement": [
        ("Squats", "Pieds largeur d’épaules, hanches vers l’arrière, poitrine haute.", "12 reps"),
        ("Pompes inclinées", "Mains sur une table ou un canapé, corps gainé.", "10 reps"),
        ("Fentes arrière", "Recule une jambe, descends doucement, alterne les côtés.", "10 / jambe"),
        ("Pont fessier", "Allongé sur le dos, pousse les hanches vers le haut.", "15 reps"),
        ("Planche", "Corps aligné, abdos serrés, respire normalement.", "30 sec"),
        ("Bird-dog", "À quatre pattes, tends bras et jambe opposés.", "8 / côté"),
    ],
    "Cardio": [
        ("Step touch", "Pas à droite puis à gauche, bras actifs.", "45 sec"),
        ("Jumping jacks doux", "Sans saut si besoin : ouvre une jambe à la fois.", "30 sec"),
        ("Mountain climbers lents", "Mains au sol ou sur un support, genoux alternés.", "30 sec"),
        ("Shadow boxing", "Petits coups de poing contrôlés, buste gainé.", "45 sec"),
    ],
    "Mobilité": [
        ("Cat-cow", "À quatre pattes, alterne dos rond et dos creux doucement.", "45 sec"),
        ("Rotation thoracique", "À quatre pattes, ouvre un bras vers le plafond.", "8 / côté"),
        ("Étirement des hanches", "Fente légère, bassin vers l’avant sans forcer.", "30 sec / côté"),
        ("Étirement des ischios", "Jambe légèrement tendue, dos long, sans rebond.", "30 sec / côté"),
    ],
}


# Démonstrations vidéo sélectionnées. Lorsqu'une vidéo directe n'est pas encore
# sélectionnée, l'app propose automatiquement une recherche YouTube ciblée.
EXERCISE_VIDEOS = {
    "Montées de genoux douces": "https://www.youtube.com/watch?v=OAJ_J3EZkdY",
    "Squats": "https://www.youtube.com/watch?v=aclHkVaku9U",
    "Pompes inclinées": "https://www.youtube.com/watch?v=Gvm5Q29UHbk",
    "Pont fessier": "https://www.youtube.com/watch?v=wPM8icPu6H8",
    "Planche": "https://www.youtube.com/watch?v=DjEN3SKl0Eg",
    "Bird-dog": "https://www.youtube.com/watch?v=ZdAHe9_HeEw",
    "Jumping jacks doux": "https://www.youtube.com/watch?v=c4DAnQ6DtF8",
    "Mountain climbers lents": "https://www.youtube.com/watch?v=nmwgirgXLYM",
    "Shadow boxing": "https://www.youtube.com/watch?v=Q1Piq_vMh5g",
    "Cat-cow": "https://www.youtube.com/watch?v=MSBOBAIeLqI",
    "Étirement des ischios": "https://www.youtube.com/watch?v=vA6qj6suhN4",
    "Développé épaules avec haltères": "https://www.youtube.com/watch?v=qEwKCR5JCog",
    "Rowing avec haltères": "https://www.youtube.com/watch?v=roCP6wCXPqo",
    "Étirement doux": "https://www.youtube.com/watch?v=eqVMAPM00DM",
}


def show_exercise_video(name: str):
    st.subheader("🎥 Démonstration")
    video_url = EXERCISE_VIDEOS.get(name)

    if video_url:
        st.video(video_url)
        return

    query = quote_plus(f"{name} exercice démonstration technique")
    search_url = f"https://www.youtube.com/results?search_query={query}"
    st.link_button("▶️ Voir une démonstration vidéo", search_url, use_container_width=True)


def build_session(goal: str, duration: int, level: str, equipment: str):
    session = []
    session.extend(EXERCISES["Échauffement"])

    if goal == "Se muscler":
        pool = EXERCISES["Renforcement"]
    elif goal == "Cardio / brûler des calories":
        pool = EXERCISES["Cardio"] + EXERCISES["Renforcement"][:2]
    elif goal == "Mobilité / récupération":
        pool = EXERCISES["Mobilité"]
    else:
        pool = EXERCISES["Renforcement"][:3] + EXERCISES["Cardio"][:2]

    if equipment == "Haltères légers":
        pool = pool + [
            ("Développé épaules avec haltères", "Pousse les haltères au-dessus de la tête sans cambrer.", "10 reps"),
            ("Rowing avec haltères", "Buste légèrement penché, tire les coudes vers l’arrière.", "12 reps"),
        ]

    rounds = 1 if duration <= 15 else 2 if duration <= 30 else 3
    if level == "Débutant":
        rounds = max(1, rounds - 1)
    elif level == "Avancé":
        rounds += 1

    for _ in range(rounds):
        session.extend(pool)

    session.extend([
        ("Respiration lente", "Inspire 4 secondes, expire 6 secondes.", "60 sec"),
        ("Étirement doux", "Relâche jambes, dos et épaules sans forcer.", "60 sec"),
    ])
    return session


st.title("💪 Fitness Coach")
st.caption("Des séances simples et guidées sur ton téléphone")

if not check_password():
    st.stop()

with st.expander("⚠️ Sécurité", expanded=False):
    st.write(
        "Fais les mouvements dans une amplitude confortable. Arrête-toi en cas de douleur, malaise, "
        "essoufflement inhabituel ou vertiges. Cette app ne remplace pas un avis médical ou un coach qualifié."
    )

st.subheader("Créer ma séance")

goal = st.selectbox(
    "Objectif",
    ["Forme générale", "Se muscler", "Cardio / brûler des calories", "Mobilité / récupération"],
)
level = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé"])
duration = st.select_slider("Durée", options=[10, 15, 20, 30, 45], value=20, format_func=lambda x: f"{x} min")
equipment = st.selectbox("Matériel", ["Aucun", "Haltères légers"])

if st.button("Créer la séance", type="primary", use_container_width=True):
    st.session_state["workout"] = build_session(goal, duration, level, equipment)
    st.session_state["exercise_index"] = 0
    st.session_state["workout_meta"] = {
        "goal": goal,
        "duration": duration,
        "level": level,
        "equipment": equipment,
    }

workout = st.session_state.get("workout")

if workout:
    idx = st.session_state.get("exercise_index", 0)
    idx = min(idx, len(workout) - 1)
    name, instruction, target = workout[idx]
    meta = st.session_state.get("workout_meta", {})

    st.divider()
    st.caption(
        f"{meta.get('goal', '')} • {meta.get('duration', '')} min • {meta.get('level', '')} • {meta.get('equipment', '')}"
    )
    st.progress((idx + 1) / len(workout))
    st.write(f"Exercice {idx + 1} sur {len(workout)}")
    st.header(name)
    st.metric("Objectif", target)
    st.info(instruction)

    show_exercise_video(name)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Précédent", use_container_width=True, disabled=idx == 0):
            st.session_state["exercise_index"] = idx - 1
            st.rerun()
    with col2:
        if idx < len(workout) - 1:
            if st.button("Suivant ➡️", type="primary", use_container_width=True):
                st.session_state["exercise_index"] = idx + 1
                st.rerun()
        else:
            if st.button("✅ Terminer", type="primary", use_container_width=True):
                st.success("Séance terminée. Bravo !")
                st.balloons()

    if st.button("🔄 Recommencer cette séance", use_container_width=True):
        st.session_state["exercise_index"] = 0
        st.rerun()

st.caption("Version 2 — démonstrations vidéo, sans API OpenAI, donc aucun coût d’utilisation.")
