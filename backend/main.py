from bots.defense_bot import DefenseBot
from bots.momentum_bot import MomentumBot
from bots.scalper_bot import ScalperBot
from bots.trend_bot import TrendBot

from backend.bot_manager import BotManager
from backend.capital_rotation_engine import CapitalRotationEngine
from backend.commander import Commander
from backend.data_feed import DataFeed
from backend.event_guard import EventGuard
from backend.kill_switch import KillSwitch
from backend.market_engine import MarketEngine
from backend.market_guard import MarketGuard
from backend.memory_engine import MemoryEngine
from backend.opportunity_engine import OpportunityEngine
from backend.portfolio_manager import PortfolioManager
from backend.risk_engine import RiskEngine
from backend.scheduler import Scheduler
from backend.strategy_engine import StrategyEngine
from config.settings import TOTAL_CAPITAL


def build_fleet():
    """Create all bots and register them with the manager."""
    manager = BotManager()

    manager.register_bot(TrendBot())
    manager.register_bot(ScalperBot())
    manager.register_bot(MomentumBot())
    manager.register_bot(DefenseBot())

    return manager


def run_cycle(feed, market, commander, guards, engines, manager, memory):
    """Run one full fleet decision cycle."""
    market_guard, event_guard, kill_switch = guards
    strategy, opportunity, rotation, portfolio, risk, scheduler = engines

    # 1. Read market data and update market state
    snapshot = feed.get_snapshot()

    market.update_market(
        regime=snapshot["regime"],
        sentiment=snapshot["sentiment"],
        volatility=snapshot["volatility"],
    )

    scheduler.market_scan()

    market_state = market.get_market_state()

    # 2. Commander decides fleet mode
    kill_active = kill_switch.evaluate(
        portfolio_risk=0,
        market_drop=snapshot["market_drop"],
    )

    mode = commander.make_decision(
        market_safe=not market_guard.should_pause(market_state["market_regime"]),
        event_mode=event_guard.event_mode,
        kill_switch=kill_active,
    )

    memory.save_memory(f"Fleet mode: {mode}")

    if mode == "FREEZE_FLEET":
        return {"mode": mode, "market": market_state}

    # 3. Bots analyze the market
    manager.get_bot("TrendBot").analyze_market(market_state["market_regime"])
    manager.get_bot("ScalperBot").analyze_market(market_state["market_regime"])
    manager.get_bot("MomentumBot").analyze_market(market_state["sentiment"])
    manager.get_bot("DefenseBot").analyze_risk(market_state["volatility"])

    for bot_name in manager.bot_names():
        strategy.register_bot(bot_name)

    # 4. Score opportunities and rank bots
    for status in manager.get_all_statuses():
        active = status["status"] not in ("WAIT", "IDLE")

        opportunity.calculate_opportunity(
            status["bot"],
            setup_quality=80 if active else 40,
            market_fit=80 if active else 40,
            risk_reward=70,
            confidence=75,
        )

    ranked = opportunity.rank_bots()
    scheduler.ranking_update()

    # 5. Rotate capital across bots by score
    allocations = rotation.allocate_capital(ranked)
    scheduler.capital_rotation()

    for bot_name, amount in allocations.items():
        portfolio.allocate_capital(bot_name, amount)

    scheduler.portfolio_audit()

    # 6. Risk report for the full portfolio
    risk_report = risk.calculate_risk(TOTAL_CAPITAL)

    memory.save_memory(f"Capital allocated: {allocations}")

    return {
        "mode": mode,
        "market": market_state,
        "bots": manager.get_all_statuses(),
        "ranking": ranked,
        "allocations": allocations,
        "risk": risk_report,
    }


def main():
    feed = DataFeed()
    market = MarketEngine()
    commander = Commander()
    memory = MemoryEngine()
    manager = build_fleet()

    guards = (MarketGuard(), EventGuard(), KillSwitch())

    engines = (
        StrategyEngine(),
        OpportunityEngine(),
        CapitalRotationEngine(total_capital=TOTAL_CAPITAL),
        PortfolioManager(),
        RiskEngine(),
        Scheduler(),
    )

    memory.save_memory("AI Fleet Commander started")

    # Demo market snapshot (replace with live data later via DataFeed)
    feed.set_snapshot(
        regime="BULL",
        sentiment="POSITIVE",
        volatility=15,
    )

    result = run_cycle(
        feed, market, commander, guards, engines, manager, memory
    )

    print("\n=== FLEET MODE ===")
    print(result["mode"])

    print("\n=== MARKET ===")
    print(result["market"])

    print("\n=== BOTS ===")
    for status in result.get("bots", []):
        print(status)

    print("\n=== RANKING ===")
    print(result.get("ranking"))

    print("\n=== ALLOCATIONS ===")
    print(result.get("allocations"))

    print("\n=== RISK ===")
    print(result.get("risk"))

    print("\n=== MEMORY ===")
    print(memory.get_memory())


if __name__ == "__main__":
    main()
