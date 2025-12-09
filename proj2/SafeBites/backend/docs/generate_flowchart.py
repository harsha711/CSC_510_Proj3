#!/usr/bin/env python3
"""
Generate SafeBites Chat Flow Diagram

This script generates a visual flowchart of the SafeBites chat processing pipeline
using Graphviz.

Requirements:
    pip install graphviz

Usage:
    python generate_flowchart.py

Output:
    - chat_flow.png
    - chat_flow.svg
    - chat_flow.pdf
"""

from graphviz import Digraph

def create_chat_flow_diagram():
    """Create the SafeBites chat flow diagram"""

    # Create directed graph
    dot = Digraph(
        'SafeBitesChatFlow',
        comment='SafeBites AI Chat Flow - LangGraph Pipeline',
        format='png',
        graph_attr={
            'rankdir': 'TB',
            'label': 'SafeBites AI Chat Flow - LangGraph Pipeline',
            'labelloc': 't',
            'fontsize': '16',
            'fontname': 'Arial'
        },
        node_attr={
            'shape': 'box',
            'style': 'rounded',
            'fontname': 'Arial'
        },
        edge_attr={
            'fontname': 'Arial'
        }
    )

    # Start node
    dot.node('start', 'User Query\n(e.g., "Show me pizza")',
             shape='oval', style='filled', fillcolor='lightgreen')

    # Step 1: Context Resolver
    dot.node('context_resolver',
             '1. Context Resolver\n\n'
             '• Resolve conversation context\n'
             '• Extract user state\n'
             '• Get conversation history\n'
             '• Identify user preferences',
             style='rounded,filled', fillcolor='lightblue')

    # Step 2: Intent Classifier
    dot.node('intent_classifier',
             '2. Intent Classifier\n\n'
             '• Extract user intents\n'
             '• Parse positive intents\n'
             '• Parse negative intents\n'
             '• Semantic expansion',
             style='rounded,filled', fillcolor='lightblue')

    # Step 3: Query Part Generator
    dot.node('query_part_generator',
             '3. Query Part Generator\n\n'
             '• Organize intents into categories:\n'
             '  - menu queries\n'
             '  - dish_info queries\n'
             '  - user_preferences queries',
             style='rounded,filled', fillcolor='lightblue')

    # Parallel execution nodes
    with dot.subgraph(name='cluster_parallel') as c:
        c.attr(label='Parallel Retrieval (Concurrent Execution)',
               style='filled', fillcolor='lavender')

        # Step 4a: Menu Retriever
        c.node('menu_retriever',
               '4a. Menu Retriever\n\n'
               '• FAISS semantic search\n'
               '• Cross-restaurant search\n'
               '• Apply threshold filter (≤2.0)\n'
               '• Return top-k dishes (20)',
               style='rounded,filled', fillcolor='lightcoral')

        # Step 4b: Informative Retriever
        c.node('informative_retriever',
               '4b. Informative Retriever\n\n'
               '• Get detailed dish info\n'
               '• Fetch nutritional data\n'
               '• Get allergen information\n'
               '• Return dish details',
               style='rounded,filled', fillcolor='lightcoral')

        # Step 4c: User Preferences Retriever
        c.node('user_preferences_retriever',
               '4c. User Preferences Retriever\n\n'
               '• Fetch user profile\n'
               '• Get allergen list\n'
               '• Get health goals\n'
               '• Get dietary pattern',
               style='rounded,filled', fillcolor='lightcoral')

    # Step 5: Compatibility Scorer
    dot.node('compatibility_scorer',
             '5. Compatibility Scorer\n\n'
             '• Limit to 7 dishes (performance)\n'
             '• Batch process with LLM\n'
             '• Calculate weighted scores:\n'
             '  - Allergen Safety (40%)\n'
             '  - Nutrition Match (25%)\n'
             '  - Taste Preference (20%)\n'
             '  - Dietary Pattern (15%)\n'
             '• Apply safety override',
             style='rounded,filled', fillcolor='lightblue')

    # Step 6: Response Formatter
    dot.node('format_final_response',
             '6. Response Formatter\n\n'
             '• Synthesize natural language\n'
             '• Format dish recommendations\n'
             '• Include compatibility scores\n'
             '• Generate final response',
             style='rounded,filled', fillcolor='lightblue')

    # End node
    dot.node('end', 'Chat Response\n(Formatted recommendations)',
             shape='oval', style='filled', fillcolor='lightgreen')

    # Data stores
    dot.node('faiss_index', 'FAISS Index\n(Vector embeddings)',
             shape='cylinder', style='filled', fillcolor='lightyellow')
    dot.node('mongodb', 'MongoDB\n(Dishes, Restaurants,\nUser Profiles)',
             shape='cylinder', style='filled', fillcolor='lightyellow')
    dot.node('openai', 'OpenAI GPT-4o-mini\n(LLM for scoring\nand responses)',
             shape='cylinder', style='filled', fillcolor='lightyellow')

    # Main flow edges
    dot.edge('start', 'context_resolver', label='User input')
    dot.edge('context_resolver', 'intent_classifier', label='Context data')
    dot.edge('intent_classifier', 'query_part_generator', label='Extracted intents')

    # Parallel execution edges
    dot.edge('query_part_generator', 'menu_retriever', label='Menu queries')
    dot.edge('query_part_generator', 'informative_retriever', label='Dish info queries')
    dot.edge('query_part_generator', 'user_preferences_retriever', label='User queries')

    # Compatibility scoring
    dot.edge('menu_retriever', 'compatibility_scorer', label='Retrieved dishes')
    dot.edge('user_preferences_retriever', 'compatibility_scorer',
             label='User profile', style='dashed')

    # Converge to final response
    dot.edge('compatibility_scorer', 'format_final_response', label='Scored dishes')
    dot.edge('informative_retriever', 'format_final_response', label='Dish details')

    dot.edge('format_final_response', 'end', label='Final response')

    # Data store connections
    dot.edge('menu_retriever', 'faiss_index', label='Vector search',
             style='dotted', dir='both')
    dot.edge('menu_retriever', 'mongodb', label='Fetch dishes',
             style='dotted', dir='both')
    dot.edge('informative_retriever', 'mongodb', label='Fetch details',
             style='dotted', dir='both')
    dot.edge('user_preferences_retriever', 'mongodb', label='Fetch profile',
             style='dotted', dir='both')
    dot.edge('compatibility_scorer', 'openai', label='Batch scoring',
             style='dotted', dir='both')
    dot.edge('format_final_response', 'openai', label='Generate response',
             style='dotted', dir='both')

    # Legend
    with dot.subgraph(name='cluster_legend') as c:
        c.attr(label='Legend', style='dashed')
        c.node('start_legend', 'Start/End', shape='oval',
               style='filled', fillcolor='lightgreen')
        c.node('service_legend', 'Service Node', shape='box',
               style='rounded,filled', fillcolor='lightblue')
        c.node('data_legend', 'Data Store', shape='cylinder',
               style='filled', fillcolor='lightyellow')
        c.node('parallel_legend', 'Parallel Execution', shape='box',
               style='rounded,filled', fillcolor='lightcoral')

    return dot


if __name__ == '__main__':
    print("Generating SafeBites Chat Flow Diagram...")

    # Create the diagram
    dot = create_chat_flow_diagram()

    # Save in multiple formats
    print("Saving PNG...")
    dot.render('chat_flow', format='png', cleanup=True)

    print("Saving SVG...")
    dot.render('chat_flow', format='svg', cleanup=True)

    print("Saving PDF...")
    dot.render('chat_flow', format='pdf', cleanup=True)

    print("\n✅ Flowcharts generated successfully!")
    print("   - chat_flow.png")
    print("   - chat_flow.svg")
    print("   - chat_flow.pdf")
    print("\nYou can also view the source: chat_flow.dot")
