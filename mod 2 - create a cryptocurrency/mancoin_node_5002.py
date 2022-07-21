# module 2- creating a cryptocurrency

# pip install Flask==0.12.2
# snap install postman
# pip install requests==2.18.4
import datetime
import hashlib
import json
from urllib import response
# get json from request class from flask library
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# part 1 - building a blockchain


class Blockchain:
    def __init__(self):  # constructor for creating genesis block for instance
        self.chain = []
        # this serves as a list of mempool,transactions and consensus makes a blockchain a crypto
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):  # take block as input and return hash sha256
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]  # current block
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '00000':
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver, 'amount': amount})
        previous_block = self.get_previous_block()
        return previous_block['index']+1

    def add_node(self, address):  # self to access nodes variable of type set.
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):

        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False


# part 2 - mining a blockchain
# creating a Web App
app = Flask(__name__)  # create flask based application
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# creating an address for the node on port 5000
node_address = str(uuid4()).replace('-', '')

# creating a Blockchain
blockchain = Blockchain()

# mining a new block


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    print("previous proof is: ", previous_proof)
    new_proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(
        sender=node_address, receiver='Krishna', amount=1)
    block = blockchain.create_block(new_proof, previous_hash)
    # time=(block['timestamp']-previous_block['timestamp']).seconds
    response = {'message': 'Congratulation, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']
                }
    return jsonify(response), 200

# getting the full blockchain


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# checking the validity of the chain


@app.route('/is_valid', methods=['GET'])
def is_valid():
    if blockchain.is_chain_valid(blockchain.chain):
        return jsonify("chain is valid"), 200
    else:
        return jsonify("chain is not valid!"), 200

# Adding a new transaction to the blockchain


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'some elements of the transaction are missing', 400
    index = blockchain.add_transaction(
        json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201

# part 3 - decentralizing our blockchain

#connecting new nodes


@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "no node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {
        'message': 'all the nodes are now connected. The Mancoin blockchain now contain the: ',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201
#replace the chain by longest chain if needed


@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the logest one',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'Nimai, All good, the chain is the largest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200


# running the app
app.run(host='0.0.0.0', port=5002)
