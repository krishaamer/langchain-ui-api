# langchain-ui-backend

## Getting started

1. Clone the repo into a public GitHub repository (or fork https://github.com/homanp/langchain-ui-backend/fork). If you plan to distribute the code, keep the source code public.

   ```sh
   git clone https://github.com/homanp/langchain-ui-backend.git
   ```

Generate ads with GPT

1. Create and activate a virtual environment

   ```sh
   virtualenv MY_ENV
   source MY_ENV/bin/activate
   ```

1. Install packages with pip

   ```sh
   cd langchain-ui-backend
   pip install -r requirements.txt
   ```

1. Set up your .env file

   - Duplicate `.env.example` to `.env`

1. Run the project

   ```sh
   uvicorn main:app --reload
   ```

## Contributions

Our mission is to make it easy for anyone to create and run LLM apps in the cloud. We are super happy for any contributions you would like to make. Create new features, fix bugs or improve on infra.

You can read more on how to contribute [here](https://github.com/homanp/langchain-ui/blob/main/.github/CONTRIBUTING.md).
