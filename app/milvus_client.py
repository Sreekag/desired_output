# from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection
# import uuid
# from transformers import AutoTokenizer, AutoModel
# import torch
# COLLECTION_NAME = "document_vectors"
# DIMENSION = 768  
# MILVUS_HOST = "localhost"
# MILVUS_PORT = "19530"
# connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
# def initialize_collection():
#     """Initialize the Milvus collection with proper schema and index."""
#     if not utility.has_collection(COLLECTION_NAME):
#         fields = [
#             FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
#             FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
#             FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
#             FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=1024),
#             FieldSchema(name="output_file", dtype=DataType.VARCHAR, max_length=256)
#         ]
        
#         schema = CollectionSchema(
#             fields=fields,
#             description="Document embeddings collection",
#             enable_dynamic_field=False
#         )
#         collection = Collection(
#             name=COLLECTION_NAME,
#             schema=schema,
#             using='default',
#             shards_num=2
#         )
#         index_params = {
#             "index_type": "IVF_FLAT",
#             "metric_type": "L2",
#             "params": {"nlist": 128}
#         }
        
#         collection.create_index(
#             field_name="embedding",
#             index_params=index_params
#         )
        
#         print(f"Collection '{COLLECTION_NAME}' created successfully.")
#         return collection
#     else:
#         print(f"Collection '{COLLECTION_NAME}' already exists.")
#         return Collection(COLLECTION_NAME)
# collection = initialize_collection()
# tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
# model = AutoModel.from_pretrained('distilbert-base-uncased')

# def generate_embedding(text: str) -> list:
#     """Generate embedding using mean pooling of DistilBERT outputs."""
#     inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
#     with torch.no_grad():
#         outputs = model(**inputs)
#     return outputs.last_hidden_state.mean(dim=1).squeeze().tolist()

# def store_embedding(embedding: list, title: str, description: str, output_file: str) -> dict:
#     """Store embedding with metadata in Milvus."""
#     doc_id = uuid.uuid4().int & ((1 << 63) - 1)
#     data = [{
#         "id": doc_id,
#         "embedding": embedding,
#         "title": title,
#         "description": description,
#         "output_file": output_file
#     }]
#     insert_result = collection.insert(data)
#     collection.flush()  
#     return {
#         "status": "success",
#         "insert_count": len(insert_result.primary_keys),
#         "doc_id": doc_id
#     }
# def search_embedding(query_embedding: list, top_k: int = 5) -> list:
#     """Search for similar embeddings in Milvus."""
#     search_params = {
#         "metric_type": "L2",
#         "params": {"nprobe": 16}
#     }
#     results = collection.search(
#         data=[query_embedding],
#         anns_field="embedding",
#         param=search_params,
#         limit=top_k,
#         output_fields=["title", "description", "output_file"]
#     )
#     matches = []
#     for hits in results:
#         for hit in hits:
#             matches.append({
#                 "id": hit.id,
#                 "score": hit.score,
#                 "title": hit.entity.get("title"),
#                 "description": hit.entity.get("description"),
#                 "output_file": hit.entity.get("output_file")
#             })
    
#     return matches

# def get_collection_stats() -> dict:
#     """Get collection statistics."""
#     return {
#         "num_entities": collection.num_entities,
#         "indexes": [index.to_dict() for index in collection.indexes],
#         "schema": collection.schema.to_dict()
#     }
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection
from transformers import AutoTokenizer, AutoModel
import torch

# Milvus connection parameters
COLLECTION_NAME = "document_vectors"
DIMENSION = 768  
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"

# Connect to Milvus
connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

def initialize_collection():
    """Initialize the Milvus collection with proper schema and index."""
    if not utility.has_collection(COLLECTION_NAME):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),  # Let Milvus handle ID
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="output_file", dtype=DataType.VARCHAR, max_length=256)
        ]
        
        schema = CollectionSchema(
            fields=fields,
            description="Document embeddings collection",
            enable_dynamic_field=False
        )
        
        collection = Collection(
            name=COLLECTION_NAME,
            schema=schema,
            using='default',
            shards_num=2
        )

        # Index creation
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        
        collection.create_index(
            field_name="embedding",
            index_params=index_params
        )
        
        print(f"Collection '{COLLECTION_NAME}' created successfully.")
        return collection
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")
        return Collection(COLLECTION_NAME)

collection = initialize_collection()

# Load tokenizer and model for embedding generation
tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
model = AutoModel.from_pretrained('distilbert-base-uncased')

def generate_embedding(text: str) -> list:
    """Generate embedding using mean pooling of DistilBERT outputs."""
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().tolist()

def store_embedding(embedding: list, title: str, description: str, output_file: str) -> dict:
    """Store embedding with metadata in Milvus."""
    # No need to manually generate doc_id, Milvus will auto-generate it
    data = [{
        "embedding": embedding,
        "title": title,
        "description": description,
        "output_file": output_file
    }]
    
    insert_result = collection.insert(data)
    collection.flush()  # Ensure the data is written to disk
    
    return {
        "status": "success",
        "insert_count": len(insert_result.primary_keys),
        "doc_ids": insert_result.primary_keys  # These are the auto-generated IDs
    }

def search_embedding(query_embedding: list, top_k: int = 5) -> list:
    """Search for similar embeddings in Milvus."""
    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 16}
    }
    
    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=["title", "description", "output_file"]
    )
    
    matches = []
    for hits in results:
        for hit in hits:
            matches.append({
                "id": hit.id,
                "score": hit.score,
                "title": hit.entity.get("title"),
                "description": hit.entity.get("description"),
                "output_file": hit.entity.get("output_file")
            })
    
    return matches

def get_collection_stats() -> dict:
    """Get collection statistics."""
    return {
        "num_entities": collection.num_entities,
        "indexes": [index.to_dict() for index in collection.indexes],
        "schema": collection.schema.to_dict()
    }
