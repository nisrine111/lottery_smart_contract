from scripts.helpful_functions import (
    get_account,
    get_contract,
    get_link_funds,
    LOCAL_ENV,
    FORKED_ENV
)
import time
from brownie import network
import pytest


def test_can_pick_winner(lottery):
    if network.show_active() in LOCAL_ENV:
        pytest.skip()

    account = get_account()
    lottery.start({"from": account})
    lottery.enter(
        {"from": account, "value": lottery.getEntranceFee()}
    )
    lottery.enter(
        {"from": account, "value": lottery.getEntranceFee()}
    )
    get_link_funds(lottery)
    lottery.end({"from": account})
    time.sleep(180)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0