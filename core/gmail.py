class Gmail:
    def __init__(self):
        # Placeholder email sender for simple tests.
        # No external dependencies; just prints to console.
        pass

    def send_email(self, to, subject, content):
        print("=== Email (disabled) ===")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print(content)
        print("========================")
        return {"status": "printed"}