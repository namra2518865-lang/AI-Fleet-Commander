from config.settings import DANGEROUS_REGIMES


class MarketGuard:

    def should_pause(self, regime):
        return regime in DANGEROUS_REGIMES


if __name__ == "__main__":
    guard = MarketGuard()

    print(guard.should_pause("FLASH_CRASH"))
