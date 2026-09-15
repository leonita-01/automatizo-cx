from ..schemas import ProcessAssessment, ProcessInput


def assess_process(item: ProcessInput) -> ProcessAssessment:
    score = 20
    rationale: list[str] = []

    if item.monthly_volume >= 1000:
        score += 25
        rationale.append("High monthly volume creates meaningful automation impact.")
    elif item.monthly_volume >= 300:
        score += 15
        rationale.append("Moderate volume supports a controlled automation business case.")
    else:
        rationale.append("Low volume reduces the immediate financial impact of automation.")

    score += round(item.rule_based_percentage * 0.35)
    rationale.append(f"{item.rule_based_percentage}% of the process is rule-based.")

    if item.systems_count <= 3:
        score += 15
        rationale.append("Limited system dependencies reduce integration complexity.")
    else:
        score -= 10
        rationale.append("Multiple systems increase delivery and integration complexity.")

    if item.sensitive_data:
        score -= 20
        rationale.append(
            "Sensitive data requires privacy controls, approval gates and human oversight."
        )

    score = max(0, min(100, score))
    recommendation = (
        "Prioritize for automation"
        if score >= 70
        else "Run a controlled pilot"
        if score >= 45
        else "Keep human-led for now"
    )
    hours_saved = (
        item.monthly_volume
        * item.average_handle_minutes
        * (item.rule_based_percentage / 100)
        * 0.7
        / 60
    )
    fte_capacity = hours_saved / 160
    risk_level = (
        "high"
        if item.sensitive_data and item.systems_count > 3
        else "medium"
        if item.sensitive_data or item.systems_count > 3
        else "low"
    )
    return ProcessAssessment(
        process_name=item.name,
        automation_score=score,
        recommendation=recommendation,
        estimated_hours_saved_monthly=round(hours_saved, 1),
        estimated_fte_capacity=round(fte_capacity, 2),
        risk_level=risk_level,
        rationale=rationale,
    )
