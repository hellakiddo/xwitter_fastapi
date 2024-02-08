def one_post(data):
    return {
        "text": data["text"],
    }

def all_posts(data):
    return [one_post(p) for p in data]