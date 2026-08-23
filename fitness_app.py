import hmac
import json

import requests
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Fitness Coach", page_icon="💪", layout="centered")

GIF_BASE = "https://raw.githubusercontent.com/mohamedatef90/exercise-library/main/gifs/"
# Hype Energy — The_Mountain, Pixabay Content License.
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


EXERCISES = {
    "Échauffement": [
        ("Cercles de chevilles", "uL9CsKm.gif", "Fais des rotations lentes dans les deux sens.", 30),
        ("Étirement quadriceps à quatre pattes", "qBcKorM.gif", "Bouge lentement et reste dans une amplitude confortable.", 35),
    ],
    "Renforcement": [
        ("Pompes profondes", "vptOQ4N.gif", "Corps gainé, descends sous contrôle puis pousse sans creuser le dos.", 35),
        ("Pont fessier", "u0cNiij.gif", "Pousse dans les talons et serre les fessiers en haut.", 40),
        ("Abdos 3/4 sit-up", "2gPfomN.gif", "Monte le buste sous contrôle sans tirer sur la nuque.", 35),
        ("Toucher de talons alterné", "qaZVsGk.gif", "Garde les abdos engagés et alterne droite et gauche.", 35),
    ],
    "Cardio": [
        ("Mountain climbers", "RJgzwny.gif", "Garde le bassin stable et alterne les genoux à un rythme régulier.", 35),
        ("Burpees", "dK9394r.gif", "Reste contrôlé ; enlève le saut si nécessaire.", 30),
        ("Fentes marchées genoux hauts", "J9zIWig.gif", "Reste droit et avance avec contrôle.", 40),
    ],
    "Haltères": [
        ("Élévations latérales haltères", "DsgkuIt.gif", "Épaules basses, monte les bras sans élan.", 35),
    ],
}

# Valeurs MET approximatives pour estimer les calories brûlées.
EXERCISE_MET = {
    "Cercles de chevilles": 2.5,
    "Étirement quadriceps à quatre pattes": 2.3,
    "Pompes profondes": 8.0,
    "Pont fessier": 4.0,
    "Abdos 3/4 sit-up": 5.0,
    "Toucher de talons alterné": 4.0,
    "Mountain climbers": 8.5,
    "Burpees": 10.0,
    "Fentes marchées genoux hauts": 6.0,
    "Élévations latérales haltères": 3.5,
}


@st.cache_data(ttl=86400, show_spinner=False, max_entries=20)
def load_gif(filename: str):
    try:
        response = requests.get(GIF_BASE + filename, timeout=30)
        response.raise_for_status()
        if len(response.content) < 1024:
            return None
        return response.content
    except requests.RequestException:
        return None


def build_session(goal: str, duration: int, level: str, equipment: str):
    session = list(EXERCISES["Échauffement"])

    if goal == "Se muscler":
        pool = EXERCISES["Renforcement"]
    elif goal == "Cardio / brûler des calories":
        pool = EXERCISES["Cardio"] + EXERCISES["Renforcement"][:2]
    elif goal == "Mobilité / récupération":
        pool = EXERCISES["Échauffement"] + EXERCISES["Renforcement"][1:2]
    else:
        pool = EXERCISES["Renforcement"][:3] + EXERCISES["Cardio"][:2]

    if equipment == "Haltères légers":
        pool += EXERCISES["Haltères"]

    rounds = 1 if duration <= 15 else 2 if duration <= 30 else 3
    if level == "Débutant":
        rounds = max(1, rounds - 1)
    elif level == "Avancé":
        rounds += 1

    for _ in range(rounds):
        session.extend(pool)

    return [
        (name, gif_file, instruction, EXERCISE_SECONDS)
        for name, gif_file, instruction, _ in session
    ]


def next_readable(workout, start_index: int):
    for candidate_idx in range(start_index, len(workout)):
        gif_bytes = load_gif(workout[candidate_idx][1])
        if gif_bytes:
            return candidate_idx, gif_bytes
    return None, None


def coach_text(exercise):
    name, _, instruction, seconds = exercise
    return f"{name}. {instruction} Fais ce mouvement pendant {seconds} secondes."


def met_for_exercise(exercise, level: str) -> float:
    name = exercise[0]
    met = EXERCISE_MET.get(name, 4.0)
    if level == "Débutant":
        met *= 0.9
    elif level == "Avancé":
        met *= 1.1
    return met


def calories_for_seconds(weight_kg: float, met: float, seconds: float) -> float:
    # Estimation : kcal/min = MET × 3,5 × poids(kg) / 200.
    return met * 3.5 * weight_kg / 200.0 * (seconds / 60.0)


def calories_before_index(workout, idx: int, weight_kg: float, level: str) -> float:
    total = 0.0
    for exercise in workout[:idx]:
        total += calories_for_seconds(
            weight_kg,
            met_for_exercise(exercise, level),
            EXERCISE_SECONDS,
        )
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
            audio.volume = 0.16;
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
              u.pitch = 1.0;
              u.volume = 1.0;
              const voices = synth.getVoices();
              const fr = voices.find(v => (v.lang || '').toLowerCase().startsWith('fr'));
              if (fr) u.voice = fr;
              const music = getMusic();
              u.onstart = () => {{ music.volume = 0.045; }};
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
            localStorage.setItem('fitnessSessionStartedAt', String(Date.now()));
            localStorage.removeItem('fitnessExerciseTimerKey');
            localStorage.removeItem('fitnessExerciseStartedAt');

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


def install_navigation_audio(workout, idx):
    current = coach_text(workout[idx])
    next_text = coach_text(workout[idx + 1]) if idx + 1 < len(workout) else "Séance terminée. Bravo."
    previous_text = coach_text(workout[idx - 1]) if idx > 0 else current
    first_text = coach_text(workout[0])

    safe = json.dumps(
        {"current": current, "next": next_text, "previous": previous_text, "first": first_text},
        ensure_ascii=False,
    )
    music_url = json.dumps(MUSIC_URL)

    components.html(
        f"""
        <script>
        (() => {{
          const P = window.parent;
          const D = P.document;
          const texts = {safe};

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
              u.pitch = 1.0;
              u.volume = 1.0;
              const voices = synth.getVoices();
              const fr = voices.find(v => (v.lang || '').toLowerCase().startsWith('fr'));
              if (fr) u.voice = fr;
              const music = getMusic();
              u.onstart = () => {{ music.volume = 0.045; }};
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
            else if (label.includes('Recommencer')) {{
              localStorage.setItem('fitnessSessionStartedAt', String(Date.now()));
              localStorage.removeItem('fitnessExerciseTimerKey');
              localStorage.removeItem('fitnessExerciseStartedAt');
              speak(texts.first);
            }}
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
            }}
          }};

          D.addEventListener('click', P.__fitnessNavHandler, true);
          D.addEventListener('click', P.__fitnessSoundHandler, true);
        }})();
        </script>
        """,
        height=0,
    )


def install_auto_advance(idx: int, total: int, calories_before: float, current_kcal_30s: float):
    """Affiche temps séance + kcal + compte à rebours, puis avance automatiquement."""
    target_label = "Suivant" if idx < total - 1 else "Terminer"
    timer_key = f"{idx}-{total}"
    safe_timer_key = json.dumps(timer_key)
    safe_target = json.dumps(target_label)

    components.html(
        f"""
        <style>
          html, body {{
            margin: 0;
            padding: 0;
            background: transparent !important;
            color: #ffffff !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          }}
          .stats-row {{
            display: flex;
            gap: 10px;
            margin: 4px 0 7px 0;
          }}
          .stat-card {{
            flex: 1;
            min-width: 0;
            text-align: center;
            background: #262730;
            border: 1px solid #4a4b55;
            border-radius: 12px;
            padding: 10px 5px;
            color: #ffffff !important;
          }}
          .stat-label {{
            font-size: 11px;
            font-weight: 650;
            letter-spacing: .3px;
            color: #d7d7dc !important;
          }}
          .stat-value {{
            margin-top: 3px;
            font-size: 25px;
            line-height: 1.1;
            font-weight: 800;
            color: #ffffff !important;
          }}
          .movement-timer {{
            text-align: center;
            font-size: 14px;
            font-weight: 650;
            color: #e6e6ea !important;
            padding-top: 2px;
          }}
        </style>

        <div class="stats-row">
          <div class="stat-card">
            <div class="stat-label">⏱ TEMPS SÉANCE</div>
            <div id="fitnessSessionTime" class="stat-value">00:00</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">🔥 CALORIES</div>
            <div id="fitnessCalories" class="stat-value">{calories_before:.1f} kcal</div>
          </div>
        </div>
        <div id="fitnessCountdown" class="movement-timer">Mouvement : 30 s restantes</div>

        <script>
        (() => {{
          const P = window.parent;
          const D = P.document;
          const timerKey = {safe_timer_key};
          const targetLabel = {safe_target};
          const sessionTime = document.getElementById('fitnessSessionTime');
          const countdown = document.getElementById('fitnessCountdown');
          const calories = document.getElementById('fitnessCalories');
          const caloriesBefore = {calories_before:.8f};
          const currentExerciseCalories = {current_kcal_30s:.8f};

          if (P.__fitnessAutoTimer) clearTimeout(P.__fitnessAutoTimer);
          if (P.__fitnessCountdownTimer) clearInterval(P.__fitnessCountdownTimer);

          let exerciseStartedAt = parseInt(localStorage.getItem('fitnessExerciseStartedAt') || '0', 10);
          const previousTimerKey = localStorage.getItem('fitnessExerciseTimerKey');
          if (previousTimerKey !== timerKey || !exerciseStartedAt) {{
            exerciseStartedAt = Date.now();
            localStorage.setItem('fitnessExerciseTimerKey', timerKey);
            localStorage.setItem('fitnessExerciseStartedAt', String(exerciseStartedAt));
          }}

          let sessionStartedAt = parseInt(localStorage.getItem('fitnessSessionStartedAt') || '0', 10);
          if (!sessionStartedAt) {{
            sessionStartedAt = Date.now() - ({idx} * 30000);
            localStorage.setItem('fitnessSessionStartedAt', String(sessionStartedAt));
          }}

          function elapsedExerciseSeconds() {{
            return Math.min(30, Math.max(0, (Date.now() - exerciseStartedAt) / 1000));
          }}

          function formatClock(totalSeconds) {{
            const whole = Math.max(0, Math.floor(totalSeconds));
            const mins = Math.floor(whole / 60).toString().padStart(2, '0');
            const secs = (whole % 60).toString().padStart(2, '0');
            return `${{mins}}:${{secs}}`;
          }}

          function render() {{
            const exerciseElapsed = elapsedExerciseSeconds();
            const left = Math.max(0, Math.ceil(30 - exerciseElapsed));
            const sessionElapsed = Math.max(0, (Date.now() - sessionStartedAt) / 1000);
            const kcal = caloriesBefore + currentExerciseCalories * (exerciseElapsed / 30);

            if (sessionTime) sessionTime.textContent = formatClock(sessionElapsed);
            if (countdown) countdown.textContent = `Mouvement : ${{left}} s restantes`;
            if (calories) calories.textContent = `${{kcal.toFixed(1)}} kcal`;
          }}

          render();
          P.__fitnessCountdownTimer = setInterval(render, 200);

          const remainingMs = Math.max(0, 30000 - (Date.now() - exerciseStartedAt));
          P.__fitnessAutoTimer = setTimeout(() => {{
            clearInterval(P.__fitnessCountdownTimer);
            render();

            const buttons = Array.from(D.querySelectorAll('button'));
            const targetButton = buttons.find(btn =>
              ((btn.innerText || btn.textContent || '').trim()).includes(targetLabel)
            );
            if (targetButton) targetButton.click();
          }}, remainingMs);
        }})();
        </script>
        """,
        height=104,
    )


st.title("💪 Fitness Coach")
st.caption("Démonstrations animées + Hype Energy + coach vocal français")

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
install_start_audio(preview_workout[0])

if st.button("Créer la séance", type="primary", use_container_width=True):
    workout = preview_workout
    with st.spinner("Préparation de la première démonstration…"):
        first_idx, first_gif = next_readable(workout, 0)

    if first_idx is not None:
        st.session_state["workout"] = workout
        st.session_state["exercise_index"] = first_idx
        st.session_state["current_gif"] = first_gif
        st.session_state["sound_enabled"] = True
        st.session_state["workout_meta"] = {
            "goal": goal,
            "duration": duration,
            "level": level,
            "equipment": equipment,
            "weight_kg": float(weight_kg),
        }
    else:
        st.error("Les démonstrations ne sont pas accessibles pour le moment.")

workout = st.session_state.get("workout")

if workout:
    idx = min(st.session_state.get("exercise_index", 0), len(workout) - 1)
    name, gif_file, instruction, seconds = workout[idx]
    meta = st.session_state.get("workout_meta", {})
    session_weight = float(meta.get("weight_kg", weight_kg))
    session_level = meta.get("level", level)

    gif_bytes = st.session_state.get("current_gif") or load_gif(gif_file)
    if not gif_bytes:
        next_idx, next_gif = next_readable(workout, idx + 1)
        if next_idx is not None:
            st.session_state["exercise_index"] = next_idx
            st.session_state["current_gif"] = next_gif
            st.rerun()
        st.error("Aucune autre démonstration disponible dans cette séance.")
        st.stop()

    install_navigation_audio(workout, idx)

    sound_enabled = st.session_state.get("sound_enabled", True)
    sound_label = "🔇 Couper le son" if sound_enabled else "🔊 Remettre le son"
    if st.button(sound_label, use_container_width=True):
        st.session_state["sound_enabled"] = not sound_enabled
        st.rerun()

    st.divider()
    st.caption(
        f"{meta.get('goal', '')} • {meta.get('duration', '')} min • {meta.get('level', '')} • {meta.get('equipment', '')}"
    )
    st.progress((idx + 1) / len(workout))
    st.write(f"Exercice {idx + 1} sur {len(workout)}")
    st.header(name)
    st.info(instruction)

    st.subheader("🎥 Suis le coach")
    st.image(gif_bytes, width="stretch")

    calories_before = calories_before_index(workout, idx, session_weight, session_level)
    current_met = met_for_exercise(workout[idx], session_level)
    current_kcal_30s = calories_for_seconds(session_weight, current_met, EXERCISE_SECONDS)
    install_auto_advance(idx, len(workout), calories_before, current_kcal_30s)

    st.caption("Calories = estimation selon le poids et l’intensité du mouvement.")
    st.write("Le mouvement suivant démarre automatiquement après 30 secondes.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Précédent", use_container_width=True, disabled=idx == 0):
            previous_idx = idx - 1
            while previous_idx >= 0:
                previous_gif = load_gif(workout[previous_idx][1])
                if previous_gif:
                    st.session_state["exercise_index"] = previous_idx
                    st.session_state["current_gif"] = previous_gif
                    st.rerun()
                previous_idx -= 1

    with col2:
        if idx < len(workout) - 1:
            if st.button("Suivant ➡️", type="primary", use_container_width=True):
                next_idx, next_gif = next_readable(workout, idx + 1)
                if next_idx is not None:
                    st.session_state["exercise_index"] = next_idx
                    st.session_state["current_gif"] = next_gif
                    st.rerun()
                st.success("Séance terminée.")
        else:
            if st.button("✅ Terminer", type="primary", use_container_width=True):
                st.success("Séance terminée. Bravo !")
                st.balloons()

    if st.button("🔄 Recommencer cette séance", use_container_width=True):
        first_idx, first_gif = next_readable(workout, 0)
        if first_idx is not None:
            st.session_state["exercise_index"] = first_idx
            st.session_state["current_gif"] = first_gif
            st.rerun()

st.caption("Musique : Hype Energy — The_Mountain, Pixabay Content License.")
