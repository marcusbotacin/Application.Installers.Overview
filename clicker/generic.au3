#cs
 Giovanni Bertao
 UNICAMP 2018
 
 This is a generic autoit installer script. 

 May not work with 'internet-explorer server' window class.
#ce

#include<ScreenCapture.au3>
#include<WinAPIProc.au3>

; Function returns the window handle of a process via PID
Func _hWndFromPID($PID)
   Local $hWnd = 0
   Local $winlist = WinList()
   ConsoleWrite("|" & $PID & "|")
   Do
	  ; If the PID corresponds to a valid window
	  For $i = 1 To $winlist[0][0]
		 if $winlist[$i][0] <> "" Then
			$tPID = WinGetProcess($winlist[$i][1])
			if $PID = $tPID Then
			   $hWnd =$winlist[$i][1]
			   ExitLoop
			EndIf
		 EndIf
	  Next

	  ; If the PID of the window is child of the actual PID
	  For $i = 1 To $winlist[0][0]
		 if $winlist[$i][0] <> "" Then
			$tPID = WinGetProcess($winlist[$i][1])
			if $PID = _WinAPI_GetParentProcess($tPID) Then
			   $hWnd =$winlist[$i][1]
			   ExitLoop
			EndIf
		 EndIf
	  Next
   Until $hWnd <> 0
   Return $hWnd
EndFunc;

; Installation routine - It will click next until installation completes. (Takes screenshot before every click)
Func Install($PID, $pathSS)

	Local $hWnd = _hWndFromPID($PID)
	Local $STEP = 0
	Local $COND = True

	WinActivate($hWnd)
	WinMove($hWnd,"",0,0)
	While $COND
	   If WinExists($hWnd,"&Next | &Next > | Next > | &Install | Install") Then
		  _ScreenCapture_CaptureWnd($pathSS & "\" & $STEP & ".jpg", $hWnd)
		  $STEP = $STEP + 1
		  sleep(5000)
		  ControlClick($hWnd,"","[ClASSNN:Button2]")
	   Else
		  $COND = False
		  ExitLoop
	   EndIf
	WEnd
EndFunc;

; Main Function - Validade the argv before calling the Install routine
Func Main()
	IF $CmdLine[0] == 2 Then
		Local $pid = int($CmdLine[1])
		Local $pathSS = $CmdLine[2]
		IF ProcessExists($pid) <> 0 Then
			Install($pid, $pathSS)
		EndIf
	EndIf
EndFunc;

; Script Begins here
Main()
