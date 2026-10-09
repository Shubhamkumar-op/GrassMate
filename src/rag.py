
import os
import re

os.environ["CUDA_VISIBLE_DEVICES"] = ""

from ollama import chat
from src.db.diverse_search import diverse_search
from src.time_plan import create_time_plan

MODEL_NAME = "gemma3:4b"

ACTIVITIES = {
    "Walking": {
        "phrase": "walk",
        "warmup": "Start with an easy pace and gently move your shoulders and arms.",
        "main": "Walk at a comfortable pace. Keep your steps relaxed and stay aware of the path.",
        "cooldown": "Slow to an easy stroll, relax your shoulders, and take a moment to enjoy being outdoors.",
    },
    "Hiking": {
        "phrase": "hike",
        "warmup": "Begin slowly on a suitable section of the path and check your footing.",
        "main": "Hike at a sustainable pace. Watch for uneven ground and stay on permitted paths.",
        "cooldown": "Ease your pace, relax your legs, and appreciate the surroundings before finishing.",
    },
    "Running": {
        "phrase": "run",
        "warmup": "Start with an easy walk and gradually increase your movement.",
        "main": "Run at a controlled pace appropriate for your fitness. Walk whenever you need to.",
        "cooldown": "Slow to a walk and allow your breathing to settle naturally.",
    },
    "Cycling": {
        "phrase": "ride",
        "warmup": "Check your bicycle and safety equipment, then begin with gentle pedalling in a safe area.",
        "main": "Ride at a controlled pace on a route suitable for cycling. Follow trail rules and stay alert.",
        "cooldown": "Slow down gradually, stop safely, and relax your legs.",
    },
    "Exploring": {
        "phrase": "outdoor exploration",
        "warmup": "Begin with an easy stroll and look around for details you might normally overlook.",
        "main": "Explore at an unhurried pace. Notice patterns, textures, and interesting details while staying on permitted paths.",
        "cooldown": "Slow down somewhere safe and choose one discovery to remember.",
    },
    "Relaxing": {
        "phrase": "outdoor relaxation break",
        "warmup": "Find a comfortable place to begin and relax your shoulders.",
        "main": "Enjoy the outdoors without rushing. Notice the breeze, natural sounds, and changing light.",
        "cooldown": "Pause somewhere safe, breathe naturally, and reflect on one thing you enjoyed.",
    },
}

INTERESTS = {
    "Nature": "Notice three natural textures, such as leaves, bark, or rocks, without disturbing them.",
    "Adventure": "Look for one unfamiliar detail along your permitted route without taking unnecessary risks.",
    "Fitness": "Focus on steady movement, comfortable posture, and an effort you can sustain.",
    "Peace and relaxation": "Notice three outdoor sounds and let yourself explore without rushing.",
    "Wildlife": "Look and listen for wildlife from a respectful distance. Never approach or feed animals.",
    "Photography": "Look for an interesting pattern, shadow, or natural composition. Stop only where safe.",
    "Something new": "Find one small detail you would normally overlook and spend a moment observing it.",
}

STYLES = {
    "Relaxed": "Keep the mission gentle, unhurried, and free of performance targets.",
    "Balanced": "Use a steady, manageable pace with time to observe your surroundings.",
    "Active": "Make the effort more purposeful while remaining controlled and taking breaks when needed.",
}


def normalize(value, choices, default):
    value = str(value or "").strip().casefold()
    for choice in choices:
        if choice.casefold() == value:
            return choice
    return default


def get_activity_phrase(activity):
    activity = normalize(activity, ACTIVITIES, "Hiking")
    return ACTIVITIES[activity]["phrase"]


def get_style_instruction(difficulty):
    difficulty = normalize(difficulty, STYLES, "Balanced")
    return STYLES[difficulty]


def build_trail_explanation(trail):
    name = str(trail[0] or "Selected route")
    length = trail[3]
    activities = str(trail[4] or "Not recorded")
    route_type = str(trail[5] or "Not recorded")

    details = []
    if length is not None:
        details.append(
            f"the recorded route segment is approximately {float(length):.2f} km long"
        )
    details.append(f"recorded activities: {activities}")
    if route_type != "Not recorded":
        details.append(f"recorded route type: {route_type}")

    return f"{name}: " + "; ".join(details) + "."


def build_fallback_phases(activity, interest, difficulty, time_plan):
    activity = normalize(activity, ACTIVITIES, "Hiking")
    interest = normalize(interest, INTERESTS, "Nature")
    difficulty = normalize(difficulty, STYLES, "Balanced")

    details = ACTIVITIES[activity]
    focus = INTERESTS[interest]
    style = STYLES[difficulty]

    main = f"{details['main']} {focus} {style}"

    if time_plan["main_activity"] <= 10:
        main += " Choose one simple focus and enjoy the short session without rushing."

    return {
        "warmup": details["warmup"],
        "main_activity": main,
        "cooldown": details["cooldown"],
    }


def parse_phase_instructions(text):
    labels = {
        "warmup": "warmup",
        "warm-up": "warmup",
        "main": "main_activity",
        "main activity": "main_activity",
        "cooldown": "cooldown",
        "cool-down": "cooldown",
    }
    parsed = {}
    current = None

    for line in text.splitlines():
        line = re.sub(r"^\s*[-*•]\s*", "", line.strip())
        if not line:
            continue

        match = re.match(
            r"^(WARM[\s-]*UP|MAIN(?:\s+ACTIVITY)?|COOL[\s-]*DOWN)\s*:\s*(.*)$",
            line,
            re.IGNORECASE,
        )
        if match:
            label = re.sub(r"\s+", " ", match.group(1).lower().replace("-", " ").strip())
            current = labels.get(label)
            content = match.group(2).strip()
            if current and content:
                parsed[current] = content
        elif current:
            parsed[current] = (parsed.get(current, "") + " " + line).strip()

    required = {"warmup", "main_activity", "cooldown"}
    if not required.issubset(parsed):
        return None
    if any(len(parsed[key]) < 10 for key in required):
        return None

    return parsed


def generate_phase_instructions(activity, interest, difficulty, time_plan):
    activity = normalize(activity, ACTIVITIES, "Hiking")
    interest = normalize(interest, INTERESTS, "Nature")
    difficulty = normalize(difficulty, STYLES, "Balanced")

    fallback = build_fallback_phases(
        activity, interest, difficulty, time_plan
    )

    prompt = f"""
Create a practical, personalized outdoor mission in exactly three phases.

Activity: {activity}
Interest: {interest}
Style: {difficulty}
Total time: {time_plan['total']} minutes
Warm-up: {time_plan['warmup']} minutes
Main activity: {time_plan['main_activity']} minutes
Cooldown: {time_plan['cooldown']} minutes

Activity guidance:
Warm-up: {ACTIVITIES[activity]['warmup']}
Main: {ACTIVITIES[activity]['main']}
Cooldown: {ACTIVITIES[activity]['cooldown']}

Interest challenge: {INTERESTS[interest]}
Style guidance: {STYLES[difficulty]}

Rules:
- Make each phase distinct and achievable.
- Main phase must combine the activity and interest challenge.
- Match the selected style and available time.
- Never invent trail facilities, weather, or wildlife sightings.
- Stay on permitted paths; respect wildlife and route safety.
- Do not include durations in the text.
- Use warm, natural, concise language.

Return exactly:
WARMUP: instruction
MAIN: instruction
COOLDOWN: instruction
""".strip()

    try:
        response = chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "Follow the exact format. Be specific, concise, and safe.",
                },
                {"role": "user", "content": prompt},
            ],
            options={"temperature": 0.4},
        )
        parsed = parse_phase_instructions(response["message"]["content"])
        if parsed:
            return parsed
    except Exception as exc:
        print(f"Mission generation fallback used: {exc}")

    return fallback


def build_mission_text(trail, activity, interest, difficulty, time_plan, phases):
    activity = normalize(activity, ACTIVITIES, "Hiking")
    interest = normalize(interest, INTERESTS, "Nature")
    difficulty = normalize(difficulty, STYLES, "Balanced")

    name = str(trail[0] or "Selected route")
    trail_length = trail[3]
    phrase = get_activity_phrase(activity)

    feasibility_note = ""
    if trail_length is not None and float(trail_length) < 1.0:
        feasibility_note = (
            "\n\n**Route note:** This is a short recorded route segment, "
            "not necessarily the full trail. The dataset does not confirm "
            "that this segment alone supports the full mission duration. "
            "Check local route information and turn back safely as needed."
        )

    return f"""Mission: Enjoy a {difficulty.lower()} {phrase} on {name}.

**Your focus: {interest}**

### Do

**Warm-up — {time_plan['warmup']} minutes**

{phases['warmup']}

**Main activity — {time_plan['main_activity']} minutes**

{phases['main_activity']}

**Cooldown — {time_plan['cooldown']} minutes**

{phases['cooldown']}

**Why this trail:** {build_trail_explanation(trail)}{feasibility_note}
"""


def generate_mission(
    total_minutes,
    activity,
    interest,
    difficulty,
    latitude=None,
    longitude=None,
    radius_km=None,
):
    time_plan = create_time_plan(total_minutes)

    activity = normalize(activity, ACTIVITIES, "Hiking")
    interest = normalize(interest, INTERESTS, "Nature")
    difficulty = normalize(difficulty, STYLES, "Balanced")

    query = (
        f"{activity}. Interest: {interest}. Style: {difficulty}. "
        f"Outdoor route for a {total_minutes}-minute outing."
    )

    try:
        trails = diverse_search(
            query=query,
            candidate_limit=50,
            result_limit=5,
            user_latitude=latitude,
            user_longitude=longitude,
            radius_km=radius_km,
            activity=activity,
        )
    except Exception as exc:
        print(f"Trail retrieval failed: {exc}")
        return {
            "mission": "GrassMate could not retrieve trails. Check the database connection and try again.",
            "time_plan": time_plan,
            "trails": [],
        }

    if not trails:
        return {
            "mission": "No matching route records were found. Try another activity or a wider search radius.",
            "time_plan": time_plan,
            "trails": [],
        }

    trail = trails[0]
    phases = generate_phase_instructions(
        activity, interest, difficulty, time_plan
    )
    mission = build_mission_text(
        trail, activity, interest, difficulty, time_plan, phases
    )

    return {
        "mission": mission,
        "time_plan": time_plan,
        "trails": trails,
    }


if __name__ == "__main__":
    result = generate_mission(
        total_minutes=45,
        activity="Walking",
        interest="Nature",
        difficulty="Relaxed",
        latitude=36.25133,
        longitude=-121.78291,
        radius_km=10,
    )
    print(result["mission"])
    print("\nTime plan:", result["time_plan"])
    print("Retrieved trails:", len(result["trails"]))
