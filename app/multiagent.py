import os
from dotenv import load_dotenv, find_dotenv
import functools
import operator
import requests
import warnings
from bs4 import BeautifulSoup
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated, Sequence, Literal
from langchain_community.tools.tavily_search import TavilySearchResults

from .logger import logger
from .rate_limiter import rate_limit
from .cache import cached
from .validators import validate_url, validate_prompt, sanitize_input, validate_api_key

warnings.filterwarnings("ignore", category=SyntaxWarning, message="invalid escape sequence")

# Cargar variables de entorno
load_dotenv(find_dotenv())

# Verificar API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or not validate_api_key(api_key):
    raise ValueError("OPENAI_API_KEY inválida o no definida en las variables de entorno")

# Configuración del modelo
MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4-turbo-preview")
llm = ChatOpenAI(model=MODEL_NAME)

@tool("process_search_tool", return_direct=False)
@rate_limit(calls_per_minute=30)
@cached(ttl_seconds=3600)
def process_search_tool(url: str) -> str:
    """Parse web content with BeautifulSoup"""
    try:
        if not validate_url(url):
            raise ValueError("URL inválida: debe comenzar con http:// o https://")
            
        response = requests.get(url=url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text(strip=True)
        
        if not text:
            logger.warning(f"No se pudo extraer contenido de {url}")
            return "No se pudo extraer contenido del sitio web."
            
        return text
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al acceder a la URL {url}: {str(e)}")
        return f"Error al acceder a la URL: {str(e)}"
    except Exception as e:
        logger.error(f"Error inesperado procesando {url}: {str(e)}")
        return f"Error inesperado: {str(e)}"

tools = [TavilySearchResults(max_results=1), process_search_tool]

def create_new_agent(llm: ChatOpenAI,
                  tools: list,
                  system_prompt: str) -> AgentExecutor:
    if not system_prompt or not isinstance(system_prompt, str):
        raise ValueError("System prompt inválido")
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor

def agent_node(state, agent, name):
    try:
        result = agent.invoke(state)
        return {"messages": [HumanMessage(content=result["output"], name=name)]}
    except Exception as e:
        logger.error(f"Error en agente {name}: {str(e)}")
        return {"messages": [HumanMessage(content=f"Error: {str(e)}", name=name)]}

content_marketing_team = ["online_researcher", "blog_manager", "social_media_manager"]

system_prompt = (
    "As a content marketing manager, your role is to oversee the insight between these"
    " workers: {content_marketing_team}. Based on the user's request,"
    " determine which worker should take the next action. Each worker is responsible for"
    " executing a specific task and reporting back thier findings and progress."
    " Once all tasks are completed, indicate 'FINISH'."
)

options = ["FINISH"] + content_marketing_team

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("system",
     "Given the conversation above, who should act next? Or should we FINISH? Select one of: {options}"),
]).partial(options=str(options), content_marketing_team=", ".join(content_marketing_team))

def content_marketing_manager(state):
    """Función que maneja la lógica del content marketing manager."""
    result = prompt | llm | StrOutputParser()
    response = result.invoke(state)
    
    # Extraer el nombre del agente o FINISH de la respuesta
    for option in options:
        if option.lower() in response.lower():
            return {"next": option}
    
    # Si no se encuentra una opción válida, por defecto ir al investigador
    return {"next": "online_researcher"}

online_researcher_agent = create_new_agent(
    llm,
    tools,
    """Your primary role is to function as an intelligent online research assistant, adept at scouring 
    the internet for the latest and most relevant trending stories across various sectors like politics, technology, 
    health, culture, and global events. You possess the capability to access a wide range of online news sources, 
    blogs, and social media platforms to gather real-time information."""
)

online_researcher_node = functools.partial(
    agent_node, agent=online_researcher_agent, name="online_researcher"
)

blog_manager_agent = create_new_agent(
    llm, tools,
    """You are a Blog Manager. The role of a Blog Manager encompasses several critical responsibilities aimed at transforming initial drafts into polished, SEO-optimized blog articles that engage and grow an audience. Starting with drafts provided by online researchers, the Blog Manager must thoroughly understand the content, ensuring it aligns with the blog's tone, target audience, and thematic goals. Key responsibilities include:

1. Content Enhancement: Elevate the draft's quality by improving clarity, flow, and engagement. This involves refining the narrative, adding compelling headers, and ensuring the article is reader-friendly and informative.

2. SEO Optimization: Implement best practices for search engine optimization. This includes keyword research and integration, optimizing meta descriptions, and ensuring URL structures and heading tags enhance visibility in search engine results.

3. Compliance and Best Practices: Ensure the content adheres to legal and ethical standards, including copyright laws and truth in advertising. The Blog Manager must also keep up with evolving SEO strategies and blogging trends to maintain and enhance content effectiveness.

4. Editorial Oversight: Work closely with writers and contributors to maintain a consistent voice and quality across all blog posts. This may also involve managing a content calendar, scheduling posts for optimal engagement, and coordinating with marketing teams to support promotional activities.

5. Analytics and Feedback Integration: Regularly review performance metrics to understand audience engagement and preferences. Use this data to refine future content and optimize overall blog strategy.

In summary, the Blog Manager plays a pivotal role in bridging initial research and the final publication by enhancing content quality, ensuring SEO compatibility, and aligning with the strategic objectives of the blog. This position requires a blend of creative, technical, and analytical skills to successfully manage and grow the blog's presence online.""")

blog_manager_node = functools.partial(
    agent_node, agent=blog_manager_agent, name="blog_manager")

social_media_manager_agent = create_new_agent(
    llm, tools,
    """You are a Social Media Manager. The role of a Social Media Manager, particularly for managing Twitter content, involves transforming research drafts into concise, engaging tweets that resonate with the audience and adhere to platform best practices. Upon receiving a draft from an online researcher, the Social Media Manager is tasked with several critical functions:

1. Content Condensation: Distill the core message of the draft into a tweet, which typically allows for only 280 characters. This requires a sharp focus on brevity while maintaining the essence and impact of the message.

2. Engagement Optimization: Craft tweets to maximize engagement. This includes the strategic use of compelling language, relevant hashtags, and timely topics that resonate with the target audience.

3. Compliance and Best Practices: Ensure that the tweets follow Twitter's guidelines and best practices, including the appropriate use of mentions, hashtags, and links. Also, adhere to ethical standards, avoiding misinformation and respecting copyright norms.

In summary, the Social Media Manager's role is crucial in leveraging Twitter to disseminate information effectively, engage with followers, and build the brand's presence online. This position combines creative communication skills with strategic planning and analysis to optimize social media impact.""")

social_media_manager_node = functools.partial(
    agent_node, agent=social_media_manager_agent, name="social_media_manager")

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    
workflow = StateGraph(AgentState)

workflow.add_node("content_marketing_manager", action=content_marketing_manager)
workflow.add_node("online_researcher", action=online_researcher_node)
workflow.add_node("blog_manager", action=blog_manager_node)
workflow.add_node("social_media_manager", action=social_media_manager_node)

for member in content_marketing_team:
    workflow.add_edge(start_key=member, end_key="content_marketing_manager")

conditional_map = {k: k for k in content_marketing_team}
conditional_map['FINISH'] = END

workflow.add_conditional_edges(
    "content_marketing_manager", lambda x: x["next"], conditional_map)

workflow.set_entry_point("content_marketing_manager")

multiagent = workflow.compile()

for s in multiagent.stream(
    {
        "messages": [
            HumanMessage(
                content="""Write me a report on Agentic Behavior. After the research on Agentic Behavior,pass the findings to the blog manager to generate the final blog article. Once done, pass it to the social media manager to write a tweet on the subject."""
            )
        ],
    },
    # Maximum number of steps to take in the multiagent
    {"recursion_limit": 150}
):
    if not "__end__" in s:
        print(s, end="\n\n-----------------\n\n")
