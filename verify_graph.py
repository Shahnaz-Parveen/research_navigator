from app import app, db
from models import Document, Entity

def check_graph_data():
    with app.app_context():
        documents = Document.query.all()
        print(f"Total Documents: {len(documents)}")
        
        nodes = []
        edges = []
        concept_map = {}
        concept_counter = 0
        
        for doc in documents:
            doc_node_id = f"doc_{doc.id}"
            nodes.append({"id": doc_node_id, "label": doc.title, "group": "paper"})
            
            entities = doc.entities
            print(f"Doc {doc.id} has {len(list(entities))} entities.")
            
            for entity in entities:
                key = entity.text.lower()
                if key not in concept_map:
                    concept_id = f"conc_{concept_counter}"
                    concept_counter += 1
                    concept_map[key] = concept_id
                    nodes.append({"id": concept_id, "label": entity.text, "group": "entity"})
                else:
                    concept_id = concept_map[key]
                
                edges.append({"from": doc_node_id, "to": concept_id})
                
        print(f"Total Nodes: {len(nodes)}")
        print(f"Total Edges: {len(edges)}")
        if len(nodes) > 0:
            print("Sample Node:", nodes[0])

if __name__ == "__main__":
    check_graph_data()
