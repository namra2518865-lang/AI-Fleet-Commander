"""Basic unit tests for the fleet engines.

Run from the repo root with:  py -m unittest discover tests
"""

import unittest

from backend.capital_rotation_engine import CapitalRotationEngine
from backend.commander import Commander
from backend.kill_switch import KillSwitch
from backend.market_engine import MarketEngine
from backend.market_guard import MarketGuard
from backend.opportunity_engine import OpportunityEngine
from backend.risk_engine import RiskEngine
from bots.trend_bot import TrendBot


class TestCapitalRotationEngine(unittest.TestCase):

    def test_allocations_sum_to_total_capital(self):
        engine = CapitalRotationEngine(total_capital=1000)

        allocations = engine.allocate_capital(
            [("TrendBot", 50), ("ScalperBot", 50)]
        )

        self.assertEqual(allocations["TrendBot"], 500)
        self.assertEqual(allocations["ScalperBot"], 500)

    def test_zero_scores_do_not_crash(self):
        engine = CapitalRotationEngine(total_capital=1000)

        allocations = engine.allocate_capital(
            [("TrendBot", 0), ("ScalperBot", 0)]
        )

        self.assertEqual(allocations["TrendBot"], 0)


class TestCommander(unittest.TestCase):

    def test_kill_switch_freezes_fleet(self):
        commander = Commander()

        result = commander.make_decision(
            market_safe=True,
            event_mode=False,
            kill_switch=True,
        )

        self.assertEqual(result, "FREEZE_FLEET")

    def test_normal_mode(self):
        commander = Commander()

        result = commander.make_decision(
            market_safe=True,
            event_mode=False,
            kill_switch=False,
        )

        self.assertEqual(result, "NORMAL_MODE")


class TestKillSwitch(unittest.TestCase):

    def test_activates_on_high_risk(self):
        kill = KillSwitch()

        self.assertTrue(kill.evaluate(portfolio_risk=9, market_drop=0))

    def test_stays_off_when_safe(self):
        kill = KillSwitch()

        self.assertFalse(kill.evaluate(portfolio_risk=1, market_drop=1))


class TestMarketEngine(unittest.TestCase):

    def test_dangerous_regime_is_unsafe(self):
        market = MarketEngine()

        market.update_market(
            regime="FLASH_CRASH",
            sentiment="NEGATIVE",
            volatility=90,
        )

        self.assertFalse(market.is_safe_market())

    def test_guard_agrees_with_engine(self):
        guard = MarketGuard()

        self.assertTrue(guard.should_pause("FLASH_CRASH"))
        self.assertFalse(guard.should_pause("BULL"))


class TestOpportunityEngine(unittest.TestCase):

    def test_known_bot_uses_its_weights(self):
        engine = OpportunityEngine()

        score = engine.calculate_opportunity(
            "TrendBot",
            setup_quality=100,
            market_fit=100,
            risk_reward=100,
            confidence=100,
        )

        self.assertEqual(score, 100)

    def test_unknown_bot_falls_back_to_defaults(self):
        engine = OpportunityEngine()

        score = engine.calculate_opportunity(
            "SomeNewBot",
            setup_quality=100,
            market_fit=100,
            risk_reward=100,
            confidence=100,
        )

        self.assertEqual(score, 100)


class TestRiskEngine(unittest.TestCase):

    def test_risk_calculation(self):
        risk = RiskEngine()

        report = risk.calculate_risk(10000)

        self.assertEqual(report["trade_size"], 1000)
        self.assertEqual(report["risk_amount"], 20)


class TestTrendBot(unittest.TestCase):

    def test_buys_in_bull_market(self):
        bot = TrendBot()

        bot.analyze_market("BULL")

        self.assertEqual(bot.get_status()["status"], "BUY")


if __name__ == "__main__":
    unittest.main()
