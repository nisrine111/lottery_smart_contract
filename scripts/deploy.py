from brownie import LOTTERY,accounts,network,config
from scripts.helpful_functions import get_account,get_contract,get_link_funds,LOCAL_ENV,FORKED_ENV
import time

def deploy_lottery():
    account=get_account()
    vrfCoordinator=get_contract("vrf_coordinator").address
    link=get_contract("link_token").address
    keyHash=config["networks"][network.show_active()]["key_hash"]
    fee=config["networks"][network.show_active()]["fee"]
    priceFeedAddress=get_contract("price_feed").address
    lottery= LOTTERY.deploy(vrfCoordinator,link,keyHash,fee,priceFeedAddress,{"from":account})
    
    print("contract deployed successfully !" )
    return(lottery)

def start_lottery():
    account=get_account()
    lottery=LOTTERY[-1]
    tx=lottery.start({"from":account})
    tx.wait(1)
    print("lottery has started !")

def enter_lottery():
    account=get_account()
    lottery=LOTTERY[-1]
    entrance_value= lottery.getEntranceFee() + 100000000
    tx1=lottery.enter({'from':account,'value':entrance_value})
    tx1.wait(1)
    print('you ve successfully entered the lottery !')

def end_lottery():
    account=get_account()
    lottery=LOTTERY[-1]
    tx3=get_link_funds(lottery.address)


    tx3= lottery.end({'from':account})
    tx3.wait(1)
    time.sleep(180)
    print("the  winner is ", lottery.recentWinner())


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()