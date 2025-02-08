import json
from web3 import Web3
from eth_account import Account
from eth_abi.codec import ABICodec
#from eth_abi import encode_abi
from uniswap_universal_router_decoder import FunctionRecipient, RouterCodec
from eth_account.signers.local import LocalAccount
import time

# 🚀 Uniswap V4 Universal Router Addresses for Each Chain
ROUTER_ADDRESSES = {
    "ethereum": "0x66a9893cc07d91d95644aedd05d03f95e1dba8af",
    "base": "0x6ff5693b99212da76ad316178a184ab56d299b43",  # Replace with Base UniswapV4 router address
    "optimism": "0x851116d9223fabed8e56c0e6b8ad0c31d98b3507",  # Replace with Optimism UniswapV4 router address
    "polygon": "0x1095692a6237d83c6a72f3f5efedb9a670c49223",  # Replace with Polygon UniswapV4 router address
    "arbitrum": "0xa51afafe0263b40edaef0df8781ea9aa03e381a3",  # Replace with Arbitrum UniswapV4 router address
}

# ✅ Universal Router ABI (Stored as JSON String)
UNIVERSAL_ROUTER_ABI_JSON = "[{\"inputs\":[{\"components\":[{\"internalType\":\"address\",\"name\":\"permit2\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"weth9\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"v2Factory\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"v3Factory\",\"type\":\"address\"},{\"internalType\":\"bytes32\",\"name\":\"pairInitCodeHash\",\"type\":\"bytes32\"},{\"internalType\":\"bytes32\",\"name\":\"poolInitCodeHash\",\"type\":\"bytes32\"},{\"internalType\":\"address\",\"name\":\"v4PoolManager\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"v3NFTPositionManager\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"v4PositionManager\",\"type\":\"address\"}],\"internalType\":\"struct RouterParameters\",\"name\":\"params\",\"type\":\"tuple\"}],\"stateMutability\":\"nonpayable\",\"type\":\"constructor\"},{\"inputs\":[],\"name\":\"BalanceTooLow\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"ContractLocked\",\"type\":\"error\"},{\"inputs\":[{\"internalType\":\"Currency\",\"name\":\"currency\",\"type\":\"address\"}],\"name\":\"DeltaNotNegative\",\"type\":\"error\"},{\"inputs\":[{\"internalType\":\"Currency\",\"name\":\"currency\",\"type\":\"address\"}],\"name\":\"DeltaNotPositive\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"ETHNotAccepted\",\"type\":\"error\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"commandIndex\",\"type\":\"uint256\"},{\"internalType\":\"bytes\",\"name\":\"message\",\"type\":\"bytes\"}],\"name\":\"ExecutionFailed\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"FromAddressIsNotOwner\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"InputLengthMismatch\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"InsufficientBalance\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"InsufficientETH\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"InsufficientToken\",\"type\":\"error\"},{\"inputs\":[{\"internalType\":\"bytes4\",\"name\":\"action\",\"type\":\"bytes4\"}],\"name\":\"InvalidAction\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"InvalidBips\",\"type\":\"error\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"commandType\",\"type\":\"uint256\"}],\"name\":\"InvalidCommandType\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"InvalidEthSender\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"InvalidPath\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"InvalidReserves\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"LengthMismatch\",\"type\":\"error\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"tokenId\",\"type\":\"uint256\"}],\"name\":\"NotAuthorizedForToken\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"NotPoolManager\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"OnlyMintAllowed\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"SliceOutOfBounds\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"TransactionDeadlinePassed\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"UnsafeCast\",\"type\":\"error\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"action\",\"type\":\"uint256\"}],\"name\":\"UnsupportedAction\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"V2InvalidPath\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"V2TooLittleReceived\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"V2TooMuchRequested\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"V3InvalidAmountOut\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"V3InvalidCaller\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"V3InvalidSwap\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"V3TooLittleReceived\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"V3TooMuchRequested\",\"type\":\"error\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"minAmountOutReceived\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"amountReceived\",\"type\":\"uint256\"}],\"name\":\"V4TooLittleReceived\",\"type\":\"error\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"maxAmountInRequested\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"amountRequested\",\"type\":\"uint256\"}],\"name\":\"V4TooMuchRequested\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"V3_POSITION_MANAGER\",\"outputs\":[{\"internalType\":\"contract INonfungiblePositionManager\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"V4_POSITION_MANAGER\",\"outputs\":[{\"internalType\":\"contract IPositionManager\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"bytes\",\"name\":\"commands\",\"type\":\"bytes\"},{\"internalType\":\"bytes[]\",\"name\":\"inputs\",\"type\":\"bytes[]\"}],\"name\":\"execute\",\"outputs\":[],\"stateMutability\":\"payable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"bytes\",\"name\":\"commands\",\"type\":\"bytes\"},{\"internalType\":\"bytes[]\",\"name\":\"inputs\",\"type\":\"bytes[]\"},{\"internalType\":\"uint256\",\"name\":\"deadline\",\"type\":\"uint256\"}],\"name\":\"execute\",\"outputs\":[],\"stateMutability\":\"payable\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"msgSender\",\"outputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"poolManager\",\"outputs\":[{\"internalType\":\"contract IPoolManager\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"int256\",\"name\":\"amount0Delta\",\"type\":\"int256\"},{\"internalType\":\"int256\",\"name\":\"amount1Delta\",\"type\":\"int256\"},{\"internalType\":\"bytes\",\"name\":\"data\",\"type\":\"bytes\"}],\"name\":\"uniswapV3SwapCallback\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"bytes\",\"name\":\"data\",\"type\":\"bytes\"}],\"name\":\"unlockCallback\",\"outputs\":[{\"internalType\":\"bytes\",\"name\":\"\",\"type\":\"bytes\"}],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"stateMutability\":\"payable\",\"type\":\"receive\"}]"

# ✅ Permit2 ABI (Stored as JSON String)
PERMIT2_ABI_JSON = "[{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"deadline\",\"type\":\"uint256\"}],\"name\":\"AllowanceExpired\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"ExcessiveInvalidation\",\"type\":\"error\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"amount\",\"type\":\"uint256\"}],\"name\":\"InsufficientAllowance\",\"type\":\"error\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"maxAmount\",\"type\":\"uint256\"}],\"name\":\"InvalidAmount\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"InvalidContractSignature\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"InvalidNonce\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"InvalidSignature\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"InvalidSignatureLength\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"InvalidSigner\",\"type\":\"error\"},{\"inputs\":[],\"name\":\"LengthMismatch\",\"type\":\"error\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"signatureDeadline\",\"type\":\"uint256\"}],\"name\":\"SignatureExpired\",\"type\":\"error\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"owner\",\"type\":\"address\"},{\"indexed\":true,\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"},{\"indexed\":true,\"internalType\":\"address\",\"name\":\"spender\",\"type\":\"address\"},{\"indexed\":false,\"internalType\":\"uint160\",\"name\":\"amount\",\"type\":\"uint160\"},{\"indexed\":false,\"internalType\":\"uint48\",\"name\":\"expiration\",\"type\":\"uint48\"}],\"name\":\"Approval\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"owner\",\"type\":\"address\"},{\"indexed\":false,\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"},{\"indexed\":false,\"internalType\":\"address\",\"name\":\"spender\",\"type\":\"address\"}],\"name\":\"Lockdown\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"owner\",\"type\":\"address\"},{\"indexed\":true,\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"},{\"indexed\":true,\"internalType\":\"address\",\"name\":\"spender\",\"type\":\"address\"},{\"indexed\":false,\"internalType\":\"uint48\",\"name\":\"newNonce\",\"type\":\"uint48\"},{\"indexed\":false,\"internalType\":\"uint48\",\"name\":\"oldNonce\",\"type\":\"uint48\"}],\"name\":\"NonceInvalidation\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"owner\",\"type\":\"address\"},{\"indexed\":true,\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"},{\"indexed\":true,\"internalType\":\"address\",\"name\":\"spender\",\"type\":\"address\"},{\"indexed\":false,\"internalType\":\"uint160\",\"name\":\"amount\",\"type\":\"uint160\"},{\"indexed\":false,\"internalType\":\"uint48\",\"name\":\"expiration\",\"type\":\"uint48\"},{\"indexed\":false,\"internalType\":\"uint48\",\"name\":\"nonce\",\"type\":\"uint48\"}],\"name\":\"Permit\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"owner\",\"type\":\"address\"},{\"indexed\":false,\"internalType\":\"uint256\",\"name\":\"word\",\"type\":\"uint256\"},{\"indexed\":false,\"internalType\":\"uint256\",\"name\":\"mask\",\"type\":\"uint256\"}],\"name\":\"UnorderedNonceInvalidation\",\"type\":\"event\"},{\"inputs\":[],\"name\":\"DOMAIN_SEPARATOR\",\"outputs\":[{\"internalType\":\"bytes32\",\"name\":\"\",\"type\":\"bytes32\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"}],\"name\":\"allowance\",\"outputs\":[{\"internalType\":\"uint160\",\"name\":\"amount\",\"type\":\"uint160\"},{\"internalType\":\"uint48\",\"name\":\"expiration\",\"type\":\"uint48\"},{\"internalType\":\"uint48\",\"name\":\"nonce\",\"type\":\"uint48\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"spender\",\"type\":\"address\"},{\"internalType\":\"uint160\",\"name\":\"amount\",\"type\":\"uint160\"},{\"internalType\":\"uint48\",\"name\":\"expiration\",\"type\":\"uint48\"}],\"name\":\"approve\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"spender\",\"type\":\"address\"},{\"internalType\":\"uint48\",\"name\":\"newNonce\",\"type\":\"uint48\"}],\"name\":\"invalidateNonces\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"wordPos\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"mask\",\"type\":\"uint256\"}],\"name\":\"invalidateUnorderedNonces\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"components\":[{\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"spender\",\"type\":\"address\"}],\"internalType\":\"struct IAllowanceTransfer.TokenSpenderPair[]\",\"name\":\"approvals\",\"type\":\"tuple[]\"}],\"name\":\"lockdown\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"nonceBitmap\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"owner\",\"type\":\"address\"},{\"components\":[{\"components\":[{\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"},{\"internalType\":\"uint160\",\"name\":\"amount\",\"type\":\"uint160\"},{\"internalType\":\"uint48\",\"name\":\"expiration\",\"type\":\"uint48\"},{\"internalType\":\"uint48\",\"name\":\"nonce\",\"type\":\"uint48\"}],\"internalType\":\"struct IAllowanceTransfer.PermitDetails[]\",\"name\":\"details\",\"type\":\"tuple[]\"},{\"internalType\":\"address\",\"name\":\"spender\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"sigDeadline\",\"type\":\"uint256\"}],\"internalType\":\"struct IAllowanceTransfer.PermitBatch\",\"name\":\"permitBatch\",\"type\":\"tuple\"},{\"internalType\":\"bytes\",\"name\":\"signature\",\"type\":\"bytes\"}],\"name\":\"permit\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"owner\",\"type\":\"address\"},{\"components\":[{\"components\":[{\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"},{\"internalType\":\"uint160\",\"name\":\"amount\",\"type\":\"uint160\"},{\"internalType\":\"uint48\",\"name\":\"expiration\",\"type\":\"uint48\"},{\"internalType\":\"uint48\",\"name\":\"nonce\",\"type\":\"uint48\"}],\"internalType\":\"struct IAllowanceTransfer.PermitDetails\",\"name\":\"details\",\"type\":\"tuple\"},{\"internalType\":\"address\",\"name\":\"spender\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"sigDeadline\",\"type\":\"uint256\"}],\"internalType\":\"struct IAllowanceTransfer.PermitSingle\",\"name\":\"permitSingle\",\"type\":\"tuple\"},{\"internalType\":\"bytes\",\"name\":\"signature\",\"type\":\"bytes\"}],\"name\":\"permit\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"components\":[{\"components\":[{\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"amount\",\"type\":\"uint256\"}],\"internalType\":\"struct ISignatureTransfer.TokenPermissions\",\"name\":\"permitted\",\"type\":\"tuple\"},{\"internalType\":\"uint256\",\"name\":\"nonce\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"deadline\",\"type\":\"uint256\"}],\"internalType\":\"struct ISignatureTransfer.PermitTransferFrom\",\"name\":\"permit\",\"type\":\"tuple\"},{\"components\":[{\"internalType\":\"address\",\"name\":\"to\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"requestedAmount\",\"type\":\"uint256\"}],\"internalType\":\"struct ISignatureTransfer.SignatureTransferDetails\",\"name\":\"transferDetails\",\"type\":\"tuple\"},{\"internalType\":\"address\",\"name\":\"owner\",\"type\":\"address\"},{\"internalType\":\"bytes\",\"name\":\"signature\",\"type\":\"bytes\"}],\"name\":\"permitTransferFrom\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"components\":[{\"components\":[{\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"amount\",\"type\":\"uint256\"}],\"internalType\":\"struct ISignatureTransfer.TokenPermissions[]\",\"name\":\"permitted\",\"type\":\"tuple[]\"},{\"internalType\":\"uint256\",\"name\":\"nonce\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"deadline\",\"type\":\"uint256\"}],\"internalType\":\"struct ISignatureTransfer.PermitBatchTransferFrom\",\"name\":\"permit\",\"type\":\"tuple\"},{\"components\":[{\"internalType\":\"address\",\"name\":\"to\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"requestedAmount\",\"type\":\"uint256\"}],\"internalType\":\"struct ISignatureTransfer.SignatureTransferDetails[]\",\"name\":\"transferDetails\",\"type\":\"tuple[]\"},{\"internalType\":\"address\",\"name\":\"owner\",\"type\":\"address\"},{\"internalType\":\"bytes\",\"name\":\"signature\",\"type\":\"bytes\"}],\"name\":\"permitTransferFrom\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"components\":[{\"components\":[{\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"amount\",\"type\":\"uint256\"}],\"internalType\":\"struct ISignatureTransfer.TokenPermissions\",\"name\":\"permitted\",\"type\":\"tuple\"},{\"internalType\":\"uint256\",\"name\":\"nonce\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"deadline\",\"type\":\"uint256\"}],\"internalType\":\"struct ISignatureTransfer.PermitTransferFrom\",\"name\":\"permit\",\"type\":\"tuple\"},{\"components\":[{\"internalType\":\"address\",\"name\":\"to\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"requestedAmount\",\"type\":\"uint256\"}],\"internalType\":\"struct ISignatureTransfer.SignatureTransferDetails\",\"name\":\"transferDetails\",\"type\":\"tuple\"},{\"internalType\":\"address\",\"name\":\"owner\",\"type\":\"address\"},{\"internalType\":\"bytes32\",\"name\":\"witness\",\"type\":\"bytes32\"},{\"internalType\":\"string\",\"name\":\"witnessTypeString\",\"type\":\"string\"},{\"internalType\":\"bytes\",\"name\":\"signature\",\"type\":\"bytes\"}],\"name\":\"permitWitnessTransferFrom\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"components\":[{\"components\":[{\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"amount\",\"type\":\"uint256\"}],\"internalType\":\"struct ISignatureTransfer.TokenPermissions[]\",\"name\":\"permitted\",\"type\":\"tuple[]\"},{\"internalType\":\"uint256\",\"name\":\"nonce\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"deadline\",\"type\":\"uint256\"}],\"internalType\":\"struct ISignatureTransfer.PermitBatchTransferFrom\",\"name\":\"permit\",\"type\":\"tuple\"},{\"components\":[{\"internalType\":\"address\",\"name\":\"to\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"requestedAmount\",\"type\":\"uint256\"}],\"internalType\":\"struct ISignatureTransfer.SignatureTransferDetails[]\",\"name\":\"transferDetails\",\"type\":\"tuple[]\"},{\"internalType\":\"address\",\"name\":\"owner\",\"type\":\"address\"},{\"internalType\":\"bytes32\",\"name\":\"witness\",\"type\":\"bytes32\"},{\"internalType\":\"string\",\"name\":\"witnessTypeString\",\"type\":\"string\"},{\"internalType\":\"bytes\",\"name\":\"signature\",\"type\":\"bytes\"}],\"name\":\"permitWitnessTransferFrom\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"components\":[{\"internalType\":\"address\",\"name\":\"from\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"to\",\"type\":\"address\"},{\"internalType\":\"uint160\",\"name\":\"amount\",\"type\":\"uint160\"},{\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"}],\"internalType\":\"struct IAllowanceTransfer.AllowanceTransferDetails[]\",\"name\":\"transferDetails\",\"type\":\"tuple[]\"}],\"name\":\"transferFrom\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"from\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"to\",\"type\":\"address\"},{\"internalType\":\"uint160\",\"name\":\"amount\",\"type\":\"uint160\"},{\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"}],\"name\":\"transferFrom\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"}]"

# ✅ generic ERC20 Token ABI (Stored as JSON String)
ERC20_ABI_JSON = "[{\"inputs\":[{\"internalType\":\"address\",\"name\":\"_l2Bridge\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"_l1Token\",\"type\":\"address\"},{\"internalType\":\"string\",\"name\":\"_name\",\"type\":\"string\"},{\"internalType\":\"string\",\"name\":\"_symbol\",\"type\":\"string\"}],\"stateMutability\":\"nonpayable\",\"type\":\"constructor\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"owner\",\"type\":\"address\"},{\"indexed\":true,\"internalType\":\"address\",\"name\":\"spender\",\"type\":\"address\"},{\"indexed\":false,\"internalType\":\"uint256\",\"name\":\"value\",\"type\":\"uint256\"}],\"name\":\"Approval\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"_account\",\"type\":\"address\"},{\"indexed\":false,\"internalType\":\"uint256\",\"name\":\"_amount\",\"type\":\"uint256\"}],\"name\":\"Burn\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"_account\",\"type\":\"address\"},{\"indexed\":false,\"internalType\":\"uint256\",\"name\":\"_amount\",\"type\":\"uint256\"}],\"name\":\"Mint\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"from\",\"type\":\"address\"},{\"indexed\":true,\"internalType\":\"address\",\"name\":\"to\",\"type\":\"address\"},{\"indexed\":false,\"internalType\":\"uint256\",\"name\":\"value\",\"type\":\"uint256\"}],\"name\":\"Transfer\",\"type\":\"event\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"owner\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"spender\",\"type\":\"address\"}],\"name\":\"allowance\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"spender\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"amount\",\"type\":\"uint256\"}],\"name\":\"approve\",\"outputs\":[{\"internalType\":\"bool\",\"name\":\"\",\"type\":\"bool\"}],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"account\",\"type\":\"address\"}],\"name\":\"balanceOf\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"_from\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"_amount\",\"type\":\"uint256\"}],\"name\":\"burn\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"decimals\",\"outputs\":[{\"internalType\":\"uint8\",\"name\":\"\",\"type\":\"uint8\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"spender\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"subtractedValue\",\"type\":\"uint256\"}],\"name\":\"decreaseAllowance\",\"outputs\":[{\"internalType\":\"bool\",\"name\":\"\",\"type\":\"bool\"}],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"spender\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"addedValue\",\"type\":\"uint256\"}],\"name\":\"increaseAllowance\",\"outputs\":[{\"internalType\":\"bool\",\"name\":\"\",\"type\":\"bool\"}],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"l1Token\",\"outputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"l2Bridge\",\"outputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"_to\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"_amount\",\"type\":\"uint256\"}],\"name\":\"mint\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"name\",\"outputs\":[{\"internalType\":\"string\",\"name\":\"\",\"type\":\"string\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"bytes4\",\"name\":\"_interfaceId\",\"type\":\"bytes4\"}],\"name\":\"supportsInterface\",\"outputs\":[{\"internalType\":\"bool\",\"name\":\"\",\"type\":\"bool\"}],\"stateMutability\":\"pure\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"symbol\",\"outputs\":[{\"internalType\":\"string\",\"name\":\"\",\"type\":\"string\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"totalSupply\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"recipient\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"amount\",\"type\":\"uint256\"}],\"name\":\"transfer\",\"outputs\":[{\"internalType\":\"bool\",\"name\":\"\",\"type\":\"bool\"}],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"sender\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"recipient\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"amount\",\"type\":\"uint256\"}],\"name\":\"transferFrom\",\"outputs\":[{\"internalType\":\"bool\",\"name\":\"\",\"type\":\"bool\"}],\"stateMutability\":\"nonpayable\",\"type\":\"function\"}]"

# ✅ Convert JSON ABIs into Python Objects
UNIVERSAL_ROUTER_ABI = json.loads(UNIVERSAL_ROUTER_ABI_JSON)
PERMIT2_ABI = json.loads(PERMIT2_ABI_JSON)
ERC20_ABI = json.loads(ERC20_ABI_JSON)

class Uniswap:
    def __init__(self, wallet_address, private_key, provider, web3):
        self.w3=web3
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.address = Web3.to_checksum_address(wallet_address)  # This is what was missing

        self.w3 = web3 if web3 else Web3(Web3.HTTPProvider(provider))
        assert self.w3.is_connected(), "❌ Web3 connection failed"

        # 🟢 Auto-select correct UniswapV4 Universal Router based on L2
        self.chain = self.get_chain_from_provider(provider)
        if self.chain not in ROUTER_ADDRESSES:
            raise ValueError(f"❌ Unsupported chain: {self.chain}")

        self.router_address = Web3.to_checksum_address(ROUTER_ADDRESSES[self.chain])
        self.router = self.w3.eth.contract(address=self.router_address, abi=UNIVERSAL_ROUTER_ABI)

        self.permit2 = self.w3.eth.contract(address=Web3.to_checksum_address("0x000000000022D473030F116dDEE9F6B43aC78BA3"), abi=PERMIT2_ABI)

        # Check for stuck transaction
        stuck_nonce = self.check_for_stuck_transactions()
        if stuck_nonce is not None:
            print("stuck transaction detected")
            self.cancel_transaction(stuck_nonce)
        else:
            print("No stuck transactions to cancel")
            time.sleep(1)
#        stuck_nonce = 1  # Explicitly set the known stuck nonce
#        self.cancel_transaction(stuck_nonce)


    def get_chain_from_provider(self, provider_url):
        """Detects the blockchain network from the provider URL."""
        if "base" in provider_url:
            return "base"
        elif "optimism" in provider_url:
            return "optimism"
        elif "polygon" in provider_url:
            return "polygon"
        elif "arbitrum" in provider_url:
            return "arbitrum"
        else:
            return "ethereum"

    def get_token_decimals(self, token_address):
        token_contract = self.w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
        return token_contract.functions.decimals().call()

    def approve_permit2(self, token_address, amount):
        """
        Approve the Permit2 contract to spend tokens (one-time approval)
        """
        token_address = Web3.to_checksum_address(token_address)
        token_contract = self.w3.eth.contract(
            address=token_address, 
            abi=ERC20_ABI
        )
        
        # Set max approval amount
        max_approval = 2**256 - 1  # max uint256
        
        # Build approval transaction
        contract_function = token_contract.functions.approve(
            self.permit2.address,
            max_approval
        )
        
        gas_params = self.calculate_gas_parameters(estimated_gas_limit=500000)
        if not gas_params or not gas_params['has_sufficient_balance']:
            return False

        tx_params = contract_function.build_transaction({
            "from": self.account.address,
            "gas": gas_params['estimated_total_wei'],
            "maxPriorityFeePerGas": gas_params['max_priority_fee_per_gas'],
            "maxFeePerGas": gas_params['max_fee_per_gas'],
            "type": 2,
            "chainId": self.w3.eth.chain_id,
            "value": 0,
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
        })
        
        signed_tx = self.w3.eth.account.sign_transaction(tx_params, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Permit2 token approve transaction hash: {tx_hash.hex()}")
        
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            if receipt.status == 1:
                print("Approval transaction confirmed")
                time.sleep(2)  # Wait for state update
                return True
        except Exception as e:
            print(f"Error waiting for approval: {str(e)}")
        return False

    def create_permit_signature(self, token_address):
        """
        Create a Permit2 signature for a specific transaction (needed for each swap)
        """
        token_address = Web3.to_checksum_address(token_address)
        permit2_contract = self.w3.eth.contract(address=self.permit2.address, abi=PERMIT2_ABI)
        
        p2_amount, p2_expiration, p2_nonce = permit2_contract.functions.allowance(
            self.wallet_address,
            token_address,
            self.router_address
        ).call()
        
        print("p2_amount, p2_expiration, p2_nonce: ", p2_amount, p2_expiration, p2_nonce)
        
        codec = RouterCodec()
        allowance_amount = 2**160 - 1  # max/infinite
        permit_data, signable_message = codec.create_permit2_signable_message(
            token_address,
            allowance_amount,
            codec.get_default_expiration(),
            p2_nonce,
            self.router_address,
            codec.get_default_deadline(),
            self.w3.eth.chain_id,
        )
        signed_message = self.account.sign_message(signable_message)
        return permit_data, signed_message

    def check_permit2_allowance(self, token_address):
        """
        Check if token has already been approved for Permit2
        Returns: True if sufficient allowance exists, False otherwise
        """
        token_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address), 
            abi=ERC20_ABI
        )
        
        # Check allowance for Permit2 contract
        permit2_allowance = token_contract.functions.allowance(
            self.wallet_address,
            self.permit2.address
        ).call()
        
        print(f"Current Permit2 allowance: {permit2_allowance}")
        
        # Check if allowance is effectively infinite (very large number)
        LARGE_APPROVAL_THRESHOLD = 2**200  # Any number larger than this is considered "infinite"
        
        return permit2_allowance > LARGE_APPROVAL_THRESHOLD

    def make_trade(self, from_token, to_token, amount, fee, slippage, pool_version="v3"):
        """
        Execute an exact input swap using Universal Router with RouterCodec.
        
        Args:
            from_token (str): Address of token to swap from
            to_token (str): Address of token to swap to
            amount (int): Amount in wei (already converted to smallest unit)
            fee (int): Fee tier (e.g., 3000 for 0.3%)
            slippage (float): Slippage tolerance in percent
        """
        # Convert addresses to checksum format
        from_token = Web3.to_checksum_address(from_token)
        
        # Check token balance first
        token_contract = self.w3.eth.contract(address=from_token, abi=ERC20_ABI)
        decimals_in = self.get_token_decimals(from_token)
        print(f"Input amount in wei: {amount}")
        print(f"Input amount in token: {amount / (10 ** decimals_in)}")
        print(f"Token decimals: {decimals_in}")

        balance = token_contract.functions.balanceOf(self.wallet_address).call()
        print(f"Token balance in wei: {balance}")
        print(f"Token balance in token: {balance / (10 ** decimals_in)}")
        
        if balance < amount:
            raise ValueError(f"Insufficient balance. Have: {balance / (10 ** decimals_in)}, Need: {amount / (10 ** decimals_in)}")

        # Check for existing Permit2 approval
        has_permit2_allowance = self.check_permit2_allowance(from_token)
        if not has_permit2_allowance:
            print("Permit2 approval needed. Initiating approval...")
            approval_success = self.approve_permit2(from_token, amount)
            if not approval_success:
                print("Failed to get Permit2 approval")
                return None
            time.sleep(2)  # Wait for approval to be mined
        else:
            print("Sufficient Permit2 allowance already exists")
        
        # Create permit signature for the swap
        permit_data, signed_message = self.create_permit_signature(from_token)
        if not permit_data or not signed_message:
            print("Failed to create permit signature")
            return None

        print(f"permit_data: {permit_data}")
        print(f"signed_message: {signed_message}")
        print(f"amount_in_wei: {amount}")

        # Continue with swap logic...
        to_token = Web3.to_checksum_address(to_token)

        # Since amount is already in wei, we don't need to convert it
        amount_in_wei = amount
        
        # Get token decimals for display purposes only
        decimals_in = self.get_token_decimals(from_token)
        print(f"Input amount in wei: {amount_in_wei}")
        print(f"Input amount in token: {amount_in_wei / (10 ** decimals_in)}")
        print(f"Token decimals: {decimals_in}")

        # Initialize codec
        codec = RouterCodec()

        #add slippage and correct min_amount_out with calculation using uniswap quoters
        min_amount_out = 0

        # Get deadline (current block timestamp + 300 seconds)
        deadline = self.w3.eth.get_block("latest")["timestamp"] + 300
        
        if pool_version.lower() == "v3":
            # Encode V3 swap
            encoded_data = (
                codec.encode.chain()
                .permit2_permit(permit_data,
                signed_message)
                .v3_swap_exact_in(
                FunctionRecipient.SENDER,
                amount_in_wei,
                min_amount_out,
                [
                    from_token,
                    fee,
                    to_token,
                ],
                ).build(deadline)
            )
            print(f"amount_in_wei: {amount_in_wei}")
        elif pool_version.lower() == "v4":
            # Encode V4 swap
            tick_spacing = 60  # Default tick spacing, adjust if needed
            
            pool_key = codec.encode.v4_pool_key(
                from_token,
                to_token,
                fee,
                tick_spacing,
            )
            
            # Determine if input is native token (ETH/MATIC)
            is_native_input = from_token.lower() == "0x0000000000000000000000000000000000000000"
            
            encoded_data = (
                codec.encode.chain()
                .v4_swap()
                .swap_exact_in_single(
                    pool_key=pool_key,
                    zero_for_one=True,
                    amount_in=amount_in_wei,
                    amount_out_min=min_amount_out,
                )
                .take_all(to_token, 0)
                .settle_all(from_token, amount_in_wei)
                .build_v4_swap()
                .build_transaction(self.account.address, amount_in_wei if is_native_input else 0, ur_address=self.router_address)
            )
        
        else:
            raise ValueError("Unsupported pool_version. Use 'v3' or 'v4'.")
        
        #calculate gas parameters with estimated gas limit for a permit
        gas_params = self.calculate_gas_parameters(estimated_gas_limit=500000)  # Higher gas limit for swaps
        
        if not gas_params or not gas_params['has_sufficient_balance']:
            return None
        # Build transaction
        tx = {
            "from": self.account.address,
            "to": self.router_address,
            "data": encoded_data,
            "value": amount_in_wei if from_token.lower() == "0x0000000000000000000000000000000000000000" else 0,
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
            "gas": gas_params['estimated_total_wei'],  # Use estimated gas from gas_params
            "maxFeePerGas": gas_params['max_fee_per_gas'],
            "maxPriorityFeePerGas": gas_params['max_priority_fee_per_gas'],
            "type": 2,  # EIP-1559 transaction type
            "chainId": self.w3.eth.chain_id
        }
        
        # Sign and send transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        return tx_hash
  
    def cancel_transaction(self, stuck_nonce):
        """
        Cancel stuck transaction by sending 0 ETH to self
        """
        # First, get the original stuck transaction
        try:

            # Get current gas values
            base_fee = self.w3.eth.get_block("latest")["baseFeePerGas"]
            priority_fee = self.w3.eth.max_priority_fee

            # Apply different multipliers
            base_multiplier = 8   # High multiplier to prevent underpricing
            priority_multiplier = 5  # Lower multiplier for miner tips

            new_max_fee_per_gas = max(base_fee * base_multiplier + priority_fee * 3, Web3.to_wei(0.1, "gwei"))  
            new_max_priority_fee = max(priority_fee * priority_multiplier, Web3.to_wei(0.005, "gwei"))

            # Estimate gas required
            gas_limit = 21000  # Example gas limit for a swap

            # ✅ Correct Total Gas Cost Calculation
            total_gas_wei = gas_limit * new_max_fee_per_gas
            total_gas_eth = Web3.from_wei(total_gas_wei, "ether")

            print(f"🟢 Estimated Total Gas Cost: {total_gas_eth} ETH")
            print(f"🔹 Max Fee per Gas: {Web3.from_wei(new_max_fee_per_gas, 'gwei')} Gwei")
            print(f"🔹 Max Priority Fee per Gas: {Web3.from_wei(new_max_priority_fee, 'gwei')} Gwei")

            # Check if we have enough balance
            balance = self.w3.eth.get_balance(self.account.address)

            print(f"\nCurrent balance: {Web3.from_wei(balance, 'ether')} ETH")
            print(f"Required balance: {(total_gas_eth, 'ether')} ETH")

            if balance < total_gas_wei:
                print(f"ERROR: Insufficient balance for cancellation!")
                print(f"Need {(total_gas_eth - Web3.from_wei(balance), 'ether')} more ETH")
                return

            cancel_tx = {
                "from": self.account.address,
                "to": self.account.address,
                "value": 0,
                "gas": 21000,
                "maxPriorityFeePerGas": new_max_priority_fee,
                "maxFeePerGas": new_max_fee_per_gas,
                "type": 2,
                "chainId": self.w3.eth.chain_id,
                "nonce": stuck_nonce
            }

            print(f"\nAttempting cancellation with:")
            print(f"New Max Fee: {Web3.from_wei(new_max_fee_per_gas, 'gwei')} gwei")
            print(f"New Priority Fee: {Web3.from_wei(new_max_priority_fee, 'gwei')} gwei")

            signed_tx = self.w3.eth.account.sign_transaction(cancel_tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"Cancellation transaction hash: {tx_hash.hex()}")

        except Exception as e:
            print(f"Error: {str(e)}")
            print("Consider sending more ETH to cover higher gas fees")

    def check_for_stuck_transactions(self):
        """
        Check for stuck transactions by comparing pending vs latest nonce
        Returns: stuck nonce if found, None if no stuck transactions
        """
        try:
            pending_nonce = self.w3.eth.get_transaction_count(self.account.address, 'pending')
            latest_nonce = self.w3.eth.get_transaction_count(self.account.address, 'latest')
            
            print(f"Pending nonce: {pending_nonce}")
            print(f"Latest nonce: {latest_nonce}")
            
            if pending_nonce > latest_nonce:
                print(f"Found stuck transaction with nonce {latest_nonce}")
                return latest_nonce
            else:
                print("No stuck transactions found")
                return None
            
        except Exception as e:
            print(f"Error checking for stuck transactions: {e}")
            return None

    def calculate_gas_parameters(self, estimated_gas_limit=21000):
        """
        Calculate optimal gas parameters and check balance sufficiency.
        
        Args:
            estimated_gas_limit (int): Estimated gas limit for the transaction
        
        Returns:
            dict: Gas parameters and status, or None if insufficient balance
            {
                'max_fee_per_gas': int,
                'max_priority_fee_per_gas': int,
                'estimated_total_wei': int,
                'has_sufficient_balance': bool
            }
        """
        try:
            # Get current gas values 
            base_fee = self.w3.eth.get_block("latest")["baseFeePerGas"]
            priority_fee = self.w3.eth.max_priority_fee

            # More efficient multipliers for Base network
            base_multiplier = 1.2   # Reduced from 2
            priority_multiplier = 1.1  # Reduced from 2

            # Calculate new gas prices (in wei) and convert to integers
            new_max_fee_per_gas = int(base_fee * base_multiplier + priority_fee * priority_multiplier)
            new_max_priority_fee = int(priority_fee * priority_multiplier)

            # Set minimum values for Base (in wei)
            min_max_fee = Web3.to_wei(0.003, 'gwei')  # 0.003 gwei minimum
            min_priority_fee = Web3.to_wei(0.001, 'gwei')  # 0.001 gwei minimum

            # Use maximum between calculated and minimum values
            new_max_fee_per_gas = max(new_max_fee_per_gas, min_max_fee)
            new_max_priority_fee = max(new_max_priority_fee, min_priority_fee)

            # Ensure max fee is higher than priority fee
            if new_max_fee_per_gas < new_max_priority_fee:
                new_max_fee_per_gas = new_max_priority_fee * 2

            # Calculate total gas cost
            total_gas_wei = int(estimated_gas_limit * new_max_fee_per_gas)
            total_gas_eth = Web3.from_wei(total_gas_wei, "ether")

            # Get current balance
            balance = self.w3.eth.get_balance(self.account.address)

            # Print gas details
            print(f"\n🟢 Gas Parameters:")
            print(f"🔹 Max Fee per Gas: {Web3.from_wei(new_max_fee_per_gas, 'gwei')} Gwei")
            print(f"🔹 Max Priority Fee per Gas: {Web3.from_wei(new_max_priority_fee, 'gwei')} Gwei")
            print(f"🔹 Estimated Total Gas Cost: {total_gas_eth} ETH")
            print(f"🔹 Current Balance: {Web3.from_wei(balance, 'ether')} ETH")

            has_sufficient_balance = balance >= total_gas_wei
            if not has_sufficient_balance:
                needed_eth = Web3.from_wei(total_gas_wei - balance, "ether")
                print(f"⚠️ ERROR: Insufficient balance!")
                print(f"⚠️ Need {needed_eth} more ETH")

            return {
                'max_fee_per_gas': int(new_max_fee_per_gas),  # Ensure integer
                'max_priority_fee_per_gas': int(new_max_priority_fee),  # Ensure integer
                'estimated_total_wei': int(estimated_gas_limit),  # Ensure integer
                'has_sufficient_balance': has_sufficient_balance
            }

        except Exception as e:
            print(f"Error calculating gas parameters: {str(e)}")
            return None

