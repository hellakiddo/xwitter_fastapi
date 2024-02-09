def serialize(obj):
    if isinstance(obj, list):
        return [serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: serialize(value) for key, value in obj.items()}
    elif hasattr(obj, '__dict__'):
        return {key: serialize(value) for key, value in obj.__dict__.items() if not key.startswith('_')}
    else:
        return obj