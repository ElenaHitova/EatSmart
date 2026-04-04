def is_health_profile_complete(user) -> bool:
    if not user.is_authenticated:
        return False

    profile = getattr(user, "userprofile", None)
    if profile is None:
        return False

    required_fields = (
        profile.role,
        profile.age,
        profile.height,
        profile.weight,
        profile.gender,
        profile.activity_level,
        profile.dietary_goal,
    )

    return all(value is not None and value != "" for value in required_fields)
