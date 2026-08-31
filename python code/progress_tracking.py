from clients_management import Client

class plan:
    def __init__(self, progress):
        self.progress = max(0, min(100, progress))

    def progress_color(self):
        width = 30
        filled = int((self.progress / 100) * width)

        if self.progress < 33:
            color = "\033[31m"   # red
        elif self.progress < 66:
            color = "\033[33m"   # yellow
        else:
            color = "\033[32m"   # green

        bar = "█" * filled + " " * (width - filled)
        print(f"{color}|{bar}| {self.progress}%\033[0m")

plan1 = plan(23)
plan1.progress_color()