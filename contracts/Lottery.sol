// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";
import "@openzeppelin-contracts/contracts/access/Ownable.sol";

contract LOTTERY is VRFConsumerBase, Ownable {
    bytes32 internal keyHash;
    uint256 fee;
    address link;
    uint256 entranceFeeUsd;
    address payable[] public players;
    LOTTERY_STATE public lottery_state;
    AggregatorV3Interface internal priceFeed;
    bytes32 requestId;
    address payable public recentWinner;
    uint256 public rnd;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    event RequestedRandomness(bytes32 requestId);

    constructor(
        address _vrfCoordinator,
        address _link,
        bytes32 _keyHash,
        uint256 _fee,
        address _priceFeedAddress
    ) VRFConsumerBase(_vrfCoordinator, _link) {
        priceFeed = AggregatorV3Interface(_priceFeedAddress);
        entranceFeeUsd = 50 * (10**18);
        lottery_state = LOTTERY_STATE.CLOSED;
        keyHash = _keyHash;
        fee = _fee;
    }

    function enter() public payable {
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "lottery isn t opened yet!"
        );
        require(msg.value >= getEntranceFee(), "you don t have enough funds!");
        players.push(payable(msg.sender));
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 answer, , , ) = priceFeed.latestRoundData();
        uint256 conversionRate = uint256(answer);
        return (entranceFeeUsd * (10**18)) / conversionRate;
    }

    function start() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "lottery isn t closed yet!"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function end() public onlyOwner {
        require(lottery_state == LOTTERY_STATE.CALCULATING_WINNER);
        requestId = requestRandomness(keyHash, fee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 randomness)
        internal
        override
    {
        require(lottery_state == LOTTERY_STATE.CALCULATING_WINNER);
        rnd = randomness;
        uint256 index = rnd % (players.length);
        recentWinner = players[index];
        recentWinner.transfer((address(this)).balance);
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
    }
}
