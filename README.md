## Prompt Manager

Prompt Manger is a simple and easy-to-use tool for comparing output of LLMs with multiple prompts.

The tool provides you:
- A simple interface to compare multiple outputs in a single window.
- Basic statistics (e.g. token length distribution) of the completions for each prompt.

### Quick Start

You need docker installed on your computer.

```
git clone https://github.com/r-fujii/prompt_manager.git
cd prompt_manager

# overwrite .env with your OpenAI API key

docker compose up -d --build

# open http://localhost:5050 on your browser.
```

### How to use

1. Write common settings (e.g. brief description of the assistant, characteristics to play) you want the model to follow throughout the prompts (Optional). Change model temperature if needed.

<img src="https://github.com/r-fujii/prompt_manager/blob/images/settings.png" width="480">

2. Write your prompt, like task description or additional prompt-specific characteristics and push "Add" button. You can add up to 4 prompts for comparison.

<img src="https://github.com/r-fujii/prompt_manager/blob/images/prompts.png" width="480">

3. Toggle mode switch on the top-right, then write user message in the textarea. Push "Run" button to get responses (completions). The responses are shown in the bottom following the prompts (This may take several seconds).

<img src="https://github.com/r-fujii/prompt_manager/blob/images/run.png" width="480">

4. You can get basic information about responses (completions) if you want. Push "Get stats" button and wait for a new tab to be opened.
Note: The browser may block new window from opening for the first time. Please change browser settings to allow popups in that case.

<img src="https://github.com/r-fujii/prompt_manager/blob/images/stats.png" width="480">

### Note

The tool is intended for personal use. It is not equipped with desirable features for commercial use, like logging in, usage management, and code testing. The author do not take responsibilities for any damages caused by using the tool.