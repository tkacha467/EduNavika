from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Float, MetaData, Table, JSON
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from backend.app.retrieval.vector_store.base import VectorStore

class PGVectorStore(VectorStore):
    def __init__(self, connection_string: str, dimension: int, table_name: str = "vector_index"):
        self.connection_string = connection_string
        self.dimension = dimension
        self.table_name = table_name
        self.engine = create_engine(connection_string)
        self.metadata_obj = MetaData()
        
        self.vector_table = Table(
            self.table_name,
            self.metadata_obj,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('chunk_id', String(100), nullable=False, index=True),
            Column('embedding', Vector(dimension)),
            Column('metadata', JSON, nullable=True)
        )
        
        # Ensure pgvector extension and table exists
        with self.engine.connect() as conn:
            conn.execute(self.vector_table.metadata.create_all(self.engine))

        self.Session = sessionmaker(bind=self.engine)

    def add(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        if len(embeddings) != len(metadata):
            raise ValueError("Number of embeddings must match number of metadata items")
            
        with self.Session() as session:
            for i in range(len(embeddings)):
                chunk_id = metadata[i].get("chunk_id")
                # Insert the embedding
                ins = self.vector_table.insert().values(
                    chunk_id=chunk_id,
                    embedding=embeddings[i].tolist(),
                    metadata=metadata[i]
                )
                session.execute(ins)
            session.commit()

    def search(self, query_embedding: np.ndarray, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if query_embedding.ndim == 2:
            query_embedding = query_embedding[0]
            
        with self.Session() as session:
            # We use cosine distance operator <=> for pgvector
            query = session.query(
                self.vector_table.c.chunk_id,
                self.vector_table.c.embedding.cosine_distance(query_embedding.tolist()).label("distance"),
                self.vector_table.c.metadata
            )
            
            if filters:
                # Assuming simple equality filters on the JSON metadata
                for k, v in filters.items():
                    query = query.filter(self.vector_table.c.metadata[k].astext == str(v))
                    
            query = query.order_by("distance").limit(top_k)
            
            results = []
            for row in query.all():
                # Score = 1 - distance (for cosine similarity)
                score = 1.0 - float(row.distance)
                results.append({
                    "chunk_id": row.chunk_id,
                    "score": score,
                    "metadata": row.metadata
                })
                
            return results

    def save(self, path: str) -> None:
        # Postgres is already persistent, nothing to save locally
        pass

    def load(self, path: str) -> None:
        # Postgres is already persistent, nothing to load locally
        pass
