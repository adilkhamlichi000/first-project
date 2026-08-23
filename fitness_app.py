import hmac
import json
import random
import time

import requests
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Fitness Coach", page_icon="💪", layout="centered")

GIF_BASE = "https://raw.githubusercontent.com/mohamedatef90/exercise-library/main/gifs/"
MUSIC_URL = "https://pixabay.com/music/download/id-171614.mp3"
EXERCISE_SECONDS = 30


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


# Nom affiché, GIF, consigne courte, MET approximatif.
# Tous les GIFs ci-dessous existent dans la bibliothèque exercise-library.
EXERCISES = {
    "Échauffement": [
        ("Cercles de chevilles", "uL9CsKm.gif", "Fais des rotations lentes dans les deux sens.", 2.5),
        ("Étirement quadriceps à quatre pattes", "qBcKorM.gif", "Bouge lentement et garde une amplitude confortable.", 2.3),
        ("Étirement des mollets assis", "17bqEXD.gif", "Tends une jambe et avance doucement le buste sans forcer.", 2.2),
        ("Étirement des fessiers assis", "DeDThfG.gif", "Croise la jambe et garde le dos long pendant l'étirement.", 2.3),
        ("Étirement quadriceps sur le côté", "BWnJR72.gif", "Attrape la cheville et rapproche doucement le talon de la fesse.", 2.3),
        ("Toucher d'orteils debout", "BbfB8Gb.gif", "Penche-toi depuis les hanches en gardant le mouvement contrôlé.", 2.8),
        ("Toucher d'orteils circulaire", "RtyAsy1.gif", "Alterne les côtés lentement en gardant le tronc contrôlé.", 3.0),
    ],
    "Renforcement": [
        ("Pompes profondes", "vptOQ4N.gif", "Corps gainé, descends sous contrôle puis pousse sans creuser le dos.", 8.0),
        ("Pompes classiques", "I4hDWkc.gif", "Garde le corps aligné et descends la poitrine sous contrôle.", 8.0),
        ("Pompes archer", "A9qxk2F.gif", "Décale le poids vers un bras puis alterne en gardant le bassin stable.", 9.0),
        ("Pompes avec planche latérale", "KhHJ338.gif", "Après chaque pompe, tourne le buste et ouvre un bras vers le plafond.", 8.5),
        ("Pont fessier", "u0cNiij.gif", "Pousse dans les talons et serre les fessiers en haut.", 4.0),
        ("Extension lombaire au sol", "ANbbry2.gif", "Soulève légèrement le buste en serrant les fessiers, sans forcer la nuque.", 3.5),
        ("Abdos 3/4 sit-up", "2gPfomN.gif", "Monte le buste sous contrôle sans tirer sur la nuque.", 5.0),
        ("Toucher de talons alterné", "qaZVsGk.gif", "Garde les abdos engagés et alterne droite et gauche.", 4.0),
        ("Dead bug", "iny3m5y.gif", "Plaque le bas du dos au sol et allonge bras et jambe opposés.", 3.5),
        ("Reverse crunch", "nCU1Ekp.gif", "Ramène les genoux vers la poitrine en enroulant doucement le bassin.", 5.0),
        ("Crunch bras au-dessus de la tête", "kjJ3VoQ.gif", "Monte les épaules avec les abdos sans tirer sur la nuque.", 5.0),
        ("Sit-up bras croisés", "6ZCiYWQ.gif", "Garde les bras croisés et monte le buste de façon régulière.", 5.5),
        ("Squat avec extension des bras", "QChZi3x.gif", "Descends les hanches puis tends les bras au-dessus de la tête en remontant.", 5.5),
        ("Squat avec rotation", "5BZHW9s.gif", "Remonte du squat puis tourne le buste en alternant les côtés.", 6.0),
        ("Fente avec rotation", "K9VL0Jq.gif", "Avance en fente puis tourne le buste vers la jambe avant.", 6.0),
        ("Fentes marchées", "IZVHb27.gif", "Avance en alternant les jambes, buste droit et genou avant contrôlé.", 6.0),
        ("Relevé de jambes assis", "Hgs6Nl1.gif", "Garde le tronc stable et monte les jambes avec les abdos.", 4.5),
        ("Crab twist avec toucher de pied", "xgsGFVM.gif", "Tourne le buste et touche le pied opposé en gardant le bassin actif.", 6.0),
    ],
    "Cardio": [
        ("Mountain climbers", "RJgzwny.gif", "Garde le bassin stable et alterne les genoux à un rythme régulier.", 8.5),
        ("Burpees", "dK9394r.gif", "Reste contrôlé ; enlève le saut si nécessaire.", 10.0),
        ("Fentes marchées genoux hauts", "J9zIWig.gif", "Reste droit et monte le genou avec contrôle à chaque pas.", 6.5),
        ("Sauts ciseaux", "Eh2v5Iu.gif", "Saute en alternant rapidement la jambe placée devant.", 8.0),
        ("Skater hops", "zfNHMN9.gif", "Saute latéralement d'un pied sur l'autre et amortis chaque réception.", 8.0),
        ("Pas de ski latéraux", "5MRH8H2.gif", "Enchaîne les sauts latéraux avec un rythme régulier et léger.", 7.5),
        ("Fentes sautées", "PM1PZjg.gif", "Change de jambe en l'air et réceptionne doucement avant de repartir.", 9.0),
    ],
    "Haltères": [
        ("Élévations latérales haltères", "DsgkuIt.gif", "Épaules basses, monte les bras sans élan.", 3.5),
        ("Rowing penché haltères", "BJ0Hz5L.gif", "Dos neutre, tire les haltères vers les côtes en serrant les omoplates.", 6.0),
        ("Développé épaule un bras", "84RyJf8.gif", "Gaine le tronc et pousse l'haltère au-dessus de la tête sans te pencher.", 6.0),
        ("Élévations frontales haltères", "3eGE2JC.gif", "Monte les haltères devant toi jusqu'à hauteur d'épaule sans élan.", 4.5),
        ("Squat avec haltères", "HsvHqgf.gif", "Garde les haltères le long du corps, poitrine haute et pousse dans les talons.", 6.0),
        ("Fentes avec haltères", "RRWFUcw.gif", "Tiens les haltères le long du corps et alterne les fentes avec contrôle.", 6.0),
        ("Fente avec curl biceps", "Mz6lLcW.gif", "Fais le curl pendant la descente en fente puis alterne les jambes.", 6.5),
        ("Soulevé de terre haltères", "nUwVh7b.gif", "Recule les hanches, garde le dos neutre puis redresse-toi en serrant les fessiers.", 6.0),
        ("Curl marteau puis développé", "LeaZOIz.gif", "Fais un curl contrôlé puis pousse l'haltère au-dessus de la tête.", 5.5),
        ("Squat avec curl biceps", "niXESDw.gif", "Descends en squat puis réalise le curl sans balancer les bras.", 6.0),
    ],
}


@st.cache_data(ttl=86400, show_spinner=False, max_entries=100)
def load_gif(filename: str):
    try:
        response = requests.get(GIF_BASE + filename, timeout=20)
        response.raise_for_status()
        if len(response.content) < 1024:
            return None
        return response.content
    except requests.RequestException:
        return None


def unique_exercises(exercises):
    seen = set()
    result = []
    for exercise in exercises:
        if exercise[1] not in seen:
            seen.add(exercise[1])
            result.append(exercise)
    return result


def choose_active_pool(goal: str, equipment: str):
    if goal == "Se muscler":
        pool = list(EXERCISES["Renforcement"])
    elif goal == "Cardio / brûler des calories":
        pool = list(EXERCISES["Cardio"]) + list(EXERCISES["Renforcement"][:10])
    elif goal == "Mobilité / récupération":
        pool = list(EXERCISES["Échauffement"]) + [
            EXERCISES["Renforcement"][4],
            EXERCISES["Renforcement"][5],
            EXERCISES["Renforcement"][8],
        ]
    else:
        pool = list(EXERCISES["Renforcement"]) + list(EXERCISES["Cardio"])

    if equipment == "Haltères légers":
        pool += EXERCISES["Haltères"]
    return unique_exercises(pool)


def build_session(goal: str, duration: int, level: str, equipment: str):
    target_count = max(1, int(duration * 60 / EXERCISE_SECONDS))
    warmups = list(EXERCISES["Échauffement"])
    active = choose_active_pool(goal, equipment)

    if not active:
        active = warmups

    session = []
    warmup_count = min(4, target_count)
    for ex in warmups[:warmup_count]:
        session.append((*ex[:3], EXERCISE_SECONDS, ex[3]))

    while len(session) < target_count:
        block = list(active)
        random.shuffle(block)
        for ex in block:
            if len(session) >= target_count:
                break
            if session and session[-1][1] == ex[1]:
                continue
            session.append((*ex[:3], EXERCISE_SECONDS, ex[3]))

    return session


def coach_text(exercise):
    name, _, instruction, seconds, _ = exercise
    return f"{name}. {instruction} Fais ce mouvement pendant {seconds} secondes."


def adjusted_met(exercise, level: str) -> float:
    met = float(exercise[4])
    if level == "Débutant":
        met *= 0.9
    elif level == "Avancé":
        met *= 1.1
    return met


def calories_for_seconds(weight_kg: float, met: float, seconds: float) -> float:
    return met * 3.5 * weight_kg / 200.0 * (seconds / 60.0)


def calories_before_index(workout, idx: int, weight_kg: float, level: str) -> float:
    total = 0.0
    for exercise in workout[:idx]:
        total += calories_for_seconds(weight_kg, adjusted_met(exercise, level), EXERCISE_SECONDS)
    return total


def install_start_audio(first_exercise):
    text = json.dumps(coach_text(first_exercise), ensure_ascii=False)
    music_url = json.dumps(MUSIC_URL)

    components.html(
        f"""
        <script>
        (() => {{
          const P = window.parent;
          const D = P.document;

          function isMuted() {{
            return localStorage.getItem('fitnessMuted') === '1';
          }}

          function getMusic() {{
            let audio = D.getElementById('fitnessGlobalMusic');
            if (!audio) {{
              audio = D.createElement('audio');
              audio.id = 'fitnessGlobalMusic';
              audio.src = {music_url};
              audio.loop = true;
              audio.preload = 'auto';
              audio.playsInline = true;
              audio.style.display = 'none';
              D.body.appendChild(audio);
            }}
            return audio;
          }}

          function speak(text) {{
            if (isMuted()) return;
            try {{
              const synth = P.speechSynthesis;
              if (!synth || !P.SpeechSynthesisUtterance) return;
              synth.cancel();
              const u = new P.SpeechSynthesisUtterance(text);
              u.lang = 'fr-FR';
              u.rate = 0.92;
              u.volume = 1.0;
              const fr = synth.getVoices().find(v => (v.lang || '').toLowerCase().startsWith('fr'));
              if (fr) u.voice = fr;
              const music = getMusic();
              u.onstart = () => {{ music.volume = 0.04; }};
              u.onend = () => {{ if (!isMuted()) music.volume = 0.16; }};
              u.onerror = () => {{ if (!isMuted()) music.volume = 0.16; }};
              synth.speak(u);
            }} catch (e) {{}}
          }}

          if (P.__fitnessStartHandler) D.removeEventListener('click', P.__fitnessStartHandler, true);

          P.__fitnessStartHandler = (event) => {{
            const button = event.target.closest ? event.target.closest('button') : null;
            if (!button) return;
            const label = (button.innerText || button.textContent || '').trim();
            if (!label.includes('Créer la séance')) return;

            localStorage.setItem('fitnessMuted', '0');
            const music = getMusic();
            music.currentTime = 0;
            music.volume = 0.16;
            music.play().catch(() => {{}});
            P.__fitnessSessionActive = true;
            speak({text});
          }};

          D.addEventListener('click', P.__fitnessStartHandler, true);
        }})();
        </script>
        """,
        height=0,
    )


def install_audio_controls(workout, idx: int, auto_announce: bool):
    current_text = coach_text(workout[idx])
    next_text = coach_text(workout[idx + 1]) if idx + 1 < len(workout) else "Séance terminée. Bravo."
    previous_text = coach_text(workout[idx - 1]) if idx > 0 else current_text
    first_text = coach_text(workout[0])
    payload = json.dumps(
        {"current": current_text, "next": next_text, "previous": previous_text, "first": first_text},
        ensure_ascii=False,
    )
    music_url = json.dumps(MUSIC_URL)
    auto_flag = "true" if auto_announce else "false"

    components.html(
        f"""
        <script>
        (() => {{
          const P = window.parent;
          const D = P.document;
          const texts = {payload};
          const autoAnnounce = {auto_flag};

          function isMuted() {{
            return localStorage.getItem('fitnessMuted') === '1';
          }}

          function getMusic() {{
            let audio = D.getElementById('fitnessGlobalMusic');
            if (!audio) {{
              audio = D.createElement('audio');
              audio.id = 'fitnessGlobalMusic';
              audio.src = {music_url};
              audio.loop = true;
              audio.preload = 'auto';
              audio.playsInline = true;
              audio.style.display = 'none';
              D.body.appendChild(audio);
            }}
            return audio;
          }}

          function speak(text) {{
            if (isMuted()) return;
            try {{
              const synth = P.speechSynthesis;
              if (!synth || !P.SpeechSynthesisUtterance) return;
              synth.cancel();
              const u = new P.SpeechSynthesisUtterance(text);
              u.lang = 'fr-FR';
              u.rate = 0.92;
              u.volume = 1.0;
              const fr = synth.getVoices().find(v => (v.lang || '').toLowerCase().startsWith('fr'));
              if (fr) u.voice = fr;
              const music = getMusic();
              u.onstart = () => {{ music.volume = 0.04; }};
              u.onend = () => {{ if (!isMuted()) music.volume = 0.16; }};
              u.onerror = () => {{ if (!isMuted()) music.volume = 0.16; }};
              synth.speak(u);
            }} catch (e) {{}}
          }}

          const music = getMusic();
          if (P.__fitnessSessionActive && !isMuted()) {{
            music.volume = 0.16;
            music.play().catch(() => {{}});
          }}

          if (P.__fitnessNavHandler) D.removeEventListener('click', P.__fitnessNavHandler, true);
          if (P.__fitnessSoundHandler) D.removeEventListener('click', P.__fitnessSoundHandler, true);

          P.__fitnessNavHandler = (event) => {{
            const button = event.target.closest ? event.target.closest('button') : null;
            if (!button) return;
            const label = (button.innerText || button.textContent || '').trim();
            if (label.includes('Suivant')) speak(texts.next);
            else if (label.includes('Précédent')) speak(texts.previous);
            else if (label.includes('Recommencer')) speak(texts.first);
          }};

          P.__fitnessSoundHandler = (event) => {{
            const button = event.target.closest ? event.target.closest('button') : null;
            if (!button) return;
            const label = (button.innerText || button.textContent || '').trim();
            const music = getMusic();

            if (label.includes('Couper le son')) {{
              localStorage.setItem('fitnessMuted', '1');
              music.pause();
              try {{ P.speechSynthesis.cancel(); }} catch (e) {{}}
            }} else if (label.includes('Remettre le son')) {{
              localStorage.setItem('fitnessMuted', '0');
              music.volume = 0.16;
              music.play().catch(() => {{}});
              speak(texts.current);
            }}
          }};

          D.addEventListener('click', P.__fitnessNavHandler, true);
          D.addEventListener('click', P.__fitnessSoundHandler, true);

          if (autoAnnounce && !isMuted()) {{
            setTimeout(() => speak(texts.current), 350);
          }}
        }})();
        </script>
        """,
        height=0,
    )


def stop_audio():
    components.html(
        """
        <script>
        (() => {
          const P = window.parent;
          const D = P.document;
          const music = D.getElementById('fitnessGlobalMusic');
          if (music) music.pause();
          try { P.speechSynthesis.cancel(); } catch (e) {}
          P.__fitnessSessionActive = false;
        })();
        </script>
        """,
        height=0,
    )


def stats_html(session_elapsed: float, calories: float, movement_left: int):
    mins = int(session_elapsed) // 60
    secs = int(session_elapsed) % 60
    clock = f"{mins:02d}:{secs:02d}"
    st.markdown(
        f"""
        <div style="display:flex;gap:10px;margin:8px 0 6px 0;">
          <div style="flex:1;background:#262730;border:1px solid #4a4b55;border-radius:12px;padding:10px 6px;text-align:center;color:white;">
            <div style="font-size:11px;color:#d7d7dc;font-weight:700;">⏱ TEMPS SÉANCE</div>
            <div style="font-size:26px;font-weight:800;color:white;">{clock}</div>
          </div>
          <div style="flex:1;background:#262730;border:1px solid #4a4b55;border-radius:12px;padding:10px 6px;text-align:center;color:white;">
            <div style="font-size:11px;color:#d7d7dc;font-weight:700;">🔥 CALORIES</div>
            <div style="font-size:26px;font-weight:800;color:white;">{calories:.1f} kcal</div>
          </div>
        </div>
        <div style="text-align:center;color:#e6e6ea;font-weight:700;margin-bottom:6px;">
          Mouvement : {movement_left} s restantes
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.fragment(run_every="1s")
def live_workout_timer(workout, weight_kg: float, level: str):
    if st.session_state.get("workout_finished"):
        return

    idx = int(st.session_state.get("exercise_index", 0))
    now = time.time()
    started = float(st.session_state.get("exercise_started_at", now))
    session_started = float(st.session_state.get("session_started_at", now))
    elapsed_exercise = max(0.0, now - started)

    if elapsed_exercise >= EXERCISE_SECONDS:
        if idx + 1 < len(workout):
            st.session_state["exercise_index"] = idx + 1
            st.session_state["current_gif"] = None
            st.session_state["exercise_started_at"] = now
            st.session_state["auto_announce"] = True
        else:
            st.session_state["workout_finished"] = True
        st.rerun()

    elapsed_exercise = min(elapsed_exercise, EXERCISE_SECONDS)
    movement_left = max(0, EXERCISE_SECONDS - int(elapsed_exercise))
    session_elapsed = max(0.0, now - session_started)

    calories_before = calories_before_index(workout, idx, weight_kg, level)
    current_kcal = calories_for_seconds(weight_kg, adjusted_met(workout[idx], level), elapsed_exercise)
    stats_html(session_elapsed, calories_before + current_kcal, movement_left)


st.title("💪 Fitness Coach")
st.caption("42 mouvements • 30 secondes par mouvement • durée totale respectée • Hype Energy")

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
weight_kg = st.number_input(
    "Poids (kg) — pour estimer les calories",
    min_value=30.0,
    max_value=200.0,
    value=70.0,
    step=1.0,
)

preview_workout = build_session(goal, duration, level, equipment)
if preview_workout:
    install_start_audio(preview_workout[0])

if st.button("Créer la séance", type="primary", use_container_width=True, disabled=not preview_workout):
    now = time.time()
    st.session_state["workout"] = preview_workout
    st.session_state["exercise_index"] = 0
    st.session_state["current_gif"] = None
    st.session_state["sound_enabled"] = True
    st.session_state["workout_finished"] = False
    st.session_state["session_started_at"] = now
    st.session_state["exercise_started_at"] = now
    st.session_state["auto_announce"] = False
    st.session_state["workout_meta"] = {
        "goal": goal,
        "duration": duration,
        "level": level,
        "equipment": equipment,
        "weight_kg": float(weight_kg),
    }
    st.rerun()

workout = st.session_state.get("workout")

if workout:
    meta = st.session_state.get("workout_meta", {})
    session_weight = float(meta.get("weight_kg", weight_kg))
    session_level = meta.get("level", level)
    requested_duration = int(meta.get("duration", duration))

    if st.session_state.get("workout_finished"):
        stop_audio()
        total_calories = calories_before_index(workout, len(workout), session_weight, session_level)
        st.success(f"Séance terminée : {requested_duration} minutes.")
        stats_html(requested_duration * 60, total_calories, 0)
        if st.button("🔄 Recommencer cette séance", type="primary", use_container_width=True):
            now = time.time()
            st.session_state["exercise_index"] = 0
            st.session_state["current_gif"] = None
            st.session_state["workout_finished"] = False
            st.session_state["session_started_at"] = now
            st.session_state["exercise_started_at"] = now
            st.session_state["auto_announce"] = True
            st.rerun()
        st.stop()

    idx = min(int(st.session_state.get("exercise_index", 0)), len(workout) - 1)
    name, gif_file, instruction, seconds, _ = workout[idx]

    gif_bytes = st.session_state.get("current_gif")
    if not gif_bytes:
        gif_bytes = load_gif(gif_file)
        st.session_state["current_gif"] = gif_bytes

    if not gif_bytes:
        if idx + 1 < len(workout):
            st.session_state["exercise_index"] = idx + 1
            st.session_state["exercise_started_at"] = time.time()
            st.session_state["current_gif"] = None
            st.session_state["auto_announce"] = True
            st.rerun()
        st.error("Les démonstrations sont temporairement indisponibles.")
        st.stop()

    auto_announce = bool(st.session_state.pop("auto_announce", False))
    install_audio_controls(workout, idx, auto_announce)

    sound_enabled = st.session_state.get("sound_enabled", True)
    sound_label = "🔇 Couper le son" if sound_enabled else "🔊 Remettre le son"
    if st.button(sound_label, use_container_width=True):
        st.session_state["sound_enabled"] = not sound_enabled
        st.rerun()

    st.divider()
    st.caption(
        f"{meta.get('goal', '')} • {requested_duration} min • {meta.get('level', '')} • {meta.get('equipment', '')}"
    )
    st.progress((idx + 1) / len(workout))
    st.write(f"Mouvement {idx + 1} sur {len(workout)}")
    st.header(name)
    st.info(instruction)

    st.subheader("🎥 Suis le coach")
    st.image(gif_bytes, width="stretch")

    live_workout_timer(workout, session_weight, session_level)
    st.caption("Calories = estimation selon le poids et l’intensité du mouvement.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Précédent", use_container_width=True, disabled=idx == 0):
            st.session_state["exercise_index"] = max(0, idx - 1)
            st.session_state["current_gif"] = None
            st.session_state["exercise_started_at"] = time.time()
            st.session_state["auto_announce"] = False
            st.rerun()

    with col2:
        if idx < len(workout) - 1:
            if st.button("Suivant ➡️", type="primary", use_container_width=True):
                st.session_state["exercise_index"] = idx + 1
                st.session_state["current_gif"] = None
                st.session_state["exercise_started_at"] = time.time()
                st.session_state["auto_announce"] = False
                st.rerun()

    if st.button("🔄 Recommencer cette séance", use_container_width=True):
        now = time.time()
        st.session_state["exercise_index"] = 0
        st.session_state["current_gif"] = None
        st.session_state["workout_finished"] = False
        st.session_state["session_started_at"] = now
        st.session_state["exercise_started_at"] = now
        st.session_state["auto_announce"] = True
        st.rerun()

st.caption("Musique : Hype Energy — The_Mountain, Pixabay Content License.")