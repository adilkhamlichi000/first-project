import hmac

import requests
import streamlit as st


st.set_page_config(page_title="Fitness Coach HD", page_icon="💪", layout="centered")

DATA_URL = "https://raw.githubusercontent.com/harshvishu/free-exercise-db-with-videos/main/data/exercises.json"


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
        ("Échauffement épaules", "Band Shoulder Warm-Up Stretch", "Mobilise les épaules sans forcer.", 35),
        ("Cercles des poignets", "Wrist Circles", "Fais des rotations lentes dans les deux sens.", 30),
        ("Mobilité chevilles", "Feet and Ankles Rotation Stretch", "Tourne les chevilles doucement et garde l’équilibre.", 30),
    ],
    "Renforcement": [
        ("Squats", "Squat", "Poitrine haute, genoux dans l’axe des pieds, pousse les hanches vers l’arrière.", 40),
        ("Pompes", "Push-Up", "Corps gainé, descends sous contrôle et pousse sans creuser le dos.", 35),
        ("Pont fessier", "Bridge Pose (Setu Bandhasana)", "Pousse dans les talons et serre les fessiers en haut.", 40),
        ("Étirement en position quadrupède", "All Fours Groin Stretch", "Bouge lentement et reste dans une amplitude confortable.", 40),
    ],
    "Cardio": [
        ("Jumping jacks", "Jumping Jack", "Garde un rythme régulier et atterris souplement.", 40),
        ("Burpees", "Burpee", "Reste contrôlé ; ralentis ou enlève le saut si nécessaire.", 30),
        ("Cardio léger", "Cardio Exercise", "Buste droit, bras actifs, cadence confortable.", 45),
    ],
    "Mobilité": [
        ("Étirement fléchisseurs de hanche", "Standing Hip Flexor and Abdominal Stretch", "Bassin légèrement rentré, ne cambre pas le bas du dos.", 40),
        ("Étirement ischios", "Single Straight Leg Stretch", "Garde le mouvement lent et évite les à-coups.", 40),
        ("Rotation du buste", "Chest Lift with Rotation", "Tourne depuis le haut du dos sans forcer la nuque.", 40),
        ("Étirement adducteurs", "All Fours Groin Stretch", "Respire calmement et garde une amplitude confortable.", 40),
    ],
    "Haltères": [
        ("Élévations latérales haltères", "Dumbbell Lateral Raise", "Garde les épaules basses et monte les bras sans élan.", 35),
        ("Développé épaules haltères", "Dumbbell Alternating Shoulder Press", "Abdos serrés, pousse au-dessus de la tête sans cambrer.", 35),
    ],
}


@st.cache_data(ttl=86400, show_spinner=False)
def load_catalogue():
    response = requests.get(
        DATA_URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    return payload if isinstance(payload, list) else []


def normalize(text: str) -> str:
    return " ".join(text.lower().replace("-", " ").split())


def find_exercise(catalogue, api_name: str):
    target = normalize(api_name)

    for item in catalogue:
        if normalize(item.get("name", "")) == target:
            return item

    for item in catalogue:
        for alias in item.get("aliases", []) or []:
            if normalize(str(alias)) == target:
                return item

    for item in catalogue:
        candidate = normalize(item.get("name", ""))
        if target and candidate and (target in candidate or candidate in target):
            return item

    return None


def female_video(item):
    if not item:
        return None
    videos = item.get("videos", {}) or {}
    return videos.get("female")


def available_exercises(catalogue, exercises):
    """Garde seulement les mouvements qui ont une vraie URL de vidéo féminine dans le catalogue."""
    available = []
    for exercise in exercises:
        _, api_name, _, _ = exercise
        item = find_exercise(catalogue, api_name)
        if female_video(item):
            available.append(exercise)
    return available


@st.cache_data(ttl=3600, show_spinner=False, max_entries=16)
def load_video_bytes(url: str):
    """Télécharge le MP4 côté Streamlit, puis l'app le sert elle-même à l'iPhone."""
    if not url:
        return None
    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1",
                "Accept": "video/mp4,video/*;q=0.9,*/*;q=0.8",
            },
            timeout=60,
            allow_redirects=True,
        )
        response.raise_for_status()
        if len(response.content) < 1024:
            return None
        return response.content
    except requests.RequestException:
        return None


def adjusted_seconds(seconds: int, level: str) -> int:
    if level == "Débutant":
        return max(20, seconds - 5)
    if level == "Avancé":
        return seconds + 10
    return seconds


def build_session(goal: str, duration: int, level: str, equipment: str, catalogue):
    warmup = available_exercises(catalogue, EXERCISES["Échauffement"])

    if goal == "Se muscler":
        pool = EXERCISES["Renforcement"]
    elif goal == "Cardio / brûler des calories":
        pool = EXERCISES["Cardio"] + EXERCISES["Renforcement"][:2]
    elif goal == "Mobilité / récupération":
        pool = EXERCISES["Mobilité"]
    else:
        pool = EXERCISES["Renforcement"][:3] + EXERCISES["Cardio"][:2]

    if equipment == "Haltères légers":
        pool = pool + EXERCISES["Haltères"]

    pool = available_exercises(catalogue, pool)
    session = list(warmup)

    rounds = 1 if duration <= 15 else 2 if duration <= 30 else 3
    if level == "Débutant":
        rounds = max(1, rounds - 1)
    elif level == "Avancé":
        rounds += 1

    for _ in range(rounds):
        session.extend(pool)

    return [
        (label, api_name, instruction, adjusted_seconds(seconds, level))
        for label, api_name, instruction, seconds in session
    ]


def move_to_next_video(workout, start_index, catalogue):
    """Cherche le prochain exercice dont le MP4 est réellement téléchargeable."""
    for candidate_idx in range(start_index, len(workout)):
        _, api_name, _, _ = workout[candidate_idx]
        item = find_exercise(catalogue, api_name)
        url = female_video(item)
        video_bytes = load_video_bytes(url)
        if video_bytes:
            return candidate_idx, video_bytes
    return None, None


st.title("💪 Fitness Coach HD")
st.caption("Uniquement des mouvements avec démonstration vidéo HD")

if not check_password():
    st.stop()

with st.expander("⚠️ Sécurité", expanded=False):
    st.write(
        "Fais les mouvements dans une amplitude confortable. Arrête-toi en cas de douleur, malaise, "
        "essoufflement inhabituel ou vertiges. Cette app ne remplace pas un avis médical ou un coach qualifié."
    )

try:
    with st.spinner("Chargement du catalogue vidéo HD…"):
        catalogue = load_catalogue()
except Exception as exc:
    catalogue = []
    st.error(f"Le catalogue HD n’a pas pu être chargé : {exc}")

if catalogue:
    st.success("Catalogue HD chargé")

st.subheader("Créer ma séance")
goal = st.selectbox(
    "Objectif",
    ["Forme générale", "Se muscler", "Cardio / brûler des calories", "Mobilité / récupération"],
)
level = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé"])
duration = st.select_slider("Durée", options=[10, 15, 20, 30, 45], value=20, format_func=lambda x: f"{x} min")
equipment = st.selectbox("Matériel", ["Aucun", "Haltères légers"])

if st.button("Créer la séance", type="primary", use_container_width=True, disabled=not bool(catalogue)):
    workout = build_session(goal, duration, level, equipment, catalogue)
    if workout:
        with st.spinner("Préparation de la première vidéo…"):
            first_idx, first_bytes = move_to_next_video(workout, 0, catalogue)
        if first_idx is not None:
            st.session_state["workout"] = workout
            st.session_state["exercise_index"] = first_idx
            st.session_state["current_video_bytes"] = first_bytes
            st.session_state["workout_meta"] = {
                "goal": goal,
                "duration": duration,
                "level": level,
                "equipment": equipment,
            }
        else:
            st.error("Les vidéos du fournisseur sont temporairement inaccessibles. Réessaie dans quelques instants.")
    else:
        st.error("Aucun mouvement avec vidéo n’est disponible pour cette sélection.")

workout = st.session_state.get("workout")

if workout:
    idx = min(st.session_state.get("exercise_index", 0), len(workout) - 1)
    label, api_name, instruction, seconds = workout[idx]
    meta = st.session_state.get("workout_meta", {})

    item = find_exercise(catalogue, api_name)
    video_url = female_video(item)
    video_bytes = st.session_state.get("current_video_bytes")

    if not video_bytes:
        with st.spinner("Chargement de la vidéo HD…"):
            video_bytes = load_video_bytes(video_url)

    # Si ce fichier précis échoue, on saute automatiquement au prochain lisible.
    if not video_bytes:
        with st.spinner("Cette vidéo ne répond pas, recherche de la suivante…"):
            next_idx, next_bytes = move_to_next_video(workout, idx + 1, catalogue)
        if next_idx is not None:
            st.session_state["exercise_index"] = next_idx
            st.session_state["current_video_bytes"] = next_bytes
            st.rerun()
        else:
            st.error("Aucune autre vidéo de cette séance n’est actuellement accessible.")
            st.stop()

    st.divider()
    st.caption(
        f"{meta.get('goal', '')} • {meta.get('duration', '')} min • {meta.get('level', '')} • {meta.get('equipment', '')}"
    )
    st.progress((idx + 1) / len(workout))
    st.write(f"Exercice {idx + 1} sur {len(workout)}")
    st.header(label)
    st.metric("Durée", f"{seconds} sec")
    st.info(instruction)

    st.subheader("🎥 Suis le coach")
    st.video(
        video_bytes,
        format="video/mp4",
        autoplay=True,
        loop=True,
        muted=True,
        width="stretch",
    )
    st.caption("Vidéo HD téléchargée par l’app puis servie directement à ton téléphone.")

    st.write(f"⏱️ Fais le mouvement pendant **{seconds} secondes**, puis passe au suivant.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Précédent", use_container_width=True, disabled=idx == 0):
            previous_idx = idx - 1
            while previous_idx >= 0:
                prev_item = find_exercise(catalogue, workout[previous_idx][1])
                prev_bytes = load_video_bytes(female_video(prev_item))
                if prev_bytes:
                    st.session_state["exercise_index"] = previous_idx
                    st.session_state["current_video_bytes"] = prev_bytes
                    st.rerun()
                previous_idx -= 1
    with col2:
        if idx < len(workout) - 1:
            if st.button("Suivant ➡️", type="primary", use_container_width=True):
                with st.spinner("Chargement du mouvement suivant…"):
                    next_idx, next_bytes = move_to_next_video(workout, idx + 1, catalogue)
                if next_idx is not None:
                    st.session_state["exercise_index"] = next_idx
                    st.session_state["current_video_bytes"] = next_bytes
                    st.rerun()
                else:
                    st.success("Séance terminée.")
        else:
            if st.button("✅ Terminer", type="primary", use_container_width=True):
                st.success("Séance terminée. Bravo !")
                st.balloons()

    if st.button("🔄 Recommencer cette séance", use_container_width=True):
        with st.spinner("Préparation de la première vidéo…"):
            first_idx, first_bytes = move_to_next_video(workout, 0, catalogue)
        if first_idx is not None:
            st.session_state["exercise_index"] = first_idx
            st.session_state["current_video_bytes"] = first_bytes
            st.rerun()

st.caption("Version HD — les mouvements sans vidéo sont exclus et les fichiers indisponibles sont sautés automatiquement.")
