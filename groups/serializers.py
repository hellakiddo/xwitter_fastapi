def serialize_group(group):
    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "author_id": group.author_id
    }