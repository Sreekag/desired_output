from pymilvus import connections, Collection

# Connect to Milvus
connections.connect(alias="default", host="localhost", port="19530")

# Load the collection
collection = Collection("document_vectors")

# Load data (if required)
collection.load()

# Print number of entities
print("Number of stored entities:", collection.num_entities)
