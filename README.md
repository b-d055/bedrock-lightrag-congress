# LightRAG Meets Amazon Bedrock ⛰️

This project integrates LightRAG with Amazon Bedrock for advanced language model interactions and knowledge graph population.

## Prerequisites

1. **Install Ollama**  
   Download and install Ollama from [https://ollama.com/download](https://ollama.com/download).

2. **Pull the Embedding Model**  
   Run the following command to pull the `nomic-embed-text` model:
   ```bash
   ollama pull nomic-embed-text
   ```

3. **Set Up AWS Credentials**  
   - Create an IAM user in AWS and attach the `AmazonBedrockFullAccess` policy (for testing only; in production, create a custom policy with minimal permissions).
   - Generate an access key for the IAM user.
   - Add the following to a `.env` file in the project directory:
     ```
     AWS_ACCESS_KEY_ID=<your-access-key-id>
     AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
     AWS_SESSION_TOKEN=""
     ```

4. **Grant Access to Amazon Foundation Models**  
   After setting up AWS credentials, ensure that your account has access to Amazon Foundation Models. Follow the instructions in the [Amazon Bedrock documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) to request access. Without this step, you will not be able to use Amazon Bedrock models.

5. **Install Dependencies**  
   Ensure you have Python installed. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

   Note: I've locked the version of the lightrag-hku in the `requirements.txt` file to ensure compatibility, as this is an in-developmnt project.

## Usage

The script supports two modes: `cli` for querying the model interactively and `populate` for populating the knowledge graph with data from a file or directory.

### CLI Mode

Use the `cli` mode to interact with the model by asking questions. 

#### Example:
```bash
python bedrock_graph.py --mode cli --working_dir ./sample_text --llm_model_name amazon.nova-lite-v1:0
```

- `--mode cli`: Specifies the CLI mode.
- `--working_dir`: The working directory where LightRAG stores its data.
- `--llm_model_name`: (Optional) The Bedrock LLM model name. Defaults to `amazon.nova-lite-v1:0`.

Once started, you can type your questions in the terminal. Type `exit` to quit.

### Populate Mode

Use the `populate` mode to insert data into the knowledge graph from a single file or all files in a directory.

#### Example (Single File):
```bash
python bedrock_graph.py --mode populate --working_dir ./sample_text --path ./record_sample.txt --llm_model_name amazon.nova-lite-v1:0
```

#### Example (Directory):
```bash
python bedrock_graph.py --mode populate --working_dir ./sample_text --path ./data_directory --llm_model_name amazon.nova-lite-v1:0
```

- `--mode populate`: Specifies the populate mode.
- `--working_dir`: The working directory where LightRAG stores its data.
- `--path`: The file or directory to populate the knowledge graph with.
- `--llm_model_name`: (Optional) The Bedrock LLM model name. Defaults to `amazon.nova-lite-v1:0`.

### Notes

- Ensure the `working_dir` exists or will be created dynamically by the script.
- The `path` parameter is required for `populate` mode but not for `cli` mode.

## Troubleshooting

- **Missing AWS Credentials**: Ensure the `.env` file is correctly configured with your AWS credentials.
- **Model Not Found**: Ensure you have pulled the `nomic-embed-text` model using `ollama pull nomic-embed-text`.
- **Access Denied to Foundation Models**: Ensure you have followed the steps to request access to Amazon Foundation Models as described [here](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html).

## License

This project is licensed under the MIT License.

