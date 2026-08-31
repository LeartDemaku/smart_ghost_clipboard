Set fso = CreateObject("Scripting.FileSystemObject")
Set WshShell = CreateObject("WScript.Shell")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir

exePath = scriptDir & "\SmartGhostClipboard.exe"

If fso.FileExists(exePath) Then
    WshShell.Run """" & exePath & """", 0, False
Else
    venvPythonW = scriptDir & "\venv\Scripts\pythonw.exe"
    If fso.FileExists(venvPythonW) Then
        WshShell.Run """" & venvPythonW & """ main.py", 0, False
    Else
        WshShell.Run "pythonw.exe main.py", 0, False
    End If
End If


