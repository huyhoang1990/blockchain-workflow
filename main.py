import blockchain
import eth_keys, os


#https://cryptobook.nakov.com/digital-signatures/ecdsa-sign-verify-examples

if __name__ == "__main__":
    private_token = b"11095597762621126487631879726450"
    my_key = eth_keys.keys.PrivateKey(private_token)
    my_wallet_address = my_key.public_key
    
    chain = blockchain.Blockchain()

    #Create the transaction 1
    #tx1 = blockchain.Transaction(my_wallet_address, 'address2', 100)
    #tx1.sign_transaction(my_key)
    #chain.add_transaction(tx1)
    chain.mine_pending_transactions(my_wallet_address)
    
    print("Balance is %s" % chain.get_balance_of_address(my_wallet_address))
    tx2 = blockchain.Transaction(my_wallet_address, 'address1', 10)
    tx2.sign_transaction(my_key)
    chain.add_transaction(tx2)
    chain.mine_pending_transactions(my_wallet_address)

    print("Balance is %s" % chain.get_balance_of_address(my_wallet_address))

    is_chain_valid = chain.is_chain_valid()
    if is_chain_valid:
        print("Chain is valid")
    else:
        print("Chain is not valid")

