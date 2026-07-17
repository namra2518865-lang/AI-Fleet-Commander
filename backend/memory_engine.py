class MemoryEngine:

    def __init__(self):

        self.memory = []

    def save_memory(self, event):

        self.memory.append(event)

    def get_memory(self):

        return self.memory


if __name__ == "__main__":

    memory = MemoryEngine()

    memory.save_memory(
        "Market changed to BULL regime"
    )

    memory.save_memory(
        "TrendBot received extra capital"
    )

    print(memory.get_memory())
