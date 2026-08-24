def generate_no_match_suggestions(
    budget: float,
    rejected_tracks
) -> list[str]:

    suggestions = []

    budget_rejections = 0

    territory_rejections = 0

    rights_rejections = 0


    for item in rejected_tracks:

        reasons = item.rejection_reasons

        for reason in reasons:

            if "exceeds the budget" in reason:

                budget_rejections += 1

            elif "territory" in reason.lower():

                territory_rejections += 1

            elif (
                "sync rights" in reason.lower()
                or "commercial" in reason.lower()
            ):

                rights_rejections += 1


    if budget_rejections > 0:

        suggestions.append(
            "Consider increasing the budget."
        )


    if territory_rejections > 0:

        suggestions.append(
            "Consider relaxing the territory "
            "requirement if appropriate."
        )


    if rights_rejections > 0:

        suggestions.append(
            "Search for alternative tracks "
            "with compatible rights."
        )


    if not suggestions:

        suggestions.append(
            "Consider broadening the creative "
            "requirements."
        )


    return suggestions