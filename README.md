# Hackathon starter project: AI chat app

<div style="display: flex; justify-content: center; gap: 10px;">
  <a href="images/polytope.png">
    <img src="images/polytope.png" alt="Polytope" style="width: 30%; height: auto;" />
  </a>
  <a href="images/chat.png">
    <img src="images/chat.png" alt="Chat" style="width: 30%; height: auto;" />
  </a>
  <a href="images/home.png">
    <img src="images/home.png" alt="Home" style="width: 30%; height: auto;" />
  </a>
</div>

This is a starter project for an LLM-based chat app, designed for you to get a running start on your Hackathon project.
It provides a simple chat interface and an LLM-powered backend that acts like a customer support bot.

Features:
- A complete API (written in Python) with persistent chats, a knowledge base, and LLM integration (courtesy of Opper).
- A frontend (written in React) that provides a chat interface for users to interact with the API.
- A portable dev env with hot reload (courtesy of Polytope) that makes it easy to iterate and collaborate on your solution. One command and you and all your team members are up and running with the same environment.

## Suggested improvements

There are lots of directions you can take this project. Here are a few suggestions:
- The bot is very unhelpful! Work with the prompts to see if you can make it do something useful.
- Expand on the knowledge base, or replace it with something different.
- The bot hallucinates a lot! Try to make it more reliable.

## Getting started

### TL;DR

0. Make sure you can run containers (on macOS we recommend [OrbStack](https://docs.orbstack.dev/install)).
1. Installed [Polytope](https://polytope.com/docs/quick-start#cli) (on macOS run `brew install polytopelabs/tap/polytope-cli`).
2. Clone this repo: `git clone https://github.com/aeriksson/hackathon-chatbot-starter.git my-project && cd my-project`
3. Go to [https://opper.ai/](https://opper.ai/) and get yourself an API key
4. Store the API key: `pt secret set opper-api-key YOUR_OPPER_API_KEY`
5. Run the stack: `pt run stack`
6. Open the UI: [http://localhost:8000](http://localhost:8000)
7. Start building something!

### Detailed instructions

#### Docker or OrbStack
You'll need Docker or OrbStack to run the app. You can install Docker from [here](https://docs.docker.com/get-docker/) and OrbStack from [here](https://docs.orbstack.dev/install).

#### Polytope CLI
On macOS:
```bash
brew install polytopelabs/tap/polytope-cli
```

For installation on Windows and Linux, see [the docs](https://polytope.com/docs/quick-start).

### Running the app
To run the app, clone this repository and navigate to the project directory:

```bash
git clone https://github.com/aeriksson/hackathon-chatbot-starter.git my-project
cd my-project
```

Next, sign up for [https://opper.ai/](https://opper.ai/) (it's free and gives you access to all the major LLMs - no credit card required!), create an API key, and store it using the Polytope CLI:
```bash
pt secret set opper-api-key YOUR_OPPER_API_KEY
```

Finally, run the following command to start the app:
```bash
pt run stack
```

Then open the UI at [http://localhost:8000](http://localhost:8000). On first load, this can take a little while to start up while dependencies are downloaded.

API documentation is automatically generated and can be found at [http://localhost:3000/redoc](http://localhost:3000/redoc).

## Project Structure

This app has two main components:
- [The API](./api) - A Python FastAPI backend that handles chat session management, knowledge base querying, and Opper AI integration
- [The UI](./frontend) - A React TypeScript frontend that provides the user interface

The API is defined in [api/src/api/routes.py](./api/src/api/routes.py). Example usage:
```bash
# Create a new chat session
curl -X POST http://localhost:3000/api/chats -H "Content-Type: application/json" -d '{}'

# Get chat details (replace UUID with the one from previous response)
curl http://localhost:3000/api/chats/550e8400-e29b-41d4-a716-446655440000

# Send a message and get a response
curl -X POST http://localhost:3000/api/chats/550e8400-e29b-41d4-a716-446655440000/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "What is your return policy?"}'

# Get chat history
curl http://localhost:3000/api/chats/550e8400-e29b-41d4-a716-446655440000/messages

# Search knowledge base
curl 'http://localhost:3000/api/knowledge-base/search?query=warranty'
```

## About Polytope

This project uses [Polytope](https://polytope.com) to run and orchestrate all your services and automation.

Polytope is the easiest way to build, run, and iterate on your software. It gives you a unified interface for running all your services and workflows (CI, DataOps, MLOps, DevOps, ...) - on your machine, in the cloud or on-prem.

## About Opper AI

This template uses [Opper AI](https://opper.ai) for LLM response generation and knowledge base integration.

Learn more about the [Opper SDK on GitHub](https://github.com/opper-ai/opper-python) and in the [official documentation](https://docs.opper.ai/).
