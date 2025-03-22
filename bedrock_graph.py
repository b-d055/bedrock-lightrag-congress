"""
LightRAG meets Amazon Bedrock ⛰️
"""

import os
import logging
import argparse

from lightrag import LightRAG, QueryParam
from lightrag.llm.bedrock import bedrock_complete_if_cache, locate_json_string_body_from_string
from lightrag.llm.ollama import ollama_embed
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status

import asyncio
import nest_asyncio

import dotenv

dotenv.load_dotenv()

nest_asyncio.apply()

logging.getLogger("aiobotocore").setLevel(logging.DEBUG)


async def bedrock_complete(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    """
    Complete the prompt using Amazon Bedrock.
    Replacement for lightrag.llm.bedrock.bedrock_complete.
    that allows us to use any bedrock model."""
    keyword_extraction = kwargs.pop("keyword_extraction", None)
    llm_model_name = kwargs["hashing_kv"].global_config["llm_model_name"]
    # bedrock doenst support stream kwarg
    kwargs.pop("stream", None)
    result = await bedrock_complete_if_cache(
        llm_model_name,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        **kwargs,
    )
    if keyword_extraction:
        return locate_json_string_body_from_string(result)
    return result


async def initialize_rag(working_dir, llm_model_name="amazon.nova-lite-v1:0"):
    """
    Initialize LightRAG with Amazon Bedrock as the LLM model
    and nomic-embed-text via Ollama as the embedding model.
    """
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)

    rag = LightRAG(
        working_dir=working_dir,
        llm_model_func=bedrock_complete,
        llm_model_name=llm_model_name,
        embedding_func=EmbeddingFunc(
            embedding_dim=768,
            max_token_size=8192,
            func=lambda texts: ollama_embed(
                texts, embed_model="nomic-embed-text", host="http://localhost:11434"
            ),
        ),
        llm_model_max_async=32
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag


def main(working_dir, llm_model_name):
    rag = asyncio.run(initialize_rag(working_dir, llm_model_name))

    print("LightRAG CLI. Type your question below (type 'exit' to quit):")
    while True:
        question = input(">> ")
        if question.lower() == "exit":
            print("Exiting LightRAG CLI.")
            break

        resp = rag.query(
            question,
            param=QueryParam(mode="mix"),
        )
        print("Response:", resp)


def populate(path, working_dir, llm_model_name):
    """
    Populate the knowledge graph with data from a single file or all files in a directory.
    """
    rag = asyncio.run(initialize_rag(working_dir, llm_model_name))

    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            print("Inserting data from file:", path)
            rag.insert(f.read(), ids=[os.path.basename(path)], file_paths=[path])
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    print("Inserting data from file:", file_path)
                    rag.insert(f.read(), ids=[os.path.basename(file_path)], file_paths=[file_path])
    else:
        print(f"Error: The path '{path}' is neither a file nor a directory.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LightRAG CLI or Populate Mode")
    parser.add_argument(
        "--mode", choices=["cli", "populate"], required=True, help="Mode to run: 'cli' or 'populate'"
    )
    parser.add_argument(
        "--working_dir", required=True, help="Working directory for LightRAG"
    )
    parser.add_argument(
        "--path", required=False, help="File or directory to populate (required for 'populate' mode)"
    )
    parser.add_argument(
        "--llm_model_name", default="amazon.nova-lite-v1:0", help="Bedrock LLM model name (default: amazon.nova-lite-v1:0)"
    )

    args = parser.parse_args()

    if args.mode == "populate":
        if not args.path:
            print("Error: --path is required for 'populate' mode.")
        else:
            populate(args.path, args.working_dir, args.llm_model_name)
    elif args.mode == "cli":
        main(args.working_dir, args.llm_model_name)