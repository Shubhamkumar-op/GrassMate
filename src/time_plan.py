def create_time_plan(total_minutes):
    """
    Divide the available time into warm-up, main activity, and cooldown.

    The three phases always add up to total_minutes.
    Short missions keep transitions brief; longer missions allow
    more time for preparation and recovery.
    """
    if not isinstance(total_minutes, int) or isinstance(total_minutes, bool):
        raise TypeError("total_minutes must be an integer.")

    if total_minutes < 9:
        raise ValueError("A mission needs at least 9 minutes.")

    if total_minutes <= 20:
        warmup = 3
        cooldown = 3
    elif total_minutes <= 60:
        warmup = 5
        cooldown = 5
    elif total_minutes <= 120:
        warmup = 8
        cooldown = 8
    else:
        warmup = 10
        cooldown = 10

    main_activity = total_minutes - warmup - cooldown

    return {
        "warmup": warmup,
        "main_activity": main_activity,
        "cooldown": cooldown,
        "total": total_minutes,
    }
