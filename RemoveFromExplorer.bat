@echo off
setlocal

:: Remove context menu entry for all files
reg delete "HKEY_CLASSES_ROOT\*\shell\TokenCounter" /f

:: Remove context menu entry for all folders
reg delete "HKEY_CLASSES_ROOT\Directory\shell\TokenCounter" /f

echo "Token Counter context menu item has been removed successfully."
pause
