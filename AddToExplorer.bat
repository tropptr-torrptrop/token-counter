@echo off
setlocal

:: Get the path of the folder where the batch script is located
set "scriptPath=%~dp0"
set "exePath=%scriptPath%token_counter.pyw"
set "iconPath=%scriptPath%icon.ico"

:: Get the path of the Python executable
for /f "usebackq tokens=*" %%p in (`where pythonw`) do (
    set "pythonPath=%%p"
)

:: Add context menu entry for all files
reg add "HKEY_CLASSES_ROOT\*\shell\TokenCounter" /ve /d "Token Counter" /f
reg add "HKEY_CLASSES_ROOT\*\shell\TokenCounter" /v "Icon" /d "%iconPath%" /f
reg add "HKEY_CLASSES_ROOT\*\shell\TokenCounter\command" /ve /d "%pythonPath% \"%exePath%\" \"%%1\"" /f

:: Add context menu entry for all folders
reg add "HKEY_CLASSES_ROOT\Directory\shell\TokenCounter" /ve /d "Token Counter" /f
reg add "HKEY_CLASSES_ROOT\Directory\shell\TokenCounter" /v "Icon" /d "%iconPath%" /f
reg add "HKEY_CLASSES_ROOT\Directory\shell\TokenCounter\command" /ve /d "%pythonPath% \"%exePath%\" \"%%1\"" /f

echo "Token Counter context menu item has been added successfully."
pause
