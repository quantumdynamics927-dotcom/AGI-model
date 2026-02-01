require("dotenv").config();
require("@nomicfoundation/hardhat-toolbox");

const { POLYGON_RPC_URL, POLYGON_MAINNET_URL, AMOY_RPC_URL, PRIVATE_KEY, POLYGONSCAN_API_KEY } = process.env;

// Normalize accounts array and ensure 0x prefix if needed
const ACCOUNTS = PRIVATE_KEY ? [(PRIVATE_KEY.startsWith('0x') ? PRIVATE_KEY : `0x${PRIVATE_KEY}`)] : [];

module.exports = {
  defaultNetwork: 'hardhat',
  solidity: "0.8.20",
  networks: {
    amoy: {
      url: AMOY_RPC_URL || "https://polygon-amoy.g.alchemy.com/v2/your-api-key",
      accounts: ACCOUNTS,
      chainId: 80002,
    },
    polygonAmoy: {
      url: AMOY_RPC_URL || "https://polygon-amoy.g.alchemy.com/v2/your-api-key",
      accounts: ACCOUNTS,
      chainId: 80002,
    },
    mumbai: {
      url: POLYGON_RPC_URL || "https://polygon-mumbai.g.alchemy.com/v2/your-api-key",
      accounts: ACCOUNTS,
      chainId: 80001,
    },
    polygon: {
      url: POLYGON_MAINNET_URL || POLYGON_RPC_URL || "https://polygon-mainnet.alchemyapi.io/v2/your-api-key",
      accounts: ACCOUNTS,
      chainId: 137,
    },
  },
  etherscan: {
    apiKey: {
      polygon: POLYGONSCAN_API_KEY || "",
      polygonMumbai: POLYGONSCAN_API_KEY || "",
      polygonAmoy: POLYGONSCAN_API_KEY || "",
    },
    customChains: [
      {
        network: "polygonAmoy",
        chainId: 80002,
        urls: {
          apiURL: "https://api-amoy.polygonscan.com/api",
          browserURL: "https://amoy.polygonscan.com"
        }
      }
    ]
  },
};
