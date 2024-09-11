def transform(config: dict) -> dict:
    return {
        "method": config["method"],
        "url": config["url"],
        "headers": config["headers"],
        "body": config["body"],
    }
