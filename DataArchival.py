# Setup
cutoff_date = datetime.utcnow() - timedelta(days=90)
query = f"SELECT * FROM c WHERE c.timestamp < '{cutoff_date.isoformat()}'"

# Cosmos DB Setup
cosmos_client = CosmosClient(endpoint, key)
container = cosmos_client.get_database_client("billing-db").get_container_client("records")

# Blob Storage Setup
blob_container = blob_service_client.get_container_client("billing-archive")

# Query with pagination
items = container.query_items(query, enable_cross_partition_query=True)
for page in items.by_page():
    records = list(page)
    blob_name = f"billing_{cutoff_date.strftime('%Y-%m-%d')}_{uuid4()}.json"
    blob_container.upload_blob(name=blob_name, data=json.dumps(records))

    # (Optional) Delete records from Cosmos DB
    for record in records:
        container.delete_item(record["id"], partition_key=record["partitionKey"])
