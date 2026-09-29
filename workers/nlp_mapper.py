import streamlit as st
import torch
from sentence_transformers import SentenceTransformer, util
from stage_registry import GENERAL_STAGE, STRATEGY_DESCRIPTIONS


@st.cache_resource
def load_nlp_model():
    
    model = SentenceTransformer('cointegrated/rubert-tiny2')
    
    
    corpus_keys = list(STRATEGY_DESCRIPTIONS.keys())
    corpus_embeddings = model.encode(list(STRATEGY_DESCRIPTIONS.values()), convert_to_tensor=True)
    
    return model, corpus_keys, corpus_embeddings

def predict_ai_strategy(task_name: str, threshold: float = 0.35) -> str:
    
    model, corpus_keys, corpus_embeddings = load_nlp_model()
    
    
    task_emb = model.encode(task_name, convert_to_tensor=True)
    
    
    cos_scores = util.cos_sim(task_emb, corpus_embeddings)[0]
    
    
    best_idx = int(torch.argmax(cos_scores))
    best_score = float(cos_scores[best_idx])
    
    
    if best_score > threshold:
        return corpus_keys[best_idx]
    
    
    return GENERAL_STAGE