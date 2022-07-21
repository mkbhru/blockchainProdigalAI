# pip install Flask==0.12.2
# snap install postman
# module 1-create a Blockchain
import datetime
import hashlib
import json
# from urllib import response
from flask import Flask, jsonify
# part 1 - building a blockchain


class Blockchain:
    def __init__(self):  # constructor for creating genesis block for instance
        self.chain = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
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

# part 2 - mining a blockchain


# creating a Web App
app = Flask(__name__)  # create flask based application
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
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
    block = blockchain.create_block(new_proof, previous_hash)
    # time=(block['timestamp']-previous_block['timestamp']).seconds
    response = {'message': 'Congratulation, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                # 'time':time
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
def ckeck_validity():
    if blockchain.is_chain_valid(blockchain.chain):
        return jsonify("chain is valid"), 200
    else:
        return jsonify("chain is not valid!"), 200


# running the app
app.run(host='0.0.0.0', port=5000)
