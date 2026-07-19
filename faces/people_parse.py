def split_people(people: str | None) -> list[str]:
    if not people:
        return []
    return [person.strip() for person in people.split(",") if person.strip()]


def split_detections(people_detect: str | None) -> list[str]:
    if not people_detect:
        return []
    return [box.strip() for box in people_detect.split(",") if box.strip()]
