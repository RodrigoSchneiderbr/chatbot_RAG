import operator
from typing import Annotated, List, TypedDict
from langchain_core.messages import BaseMessage 

class EstadoDoAgente(TypedDict):
    mensagens: Annotated[list[BaseMessage], operator.add]
    documentos: List[str]