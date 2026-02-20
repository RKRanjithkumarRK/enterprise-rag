def store_chunks(collection, chunks, embeddings):
    ids= []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):

        ids.append(f"chunk_{i}")
        documents.append(chunk["text"])

        # ---- CLEAN METADATA ----
        clean_metadata = {}

        for key, value in chunk["metadata"].items():
            if value is not None:
                clean_metadata[key] = str(value) # ensuring string type

        metadatas.append(clean_metadata)


    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )