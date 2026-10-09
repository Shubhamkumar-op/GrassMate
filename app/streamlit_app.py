
import streamlit as st

from src.rag import generate_mission


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="GrassMate",
    page_icon="🌿",
    layout="centered",
)


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
        .main {
            padding-top: 1.5rem;
        }

        .mission-card {
            padding: 1.2rem;
            border-radius: 14px;
            border: 1px solid rgba(128, 128, 128, 0.3);
            margin-bottom: 1rem;
        }

        .phone-banner {
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            font-weight: bold;
            margin-top: 1.2rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(128, 128, 128, 0.3);
        }

        .footer {
            text-align: center;
            opacity: 0.7;
            font-size: 0.85rem;
            margin-top: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🌳 GrassMate")
st.subheader("Your AI-powered outdoor companion")

st.write(
    "Turn your free time into a simple outdoor mission. "
    "Choose your preferences, get your mission, and go outside."
)

st.divider()


# --------------------------------------------------
# USER PREFERENCES
# --------------------------------------------------

st.header("🎯 Create Your Outdoor Mission")

time = st.slider(
    "How much time do you have?",
    min_value=15,
    max_value=180,
    value=45,
    step=15,
    format="%d minutes",
)

activity = st.selectbox(
    "What would you like to do?",
    [
        "Walking",
        "Running",
        "Hiking",
        "Cycling",
        "Exploring",
        "Relaxing",
    ],
)

interest = st.selectbox(
    "What interests you?",
    [
        "Nature",
        "Adventure",
        "Fitness",
        "Peace and relaxation",
        "Wildlife",
        "Photography",
        "Something new",
    ],
)

mission_style = st.selectbox(
    "Choose your mission style",
    [
        "Relaxed",
        "Balanced",
        "Active",
    ],
)


# --------------------------------------------------
# LOCATION SETTINGS
# --------------------------------------------------

st.subheader("📍 Location Preferences")

use_location = st.checkbox(
    "Find trails near a location",
    value=False,
)

latitude = None
longitude = None
radius_km = None

if use_location:
    st.caption(
        "Enter coordinates for your search location. "
        "The current dataset contains California State Parks "
        "route records. These fields do not automatically detect "
        "your current location."
    )

    col1, col2 = st.columns(2)

    with col1:
        latitude = st.number_input(
            "Latitude",
            min_value=-90.0,
            max_value=90.0,
            value=36.25133,
            format="%.5f",
        )

    with col2:
        longitude = st.number_input(
            "Longitude",
            min_value=-180.0,
            max_value=180.0,
            value=-121.78291,
            format="%.5f",
        )

    radius_km = st.slider(
        "Search radius",
        min_value=1,
        max_value=100,
        value=10,
        step=1,
        format="%d km",
    )


st.divider()


# --------------------------------------------------
# GENERATE MISSION
# --------------------------------------------------

if st.button(
    "🌿 Generate My Mission",
    type="primary",
    use_container_width=True,
):
    try:
        with st.spinner(
            "Finding a route and creating your outdoor mission..."
        ):
            result = generate_mission(
                total_minutes=time,
                activity=activity,
                interest=interest,
                difficulty=mission_style,
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km,
            )

        st.session_state["grassmate_result"] = result

    except Exception as exc:
        st.session_state.pop("grassmate_result", None)

        st.error(
            "GrassMate couldn't generate a mission. "
            "Check that Ollama is running and the database "
            "connection is working."
        )
        st.exception(exc)


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

result = st.session_state.get("grassmate_result")

if result is not None:
    st.divider()
    st.header("🌳 Your Outdoor Mission")

    mission_text = result.get("mission", "")
    trails = result.get("trails") or []

    # Remove the generated Phone section because the app
    # displays its own phone-away banner for valid missions.
    if "\nPhone:" in mission_text:
        mission_text = mission_text.split("\nPhone:", 1)[0]

    # --------------------------------------------------
    # NO-ROUTE STATE
    # --------------------------------------------------

    if not trails:
        st.warning(
            "No matching outdoor routes were found for "
            f"your selected activity: **{activity}**."
        )

        st.write(
            "The current dataset may not contain routes "
            "recorded for this activity in the selected area."
        )

        st.info(
            "Try another activity, such as Walking, Hiking, "
            "or Cycling, or adjust your search location."
        )

        # Intentionally do not display a time plan or
        # phone-away banner when there is no matching route.

    # --------------------------------------------------
    # VALID MISSION STATE
    # --------------------------------------------------

    else:
        st.markdown(
            '<div class="mission-card">',
            unsafe_allow_html=True,
        )

        st.markdown(mission_text)

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

        # ----------------------------------------------
        # TIME PLAN
        # ----------------------------------------------

        plan = result.get("time_plan", {})

        st.header("⏱️ Time Plan")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Warm-up",
                f"{plan.get('warmup', 0)} min",
            )

        with col2:
            st.metric(
                "Main Activity",
                f"{plan.get('main_activity', 0)} min",
            )

        with col3:
            st.metric(
                "Cooldown",
                f"{plan.get('cooldown', 0)} min",
            )

        st.caption(
            f"Total mission time: "
            f"{plan.get('total', 0)} minutes"
        )

        # ----------------------------------------------
        # RETRIEVED TRAILS
        # ----------------------------------------------

        with st.expander(
            f"🔎 View trails used by GrassMate "
            f"({len(trails)} found)",
            expanded=False,
        ):
            for index, trail in enumerate(trails, start=1):
                (
                    trail_name,
                    trail_latitude,
                    trail_longitude,
                    segment_length_km,
                    recorded_activities,
                    route_type,
                    route_category,
                    retrieval_text,
                    vector_distance,
                    location_distance_km,
                ) = trail

                st.markdown(
                    f"**{index}. {trail_name}**"
                )

                if segment_length_km is not None:
                    st.write(
                        "**Recorded segment length:** "
                        f"{segment_length_km:.2f} km"
                    )
                else:
                    st.write(
                        "**Recorded segment length:** "
                        "Not available"
                    )

                st.write(
                    "**Recorded activities:** "
                    f"{recorded_activities or 'Not specified'}"
                )

                if route_type:
                    st.write(
                        f"**Recorded route type:** {route_type}"
                    )

                if route_category:
                    st.write(
                        f"**Recorded route category:** "
                        f"{route_category}"
                    )

                if (
                    trail_latitude is not None
                    and trail_longitude is not None
                ):
                    st.caption(
                        f"Coordinates: {trail_latitude:.5f}, "
                        f"{trail_longitude:.5f}"
                    )

                if location_distance_km is not None:
                    st.write(
                        "**Distance from search location:** "
                        f"{location_distance_km:.2f} km"
                    )

                st.divider()

        # ----------------------------------------------
        # PHONE-AWAY MESSAGE
        # ----------------------------------------------

        st.markdown(
            """
            <div class="phone-banner">
                📵 Read this once, put your phone away,
                and go outside. 🌿
            </div>
            """,
            unsafe_allow_html=True,
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
        Powered by Gemma 3 4B • BGE • Tiger Data + pgvector
    </div>
    """,
    unsafe_allow_html=True,
)
