from scripts.helpful_functions import (
    get_account,
    get_link_funds,
    get_contract,
    LOCAL_ENV,
)
from brownie import exceptions, network
from web3 import Web3
import pytest


def test_get_entrance_fee(lottery_contract):
    
    if network.show_active() not in LOCAL_ENV:
        pytest.skip()

    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery_contract.getEntranceFee()
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started(lottery_contract):
    
    if network.show_active() not in LOCAL_ENV:
        pytest.skip()

    
    with pytest.raises(exceptions.VirtualMachineError):
        lottery_contract.enter(
            {"from": get_account(), "value": lottery_contract.getEntranceFee()}
        )


def test_can_start_and_enter_lottery(lottery_contract):
    
    if network.show_active() not in LOCAL_ENV:
        pytest.skip()

    account = get_account()
    lottery_contract.start({"from": account})

    lottery_contract.enter(
        {"from": account, "value": lottery_contract.getEntranceFee()}
    )
    
    assert lottery_contract.players(0) == account


def test_can_end_lottery(lottery_contract):
    
    if network.show_active() not in LOCAL_ENV:
        pytest.skip()

    account = get_account()
    lottery_contract.start({"from": account})
    lottery_contract.enter(
        {"from": account, "value": lottery_contract.getEntranceFee()}
    )
    get_link_funds(lottery_contract)
    lottery_contract.end({"from": account})
    assert lottery_contract.lottery_state() == 2


def test_can_pick_winner_correctly(lottery_contract):
    
    if network.show_active() not in LOCAL_ENV:
        pytest.skip()

    account = get_account()
    lottery_contract.start({"from": account})
    lottery_contract.enter(
        {"from": account, "value": lottery_contract.getEntranceFee()}
    )
    lottery_contract.enter(
        {"from": get_account(index=1), "value": lottery_contract.getEntranceFee()}
    )
    lottery_contract.enter(
        {"from": get_account(index=2), "value": lottery_contract.getEntranceFee()}
    )
    get_link_funds(lottery_contract)
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery_contract.balance()
    transaction = lottery_contract.end({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 657
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery_contract.address, {"from": account}
    )
    
    assert lottery_contract.recentWinner() == account
    assert lottery_contract.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery