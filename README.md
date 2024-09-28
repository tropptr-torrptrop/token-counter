
https://github.com/tropptr-torrptrop/token-counter

This application is a versatile token counting tool that supports multiple tokenizer models. It provides a graphical user interface for easy token counting of files or entire directories.

## Installation

1. Ensure you have Python 3.7 or later installed on your system.

2. Install the required dependencies using pip:

   ```
   pip install tiktoken transformers anthropic
   ```

   Note: You may need to install additional dependencies for specific tokenizers.


## Usage

To run the application, use the following command in your terminal: `python token_counter.pyw <file_or_folder_path>`
Replace `<file_or_folder_path>` with the path to the file or directory you want to analyze.

OR use `AddToExplorer.bat` (run as Admin) for Windows systems. It will add context menu item for files and folders. Tested on Win10.


The application will open a graphical user interface with the following features:

- A large text box displaying the total token count
- A dropdown menu to select the tokenizer model
- A "Copy to Clipboard" button to copy the token count
- A list view showing individual file names and their token counts


## Logic Explanation

1. The application starts by loading the configuration and initializing the GUI.

2. When a file or directory is selected, the application processes it as follows:
   - For a single file, it reads the content and tokenizes it.
   - For multiple files - it will launch multiple instances of the program and tokenize each.
   - For a directory, it recursively processes all files, skipping binary files.

3. The tokenization process depends on the selected model. You can see available options in dropdown.

To add new tokenizer - first check this link: https://huggingface.co/docs/transformers/v4.45.1/en/model_doc/auto#transformers.AutoTokenizer.from_pretrained

Click on the tokenizer class link (i.e. PegasusTokenizerFast) and you will see example usage. Prefer '...Fast' option. Add it to the program (import line, get_tokenizer entity, dropdown option). Alternatively, you can add AutoTokenizer class with HF model specified (example in 'llama3').

Note, that some models are closed for anonymous access. Program currently does not work with such models.

For tokenizers other than gpt and claude - Python will have to download models first. You will have a lag when using such tokenizer first time. 


## Troubleshooting

- If you encounter issues, run program from console to see errors: `python token_counter.pyw token_counter.pyw`


Development assisted by Claude 3.5 Sonnet, Mistral Large 2 and Qwen 2.5
