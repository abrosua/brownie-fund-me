// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol"; // similar to npm import!

// Objective: accept payment
contract FundMe {
    // handle user total payment here
    mapping(address => uint256) public addressToAmountFunded;
    // handle payment history
    struct Payments {
        address senderAddress;
        uint256 sentFund;
        uint256 timestamp;
    }
    Payments[] public paymentHistory;
    address public owner;
    uint256 public minUsd = 5; // minimum fee in USD

    // Chainlink interface - ABI
    AggregatorV3Interface internal dataFeed;

    // ---- constructor: will be executed at the beginning of the contracts,
    // and the variables will be available through the contract
    constructor(address _dataFeed) public {
        /**
         * Network: Sepolia
         * Aggregator: ETH/USD
         * Address: 0x694AA1769357215DE4FAC081bf1f309aDC325306
         */
        dataFeed = AggregatorV3Interface(_dataFeed); // dynamic price feed address
        // this will allow us to MOCK the oracle on local (Ganache) run!
        // set deployer as contract owner
        owner = msg.sender;
    }

    // ---- modifier: similar to Python decorator
    // ownership modifier
    modifier onlyOwner() {
        require(msg.sender == owner, "You are NOT the owner!"); // msg.<something> only works for payable function!
        _; // the function code will be run here, on the under score (_)
    }

    // get the version
    function getVersion() public view returns (uint256) {
        return dataFeed.version();
    }

    // get the latest ETH/USD price
    function getPrice() public view returns (uint256) {
        (
            ,
            /* uint80 roundID */ int answer /*uint startedAt*/ /*uint timeStamp*/ /*uint80 answeredInRound*/, // 181203000000 in 8 decimals (1812.03)
            ,
            ,

        ) = dataFeed.latestRoundData(); // (,int answer,,,) = dataFeed.latestRoundData();
        return uint256(answer); // return in uint
    }

    // get the minimum fee in Wei
    function getEntranceFee() public view returns (uint256) {
        return getUsdToWei(minUsd) + 1;
    }

    // get the conversion rate
    function getUsdToWei(uint256 _usdAmount) public view returns (uint256) {
        return (_usdAmount * (10 ** 26)) / getPrice();
    }

    // payable (RED) function, allow user to interact with payment on this function!
    function fund() public payable {
        // msg.sender: the user/sender (the one that call the function) address
        // msg.value: amount of token sent/paid

        // set minimum payment, in other currency (e.g., USD)
        uint256 minWei = getUsdToWei(minUsd);
        // revert function/transaction if the paid fund is below the minimum USD
        require(msg.value >= minWei, "Please spend more ETH!"); // refund if not fulfilled!

        // store the funds here
        addressToAmountFunded[msg.sender] += msg.value;
        paymentHistory.push(Payments(msg.sender, msg.value, block.timestamp)); // current block timestamp
    }

    // withdrawal function
    function withdraw() public payable onlyOwner {
        payable(msg.sender).transfer(address(this).balance);
        // reset all balance into zero after a successful withdrawal!
        for (
            uint256 funderIndex = 0;
            funderIndex < paymentHistory.length;
            funderIndex++
        ) {
            address funder = paymentHistory[funderIndex].senderAddress; // get funder address
            addressToAmountFunded[funder] = 0; // reset funder total funds to zero
        }
        delete paymentHistory;
        assert(paymentHistory.length == 0);
    }
}
