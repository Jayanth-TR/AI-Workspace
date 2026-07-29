class ChunkService:

    def create_chunks(
        self,
        text: str,
        chunk_size: int = 1000,
        overlap: int = 200
    ):

        chunks = []

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end]

            chunks.append(chunk)

            start += chunk_size - overlap

        return chunks