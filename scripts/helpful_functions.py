from brownie import LOTTERY, network,accounts,config,MockV3Aggregator,VRFCoordinatorMock,LinkToken,Contract
#mock aggregatorV3Interface linkToken VRFConsumerBase


LOCAL_ENV=["development"]
FORKED_ENV=["mainnet-fork-dev","mainnet-fork"]


def get_account(index=None,id=None):
    if network.show_active() in LOCAL_ENV or network.show_active() in FORKED_ENV:
        return accounts[0]
    elif id:
        return accounts.load(id)
    elif index:
        return accounts[index]
    else:
        return accounts.add(config["wallets"]["from_key"])


# deploying mocks
decimals=8
initial_answer=200000000000

def deploy_mocks(_decimals=decimals,_initial_answer=initial_answer):
    account=get_account()
    MockV3Aggregator.deploy(_decimals,_initial_answer,{'from':account})
    link_token=LinkToken.deploy({'from':account})
    VRFCoordinatorMock.deploy(link_token.address,{'from':account})
    print("Mocks deployed successfully ! ")



# type: str  "price_feed"  "vrf_coordinator"   "link_token"
def get_contract(type):
    mapping={
        "price_feed":MockV3Aggregator,
        "vrf_coordinator":VRFCoordinatorMock,
        "link_token": LinkToken
    }
    if network.show_active() in LOCAL_ENV or network.show_active() in FORKED_ENV:
        if len(mapping[type])<=0 :
            deploy_mocks()
        return mapping[type][-1]

    else:
        # abi and address
        address=config["networks"][network.show_active()][type]
        name=mapping[type]._name
        abi=mapping[type].abi
        contract=Contract.from_abi(name,address,abi)
        return contract



def get_link_funds(contract_address,account=None,link_token=None,amount=0.1*10*18):
    account=account if account else get_account()
    link_token=link_token if link_token else get_contract("link_token")

    tx= link_token.transfer(contract_address,amount)
    tx.wait(1)
    print("contract funded with Link successfully !")
    return tx



