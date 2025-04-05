import matplotlib.pyplot as plt
import networkx as nx

def generate_er_diagram_with_networkx():
    G = nx.DiGraph()
    
    # Добавляем узлы (таблицы)
    tables = ["users", "categories", "tenders", "bids", "documents", "chat_history", "chat_ratings", "data"]
    G.add_nodes_from(tables)
    
    # Добавляем связи (пример)
    G.add_edge("users", "tenders", label="1..*")
    G.add_edge("users", "bids", label="1..*")
    G.add_edge("tenders", "bids", label="1..*")
    G.add_edge("categories", "tenders", label="1..*")
    G.add_edge("tenders", "documents", label="1..*")
    G.add_edge("users", "documents", label="1..*")
    G.add_edge("users", "chat_history", label="1..*")
    G.add_edge("users", "chat_ratings", label="1..*")
    
    # Рисуем граф
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(12, 10))
    
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color="skyblue")
    nx.draw_networkx_edges(G, pos, edge_color="gray", width=1, arrowstyle='-|>', arrowsize=20)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'label'))
    
    plt.title("Database Schema", fontsize=16)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("database_schema.png", dpi=300, bbox_inches="tight")
    plt.show()

generate_er_diagram_with_networkx()