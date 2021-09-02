import json
from json import JSONEncoder
from cryptohash import sha256
import time

class Transaction:
    def __init__(self, from_address, to_address, amount):
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.timestamp = time.time()
        pass
    
    def calculate_hash(self):
        return bytes(sha256('%s%s%s%s' % (self.from_address, self.to_address, self.amount, self.timestamp)), 'utf-8')
    
    def sign_transaction(self, signing_key):
        if signing_key.public_key != self.from_address:
            raise Exception("Cannot sign transaction for other wallet")

        self.signature = signing_key.sign_msg(self.calculate_hash())

    def is_valid(self):
        if self.from_address is None:
            return True

        if not self.signature:
            raise Exception("No signature for this transaction")
        
        msg = self.calculate_hash()
        recovered_public_key = self.signature.recover_public_key_from_msg(msg)
        if self.from_address != recovered_public_key:
            raise Exception("From Address is not correct")
        
        return  self.from_address.verify_msg(msg, self.signature)
    
    def to_string(self):
        return str(self.__dict__) 


class Block:
    def __init__(self, timestamp, transactions , previous_hash=""):
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        if self.transactions:
            stringify = "".join([str(i.__dict__) for i in self.transactions])
            return sha256("%s%s%s%s" % (self.previous_hash, self.timestamp, stringify, self.nonce))
        else:
            return sha256("%s%s%s%s" % (self.previous_hash, self.timestamp, "", self.nonce))
    
    def mind_block(self, difficulty):
        while self.hash[0:difficulty] != "0".zfill(difficulty):
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def has_valid_transactions(self):
        for tran in self.transactions:
            if not tran.is_valid():
                return False

        return True

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.mining_reward = 100
        self.difficulty = 2

    def create_genesis_block(self):
        return Block("2021-09-02", [], '0')
    
    def get_lastest_block(self):
        return self.chain[len(self.chain) - 1]

    def add_transaction(self, transaction):
        if not transaction.from_address or not transaction.to_address:
            raise Exception("Need from address or to address")

        if not transaction.is_valid():
            raise Exception("Transaction is not valid")
        
        if transaction.amount <= 0:
            raise Exception("Transaction amount must be higher than 0")

        if self.get_balance_of_address(transaction.from_address) < transaction.amount:
            raise Exception("Not enough amount")

        self.pending_transactions.append(transaction)


    def get_balance_of_address(self, address):
        balance = 0

        for block in self.chain:
            for tran in block.transactions:
                if tran.from_address == address:
                    balance -= tran.amount

                if tran.to_address == address:
                    balance += tran.amount

        return balance


    def is_chain_valid(self):
        real_genesis_hash = self.create_genesis_block().calculate_hash()

        if (real_genesis_hash != self.chain[0].calculate_hash()):
            return False 
        
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if previous_block.hash != current_block.previous_hash:
                return False 
                
            if not current_block.has_valid_transactions():
                return False
            
            if current_block.hash != current_block.calculate_hash():
                return False

        return True
    
    def mine_pending_transactions(self, mining_reward_address):
        reward_transaction = Transaction(None, mining_reward_address, self.mining_reward)
        
        self.pending_transactions.append(reward_transaction)
        block = Block(time.time(), self.pending_transactions, self.get_lastest_block().hash)

        block.mind_block(self.difficulty)
        self.chain.append(block)
        self.pending_transactions = []

