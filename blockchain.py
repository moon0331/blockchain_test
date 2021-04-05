import hashlib
import json
import time

from textwrap import dedent
from uuid import uuid4

from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transcactions = []

        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index' : len(self.chain)+ 1,
            'timestamp' : time.time(),
            'transactions' : self.current_transcactions,
            'proof' : proof,
            'previous_hash' : previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transcactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transcactions.append(
            {
                'sender' : sender,
                'recipient' : recipient,
                'amount' : amount,
            }
        )

        return self.last_block['index'] + 1

    def net_block(self):
        pass

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
    
        return proof
    
    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'

    @staticmethod
    def hash(block): # hash of block
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self): # last chain block
        return self.chain[-1]

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # 블록 채굴에 대한 보상을 설정한다.
    # 송신자를 0으로 표현한 것은 블록 채굴에 대한 보상이기 때문이다.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # 체인에 새로운 블록을 추가하는 코드이다. 
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200
  
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # 필요한 값이 모두 존재하는지 확인하는 과정이다.
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # 새로운 거래를 추가한다.
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

    # https://medium.com/caulink/파이썬으로-블록체인-만들기-part-2-633bb0555221