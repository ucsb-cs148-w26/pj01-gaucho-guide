import os
import concurrent.futures

import click
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_ollama import ChatOllama

from backend.src.managers.session_manager import SessionManager
from backend.src.managers.vector_manager import VectorManager
from backend.src.scrapers.rmp_scraper import get_school_reviews, get_school_professors

load_dotenv()
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
UCSB_SCHOOL_ID = os.getenv("UCSB_SCHOOL_ID")


def select_session(session_manager: SessionManager):
    sessions = session_manager.get_recent_sessions(limit=5)
    if not sessions:
        return session_manager.create_session(name="New Session")

    click.secho("\n--- Recent Sessions ---", fg="yellow")
    for idx, (sid, name, time) in enumerate(sessions):
        short_time = str(time).split('.')[0]
        click.secho(f"{idx + 1}. {name} ({short_time})", fg="cyan")
    click.secho("N. Start New Chat", fg="green")

    choice = click.prompt("Select a session", default="N")
    if choice.upper() == 'N':
        return session_manager.create_session(name="New Session")

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(sessions):
            click.secho(f"Resuming '{sessions[idx][1]}'...", dim=True)
            return sessions[idx][0]
        else:
            return session_manager.create_session()
    except ValueError:
        return session_manager.create_session()


def print_logo():
    logo = r"""
      _____              __        _____     _    __       
     / ___/__ ___ ______/ /  ___  / ___/_ __(_)__/ /__ ____
    / (_ / _ `/ // / __/ _ \/ _ \/ (_ / // / / _  / -_) __/
    \___/\_,_/\_,_/\__/_//_/\___/\___/\_,_/_/\_,_/\__/_/   
    
    
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡤⠖⠒⠒⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡴⠋⠁⠀⠀⠉⠉⠒⠂⠤⠤⠤⠴⠚⠁⠐⠒⢲⡀⠀⠙⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠃⠀⠀⠀⠀⣶⣊⣉⡉⠉⠉⠉⠉⠙⠒⠒⠒⠋⠀⠀⠀⠘⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡸⠀⠀⠀⠀⠀⠈⠀⠀⠉⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⢀⡴⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠁⣀⣀⡤⠤⠒⠒⠊⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢳⣤⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢀⣠⠴⣒⡚⠿⠿⠿⠶⣿⣒⠤⢤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡏⠙⠛⠫⢽⣶⢤⡀⠀⠀⠀⠀
⠀⡰⠋⡰⠊⠁⠀⠀⠀⠀⠀⠀⠀⠉⠑⠺⠭⣲⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣇⠀⠀⠀⠀⠈⠳⣍⢷⡀⠀⠀
⢰⠁⠰⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠺⢗⣦⣄⣀⣀⣀⡀⠀⠀⣀⣀⣀⣀⣤⣶⣿⣷⡫⢿⠀⠀⠀⠀⠀⠀⠈⠳⡿⣆⠀
⢀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠪⣝⢿⣢⠭⡿⣿⣟⡺⣛⣷⡯⠴⠛⣉⣠⣼⣇⡀⠀⠀⠀⠀⠀⠀⠹⡘⡄
⠸⣄⠀⠀⠀⠀⣀⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⣿⣯⣍⣩⢭⣥⢤⣶⣶⣶⡯⠽⠛⠉⠀⠈⠉⠒⠦⣀⠀⠀⠀⡇⢡
⠀⠈⠳⠤⣠⣎⠁⠀⠀⠀⠈⠉⠑⠲⢤⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠱⢿⣮⡉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⡇⠸
⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠒⠢⠤⣀⡀⠀⠀⠀⠀⠀⠙⢮⣳⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⢣⠇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠒⠒⠤⢄⣀⡀⠈⠻⣿⣦⣀⠀⠀⠀⠀⠀⠀⠀⣀⣀⡤⢴⣫⠴⠃⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠑⠒⠿⣿⠯⣍⣀⣈⣉⡉⠭⠵⠒⢋⠉⠀⠀⠀⠀
                                                       
    """
    click.secho(logo, fg="yellow", bold=True)


@click.command()
def start():
    """GauchoGuider: Your UCSB Companion."""

    print_logo()

    try:
        llm = ChatOllama(model=MODEL_NAME, temperature=0)  # Keep temperature low to avoid hallucinations
        vector_manager = VectorManager(PINECONE_API_KEY)
        session_manager = SessionManager()
    except Exception as e:
        click.secho(f"Initialization Error: {e}", fg="red")
        return

    current_session_id = select_session(session_manager)

    history = session_manager.load_history(current_session_id)

    if history:
        click.secho(f"\n[Restored {len(history)} messages from history]\n", dim=True)
        if isinstance(history[-1], AIMessage):
            click.secho(f"[Last Reply]: {history[-1].content}", fg="cyan")

    system_prompt = SystemMessage(content="""
    You are GauchoGuider. A guide for ucsb students navigating through college life.

    RULES:
    1. STRICTLY talk about UCSB, Isla Vista, or college life at Santa Barbara. 
    2. If the user asks about unrelated topics (like generic coding, world news, or other universities), 
    politely steer them back to UCSB or say you only know about UCSB.
    3. Use the provided Context (reviews and stats) to answer questions accurately.
    4. When mentioning names, always use the provided Context and the Context only. DO NOT ADD EXTRA INFORMATION.
    5. Be casual, use slang like "IV" (Isla Vista), "The Loop", "Arroyo", etc., if appropriate.
    """)

    click.secho(
        "\n[GauchoGuider]: Type '/scrape' to update my knowledge base or just ask a question!",
        fg="cyan")

    while True:
        try:
            user_input = click.prompt(click.style("\n> You", fg="white", bold=True))

            # --- Commands ---
            if user_input.lower() in ['exit', 'quit', 'q']:
                click.secho("[GauchoGuider]: Go Gauchos! See ya later!", fg="cyan")
                break

            if user_input.lower() == '/scrape':
                click.secho("Accessing RMP Mainframe...", fg="yellow")
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_reviews = executor.submit(get_school_reviews, UCSB_SCHOOL_ID)
                    future_profs = executor.submit(get_school_professors, UCSB_SCHOOL_ID)
                    try:
                        school_reviews = future_reviews.result()
                    except Exception as e:
                        click.secho(f"Error fetching reviews: {e}", fg="red")
                        school_reviews = None

                    try:
                        professors = future_profs.result()
                    except Exception as e:
                        click.secho(f"Error fetching professors: {e}", fg="red")
                        professors = None
                if school_reviews:
                    vector_manager.ingest_data(school_reviews, "school_reviews")
                if professors:
                    vector_manager.ingest_data(professors, "professor_data")
                continue

            # --- RAG Logic ---
            click.secho("(Thinking...)", fg="black", bold=True)  # visual feedback
            docs = vector_manager.search(user_input, k=4)
            context_text = "\n\n".join([d.page_content for d in docs])

            rag_prompt = f"""
            CONTEXT FROM RMP REVIEWS:
            {context_text}

            USER QUESTION:
            {user_input}
            """

            # click.secho(context_text, fg="yellow", bold=True)
            messages = [system_prompt] + history + [HumanMessage(content=rag_prompt)]
            response = llm.invoke(messages)
            response_content = response.content

            click.secho(f"[GauchoGuider]: {response_content}", fg="cyan")

            session_manager.save_message(current_session_id, "human", user_input)
            session_manager.save_message(current_session_id, "ai", response_content)

            history = session_manager.load_history(current_session_id)

        except KeyboardInterrupt:
            break
        except Exception as e:
            click.secho(f"Error: {e}", fg="red")


if __name__ == "__main__":
    start()
