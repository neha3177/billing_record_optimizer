def get_billing_record(record_id):
    # First try Cosmos DB (hot tier)
    try:
        record = cosmos_container.read_item(record_id, partition_key=calculate_pk(record_id))
        return record
    except CosmosResourceNotFoundError:
        pass

    # If not found in hot tier, try cold tier (Blob)
    for blob in blob_container.list_blobs(name_starts_with="billing_"):
        blob_data = blob_container.get_blob_client(blob).download_blob().readall()
        records = json.loads(blob_data)
        for record in records:
            if record["id"] == record_id:
                return record

    return {"error": "Record not found"}
