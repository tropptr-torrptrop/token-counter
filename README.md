This application is a versatile token counting tool that supports multiple tokenizer models. It provides a graphical user interface for easy token counting of files or entire directories.

## Installation

1. Ensure you have Python 3.7 or later installed on your system.

2. Install the required dependencies using pip:

   ```
   pip install tiktoken transformers
   ```

   Note: You may need to install additional dependencies for specific tokenizers.


## Usage

To run the application, use the following command in your terminal: `python token_counter.pyw <file_or_folder_path>`
Replace `<file_or_folder_path>` with the path to the file or directory you want to analyze.

OR use `AddToExplorer.bat` (run as Admin) for Windows systems. It will add context menu item for files and folders. Tested on Win10.


The application will open a graphical user interface with the following features:

- A tree view showing files and folders (lazily loaded for speed)
- Right-click any file or folder to exclude it from token counting (it is not deleted, just hidden from the tree and calculation)
- A dropdown menu to select the tokenizer model
- A "Copy to Clipboard" button to copy the total token count
- A "Calculate Tokens" button: tokens are only counted when you press this button, after you have excluded any files/folders you wish
- Each file/folder in the tree will show its token count after calculation


## Logic Explanation

1. The application starts by loading the configuration and initializing the GUI.

2. The file/folder tree is loaded lazily for speed. You can right-click to exclude any files or folders before calculation (they are not deleted from disk).

3. Token calculation only happens when you press the "Calculate Tokens" button. The app recursively processes all non-excluded files and folders, skipping binary files, and updates the tree with token counts.

4. The tokenization process depends on the selected model. You can see available options in dropdown.

To add new tokenizer - first check this link: https://huggingface.co/docs/transformers/v4.45.1/en/model_doc/auto#transformers.AutoTokenizer.from_pretrained

Click on the tokenizer class link (i.e. PegasusTokenizerFast) and you will see example usage. Prefer '...Fast' option. Add it to the program (import line, get_tokenizer entity, dropdown option). Alternatively, you can add AutoTokenizer class with HF model specified (example in 'llama3').

Note, that some models are closed for anonymous access. Program currently does not work with such models.

For tokenizers other than gpt and claude - Python will have to download models first. You will have a lag when using such tokenizer first time. 


## Troubleshooting

- If you encounter issues, run program from console to see errors: `python token_counter.pyw token_counter.pyw`


Development assisted by Claude 3.5 Sonnet, Mistral Large 2 and Qwen 2.5

## Special Thanks

Thanks to the original author for the initial version: https://github.com/tropptr-torrptrop/token-counter