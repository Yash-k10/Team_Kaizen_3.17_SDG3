from database import get_donors, get_recipients


# Blood group compatibility rules
BLOOD_COMPATIBILITY = {
    "O": ["O", "A", "B", "AB"],
    "A": ["A", "AB"],
    "B": ["B", "AB"],
    "AB": ["AB"]
}


def is_blood_compatible(donor_bg, recipient_bg):
    donor_bg = donor_bg.upper()
    recipient_bg = recipient_bg.upper()
    return recipient_bg in BLOOD_COMPATIBILITY.get(donor_bg, [])


def calculate_match_score(donor, recipient):
    score = 0

    # donor = (id, name, age, blood, organ, city, urgency)
    # recipient = (id, name, age, blood, organ, city, urgency)

    # 1. Organ match (mandatory)
    if donor[4].lower() != recipient[4].lower():
        return 0

    score += 40  # strong weight

    # 2. Blood group compatibility
    if is_blood_compatible(donor[3], recipient[3]):
        score += 30

    # 3. Same city bonus
    if donor[5].lower() == recipient[5].lower():
        score += 15

    # 4. Urgency priority
    score += min(recipient[6] * 2, 10)

    # 5. Age similarity
    age_diff = abs(donor[2] - recipient[2])
    if age_diff <= 5:
        score += 5

    return score


def find_matches():
    donors = get_donors()
    recipients = get_recipients()

    matches = []

    for recipient in recipients:
        for donor in donors:
            score = calculate_match_score(donor, recipient)
            if score > 0:
                matches.append({
                    "donor_name": donor[1],
                    "recipient_name": recipient[1],
                    "organ": donor[4],
                    "score": score
                })

    # Sort by highest score
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches